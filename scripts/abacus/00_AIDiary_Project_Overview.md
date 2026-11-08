# AI Diary — Project Overview for File-Based Agent Workflows

## 1. Project purpose

**AI Diary** is a personal diary system where daily memories, notes, media, and reflections are stored as files, primarily in a user-owned storage location such as **Google Drive**.

The system is designed around the idea:

> Capture first. Structure later.

The user should be able to quickly save raw thoughts, text notes, Markdown files, JSON snippets, photos, audio, screenshots, and other media without being forced to fill in structured metadata manually.

AI agents then help transform this raw material into structured diary entries, enrich entries with tags, preserve original raw inputs, and maintain a file-based archive that remains understandable and portable.

---

## 2. Role of the agent

The agent is not the owner of the diary.

The agent is an assistant that helps:

- inspect raw files in the inbox;
- infer dates, topics, and possible diary entry boundaries;
- create structured diary entries from raw material;
- preserve original raw files;
- suggest and apply tags;
- maintain simple indexes if needed;
- explain uncertain decisions instead of silently inventing facts.

The agent must be conservative and transparent.

If the agent is not sure about something, it should mark the result as `needs_review` rather than pretending to know.

---

## 3. Core storage principle

The file system is treated as the source of truth.

Structured information is stored as plain files:

- Markdown for human-readable text;
- JSON for metadata, links, status, and machine-readable structures;
- original media files preserved as-is;
- derived files stored separately.

The storage should remain useful even without a database.

A future application may index these files, display them in a web or mobile UI, and run additional agent workflows.

---

## 4. Main entities

### 4.1 Raw input

A raw input is anything placed into the inbox before it becomes a diary entity.

Examples:

- `.txt` file with a note;
- `.md` file with a diary fragment;
- `.json` file exported from another system;
- photo;
- screenshot;
- audio note;
- mixed folder containing text and media.

Raw input may have no structured metadata.

The agent may use:

- file name;
- file creation date;
- file modification date;
- EXIF metadata;
- text content;
- surrounding files in the same folder.

But the agent must not assume facts that are not supported by the available material.

---

### 4.2 Entry

An entry is a structured diary record.

An entry is stored as a folder containing:

- `ENTRY.json` — canonical metadata;
- `entry.md` — current human-readable text;
- `revisions/` — history of raw, AI-generated, and user-edited versions;
- `links/` — references to raw inputs and related entities;
- optional `assets/` references;
- optional AI proposals and feedback.

---

### 4.3 Asset

An asset is a media file or external file associated with one or more entries.

Examples:

- photo;
- video;
- audio note;
- screenshot;
- PDF;
- imported file.

Assets may be stored globally under `assets/by_id/`, while entries keep references to them.

---

### 4.4 Tag

A tag is the first and currently only catalog entity.

Tags are used for navigation, filtering, grouping, and later album generation.

At this stage there are no separate catalogs for people, places, or sources. These may be represented as tags with a simple `type`.

Examples:

- `person`
- `pet`
- `place`
- `topic`
- `event_cluster`
- `project`
- `activity`
- `mood`
- `system`

---

## 5. Important behavioral rules for the agent

### 5.1 Preserve raw input

Never delete raw input after processing.

After raw files are processed, move or copy them to the processed raw archive and keep a link from the created entry back to the original material.

---

### 5.2 Do not overwrite human work

If an entry or tag was edited by the user, do not overwrite it silently.

Create a new proposal or mark a conflict for review.

---

### 5.3 Prefer explicit uncertainty

Use fields such as:

- `confidence`
- `needs_review`
- `unknown`
- `inferred`
- `user_confirmed`

Do not invent people, dates, locations, or relationships.

---

### 5.4 Keep AI output traceable

Whenever the agent creates or changes structured data, it should record:

- which workflow was used;
- which prompt was used;
- when the operation happened;
- which input files were used;
- which output files were created or changed.

For early manual debugging this can be lightweight, but the trace should exist.

---

### 5.5 Keep the system simple

This is an early file-based prototype.

Avoid overengineering.

Prefer:

- plain folders;
- readable Markdown;
- small JSON manifests;
- clear status files;
- simple append-only revisions.

---

## 6. Initial agent workflows

The first two workflows are:

1. **Inbox to Entry**  
   Convert raw inbox files into structured diary entries.

2. **Tag Enrichment**  
   Suggest and apply tags to existing entries using the tag catalog.

These workflows are described in separate Markdown files.

---

## 7. Long-term direction

The file-based storage may later support:

- web UI;
- Android app;
- Google Drive synchronization;
- local-first mode;
- migration between format versions;
- AI-generated summaries;
- ZoomAlbum export;
- richer catalogs for people, places, events, and relationships.

For now the priority is to make file-based diary capture and agent-assisted structuring reliable, inspectable, and easy to debug manually.

