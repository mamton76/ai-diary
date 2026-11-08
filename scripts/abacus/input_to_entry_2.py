#!/usr/bin/env python3
"""
AI Diary — Inbox to Entry workflow for Google Drive, v2.1

This workflow converts file-based inbox items into structured diary entries.

Supported inputs:

1. Flat files:
   inbox/drop/text/note.md
   inbox/drop/mixed/note.md

2. Legacy raw item folders:
   inbox/drop/mixed/some_item/
     raw.md
     source_entry.json
     import_metadata.json
     photos/

3. Structured inbox packages:
   inbox/new/2026-04-26__google_calendar__event_<hash>/
     MESSAGE.json
     raw_text.md
     source_event.json

Important:
- This script does NOT read Google Calendar directly.
- Calendar events are imported into inbox/new/ by gcal_to_inbox.py.
- This script only processes file-system inbox items.

After successful processing:
- flat files from inbox/drop/* are moved to inbox/_processed_raw/.../original_files/
- folder packages from inbox/new/ or inbox/drop/mixed/ are copied to _processed_raw
  and then moved out of the active inbox to inbox/archived/YYYY/MM/
- the original raw material is preserved
- a diary entry is created under entries/YYYY/MM/

Run dry-run first:

    python input_to_entry_2.py \
      --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
      --credentials ~/google_credentials.json \
      --token ~/.config/ai-diary/google_token.json \
      --dry-run

Then process one item:

    python input_to_entry_2.py \
      --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
      --credentials ~/google_credentials.json \
      --token ~/.config/ai-diary/google_token.json \
      --limit 1
"""

from __future__ import annotations

import argparse
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from drive_client import DriveClient, DriveFile


TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".json"}
MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".mp4", ".mov", ".ogg", ".mp3", ".wav"}

IGNORED_FILE_NAMES = {
    ".gitkeep",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
}
IGNORED_PREFIXES = {"~$"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_rfc3339(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def sanitize_title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}[T_\-\s]*\d{0,2}:?\d{0,2}:?\d{0,2}", "", stem)
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}", "", stem)
    stem = re.sub(r"^\d{8}", "", stem)
    stem = re.sub(r"^[A-Fa-f0-9]{8,}__", "", stem)
    stem = re.sub(r"[_\-]+", " ", stem).strip()
    stem = re.sub(r"\s+", " ", stem)
    if not stem:
        return "Untitled"
    return " ".join(word[:1].upper() + word[1:] for word in stem.split())


def extract_heading_or_first_line(text: str) -> str | None:
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("#"):
            clean = clean.lstrip("#").strip()
        if clean:
            return clean[:120]
    return None


@dataclass
class DateInfo:
    entry_date: str
    confidence: str
    start_datetime: str | None = None
    end_datetime: str | None = None


@dataclass
class RawInputItem:
    """
    A raw input item can be either:
    - a single file;
    - a folder with raw.md and optional metadata/photos;
    - a structured folder with MESSAGE.json and raw_text.md.
    """
    label: str
    kind: str  # "file" or "folder"
    item: DriveFile
    parent_folder: DriveFile
    raw_text_file: DriveFile | None = None
    source_entry_file: DriveFile | None = None
    import_metadata_file: DriveFile | None = None


@dataclass
class ProcessResult:
    status: str
    source: str
    reason: str | None = None
    entry_id: str | None = None
    entry_title: str | None = None
    entry_date: str | None = None
    entry_path: str | None = None
    raw_archive_path: str | None = None
    source_archive_path: str | None = None


class InboxToEntryDriveWorkflow:
    def __init__(
        self,
        drive: DriveClient,
        *,
        root_folder_id: str,
        local_timezone: str = "Europe/Belgrade",
        dry_run: bool = False,
        max_scan_depth: int = 6,
    ) -> None:
        self.drive = drive
        self.root_folder_id = root_folder_id
        self.local_tz = ZoneInfo(local_timezone)
        self.dry_run = dry_run
        self.max_scan_depth = max_scan_depth
        self.timestamp = utc_now_iso()

    # ------------------------------------------------------------------
    # Structure
    # ------------------------------------------------------------------

    def find_folder_path(self, path_parts: list[str]) -> DriveFile | None:
        """Return an existing folder path from root, or None. Does not create folders."""
        current_id = self.root_folder_id
        current_folder: DriveFile | None = None

        for part in path_parts:
            found = self.drive.find_child_folder(current_id, part)
            if not found:
                return None
            current_folder = found
            current_id = found.id

        return current_folder

    def get_folder_path(self, path_parts: list[str], *, create: bool) -> DriveFile | None:
        """Find or create a folder path depending on create flag."""
        if create:
            return self.drive.ensure_path(self.root_folder_id, path_parts)
        return self.find_folder_path(path_parts)

    def ensure_base_structure(self) -> None:
        if self.dry_run:
            print("DRY RUN: would ensure base folder structure")
            return

        required_paths = [
            ["inbox"],
            ["inbox", "drop"],
            ["inbox", "drop", "text"],
            ["inbox", "drop", "media"],
            ["inbox", "drop", "mixed"],
            ["inbox", "new"],
            ["inbox", "processing"],
            ["inbox", "needs_review"],
            ["inbox", "failed"],
            ["inbox", "archived"],
            ["inbox", "_processed_raw"],
            ["entries"],
            ["assets", "by_id"],
            ["catalogs", "tags"],
            ["indexes"],
        ]

        for parts in required_paths:
            self.drive.ensure_path(self.root_folder_id, parts)

    def get_drop_roots(self) -> list[tuple[str, DriveFile]]:
        roots: list[tuple[str, DriveFile]] = []

        for label, parts in [
            ("inbox/drop/text", ["inbox", "drop", "text"]),
            ("inbox/drop/mixed", ["inbox", "drop", "mixed"]),
        ]:
            folder = self.get_folder_path(parts, create=not self.dry_run)
            if folder:
                roots.append((label, folder))
            elif self.dry_run:
                print(f"DRY RUN: folder does not exist, skipping scan: {'/'.join(parts)}")

        return roots

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def should_ignore(self, file: DriveFile) -> bool:
        if file.name in IGNORED_FILE_NAMES:
            return True
        if any(file.name.startswith(prefix) for prefix in IGNORED_PREFIXES):
            return True
        return False

    def discover_raw_items(self) -> list[RawInputItem]:
        """
        Scan inbox/drop/text, inbox/drop/mixed, and inbox/new/.

        Rules:
        - regular supported text file = raw input item;
        - folder with raw.md = raw input item (legacy drop format);
        - folder with MESSAGE.json = raw input item (structured inbox format);
        - folder without raw.md or MESSAGE.json = batch/container; scan recursively;
        - helper files are ignored;
        - media-only files are skipped for now.
        """
        items: list[RawInputItem] = []

        for label, folder in self.get_drop_roots():
            items.extend(self._discover_inside_folder(label, folder, folder, depth=0))

        # Also scan inbox/new/ for structured packages (MESSAGE.json format).
        items.extend(self._discover_inbox_new())

        return items

    def _discover_inbox_new(self) -> list[RawInputItem]:
        """Scan inbox/new/ for structured packages with MESSAGE.json + raw_text.md."""
        inbox_new = self.get_folder_path(["inbox", "new"], create=not self.dry_run)
        if not inbox_new:
            if self.dry_run:
                print("DRY RUN: inbox/new does not exist, skipping structured inbox scan")
            return []

        items: list[RawInputItem] = []
        pkg_folders = self.drive.list_children(inbox_new.id)

        for pkg in sorted(pkg_folders, key=lambda f: f.name):
            if self.should_ignore(pkg) or not pkg.is_folder:
                continue

            children = self.drive.list_children(pkg.id)
            msg_file = next((c for c in children if not c.is_folder and c.name == "MESSAGE.json"), None)
            raw_text_file = next((c for c in children if not c.is_folder and c.name == "raw_text.md"), None)
            source_event_file = next((c for c in children if not c.is_folder and c.name == "source_event.json"), None)

            if not msg_file or not raw_text_file:
                continue  # not a valid structured package

            if not source_event_file:
                # Calendar packages are published only when the source snapshot is present.
                metadata = json.loads(self.drive.download_text(msg_file))
                if metadata.get("source", {}).get("type") == "google_calendar":
                    continue

            items.append(
                RawInputItem(
                    label=f"inbox/new/{pkg.name}",
                    kind="folder",
                    item=pkg,
                    parent_folder=inbox_new,
                    raw_text_file=raw_text_file,
                    source_entry_file=source_event_file,
                    import_metadata_file=msg_file,  # MESSAGE.json
                )
            )

        return items

    def _discover_inside_folder(
        self,
        label: str,
        folder: DriveFile,
        root_drop_folder: DriveFile,
        *,
        depth: int,
    ) -> list[RawInputItem]:
        if depth > self.max_scan_depth:
            return []

        children = sorted(self.drive.list_children(folder.id), key=lambda f: (not f.is_folder, f.name.lower()))
        items: list[RawInputItem] = []

        # If this folder contains raw.md, the whole folder is one raw item.
        raw_md = next((c for c in children if not c.is_folder and c.name == "raw.md"), None)
        if raw_md:
            source_entry = next((c for c in children if not c.is_folder and c.name == "source_entry.json"), None)
            import_metadata = next((c for c in children if not c.is_folder and c.name == "import_metadata.json"), None)
            items.append(
                RawInputItem(
                    label=label,
                    kind="folder",
                    item=folder,
                    parent_folder=root_drop_folder,
                    raw_text_file=raw_md,
                    source_entry_file=source_entry,
                    import_metadata_file=import_metadata,
                )
            )
            return items

        for child in children:
            if self.should_ignore(child):
                continue

            if child.is_folder:
                child_label = f"{label}/{child.name}"
                items.extend(self._discover_inside_folder(child_label, child, root_drop_folder, depth=depth + 1))
                continue

            suffix = Path(child.name).suffix.lower()
            if suffix in TEXT_EXTENSIONS:
                items.append(
                    RawInputItem(
                        label=label,
                        kind="file",
                        item=child,
                        parent_folder=folder,
                        raw_text_file=child,
                    )
                )

        return items

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------

    def read_import_metadata(self, item: RawInputItem) -> dict:
        if not item.import_metadata_file:
            return {}

        try:
            metadata_text = self.drive.download_text(item.import_metadata_file)
            data = json.loads(metadata_text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        return {}

    def infer_raw_input_id(self, item: RawInputItem, date_info: DateInfo, entry_id: str) -> str:
        """
        Preserve structured inbox raw id when available.

        For Google Calendar packages created by gcal_to_inbox.py this keeps:
            raw_gcal_event_<hash>

        This makes PROCESSING_RESULT.json and links/source_raw_inputs.json line up
        with the original MESSAGE.json and import log.
        """
        metadata = self.read_import_metadata(item)
        raw_id = metadata.get("id")
        if isinstance(raw_id, str) and raw_id.strip():
            return raw_id.strip()

        return f"raw_{date_info.entry_date}_{entry_id}"

    def infer_external_source(self, item: RawInputItem) -> dict | None:
        metadata = self.read_import_metadata(item)
        source = metadata.get("source")
        if isinstance(source, dict) and source.get("type"):
            return source
        return None

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def generate_entry_id(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        suffix = uuid.uuid4().hex[:10]
        return f"entry_{stamp}_{suffix}"

    def infer_date_from_text(self, text: str) -> DateInfo | None:
        match = re.search(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)", text)
        if match:
            return DateInfo(entry_date=match.group(0), confidence="text")

        match = re.search(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)", text)
        if match:
            return DateInfo(
                entry_date=f"{match.group(1)}-{match.group(2)}-{match.group(3)}",
                confidence="text",
            )

        return None

    def infer_date_from_name_or_metadata(self, item: RawInputItem, raw_text: str) -> DateInfo:
        # 1. Try import_metadata_file — supports both MESSAGE.json and legacy import_metadata.json.
        metadata = self.read_import_metadata(item)
        if metadata:
            # MESSAGE.json format (gcal/structured inbox).
            if metadata.get("schema") == "raw_input_message" or "time" in metadata:
                time_block = metadata.get("time") or {}
                entry_date = time_block.get("entryDate") or ""
                start_dt_str = time_block.get("startDateTime") or ""
                end_dt_str = time_block.get("endDateTime") or ""
                confidence = time_block.get("confidence") or "source_provided"
                if entry_date:
                    return DateInfo(
                        entry_date=entry_date,
                        start_datetime=start_dt_str or None,
                        end_datetime=end_dt_str or None,
                        confidence=confidence,
                    )

            # Legacy import_metadata.json format.
            creation_date = metadata.get("dates", {}).get("creationDate")
            time_zone = metadata.get("dates", {}).get("timeZone")
            dt = parse_rfc3339(creation_date)
            if dt:
                if time_zone:
                    try:
                        dt = dt.astimezone(ZoneInfo(time_zone))
                    except Exception:
                        dt = dt.astimezone(self.local_tz)
                else:
                    dt = dt.astimezone(self.local_tz)
                return DateInfo(
                    entry_date=dt.date().isoformat(),
                    start_datetime=dt.replace(microsecond=0).isoformat(),
                    confidence="source_metadata",
                )

        # 2. Try raw text.
        date_from_text = self.infer_date_from_text(raw_text)
        if date_from_text:
            return date_from_text

        # 3. Try folder/file name.
        candidates = [item.item.name]
        if item.raw_text_file:
            candidates.append(item.raw_text_file.name)

        for name in candidates:
            match = re.search(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)", name)
            if match:
                return DateInfo(entry_date=match.group(0), confidence="filename")

            match = re.search(r"(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)", name)
            if match:
                return DateInfo(
                    entry_date=f"{match.group(1)}-{match.group(2)}-{match.group(3)}",
                    confidence="filename",
                )

        # 4. Try Drive timestamps.
        created_dt = parse_rfc3339(item.item.created_time)
        if created_dt:
            local_dt = created_dt.astimezone(self.local_tz)
            return DateInfo(
                entry_date=local_dt.date().isoformat(),
                start_datetime=local_dt.replace(microsecond=0).isoformat(),
                confidence="file_createdTime",
            )

        modified_dt = parse_rfc3339(item.item.modified_time)
        if modified_dt:
            local_dt = modified_dt.astimezone(self.local_tz)
            return DateInfo(
                entry_date=local_dt.date().isoformat(),
                start_datetime=local_dt.replace(microsecond=0).isoformat(),
                confidence="file_modifiedTime",
            )

        local_now = datetime.now(self.local_tz)
        return DateInfo(entry_date=local_now.date().isoformat(), confidence="system_date")

    def infer_title(self, item: RawInputItem, raw_text: str) -> str:
        metadata = self.read_import_metadata(item)
        title = metadata.get("title")
        if isinstance(title, str) and title.strip() and title.strip() != "(no title)":
            return title.strip()[:120]

        heading = extract_heading_or_first_line(raw_text)
        if heading and len(heading.split()) <= 12:
            return heading

        return sanitize_title_from_filename(item.item.name)

    # ------------------------------------------------------------------
    # JSON builders
    # ------------------------------------------------------------------

    def build_entry_json(
        self,
        *,
        entry_id: str,
        title: str,
        date_info: DateInfo,
        raw_ref_path: str,
        needs_review: bool,
        review_reason: str | None,
        external_source: dict | None,
    ) -> dict:
        source_block: dict = {
            "rawInputRefs": [raw_ref_path],
        }
        if external_source:
            source_block["external"] = external_source

        return {
            "formatVersion": "v0.1.0",
            "schema": "entry",
            "id": entry_id,
            "title": title,
            "createdAt": self.timestamp,
            "updatedAt": self.timestamp,
            "time": {
                "entryDate": date_info.entry_date,
                "startDateTime": date_info.start_datetime,
                "endDateTime": date_info.end_datetime,
                "confidence": date_info.confidence,
            },
            "status": "needs_review" if needs_review else "processed",
            "currentRevisionId": "rev_000_raw",
            "rawRevisionId": "rev_000_raw",
            "tags": [],
            "source": source_block,
            "ai": {
                "createdByWorkflow": "inbox_to_entry",
                "needsReview": needs_review,
                "reviewReason": review_reason,
            },
        }

    def build_revision_json(self, *, entry_id: str) -> dict:
        return {
            "formatVersion": "v0.1.0",
            "id": "rev_000_raw",
            "entryId": entry_id,
            "revisionNumber": 0,
            "type": "raw",
            "createdAt": self.timestamp,
            "createdBy": {
                "type": "agent",
                "workflow": "inbox_to_entry",
            },
            "textPath": "text.md",
        }

    def build_source_links_json(self, *, raw_input_id: str, raw_ref_path: str) -> dict:
        return {
            "formatVersion": "v0.1.0",
            "rawSources": [
                {
                    "rawInputId": raw_input_id,
                    "path": raw_ref_path,
                }
            ],
        }

    def build_processing_result_json(
        self,
        *,
        raw_input_id: str,
        source_label: str,
        source_files: list[str],
        entry_id: str,
        entry_path: str,
        external_source: dict | None,
        source_archive_path: str | None,
    ) -> dict:
        result: dict = {
            "formatVersion": "v0.1.0",
            "rawInputId": raw_input_id,
            "processedAt": self.timestamp,
            "source": source_label,
            "sourceFiles": source_files,
            "createdEntities": [
                {
                    "type": "entry",
                    "id": entry_id,
                    "path": entry_path,
                }
            ],
            "status": "processed",
        }

        if external_source:
            result["externalSource"] = external_source
        if source_archive_path:
            result["sourceArchivePath"] = source_archive_path

        return result

    # ------------------------------------------------------------------
    # Archiving helpers
    # ------------------------------------------------------------------

    def copy_folder_children_to_original_files(
        self, raw_item: RawInputItem, original_files_folder: DriveFile, *, resume: bool = False,
    ) -> list[str]:
        """
        Copy contents of a folder raw item into original_files/.

        MVP behavior:
        - files are copied;
        - one level of nested folders is copied;
        - deeper nested folders are skipped.
        """
        source_files: list[str] = []
        children = self.drive.list_children(raw_item.item.id)

        for child in sorted(children, key=lambda f: f.name.lower()):
            if self.should_ignore(child):
                continue

            if resume and not child.is_folder and self.drive.list_children(original_files_folder.id, name=child.name):
                source_files.append(f"original_files/{child.name}")
                continue

            if child.is_folder:
                child_archive_folder = self.drive.ensure_folder(original_files_folder.id, child.name)
                grand_children = self.drive.list_children(child.id)

                for grand_child in sorted(grand_children, key=lambda f: f.name.lower()):
                    if grand_child.is_folder or self.should_ignore(grand_child):
                        continue
                    if not resume or not self.drive.list_children(child_archive_folder.id, name=grand_child.name):
                        self.drive.copy_file(grand_child.id, child_archive_folder.id)
                    source_files.append(f"original_files/{child.name}/{grand_child.name}")
            else:
                copied = self.drive.copy_file(child.id, original_files_folder.id)
                source_files.append(f"original_files/{copied.name}")

        return source_files

    def archive_processed_folder_item(self, raw_item: RawInputItem, year: str, month: str) -> str | None:
        """
        Move a processed folder item out of the active inbox.

        This prevents repeated runs from re-processing the same inbox/new package.

        Returns a logical path, or None when nothing was moved.
        """
        if raw_item.kind != "folder":
            return None

        archive_parts = ["inbox", "archived", year, month]
        archive_folder = self.drive.ensure_path(self.root_folder_id, archive_parts)

        moved = self.drive.move_file(
            raw_item.item.id,
            archive_folder.id,
            old_parent_ids=[raw_item.parent_folder.id],
        )

        return "/".join(archive_parts + [moved.name])

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def process_raw_item(self, raw_item: RawInputItem) -> ProcessResult:
        if not raw_item.raw_text_file:
            return ProcessResult(status="failed", source=raw_item.item.name, reason="Raw item has no raw text file")

        raw_text = self.drive.download_text(raw_item.raw_text_file).strip()
        if len(raw_text) < 3:
            return ProcessResult(status="failed", source=raw_item.item.name, reason="raw.md/text is empty or too short")

        date_info = self.infer_date_from_name_or_metadata(raw_item, raw_text)
        title = self.infer_title(raw_item, raw_text)
        external_source = self.infer_external_source(raw_item)
        calendar_package = (
            raw_item.kind == "folder" and external_source
            and external_source.get("type") == "google_calendar"
        )
        if calendar_package:
            calendar_id = external_source["calendarId"]
            event_id = external_source["eventId"]
            source_key = json.dumps([calendar_id, event_id], ensure_ascii=False, separators=(",", ":"))
            entry_id = f"entry_gcal_{uuid.uuid5(uuid.NAMESPACE_URL, source_key).hex}"
        else:
            entry_id = self.generate_entry_id()
        raw_input_id = self.infer_raw_input_id(raw_item, date_info, entry_id)

        needs_review = date_info.confidence in {"system_date", "file_modifiedTime"}
        review_reason = None
        if needs_review:
            review_reason = f"Entry date confidence is {date_info.confidence}; user review recommended."

        year, month, _ = date_info.entry_date.split("-")

        raw_batch_folder_name = f"raw_batch_{date_info.entry_date}_{entry_id}"

        raw_archive_parts = ["inbox", "_processed_raw", year, month, raw_batch_folder_name]
        raw_archive_path = "/".join(raw_archive_parts)
        raw_ref_path = f"{raw_archive_path}/PROCESSING_RESULT.json"

        entry_parts = ["entries", year, month, f"{date_info.entry_date}__{entry_id}"]
        entry_path = "/".join(entry_parts) + "/ENTRY.json"

        if self.dry_run:
            print(f"DRY RUN: would process raw item: {raw_item.label}/{raw_item.item.name}")
            print(f"  kind:        {raw_item.kind}")
            print(f"  raw file:    {raw_item.raw_text_file.name}")
            print(f"  raw id:      {raw_input_id}")
            print(f"  entry_id:    {entry_id}")
            print(f"  title:       {title}")
            print(f"  date:        {date_info.entry_date} ({date_info.confidence})")
            print(f"  entry_path:  {entry_path}")
            print(f"  raw_archive: {raw_archive_path}")
            if raw_item.kind == "folder":
                print(f"  source item: would move to inbox/archived/{year}/{month}/ after success")
            return ProcessResult(
                status="dry_run",
                source=f"{raw_item.label}/{raw_item.item.name}",
                entry_id=entry_id,
                entry_title=title,
                entry_date=date_info.entry_date,
                entry_path=entry_path,
                raw_archive_path=raw_archive_path,
            )

        if calendar_package:
            entry_folder = self.find_folder_path(entry_parts)
            if entry_folder and self.drive.list_children(entry_folder.id, name="ENTRY.json"):
                # The commit succeeded. A retry only needs to archive the original package.
                source_archive_path = self.archive_processed_folder_item(raw_item, year, month)
                return ProcessResult(
                    status="success",
                    source=f"{raw_item.label}/{raw_item.item.name}",
                    entry_id=entry_id,
                    entry_title=title,
                    entry_date=date_info.entry_date,
                    entry_path=entry_path,
                    raw_archive_path=raw_archive_path,
                    source_archive_path=source_archive_path,
                )

        # 1. Create raw archive.
        raw_archive_folder = self.drive.ensure_path(self.root_folder_id, raw_archive_parts)
        original_files_folder = self.drive.ensure_folder(raw_archive_folder.id, "original_files")

        source_files: list[str] = []

        if raw_item.kind == "folder":
            # Copy folder contents to raw archive. The original folder is moved to inbox/archived
            # only after all entry files and PROCESSING_RESULT.json are successfully written.
            source_files = self.copy_folder_children_to_original_files(
                raw_item, original_files_folder, resume=bool(calendar_package),
            )
        else:
            moved = self.drive.move_file(raw_item.item.id, original_files_folder.id, old_parent_ids=[raw_item.parent_folder.id])
            source_files.append(f"original_files/{moved.name}")

        # 2. Create entry folder.
        entry_folder = self.drive.ensure_path(self.root_folder_id, entry_parts)
        revisions_folder = self.drive.ensure_folder(entry_folder.id, "revisions")
        links_folder = self.drive.ensure_folder(entry_folder.id, "links")
        self.drive.ensure_folder(entry_folder.id, "ai")
        raw_revision_folder = self.drive.ensure_folder(revisions_folder.id, "000_raw")

        # 3. Build entry files.
        entry_markdown = f"# {title}\n\n{raw_text}\n"

        entry_json = self.build_entry_json(
            entry_id=entry_id,
            title=title,
            date_info=date_info,
            raw_ref_path=raw_ref_path,
            needs_review=needs_review,
            review_reason=review_reason,
            external_source=external_source,
        )
        revision_json = self.build_revision_json(entry_id=entry_id)
        source_links_json = self.build_source_links_json(raw_input_id=raw_input_id, raw_ref_path=raw_ref_path)

        write_json = self.drive.upsert_json if calendar_package else self.drive.upload_json
        write_text = self.drive.upsert_text if calendar_package else self.drive.upload_text
        if not calendar_package:
            write_json(entry_folder.id, "ENTRY.json", entry_json)
        write_text(entry_folder.id, "entry.md", entry_markdown, mime_type="text/markdown")
        write_json(raw_revision_folder.id, "revision.json", revision_json)
        write_text(raw_revision_folder.id, "text.md", raw_text + "\n", mime_type="text/markdown")
        write_json(links_folder.id, "source_raw_inputs.json", source_links_json)

        source_archive_path = None
        if calendar_package:
            # Publish ENTRY.json only after its revisions and provenance are durable.
            source_archive_path = f"inbox/archived/{year}/{month}/{raw_item.item.name}"
        elif raw_item.kind == "folder":
            source_archive_path = self.archive_processed_folder_item(raw_item, year, month)

        processing_result_json = self.build_processing_result_json(
            raw_input_id=raw_input_id,
            source_label=f"{raw_item.label}/{raw_item.item.name}",
            source_files=source_files,
            entry_id=entry_id,
            entry_path=entry_path,
            external_source=external_source,
            source_archive_path=source_archive_path,
        )
        write_json(raw_archive_folder.id, "PROCESSING_RESULT.json", processing_result_json)

        if calendar_package:
            write_json(entry_folder.id, "ENTRY.json", entry_json)
            self.archive_processed_folder_item(raw_item, year, month)

        return ProcessResult(
            status="success",
            source=f"{raw_item.label}/{raw_item.item.name}",
            entry_id=entry_id,
            entry_title=title,
            entry_date=date_info.entry_date,
            entry_path=entry_path,
            raw_archive_path=raw_archive_path,
            source_archive_path=source_archive_path,
        )

    def run(self, *, limit: int | None = None) -> list[ProcessResult]:
        print("=" * 72)
        print("AI Diary — Inbox to Entry workflow for Google Drive, v2.1")
        print("=" * 72)

        self.ensure_base_structure()

        raw_items = self.discover_raw_items()
        print(f"\nDiscovered raw input items: {len(raw_items)}")

        results: list[ProcessResult] = []
        processed_count = 0

        for raw_item in raw_items:
            if limit is not None and processed_count >= limit:
                break

            print(f"\nCandidate: {raw_item.label}/{raw_item.item.name}")

            try:
                result = self.process_raw_item(raw_item)
            except Exception as exc:
                result = ProcessResult(
                    status="failed",
                    source=f"{raw_item.label}/{raw_item.item.name}",
                    reason=f"{type(exc).__name__}: {exc}",
                )

            results.append(result)
            self.print_result(result)

            if result.status in {"success", "dry_run"}:
                processed_count += 1

        self.print_summary(results)
        return results

    @staticmethod
    def print_result(result: ProcessResult) -> None:
        icon = {
            "success": "✅",
            "dry_run": "🧪",
            "skipped": "⏭️",
            "failed": "❌",
        }.get(result.status, "•")

        print(f"{icon} {result.status}: {result.source}")

        if result.reason:
            print(f"   reason: {result.reason}")
        if result.entry_id:
            print(f"   entry:  {result.entry_id}")
        if result.entry_title:
            print(f"   title:  {result.entry_title}")
        if result.entry_date:
            print(f"   date:   {result.entry_date}")
        if result.source_archive_path:
            print(f"   archived source: {result.source_archive_path}")

    @staticmethod
    def print_summary(results: list[ProcessResult]) -> None:
        counts: dict[str, int] = {}
        for result in results:
            counts[result.status] = counts.get(result.status, 0) + 1

        print("\n" + "=" * 72)
        print("Summary")
        print("=" * 72)
        for status in sorted(counts):
            print(f"{status}: {counts[status]}")
        print(f"total: {len(results)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Diary Inbox to Entry workflow for Google Drive, v2.1")
    parser.add_argument("--root-folder-id", required=True, help="Google Drive folder id of the AI-Diary root folder.")
    parser.add_argument("--credentials", default=str(Path.home() / "google_credentials.json"))
    parser.add_argument("--token", default=str(Path.home() / ".config" / "ai-diary" / "google_token.json"))
    parser.add_argument("--timezone", default="Europe/Belgrade")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-scan-depth", type=int, default=6)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    drive = DriveClient(
        credentials_file=Path(args.credentials),
        token_file=Path(args.token),
    )

    workflow = InboxToEntryDriveWorkflow(
        drive,
        root_folder_id=args.root_folder_id,
        local_timezone=args.timezone,
        dry_run=args.dry_run,
        max_scan_depth=args.max_scan_depth,
    )

    workflow.run(limit=args.limit)


if __name__ == "__main__":
    main()
