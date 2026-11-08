#!/usr/bin/env python3
"""
AI Diary — Google Calendar Timeline Projection

One-way sync: entries/ in Google Drive → Google Calendar timeline.

This script:
- Reads ENTRY.json files from entries/ in Drive
- Creates or updates Google Calendar events
- Tracks the mapping in indexes/google_calendar_events.jsonl
- Writes a run log to _runs/calendar_sync_YYYY-MM-DD_NNN.json
- Does NOT modify diary entry files
- Treats Google Calendar as a rebuildable projection, not as source of truth

Usage:

    # Dry run — should not write anything to Drive or Calendar
    python gcal_projection_fixed.py \
      --root-folder-id YOUR_ROOT_FOLDER_ID \
      --credentials google_credentials.json \
      --token google_token.json \
      --dry-run

    # Sync up to 20 entries
    python gcal_projection_fixed.py \
      --root-folder-id YOUR_ROOT_FOLDER_ID \
      --credentials google_credentials.json \
      --token google_token.json \
      --limit 20

    # Sync only a date range
    python gcal_projection_fixed.py \
      --root-folder-id YOUR_ROOT_FOLDER_ID \
      --from-date 2026-04-01 \
      --to-date 2026-04-30

Important:
- If your existing token was created without Calendar or Drive scopes,
  delete google_token.json once and re-run the script to grant the new scopes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, date
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build as gapi_build

from mamton_drive_client import DriveClient, DriveFile


# ------------------------------------------------------------------ #
# Constants                                                           #
# ------------------------------------------------------------------ #

FORMAT_VERSION = "v0.1.0"
DRIVE_FOLDER_MIME = "application/vnd.google-apps.folder"

REQUIRED_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]

DEFAULT_PROJECTION_CONFIG = {
    "formatVersion": FORMAT_VERSION,
    "schema": "google_calendar_projection",
    "enabled": True,
    "syncMode": "one_way_files_to_calendar",
    "calendarName": "AI Diary Timeline",
    "calendarId": None,
    "includeStatuses": [
        "raw",
        "processed",
        "needs_review",
        "ai_proposed",
        "user_edited",
        "failed",
    ],
    "colorBy": "entry.status",
    "defaultDurationMinutes": 30,
    "dateOnlyEntriesAsAllDay": True,
    "includeTagsInTitle": True,
    "maxTagsInTitle": 3,
    "includeAssetLinksInDescription": True,
    "writeBackFromCalendar": False,
    "statusColors": {
        "raw": "grey",
        "processed": "green",
        "needs_review": "yellow",
        "ai_proposed": "blue",
        "user_edited": "purple",
        "failed": "red",
        "archived": "grey",
    },
}

# Abstract names from our config/spec -> Google Calendar event colorId.
# The exact palette can be checked via Calendar API colors().get(), but these
# IDs are stable enough for MVP and can be changed in config later.
STATUS_COLOR_ID: dict[str, str] = {
    "lavender": "1",
    "sage": "2",
    "grape": "3",
    "flamingo": "4",
    "banana": "5",
    "tangerine": "6",
    "peacock": "7",
    "graphite": "8",
    "blueberry": "9",
    "basil": "10",
    "tomato": "11",

    # Friendly aliases used by our config.
    "grey": "8",
    "gray": "8",
    "green": "2",
    "yellow": "5",
    "blue": "7",
    "purple": "3",
    "red": "11",
    "orange": "6",
}

STATUS_ICON: dict[str, str] = {
    "raw": "📝",
    "processed": "✅",
    "needs_review": "❓",
    "ai_proposed": "🤖",
    "user_edited": "✍️",
    "failed": "⚠️",
    "archived": "🗄️",
}

ASSET_ICON: dict[str, str] = {
    "image": "📷",
    "photo": "📷",
    "video": "🎬",
    "audio": "🎙️",
    "voice": "🎙️",
    "document": "📄",
    "pdf": "📄",
    "file": "📎",
}


# ------------------------------------------------------------------ #
# Auth                                                                #
# ------------------------------------------------------------------ #

def get_credentials(credentials_file: str, token_file: str) -> Credentials:
    """Authorize with both Drive and Calendar scopes.

    If the token exists but does not contain the required scopes, the script
    starts a new OAuth flow and overwrites the token.
    """
    creds: Credentials | None = None
    token_path = Path(token_file)

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), REQUIRED_SCOPES)
        except Exception:
            creds = None

    if creds and not _has_required_scopes(creds):
        print("  Existing token does not contain required Drive+Calendar scopes.")
        print("  Re-authorizing and overwriting token file.")
        creds = None

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, REQUIRED_SCOPES)
        creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _has_required_scopes(creds: Credentials) -> bool:
    try:
        return creds.has_scopes(REQUIRED_SCOPES)
    except Exception:
        granted = set(getattr(creds, "scopes", None) or [])
        return set(REQUIRED_SCOPES).issubset(granted)


def build_drive_client(credentials_file: str, token_file: str, creds: Credentials) -> DriveClient:
    """Build mamton DriveClient around an already authorized Drive service.

    This keeps compatibility with the existing project where DriveClient methods
    are used for file operations, but authorization is shared with Calendar.
    """
    drive_service = gapi_build("drive", "v3", credentials=creds)

    drive = DriveClient.__new__(DriveClient)
    drive.credentials_file = Path(credentials_file)
    drive.token_file = Path(token_file)
    drive.scopes = REQUIRED_SCOPES
    drive.service = drive_service
    return drive


# ------------------------------------------------------------------ #
# Generic helpers                                                     #
# ------------------------------------------------------------------ #

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def entry_hash(entry_json_text: str, entry_md_text: str) -> str:
    h = hashlib.sha256()
    h.update(entry_json_text.encode("utf-8"))
    h.update(b"\n---entry.md---\n")
    h.update(entry_md_text.encode("utf-8"))
    return "sha256:" + h.hexdigest()[:16]


def run_log_name(existing_names: list[str]) -> str:
    date_str = utc_now().strftime("%Y-%m-%d")
    prefix = f"calendar_sync_{date_str}_"
    nums: list[int] = []
    for name in existing_names:
        if name.startswith(prefix) and name.endswith(".json"):
            maybe_num = name[len(prefix): len(prefix) + 3]
            if maybe_num.isdigit():
                nums.append(int(maybe_num))
    next_num = (max(nums) + 1) if nums else 1
    return f"{prefix}{next_num:03d}.json"


def parse_ymd(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def drive_folder_url(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}"


# ------------------------------------------------------------------ #
# Drive path helpers                                                  #
# ------------------------------------------------------------------ #

def find_path(drive: DriveClient, root_id: str, parts: list[str]) -> DriveFile | None:
    """Find a nested folder path without creating anything."""
    current_id = root_id
    current: DriveFile | None = None
    for part in parts:
        current = drive.find_child_folder(current_id, part)
        if not current:
            return None
        current_id = current.id
    return current


def find_file(drive: DriveClient, parent_id: str, name: str) -> DriveFile | None:
    children = drive.list_children(parent_id, name=name)
    return children[0] if children else None


def read_json_file(drive: DriveClient, file: DriveFile) -> dict[str, Any] | list[Any] | None:
    try:
        text = drive.download_text(file)
        return json.loads(text)
    except Exception:
        return None


def read_text_file(drive: DriveClient, file: DriveFile) -> str:
    try:
        return drive.download_text(file)
    except Exception:
        return ""


def write_json_file(drive: DriveClient, parent_id: str, name: str, data: dict | list) -> DriveFile:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    return drive.upsert_text(parent_id, name, text, mime_type="application/json")


def read_jsonl_file(drive: DriveClient, file: DriveFile | None) -> list[dict[str, Any]]:
    if not file:
        return []

    text = read_text_file(drive, file)
    result: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
            if isinstance(value, dict):
                result.append(value)
        except json.JSONDecodeError:
            print(f"  Warning: invalid JSONL line {line_no} in {file.name}; skipped.")
    return result

# ------------------------------------------------------------------ #
# Tag catalog                                                         #
# ------------------------------------------------------------------ #

def load_tag_catalog(drive: DriveClient, root_id: str) -> dict[str, str]:
    """Load catalogs/tags/tags.json and return {tagId_or_alias: displayName}.

    Supports the current AI Diary format:

        {
          "formatVersion": "v0.1.0",
          "items": [
            {"id": "tag_lis", "name": "Lis", "aliases": ["Лис"]}
          ]
        }

    Also supports older/debug formats:
    - [{"id": ..., "name": ...}]
    - {"tag_id": {"name": ...}}
    - {"tag_id": "Display name"}
    """
    tags_folder = find_path(drive, root_id, ["catalogs", "tags"])
    if not tags_folder:
        return {}

    tag_map: dict[str, str] = {}

    tags_file = find_file(drive, tags_folder.id, "tags.json")
    data = read_json_file(drive, tags_file) if tags_file else None

    def add_item(item: dict[str, Any]) -> None:
        tag_id = item.get("id") or item.get("tagId") or item.get("slug")
        display_name = item.get("name") or item.get("title") or tag_id
        if not tag_id or not display_name:
            return
        tag_map[str(tag_id)] = str(display_name)

        # Useful fallbacks: slug/name can also resolve to the same display name.
        if item.get("slug"):
            tag_map[str(item["slug"])] = str(display_name)
        if item.get("name"):
            tag_map[str(item["name"])] = str(display_name)

        aliases = item.get("aliases") or []
        if isinstance(aliases, list):
            for alias in aliases:
                if isinstance(alias, str) and alias.strip():
                    tag_map[alias.strip()] = str(display_name)

    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    add_item(item)
        else:
            for key, value in data.items():
                if key in {"formatVersion", "schema"}:
                    continue
                if isinstance(value, dict):
                    item = dict(value)
                    item.setdefault("id", key)
                    add_item(item)
                elif isinstance(value, str):
                    tag_map[key] = value
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                add_item(item)

    aliases_file = find_file(drive, tags_folder.id, "aliases.json")
    aliases = read_json_file(drive, aliases_file) if aliases_file else None
    if isinstance(aliases, dict):
        # Supports either {"alias": "tag_id"} or {"items": [{"alias": ..., "tagId": ...}]}
        alias_items = aliases.get("items")
        if isinstance(alias_items, list):
            for item in alias_items:
                if not isinstance(item, dict):
                    continue
                alias = item.get("alias") or item.get("name")
                canonical = item.get("tagId") or item.get("id") or item.get("canonical")
                if alias and canonical and canonical in tag_map:
                    tag_map[str(alias)] = tag_map[str(canonical)]
        else:
            for alias, canonical in aliases.items():
                if alias in {"formatVersion", "schema"}:
                    continue
                if isinstance(canonical, str) and canonical in tag_map:
                    tag_map[str(alias)] = tag_map[canonical]

    return tag_map


def extract_tag_ids(raw_tags: list[Any]) -> list[str]:
    """Extract tag identifiers from ENTRY.json tags.

    Supports both:
      "tags": ["tag_lis"]
    and:
      "tags": [{"tagId": "tag_lis", "source": "ai"}]
    """
    result: list[str] = []
    for item in raw_tags:
        if isinstance(item, str):
            if item.strip():
                result.append(item.strip())
        elif isinstance(item, dict):
            tag_id = (
                item.get("tagId")
                or item.get("id")
                or item.get("slug")
                or item.get("name")
            )
            if tag_id:
                result.append(str(tag_id).strip())
    return result


def resolve_tags(tag_ids: list[str], tag_catalog: dict[str, str]) -> tuple[list[str], list[str]]:
    result: list[str] = []
    unresolved: list[str] = []

    for tag_id in tag_ids:
        display_name = tag_catalog.get(tag_id)
        if display_name:
            result.append(display_name)
        else:
            result.append(tag_id)
            unresolved.append(tag_id)

    # Preserve order, remove duplicates.
    return dedupe_keep_order(result), dedupe_keep_order(unresolved)


def dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


# ------------------------------------------------------------------ #
# Config                                                              #
# ------------------------------------------------------------------ #

def load_or_create_config(drive: DriveClient, root_id: str, dry_run: bool) -> dict[str, Any]:
    """Load projection config.

    In dry-run mode this function must not create _system/integrations.
    """
    system_integrations = find_path(drive, root_id, ["_system", "integrations"])

    if system_integrations:
        config_file = find_file(drive, system_integrations.id, "google_calendar_projection.json")
        if config_file:
            data = read_json_file(drive, config_file)
            if isinstance(data, dict):
                print("  Config loaded from Drive.")
                return _merge_config_with_defaults(data)

    print("  Config not found — using defaults.")

    if not dry_run:
        system_integrations = drive.ensure_path(root_id, ["_system", "integrations"])
        write_json_file(
            drive,
            system_integrations.id,
            "google_calendar_projection.json",
            DEFAULT_PROJECTION_CONFIG,
        )
        print("  Default config written to _system/integrations/google_calendar_projection.json")

    return dict(DEFAULT_PROJECTION_CONFIG)


def _merge_config_with_defaults(config: dict[str, Any]) -> dict[str, Any]:
    merged = dict(DEFAULT_PROJECTION_CONFIG)
    merged.update(config)

    # Merge nested statusColors instead of replacing defaults completely.
    status_colors = dict(DEFAULT_PROJECTION_CONFIG.get("statusColors", {}))
    status_colors.update(config.get("statusColors") or {})
    merged["statusColors"] = status_colors
    return merged


def save_config(drive: DriveClient, root_id: str, config: dict[str, Any]) -> None:
    system_folder = drive.ensure_path(root_id, ["_system", "integrations"])
    write_json_file(drive, system_folder.id, "google_calendar_projection.json", config)


# ------------------------------------------------------------------ #
# Sync index                                                          #
# ------------------------------------------------------------------ #

def load_sync_index(drive: DriveClient, root_id: str) -> tuple[dict[str, dict[str, Any]], int]:
    """Load indexes/google_calendar_events.jsonl.

    Returns ({entryId: latest_record}, duplicate_count).
    When multiple records exist for the same entryId, keeps the one with the
    latest lastSyncedAt string.
    """
    indexes_folder = find_path(drive, root_id, ["indexes"])
    if not indexes_folder:
        return {}, 0

    idx_file = find_file(drive, indexes_folder.id, "google_calendar_events.jsonl")
    records = read_jsonl_file(drive, idx_file)

    seen: dict[str, dict[str, Any]] = {}
    duplicate_count = 0

    for record in records:
        entry_id = record.get("entryId")
        if not entry_id:
            continue

        if entry_id in seen:
            duplicate_count += 1
            existing_ts = seen[entry_id].get("lastSyncedAt", "")
            new_ts = record.get("lastSyncedAt", "")
            if new_ts > existing_ts:
                seen[entry_id] = record
        else:
            seen[entry_id] = record

    return seen, duplicate_count


def upsert_sync_record(drive: DriveClient, root_id: str, record: dict[str, Any]) -> None:
    """Rewrite indexes/google_calendar_events.jsonl with one record per entryId."""
    indexes_folder = drive.ensure_path(root_id, ["indexes"])
    idx_file = find_file(drive, indexes_folder.id, "google_calendar_events.jsonl")
    existing = read_jsonl_file(drive, idx_file)

    replaced = False
    new_records: list[dict[str, Any]] = []

    for old_record in existing:
        if old_record.get("entryId") == record["entryId"]:
            if not replaced:
                new_records.append(record)
                replaced = True
            # Skip duplicate old records for the same entryId.
        else:
            new_records.append(old_record)

    if not replaced:
        new_records.append(record)

    text = "\n".join(json.dumps(item, ensure_ascii=False) for item in new_records) + "\n"
    drive.upsert_text(
        indexes_folder.id,
        "google_calendar_events.jsonl",
        text,
        mime_type="application/x-ndjson",
    )


# ------------------------------------------------------------------ #
# Entry discovery                                                     #
# ------------------------------------------------------------------ #

@dataclass
class EntryData:
    folder_id: str
    folder_path: str
    entry_json: dict[str, Any]
    entry_json_text: str
    entry_md_text: str
    resolved_tags: list[str] = field(default_factory=list)
    unresolved_tag_ids: list[str] = field(default_factory=list)


def collect_entries(
    drive: DriveClient,
    root_id: str,
    include_statuses: list[str],
    limit: int,
    tag_catalog: dict[str, str] | None = None,
    from_date: str = "",
    to_date: str = "",
    parse_errors: list[dict[str, Any]] | None = None,
) -> list[EntryData]:
    """Walk entries/YYYY/MM/... in Drive and collect entry folders."""
    entries_folder = find_path(drive, root_id, ["entries"])
    if not entries_folder:
        print("  No entries/ folder found in Drive root.")
        return []

    errors = parse_errors if parse_errors is not None else []
    results: list[EntryData] = []

    _walk_entries(
        drive=drive,
        folder_id=entries_folder.id,
        path_hint="entries",
        include_statuses=include_statuses,
        results=results,
        limit=limit,
        tag_catalog=tag_catalog or {},
        from_date=from_date,
        to_date=to_date,
        parse_errors=errors,
    )

    results.sort(key=lambda item: (
        (item.entry_json.get("time") or {}).get("entryDate", ""),
        item.folder_path,
    ))
    return results


def _walk_entries(
    drive: DriveClient,
    folder_id: str,
    path_hint: str,
    include_statuses: list[str],
    results: list[EntryData],
    limit: int,
    tag_catalog: dict[str, str],
    from_date: str,
    to_date: str,
    parse_errors: list[dict[str, Any]],
) -> None:
    if limit > 0 and len(results) >= limit:
        return

    try:
        children = sorted(drive.list_children(folder_id), key=lambda f: f.name)
    except Exception as exc:
        parse_errors.append({"path": path_hint, "error": "list_children_failed", "detail": str(exc)})
        return

    for child in children:
        if limit > 0 and len(results) >= limit:
            return
        if not child.is_folder:
            continue

        child_path = f"{path_hint}/{child.name}"
        entry_file = find_file(drive, child.id, "ENTRY.json")

        if entry_file:
            _collect_one_entry_folder(
                drive=drive,
                entry_folder=child,
                entry_file=entry_file,
                child_path=child_path,
                include_statuses=include_statuses,
                results=results,
                tag_catalog=tag_catalog,
                from_date=from_date,
                to_date=to_date,
                parse_errors=parse_errors,
            )
        else:
            _walk_entries(
                drive=drive,
                folder_id=child.id,
                path_hint=child_path,
                include_statuses=include_statuses,
                results=results,
                limit=limit,
                tag_catalog=tag_catalog,
                from_date=from_date,
                to_date=to_date,
                parse_errors=parse_errors,
            )


def _collect_one_entry_folder(
    drive: DriveClient,
    entry_folder: DriveFile,
    entry_file: DriveFile,
    child_path: str,
    include_statuses: list[str],
    results: list[EntryData],
    tag_catalog: dict[str, str],
    from_date: str,
    to_date: str,
    parse_errors: list[dict[str, Any]],
) -> None:
    try:
        entry_json_text = drive.download_text(entry_file)
        entry_json = json.loads(entry_json_text)
        if not isinstance(entry_json, dict):
            raise ValueError("ENTRY.json must be a JSON object")
    except Exception as exc:
        parse_errors.append({
            "entryPath": child_path + "/ENTRY.json",
            "error": "invalid_json",
            "detail": str(exc),
        })
        return

    status = entry_json.get("status", "")
    if include_statuses and status not in include_statuses:
        return

    entry_date = (entry_json.get("time") or {}).get("entryDate", "")
    if from_date and entry_date and entry_date < from_date:
        return
    if to_date and entry_date and entry_date > to_date:
        return

    entry_md_files = drive.list_children(entry_folder.id, name="entry.md")
    entry_md_text = drive.download_text(entry_md_files[0]) if entry_md_files else ""

    raw_tags = entry_json.get("tags") or []
    tag_ids = extract_tag_ids(raw_tags) if isinstance(raw_tags, list) else []
    resolved_tags, unresolved_tag_ids = resolve_tags(tag_ids, tag_catalog)

    results.append(EntryData(
        folder_id=entry_folder.id,
        folder_path=child_path,
        entry_json=entry_json,
        entry_json_text=entry_json_text,
        entry_md_text=entry_md_text,
        resolved_tags=resolved_tags,
        unresolved_tag_ids=unresolved_tag_ids,
    ))

# ------------------------------------------------------------------ #
# Calendar event rendering                                            #
# ------------------------------------------------------------------ #

def render_event_title(entry: dict[str, Any], config: dict[str, Any], resolved_tags: list[str]) -> str:
    status = entry.get("status", "raw")
    status_icon = STATUS_ICON.get(status, "📝")
    asset_part = render_asset_icon_summary(entry, config)
    title = entry.get("title") or "(без названия)"

    parts = [status_icon]
    if asset_part:
        parts.append(asset_part)
    parts.append(title)

    base_title = " ".join(parts)

    if config.get("includeTagsInTitle", True) and resolved_tags:
        max_tags = int(config.get("maxTagsInTitle", 3) or 3)
        tag_labels = [_hashtag(label) for label in resolved_tags[:max_tags]]
        return base_title + " · " + " ".join(tag_labels)

    return base_title


def render_asset_icon_summary(entry: dict[str, Any], config: dict[str, Any]) -> str:
    if not config.get("includeAssetLinksInDescription", True):
        return ""

    assets = extract_assets(entry)
    if not assets:
        return ""

    counts: dict[str, int] = {}
    for asset in assets:
        asset_type = _canonical_asset_type(asset.get("type") or asset.get("assetType") or "file")
        counts[asset_type] = counts.get(asset_type, 0) + 1

    parts: list[str] = []
    for asset_type, icon in [("image", "📷"), ("audio", "🎙️"), ("video", "🎬"), ("document", "📄"), ("file", "📎")]:
        count = counts.get(asset_type, 0)
        if count == 1:
            parts.append(icon)
        elif count > 1:
            parts.append(f"{icon}{count}")
    return " ".join(parts)


def render_event_description(
    entry: dict[str, Any],
    folder_path: str,
    folder_id: str,
    resolved_tags: list[str],
    unresolved_tag_ids: list[str],
    entry_md_text: str,
) -> str:
    lines = ["AI Diary Entry", ""]
    lines.append(f"Entry ID: {entry.get('id', '')}")
    lines.append(f"Status: {entry.get('status', '')}")

    time_info = entry.get("time") or {}
    confidence = time_info.get("confidence", "")
    if confidence:
        lines.append(f"Time confidence: {confidence}")

    if resolved_tags:
        lines += ["", "Tags:"]
        lines.append(" ".join(_hashtag(label) for label in resolved_tags))

    if unresolved_tag_ids:
        lines += ["", "Unresolved tag ids:"]
        lines.append(", ".join(unresolved_tag_ids))

    assets = extract_assets(entry)
    if assets:
        lines += ["", "Assets:"]
        for asset in assets:
            asset_type = _canonical_asset_type(asset.get("type") or asset.get("assetType") or "file")
            icon = ASSET_ICON.get(asset_type, "📎")
            name = asset.get("name") or asset.get("filename") or asset.get("id") or "asset"
            path = asset.get("path") or asset.get("storagePath") or asset.get("url") or ""
            lines.append(f"{icon} {name}")
            if path:
                lines.append(f"  {path}")

    preview = entry_md_preview(entry_md_text)
    if preview:
        lines += ["", "Preview:", preview]

    lines += ["", "Entry path:", folder_path + "/"]
    lines += ["", "Entry folder:", drive_folder_url(folder_id)]

    return "\n".join(lines)


def extract_assets(entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract asset-like objects from ENTRY.json.

    MVP supports several likely field names to stay tolerant while the format is
    still evolving.
    """
    for key in ("assets", "assetRefs", "entryAssets"):
        value = entry.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _canonical_asset_type(value: Any) -> str:
    text = str(value or "file").lower()
    if text in {"image", "photo", "jpg", "jpeg", "png", "webp"}:
        return "image"
    if text in {"audio", "voice", "voice_note", "ogg", "mp3", "m4a", "wav"}:
        return "audio"
    if text in {"video", "mp4", "mov"}:
        return "video"
    if text in {"document", "pdf", "doc", "docx", "md", "txt"}:
        return "document"
    return "file"


def _hashtag(label: str) -> str:
    clean = str(label).strip().lstrip("#")
    clean = re.sub(r"\s+", "_", clean)
    return f"#{clean}" if clean else ""


def entry_md_preview(md_text: str, max_chars: int = 200) -> str:
    lines: list[str] = []
    for line in md_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
        if sum(len(item) for item in lines) >= max_chars:
            break

    preview = " ".join(lines).strip()
    if len(preview) > max_chars:
        preview = preview[:max_chars].rstrip() + "…"
    return preview


def status_color_id(status: str, config: dict[str, Any]) -> str:
    status_colors = config.get("statusColors") or {}
    color_name = str(status_colors.get(status, "grey"))
    return STATUS_COLOR_ID.get(color_name, "8")


def build_calendar_event_body(
    entry_data: EntryData,
    config: dict[str, Any],
) -> dict[str, Any]:
    entry = entry_data.entry_json
    title = render_event_title(entry, config, entry_data.resolved_tags)
    description = render_event_description(
        entry=entry,
        folder_path=entry_data.folder_path,
        folder_id=entry_data.folder_id,
        resolved_tags=entry_data.resolved_tags,
        unresolved_tag_ids=entry_data.unresolved_tag_ids,
        entry_md_text=entry_data.entry_md_text,
    )
    color_id = status_color_id(entry.get("status", "raw"), config)

    time_info = entry.get("time") or {}
    entry_date = time_info.get("entryDate", "")
    start_dt_str = time_info.get("startDateTime", "")
    end_dt_str = time_info.get("endDateTime", "")
    date_only = config.get("dateOnlyEntriesAsAllDay", True)
    default_duration = int(config.get("defaultDurationMinutes", 30) or 30)

    entry_id = entry.get("id", "")
    ext_props = {
        "extendedProperties": {
            "private": {
                "aiDiaryEntryId": entry_id,
                "aiDiaryEntryPath": entry_data.folder_path + "/ENTRY.json",
            }
        }
    }

    base = {
        "summary": title,
        "description": description,
        "colorId": color_id,
        **ext_props,
    }

    if start_dt_str:
        try:
            start_dt = parse_datetime(start_dt_str)
            end_dt = parse_datetime(end_dt_str) if end_dt_str else start_dt + timedelta(minutes=default_duration)
            if end_dt <= start_dt:
                end_dt = start_dt + timedelta(minutes=default_duration)

            return {
                **base,
                "start": {"dateTime": start_dt.isoformat()},
                "end": {"dateTime": end_dt.isoformat()},
            }
        except ValueError:
            # Fall through to date-only entryDate.
            pass

    if entry_date:
        if date_only:
            start_date = parse_ymd(entry_date)
            if not start_date:
                return {}
            end_date = start_date + timedelta(days=1)
            return {
                **base,
                "start": {"date": start_date.isoformat()},
                "end": {"date": end_date.isoformat()},
            }

        # If all-day mode is disabled, place date-only records at noon UTC.
        start_dt = datetime.fromisoformat(f"{entry_date}T12:00:00+00:00")
        end_dt = start_dt + timedelta(minutes=default_duration)
        return {
            **base,
            "start": {"dateTime": start_dt.isoformat()},
            "end": {"dateTime": end_dt.isoformat()},
        }

    return {}


def parse_datetime(value: str) -> datetime:
    if not value:
        raise ValueError("empty datetime")

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


# ------------------------------------------------------------------ #
# Calendar management                                                 #
# ------------------------------------------------------------------ #

def get_or_create_timeline_calendar(cal_service: Any, calendar_name: str) -> str:
    """Return calendar id for the timeline calendar, creating it if needed."""
    page_token: str | None = None

    while True:
        response = cal_service.calendarList().list(pageToken=page_token).execute()
        for item in response.get("items", []):
            if item.get("summary") == calendar_name:
                return item["id"]

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    created = cal_service.calendars().insert(body={"summary": calendar_name}).execute()
    return created["id"]


def create_calendar_event(cal_service: Any, calendar_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return cal_service.events().insert(calendarId=calendar_id, body=body).execute()


def update_calendar_event(cal_service: Any, calendar_id: str, event_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return cal_service.events().update(
        calendarId=calendar_id,
        eventId=event_id,
        body=body,
    ).execute()


def get_calendar_event(cal_service: Any, calendar_id: str, event_id: str) -> dict[str, Any] | None:
    try:
        return cal_service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    except Exception:
        return None


# ------------------------------------------------------------------ #
# Main workflow                                                       #
# ------------------------------------------------------------------ #

@dataclass
class SyncResult:
    entry_id: str
    title: str
    status: str
    action: str   # created | updated | skipped | failed | no_time
    google_event_id: str = ""
    error: str = ""


def run_projection(
    drive: DriveClient,
    cal_service: Any,
    root_folder_id: str,
    limit: int = 20,
    dry_run: bool = False,
    from_date: str = "",
    to_date: str = "",
    calendar_name_override: str = "",
) -> list[SyncResult]:
    results: list[SyncResult] = []
    parse_errors: list[dict[str, Any]] = []
    started_at = utc_now_iso()

    validate_date_args(from_date, to_date)

    print("\nLoading projection config ...")
    config = load_or_create_config(drive, root_folder_id, dry_run)

    if not config.get("enabled", True):
        print("  Projection is disabled in config (enabled=false). Exiting.")
        return []

    calendar_name = calendar_name_override or config.get("calendarName", "AI Diary Timeline")
    calendar_id = config.get("calendarId") or ""

    if calendar_id:
        print(f"Timeline calendar id: {calendar_id}")
    else:
        print(f"Looking up or creating calendar '{calendar_name}' ...")
        if dry_run:
            print("  [dry-run] Would look up or create calendar.")
            calendar_id = "dry-run-placeholder"
        else:
            calendar_id = get_or_create_timeline_calendar(cal_service, calendar_name)
            config["calendarId"] = calendar_id
            save_config(drive, root_folder_id, config)
            print(f"  Calendar id: {calendar_id}")

    print("\nLoading sync index ...")
    sync_index, duplicate_sync_records = load_sync_index(drive, root_folder_id)
    print(f"  {len(sync_index)} entries already indexed.")
    if duplicate_sync_records:
        print(f"  Warning: found {duplicate_sync_records} duplicate sync records; latest records will be used.")

    print("\nLoading tag catalog ...")
    tag_catalog = load_tag_catalog(drive, root_folder_id)
    print(f"  {len(tag_catalog)} tag ids/aliases loaded.")

    include_statuses = config.get("includeStatuses") or []
    print(f"\nCollecting entries (statuses: {include_statuses}, limit: {limit}) ...")
    if from_date or to_date:
        print(f"  Date filter: from={from_date or '-∞'} to={to_date or '+∞'}")

    entries = collect_entries(
        drive=drive,
        root_id=root_folder_id,
        include_statuses=include_statuses,
        limit=limit,
        tag_catalog=tag_catalog,
        from_date=from_date,
        to_date=to_date,
        parse_errors=parse_errors,
    )
    print(f"  Found {len(entries)} entries to process.")
    if parse_errors:
        print(f"  Warning: {len(parse_errors)} parse/list errors collected.")

    for index, entry_data in enumerate(entries, 1):
        entry = entry_data.entry_json
        entry_id = entry.get("id", "")
        title = entry.get("title") or "(без названия)"
        status = entry.get("status", "raw")

        print(f"\n[{index}/{len(entries)}] {title} (id={entry_id}, status={status})")

        if not entry_id:
            print("  ✗ Missing entry id — skipping.")
            results.append(SyncResult(
                entry_id="",
                title=title,
                status=status,
                action="failed",
                error="missing_entry_id",
            ))
            continue

        event_body = build_calendar_event_body(entry_data, config)
        if not event_body:
            print("  ⏭  No usable time info — skipping.")
            results.append(SyncResult(
                entry_id=entry_id,
                title=title,
                status=status,
                action="no_time",
                error="missing_or_invalid_time",
            ))
            continue

        current_hash = entry_hash(
            json.dumps(entry, ensure_ascii=False, sort_keys=True),
            entry_data.entry_md_text,
        )

        existing_record = sync_index.get(entry_id)
        existing_event_id = (existing_record or {}).get("googleEventId", "")
        existing_hash = (existing_record or {}).get("entryHash", "")

        if existing_event_id and existing_hash == current_hash:
            print("  ✓ Up to date (hash unchanged).")
            results.append(SyncResult(
                entry_id=entry_id,
                title=title,
                status=status,
                action="skipped",
                google_event_id=existing_event_id,
            ))
            continue

        if dry_run:
            action = "updated" if existing_event_id else "created"
            print(f"  [dry-run] Would {action} calendar event.")
            results.append(SyncResult(
                entry_id=entry_id,
                title=title,
                status=status,
                action=action,
                google_event_id=existing_event_id or "(new)",
            ))
            continue

        try:
            if existing_event_id:
                existing_event = get_calendar_event(cal_service, calendar_id, existing_event_id)
                if existing_event:
                    updated = update_calendar_event(cal_service, calendar_id, existing_event_id, event_body)
                    google_event_id = updated["id"]
                    action = "updated"
                    print(f"  ✏️  Event updated: {google_event_id}")
                else:
                    created = create_calendar_event(cal_service, calendar_id, event_body)
                    google_event_id = created["id"]
                    action = "created"
                    print(f"  ✅ Event recreated: {google_event_id}")
            else:
                created = create_calendar_event(cal_service, calendar_id, event_body)
                google_event_id = created["id"]
                action = "created"
                print(f"  ✅ Event created: {google_event_id}")

        except Exception as exc:
            print(f"  ✗ Failed: {exc}")
            results.append(SyncResult(
                entry_id=entry_id,
                title=title,
                status=status,
                action="failed",
                error=str(exc),
            ))
            continue

        sync_record = {
            "formatVersion": FORMAT_VERSION,
            "entryId": entry_id,
            "entryPath": entry_data.folder_path + "/ENTRY.json",
            "calendarId": calendar_id,
            "googleEventId": google_event_id,
            "lastSyncedAt": utc_now_iso(),
            "entryHash": current_hash,
            "syncStatus": "synced",
        }
        upsert_sync_record(drive, root_folder_id, sync_record)
        sync_index[entry_id] = sync_record

        results.append(SyncResult(
            entry_id=entry_id,
            title=title,
            status=status,
            action=action,
            google_event_id=google_event_id,
        ))

    if not dry_run:
        write_run_log(
            drive=drive,
            root_id=root_folder_id,
            started_at=started_at,
            results=results,
            calendar_name=calendar_name,
            calendar_id=calendar_id,
            parse_errors=parse_errors,
            duplicate_sync_records=duplicate_sync_records,
        )

    return results


def validate_date_args(from_date: str, to_date: str) -> None:
    if from_date and not parse_ymd(from_date):
        raise SystemExit(f"Invalid --from-date: {from_date}. Expected YYYY-MM-DD.")
    if to_date and not parse_ymd(to_date):
        raise SystemExit(f"Invalid --to-date: {to_date}. Expected YYYY-MM-DD.")
    if from_date and to_date and from_date > to_date:
        raise SystemExit("Invalid date range: --from-date is after --to-date.")


def write_run_log(
    drive: DriveClient,
    root_id: str,
    started_at: str,
    results: list[SyncResult],
    calendar_name: str,
    calendar_id: str,
    parse_errors: list[dict[str, Any]] | None = None,
    duplicate_sync_records: int = 0,
) -> None:
    runs_folder = drive.ensure_path(root_id, ["_runs"])
    existing_names = [file.name for file in drive.list_children(runs_folder.id)]
    log_name = run_log_name(existing_names)

    api_errors = [
        {"entryId": result.entry_id, "title": result.title, "error": result.error}
        for result in results
        if result.action == "failed"
    ]
    no_time_errors = [
        {"entryId": result.entry_id, "title": result.title, "error": result.error}
        for result in results
        if result.action == "no_time"
    ]
    all_errors = (parse_errors or []) + no_time_errors + api_errors

    log = {
        "formatVersion": FORMAT_VERSION,
        "workflow": "google_calendar_projection",
        "configPath": "_system/integrations/google_calendar_projection.json",
        "startedAt": started_at,
        "finishedAt": utc_now_iso(),
        "calendarName": calendar_name,
        "calendarId": calendar_id,
        "entriesScanned": len(results),
        "eventsCreated": sum(1 for result in results if result.action == "created"),
        "eventsUpdated": sum(1 for result in results if result.action == "updated"),
        "eventsSkipped": sum(1 for result in results if result.action == "skipped"),
        "noTimeSkipped": sum(1 for result in results if result.action == "no_time"),
        "eventsFailed": sum(1 for result in results if result.action == "failed"),
        "duplicateSyncRecords": duplicate_sync_records,
        "errors": all_errors,
    }
    write_json_file(drive, runs_folder.id, log_name, log)
    print(f"\n  Run log written: _runs/{log_name}")


# ------------------------------------------------------------------ #
# CLI                                                                 #
# ------------------------------------------------------------------ #

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Diary — Google Calendar Timeline Projection")
    parser.add_argument("--root-folder-id", required=True)
    parser.add_argument("--credentials", default="google_credentials.json")
    parser.add_argument("--token", default="google_token.json")
    parser.add_argument("--limit", type=int, default=20, help="Max entries to sync per run. Use 0 for no limit.")
    parser.add_argument("--calendar-name", default="", help="Override target calendar name (default: from config or 'AI Diary Timeline')")
    parser.add_argument("--from-date", default="", help="Only sync entries on/after this date (YYYY-MM-DD)")
    parser.add_argument("--to-date", default="", help="Only sync entries on/before this date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dry_run:
        print("=" * 60)
        print("DRY RUN MODE — no Drive or Calendar writes should be made")
        print("=" * 60)

    print("\nAuthorizing (Drive + Calendar scopes) ...")
    creds = get_credentials(args.credentials, args.token)

    drive = build_drive_client(args.credentials, args.token, creds)
    cal_service = gapi_build("calendar", "v3", credentials=creds)

    print(f"Root folder id: {args.root_folder_id}")

    results = run_projection(
        drive=drive,
        cal_service=cal_service,
        root_folder_id=args.root_folder_id,
        limit=args.limit,
        dry_run=args.dry_run,
        from_date=args.from_date,
        to_date=args.to_date,
        calendar_name_override=args.calendar_name,
    )

    print_summary(results, dry_run=args.dry_run)


def print_summary(results: list[SyncResult], dry_run: bool) -> None:
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    created = sum(1 for result in results if result.action == "created")
    updated = sum(1 for result in results if result.action == "updated")
    skipped = sum(1 for result in results if result.action == "skipped")
    no_time = sum(1 for result in results if result.action == "no_time")
    failed = sum(1 for result in results if result.action == "failed")

    print(f"  Total processed: {len(results)}")
    print(f"  Created:         {created}")
    print(f"  Updated:         {updated}")
    print(f"  Skipped (same):  {skipped}")
    print(f"  No time info:    {no_time}")
    print(f"  Failed:          {failed}")

    if failed:
        print("\nErrors:")
        for result in results:
            if result.action == "failed":
                print(f"  - {result.title}: {result.error}")

    if dry_run:
        print("\n[dry-run] No Drive or Calendar changes were made by the sync workflow.")
    print()


if __name__ == "__main__":
    main()
