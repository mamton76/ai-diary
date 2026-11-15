#!/usr/bin/env python3
"""Portable, single-writer task ID registrar.

This script operates ONLY on local repository files. The GitHub adapter (Action)
serializes manual requests and performs a guarded fast-forward push to master.
Tests can run without tokens/network and no real diary data is touched.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = Path("docs/agent-team/tasks")
REGISTRY = TASKS_ROOT / "registry.json"
FOLDER_RE = re.compile(r"^(TASK-(\d{4}))_([a-z0-9]+(?:-[a-z0-9]+)*)$")
ID_RE = re.compile(r"^TASK-(\d{4})$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUEST_RE = re.compile(r"^[A-Za-z0-9_.:-]{5,128}$")


class RegistrationError(ValueError):
    pass


def validate_text(value: str, name: str, length: int = 160) -> str:
    value = value.strip()
    if not value or len(value) > length or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise RegistrationError(f"Invalid {name}: empty, too long or control characters")
    return value


def folders(root: Path) -> dict[str, str]:
    found: dict[str, str] = {}
    for state in ("active", "completed"):
        parent = root / TASKS_ROOT / state
        if not parent.exists():
            continue
        for child in parent.iterdir():
            if not child.is_dir():
                continue
            match = FOLDER_RE.fullmatch(child.name)
            if not match:
                if child.name.startswith("TASK-"):
                    raise RegistrationError(f"Invalid task directory: {child}")
                continue
            task_id, _, slug = match.groups()
            if task_id in found:
                raise RegistrationError(f"Duplicate task ID in folders: {task_id}")
            found[task_id] = slug
    return found


def load_registry(root: Path) -> dict:
    path = root / REGISTRY
    if not path.is_file():
        raise RegistrationError(f"Missing task registry: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistrationError(f"Invalid registry JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("requests"), list):
        raise RegistrationError("Registry needs schema_version=1 and requests array")
    return data


def validate_registry(data: dict, existing: dict[str, str]) -> None:
    keys: set[str] = set()
    ids: set[str] = set()
    for record in data["requests"]:
        if not isinstance(record, dict):
            raise RegistrationError("Registry record must be an object")
        key, task_id, slug = record.get("request_key"), record.get("id"), record.get("slug")
        if not isinstance(key, str) or not REQUEST_RE.fullmatch(key):
            raise RegistrationError("Invalid registry request_key")
        if not isinstance(task_id, str) or not ID_RE.fullmatch(task_id):
            raise RegistrationError("Invalid registry task id")
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            raise RegistrationError("Invalid registry task slug")
        if key in keys or task_id in ids:
            raise RegistrationError("Duplicate registry request_key or task id")
        if task_id in existing and existing[task_id] != slug:
            raise RegistrationError(f"Registry slug conflicts with folder: {task_id}")
        keys.add(key)
        ids.add(task_id)


def allocate(
    root: Path,
    request_key: str,
    slug: str,
    title: str,
    requester: str,
    source: str = "",
    timestamp: str | None = None,
) -> tuple[str, bool]:
    """Register one draft task; returns (task_id, newly_created).

    Do not call concurrently on the same worktree. The adapter uses a serialized
    workflow plus a fast-forward-only git push, retrying on master changes.
    """
    if not REQUEST_RE.fullmatch(request_key):
        raise RegistrationError("request_key must be 5–128 characters [A-Za-z0-9_.:-]")
    if not SLUG_RE.fullmatch(slug) or not 4 <= len(slug) <= 64:
        raise RegistrationError("Invalid task slug (4–64 chars, lowercase kebab-case)")
    title = validate_text(title, "title", 120)
    requester = validate_text(requester, "requester", 80)
    source = validate_text(source, "source", 300) if source else ""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not isinstance(timestamp, str) or not timestamp:
        raise RegistrationError("timestamp is required")
    data = load_registry(root)
    existing = folders(root)
    validate_registry(data, existing)
    for rec in data["requests"]:
        if rec["request_key"] == request_key:
            if (rec["slug"], rec["title"]) != (slug, title):
                raise RegistrationError("Same request_key used for different task metadata")
            return rec["id"], False
    ids = list(existing) + [r["id"] for r in data["requests"]]
    largest = max((int(ID_RE.fullmatch(i).group(1)) for i in ids), default=0)
    if largest >= 9999:
        raise RegistrationError("Task numeric IDs exhausted")
    task_id = f"TASK-{largest + 1:04d}"
    task_dir = root / TASKS_ROOT / "active" / f"{task_id}_{slug}"
    if task_dir.exists():
        raise RegistrationError(f"Task path already exists: {task_dir}")
    now = timestamp
    task_dir.mkdir(parents=True)
    task_text = f"""# {task_id} — {title}

**ID:** {task_id}
**Status:** draft
**Owner / executor:** not assigned
**Created:** `{now}`
**Request key:** `{request_key}`
**Requested by:** {requester}
**Source:** {source or "not specified"}
**Related tasks:** —
**External links:** —
**Presentation:** pending triage (required for nontrivial tasks)
**Presentation source:** —
**Presentation preview URL:** not deployed

## Цель и границы

Уточнить при планировании. Создание этой записи **не разрешает агентам начинать работу**.

## Канонический контекст

Указать действующие документы требований, архитектуры и предыдущие задачи.

## План и исполнители

- [ ] **S1 — Согласовать scope, критерии и распределение ролей**
  - **Исполнитель:** назначается
  - **Проверяет:** Product Owner
  - **Поставлен:** `{now}`
  - **Закрыт:** —
  - **Зависит от:** —
  - **Результат / evidence:** —

## Acceptance criteria

- [ ] Утвердить проверяемые критерии и разрешённый scope.
- [ ] Documentation Impact проверен.

## Documentation Impact

**Документы для проверки:** определить перед реализацией.
**Изменения:** пока не выполнялись.

## Безопасность / запрещённые действия

Без auto-merge/deploy; никаких реальных Google Drive/Calendar/Abacus или пользовательских данных.

## Открытые вопросы

Определить при планировании.
"""
    (task_dir / "task.md").write_text(task_text, encoding="utf-8")
    data["requests"].append({
        "request_key": request_key,
        "id": task_id,
        "slug": slug,
        "title": title,
        "source": source,
        "status": "registered-draft",
    })
    data["requests"].sort(key=lambda rec: rec["id"])
    (root / REGISTRY).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return task_id, True


def validate(root: Path) -> None:
    data = load_registry(root)
    validate_registry(data, folders(root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate", action="store_true", help="check IDs and registry without changes")
    parser.add_argument("--request-key")
    parser.add_argument("--slug")
    parser.add_argument("--title")
    parser.add_argument("--requester")
    parser.add_argument("--source", default="")
    args = parser.parse_args()
    try:
        if args.validate:
            validate(REPO_ROOT)
            print("OK: task registry and active/completed task IDs are consistent")
            return 0
        if not all([args.request_key, args.slug, args.title, args.requester]):
            parser.error("--request-key, --slug, --title and --requester are required")
        task_id, created = allocate(REPO_ROOT, args.request_key, args.slug, args.title,
                                   args.requester, args.source)
    except RegistrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"{'CREATED' if created else 'EXISTS'} {task_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
