#!/usr/bin/env python3
"""Build or verify deterministic concatenations of agent-team task discussions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = ROOT / "docs" / "agent-team" / "tasks"


def render(thread_files: list[Path]) -> str:
    sections = [
        f"<!-- Source: threads/{path.name} -->\n\n{path.read_text(encoding='utf-8').rstrip()}"
        for path in sorted(thread_files)
    ]
    return "\n\n---\n\n".join(sections) + "\n"


def process(tasks_root: Path, write: bool) -> int:
    problems = 0
    count = 0
    for state in ("active", "completed"):
        parent = tasks_root / state
        if not parent.exists():
            continue
        for task in sorted(parent.iterdir()):
            if not task.is_dir() or not task.name.startswith("TASK-"):
                continue
            threads = task / "discussion" / "threads"
            if not threads.exists():
                continue
            sources = sorted(threads.glob("*.md"))
            if not sources:
                print(f"ERROR {task}: threads/ exists but has no *.md files")
                problems += 1
                continue
            output = task / "discussion" / "00_all.md"
            expected = render(sources)
            actual = output.read_text(encoding="utf-8") if output.exists() else None
            count += 1
            if actual == expected:
                print(f"OK {output.relative_to(tasks_root)}")
            elif write:
                output.write_text(expected, encoding="utf-8")
                print(f"UPDATED {output.relative_to(tasks_root)}")
            else:
                print(f"STALE {output.relative_to(tasks_root)} (run with --write)")
                problems += 1
    print(f"Checked {count} discussion bundles; problems: {problems}")
    return int(bool(problems))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="regenerate derived files")
    mode.add_argument("--check", action="store_true", help="verify derived files (default)")
    args = parser.parse_args()
    return process(TASKS_ROOT, write=args.write)


if __name__ == "__main__":
    sys.exit(main())
