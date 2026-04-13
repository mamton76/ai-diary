# PRD — AI Diary (MVP)

## 1. Overview

Product name: AI Diary
Type: Android-first, offline-first diary application with cloud sync
Role: Foundational layer for ZoomAlboom

AI Diary is a personal journaling system that allows users to quickly capture their daily experiences as text entries. Entries are stored locally first and synced to the cloud in the background. AI will later structure and enrich this data for transformation into interactive albums.

---

## 2. Product Vision

People want to remember their lives, but:

- writing structured diaries is hard
- media is scattered across apps
- memories are not connected

AI Diary solves this by:

- making capture fast and effortless
- storing entries locally for instant access (offline-first)
- syncing to the cloud for backup and multi-device access
- preparing data for AI enrichment and visual storytelling (ZoomAlboom)

---

## 3. MVP Scope

### Goal
Enable fast daily capture with reliable local storage and basic cloud sync.

### Included

- Create text entry (title + body)
- Automatic timestamps (createdAt, updatedAt)
- Entry date (what day the entry is about — may differ from creation time)
- Entry source tracking (TEXT for MVP; VOICE, IMPORT later)
- Entry list sorted by date
- Entry detail view
- Local persistence (Room — works fully offline)
- Background sync to Firebase Data Connect
- Google Sign-In
- Basic loading/error/empty states

### Not included (future phases)

- Tagging UI (data model ready)
- Media attachment UI (data model + repository ready)
- Album generation
- AI summaries
- Edit/delete entry UI (repository supports it, UI in Phase 3)

---

## 4. Core Concepts

The data model is described in detail in [data-model-proposal.md](data-model-proposal.md). Key entities:

- **Entry** — main diary record (text, dates, status, origin type). Stores current denormalized state.
- **EntryRevision** — canonical historical content. Every meaningful change creates a new revision.
- **Tag / TagLabel** — tags with separate identity and display text (labels, synonyms, normalization).
- **Asset** — external content (photo, video, audio, link, file) attached to entries.
- **AI layer** — AIRequest, AIResult, AIFeedback, UserAIContext (Phase 5).

Core principle: Entry is the current product object; EntryRevision is the canonical historical truth.

---

## 5. User Flow

### Create Entry

1. Open app
2. Tap "+" button
3. Enter title (optional) and body text
4. Save
5. Entry is stored locally and appears in list immediately
6. Sync to cloud happens in background

---

### View Entries

1. Open app
2. See list sorted by entry date
3. Tap entry
4. View detail

---

## 6. Data Strategy

### Offline-first

- Room is the local database and single source of truth for the UI
- All writes go to Room first — the UI updates instantly
- Background sync pushes local entries to Firebase Data Connect
- On app start and pull-to-refresh, remote entries are fetched and merged into Room
- Conflict resolution: last-write-wins by updatedAt (sufficient for MVP)

### Cloud backend

- Firebase Data Connect (PostgreSQL) stores structured data
- Firebase Storage will store media assets (future)
- All data is user-scoped via Firebase Auth UID

---

## 7. AI Role (Post-MVP)

AI will:

- clean text
- extract topics
- detect structure (tasks, events, reflections)

Important:
- original body text is always preserved
- AI output is optional and replaceable

---

## 8. Android Architecture

Stack:

- Kotlin
- Jetpack Compose
- MVI
- Clean Architecture
- StateFlow
- Hilt
- Room (local DB)
- Coroutines

Layers:

- Presentation (Compose + ViewModels)
- Domain (pure Kotlin models, use cases)
- Data (Room, Firebase, repository implementations)

---

## 9. Screens (MVP)

- Entry List
- Entry Detail / Create
- Auth (Google Sign-In)

---

## 10. Non-functional Requirements

- fast input (<1s to start writing)
- works fully offline
- reliable local storage
- simple, clear UX
- scalable data model

---

## 11. Future Extensions

### Phase 3
- Edit/delete entry UI (repository already supports revision-based edits)
- Basic search/filter

### Phase 4
- Media attachment UI (AssetRepository + Firebase Storage integration)

### Phase 5
- AI pipeline: cleaning, summarization, tagging (AI tables ready in Room)
- Synthetic entries (originType = AI_SYNTHETIC)

### Phase 6
- ZoomAlboom integration (spatial canvas, frames, navigation)

---

## 12. Use Cases / Verticals

AI Diary is not a single-purpose journal — it is a personal memory system that works across multiple life contexts through the same capture → structure → explore pipeline.

### 12.1 Life Diary (default)

General-purpose daily journaling. Users capture thoughts, events, links, moods, plans on the go — via voice or text. AI structures entries, extracts topics/people/emotions, finds patterns over time.

This is the "modern LiveJournal without the effort" — you live, AI writes your story.

### 12.2 Baby & Early Years Diary

Parents capture milestones, funny moments, first words, health notes, growth observations — often as quick voice memos while multitasking. AI auto-tags developmental milestones (first steps, first tooth, first day at kindergarten), builds a timeline, connects photos to entries.

High emotional value, natural shareability (with partner, grandparents), built-in time horizon (pregnancy → first 3–5 years).

This vertical has the strongest product-market fit for launch: clear audience, high motivation, willingness to pay, almost no AI competitors in this niche.

### 12.3 Travel Diary

Users capture experiences during a single trip or across multiple trips — places, food, impressions, recommendations, photos, links. AI structures by location/day, extracts places and highlights, builds a trip narrative.

ZoomAlboom integration is most natural here: trips literally map to spatial exploration. Can serve both as personal memory and as shareable travel story.

### Architecture note

These are not separate apps or modules — they are "lenses" on the same engine:

- Same Entry model, same AI pipeline, same storage
- Differences are in:
  - AI prompt templates (what to extract and how to tag)
  - Suggested capture triggers and reminders
  - ZoomAlboom visualization defaults (timeline vs map vs milestone view)
  - Sharing defaults

### Sharing and retention

Pure private diaries suffer from retention drop-off. LiveJournal proved that even minimal audience (friends, family) dramatically improves motivation.

AI Diary should support selective sharing of moments, AI-generated summaries, and ZoomAlboom visual stories — not as a social network, but as a way to share memory artifacts with close people. Sharing is a retention mechanism, not a social feature.

---

## 13. Design Principles

- capture first, structure later
- offline-first — the app must work without internet
- minimal friction
- AI is assistant, not blocker
- user data is always preserved

---

## 14. Success Criteria

- entry created in <10 seconds
- app works fully offline
- reliable local + cloud storage
- clean architecture ready for extension

---

End of document
