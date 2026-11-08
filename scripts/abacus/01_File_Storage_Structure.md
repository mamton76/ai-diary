# AI Diary — File Storage Structure
:
## 1. Purpose of this document

This document describes the proposed folder structure for the file-based AI Diary storage.

The storage may live on:

- Google Drive;
- local disk;
- mounted cloud drive;
- VPS-attached storage;
- another file system compatible backend.

The structure is designed to support:

- raw unstructured capture;
- conversion into structured diary entries;
- preservation of original files;
- prompt-based AI workflows;
- simple tag catalog;
- future migration and indexing.

---

## 2. Top-level structure

```text
AI-Diary/
  _system/
  _formats/
  _prompts/
  _agents/
  _runs/
  inbox/
  entries/
  assets/
  catalogs/
  indexes/
  exports/
  backups/
  migrations/
  trash/
```

Not all folders are required in the first prototype.

The minimal active folders are:

```text
AI-Diary/
  _system/
  _formats/
  _prompts/
  inbox/
  entries/
  assets/
  catalogs/
  indexes/
```

---

## 3. `_system/`

```text
_system/
  storage_manifest.json
  status.json
```

### Purpose

Stores global information about the diary storage.

### `storage_manifest.json`

Describes the storage itself.

Example:

```json
{
  "formatVersion": "v0.1.0",
  "storageId": "ai-diary-main",
  "storageType": "google_drive",
  "createdAt": "2026-04-25T12:00:00Z",
  "currentPromptSet": "promptset_2026-04-25_001",
  "paths": {
    "inbox": "inbox/",
    "entries": "entries/",
    "assets": "assets/",
    "catalogs": "catalogs/",
    "indexes": "indexes/"
  }
}
```

### `status.json`

Describes the current operational mode.

Example:

```json
{
  "mode": "normal",
  "activeMigration": null,
  "lastAgentRun": null,
  "notes": []
}
```

Possible modes:

```text
normal
read_only
processing
migration_in_progress
backup_in_progress
maintenance
```

---

## 4. `_formats/`

```text
_formats/
  v0.1.0/
    README.md
    entry.schema.json
    tag.schema.json
    raw_input.schema.json
```

### Purpose

Stores descriptions and schemas for the file format.

The format version is important because the diary storage will evolve.

Every important JSON file should include:

```json
{
  "formatVersion": "v0.1.0"
}
```

---

## 5. `_prompts/`

```text
_prompts/
  active/
    PROMPTSET.json
    inbox_to_entry.prompt.md
    tag_extraction.prompt.md
    cleanup_text.prompt.md

  archive/
```

### Purpose

Stores prompts used by agents.

The agent should read prompts from files instead of having them hardcoded.

### `PROMPTSET.json`

`PROMPTSET.json` is a manifest of active prompts.

It is not itself a prompt.

It tells the system:

- which prompts are active;
- where prompt files are located;
- what each prompt is for;
- which version of each prompt is being used.

Minimal example:

```json
{
  "formatVersion": "v0.1.0",
  "promptSetId": "promptset_2026-04-25_001",
  "status": "active",
  "createdAt": "2026-04-25T12:00:00Z",
  "prompts": [
    {
      "id": "inbox_to_entry",
      "version": "2026-04-25.1",
      "path": "inbox_to_entry.prompt.md",
      "purpose": "Turn raw inbox files into diary entries"
    },
    {
      "id": "tag_extraction",
      "version": "2026-04-25.1",
      "path": "tag_extraction.prompt.md",
      "purpose": "Suggest tags for an entry"
    },
    {
      "id": "cleanup_text",
      "version": "2026-04-25.1",
      "path": "cleanup_text.prompt.md",
      "purpose": "Clean messy text while preserving meaning"
    }
  ]
}
```

---

## 6. `inbox/`

```text
inbox/
  drop/
    text/
    media/
    mixed/

  new/
  processing/
  needs_review/
  failed/
  archived/

  _processed_raw/
```

### Purpose

Inbox is the capture zone.

It may contain completely unstructured files.

The agent must accept that some files have no metadata.

---

### 6.1 `inbox/drop/`

This is the raw drop zone.

Users can manually place files here.

Examples:

```text
inbox/drop/text/
  2026-04-25-walk-with-lis.md
  random-note.txt

inbox/drop/media/
  IMG_1234.jpg
  screenshot.png

inbox/drop/mixed/
  trip-note.md
  photo1.jpg
  photo2.jpg
```

No `MESSAGE.json` is required here.

The agent may infer information from:

- file name;
- file timestamps;
- EXIF metadata;
- file content;
- nearby files.

---

### 6.2 `inbox/new/`

This folder is for structured inbox items created by a capture tool such as a Telegram bot, web app, Android app, or import script.

Example:

```text
inbox/new/2026-04-25T12-34-18Z__telegram__msg_01HWXYZ/
  MESSAGE.json
  raw_text.md
  attachments/
    voice_001.ogg
    photo_001.jpg
```

---

### 6.3 `inbox/processing/`

Temporary folder for items currently being processed.

Agents may move items here to avoid duplicate work.

---

### 6.4 `inbox/needs_review/`

Items that the agent could not confidently process.

Examples:

- date unclear;
- file content ambiguous;
- multiple possible entries;
- unsupported format;
- conflicting metadata.

---

### 6.5 `inbox/failed/`

Items that failed due to technical errors.

The agent should include a small error report.

---

### 6.6 `inbox/archived/`

Structured inbox items that were successfully processed.

---

### 6.7 `inbox/_processed_raw/`

Raw files from `inbox/drop/` after processing.

The original files should be preserved here.

Example:

```text
inbox/_processed_raw/
  2026/
    04/
      raw_batch_2026-04-25_001/
        original_files/
          2026-04-25-walk-with-lis.md
          IMG_1234.jpg
        PROCESSING_RESULT.json
```

`PROCESSING_RESULT.json` links raw files to created entities.

Example:

```json
{
  "formatVersion": "v0.1.0",
  "rawInputId": "raw_2026-04-25_walk_with_lis",
  "processedAt": "2026-04-25T13:10:00Z",
  "sourceFiles": [
    "original_files/2026-04-25-walk-with-lis.md",
    "original_files/IMG_1234.jpg"
  ],
  "createdEntities": [
    {
      "type": "entry",
      "id": "entry_01HWABC",
      "path": "entries/2026/04/2026-04-25__entry_01HWABC/ENTRY.json"
    }
  ],
  "status": "processed"
}
```

---

## 7. `entries/`

```text
entries/
  2026/
    04/
      2026-04-25__entry_01HWABC/
        ENTRY.json
        entry.md
        revisions/
        links/
        ai/
```

### Purpose

Stores structured diary entries.

Each entry is a folder.

The folder name should include a date and stable entry id.

Avoid relying on tags in folder names because tags may change.

---

### 7.1 Entry folder

```text
2026-04-25__entry_01HWABC/
  ENTRY.json
  entry.md

  revisions/
    000_raw/
      revision.json
      text.md
    001_ai_cleaned/
      revision.json
      text.md
    002_user_edited/
      revision.json
      text.md

  links/
    source_raw_inputs.json

  ai/
    tag_proposals.json
    notes.md
```

---

### 7.2 `ENTRY.json`

Canonical metadata for the entry.

Example:

```json
{
  "formatVersion": "v0.1.0",
  "schema": "entry",
  "id": "entry_01HWABC",
  "title": "Walk with Lis",
  "createdAt": "2026-04-25T13:00:00Z",
  "updatedAt": "2026-04-25T13:20:00Z",
  "time": {
    "entryDate": "2026-04-25",
    "startDateTime": "2026-04-25T10:30:00+02:00",
    "endDateTime": null,
    "confidence": "inferred"
  },
  "status": "processed",
  "currentRevisionId": "rev_001_ai_cleaned",
  "rawRevisionId": "rev_000_raw",
  "tags": [
    {
      "tagId": "tag_lis",
      "source": "ai",
      "confidence": 0.93
    }
  ],
  "source": {
    "rawInputRefs": [
      "inbox/_processed_raw/2026/04/raw_batch_2026-04-25_001/PROCESSING_RESULT.json"
    ]
  }
}
```

---

## 8. `assets/`

```text
assets/
  by_id/
    asset_01HWPHOTO/
      ASSET.json
      original.jpg
      preview.webp
      metadata.json
```

### Purpose

Stores media and attached files.

Entries may reference assets by id.

The same asset may be linked to more than one entry.

Example `ASSET.json`:

```json
{
  "formatVersion": "v0.1.0",
  "id": "asset_01HWPHOTO",
  "type": "image",
  "createdAt": "2026-04-25T12:40:00Z",
  "storage": {
    "type": "file",
    "path": "assets/by_id/asset_01HWPHOTO/original.jpg"
  },
  "metadata": {
    "originalFileName": "IMG_1234.jpg",
    "mimeType": "image/jpeg",
    "exifDateTime": "2026-04-25T12:39:10+02:00"
  }
}
```

---

## 9. `catalogs/`

```text
catalogs/
  tags/
    tags.json
    aliases.json
```

### Purpose

Stores tag catalog.

At this stage there are no separate catalogs for people, places, or sources.

People, places, pets, moods, activities, and projects may all be represented as tags.

Example `tags.json`:

```json
{
  "formatVersion": "v0.1.0",
  "items": [
    {
      "id": "tag_lis",
      "name": "Lis",
      "slug": "lis",
      "type": "pet",
      "createdBy": "user",
      "aliases": ["dog", "Lisich"]
    },
    {
      "id": "tag_fedor_school",
      "name": "Fedor school",
      "slug": "fedor-school",
      "type": "topic",
      "createdBy": "user",
      "aliases": []
    },
    {
      "id": "tag_trip_moscow_2025",
      "name": "Moscow trip, May 2025",
      "slug": "trip-moscow-2025-05",
      "type": "event_cluster",
      "createdBy": "ai",
      "aliases": []
    }
  ]
}
```

Suggested initial tag types:

```text
topic
person
pet
place
event_cluster
project
activity
mood
system
```

These types are soft categories, not a strict ontology.

---

## 10. `indexes/`

```text
indexes/
  entries_by_date.jsonl
  entries_by_tag.jsonl
```

### Purpose

Indexes are derived data.

They are useful for UI and search, but they are not the source of truth.

They can be deleted and rebuilt from entries and catalogs.

For the first prototype, only `entries_by_date.jsonl` may be enough.

---

## 11. `_agents/`

```text
_agents/
  workflows/
```

### Purpose

Stores workflow descriptions for agents.

This can be kept minimal in the first prototype.

---

## 12. `_runs/`

```text
_runs/
  run_2026-04-25_001.json
```

### Purpose

Stores logs of agent executions.

This is useful later for debugging and reproducibility.

For manual early debugging, this can be minimal or postponed.

---

## 13. `backups/`, `migrations/`, `exports/`, `trash/`

These folders are planned for later.

### `backups/`

Snapshots before migrations or major operations.

### `migrations/`

Scripts and reports for format changes.

### `exports/`

Exported data, including possible ZoomAlbum source packages.

### `trash/`

Soft-deleted items.

---

## 14. General rules

1. Raw input must be preserved.
2. Entries should be stable folders with stable ids.
3. Tags are stored in one simple catalog.
4. Indexes are derived and rebuildable.
5. Prompts are stored as files and referenced through `PROMPTSET.json`.
6. The agent should prefer `needs_review` over uncertain silent changes.

