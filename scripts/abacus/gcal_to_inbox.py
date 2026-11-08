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

This log is used as a simple duplicate guard. It is derived/debug data and can
be rebuilt later from processed raw sources or entries if needed.

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
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from googleapiclient.discovery import build as gapi_build
from googleapiclient.http import MediaInMemoryUpload

from drive_client import DriveClient
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
    return f"{calendar_id}|{event.id}|{event.start_dt}"


def raw_input_id(calendar_id: str, event: CalendarEvent) -> str:
    """Deterministic raw input id from calendar + event occurrence identity."""
    return f"raw_gcal_event_{short_hash(event_identity_key(calendar_id, event))}"


def package_folder_name(event: CalendarEvent, calendar_id: str) -> str:
    """Deterministic package folder name for easier debugging and duplicate detection."""
    h = short_hash(event_identity_key(calendar_id, event))
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


def find_folder_by_path(drive: DriveClient, root_id: str, path_parts: list[str]) -> str | None:
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
# Import log / duplicate guard                                        #
# ------------------------------------------------------------------ #


def read_import_log(drive: DriveClient, root_id: str) -> list[dict[str, Any]]:
    indexes_id = find_folder_by_path(drive, root_id, IMPORT_LOG_PATH)
    if not indexes_id:
        return []

    log_file_id = drive_find_child_file_id(drive.service, indexes_id, IMPORT_LOG_FILE)
    if not log_file_id:
        return []

    text = drive_download_text_by_id(drive.service, log_file_id)
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            # Keep the importer tolerant. Broken debug log lines should not block capture.
            continue
    return records


def already_imported(drive: DriveClient, root_id: str, raw_id: str) -> bool:
    for record in read_import_log(drive, root_id):
        if record.get("rawInputId") == raw_id:
            return True

    # Fallback for old packages created before the log existed: scan inbox/new only.
    new_folder_id = find_folder_by_path(drive, root_id, ["inbox", "new"])
    if new_folder_id:
        for folder in drive.list_children(new_folder_id):
            if folder.mime_type != FOLDER_MIME:
                continue
            try:
                msg_file = next((f for f in drive.list_children(folder.id) if f.name == "MESSAGE.json"), None)
                if not msg_file:
                    continue
                data = json.loads(drive.download_text(msg_file))
                if data.get("id") == raw_id:
                    return True
            except Exception:
                continue

    return False


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

    if has_useful_content(event):
        target_parts = ["inbox", "new"]
        status = "new"
        review_reason = None
    else:
        target_parts = ["inbox", "needs_review"]
        status = "needs_review"
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

    target_folder_id = ensure_folder_path(drive, root_id, target_parts)
    existing_pkg = drive.find_child_folder(target_folder_id, folder_name)
    if existing_pkg:
        raise RuntimeError(f"Package folder already exists: {target_path}{folder_name}")

    pkg_folder = drive.create_folder(target_folder_id, folder_name)
    pkg_folder_id = pkg_folder.id

    drive.upload_text(
        pkg_folder_id,
        "MESSAGE.json",
        json.dumps(message, ensure_ascii=False, indent=2),
        mime_type="application/json",
    )
    drive.upload_text(pkg_folder_id, "raw_text.md", raw_text, mime_type="text/markdown")
    drive.upload_text(
        pkg_folder_id,
        "source_event.json",
        json.dumps(source_event, ensure_ascii=False, indent=2),
        mime_type="application/json",
    )

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

        if not dry_run and already_imported(drive, root_folder_id, raw_id):
            print(f"  ⏭  Already imported (raw_id={raw_id}).")
            moved = False
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
                print(f"    ⚠  Already imported, but move failed: {exc}")

            results.append(
                WorkflowResult(
                    event_id=event.id,
                    title=event.summary or "",
                    raw_id=raw_id,
                    folder_name="",
                    success=True,
                    skipped=True,
                    moved=moved,
                    status="already_imported",
                )
            )
            continue

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
            print(f"    ⚠  Package created, but calendar move failed: {exc}")
            print("       Next run should skip this event via the import log.")

        results.append(
            WorkflowResult(
                event_id=event.id,
                title=event.summary or "",
                raw_id=created.raw_id,
                folder_name=created.folder_name,
                success=True,
                moved=moved,
                status=created.status,
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
