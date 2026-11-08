# AI Diary Google Drive Workflow — rewritten version

This package contains a cleaner version of the Google Drive inbox-to-entry workflow.

## Files

- `ai_diary_drive_client.py` — low-level Google Drive API wrapper.
- `inbox_to_entry_drive.py` — AI Diary workflow that processes files from `inbox/drop/text` and `inbox/drop/mixed`.

## Install dependencies

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## First run

python input_to_entry_2.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --credentials ~/ai-diary/google_credentials.json \
  --token ~/ai-diary/google_token.json \
  --dry-run

python gcal_to_inbox.py   --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID   --inbox-calendar "Дневничок"   --processed-calendar "Дневничок обработанное"   --credentials google_credentials.json   --token google_token.json   --dry-run

/opt/computersetup/.pyenv/versions/3.11.6/bin/python3 \
  /home/ubuntu/ai-diary/gcal_projection.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --credentials /home/ubuntu/ai-diary/google_credentials.json \
  --token /home/ubuntu/ai-diary/google_token.json \
  --limit 500 \
  --dry-run

```bash
python inbox_to_entry_drive.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --credentials ~/ai-diary/google_credentials.json \
  --token ~/ai-diary/google_token.json \
  --dry-run
```

Then create one entry:

```bash
python inbox_to_entry_drive.py \
  --root-folder-id YOUR_AI_DIARY_ROOT_FOLDER_ID \
  --credentials ~/ai-diary/google_credentials.json \
  --token ~/ai-diary/google_token.json \
  --limit 1
```

## What it processes

Only:

```text
inbox/drop/text
inbox/drop/mixed
```

Supported entry input files:

```text
.txt
.md
.markdown
.json
```

Media-only files are skipped for now.

## What it creates

For an input file such as:

```text
inbox/drop/text/2026-04-25-test.md
```

it creates:

```text
entries/2026/04/2026-04-25__entry_<id>/
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

and moves original raw input to:

```text
inbox/_processed_raw/2026/04/raw_batch_2026-04-25_entry_<id>/
  original_files/
    2026-04-25-test.md
  PROCESSING_RESULT.json
```

