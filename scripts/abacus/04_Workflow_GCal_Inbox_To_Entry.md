# Agent Workflow — Google Calendar Inbox to Entry

## 1. Workflow goal

Use Google Calendar as a lightweight voice-friendly inbox for AI Diary.

The user creates raw diary notes as Google Calendar events (e.g. via Gemini voice input).
The agent reads events from a dedicated inbox calendar, converts them into structured inbox items
in `inbox/new/`, runs the normal `Inbox to Entry` workflow, then moves successfully processed
events to a separate processed calendar.

Google Calendar is **not** diary storage — it is only an external capture channel / queue.
The file system (Google Drive) remains the source of truth.

---

## 2. Script

```
ai-diary/gcal_inbox_to_entry.py
```

Run with `--dry-run` first.

---

## 3. Quick start

```bash
# Dry run — show what would be processed
python gcal_inbox_to_entry.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --inbox-calendar "AI Diary Inbox" \
  --processed-calendar "AI Diary Processed" \
  --credentials google_credentials.json \
  --token google_token.json \
  --dry-run

# Process up to 3 events
python gcal_inbox_to_entry.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --inbox-calendar "AI Diary Inbox" \
  --processed-calendar "AI Diary Processed" \
  --credentials google_credentials.json \
  --token google_token.json \
  --limit 3
```

---

## 4. Required calendar setup

Create two Google Calendars:

- **AI Diary Inbox** — raw unprocessed events (user adds here via voice/Gemini)
- **AI Diary Processed** — events moved here after successful entry creation

---

## 5. File output per event

```
inbox/new/<timestamp>__google_calendar__event_<hash>/
  MESSAGE.json
  raw_text.md
  source_event.json
```

After `Inbox to Entry` runs successfully:

```
inbox/_processed_raw/YYYY/MM/raw_batch_<date>_<N>/
  original_files/
    MESSAGE.json
    raw_text.md
    source_event.json
  PROCESSING_RESULT.json
```

---

## 6. Auth scopes required

The script needs both Drive and Calendar scopes:

```
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/calendar
```

If existing token only has Drive scope, delete `google_token.json` and re-run —
the script will open a browser for re-authorization.

---

## 7. Error handling

| Situation | Behavior |
|---|---|
| Event has no title and no description | Skip; log warning; leave in Inbox |
| Entry creation fails | Leave event in Inbox; move package to `inbox/failed/` |
| Event move to Processed fails | Log error; entry already created; rely on deterministic ID on retry |

---

## 8. Duplicate prevention

Deterministic raw input ID derived from `hash(calendarId + eventId + startDateTime)`.
Before creating a new package, the script checks whether a `MESSAGE.json` with the same
`rawInputId` already exists in recent processed raw archive or in `inbox/new/`.
