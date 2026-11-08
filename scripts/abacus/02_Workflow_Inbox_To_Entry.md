# Agent Workflow — Inbox to Entry

## 1. Workflow goal

Convert raw files from the AI Diary inbox into one or more structured diary entries.

This workflow supports two types of input:

1. completely unstructured files from `inbox/drop/`;
2. structured inbox items from `inbox/new/`.

The workflow must preserve original raw material and create traceable links between raw inputs and generated entries.

---

## 2. Input locations

### 2.1 Raw drop zone

```text
inbox/drop/
  text/
  media/
  mixed/
```

Files may be plain and unstructured.

Examples:

```text
inbox/drop/text/2026-04-25-walk-with-lis.md
inbox/drop/media/IMG_1234.jpg
inbox/drop/mixed/trip-note.md
inbox/drop/mixed/photo1.jpg
```

No manifest is required.

---

### 2.2 Structured inbox items

```text
inbox/new/
  2026-04-25T12-34-18Z__telegram__msg_01HWXYZ/
    MESSAGE.json
    raw_text.md
    attachments/
```

Structured inbox items may already contain metadata.

---

## 3. Output locations

### 3.1 Entry

```text
entries/YYYY/MM/YYYY-MM-DD__entry_<id>/
  ENTRY.json
  entry.md
  revisions/
    000_raw/
      revision.json
      text.md
  links/
    source_raw_inputs.json
  ai/
```

### 3.2 Processed raw archive

```text
inbox/_processed_raw/YYYY/MM/raw_batch_<date>_<number>/
  original_files/
  PROCESSING_RESULT.json
```

### 3.3 Assets

If media files are promoted to assets:

```text
assets/by_id/asset_<id>/
  ASSET.json
  original.<ext>
  metadata.json
```

---

## 4. Main principles

### 4.1 Do not delete raw files

After processing, raw files must remain available.

They may be moved from `inbox/drop/` to `inbox/_processed_raw/`, but they must not be deleted.

---

### 4.2 Do not invent facts

The agent may infer dates and topics, but uncertainty must be marked.

Use:

```text
inferred
unknown
needs_review
user_confirmed
```

---

### 4.3 One raw input may create multiple entries

If one file contains several clearly separate diary moments, the agent may propose multiple entries.

If separation is uncertain, create one entry and mark it as `needs_review`.

---

### 4.4 Multiple raw files may create one entry

If several files clearly belong together, the agent may group them into one raw batch and create one entry.

Examples:

- a Markdown note plus several photos;
- a text note and an audio file from the same time;
- a JSON export plus attached media.

---

## 5. Step-by-step workflow

### Step 1 — Select input

Inspect:

```text
inbox/drop/
inbox/new/
```

Choose one small batch for manual debugging.

Prefer one of:

- one text file;
- one Markdown file;
- one folder containing text + photos;
- one structured inbox item.

Do not process the entire inbox unless explicitly requested.

---

### Step 2 — Move or mark item as processing

For structured inbox items, move the item from:

```text
inbox/new/
```

to:

```text
inbox/processing/
```

For raw drop files, either:

1. move selected files to a temporary processing folder; or
2. leave them in place and record selected file paths in the processing report.

For early manual debugging, option 2 is acceptable.

---

### Step 3 — Read available information

For each selected file, collect:

- file path;
- file name;
- file extension;
- created time if available;
- modified time if available;
- EXIF datetime if media;
- text content if readable;
- existing structured metadata if available.

---

### Step 4 — Decide whether this can become an entry

The agent should classify the input as one of:

```text
create_entry
create_multiple_entries
create_asset_only
needs_review
unsupported
```

Examples:

- diary-like text → `create_entry`;
- long text with clearly separate dates → `create_multiple_entries`;
- photo without text but with useful EXIF → possibly `create_asset_only` or `needs_review`;
- unreadable file → `unsupported`.

---

### Step 5 — Infer entry date and title

Infer:

- `entryDate`;
- optional `startDateTime`;
- optional `endDateTime`;
- title.

Priority for date inference:

1. explicit date in text;
2. explicit date in file name;
3. EXIF datetime;
4. file creation time;
5. file modification time;
6. unknown.

Each date must have confidence.

Example:

```json
"time": {
  "entryDate": "2026-04-25",
  "startDateTime": "2026-04-25T10:30:00+02:00",
  "endDateTime": null,
  "confidence": "inferred"
}
```

If date is unclear, use the best available date and mark the entry as `needs_review`.

---

### Step 6 — Create entry folder

Create:

```text
entries/YYYY/MM/YYYY-MM-DD__entry_<id>/
```

Use a stable generated id.

Example:

```text
entries/2026/04/2026-04-25__entry_01HWABC/
```

---

### Step 7 — Create raw revision

Create:

```text
revisions/000_raw/
  revision.json
  text.md
```

`text.md` should contain the raw or lightly extracted text.

If the source is a photo or media-only input, `text.md` may contain a short note:

```markdown
# Raw source

This entry was created from media-only input.

Original files are preserved in the processed raw archive.
```

Example `revision.json`:

```json
{
  "formatVersion": "v0.1.0",
  "id": "rev_000_raw",
  "entryId": "entry_01HWABC",
  "revisionNumber": 0,
  "type": "raw",
  "createdAt": "2026-04-25T13:00:00Z",
  "createdBy": {
    "type": "agent",
    "workflow": "inbox_to_entry"
  },
  "textPath": "text.md"
}
```

---

### Step 8 — Create current entry text

Create:

```text
entry.md
```

This should be readable diary text.

For the first prototype, avoid heavy rewriting.

The agent may:

- clean obvious transcription errors;
- split paragraphs;
- keep original meaning;
- avoid adding details not present in the input.

---

### Step 9 — Create `ENTRY.json`

Example:

```json
{
  "formatVersion": "v0.1.0",
  "schema": "entry",
  "id": "entry_01HWABC",
  "title": "Walk with Lis",
  "createdAt": "2026-04-25T13:00:00Z",
  "updatedAt": "2026-04-25T13:00:00Z",
  "time": {
    "entryDate": "2026-04-25",
    "startDateTime": null,
    "endDateTime": null,
    "confidence": "inferred"
  },
  "status": "processed",
  "currentRevisionId": "rev_000_raw",
  "rawRevisionId": "rev_000_raw",
  "tags": [],
  "source": {
    "rawInputRefs": []
  },
  "ai": {
    "createdByWorkflow": "inbox_to_entry",
    "needsReview": false
  }
}
```

If uncertain:

```json
"status": "needs_review",
"ai": {
  "createdByWorkflow": "inbox_to_entry",
  "needsReview": true,
  "reviewReason": "Entry date inferred only from file modification time."
}
```

---

### Step 10 — Preserve raw files

Move or copy original files to:

```text
inbox/_processed_raw/YYYY/MM/raw_batch_<date>_<number>/original_files/
```

Create:

```text
PROCESSING_RESULT.json
```

Example:

```json
{
  "formatVersion": "v0.1.0",
  "rawInputId": "raw_2026-04-25_001",
  "processedAt": "2026-04-25T13:10:00Z",
  "sourceFiles": [
    "original_files/2026-04-25-walk-with-lis.md"
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

### Step 11 — Link entry to raw source

Create:

```text
links/source_raw_inputs.json
```

Example:

```json
{
  "formatVersion": "v0.1.0",
  "rawSources": [
    {
      "rawInputId": "raw_2026-04-25_001",
      "path": "inbox/_processed_raw/2026/04/raw_batch_2026-04-25_001/PROCESSING_RESULT.json"
    }
  ]
}
```

Also update `ENTRY.json`:

```json
"source": {
  "rawInputRefs": [
    "inbox/_processed_raw/2026/04/raw_batch_2026-04-25_001/PROCESSING_RESULT.json"
  ]
}
```

---

### Step 12 — Handle media

If media should be linked as an asset:

1. create an asset id;
2. copy or move the media file to `assets/by_id/asset_<id>/`;
3. create `ASSET.json`;
4. reference the asset from `ENTRY.json`.

If media is not yet promoted to an asset, it can remain only in processed raw archive.

For the first prototype, it is acceptable to preserve media only in `_processed_raw/`.

---

### Step 13 — Update simple index if available

If `indexes/entries_by_date.jsonl` exists, append or rebuild a line:

```json
{"date":"2026-04-25","entryId":"entry_01HWABC","path":"entries/2026/04/2026-04-25__entry_01HWABC/ENTRY.json","title":"Walk with Lis"}
```

Indexes are derived data. If uncertain, skip index update and mention it in the report.

---

## 6. Error handling

### 6.1 Unsupported file

Move or record the item under:

```text
inbox/failed/
```

Create a short error report:

```json
{
  "status": "failed",
  "reason": "Unsupported file format",
  "sourceFile": "inbox/drop/media/file.xyz"
}
```

---

### 6.2 Unclear content

Move or record the item under:

```text
inbox/needs_review/
```

Use `needs_review` when:

- there is no reliable date;
- the text is not clearly diary content;
- grouping is uncertain;
- the agent cannot decide whether to create one or multiple entries.

---

## 7. Manual debugging mode

When manually debugging this workflow, process only one small input batch at a time.

For each run, report:

1. files inspected;
2. date/title inferred;
3. entry folder created;
4. raw archive location;
5. uncertain decisions;
6. files changed.

Do not process hidden or unrelated files.

---

## 8. Success criteria

The workflow succeeds if:

- raw input is preserved;
- at least one valid entry is created when appropriate;
- the entry has `ENTRY.json`;
- the entry has readable `entry.md`;
- the entry links back to raw source;
- uncertain cases are marked for review;
- no user-edited data is overwritten.

---

## 9. Minimal first test

Input:

```text
inbox/drop/text/2026-04-25-walk-with-lis.md
```

Expected output:

```text
entries/2026/04/2026-04-25__entry_<id>/
  ENTRY.json
  entry.md
  revisions/000_raw/text.md
  links/source_raw_inputs.json

inbox/_processed_raw/2026/04/raw_batch_2026-04-25_001/
  original_files/2026-04-25-walk-with-lis.md
  PROCESSING_RESULT.json
```

No tags are required in this workflow. Tags may be added by the separate Tag Enrichment workflow.


