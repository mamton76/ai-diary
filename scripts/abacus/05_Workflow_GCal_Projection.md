# Agent Workflow — Google Calendar Timeline Projection

## 1. Workflow goal

Project diary entries from the file system into a Google Calendar timeline.

This is a **one-way** sync: `entries/ → Google Calendar`.
Calendar edits do not write back into diary files.

Google Calendar is derived, rebuildable projection data.
The file system remains the source of truth.

---

## 2. Script

```
ai-diary/gcal_projection.py
```

Run with `--dry-run` first.

---

## 3. Quick start

```bash
# Dry run
python gcal_projection.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --credentials google_credentials.json \
  --token google_token.json \
  --dry-run

# Sync up to 20 entries
python gcal_projection.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --credentials google_credentials.json \
  --token google_token.json \
  --limit 20
```

---

## 4. Configuration

The workflow reads `_system/integrations/google_calendar_projection.json` from Drive.

If the file does not exist, it is created with default values on first run.

Key fields:

| Field | Description |
|---|---|
| `enabled` | Enable/disable sync |
| `calendarId` | Google Calendar id (set on first run) |
| `calendarName` | Target calendar display name |
| `includeStatuses` | Which entry statuses to project |
| `syncMode` | Always `one_way_files_to_calendar` for MVP |
| `colorBy` | Always `entry.status` |
| `statusColors` | Abstract color names per status |
| `defaultDurationMinutes` | Duration for entries with only a date |
| `dateOnlyEntriesAsAllDay` | Render date-only entries as all-day events |

---

## 5. Calendar event rendering

### Title format

```
{statusIcon} {assetIcons} {title} · {topTags}
```

Examples:
```
✅ 📷3 Прогулка с Лисом · #Лис #парк
❓ 🎙️ Разговор про школу · #Федор #школа
⚠️ Импорт не разобран · #import
```

### Description sections

```
AI Diary Entry

Status: needs_review
Time confidence: inferred

Tags:
#Федор #школа #предметы

Assets:
📷 photo_001.jpg
assets/by_id/asset_01HWPHOTO/original.jpg

Entry path:
entries/2026/04/2026-04-25__entry_01HWABC/
```

### Color mapping (Google Calendar colorId)

| Status | Color name | colorId |
|---|---|---|
| raw | graphite | 8 |
| processed | sage | 2 |
| needs_review | banana | 5 |
| ai_proposed | peacock | 7 |
| user_edited | grape | 3 |
| failed | tomato | 11 |
| archived | graphite | 8 |

---

## 6. Sync index

`indexes/google_calendar_events.jsonl` tracks the mapping between entries and events.

Each line:
```json
{"formatVersion":"v0.1.0","entryId":"entry_01HWABC","calendarId":"xxx","googleEventId":"abc","lastSyncedAt":"2026-04-26T12:00:00Z","entryHash":"sha256:...","syncStatus":"synced"}
```

The hash is computed from `ENTRY.json` + `entry.md` content.
If the hash changes, the calendar event is updated.

---

## 7. Run logs

Each run writes:
```
_runs/calendar_sync_YYYY-MM-DD_NNN.json
```

---

## 8. Error handling

| Situation | Behavior |
|---|---|
| Entry missing required time | Skip; log warning |
| Calendar event create fails | Log error; entry not marked synced |
| Config file missing | Create default config; continue |
| Calendar not found | Create calendar; write id to config |
