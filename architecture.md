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
  domain/     — model, repository interfaces, use cases
  data/       — local (Room), remote (Data Connect), mapper, repository impl
  feature/    — entrylist, entrydetail, auth (each: Contract, ViewModel, Screen)
```

---

## 7. Backend architecture

Firebase Data Connect stores structured relational data in the cloud:

- Entry (synced from local Room)
- Asset metadata (future)
- EntryAsset (future)
- Tags / People / Places (future)
- AI analysis results (future)

The client never reads directly from Data Connect for UI rendering. Data Connect is a sync target — data flows through Room.

---

## 8. Data model

### Entry (MVP)

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Generated client-side |
| title | String | Optional, can be blank |
| body | String | Main text content |
| entryDate | LocalDate | What date this entry is about |
| source | enum | TEXT (MVP), VOICE / IMPORT (future) |
| createdAt | Instant / Long | When the record was created |
| updatedAt | Instant / Long | Last modification time |
| isSynced | Boolean | Local-only sync flag |

### Sync state

MVP uses a simple `isSynced: Boolean` flag. The conceptual direction for future phases is a richer sync state:

- `LOCAL_ONLY` — created locally, not yet synced
- `SYNCING` — sync in progress
- `SYNCED` — successfully synced to cloud
- `ERROR` — sync failed, will retry

For MVP, `isSynced = false` covers LOCAL_ONLY and ERROR; `isSynced = true` covers SYNCED. This is intentionally simple and will be expanded when multi-device sync or retry logic is added.

### Entry (remote — Data Connect)

Same fields as the local entry plus `uid` (Firebase Auth user ID) for row-level security. `isSynced` is local-only and not stored remotely.

### Entry (future enrichment)

Fields to be added when the AI pipeline is introduced:
- cleanedText, eventDateTime, status (RAW / PROCESSED)

### Asset (future)
- id, ownerUserId, type, storageType, storagePath, url, previewUrl, metadataJson

### EntryAsset (future)
- entryId, assetId, role

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

## 12. Data operations (MVP)

Mutations:
- createEntry (write to Room, push to Data Connect in background)
- syncEntries (bidirectional: pull remote → upsert local, push unsynced → remote)

Queries:
- listEntries (from Room, sorted by entryDate DESC)
- getEntry (from Room by id)
- listEntriesByUser (from Data Connect, for sync)

Future:
- updateEntry
- deleteEntry

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
- Entry model with entryDate + source fields
- Firebase dependencies added (Auth, Data Connect, Storage)
- Firebase project connected (google-services.json)

Phase 1 — Local diary CRUD (done):
- Create text entries
- View entry list sorted by date
- View entry detail
- Local persistence with Room
- Loading/error/empty states

Phase 2 — Auth + cloud sync (current):
- Firebase Auth (Google Sign-In)
- Auth screen and navigation gating
- Data Connect schema, queries, mutations
- Background sync logic in repository
- EntryRemoteDataSource

Phase 3 — Edit, delete, polish:
- Edit existing entries
- Delete entries (local + remote)
- Basic search/filter
- Material3 styling refinements

Phase 4 — Media and assets:
- Asset model and Firebase Storage integration
- Photo/voice attachments on entries
- EntryAsset relation

Phase 5 — AI enrichment:
- AI pipeline (cleaning, summarization, tagging)
- cleanedText, status fields on Entry

Phase 6 — ZoomAlboom integration:
- Spatial positioning model
- Infinite canvas view
- Frame/card UI for entries
- Animated transitions

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
