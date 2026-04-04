# Architecture — AI Diary (MVP)

## 1. Purpose

This document describes the technical architecture of **AI Diary**, based on the current PRD and the chosen backend direction: **Firebase Data Connect** as the primary cloud database, with Firebase Storage as primary operational asset storage and optional Google Drive integration for user-owned assets.

AI Diary is a personal journaling system that allows users to capture daily life in a lightweight way, starting with text entries and later expanding to voice, links, photos, AI enrichment, and integration with ZoomAlbum.

---

## 2. Architectural goals

The architecture should support:

- very fast MVP development
- clean, extensible domain model
- Android-first implementation
- simple web access to the same data
- offline-first UX with cloud sync
- gradual introduction of AI processing
- future export of diary content into ZoomAlbum

Core principle:

> **Diary stores events and meaning.  
> ZoomAlbum stores visual composition and navigation.**

---

## 3. High-level system overview

The system consists of:

1. Android client
2. Web client (future)
3. Firebase Authentication
4. Firebase Data Connect
5. Firebase Storage (primary asset storage, future)
6. Optional Google Drive integration (user-owned assets, future)
7. Background processing / AI pipeline (future)

---

## 4. Technology stack

### Client
- Kotlin
- Jetpack Compose
- MVI (StateFlow + Channel for side effects)
- Clean Architecture (presentation / domain / data)
- Hilt (DI)
- Room (local database, offline-first)
- Coroutines

### Backend / cloud
- Firebase Authentication (Google Sign-In)
- Firebase Data Connect (PostgreSQL)
- Firebase Storage (future)
- Cloud Functions (future)

---

## 5. Architectural principles

- Clean layering (presentation / domain / data)
- Domain independent from Android and Firebase (pure Kotlin)
- Repository abstraction (interface in domain, implementation in data)
- Room as single source of truth; Firebase as sync target
- AI as asynchronous enhancement (future)
- Storage abstraction for assets (future)

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

Firebase Data Connect is used for structured relational data:

- Entry
- Asset metadata (future)
- EntryAsset (future)
- Tags / People / Places (future)
- AI analysis (future)

---

## 8. Data model

### Entry (MVP)

| Field | Type | Notes |
|-------|------|-------|
| id | String (UUID) | Generated client-side |
| title | String | Optional, can be blank |
| body | String | Main content (maps to rawText in PRD) |
| createdAt | Instant / Long | When the record was created |
| updatedAt | Instant / Long | Last modification time |
| entryDate | LocalDate | What date this entry is about (may differ from createdAt) |
| source | enum | TEXT (MVP), VOICE / IMPORT (future) |
| isSynced | Boolean | Local-only flag for offline sync |

The MVP model is a simplified subset of the PRD's full Entry spec. Fields like `cleanedText`, `eventDateTime`, and `status` will be added when the AI pipeline is introduced.

### Entry (remote — Data Connect)

Same fields as above plus `uid` (Firebase Auth user ID) for row-level security. `isSynced` is local-only and not stored remotely.

### Asset (future)
- id, ownerUserId, type, storageType, storagePath, url, previewUrl, metadataJson

### EntryAsset (future)
- entryId, assetId, role

---

## 9. Asset Storage Strategy

### 9.1 Principle

Structured data lives in Data Connect.  
Heavy files live in storage systems.

### 9.2 Storage abstraction

Asset does not store the file — it stores a reference.

Supported storage types (future):
- firebase_storage
- google_drive_user
- external_url

### 9.3 Primary storage (future)

Firebase Storage for: uploads, previews, thumbnails, voice notes.

### 9.4 Google Drive usage (future)

Optional: backups, exports, long-term storage, user-owned originals.

---

## 10. Auth and security

- All data is user-scoped
- Firebase Auth (Google Sign-In)
- No cross-user access
- Data Connect queries filtered by `uid`

---

## 11. Android data strategy

### MVP: Offline-first with Room

- **Room is the single source of truth.** UI observes Room via Flow.
- **Write path:** Insert into Room with `isSynced=false` (instant UI update) → push to Data Connect in background → mark synced on success.
- **Read/sync path:** On app start + pull-to-refresh: fetch remote entries → upsert into Room → push unsynced local entries.
- **Conflict resolution:** Last-write-wins by `updatedAt`. MVP is create-only, so real conflicts are not expected.

### Future enhancements
- Background sync via WorkManager
- Realtime subscriptions from Data Connect
- Retry with exponential backoff
- Deletion sync
- Multi-device conflict merge

---

## 12. Web client (future)

Thin client:
- list entries
- open entry
- basic editing

Out of scope for MVP.

---

## 13. Data operations (MVP)

Mutations:
- createEntry (local + remote)
- syncEntries (bidirectional)

Queries:
- listEntries (from Room, sorted by entryDate DESC)
- getEntry (from Room by id)
- listEntriesByUser (remote, for sync)

Future:
- updateEntry
- deleteEntry

---

## 14. Processing pipeline (future)

- transcription
- cleaning (rawText → cleanedText)
- summarization
- tagging
- album preparation

---

## 15. Development phases

Phase 0 (done):
- Project skeleton
- Compose + Hilt + Room + MVI setup
- Domain layer, data layer, UI screens

Phase 1 (current):
- Firebase project setup
- Auth (Google Sign-In)
- Data Connect schema + sync

Phase 2:
- Entry model enrichment (entryDate, source)
- Assets + media attachments

Phase 3:
- AI pipeline

Phase 4:
- ZoomAlbum integration

---

## 16. MVP scope

- text entry only
- offline-first with Room + Firebase Data Connect sync
- Android UI (Compose)
- Google Sign-In

---

## 17. Summary

AI Diary uses:

- Room → offline-first local database (single source of truth)
- Firebase Data Connect → cloud sync and relational storage
- Firebase Storage → operational assets (future)
- Google Drive → optional user-owned archive (future)

This provides fast MVP development with a scalable long-term model.
