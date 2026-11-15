#!/usr/bin/env python3
"""Проверка проекта файлового формата v1 (docs/baseline/07, 08).

Что проверяется:
  1. core-record.schema.json — корректная JSON Schema Draft 2020-12.
  2. Пример Save (examples/file-format-v1/save-with-new-tag.json):
     - каждая JSON-запись проходит схему;
     - каждый FileRef на файл из примера совпадает с SHA-256 точных байтов
       (кодек: UTF-8, ensure_ascii=False, indent=2, финальный LF);
     - цепочка публикаций непрерывна, before-условия совпадают с состоянием
       на предыдущей публикации;
     - replay трёх фаз даёт значения из `expected`.
  3. Положительные примеры отдельных записей (examples/file-format-v1/records/)
     проходят схему. Ссылки в них — заглушки и не разрешаются.
  4. Негативные случаи отклоняются.

Запуск: python3 tools/format-check/check_format.py   (код возврата 0 — всё в порядке)
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs" / "baseline"
SCHEMA = BASE / "schemas" / "file-format-v1" / "core-record.schema.json"
EXAMPLE = BASE / "examples" / "file-format-v1" / "save-with-new-tag.json"
RECORDS = BASE / "examples" / "file-format-v1" / "records"


def file_bytes(f):
    if f["encoding"] == "json":
        return (json.dumps(f["value"], ensure_ascii=False, indent=2) + "\n").encode()
    return f["value"].encode()


def iter_refs(o):
    if isinstance(o, dict):
        if "path" in o and "sha256" in o:
            yield o
        for v in o.values():
            yield from iter_refs(v)
    elif isinstance(o, list):
        for v in o:
            yield from iter_refs(v)


def check_example(ex, validator):
    """Возвращает список ошибок; пустой список — пример корректен."""
    errors = []
    files = ex["files"]
    hashes = {p: hashlib.sha256(file_bytes(f)).hexdigest() for p, f in files.items()}

    for path, f in files.items():
        if f["encoding"] == "json":
            for e in validator.iter_errors(f["value"]):
                errors.append(f"schema: {path}: {e.message[:160]}")

    for ref in iter_refs(ex):
        if ".." in ref["path"].split("/") or ref["path"].startswith("/"):
            errors.append(f"path: недопустимый путь {ref['path']}")
        if ref["path"] in hashes and ref["sha256"] != hashes[ref["path"]]:
            errors.append(f"hash: {ref['path']}")

    commits = sorted(p for p in files if p.startswith("_system/commits/"))
    resources = {}
    states = {}
    for i, path in enumerate(commits):
        pub = files[path]["value"]
        if pub.get("sequence") != i:
            errors.append(f"chain: {path} sequence {pub.get('sequence')} != {i}")
        prev = pub.get("previous")
        if i == 0 and prev is not None:
            errors.append("chain: genesis имеет previous")
        if i > 0 and (prev is None or prev["path"] != commits[i - 1]):
            errors.append(f"chain: {path} previous не указывает на {commits[i - 1]}")
        for cond in pub.get("conditions", []):
            if resources.get(cond["resourceKey"], cond["expected"]) != cond["expected"]:
                errors.append(f"condition: {path} {cond['resourceKey']}")
        for ch in pub.get("changes", []):
            key = ch["resourceKey"]
            if resources.get(key) != ch["before"]:
                errors.append(f"before: {path} {key} не совпадает с текущим состоянием")
            resources[key] = ch["after"]
        states[path] = copy.deepcopy(resources)

    def snapshot(phase_path):
        res = states.get(phase_path, {})
        out = {"currentRevisionId": None, "hasDraft": False, "canonicalTagIds": [], "operationStatus": None}
        for key, ref in res.items():
            if ref is None or ref["path"] not in files:
                continue
            v = files[ref["path"]]["value"]
            if key.startswith("entry:"):
                out["currentRevisionId"] = v["currentRevisionId"]
                out["hasDraft"] = v["draftCursor"]["path"] in files
            elif key == "catalog:tags":
                out["canonicalTagIds"] = [t["tagId"] for t in v["tags"]]
            elif key.startswith("operation:"):
                out["operationStatus"] = v["status"]
        return out

    for phase, ref in ex["phases"].items():
        got = snapshot(ref["path"])
        exp = ex["expected"][phase]
        for k, val in exp.items():
            if got.get(k) != val:
                errors.append(f"replay: {phase}.{k} = {got.get(k)!r}, ожидалось {val!r}")
    return errors


def negative_cases(ex):
    """(название, функция-мутация примера). Каждый случай обязан дать ошибку."""
    files_key = lambda e, suffix: next(p for p in e["files"] if p.endswith(suffix))

    def dup_tags(e):
        d = e["files"][files_key(e, "draft/slots/000007/DRAFT.json")]["value"]
        d["content"]["tagIds"].append(d["content"]["tagIds"][0])

    def wrong_hash(e):
        r = e["files"][files_key(e, "_system/commits/000002.json")]["value"]["previous"]
        r["sha256"] = "0" * 64

    def stale_before(e):
        pub = e["files"][files_key(e, "_system/commits/000002.json")]["value"]
        pub["changes"][0]["before"] = copy.deepcopy(pub["changes"][0]["after"])

    def approx_without_evidence(e):
        d = e["files"][files_key(e, "draft/slots/000007/DRAFT.json")]["value"]
        d["content"]["eventTime"]["uncertainties"] = [{"field": "from", "kind": "approximate"}]

    def unknown_publication_kind(e):
        e["files"][files_key(e, "_system/commits/000002.json")]["value"]["kind"] = "AUTOSAVE"

    def synthetic_without_type(e):
        v = e["files"][files_key(e, "states/state_after/ENTRY.json")]["value"]
        v["origin"] = {"kind": "SYNTHETIC", "syntheticType": None}

    def legacy_draft_ref(e):
        v = e["files"][files_key(e, "states/state_after/ENTRY.json")]["value"]
        v["draftRef"] = None

    def time_with_seconds(e):
        d = e["files"][files_key(e, "draft/slots/000007/DRAFT.json")]["value"]
        d["content"]["eventTime"]["from"]["time"] = "12:30:00"

    return [
        ("повтор tagId", dup_tags),
        ("неверный hash", wrong_hash),
        ("устаревшее before-условие", stale_before),
        ("approximate без evidence", approx_without_evidence),
        ("неизвестный вид публикации", unknown_publication_kind),
        ("синтетическая запись без типа", synthetic_without_type),
        ("старое поле draftRef", legacy_draft_ref),
        ("время с секундами", time_with_seconds),
    ]


def main():
    schema = json.loads(SCHEMA.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    failures = 0

    ex = json.loads(EXAMPLE.read_text())
    errs = check_example(ex, validator)
    print(f"пример Save: {len(ex['files'])} файлов, ошибок {len(errs)}")
    for e in errs:
        print("  ", e)
    failures += len(errs)

    for path in sorted(RECORDS.glob("*.json")):
        rec_errs = list(validator.iter_errors(json.loads(path.read_text())))
        print(f"запись {path.name}: {'ok' if not rec_errs else rec_errs[0].message[:160]}")
        failures += len(rec_errs)

    for name, mutate in negative_cases(ex):
        bad = copy.deepcopy(ex)
        mutate(bad)
        # хеши пересчитываются, чтобы ловилась именно сама мутация, а не побочный рассинхрон
        if name not in ("неверный hash",):
            files = bad["files"]
            for _ in range(20):
                hashes = {p: hashlib.sha256(file_bytes(f)).hexdigest() for p, f in files.items()}
                changed = False
                for ref in iter_refs(bad):
                    if ref["path"] in hashes and ref["sha256"] != hashes[ref["path"]]:
                        ref["sha256"] = hashes[ref["path"]]
                        changed = True
                if not changed:
                    break
        caught = check_example(bad, validator)
        print(f"негативный случай «{name}»: {'отклонён' if caught else 'НЕ ОТКЛОНЁН'}")
        if not caught:
            failures += 1

    print("ИТОГ:", "OK" if failures == 0 else f"ошибок {failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
