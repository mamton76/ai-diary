#!/usr/bin/env python3
"""
AI Diary — Entry duplicate finder for Google Drive

Drive-adapted version of find_entry_duplicates_v2.py.

All analysis logic is identical. Only data access is replaced:
- entries are read from Google Drive via API
- archive action moves folders via Drive API instead of shutil.move
- reports are written to Drive indexes/duplicates/ and optionally locally

Usage:

    # Report only (no changes)
    python find_entry_duplicates_drive.py \\
      --root-folder-id YOUR_ROOT_FOLDER_ID \\
      --credentials google_credentials.json \\
      --token google_token.json

    # Archive exact duplicates (soft-delete to trash/duplicates/)
    python find_entry_duplicates_drive.py \\
      --root-folder-id YOUR_ROOT_FOLDER_ID \\
      --credentials google_credentials.json \\
      --token google_token.json \\
      --apply-exact-duplicates
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from mamton_drive_client import DriveClient, DriveFile
from gcal_client import CALENDAR_SCOPES, get_credentials
from googleapiclient.discovery import build as gapi_build


# ------------------------------------------------------------------ #
# Analysis constants (same as original)                               #
# ------------------------------------------------------------------ #

IGNORED_DIR_NAMES = {".git", "__pycache__", "node_modules", ".trash"}

DEFAULT_SIMILARITY_THRESHOLD = 0.88
DEFAULT_POSSIBLE_THRESHOLD   = 0.78

STATUS_PRIORITY = {
    "user_edited":  100,
    "processed":     80,
    "ai_proposed":   70,
    "needs_review":  50,
    "raw":           40,
    "failed":         0,
    "archived":      -10,
    "deleted":      -100,
}


# ------------------------------------------------------------------ #
# Pure analysis helpers (unchanged from original)                     #
# ------------------------------------------------------------------ #

def utc_now_for_filename() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def normalize_title(value: str | None) -> str:
    value = value or ""
    value = value.lower().replace("ё", "е")
    value = re.sub(r"[^\wа-яa-z0-9]+", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value).strip()
    return value

def strip_markdown_noise(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    return text

def normalize_text(text: str) -> str:
    text = text or ""
    text = text.replace("\ufeff", "")
    text = text.lower().replace("ё", "е")
    text = strip_markdown_noise(text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^\wа-яa-z0-9]+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

def word_count(text: str) -> int:
    return len(text.split()) if text else 0

def parse_entry_date(entry: dict[str, Any]) -> date | None:
    raw = (entry.get("time") or {}).get("entryDate")
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None

def date_distance_days(a: date | None, b: date | None) -> int | None:
    if not a or not b:
        return None
    return abs((a - b).days)

def get_raw_refs(entry: dict[str, Any]) -> list[str]:
    source = entry.get("source") or {}
    refs = source.get("rawInputRefs") or []
    if isinstance(refs, list):
        return [str(r) for r in refs]
    return []

def get_tag_ids(entry: dict[str, Any]) -> list[str]:
    tags = entry.get("tags") or []
    tag_ids = []
    for tag in tags:
        if isinstance(tag, dict) and tag.get("tagId"):
            tag_ids.append(str(tag["tagId"]))
        elif isinstance(tag, str):
            tag_ids.append(tag)
    return tag_ids

def jaccard_tokens(a: str, b: str) -> float:
    set_a, set_b = set(a.split()), set(b.split())
    if not set_a and not set_b: return 1.0
    if not set_a or not set_b:  return 0.0
    return len(set_a & set_b) / len(set_a | set_b)

def sequence_similarity(a: str, b: str) -> float:
    if not a and not b: return 1.0
    if not a or not b:  return 0.0
    longer, shorter = max(len(a), len(b)), min(len(a), len(b))
    if longer > 0 and shorter / longer < 0.35: return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()

def compute_keep_score(entry: dict, text_len: int, tag_ids: list, raw_refs: list) -> int:
    score = STATUS_PRIORITY.get(str(entry.get("status") or ""), 10)
    score += min(len(tag_ids), 10) * 5
    score += min(len(raw_refs), 10) * 3
    if entry.get("currentRevisionId"): score += 3
    if entry.get("rawRevisionId"):     score += 3
    if text_len > 0:                   score += 2
    return score


# ------------------------------------------------------------------ #
# Data classes                                                        #
# ------------------------------------------------------------------ #

@dataclass
class EntryRecord:
    id: str
    title: str
    normalized_title: str
    status: str | None
    created_at: str | None
    updated_at: str | None
    entry_date: str | None
    path: str          # relative Drive path hint
    folder: str        # folder name
    drive_folder_id: str   # Drive folder id (used for archiving)
    text_len: int
    word_count: int
    normalized_hash: str
    raw_refs: list[str]
    tag_ids: list[str]
    keep_score: int

    # Compat alias for report functions
    @property
    def abs_folder(self) -> str:
        return self.drive_folder_id


@dataclass
class DuplicateCandidate:
    kind: str
    severity: str
    score: float
    reasons: list[str]
    entry_a_id: str
    entry_a_date: str | None
    entry_a_title: str
    entry_a_path: str
    entry_b_id: str
    entry_b_date: str | None
    entry_b_title: str
    entry_b_path: str


@dataclass
class ArchivedDuplicate:
    action: str
    duplicateEntryId: str
    keptEntryId: str
    reason: str
    sourceFolder: str      # Drive folder id
    destinationFolder: str # Drive folder id of destination
    normalizedHash: str


# ------------------------------------------------------------------ #
# Drive: load entries                                                 #
# ------------------------------------------------------------------ #

def walk_entries_drive(
    drive: DriveClient,
    folder_id: str,
    path_hint: str,
    records: list[EntryRecord],
    errors: list[dict],
    min_words: int,
) -> None:
    children = drive.list_children(folder_id)
    entry_json_file = next((c for c in children if not c.is_folder and c.name == "ENTRY.json"), None)

    if entry_json_file:
        # This is an entry folder
        try:
            entry_text = drive.download_text(entry_json_file)
            entry = json.loads(entry_text)
        except Exception as exc:
            errors.append({"path": path_hint + "/ENTRY.json", "error": str(exc)})
            return

        entry_md_file = next((c for c in children if not c.is_folder and c.name == "entry.md"), None)
        md_text = ""
        if entry_md_file:
            try:
                md_text = drive.download_text(entry_md_file)
            except Exception:
                pass

        normalized = normalize_text(md_text)
        raw_refs = get_raw_refs(entry)
        tag_ids = get_tag_ids(entry)
        parsed_date = parse_entry_date(entry)
        entry_id = str(entry.get("id") or path_hint.split("/")[-1])
        title = str(entry.get("title") or "")

        records.append(EntryRecord(
            id=entry_id,
            title=title,
            normalized_title=normalize_title(title),
            status=entry.get("status"),
            created_at=entry.get("createdAt"),
            updated_at=entry.get("updatedAt"),
            entry_date=parsed_date.isoformat() if parsed_date else None,
            path=path_hint + "/ENTRY.json",
            folder=path_hint.split("/")[-1],
            drive_folder_id=folder_id,
            text_len=len(md_text),
            word_count=word_count(normalized),
            normalized_hash=sha256_text(normalized),
            raw_refs=raw_refs,
            tag_ids=tag_ids,
            keep_score=compute_keep_score(entry, len(md_text), tag_ids, raw_refs),
        ))
        return

    # Container folder — recurse
    for child in children:
        if child.is_folder:
            walk_entries_drive(drive, child.id, path_hint + "/" + child.name, records, errors, min_words)


def build_records_drive(
    drive: DriveClient,
    root_folder_id: str,
    min_words: int,
) -> tuple[list[EntryRecord], list[dict]]:
    records: list[EntryRecord] = []
    errors: list[dict] = []

    entries_folder = drive.find_child_folder(root_folder_id, "entries")
    if not entries_folder:
        print("WARNING: no entries/ folder found in Drive root.", file=sys.stderr)
        return records, errors

    print(f"  Scanning entries/ in Drive ...")
    walk_entries_drive(drive, entries_folder.id, "entries", records, errors, min_words)
    return records, errors


# ------------------------------------------------------------------ #
# Analysis (same logic as original)                                   #
# ------------------------------------------------------------------ #

def find_exact_text_groups(records: list[EntryRecord], min_words: int) -> list[list[EntryRecord]]:
    by_hash: dict[str, list[EntryRecord]] = {}
    for r in records:
        if r.word_count < min_words:
            continue
        by_hash.setdefault(r.normalized_hash, []).append(r)

    groups = [recs for recs in by_hash.values() if len(recs) > 1]

    for group in groups:
        group.sort(key=lambda r: r.keep_score, reverse=True)

    return groups


def find_duplicates(
    records: list[EntryRecord],
    *,
    similarity_threshold: float,
    possible_threshold: float,
    date_window_days: int,
    compare_all: bool,
    min_words: int,
) -> list[DuplicateCandidate]:
    candidates: list[DuplicateCandidate] = []
    n = len(records)

    for i in range(n):
        a = records[i]
        for j in range(i + 1, n):
            b = records[j]

            reasons: list[str] = []
            score = 0.0

            # Exact hash
            if a.normalized_hash == b.normalized_hash and a.word_count >= min_words:
                reasons.append("exact_text_hash")
                score = max(score, 1.0)

            # Shared raw refs
            shared_refs = set(a.raw_refs) & set(b.raw_refs)
            if shared_refs:
                reasons.append(f"shared_raw_refs:{','.join(sorted(shared_refs))}")
                score = max(score, 0.95)

            # Same date + similar title
            date_dist = date_distance_days(
                date.fromisoformat(a.entry_date) if a.entry_date else None,
                date.fromisoformat(b.entry_date) if b.entry_date else None,
            )
            title_sim = sequence_similarity(a.normalized_title, b.normalized_title)

            if date_dist is not None and date_dist <= date_window_days and title_sim >= 0.85:
                reasons.append(f"same_date_similar_title:{title_sim:.2f}")
                score = max(score, 0.90)

            # Text similarity
            if compare_all or (date_dist is not None and date_dist <= date_window_days * 2):
                if a.word_count >= min_words and b.word_count >= min_words:
                    text_sim = max(
                        jaccard_tokens(a.normalized_hash, b.normalized_hash),
                        sequence_similarity(a.normalized_hash[:2000], b.normalized_hash[:2000]),
                    )
                    if text_sim >= similarity_threshold:
                        reasons.append(f"similar_text:{text_sim:.2f}")
                        score = max(score, text_sim)
                    elif text_sim >= possible_threshold:
                        reasons.append(f"possibly_similar_text:{text_sim:.2f}")
                        score = max(score, text_sim)

            if not reasons:
                continue

            if score >= 1.0 or "exact_text_hash" in reasons:
                severity = "exact"
            elif score >= similarity_threshold:
                severity = "likely"
            else:
                severity = "possible"

            candidates.append(DuplicateCandidate(
                kind="text_duplicate" if "exact_text_hash" in reasons else
                     "shared_source"  if any("raw_refs" in r for r in reasons) else
                     "similar_text",
                severity=severity,
                score=round(score, 4),
                reasons=reasons,
                entry_a_id=a.id,
                entry_a_date=a.entry_date,
                entry_a_title=a.title,
                entry_a_path=a.path,
                entry_b_id=b.id,
                entry_b_date=b.entry_date,
                entry_b_title=b.title,
                entry_b_path=b.path,
            ))

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates


# ------------------------------------------------------------------ #
# Drive: archive duplicates                                           #
# ------------------------------------------------------------------ #

def archive_exact_duplicates_drive(
    drive: DriveClient,
    root_folder_id: str,
    exact_groups: list[list[EntryRecord]],
    run_id: str,
    limit: int | None = None,
) -> list[ArchivedDuplicate]:
    """Move duplicate entry folders to trash/duplicates/<run_id>/ in Drive."""
    trash_folder = drive.ensure_path(root_folder_id, ["trash", "duplicates", run_id])
    archived: list[ArchivedDuplicate] = []
    count = 0

    for group in exact_groups:
        if not group:
            continue
        canonical = group[0]
        for duplicate in group[1:]:
            if limit is not None and count >= limit:
                return archived
            try:
                drive.move_file(duplicate.drive_folder_id, trash_folder.id)
                archived.append(ArchivedDuplicate(
                    action="moved_to_trash_duplicates",
                    duplicateEntryId=duplicate.id,
                    keptEntryId=canonical.id,
                    reason="exact normalized entry.md duplicate",
                    sourceFolder=duplicate.drive_folder_id,
                    destinationFolder=trash_folder.id,
                    normalizedHash=duplicate.normalized_hash,
                ))
                count += 1
                print(f"  Archived: {duplicate.id} (kept: {canonical.id})")
            except Exception as exc:
                print(f"  ERROR archiving {duplicate.id}: {exc}", file=sys.stderr)
                archived.append(ArchivedDuplicate(
                    action="error",
                    duplicateEntryId=duplicate.id,
                    keptEntryId=canonical.id,
                    reason=str(exc),
                    sourceFolder=duplicate.drive_folder_id,
                    destinationFolder="",
                    normalizedHash=duplicate.normalized_hash,
                ))

    return archived


# ------------------------------------------------------------------ #
# Reports                                                             #
# ------------------------------------------------------------------ #

def write_markdown_report(candidates: list[DuplicateCandidate], payload: dict) -> str:
    archived = payload.get("archivedExactDuplicates") or []
    lines = [
        "# AI Diary — Duplicate Candidates Report",
        "",
        f"Generated: `{payload['generatedAt']}`",
        "",
        "## Summary",
        "",
        f"- Entries scanned: **{payload['entriesScanned']}**",
        f"- Candidates found: **{len(candidates)}**",
        f"- Exact: **{sum(1 for c in candidates if c.severity == 'exact')}**",
        f"- Likely: **{sum(1 for c in candidates if c.severity == 'likely')}**",
        f"- Possible: **{sum(1 for c in candidates if c.severity == 'possible')}**",
        f"- Archived: **{sum(1 for x in archived if x.get('action') == 'moved_to_trash_duplicates')}**",
        "",
    ]

    if archived:
        lines += ["## Archived Exact Duplicates", ""]
        for item in archived:
            lines.append(f"- `{item.get('duplicateEntryId')}` → kept `{item.get('keptEntryId')}` ({item.get('action')})")
        lines.append("")

    lines += ["## Candidates", ""]
    if not candidates:
        lines.append("No duplicate candidates found.")
    else:
        for idx, c in enumerate(candidates, 1):
            lines += [
                f"### {idx}. {c.severity.upper()} · {c.kind} · score {c.score}",
                "",
                f"Reasons: {', '.join(c.reasons)}",
                "",
                "| Field | Entry A | Entry B |",
                "|---|---|---|",
                f"| ID | `{c.entry_a_id}` | `{c.entry_b_id}` |",
                f"| Date | `{c.entry_a_date}` | `{c.entry_b_date}` |",
                f"| Title | {c.entry_a_title} | {c.entry_b_title} |",
                f"| Path | `{c.entry_a_path}` | `{c.entry_b_path}` |",
                "",
            ]

    return "\n".join(lines) + "\n"


def write_csv_report(candidates: list[DuplicateCandidate]) -> str:
    import io as _io
    buf = _io.StringIO()
    fields = ["kind","severity","score","reasons",
              "entry_a_id","entry_a_date","entry_a_title","entry_a_path",
              "entry_b_id","entry_b_date","entry_b_title","entry_b_path"]
    import csv as _csv
    writer = _csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader()
    for c in candidates:
        row = asdict(c)
        row["reasons"] = "; ".join(c.reasons)
        writer.writerow(row)
    return buf.getvalue()


def save_report_to_drive(drive: DriveClient, root_folder_id: str, run_id: str,
                          json_text: str, md_text: str, csv_text: str) -> None:
    out_folder = drive.ensure_path(root_folder_id, ["indexes", "duplicates"])
    for name, text, mime in [
        (f"duplicate_candidates_{run_id}.json", json_text, "application/json"),
        (f"duplicate_candidates_{run_id}.md",   md_text,   "text/markdown"),
        (f"duplicate_candidates_{run_id}.csv",  csv_text,  "text/csv"),
        ("duplicate_candidates_latest.json",    json_text, "application/json"),
        ("duplicate_candidates_latest.md",      md_text,   "text/markdown"),
        ("duplicate_candidates_latest.csv",     csv_text,  "text/csv"),
    ]:
        drive.upsert_text(out_folder.id, name, text, mime_type=mime)
        print(f"  Saved to Drive: indexes/duplicates/{name}")


def save_report_locally(output_dir: Path, run_id: str,
                         json_text: str, md_text: str, csv_text: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, text in [
        (f"duplicate_candidates_{run_id}.json", json_text),
        (f"duplicate_candidates_{run_id}.md",   md_text),
        (f"duplicate_candidates_{run_id}.csv",  csv_text),
    ]:
        (output_dir / name).write_text(text, encoding="utf-8")
        print(f"  Saved locally: {output_dir / name}")


# ------------------------------------------------------------------ #
# CLI                                                                 #
# ------------------------------------------------------------------ #

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI Diary — Entry duplicate finder for Google Drive")
    p.add_argument("--root-folder-id", required=True)
    p.add_argument("--credentials", default="google_credentials.json")
    p.add_argument("--token", default="google_token.json")
    p.add_argument("--similarity-threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD)
    p.add_argument("--possible-threshold",   type=float, default=DEFAULT_POSSIBLE_THRESHOLD)
    p.add_argument("--date-window-days", type=int, default=3)
    p.add_argument("--min-words", type=int, default=5)
    p.add_argument("--compare-all", action="store_true")
    p.add_argument("--limit-candidates", type=int, default=None)
    p.add_argument("--apply-exact-duplicates", action="store_true",
                   help="Move exact text duplicates to trash/duplicates/<run_id>/ in Drive")
    p.add_argument("--limit-archive", type=int, default=None)
    p.add_argument("--no-drive-write", action="store_true",
                   help="Do not write reports to Drive (print summary only)")
    p.add_argument("--local-output", type=Path, default=None,
                   help="Also save reports locally to this directory")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    print("Authorizing ...")
    creds = get_credentials(args.credentials, args.token)
    drive_service = gapi_build("drive", "v3", credentials=creds)
    drive = DriveClient.__new__(DriveClient)
    drive.credentials_file = Path(args.credentials)
    drive.token_file = Path(args.token)
    drive.scopes = CALENDAR_SCOPES
    drive.service = drive_service

    run_id = utc_now_for_filename()
    print(f"Run id: {run_id}")

    # Load entries
    records, errors = build_records_drive(drive, args.root_folder_id, args.min_words)
    print(f"Entries scanned: {len(records)}")
    if errors:
        print(f"Load errors: {len(errors)}")

    # Analysis
    exact_groups = find_exact_text_groups(records, args.min_words)
    candidates = find_duplicates(
        records,
        similarity_threshold=args.similarity_threshold,
        possible_threshold=args.possible_threshold,
        date_window_days=args.date_window_days,
        compare_all=args.compare_all,
        min_words=args.min_words,
    )

    if args.limit_candidates is not None:
        candidates = candidates[:args.limit_candidates]

    # Archive if requested
    archived: list[ArchivedDuplicate] = []
    if args.apply_exact_duplicates:
        print(f"\nArchiving exact duplicates ...")
        archived = archive_exact_duplicates_drive(
            drive, args.root_folder_id, exact_groups, run_id, args.limit_archive
        )

    # Print summary
    print(f"\nDuplicate candidates: {len(candidates)}")
    print(f"  exact:    {sum(1 for c in candidates if c.severity == 'exact')}")
    print(f"  likely:   {sum(1 for c in candidates if c.severity == 'likely')}")
    print(f"  possible: {sum(1 for c in candidates if c.severity == 'possible')}")
    print(f"Exact text duplicate groups: {len(exact_groups)}")
    print(f"Archived: {sum(1 for x in archived if x.action == 'moved_to_trash_duplicates')}")

    if candidates:
        print("\nTop candidates:")
        for c in candidates[:10]:
            print(f"  {c.severity} {c.score:.3f}: {c.entry_a_date} {c.entry_a_title!r} <-> {c.entry_b_title!r}")
            print(f"    {c.entry_a_path}")
            print(f"    {c.entry_b_path}")

    # Build report payload
    payload = {
        "formatVersion": "v0.1.0",
        "schema": "duplicate_candidates_report",
        "generatedAt": utc_now_iso(),
        "runId": run_id,
        "rootFolderId": args.root_folder_id,
        "settings": {
            "similarityThreshold": args.similarity_threshold,
            "possibleThreshold": args.possible_threshold,
            "dateWindowDays": args.date_window_days,
            "compareAll": args.compare_all,
            "minWords": args.min_words,
            "applyExactDuplicates": args.apply_exact_duplicates,
            "limitArchive": args.limit_archive,
        },
        "entriesScanned": len(records),
        "loadErrors": errors,
        "exactTextDuplicateGroups": [
            {
                "normalizedHash": g[0].normalized_hash,
                "keptEntryId": g[0].id,
                "keptEntryPath": g[0].path,
                "duplicateEntryIds": [r.id for r in g[1:]],
                "duplicateEntryPaths": [r.path for r in g[1:]],
            }
            for g in exact_groups
        ],
        "archivedExactDuplicates": [asdict(x) for x in archived],
        "candidates": [asdict(c) for c in candidates],
    }

    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    md_text   = write_markdown_report(candidates, payload)
    csv_text  = write_csv_report(candidates)

    if not args.no_drive_write:
        print("\nSaving reports to Drive ...")
        save_report_to_drive(drive, args.root_folder_id, run_id, json_text, md_text, csv_text)

    if args.local_output:
        print(f"\nSaving reports locally to {args.local_output} ...")
        save_report_locally(args.local_output, run_id, json_text, md_text, csv_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
