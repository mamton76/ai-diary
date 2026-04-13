# Data Model — AI Diary

## Core Principle

> **Entry is the current product object.
> EntryRevision is the canonical historical truth.**

- The user sees and interacts with Entry
- The system preserves real historical content in EntryRevision
- Current state is denormalized back onto Entry for performance and simpler UI

Room v2 has 17+ tables. Firebase Data Connect mirrors core tables for cloud sync.

---

## Status Summary

Each status field lives on the object it describes. They do not overlap.

| Object | Field | Meaning | Values |
|--------|-------|---------|--------|
| Entry | status | Lifecycle of the entry as a product object | DRAFT, ACTIVE, ARCHIVED, DELETED |
| EntryRevision | aiStatus | Technical processing status of AI work on this revision | NOT_REQUESTED, QUEUED, PROCESSING, SUCCEEDED, FAILED, STALE |
| AIResult | aiReviewStatus | User-facing outcome of reviewing the AI output | NOT_NEEDED, PENDING_REVIEW, ACCEPTED, REJECTED, PARTIALLY_ACCEPTED |
| Tag | state | Lifecycle and visibility state of the tag | ACTIVE, HIDDEN, BLOCKED, CANDIDATE, MERGED |

Why this matters:
- `Entry.status = ACTIVE` says nothing about whether AI has processed it.
- `EntryRevision.aiStatus = SUCCEEDED` means AI finished — not that the user accepted the output.
- `AIResult.aiReviewStatus = ACCEPTED` means the user approved this specific AI result.

These three statuses are intentionally separate. Do not collapse them.

---

## 1. Entry

Main product object shown in lists and screens. Stores the current denormalized snapshot.

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Generated client-side |
| userId | String | Owner (Firebase Auth UID). Required for all queries and Data Connect row-level security |
| title | String | Optional, can be blank |
| body | String | Main text content |
| entryDateStart | LocalDate | Start of calendar interval |
| entryDateEnd | LocalDate | End of calendar interval (= start for single-day) |
| eventStartAt | Instant? | Precise event time, if known |
| eventEndAt | Instant? | Precise event end, if known |
| originType | enum | USER_CREATED, IMPORTED, AI_SYNTHETIC |
| source | enum | TEXT, VOICE, IMPORT |
| status | enum | DRAFT, ACTIVE, ARCHIVED, DELETED |
| currentRevisionId | String? | Pointer to latest EntryRevision |
| createdAt | Instant | When the record was created |
| updatedAt | Instant | Last modification time |
| isSynced | Boolean | Local-only sync flag |

Validation: `entryDateStart <= entryDateEnd` enforced in domain model constructor.

### Entry.status

`status` represents the lifecycle of the entry as a product object:

- **DRAFT** — entry is being composed, not yet finalized
- **ACTIVE** — entry is live and visible in normal lists
- **ARCHIVED** — entry is hidden from default views but preserved
- **DELETED** — soft-deleted, excluded from queries, eligible for permanent removal

This field is about the entry's lifecycle. It has nothing to do with AI processing or review outcomes.

Entry merging (consolidating two entries into one) is handled by setting the merged-away entry to `status = DELETED` and recording the merge relationship via EntryRevisionSourceLink on the target entry's new revision.

### Synthetic entries

Synthetic entries are not a separate table. They are normal Entry records with `originType = AI_SYNTHETIC`. This ensures they appear in the same lists, are filterable, have their own revisions, and behave as first-class product objects.

---

## 2. EntryRevision

Stores canonical historical content. Every meaningful content change creates a new revision with a monotonic `revisionNumber` per entry.

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Identity |
| entryId | String | FK to Entry |
| userId | String | Owner. Denormalized from Entry for direct queries and Data Connect security |
| revisionNumber | Int | Monotonic per entry, starts at 1 |
| title | String | Canonical title at this revision |
| body | String | Canonical body at this revision |
| entryDateStart | LocalDate | Canonical date interval start |
| entryDateEnd | LocalDate | Canonical date interval end |
| eventStartAt | Instant? | Canonical event time |
| eventEndAt | Instant? | Canonical event end |
| aiStatus | enum | NOT_REQUESTED, QUEUED, PROCESSING, SUCCEEDED, FAILED, STALE |
| createdAt | Instant | When this revision was created |

Operations:
- `createEntry` creates Entry + initial EntryRevision atomically
- `updateEntry` creates a new revision and updates the Entry's denormalized fields

EntryRevision is the source of truth for: text/title, date interval, event timestamps, revision metadata, historical tag and asset relations, provenance/derivation.

### EntryRevision.aiStatus

`aiStatus` tracks the technical processing status of AI work on this specific revision:

- **NOT_REQUESTED** — no AI processing has been requested for this revision
- **QUEUED** — AI processing is scheduled but not yet started
- **PROCESSING** — AI is actively working on this revision
- **SUCCEEDED** — AI processing completed successfully (does **not** mean the user accepted the output)
- **FAILED** — AI processing encountered an error
- **STALE** — AI processing completed previously, but the source content has since changed, so the AI output no longer reflects the current input

`SUCCEEDED` is a technical status. Whether the user accepts, rejects, or partially accepts the AI output is tracked separately on `AIResult.aiReviewStatus`.

`STALE` is set when the underlying content changes after AI processing completed — for example, the user edits text that AI already processed. This lets the system know that re-processing may be warranted without discarding the previous AI results.

---

## 3. Date Handling

Two levels of date:

- **entryDateStart / entryDateEnd** — inclusive calendar interval where the entry belongs. Both required. For single-day entries: `entryDateStart = entryDateEnd`.
- **eventStartAt / eventEndAt** — precise event timestamps, if known. Optional.

Important distinction:
- entryDateStart / entryDateEnd = calendar span where the entry belongs
- eventStartAt / eventEndAt = more precise event time, if known

Canonical dates live in EntryRevision. Current dates are denormalized into Entry.

---

## 4. Tags

Tag identity is separate from display text.

### Tag

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Identity |
| userId | String | Owner |
| type | enum? | Optional: topic, mood, activity, person_like, place_like |
| state | enum | ACTIVE, HIDDEN, BLOCKED, CANDIDATE, MERGED |
| source | enum | How the tag was created (user, ai, system) |
| mergedIntoTagId | String? | FK to target tag after merge |
| createdAt | Instant | Created timestamp |
| updatedAt | Instant | Last modified timestamp |

A tag may be a generic user tag without a type.

### Tag.state

`state` controls the tag's lifecycle and visibility:

- **ACTIVE** — tag is live and visible in normal UI, can be assigned to entries
- **HIDDEN** — tag exists in the system but is excluded from normal UI (e.g., internal system tags, deprecated tags that still have historical references)
- **BLOCKED** — tag must not be suggested or generated again by AI. Supports "do not use this tag" user intent without deleting the tag or its historical associations
- **CANDIDATE** — emerging tag, typically AI-discovered. Not yet promoted to full user-facing status. Useful for evolving clusters that aren't fully defined yet
- **MERGED** — tag has been consolidated into another tag. `mergedIntoTagId` records the target. Historical references remain intact

### Synthetic / candidate tags

Synthetic tags are not the same as synthetic entries. A synthetic tag is a grouping concept that the AI system has identified or proposed, used to connect related entries before a fully formed synthetic entry may exist.

Candidate tags are especially useful for evolving clusters. For example, a tag like "Trip Belgrade -> Eindhoven, June-July 2026" may begin as a `CANDIDATE` grouping tag while the system accumulates entries. As the trip progresses and enough clarity emerges, the system may promote the tag to `ACTIVE` and optionally generate a synthetic entry summarizing the trip.

This matters because:
- grouping tags let the system retrieve all related entries even before synthesis
- candidate tags allow AI to propose structure without committing to it
- the user can promote, block, or ignore candidate tags at any time

### TagLabel

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Identity |
| tagId | String | FK to Tag |
| text | String | Display text |
| normalizedText | String | For search/matching |
| isPrimary | Boolean | One primary label per tag |
| locale | String? | Language |
| source | enum | How the label was created |
| createdAt | Instant | Created timestamp |
| updatedAt | Instant | Last modified timestamp |

Used for: primary display label, synonyms, alternative spellings, normalization, merge/search/alias handling.

Rule: each Tag must have exactly one primary TagLabel (enforced at application level).

---

## 5. Tag Relations

Two levels, mirroring the Entry/EntryRevision split.

### EntryRevisionTag (canonical)

Historical relation between a revision and a tag. Minimal but traceable.

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Identity |
| entryRevisionId | String | FK to EntryRevision |
| tagId | String | FK to Tag |
| source | enum | How this assignment was created (user, ai, system) |
| sourceAiResultId | String? | FK to AIResult, if AI-assigned |
| createdAt | Instant | When assigned |
| removedAt | Instant? | When removed (null = still active on this revision) |

Review/acceptance logic for AI-assigned tags lives in AIResult and AIFeedback, not here. Confidence scores live in the AIResult payload. This keeps the join table simple and avoids duplicating review state across multiple tables.

### EntryTag (denormalized)

Current relation between an entry and a tag. Reflects the latest revision's tag set.

| Field | Type | Notes |
|-------|------|-------|
| entryId | String | FK to Entry |
| tagId | String | FK to Tag |

---

## 6. Assets

Represent external content attached to an entry: photo, video, audio, link, file.

### Asset

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Identity |
| userId | String | Owner |
| type | enum | photo, video, audio, link, file |
| storageUrl | String | Reference to stored file |
| mimeType | String? | Content type |
| originalFilename | String? | Original name |
| sizeBytes | Long? | File size |
| createdAt | Instant | Created timestamp |
| updatedAt | Instant | Last modified timestamp |

Asset does not store the file — it stores a reference. Supported storage types (future): firebase_storage, google_drive_user, external_url.

### Asset Relations

Two levels:

- **EntryRevisionAsset** — canonical historical relation to a revision
- **EntryAsset** — current denormalized relation to an entry

---

## 7. Provenance / Derivation

### EntryRevisionSourceLink

Records what a revision was derived from. This is the provenance layer — it makes derived content explainable and traceable.

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Identity |
| entryRevisionId | String | FK to the derived EntryRevision |
| sourceType | enum | What kind of source: ENTRY_REVISION, AI_RESULT, ASSET, TAG |
| sourceId | String | ID of the source object |
| sourceRole | enum | INPUT, EVIDENCE, CONTEXT, TRIGGER |
| createdAt | Instant | When recorded |

### sourceRole values

- **INPUT** — source directly used to generate this revision. Example: the original EntryRevision whose text was cleaned by AI, producing this new revision.
- **EVIDENCE** — source that confirms or supports the result. Example: an asset (photo with geolocation) that corroborates the location mentioned in a synthetic entry.
- **CONTEXT** — supporting background context that influenced generation. Example: a UserAIContextVersion that shaped how AI phrased a summary.
- **TRIGGER** — source that initiated the creation of this derived revision. Example: a user action or scheduled job that caused the system to generate a synthetic entry from a cluster of existing entries.

Provenance is a first-class design principle. Any derived content — AI-generated revisions, synthetic entries, merged entries — must record what it was built from and why.

---

## 8. AI Layer

In Room locally. Data Connect deployment deferred to Phase 5.

### AIRequest

What was sent to the model.

| Field | Notes |
|-------|-------|
| id | Identity |
| userId | Owner. Required for querying user's AI requests |
| entryRevisionId | FK to the revision being processed |
| requestType | What kind of AI work (clean, summarize, tag, synthesize) |
| modelName | Which model was used |
| promptVersion | Version of the prompt template |
| inputPayload | Serialized input sent to the model |
| contextSnapshotId | FK to AIContextSnapshot |
| createdAt | When the request was created |

### AIResult

What came back from the model.

| Field | Notes |
|-------|-------|
| id | Identity |
| userId | Owner. Denormalized from AIRequest for direct queries |
| aiRequestId | FK to AIRequest |
| outputPayload | Serialized model output (includes confidence scores, proposed changes, proposed tags, etc.) |
| aiReviewStatus | NOT_NEEDED, PENDING_REVIEW, ACCEPTED, REJECTED, PARTIALLY_ACCEPTED |
| createdAt | When the result was received |

### AIResult.aiReviewStatus

`aiReviewStatus` tracks the user-facing outcome of reviewing a specific AI result:

- **NOT_NEEDED** — result does not require user review (e.g., internal metadata extraction)
- **PENDING_REVIEW** — result is awaiting user review
- **ACCEPTED** — user accepted the AI output in full
- **REJECTED** — user rejected the AI output
- **PARTIALLY_ACCEPTED** — user accepted some parts and rejected or modified others

This is about the user's decision on the AI output. It is separate from `EntryRevision.aiStatus`, which tracks whether the AI processing itself succeeded or failed.

### AIFeedback

Feedback on a specific AIResult. Attached to the AI result, not to the entry in general.

AIFeedback is **not only explicit user-entered feedback**. It also represents implicit review outcomes derived from user actions, even if the user never wrote a comment.

AIFeedback may capture:
- explicit ratings or comments the user provided
- which AI-proposed changes were accepted
- which were rejected
- which parts the user reverted before accepting
- what the user edited or rewrote before finalizing the revision
- whether the result was partially accepted and which portions survived

This dual nature (explicit + implicit) matters because most real-world feedback is behavioral. A user who accepts 3 of 5 proposed tags and edits the AI-cleaned text before saving has given rich feedback without writing a single comment. The system must capture this.

| Field | Notes |
|-------|-------|
| id | Identity |
| userId | Owner. Denormalized from AIResult for direct queries |
| aiResultId | FK to AIResult |
| feedbackType | explicit, implicit |
| payload | Serialized feedback data (structured per feedback type) |
| createdAt | When the feedback was recorded |

---

## 9. User AI Memory

### UserPreferences

Explicit user-configured settings: summary style, AI aggressiveness, whether AI suggestions are shown. These are direct user choices, not learned behavior. Keyed by `userId`.

### UserAIContext

Keyed by `userId`. Current accumulated AI memory/profile of the user. Long-lived, built over time. May include: learned stylistic preferences, recurring entities, preferred cleanup behavior, patterns in accepted/rejected suggestions, rendered summary for LLM use, structured signals.

This is not the same as UserPreferences. UserPreferences are what the user explicitly sets. UserAIContext is what the system learns over time.

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

## 11. Sync and Data Ownership

All user-owned data is scoped by `userId` (Firebase Auth UID). Root entities (Entry, Tag, Asset, AIRequest, UserPreferences, UserAIContext) carry `userId` directly. Child entities that may be queried independently (EntryRevision, AIResult, AIFeedback) denormalize `userId` from their parent. Join tables and pure children (TagLabel, EntryTag, EntryRevisionTag, EntryRevisionSourceLink, etc.) derive userId through their parent FK.

- `isSynced: Boolean` — `false` means pending sync, `true` means synced
- `isSynced` is local-only, not stored remotely
- In Data Connect, `userId` is used for row-level security on all synced tables
- Core tables deployed to Data Connect; AI layer tables deferred to Phase 5
- Will be expanded when multi-device sync or retry logic is added

---

## 12. Entry Workflow

### A. User-created entry

1. User creates an entry.
2. Entry is created with `status = DRAFT` (if composing) or `status = ACTIVE` (if saving immediately).
3. An initial EntryRevision is created atomically with `revisionNumber = 1` and `aiStatus = NOT_REQUESTED`.
4. Entry stores the current denormalized snapshot (title, body, dates).
5. Tags and assets may be linked via EntryRevisionTag / EntryRevisionAsset (canonical) and denormalized into EntryTag / EntryAsset.
6. Later edits create new EntryRevision records. Each new revision increments `revisionNumber`. Entry's denormalized fields are updated to reflect the latest revision.

### B. AI processing flow

1. AI processing is requested for a specific EntryRevision.
2. An AIRequest is created, recording the request type, model, prompt version, input, and context snapshot.
3. `EntryRevision.aiStatus` transitions: `NOT_REQUESTED` -> `QUEUED` -> `PROCESSING`.
4. AI finishes. An AIResult is created with the output payload.
5. `EntryRevision.aiStatus` becomes `SUCCEEDED` (processing completed) or `FAILED` (error).
6. If the result requires user review, `AIResult.aiReviewStatus` is set to `PENDING_REVIEW`. If no review is needed (e.g., internal metadata), it is set to `NOT_NEEDED`.
7. The user reviews the AI output and decides: `ACCEPTED`, `REJECTED`, or `PARTIALLY_ACCEPTED`.
8. If the user accepts or partially accepts, a **new** EntryRevision is created incorporating the accepted changes. Entry's denormalized fields update. EntryRevisionSourceLink records provenance from the original revision and the AIResult.
9. AIFeedback is recorded — both explicit (user comments/ratings) and implicit (which changes survived, what was edited, what was reverted).
10. If the user later edits the text that AI already processed, the original revision's `aiStatus` may transition to `STALE`.

### C. Synthetic entry workflow

1. The system detects a cluster, pattern, or episode candidate across existing entries.
2. Synthetic grouping tags may appear first — for example, a `CANDIDATE` tag like "Trip Belgrade -> Eindhoven, June-July 2026" that groups related entries before full synthesis.
3. When enough clarity exists, AI generates a synthetic entry candidate.
4. A new Entry is created with `originType = AI_SYNTHETIC` and `status = ACTIVE` (or `DRAFT` if pending user review).
5. An initial EntryRevision is created. EntryRevisionSourceLink records provenance: which entries, revisions, tags, or AI results contributed (with appropriate `sourceRole` values).
6. The user may accept the synthetic entry as-is, revise it (creating new revisions), archive it, or delete it. The synthetic entry follows the same lifecycle as any other entry.
7. Later recomputation may create new revisions of the same synthetic entry — for example, when new diary entries are added to the cluster. Each recomputation is a new revision with its own provenance chain.

### D. Revision and provenance

- EntryRevision is the canonical historical layer. It stores the actual content at each point in time.
- Entry is the current snapshot. It is always derivable from the latest revision but stored denormalized for performance.
- Provenance is stored via EntryRevisionSourceLink. Every derived revision records what it was built from, what role each source played, and when.
- Derived content must remain explainable. Given any revision, it should be possible to trace back through its source links to understand how it was produced.

---

## 13. Structural Principles

1. **Entry and EntryRevision must remain distinct** — Entry = current product object, EntryRevision = canonical history
2. **History belongs on revision level** — text, dates, tags, assets, provenance
3. **Current state may be denormalized onto Entry** — text, dates, tags, assets
4. **Synthetic entries are first-class entries** — not hidden artifacts, not a separate table
5. **AIRequest and AIResult are separate** — request = what was sent, result = what came back
6. **User AI memory is separate from settings** — UserPreferences != UserAIContext
7. **Tag labels/synonyms are modeled explicitly** — not collapsed into a single name field
8. **Status fields live where they belong** — entry lifecycle on Entry, AI processing on EntryRevision, review outcome on AIResult, tag lifecycle on Tag
9. **Provenance is a first-class concern** — derived content must be traceable and explainable
10. **Feedback includes implicit signals** — user actions (accept, reject, edit) are feedback, not just explicit ratings
