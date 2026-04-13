# Architecture — AI Diary

## 1. Purpose

This document describes the technical architecture of **AI Diary**, an Android-first, offline-first diary application with cloud sync via Firebase Data Connect.

AI Diary is the foundational layer for ZoomAlboom. It starts with text entries and will expand to voice, media, AI enrichment, and spatial album integration.

---

## 2. Architectural goals

- Offline-first: the app works fully without internet
- Room as the single source of truth for the client UI
- Clean, extensible domain model
- Android-first implementation
- Cloud sync via Firebase Data Connect (background, non-blocking)
- Gradual introduction of AI processing
- Future export of diary content into ZoomAlboom

Core principle:

> **Diary stores events and meaning.
> ZoomAlboom stores visual composition and navigation.**

---

## 3. High-level system overview

The system consists of:

1. Android client (offline-first)
2. Firebase Authentication (Google Sign-In)
3. Firebase Data Connect (cloud sync for structured data)
4. Firebase Storage (asset storage — dependency added, ready to use)
5. Web client (future)
6. Google Drive integration (future)
7. AI pipeline (future)

---

## 4. Technology stack

### Client
- Kotlin
- Jetpack Compose
- MVI (StateFlow + Channel for side effects)
- Clean Architecture (presentation / domain / data)
- Hilt (DI)
- Room (local database, single source of truth)
- Coroutines

### Backend / cloud
- Firebase Authentication (Google Sign-In)
- Firebase Data Connect (PostgreSQL)
- Firebase Storage (asset uploads)
- Cloud Functions (future)

---

## 5. Architectural principles

- Clean layering (presentation / domain / data)
- Domain independent from Android and Firebase (pure Kotlin)
- Repository abstraction (interface in domain, implementation in data)
- Room is the single source of truth — UI reads only from Room
- Writes happen locally first, sync to cloud in the background
- Firebase Data Connect is the sync target, not the primary data source
- Last-write-wins conflict resolution (sufficient for MVP)
- AI as asynchronous enhancement (future)

---

## 6. Client architecture

### Layers

- **Presentation**: Compose screens + HiltViewModels (MVI pattern)
- **Domain**: pure Kotlin models, repository interfaces, use cases
- **Data**: Room entities, DAO, repository implementation, remote data sources

### Package structure

```
com.mamton.aidiary/
  DiaryApp.kt, MainActivity.kt
  core/       — DI modules, navigation, theme
  domain/     — model (14 models + enums), repository interfaces (Entry, Tag, Asset), use cases
  data/       — local/entity (17 Room entities), local/dao (17 DAOs), remote, mapper, repository impl
  feature/    — entrylist, entrydetail, auth (each: Contract, ViewModel, Screen)
```

---

## 7. Backend architecture

Firebase Data Connect stores structured relational data in the cloud:

- Entry (synced, with entryDateStart/End, originType, status, currentRevisionId)
- EntryRevision, Tag, TagLabel, EntryRevisionTag, EntryTag (deployed)
- Asset, EntryRevisionAsset, EntryAsset, EntryRevisionSourceLink (deployed)
- AI layer tables (AIRequest, AIResult, etc. — in Room locally, Data Connect deferred to Phase 5)

The client never reads directly from Data Connect for UI rendering. Data Connect is a sync target — data flows through Room.

---

## 8. Data model

The full data model is described in [data-model-proposal.md](data-model-proposal.md). Room v2 has 17 tables; Firebase Data Connect mirrors core tables for cloud sync.

> **Entry is the current product object. EntryRevision is the canonical historical truth.**

Key entities: Entry, EntryRevision, Tag/TagLabel, Asset, EntryRevisionSourceLink (provenance), and AI layer tables (AIRequest, AIResult, AIFeedback, UserAIContext). Entry stores current denormalized state; EntryRevision stores canonical history. History, tags, assets, and provenance all live at the revision level.

Repositories: EntryRepository (CRUD + revision tracking + sync), TagRepository, AssetRepository. Sync uses a simple `isSynced` boolean flag; remote entries add `uid` for row-level security.

---

## 9. Asset storage strategy

### Principle

Structured data lives in Data Connect.
Heavy files live in storage systems.

### Storage abstraction

Asset does not store the file — it stores a reference.

Supported storage types (future):
- firebase_storage
- google_drive_user
- external_url

### Firebase Storage

For: uploads, previews, thumbnails, voice notes. Dependency is added to the project; integration code will be built alongside the Asset model in Phase 4.

### Google Drive (future)

Optional: backups, exports, long-term storage, user-owned originals.

---

## 10. Auth and security

- All data is user-scoped
- Firebase Auth (Google Sign-In)
- No cross-user access
- Data Connect queries filtered by `uid`

---

## 11. Offline-first data strategy

### How it works

1. **Room is the single source of truth.** The UI observes Room via Flow. The UI never reads from the network directly.
2. **Writes go to Room first.** When the user creates an entry, it is inserted into Room with `isSynced = false`. The UI sees it instantly.
3. **Sync runs in the background.** After a local write, a background coroutine pushes the entry to Data Connect. On success, the entry is marked `isSynced = true`.
4. **Pull sync on app start and pull-to-refresh.** Remote entries are fetched from Data Connect and upserted into Room. Unsynced local entries are pushed to the cloud.
5. **Conflict resolution: last-write-wins by `updatedAt`.** MVP is create-only, so real conflicts are not expected.

### What MVP sync does NOT include

- Background sync via WorkManager
- Realtime subscriptions
- Retry with exponential backoff
- Deletion sync
- Multi-device conflict merge

These are future enhancements. MVP sync is simple and pragmatic: sync on app start, sync after writes, no retry on failure.

---

## 12. Data operations

Mutations:
- createEntry (write Entry + initial EntryRevision to Room, push to Data Connect in background)
- updateEntry (create new EntryRevision, update Entry denormalized fields, push to Data Connect)
- syncEntries (bidirectional: pull remote → upsert local, push unsynced → remote)
- createTag (create Tag + primary TagLabel)
- addTagToEntry / removeTagFromEntry
- createAsset, addAssetToEntry / removeAssetFromEntry

Queries:
- listEntries (from Room, sorted by entryDateStart DESC, excludes DELETED)
- listEntries by date range, status, originType
- getEntry (from Room by id)
- getRevisions (all revisions for an entry, ordered by revisionNumber)
- searchTags (by normalized text)
- listEntriesByUser (from Data Connect, for sync)

---

## 13. Web client (future)

Thin client:
- list entries
- open entry
- basic editing

Out of scope for MVP.

---

## 14. Processing pipeline (future)

- transcription (voice → text)
- cleaning (body → cleanedText)
- summarization
- tagging
- album preparation (ZoomAlboom export)

---

## 15. Development phases

Phase 0 — Foundation (done):
- Project skeleton: Compose + Hilt + Room + MVI
- Domain layer, data layer, UI screens
- Firebase dependencies added (Auth, Data Connect, Storage)
- Firebase project connected (google-services.json)

Phase 1 — Local diary CRUD (done):
- Create text entries, view list and detail
- Local persistence with Room
- Loading/error/empty states

Phase 2 — Auth + cloud sync (done):
- Firebase Auth (Google Sign-In), auth screen, navigation gating
- Data Connect schema, queries, mutations, EntryRemoteDataSource
- Background sync logic in repository

Phase 2.5 — Data model expansion (done):
- Full data model from `data-model-proposal.md` implemented
- Room v2: 17 tables with indexes and validation
- Entry/EntryRevision split, Tag/TagLabel, Asset, provenance, AI layer
- TagRepository, AssetRepository with full CRUD
- Data Connect schema deployed with all core tables
- Existing remote data migrated (entry_date → entry_date_start/end)

Phase 3 — Edit, delete, polish (next):
- Wire edit/delete to UI (repository already supports it)
- Soft delete via status = DELETED
- Search/filter, Material3 refinements

Phase 4 — Media and assets:
- Firebase Storage integration
- Photo/voice attachments using AssetRepository
- Sync assets to Data Connect

Phase 5 — AI enrichment:
- AI pipeline (cleaning, summarization, tagging)
- Synthetic entries (originType = AI_SYNTHETIC)
- Wire AIRequest/AIResult/AIFeedback + UserAIContext to Data Connect

Phase 6 — ZoomAlboom integration:
- Spatial positioning, infinite canvas, frame UI, animated transitions

---

## 16. MVP scope

- Text entries only
- Offline-first with Room as source of truth
- Background sync to Firebase Data Connect
- Android UI (Jetpack Compose)
- Google Sign-In

---

## 17. Summary

AI Diary is an offline-first Android diary app:

- **Room** → local database, single source of truth for the UI
- **Firebase Data Connect** → cloud sync and backup
- **Firebase Storage** → media assets (Phase 4)
- **ZoomAlboom** → spatial album integration (Phase 6)

Writes happen locally first. Sync runs in the background. The MVP is intentionally simple.
