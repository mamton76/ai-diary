#!/usr/bin/env python3
"""Build an explicit-allowlist public gallery from portable task presentations.

Cloudflare Pages build command:
  python3 scripts/agent-team/build_preview_site.py
Cloudflare Pages output directory:
  dist/agent-team-previews

No cloud credentials, network requests or external build dependencies required.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TASKS = REPO / "docs" / "agent-team" / "tasks"
MANIFEST = REPO / "docs" / "agent-team" / "publishing" / "public-previews.json"
DEFAULT_OUTPUT = REPO / "dist" / "agent-team-previews"
TASK_ID = re.compile(r"^TASK-[0-9]{4}$")
FOLDER = re.compile(r"^(TASK-[0-9]{4})_[a-z0-9]+(?:-[a-z0-9]+)*$")
EXTENSIONS = {".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".json", ".txt"}
MAX_FILE_BYTES = 10 * 1024 * 1024


def find_task(tasks_root: Path, task_id: str) -> Path:
    matches = []
    for state in ("active", "completed"):
        parent = tasks_root / state
        if parent.exists():
            matches.extend(p for p in parent.iterdir()
                           if p.is_dir() and not p.is_symlink()
                           and (m := FOLDER.fullmatch(p.name)) and m.group(1) == task_id)
    if len(matches) != 1:
        raise ValueError(f"{task_id}: expected exactly one task directory, found {len(matches)}")
    return matches[0]


def build(tasks_root: Path, manifest: Path, output: Path) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("public_task_ids"), list):
        raise ValueError("Invalid publication manifest format")
    ids = data["public_task_ids"]
    if len(ids) != len(set(ids)) or any(not isinstance(x, str) or not TASK_ID.fullmatch(x) for x in ids):
        raise ValueError("Invalid or duplicate public task ID")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    items = []
    for task_id in sorted(ids):
        task = find_task(tasks_root, task_id)
        presentation = task / "presentation"
        if not presentation.is_dir() or presentation.is_symlink() or not (presentation / "index.html").is_file():
            raise ValueError(f"{task_id}: missing presentation/index.html")
        dest = output / task_id
        for source in presentation.rglob("*"):
            if source.is_symlink():
                raise ValueError(f"{task_id}: symbolic link is prohibited in public presentation")
            if not source.is_file():
                continue
            if source.suffix.lower() not in EXTENSIONS or source.stat().st_size > MAX_FILE_BYTES:
                raise ValueError(f"{task_id}: unsafe file in public presentation: {source.name}")
            relative = source.relative_to(presentation)
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        items.append((task_id, task.name))
    links = "\n".join(
        f'<li><a href="{html.escape(task_id)}/index.html">{html.escape(label)}</a></li>'
        for task_id, label in items
    )
    index = ('<!doctype html><html lang="ru"><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width, initial-scale=1">'
             '<title>AI Diary — опубликованные презентации</title>'
             '<h1>AI Diary — опубликованные презентации</h1>'
             '<p>Демонстрационные материалы. Содержимое не включает реальный дневник.</p>'
             f'<ul>{links}</ul></html>\n')
    (output / "index.html").write_text(index, encoding="utf-8")
    return [task_id for task_id, _ in items]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        ids = build(TASKS, MANIFEST, args.output.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Built public previews: {', '.join(ids) or '(none)'}")
    print(f"Output: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
