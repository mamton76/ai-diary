# Data Model — AI Diary

## Core Principle

> **Entry is the current product object.
> EntryRevision is the canonical historical truth.**

- The user sees and interacts with Entry
- The system preserves real historical content in EntryRevision
- Current state is denormalized back onto Entry for performance and simpler UI

Room v2 has 17 tables. Firebase Data Connect mirrors core tables for cloud sync.

---

## 1. Entry

Main product object shown in lists and screens. Stores the current snapshot.

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Generated client-side |
| title | String | Optional, can be blank |
| body | String | Main text content |
| entryDateStart | LocalDate | Start of calendar interval |
| entryDateEnd | LocalDate | End of calendar interval (= start for single-day) |
| eventStartAt | Instant? | Precise event time, if known |
| eventEndAt | Instant? | Precise event end, if known |
| originType | enum | USER_CREATED, IMPORTED, AI_SYNTHETIC |
| source | enum | TEXT, VOICE, IMPORT |
| status | enum | ACTIVE, ARCHIVED, MERGED, DELETED |
| currentRevisionId | String? | Pointer to latest EntryRevision |
| createdAt | Instant | When the record was created |
| updatedAt | Instant | Last modification time |
| isSynced | Boolean | Local-only sync flag |

Validation: `entryDateStart <= entryDateEnd` enforced in domain model constructor.

Entry can be user-created, imported, or AI-synthetic. Synthetic entries are not a separate table — they are normal Entry records with `originType = AI_SYNTHETIC`. This ensures synthetic objects appear in the same lists, are filterable, have their own revisions, and behave as first-class product objects.

---

## 2. EntryRevision

Stores canonical historical content. Every meaningful content change creates a new revision with a monotonic `revisionNumber` per entry.

- `createEntry` creates Entry + initial EntryRevision atomically
- `updateEntry` creates a new revision and updates the Entry's denormalized fields

EntryRevision is the source of truth for: text/title, date interval, event timestamps, revision metadata, historical tag and asset relations, provenance/derivation.

---

## 3. Date Handling

Two levels of date:

- **entryDateStart / entryDateEnd** — inclusive calendar interval where the entry belongs. Both required. For single-day entries: `entryDateStart = entryDateEnd`.
- **eventStartAt / eventEndAt** — precise event timestamps, if known. Optional.

Canonical dates live in EntryRevision. Current dates are denormalized into Entry.

---

## 4. Tags

Tag identity is separate from display text.

### Tag

| Field | Notes |
|-------|-------|
| id | Identity |
| userId | Owner |
| type | Optional: topic, mood, activity, person_like, place_like |
| source | How the tag was created |
| mergedIntoTagId | For tag merging |
| createdAt / updatedAt | Timestamps |

A tag may be a generic user tag without a type.

### TagLabel

| Field | Notes |
|-------|-------|
| tagId | FK to Tag |
| text | Display text |
| normalizedText | For search/matching |
| isPrimary | One primary label per tag |
| locale | Language |
| source | How the label was created |
| createdAt / updatedAt | Timestamps |

Used for: primary display label, synonyms, alternative spellings, normalization, merge/search/alias handling.

Rule: each Tag must have exactly one primary TagLabel (enforced at application level).

---

## 5. Tag Relations

Two levels, mirroring the Entry/EntryRevision split:

- **EntryRevisionTag** — canonical historical relation between a revision and a tag
- **EntryTag** — current denormalized relation between an entry and a tag

---

## 6. Assets

Represent external content attached to an entry: photo, video, audio, link, file.

### Asset

| Field | Notes |
|-------|-------|
| id | Identity |
| userId | Owner |
| type | photo, video, audio, link, file |
| storageUrl | Reference to stored file |
| mimeType | Content type |
| originalFilename | Original name |
| sizeBytes | File size |
| createdAt / updatedAt | Timestamps |

Asset does not store the file — it stores a reference. Supported storage types (future): firebase_storage, google_drive_user, external_url.

### Asset Relations

Two levels:

- **EntryRevisionAsset** — canonical historical relation to a revision
- **EntryAsset** — current denormalized relation to an entry

---

## 7. Provenance / Derivation

### EntryRevisionSourceLink

Records what a revision was derived from. Especially important for synthetic entries and AI-generated revisions.

A revision may be derived from: other EntryRevisions, AI results, assets, tags, synthetic entries.

Fields include a `role` (primary_source, context, supporting_evidence) to describe the relationship.

This is a provenance layer — it answers: what evidence was used, what this synthetic object was built from, which earlier records contributed.

---

## 8. AI Layer

In Room locally. Data Connect deployment deferred to Phase 5.

### AIRequest

What was sent to the model: request type, model name, prompt version, input payload, context snapshot used, timestamps.

### AIResult

What came back: request reference, output payload, status, timestamps.

### AIFeedback

User feedback on a specific AIResult (not on the entry in general).

---

## 9. User AI Memory

### UserPreferences

Explicit user-configured settings: summary style, AI aggressiveness, whether AI suggestions are shown.

### UserAIContext

Current accumulated AI memory/profile of the user. Long-lived, built over time. May include: learned stylistic preferences, recurring entities, preferred cleanup behavior, patterns in accepted/rejected suggestions, rendered summary for LLM use, structured signals.

### UserAIContextVersion

History of UserAIContext over time. The evolution of the user AI profile matters independently from individual AI calls.

### AIContextSnapshot

FK to UserAIContextVersion (not a full blob copy). Records the exact AI context used in one specific AI request.

Distinction:
- UserAIContext = current long-lived accumulated profile
- UserAIContextVersion = history of that profile
- AIContextSnapshot = exact snapshot used in one specific AI call

---

## 10. Repositories

- **EntryRepository** — CRUD with revision tracking, sync
- **TagRepository** — create tag with label, search by normalized text, add/remove from entries
- **AssetRepository** — create assets, link/unlink from entries

---

## 11. Sync

- `isSynced: Boolean` — `false` means pending sync, `true` means synced
- Remote Entry has the same fields plus `uid` (Firebase Auth user ID) for row-level security
- `isSynced` is local-only, not stored remotely
- Core tables deployed to Data Connect; AI layer tables deferred to Phase 5
- Will be expanded when multi-device sync or retry logic is added

---

## 12. Structural Principles

1. **Entry and EntryRevision must remain distinct** — Entry = current product object, EntryRevision = canonical history
2. **History belongs on revision level** — text, dates, tags, assets, provenance
3. **Current state may be denormalized onto Entry** — text, dates, tags, assets
4. **Synthetic entries are first-class entries** — not hidden artifacts
5. **AIRequest and AIResult are separate** — request = what was sent, result = what came back
6. **User AI memory is separate from settings** — UserPreferences != UserAIContext
7. **Tag labels/synonyms are modeled explicitly** — not collapsed into a single name field