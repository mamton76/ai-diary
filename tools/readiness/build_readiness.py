#!/usr/bin/env python3
"""Собирает срез готовности требований AI Diary из docs/baseline в JSON.

Выход (в каталог, переданный первым аргументом, по умолчанию текущий):
  requirements.json — требования из 02-requirements-inventory.md
  questions.json    — вопросы из 04-open-questions.md, Functional/Screens Spec
                      и подвопросы (SQ) из индексов discussion threads
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs" / "baseline"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def req_group(raw: str) -> str:
    s = raw.upper()
    if s.startswith("ПОДТВЕРЖДЕНО") and "/ ОТЛОЖЕНО" not in s:
        return "Подтверждено"
    if s.startswith("РАБОЧЕЕ_НАПРАВЛЕНИЕ"):
        return "Рабочее направление"
    if s.startswith("ОТКРЫТО"):
        return "Открыто"
    if "ОТЛОЖЕНО" in s or "FUTURE" in s or "PARKED" in s:
        return "Отложено"
    return "Устарело / не требуется"


def requirements():
    rows, area = [], None
    lines = (BASE / "02-requirements-inventory.md").read_text().splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^# ([A-Z]\d?)\. (.+)$", line)
        if m:
            area = f"{m.group(1)}. {m.group(2).strip()}"
            continue
        m = re.match(r"^### ([A-Z]+-\d+) — (.+)$", line)
        if not m:
            continue
        raw = ""
        for nxt in lines[i + 1:i + 6]:
            sm = re.match(r"^\*\*Статус:\*\*\s*(.*)$", nxt)
            if sm:
                raw = sm.group(1).strip().rstrip(".").strip()
                break
        short = re.split(r"[.(]", raw)[0].strip() or "—"
        rows.append({"id": m.group(1), "area": area, "title": m.group(2).strip(),
                     "status": req_group(raw), "status_raw": short[:60]})
    return rows


def q_group(text: str) -> str:
    s = text.lower()
    if "отлож" in s:
        return "Отложено"
    if "частично" in s or "остаток" in s or "обсужда" in s or "ждём" in s:
        return "Частично / в работе"
    if "решен" in s or "решён" in s or "решено" in s:
        return "Решено"
    return "Открыто"


def thread_meta():
    """lifecycle/claim из индексов тредов: {id: (lifecycle, claim, status)}"""
    meta = {}
    for idx in BASE.glob("*.threads/00_index.md"):
        for line in idx.read_text().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 6 or not re.match(r"^(PQ|AQ|FQ|UI)", cells[1]):
                continue
            qid = cells[1].split(" ")[0]
            life = re.sub(r"^[^\w]+", "", cells[4]).strip()
            meta[qid] = {"lifecycle": life, "claim": cells[5], "status_txt": cells[3],
                         "title": cells[2], "source": idx.parent.name}
    return meta


def questions():
    meta = thread_meta()
    rows = []
    # 1. 04-open-questions.md
    lines = (BASE / "04-open-questions.md").read_text().splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^## ((?:PQ|AQ)-[A-Z\-]*\d+) — (.+)$", line)
        if not m:
            continue
        st = ""
        for nxt in lines[i + 1:]:
            if nxt.startswith("## ") or nxt.startswith("# "):
                break
            sm = re.match(r"^\*\*Статус:\*\*\s*(.*)$", nxt)
            if sm:
                st = sm.group(1)
                break
        qid = m.group(1)
        kind = re.match(r"^(PQ|AQ-[A-Z]+)", qid).group(1)
        rows.append({"id": qid, "title": m.group(2).strip(), "doc": "Открытые вопросы",
                     "kind": kind, "status": q_group(st) if st else "Открыто",
                     "thread": "да" if qid in meta else "нет", "parent": ""})
    # 2. Functional Spec §14 table
    for line in (BASE / "AI-Diary-Functional-Spec-v0.1.md").read_text().splitlines():
        m = re.match(r"^\| (FQ-\d+)( — [^|]+)? \| ([^|]+) \|", line)
        if m:
            qid = m.group(1)
            rows.append({"id": qid, "title": m.group(3).strip(), "doc": "Функциональное ТЗ",
                         "kind": "FQ", "status": q_group(m.group(2) or ""),
                         "thread": "да" if qid in meta else "нет", "parent": ""})
    # 3. Screens Spec table
    for line in (BASE / "AI-Diary-Screens-Spec-v0.1.md").read_text().splitlines():
        m = re.match(r"^\| (UI-Q\d+)( — [^|]+)? \| ([^|]+) \|", line)
        if m:
            qid = m.group(1)
            title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", m.group(3)).strip()
            title = re.split(r":\s*история|:\s*$", title)[0].strip()
            rows.append({"id": qid, "title": title[:90], "doc": "Спецификация экранов",
                         "kind": "UI-Q", "status": q_group(m.group(2) or ""),
                         "thread": "да" if qid in meta else "нет", "parent": ""})
    # 4. Подвопросы SQ из индексов тредов
    for qid, mt in meta.items():
        if "/SQ-" not in qid:
            continue
        parent = qid.split("/")[0]
        doc = "Функциональное ТЗ" if parent.startswith("FQ") else "Открытые вопросы"
        rows.append({"id": qid, "title": mt["title"], "doc": doc, "kind": "SQ",
                     "status": q_group(mt["status_txt"]), "thread": "да", "parent": parent})
    for r in rows:
        mt = meta.get(r["id"], {})
        r["lifecycle"] = mt.get("lifecycle", "—") or "—"
        claim = mt.get("claim", "")
        r["claim"] = "активен" if claim == "active" else "—"
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    req, qs = requirements(), questions()
    (OUT / "requirements.json").write_text(json.dumps(req, ensure_ascii=False, indent=1))
    (OUT / "questions.json").write_text(json.dumps(qs, ensure_ascii=False, indent=1))
    print(f"commit {sha}: {len(req)} требований, {len(qs)} вопросов -> {OUT}")


if __name__ == "__main__":
    main()
