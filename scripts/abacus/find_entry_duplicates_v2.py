#!/usr/bin/env python3
"""
AI Diary — Entry duplicate finder and exact-duplicate archiver

Report-first script for the file-based AI Diary storage.

It scans:

    entries/**/ENTRY.json
    entries/**/entry.md

and tries to find:

1. exact duplicates by normalized text hash;
2. entries linked to the same raw source;
3. near-duplicate candidates by text similarity;
4. suspicious same-date + same-title candidates.

By default, it does NOT modify entries.

If explicitly called with:

    --apply-exact-duplicates

it moves exact text duplicates out of active `entries/` into:

    trash/duplicates/<run_id>/

This is intentionally a soft-delete/archive action, not permanent deletion.

Recommended first run:

    python find_entry_duplicates_v2.py --root /path/to/AI-Diary --no-write

Recommended safe cleanup run:

    python find_entry_duplicates_v2.py --root /path/to/AI-Diary --apply-exact-duplicates
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any


IGNORED_DIR_NAMES = {
    ".git",
    "__pycache__",
    "node_modules",
    ".trash",
}

DEFAULT_SIMILARITY_THRESHOLD = 0.88
DEFAULT_POSSIBLE_THRESHOLD = 0.78

STATUS_PRIORITY = {
    "user_edited": 100,
    "processed": 80,
    "ai_proposed": 70,
    "needs_review": 50,
    "raw": 40,
    "failed": 0,
    "archived": -10,
    "deleted": -100,
}


def utc_now_for_filename() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


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
    if not text:
        return 0
    return len(text.split())


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


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
        return [str(ref) for ref in refs]
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
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def sequence_similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    longer = max(len(a), len(b))
    shorter = min(len(a), len(b))
    if longer > 0 and shorter / longer < 0.35:
        return 0.0

    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


@dataclass
class EntryRecord:
    id: str
    title: str
    normalized_title: str
    status: str | None
    created_at: str | None
    updated_at: str | None
    entry_date: str | None
    path: str
    folder: str
    abs_folder: str
    text_path: str | None
    text_len: int
    word_count: int
    normalized_hash: str
    raw_refs: list[str]
    tag_ids: list[str]
    keep_score: int


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
    sourceFolder: str
    destinationFolder: str
    normalizedHash: str


def discover_entry_json_files(entries_dir: Path) -> list[Path]:
    result = []
    for path in entries_dir.rglob("ENTRY.json"):
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        result.append(path)
    return sorted(result)


def compute_keep_score(entry: dict[str, Any], text_len: int, tag_ids: list[str], raw_refs: list[str]) -> int:
    status = str(entry.get("status") or "")
    score = STATUS_PRIORITY.get(status, 10)

    # Prefer entries with more metadata/links.
    score += min(len(tag_ids), 10) * 5
    score += min(len(raw_refs), 10) * 3

    if entry.get("currentRevisionId"):
        score += 3
    if entry.get("rawRevisionId"):
        score += 3

    # Slight preference for entries that actually have text.
    if text_len > 0:
        score += 2

    return score


def load_entry_record(root: Path, entry_json_path: Path) -> EntryRecord | None:
    try:
        entry = load_json(entry_json_path)
    except Exception as exc:
        print(f"WARNING: cannot parse {entry_json_path}: {exc}", file=sys.stderr)
        return None

    entry_folder = entry_json_path.parent
    entry_md = entry_folder / "entry.md"
    text = read_text_if_exists(entry_md)
    normalized = normalize_text(text)

    entry_id = str(entry.get("id") or entry_folder.name)
    title = str(entry.get("title") or "")
    parsed_date = parse_entry_date(entry)
    raw_refs = get_raw_refs(entry)
    tag_ids = get_tag_ids(entry)

    try:
        rel_entry_path = str(entry_json_path.relative_to(root))
    except ValueError:
        rel_entry_path = str(entry_json_path)

    try:
        rel_folder_path = str(entry_folder.relative_to(root))
    except ValueError:
        rel_folder_path = str(entry_folder)

    try:
        rel_text_path = str(entry_md.relative_to(root)) if entry_md.exists() else None
    except ValueError:
        rel_text_path = str(entry_md) if entry_md.exists() else None

    record = EntryRecord(
        id=entry_id,
        title=title,
        normalized_title=normalize_title(title),
        status=entry.get("status"),
        created_at=entry.get("createdAt"),
        updated_at=entry.get("updatedAt"),
        entry_date=parsed_date.isoformat() if parsed_date else None,
        path=rel_entry_path,
        folder=rel_folder_path,
        abs_folder=str(entry_folder),
        text_path=rel_text_path,
        text_len=len(text),
        word_count=word_count(normalized),
        normalized_hash=sha256_text(normalized),
        raw_refs=raw_refs,
        tag_ids=tag_ids,
        keep_score=compute_keep_score(entry, len(text), tag_ids, raw_refs),
    )

    setattr(record, "_normalized_text", normalized)
    return record


def candidate_from_pair(
    kind: str,
    severity: str,
    score: float,
    reasons: list[str],
    a: EntryRecord,
    b: EntryRecord,
) -> DuplicateCandidate:
    return DuplicateCandidate(
        kind=kind,
        severity=severity,
        score=round(float(score), 4),
        reasons=reasons,
        entry_a_id=a.id,
        entry_a_date=a.entry_date,
        entry_a_title=a.title,
        entry_a_path=a.path,
        entry_b_id=b.id,
        entry_b_date=b.entry_date,
        entry_b_title=b.title,
        entry_b_path=b.path,
    )


def canonical_sort_key(record: EntryRecord) -> tuple:
    # Higher keep_score wins; older createdAt wins as stable original; path as deterministic tie-breaker.
    created_dt = parse_dt(record.created_at)
    created_sort = created_dt.timestamp() if created_dt else float("inf")
    return (-record.keep_score, created_sort, record.folder)


def find_exact_text_groups(records: list[EntryRecord], min_words: int) -> list[list[EntryRecord]]:
    by_hash: dict[str, list[EntryRecord]] = {}
    for record in records:
        if record.word_count < min_words:
            continue
        by_hash.setdefault(record.normalized_hash, []).append(record)

    groups = []
    for group in by_hash.values():
        if len(group) >= 2:
            groups.append(sorted(group, key=canonical_sort_key))

    groups.sort(key=lambda g: (g[0].entry_date or "", g[0].title, g[0].normalized_hash))
    return groups


def find_duplicates(
    records: list[EntryRecord],
    *,
    similarity_threshold: float,
    possible_threshold: float,
    date_window_days: int | None,
    compare_all: bool,
    min_words: int,
) -> list[DuplicateCandidate]:
    candidates: list[DuplicateCandidate] = []
    seen_pairs: set[tuple[str, str, str]] = set()

    def add_candidate(candidate: DuplicateCandidate) -> None:
        key = tuple(sorted([candidate.entry_a_id, candidate.entry_b_id])) + (candidate.kind,)
        if key in seen_pairs:
            return
        seen_pairs.add(key)
        candidates.append(candidate)

    # 1. Exact normalized text duplicates.
    for group in find_exact_text_groups(records, min_words):
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                add_candidate(
                    candidate_from_pair(
                        "exact_text",
                        "exact",
                        1.0,
                        ["same normalized entry.md text hash"],
                        a,
                        b,
                    )
                )

    # 2. Same raw source references.
    by_raw_ref: dict[str, list[EntryRecord]] = {}
    for record in records:
        for ref in record.raw_refs:
            by_raw_ref.setdefault(ref, []).append(record)

    for raw_ref, group in by_raw_ref.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                add_candidate(
                    candidate_from_pair(
                        "same_raw_source",
                        "exact",
                        1.0,
                        [f"same rawInputRef: {raw_ref}"],
                        a,
                        b,
                    )
                )

    parsed_dates: dict[str, date | None] = {}
    for r in records:
        try:
            parsed_dates[r.id] = date.fromisoformat(r.entry_date) if r.entry_date else None
        except ValueError:
            parsed_dates[r.id] = None

    # 3. Near duplicates / suspicious pairs.
    for i in range(len(records)):
        a = records[i]
        a_text = getattr(a, "_normalized_text", "")
        if a.word_count < min_words:
            continue

        for j in range(i + 1, len(records)):
            b = records[j]
            b_text = getattr(b, "_normalized_text", "")
            if b.word_count < min_words:
                continue

            dist = date_distance_days(parsed_dates.get(a.id), parsed_dates.get(b.id))
            same_date = dist == 0
            close_date = dist is not None and date_window_days is not None and dist <= date_window_days
            same_title = bool(a.normalized_title and a.normalized_title == b.normalized_title)

            if not compare_all and not (same_date or close_date or same_title):
                continue

            reasons = []
            if same_date:
                reasons.append("same entryDate")
            elif close_date:
                reasons.append(f"entryDate within {dist} days")

            if same_title:
                reasons.append("same normalized title")

            shared_raw_refs = sorted(set(a.raw_refs) & set(b.raw_refs))
            if shared_raw_refs:
                reasons.append("shared rawInputRef")

            shared_tags = sorted(set(a.tag_ids) & set(b.tag_ids))
            if shared_tags:
                reasons.append(f"shared tags: {', '.join(shared_tags[:5])}")

            seq = sequence_similarity(a_text, b_text)
            jac = jaccard_tokens(a_text, b_text)
            score = max(seq, jac)

            if score >= similarity_threshold:
                add_candidate(
                    candidate_from_pair(
                        "similar_text",
                        "likely",
                        score,
                        reasons + [f"text similarity >= {similarity_threshold}"],
                        a,
                        b,
                    )
                )
            elif score >= possible_threshold and (same_date or same_title):
                add_candidate(
                    candidate_from_pair(
                        "possible_text",
                        "possible",
                        score,
                        reasons + [f"text similarity >= {possible_threshold}"],
                        a,
                        b,
                    )
                )
            elif same_title and same_date:
                add_candidate(
                    candidate_from_pair(
                        "same_date_title",
                        "possible",
                        score,
                        reasons,
                        a,
                        b,
                    )
                )

    severity_rank = {"exact": 0, "likely": 1, "possible": 2}
    candidates.sort(key=lambda c: (severity_rank.get(c.severity, 99), -c.score, c.entry_a_date or "", c.entry_a_title))
    return candidates


def build_records(root: Path, entries_dir: Path) -> tuple[list[EntryRecord], list[dict[str, Any]]]:
    records: list[EntryRecord] = []
    errors: list[dict[str, Any]] = []

    for entry_json_path in discover_entry_json_files(entries_dir):
        record = load_entry_record(root, entry_json_path)
        if not record:
            errors.append({"path": str(entry_json_path), "error": "cannot_load_entry"})
            continue
        records.append(record)

    return records, errors


def unique_destination(base_dir: Path, folder_name: str) -> Path:
    candidate = base_dir / folder_name
    if not candidate.exists():
        return candidate

    i = 2
    while True:
        candidate = base_dir / f"{folder_name}__duplicate_{i}"
        if not candidate.exists():
            return candidate
        i += 1


def archive_exact_duplicates(
    *,
    root: Path,
    exact_groups: list[list[EntryRecord]],
    run_id: str,
    trash_dir: Path | None = None,
    limit: int | None = None,
) -> list[ArchivedDuplicate]:
    """
    Move duplicate entry folders to trash/duplicates/<run_id>/.

    For each exact-text group:
    - keep the canonical first record;
    - archive all other records.

    This does not permanently delete anything.
    """
    archive_root = trash_dir or (root / "trash" / "duplicates" / run_id)
    archive_root.mkdir(parents=True, exist_ok=True)

    archived: list[ArchivedDuplicate] = []
    archived_count = 0

    for group in exact_groups:
        if not group:
            continue

        canonical = group[0]
        duplicates = group[1:]

        for duplicate in duplicates:
            if limit is not None and archived_count >= limit:
                return archived

            source_folder = Path(duplicate.abs_folder)

            if not source_folder.exists():
                archived.append(
                    ArchivedDuplicate(
                        action="missing_source",
                        duplicateEntryId=duplicate.id,
                        keptEntryId=canonical.id,
                        reason="Source folder no longer exists",
                        sourceFolder=str(source_folder),
                        destinationFolder="",
                        normalizedHash=duplicate.normalized_hash,
                    )
                )
                continue

            # Guardrail: only move folders inside root/entries.
            try:
                source_folder.relative_to(root / "entries")
            except ValueError:
                archived.append(
                    ArchivedDuplicate(
                        action="skipped",
                        duplicateEntryId=duplicate.id,
                        keptEntryId=canonical.id,
                        reason="Source folder is not inside root/entries",
                        sourceFolder=str(source_folder),
                        destinationFolder="",
                        normalizedHash=duplicate.normalized_hash,
                    )
                )
                continue

            dest = unique_destination(archive_root, source_folder.name)
            dest.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(source_folder), str(dest))
            archived_count += 1

            archived.append(
                ArchivedDuplicate(
                    action="moved_to_trash_duplicates",
                    duplicateEntryId=duplicate.id,
                    keptEntryId=canonical.id,
                    reason="exact normalized entry.md duplicate",
                    sourceFolder=str(source_folder),
                    destinationFolder=str(dest),
                    normalizedHash=duplicate.normalized_hash,
                )
            )

    return archived


def write_json_report(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv_report(path: Path, candidates: list[DuplicateCandidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "kind", "severity", "score", "reasons",
        "entry_a_id", "entry_a_date", "entry_a_title", "entry_a_path",
        "entry_b_id", "entry_b_date", "entry_b_title", "entry_b_path",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for candidate in candidates:
            row = asdict(candidate)
            row["reasons"] = "; ".join(candidate.reasons)
            writer.writerow(row)


def write_markdown_report(path: Path, payload: dict[str, Any], candidates: list[DuplicateCandidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    archived = payload.get("archivedExactDuplicates") or []

    lines: list[str] = []
    lines.append("# AI Diary duplicate candidates")
    lines.append("")
    lines.append(f"Generated at: `{payload['generatedAt']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Entries scanned: **{payload['entriesScanned']}**")
    lines.append(f"- Candidates found: **{len(candidates)}**")
    lines.append(f"- Exact candidates: **{sum(1 for c in candidates if c.severity == 'exact')}**")
    lines.append(f"- Likely candidates: **{sum(1 for c in candidates if c.severity == 'likely')}**")
    lines.append(f"- Possible candidates: **{sum(1 for c in candidates if c.severity == 'possible')}**")
    lines.append(f"- Archived exact duplicates: **{len([x for x in archived if x.get('action') == 'moved_to_trash_duplicates'])}**")
    lines.append("")

    if archived:
        lines.append("## Archived exact duplicates")
        lines.append("")
        for item in archived:
            lines.append(f"- `{item.get('duplicateEntryId')}` → kept `{item.get('keptEntryId')}`")
            lines.append(f"  - action: `{item.get('action')}`")
            lines.append(f"  - from: `{item.get('sourceFolder')}`")
            lines.append(f"  - to: `{item.get('destinationFolder')}`")
        lines.append("")

    lines.append("## Candidates")
    lines.append("")

    if not candidates:
        lines.append("No duplicate candidates found.")
    else:
        for idx, c in enumerate(candidates, 1):
            lines.append(f"### {idx}. {c.severity.upper()} · {c.kind} · score {c.score}")
            lines.append("")
            lines.append(f"Reasons: {', '.join(c.reasons) if c.reasons else 'n/a'}")
            lines.append("")
            lines.append("| Field | Entry A | Entry B |")
            lines.append("|---|---|---|")
            lines.append(f"| ID | `{c.entry_a_id}` | `{c.entry_b_id}` |")
            lines.append(f"| Date | `{c.entry_a_date}` | `{c.entry_b_date}` |")
            lines.append(f"| Title | {c.entry_a_title} | {c.entry_b_title} |")
            lines.append(f"| Path | `{c.entry_a_path}` | `{c.entry_b_path}` |")
            lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find and optionally archive exact duplicate AI Diary entries.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--root", type=Path, help="Path to AI-Diary root folder.")
    group.add_argument("--entries", type=Path, help="Path directly to entries/ folder.")

    parser.add_argument("--output-dir", type=Path, default=None, help="Where to write reports. Default: <root>/indexes/duplicates/")
    parser.add_argument("--similarity-threshold", type=float, default=DEFAULT_SIMILARITY_THRESHOLD)
    parser.add_argument("--possible-threshold", type=float, default=DEFAULT_POSSIBLE_THRESHOLD)
    parser.add_argument("--date-window-days", type=int, default=3)
    parser.add_argument("--compare-all", action="store_true")
    parser.add_argument("--min-words", type=int, default=5)
    parser.add_argument("--no-write", action="store_true", help="Only print summary, do not write report files.")
    parser.add_argument("--limit-candidates", type=int, default=None)

    parser.add_argument(
        "--apply-exact-duplicates",
        action="store_true",
        help="Move exact text duplicates to trash/duplicates/<run_id>/, keeping one canonical entry per group.",
    )
    parser.add_argument(
        "--trash-dir",
        type=Path,
        default=None,
        help="Override trash destination. Default: <root>/trash/duplicates/<run_id>/",
    )
    parser.add_argument(
        "--limit-archive",
        type=int,
        default=None,
        help="Maximum number of exact duplicate entry folders to archive.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.root:
        root = args.root.expanduser().resolve()
        entries_dir = root / "entries"
    else:
        entries_dir = args.entries.expanduser().resolve()
        root = entries_dir.parent

    if not entries_dir.exists():
        print(f"ERROR: entries directory not found: {entries_dir}", file=sys.stderr)
        return 2

    run_id = utc_now_for_filename()

    records, errors = build_records(root, entries_dir)

    print(f"Entries scanned: {len(records)}")
    if errors:
        print(f"Load errors: {len(errors)}")

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
        candidates = candidates[: args.limit_candidates]

    archived: list[ArchivedDuplicate] = []

    if args.apply_exact_duplicates:
        archived = archive_exact_duplicates(
            root=root,
            exact_groups=exact_groups,
            run_id=run_id,
            trash_dir=args.trash_dir.expanduser().resolve() if args.trash_dir else None,
            limit=args.limit_archive,
        )

    print(f"Duplicate candidates found: {len(candidates)}")
    print(f"  exact:    {sum(1 for c in candidates if c.severity == 'exact')}")
    print(f"  likely:   {sum(1 for c in candidates if c.severity == 'likely')}")
    print(f"  possible: {sum(1 for c in candidates if c.severity == 'possible')}")
    print(f"Exact text duplicate groups: {len(exact_groups)}")
    print(f"Archived exact duplicate folders: {sum(1 for x in archived if x.action == 'moved_to_trash_duplicates')}")

    generated_at = utc_now_iso()
    payload = {
        "formatVersion": "v0.1.0",
        "schema": "duplicate_candidates_report",
        "generatedAt": generated_at,
        "runId": run_id,
        "root": str(root),
        "entriesDir": str(entries_dir),
        "settings": {
            "similarityThreshold": args.similarity_threshold,
            "possibleThreshold": args.possible_threshold,
            "dateWindowDays": args.date_window_days,
            "compareAll": args.compare_all,
            "minWords": args.min_words,
            "applyExactDuplicates": args.apply_exact_duplicates,
            "trashDir": str(args.trash_dir) if args.trash_dir else None,
            "limitArchive": args.limit_archive,
        },
        "entriesScanned": len(records),
        "loadErrors": errors,
        "exactTextDuplicateGroups": [
            {
                "normalizedHash": group[0].normalized_hash,
                "keptEntryId": group[0].id,
                "keptEntryPath": group[0].path,
                "duplicateEntryIds": [r.id for r in group[1:]],
                "duplicateEntryPaths": [r.path for r in group[1:]],
            }
            for group in exact_groups
        ],
        "archivedExactDuplicates": [asdict(item) for item in archived],
        "candidates": [asdict(candidate) for candidate in candidates],
    }

    if not args.no_write:
        output_dir = args.output_dir or (root / "indexes" / "duplicates")

        json_path = output_dir / f"duplicate_candidates_{run_id}.json"
        md_path = output_dir / f"duplicate_candidates_{run_id}.md"
        csv_path = output_dir / f"duplicate_candidates_{run_id}.csv"

        write_json_report(json_path, payload)
        write_markdown_report(md_path, payload, candidates)
        write_csv_report(csv_path, candidates)

        latest_json = output_dir / "duplicate_candidates_latest.json"
        latest_md = output_dir / "duplicate_candidates_latest.md"
        latest_csv = output_dir / "duplicate_candidates_latest.csv"

        write_json_report(latest_json, payload)
        write_markdown_report(latest_md, payload, candidates)
        write_csv_report(latest_csv, candidates)

        print("")
        print("Reports written:")
        print(f"- {json_path}")
        print(f"- {md_path}")
        print(f"- {csv_path}")
        print(f"- {latest_json}")
        print(f"- {latest_md}")
        print(f"- {latest_csv}")

    if candidates:
        print("")
        print("Top candidates:")
        for c in candidates[:10]:
            print(f"- {c.severity} {c.score:.3f}: {c.entry_a_date} {c.entry_a_title!r} <-> {c.entry_b_title!r}")
            print(f"  {c.entry_a_path}")
            print(f"  {c.entry_b_path}")

    if args.apply_exact_duplicates:
        print("")
        print("Archived exact duplicates:")
        for item in archived[:20]:
            print(f"- {item.duplicateEntryId} -> kept {item.keptEntryId}: {item.action}")
            if item.destinationFolder:
                print(f"  {item.destinationFolder}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

