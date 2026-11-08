#!/usr/bin/env python3
"""
AI Diary — Telegram Sync Agent

Listens for commands from Telegram and runs the 3-step diary sync workflow:
  1. gcal_to_inbox.py    — Google Calendar Inbox → Drive inbox/new/
  2. input_to_entry_2.py — Drive inbox/new/ → entries/
  3. gcal_projection.py  — entries/ → Google Calendar Timeline

Commands:
  /sync       — run all 3 steps
  /sync1      — step 1 only
  /sync2      — step 2 only
  /sync3      — step 3 only
  /status     — show last run summary
  /help       — show available commands

Configuration:
  All secrets and runtime config are read from environment variables.
  Create a .env file based on .env.example and source it before starting:

      set -a && source .env && set +a
      python diary_sync_agent.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests


# ------------------------------------------------------------------ #
# Settings                                                            #
# ------------------------------------------------------------------ #

def _required(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

def _optional(name: str, default: str) -> str:
    v = os.environ.get(name, "").strip()
    return v if v else default

def _required_int(name: str) -> int:
    raw = _required(name)
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(f"Environment variable {name} must be an integer, got: {raw!r}")

def _optional_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(f"Environment variable {name} must be an integer, got: {raw!r}")


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    allowed_chat_id: int
    root_folder_id: str
    scripts_dir: Path
    python_bin: str
    google_credentials_file: Path
    google_token_file: Path
    gcal_inbox_calendar_id: str
    gcal_processed_calendar_id: str
    gcal_timeline_calendar_name: str
    sync_timeout_seconds: int
    max_events_per_sync: int


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=_required("TELEGRAM_BOT_TOKEN"),
        allowed_chat_id=_required_int("TELEGRAM_ALLOWED_CHAT_ID"),
        root_folder_id=_required("AI_DIARY_ROOT_FOLDER_ID"),
        scripts_dir=Path(_optional("AI_DIARY_SCRIPTS_DIR", str(Path(__file__).parent))),
        python_bin=_optional("AI_DIARY_PYTHON", "python3"),
        google_credentials_file=Path(_optional("GOOGLE_CREDENTIALS_FILE",
            str(Path(__file__).parent / "google_credentials.json"))),
        google_token_file=Path(_optional("GOOGLE_TOKEN_FILE",
            str(Path(__file__).parent / "google_token.json"))),
        gcal_inbox_calendar_id=_required("GCAL_INBOX_CALENDAR_ID"),
        gcal_processed_calendar_id=_required("GCAL_PROCESSED_CALENDAR_ID"),
        gcal_timeline_calendar_name=_optional("GCAL_TIMELINE_CALENDAR_NAME", "AI Diary Timeline"),
        sync_timeout_seconds=_optional_int("AI_DIARY_SYNC_TIMEOUT_SECONDS", 900),
        max_events_per_sync=_optional_int("AI_DIARY_MAX_EVENTS_PER_SYNC", 5),
    )


# ------------------------------------------------------------------ #
# Telegram helpers                                                    #
# ------------------------------------------------------------------ #

def tg_api(cfg: Settings) -> str:
    return f"https://api.telegram.org/bot{cfg.telegram_bot_token}"

def tg_get(cfg: Settings, method: str, **params) -> dict:
    resp = requests.get(f"{tg_api(cfg)}/{method}", params=params, timeout=10)
    return resp.json()

def tg_send(cfg: Settings, chat_id: int, text: str, parse_mode: str = "HTML") -> None:
    max_len = 4096
    while text:
        chunk, text = text[:max_len], text[max_len:]
        requests.post(f"{tg_api(cfg)}/sendMessage", json={
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": parse_mode,
        }, timeout=10)


# ------------------------------------------------------------------ #
# State                                                               #
# ------------------------------------------------------------------ #

STATE_FILE = Path(__file__).parent / "diary_agent_state.json"

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_update_id": 0, "last_run": None}

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------ #
# Workflow steps                                                      #
# ------------------------------------------------------------------ #

def run_step(name: str, cmd: list[str], timeout: int) -> tuple[bool, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"⏱ {name}: timeout after {timeout}s"
    except Exception as exc:
        return False, f"💥 {name}: {exc}"


def extract_summary(output: str) -> str:
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if "SUMMARY" in line or ("=" * 10 in line and i > len(lines) // 2):
            return "\n".join(lines[i:])
    return "\n".join(lines[-15:]) if lines else "(no output)"


def run_full_sync(cfg: Settings, chat_id: int, steps: list[int]) -> None:
    tg_send(cfg, chat_id, "🔄 <b>Запускаю синхронизацию дневника...</b>")

    creds = str(cfg.google_credentials_file)
    token = str(cfg.google_token_file)
    root  = cfg.root_folder_id
    py    = cfg.python_bin
    sd    = str(cfg.scripts_dir)
    n     = str(cfg.max_events_per_sync)

    step_configs = {
        1: {
            "name": "Шаг 1 — Календарь-инбокс → Файловый инбокс",
            "emoji": "📥",
            "cmd": [
                py, str(cfg.scripts_dir / "gcal_to_inbox.py"),
                "--root-folder-id", root,
                "--credentials", creds, "--token", token,
                "--inbox-calendar-id",     cfg.gcal_inbox_calendar_id,
                "--processed-calendar-id", cfg.gcal_processed_calendar_id,
                "--limit", n,
            ],
        },
        2: {
            "name": "Шаг 2 — Файловый инбокс → Записи",
            "emoji": "⚙️",
            "cmd": [
                py, str(cfg.scripts_dir / "input_to_entry_2.py"),
                "--root-folder-id", root,
                "--credentials", creds, "--token", token,
                "--limit", n,
            ],
        },
        3: {
            "name": "Шаг 3 — Записи → Календарь-таймлайн",
            "emoji": "📅",
            "cmd": [
                py, str(cfg.scripts_dir / "gcal_projection.py"),
                "--root-folder-id", root,
                "--credentials", creds, "--token", token,
                "--calendar-name", cfg.gcal_timeline_calendar_name,
                "--limit", "100",
            ],
        },
    }

    results = []
    for step_num in steps:
        cfg_step = step_configs[step_num]
        tg_send(cfg, chat_id, f"{cfg_step['emoji']} <b>{cfg_step['name']}</b>")

        start = time.time()
        ok, output = run_step(cfg_step["name"], cfg_step["cmd"], cfg.sync_timeout_seconds)
        elapsed = time.time() - start

        summary = extract_summary(output)
        icon = "✅" if ok else "❌"
        tg_send(cfg, chat_id, (
            f"{icon} <b>{cfg_step['name']}</b>\n"
            f"Время: {elapsed:.1f}с\n\n"
            f"<pre>{summary[:1500]}</pre>"
        ))
        results.append({"step": step_num, "ok": ok, "elapsed": elapsed})

    ok_steps = sum(1 for r in results if r["ok"])
    final_icon = "✅" if all(r["ok"] for r in results) else "⚠️"
    tg_send(cfg, chat_id, (
        f"{final_icon} <b>Готово</b>: {ok_steps}/{len(results)} шагов успешно\n"
        f"Всего: {sum(r['elapsed'] for r in results):.1f}с"
    ))

    state = load_state()
    state["last_run"] = {
        "at": datetime.now(timezone.utc).isoformat(),
        "steps": steps,
        "ok": all(r["ok"] for r in results),
        "step_results": results,
    }
    save_state(state)


# ------------------------------------------------------------------ #
# Command handler                                                     #
# ------------------------------------------------------------------ #

HELP_TEXT = """
<b>AI Diary Sync Bot</b>

/sync  — полная синхронизация (все 3 шага)
/sync1 — шаг 1: Календарь-инбокс → Файловый инбокс
/sync2 — шаг 2: Файловый инбокс → Записи дневника
/sync3 — шаг 3: Записи → Таймлайн-календарь
/status — последний запуск
/help  — эта справка
""".strip()


def handle_command(cfg: Settings, chat_id: int, text: str) -> None:
    cmd = text.strip().lower().split()[0].split("@")[0]

    if cmd == "/sync":
        run_full_sync(cfg, chat_id, [1, 2, 3])
    elif cmd == "/sync1":
        run_full_sync(cfg, chat_id, [1])
    elif cmd == "/sync2":
        run_full_sync(cfg, chat_id, [2])
    elif cmd == "/sync3":
        run_full_sync(cfg, chat_id, [3])
    elif cmd == "/status":
        state = load_state()
        last = state.get("last_run")
        if not last:
            tg_send(cfg, chat_id, "Ещё не было запусков.")
        else:
            icon = "✅" if last["ok"] else "⚠️"
            at = last["at"][:19].replace("T", " ")
            steps = ", ".join(str(s) for s in last["steps"])
            tg_send(cfg, chat_id, f"{icon} Последний запуск: {at} UTC\nШаги: {steps}")
    elif cmd in ("/start", "/help"):
        tg_send(cfg, chat_id, HELP_TEXT)
    else:
        tg_send(cfg, chat_id, "Неизвестная команда. /help — список команд.")


# ------------------------------------------------------------------ #
# Main polling loop                                                   #
# ------------------------------------------------------------------ #

def main() -> None:
    try:
        cfg = load_settings()
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        print("Create a .env file based on .env.example and source it before starting.", file=sys.stderr)
        sys.exit(1)

    print(f"AI Diary Sync Agent started.")
    print(f"  Allowed chat_id: {cfg.allowed_chat_id}")
    print(f"  Scripts dir:     {cfg.scripts_dir}")
    print(f"  Root folder id:  {cfg.root_folder_id}")

    state = load_state()
    offset = state.get("last_update_id", 0) + 1

    while True:
        try:
            data = tg_get(cfg, "getUpdates", offset=offset, timeout=30)
            for update in data.get("result", []):
                update_id = update["update_id"]
                offset = update_id + 1
                state["last_update_id"] = update_id
                save_state(state)

                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")

                if not text or not chat_id:
                    continue
                if chat_id != cfg.allowed_chat_id:
                    print(f"Ignored message from unknown chat_id={chat_id}")
                    continue

                print(f"Command: {text}")
                try:
                    handle_command(cfg, chat_id, text)
                except Exception as exc:
                    print(f"Error: {traceback.format_exc()}")
                    tg_send(cfg, chat_id, f"❌ Ошибка: {exc}")

        except Exception as exc:
            print(f"Polling error: {exc}")
            time.sleep(5)

        time.sleep(2)


if __name__ == "__main__":
    main()
