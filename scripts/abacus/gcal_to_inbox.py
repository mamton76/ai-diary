#!/usr/bin/env python3
"""
AI Diary — Google Calendar → file inbox adapter

Reads events from a Google Calendar inbox, creates structured inbox packages in
AI-Diary/inbox/new/, and then moves imported events to a processed calendar.

Important:
- This script does NOT create diary entries directly.
- It only imports Calendar events into the file-based inbox.
- Run the existing Inbox-to-Entry workflow separately to create entries from
  inbox/new/ packages.

Meaning of calendars in this MVP:
- Inbox calendar      = events not yet imported into the file inbox
- Processed calendar  = events already imported into the file inbox

Created package shape:

    inbox/new/YYYY-MM-DD__google_calendar__event_<hash>/
      MESSAGE.json
      raw_text.md
      source_event.json

For events with neither title nor description, the package is created under:

    inbox/needs_review/YYYY-MM-DD__google_calendar__event_<hash>/

A small import log is stored in:

    indexes/source_google_calendar_events.jsonl

This log is diagnostic. Active and archived Drive packages determine whether an
event has been imported.

Usage:

    # Dry run — show what would be imported, touch nothing
    python gcal_to_inbox.py \
      --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
      --inbox-calendar "Дневничок" \
      --processed-calendar "Дневничок обработанное" \
      --credentials google_credentials.json \
      --token google_token.json \
      --dry-run

    # Import up to 3 events
    python gcal_to_inbox.py \
      --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
      --inbox-calendar "Дневничок" \
      --processed-calendar "Дневничок обработанное" \
      --credentials google_credentials.json \
      --token google_token.json \
      --limit 3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from googleapiclient.discovery import build as gapi_build
from googleapiclient.http import MediaInMemoryUpload

from drive_client import DriveClient, DriveFile
from gcal_client import (
    CALENDAR_SCOPES,
    CalendarClient,
    CalendarEvent,
    build_calendar_client_from_creds,
    get_credentials,
)


FORMAT_VERSION = "v0.1.0"
SCHEMA_RAW_INPUT = "raw_input_message"
IMPORT_LOG_PATH = ["indexes"]
IMPORT_LOG_FILE = "source_google_calendar_events.jsonl"
STAGING_PATH = ("inbox", "processing")
FOLDER_MIME = "application/vnd.google-apps.folder"


# ------------------------------------------------------------------ #
# Generic helpers                                                     #
# ------------------------------------------------------------------ #


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_hash(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def event_date(event: CalendarEvent) -> str:
    """Return the calendar date of the event start as YYYY-MM-DD."""
    dt_str = event.start_dt
    if not dt_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return dt_str[:10]


def event_identity_key(calendar_id: str, event: CalendarEvent) -> str:
    """Stable identity key for this calendar event occurrence."""
    return json.dumps([calendar_id, event.id], ensure_ascii=False, separators=(",", ":"))


def raw_input_id(calendar_id: str, event: CalendarEvent) -> str:
    """Deterministic raw input id from calendar + event occurrence identity."""
    return f"raw_gcal_event_{short_hash(event_identity_key(calendar_id, event), length=32)}"


def package_folder_name(event: CalendarEvent, calendar_id: str) -> str:
    """Deterministic package folder name for easier debugging and duplicate detection."""
    h = short_hash(event_identity_key(calendar_id, event), length=32)
    return f"{event_date(event)}__google_calendar__event_{h}"


def has_useful_content(event: CalendarEvent) -> bool:
    return bool((event.summary or "").strip() or (event.description or "").strip())


# ------------------------------------------------------------------ #
# Builders                                                            #
# ------------------------------------------------------------------ #


def build_message_json(
    event: CalendarEvent,
    calendar_id: str,
    calendar_name: str,
    raw_input_id_str: str,
    captured_at: str,
    status: str,
    review_reason: str | None = None,
) -> dict[str, Any]:
    message: dict[str, Any] = {
        "formatVersion": FORMAT_VERSION,
        "schema": SCHEMA_RAW_INPUT,
        "id": raw_input_id_str,
        "source": {
            "type": "google_calendar",
            "calendarRole": "inbox",
            "calendarId": calendar_id,
            "calendarName": calendar_name,
            "eventId": event.id,
            "iCalUID": event.ical_uid,
            "htmlLink": event.html_link or "",
        },
        "capturedAt": captured_at,
        "sourceCreatedAt": event.created or "",
        "sourceUpdatedAt": event.updated or "",
        "time": {
            "entryDate": event_date(event),
            "startDateTime": event.start_dt,
            "endDateTime": event.end_dt,
            "confidence": "source_provided",
        },
        "title": event.summary or "(no title)",
        "textPath": "raw_text.md",
        "rawEventPath": "source_event.json",
        "status": status,
    }

    if review_reason:
        message["ai"] = {
            "needsReview": True,
            "reviewReason": review_reason,
        }

    return message


def build_raw_text_md(event: CalendarEvent, calendar_name: str) -> str:
    title = event.summary or "(no title)"
    description = (event.description or "").strip()

    lines = [f"# {title}", ""]
    if description:
        lines.append(description)
        lines.append("")

    lines += [
        "---",
        "",
        "Source: Google Calendar",
        f"Calendar: {calendar_name}",
        f"Event start: {event.start_dt}",
        f"Event end: {event.end_dt}",
    ]
    return "\n".join(lines) + "\n"


def build_source_event_json(event: CalendarEvent) -> dict[str, Any]:
    """Return the raw Google Calendar API event snapshot."""
    return event.raw


# ------------------------------------------------------------------ #
# Drive helpers                                                       #
# ------------------------------------------------------------------ #


def ensure_folder_path(drive: DriveClient, root_id: str, path_parts: list[str]) -> str:
    folder = drive.ensure_path(root_id, path_parts)
    return folder.id


def find_folder_by_path(drive: DriveClient, root_id: str, path_parts: list[str] | tuple[str, ...]) -> str | None:
    current = root_id
    for part in path_parts:
        found = drive.find_child_folder(current, part)
        if not found:
            return None
        current = found.id
    return current


def _drive_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def drive_find_child_file_id(service: Any, parent_id: str, name: str) -> str | None:
    q = (
        f"'{_drive_escape(parent_id)}' in parents and "
        f"name = '{_drive_escape(name)}' and "
        "mimeType != 'application/vnd.google-apps.folder' and "
        "trashed = false"
    )
    resp = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None


def drive_download_text_by_id(service: Any, file_id: str) -> str:
    data = service.files().get_media(fileId=file_id).execute()
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return str(data)


def drive_create_or_update_text(
    service: Any,
    parent_id: str,
    name: str,
    text: str,
    mime_type: str = "text/plain",
) -> str:
    media = MediaInMemoryUpload(text.encode("utf-8"), mimetype=mime_type, resumable=False)
    existing_id = drive_find_child_file_id(service, parent_id, name)

    if existing_id:
        resp = service.files().update(fileId=existing_id, media_body=media, fields="id").execute()
        return resp["id"]

    metadata = {
        "name": name,
        "parents": [parent_id],
        "mimeType": mime_type,
    }
    resp = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return resp["id"]

# ------------------------------------------------------------------ #
# Import log                                                          #
# ------------------------------------------------------------------ #


def append_import_log(
    drive: DriveClient,
    root_id: str,
    record: dict[str, Any],
    dry_run: bool = False,
) -> None:
    if dry_run:
        print("    [dry-run] Would append import log record")
        return

    indexes_id = ensure_folder_path(drive, root_id, IMPORT_LOG_PATH)
    log_file_id = drive_find_child_file_id(drive.service, indexes_id, IMPORT_LOG_FILE)

    old_text = ""
    if log_file_id:
        old_text = drive_download_text_by_id(drive.service, log_file_id)
        if old_text and not old_text.endswith("\n"):
            old_text += "\n"

    new_line = json.dumps(record, ensure_ascii=False, sort_keys=True)
    drive_create_or_update_text(
        service=drive.service,
        parent_id=indexes_id,
        name=IMPORT_LOG_FILE,
        text=old_text + new_line + "\n",
        mime_type="application/jsonl",
    )


# ------------------------------------------------------------------ #
# Core package creation                                               #
# ------------------------------------------------------------------ #


@dataclass(frozen=True)
class CreatedPackage:
    folder_name: str
    target_path: str
    raw_id: str
    status: str
    already_complete: bool = False


@dataclass(frozen=True)
class ExistingPackage:
    parent_id: str
    folder: DriveFile
    path: tuple[str, ...]
    message: dict
    complete: bool


def calendar_package_locations(
    drive: DriveClient, root_id: str,
) -> Iterator[tuple[tuple[str, ...], str]]:
    for path in (("inbox", "new"), ("inbox", "needs_review"), STAGING_PATH):
        folder_id = find_folder_by_path(drive, root_id, path)
        if folder_id:
            yield path, folder_id

    archived = find_folder_by_path(drive, root_id, ["inbox", "archived"])
    if archived:
        for year in drive.list_children(archived, mime_type=FOLDER_MIME):
            for month in drive.list_children(year.id, mime_type=FOLDER_MIME):
                yield ("inbox", "archived", year.name, month.name), month.id


def find_calendar_package(
    drive: DriveClient, root_id: str, calendar_id: str, event: CalendarEvent,
) -> ExistingPackage | None:
    identity_suffix = raw_input_id(calendar_id, event).removeprefix("raw_gcal_")
    legacy_key = f"{calendar_id}|{event.id}|{event.start_dt}"
    legacy_name = f"{event_date(event)}__google_calendar__event_{short_hash(legacy_key)}"
    partial = None

    for path, parent_id in calendar_package_locations(drive, root_id):
        for folder in drive.list_children(parent_id, mime_type=FOLDER_MIME):
            _, marker, folder_hash = folder.name.rpartition("__google_calendar__event_")
            if not marker or (len(folder_hash) == 32 and f"event_{folder_hash}" != identity_suffix):
                continue
            files = {file.name: file for file in drive.list_children(folder.id) if not file.is_folder}
            message = json.loads(drive.download_text(files["MESSAGE.json"])) if "MESSAGE.json" in files else {}
            source = message.get("source", {})
            if message:
                matches = (source.get("type"), source.get("calendarId"), source.get("eventId")) == (
                    "google_calendar", calendar_id, event.id,
                )
            else:
                matches = folder.name.endswith(f"__google_calendar__{identity_suffix}") or folder.name == legacy_name
            if not matches:
                continue

            complete = bool(message.get("id")) and {"raw_text.md", "source_event.json"} <= files.keys()
            package = ExistingPackage(parent_id, folder, path, message, complete)
            if complete and path != STAGING_PATH:
                return package
            if partial is None:
                partial = package

    return partial


def create_calendar_package(
    drive: DriveClient,
    root_id: str,
    event: CalendarEvent,
    calendar_id: str,
    calendar_name: str,
    dry_run: bool = False,
) -> CreatedPackage:
    """
    Create a structured package from one calendar event.

    Useful events go to inbox/new/.
    Empty/ambiguous events go to inbox/needs_review/.
    """
    captured_at = utc_now_iso()
    raw_id = raw_input_id(calendar_id, event)
    folder_name = package_folder_name(event, calendar_id)

    existing = None if dry_run else find_calendar_package(drive, root_id, calendar_id, event)
    if existing:
        folder_name = existing.folder.name
        raw_id = existing.message.get("id") or raw_id
        if existing.complete and existing.path != STAGING_PATH:
            return CreatedPackage(
                folder_name, "/".join(existing.path) + "/", raw_id,
                existing.message.get("status", "new"), already_complete=True,
            )
        if existing.path[:2] == ("inbox", "archived"):
            raise RuntimeError(f"Archived package is incomplete: {folder_name}")

    status = "new" if has_useful_content(event) else "needs_review"
    target_parts = ["inbox", status]
    review_reason = None
    if status == "needs_review":
        review_reason = "Google Calendar event has neither title nor description."

    target_path = "/".join(target_parts) + "/"

    message = build_message_json(
        event=event,
        calendar_id=calendar_id,
        calendar_name=calendar_name,
        raw_input_id_str=raw_id,
        captured_at=captured_at,
        status=status,
        review_reason=review_reason,
    )
    raw_text = build_raw_text_md(event, calendar_name)
    source_event = build_source_event_json(event)

    print(f"  → Package folder: {target_path}{folder_name}")
    print(f"    Raw input id:    {raw_id}")
    print(f"    Status:          {status}")
    print(f"    Title:           {event.summary or '(no title)'}")
    print(f"    Start:           {event.start_dt}")

    if dry_run:
        print("    [dry-run] Would create MESSAGE.json, raw_text.md, source_event.json")
        return CreatedPackage(folder_name=folder_name, target_path=target_path, raw_id=raw_id, status=status)

    staging_id = ensure_folder_path(drive, root_id, list(STAGING_PATH))
    if existing:
        pkg_folder_id = existing.folder.id
        if existing.parent_id != staging_id:
            drive.move_file(pkg_folder_id, staging_id, old_parent_ids=[existing.parent_id])
    else:
        pkg_folder_id = drive.create_folder(staging_id, folder_name).id

    # Retry staged writes in place and publish only after all three writes succeed.
    drive.upsert_text(pkg_folder_id, "raw_text.md", raw_text, mime_type="text/markdown")
    drive.upsert_json(pkg_folder_id, "source_event.json", source_event)
    drive.upsert_json(pkg_folder_id, "MESSAGE.json", message)

    target_folder_id = ensure_folder_path(drive, root_id, target_parts)
    drive.move_file(pkg_folder_id, target_folder_id, old_parent_ids=[staging_id])

    return CreatedPackage(folder_name=folder_name, target_path=target_path, raw_id=raw_id, status=status)


# ------------------------------------------------------------------ #
# Workflow                                                            #
# ------------------------------------------------------------------ #


@dataclass
class WorkflowResult:
    event_id: str
    title: str
    raw_id: str
    folder_name: str
    success: bool
    skipped: bool = False
    moved: bool = False
    status: str = ""
    error: str = ""


def resolve_calendar_id(cal: CalendarClient, explicit_id: str, name: str, label: str) -> str:
    if explicit_id:
        print(f"{label}: {name} ({explicit_id})")
        return explicit_id

    print(f"Looking up {label.lower()}: '{name}' ...")
    calendar_id = cal.find_calendar_id(name)
    if calendar_id:
        print(f"  {label} id: {calendar_id}")
        return calendar_id

    print(f"ERROR: Calendar '{name}' not found.")
    print("Available calendars:")
    for calendar in cal.list_calendars():
        print(f"  - {calendar.get('summary')} (id: {calendar.get('id')})")
    sys.exit(1)


def try_move_event(
    cal: CalendarClient,
    inbox_calendar_id: str,
    event_id: str,
    processed_calendar_id: str,
    processed_calendar_name: str,
    dry_run: bool,
) -> bool:
    if dry_run:
        print(f"    [dry-run] Would move event to '{processed_calendar_name}'")
        return False

    cal.move_event(inbox_calendar_id, event_id, processed_calendar_id)
    print(f"    ✓ Event moved to '{processed_calendar_name}'")
    return True

def run_workflow(
    drive: DriveClient,
    cal: CalendarClient,
    root_folder_id: str,
    inbox_calendar_name: str,
    processed_calendar_name: str,
    inbox_calendar_id: str = "",
    processed_calendar_id: str = "",
    days_back: int = 30,
    days_forward: int = 30,
    limit: int = 5,
    dry_run: bool = False,
) -> list[WorkflowResult]:
    results: list[WorkflowResult] = []

    inbox_cal_id = resolve_calendar_id(cal, inbox_calendar_id, inbox_calendar_name, "Inbox calendar")
    processed_cal_id = resolve_calendar_id(cal, processed_calendar_id, processed_calendar_name, "Processed calendar")

    now = datetime.now(timezone.utc)
    time_min = now - timedelta(days=days_back)
    time_max = now + timedelta(days=days_forward)

    print(f"\nFetching events from '{inbox_calendar_name}' ...")
    print(f"  Range: {time_min.date()} → {time_max.date()}")

    events = cal.list_events(inbox_cal_id, time_min, time_max)
    print(f"  Found {len(events)} event(s)")

    if not events:
        print("Nothing to import.")
        return results

    batch = events[:limit]
    print(f"  Importing batch of {len(batch)} event(s) (limit={limit})")

    for i, event in enumerate(batch, 1):
        title = event.summary or "(no title)"
        raw_id = raw_input_id(inbox_cal_id, event)

        print(f"\n[{i}/{len(batch)}] Event: {title}")

        try:
            created = create_calendar_package(
                drive=drive,
                root_id=root_folder_id,
                event=event,
                calendar_id=inbox_cal_id,
                calendar_name=inbox_calendar_name,
                dry_run=dry_run,
            )
        except Exception as exc:
            print(f"  ✗ Failed to create inbox package: {exc}")
            results.append(
                WorkflowResult(
                    event_id=event.id,
                    title=event.summary or "",
                    raw_id=raw_id,
                    folder_name="",
                    success=False,
                    error=str(exc),
                )
            )
            continue

        if not created.already_complete:
            import_record = {
                "formatVersion": FORMAT_VERSION,
                "source": "google_calendar",
                "rawInputId": created.raw_id,
                "calendarId": inbox_cal_id,
                "calendarName": inbox_calendar_name,
                "eventId": event.id,
                "iCalUID": event.ical_uid,
                "eventStart": event.start_dt,
                "eventEnd": event.end_dt,
                "sourceUpdatedAt": event.updated or "",
                "packagePath": f"{created.target_path}{created.folder_name}/",
                "packageStatus": created.status,
                "importedAt": utc_now_iso(),
            }

            try:
                append_import_log(drive, root_folder_id, import_record, dry_run=dry_run)
                if not dry_run:
                    print(f"    ✓ Import logged in indexes/{IMPORT_LOG_FILE}")
            except Exception as exc:
                # Package exists; log failure should not cause duplicate package creation in this run.
                print(f"    ⚠  Package created, but import log update failed: {exc}")

        moved = False
        move_error = ""
        try:
            moved = try_move_event(
                cal=cal,
                inbox_calendar_id=inbox_cal_id,
                event_id=event.id,
                processed_calendar_id=processed_cal_id,
                processed_calendar_name=processed_calendar_name,
                dry_run=dry_run,
            )
        except Exception as exc:
            print(f"    ⚠  Package saved, but calendar move failed: {exc}")
            move_error = str(exc)

        results.append(
            WorkflowResult(
                event_id=event.id,
                title=event.summary or "",
                raw_id=created.raw_id,
                folder_name=created.folder_name,
                success=not move_error,
                skipped=created.already_complete,
                moved=moved,
                status="already_imported" if created.already_complete else created.status,
                error=move_error,
            )
        )

    return results


# ------------------------------------------------------------------ #
# CLI                                                                 #
# ------------------------------------------------------------------ #


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Diary — import Google Calendar events into the file inbox"
    )
    parser.add_argument("--root-folder-id", required=True, help="Google Drive root folder id for AI Diary")
    parser.add_argument("--inbox-calendar", default="Дневничок", help="Name of the inbox calendar")
    parser.add_argument("--inbox-calendar-id", default="", help="Direct inbox calendar id; skips name lookup")
    parser.add_argument("--processed-calendar", default="Дневничок обработанное", help="Name of the processed calendar")
    parser.add_argument("--processed-calendar-id", default="", help="Direct processed calendar id; skips name lookup")
    parser.add_argument("--credentials", default="google_credentials.json", help="Path to OAuth credentials JSON")
    parser.add_argument("--token", default="google_token.json", help="Path to OAuth token JSON")
    parser.add_argument("--days-back", type=int, default=30, help="Days back to scan (default: 30)")
    parser.add_argument("--days-forward", type=int, default=30, help="Days forward to scan (default: 30)")
    parser.add_argument("--limit", type=int, default=5, help="Max events to import per run (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes")
    return parser.parse_args()


def build_drive_client_from_creds(credentials_path: str | Path, token_path: str | Path, creds: Any) -> DriveClient:
    """
    Build the existing Mamton DriveClient from already-authorized credentials.

    This mirrors the current project style and avoids running a separate Drive auth flow.
    """
    drive_service = gapi_build("drive", "v3", credentials=creds)
    drive = DriveClient.__new__(DriveClient)
    drive.credentials_file = Path(credentials_path)
    drive.token_file = Path(token_path)
    drive.scopes = CALENDAR_SCOPES
    drive.service = drive_service
    return drive


def main() -> None:
    args = parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE — no changes will be made")
        print("=" * 60)

    print("\nAuthorizing with shared Drive + Calendar token ...")
    creds = get_credentials(args.credentials, args.token)

    print("Building Google Drive client ...")
    drive = build_drive_client_from_creds(args.credentials, args.token, creds)

    print("Building Google Calendar client ...")
    cal = build_calendar_client_from_creds(creds)

    print(f"Root folder id: {args.root_folder_id}\n")

    results = run_workflow(
        drive=drive,
        cal=cal,
        root_folder_id=args.root_folder_id,
        inbox_calendar_name=args.inbox_calendar,
        processed_calendar_name=args.processed_calendar,
        inbox_calendar_id=args.inbox_calendar_id,
        processed_calendar_id=args.processed_calendar_id,
        days_back=args.days_back,
        days_forward=args.days_forward,
        limit=args.limit,
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = len(results)
    imported = sum(1 for r in results if r.success and not r.skipped)
    skipped = sum(1 for r in results if r.skipped)
    failed = sum(1 for r in results if not r.success)
    moved = sum(1 for r in results if r.moved)
    needs_review = sum(1 for r in results if r.status == "needs_review")

    print(f"  Total events examined: {total}")
    print(f"  Packages imported:     {imported}")
    print(f"  Already imported:      {skipped}")
    print(f"  Needs review packages: {needs_review}")
    print(f"  Events moved:          {moved}")
    print(f"  Errors:                {failed}")

    if failed:
        print("\nFailed events:")
        for result in results:
            if not result.success:
                print(f"  - {result.title or result.event_id}: {result.error}")

    if args.dry_run:
        print("\n[dry-run] No changes were made to Drive or Calendar.")

    print("\nNext step: run the existing Inbox-to-Entry workflow to convert inbox/new packages into entries.")


if __name__ == "__main__":
    main()
