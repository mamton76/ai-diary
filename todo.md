# Diary App — Next Steps

## Phase 0: Foundation (done)
- [x] Project skeleton: Compose + Hilt + Room + MVI + KSP
- [x] Gradle configuration with version catalog
- [x] Theme, navigation shell, app entry point
- [x] Firebase dependencies (Auth, Data Connect, Storage)
- [x] Firebase project connected (google-services.json)

## Phase 1: Local Diary CRUD (done)
- [x] Entry domain model (id, title, body, entryDate, source, timestamps, isSynced)
- [x] Room database, entity, DAO
- [x] Repository interface (domain) and implementation (data)
- [x] Use cases (GetEntries, GetEntryById, CreateEntry, SyncEntries)
- [x] Entry list screen with MVI (pull-to-refresh, empty state, error state)
- [x] Entry detail/create screen with MVI
- [x] Navigation between screens

## Phase 2: Auth + Cloud Sync
- [x] Create `FirebaseModule.kt` (provides FirebaseAuth)
- [x] Create `AuthViewModel.kt` (Google Sign-In via Credential Manager)
- [x] Create `AuthScreen.kt` (sign-in UI)
- [x] Add Auth route to `Screen.kt` and gate navigation in `DiaryNavHost.kt`
- [x] Define Data Connect schema (`schema.gql` — Entry table with `uid`)
- [x] Define queries (`queries.gql` — ListEntriesByUser, GetEntryById)
- [x] Define mutations (`mutations.gql` — UpsertEntry)
- [x] Run `firebase dataconnect:sdk:generate`
- [x] Create `EntryRemoteDataSource.kt` (wraps generated SDK)
- [x] Wire real sync logic in `EntryRepositoryImpl.kt`
- [ ] Test end-to-end: create locally → sync to Firebase → pull from Firebase
- [ ] Tighten Data Connect security: use `auth.uid` in queries/mutations instead of `$uid` parameter
- [ ] Consider additional sync triggers: app resume (onResume), network reconnect, after edit/delete, periodic WorkManager sync, Firebase Cloud Messaging push notifications for multi-device sync

## Phase 3: Edit, Delete, Polish
- [ ] Edit existing entries
- [ ] Delete entries (local + remote sync)
- [ ] Add `startTime` / `endTime` fields to Entry (optional, for event duration)
- [ ] Time picker UI for startTime/endTime
- [ ] Basic search / filter entries
- [ ] Better date formatting (relative: "Today", "Yesterday")
- [ ] Empty state improvements
- [ ] Loading skeleton / shimmer
- [ ] Material3 styling refinements

## Phase 4: Media and Assets
- [ ] Asset domain model (id, type, storageType, url, metadata)
- [ ] EntryAsset relation model
- [ ] Firebase Storage upload/download integration
- [ ] Photo attachment on entries
- [ ] Voice note attachment on entries
- [ ] Asset previews in entry list and detail

## Phase 5: AI Enrichment
- [ ] Research: text processing libraries (tokenization, cleaning, spell correction) — OpenNLP, LanguageTool, on-device vs server-side LLM
- [ ] AI Agent implementation (see [agent-idea.md](agent-idea.md) — hybrid model: deterministic pipeline + LLM decisions)
- [ ] AI pipeline: text cleaning (body → cleanedText)
- [ ] AI pipeline: summarization
- [ ] AI pipeline: tagging and topic extraction
- [ ] Entry status field (RAW / PROCESSED)
- [ ] Display AI-generated content alongside original
- [ ] Auto-generate text entry from media (media → signals → draft → user confirmation)

## Phase 6: ZoomAlboom Integration
- [ ] Spatial positioning model (x, y, scale on canvas)
- [ ] Infinite canvas view with pinch/zoom
- [ ] Frame/card UI for entries on canvas
- [ ] Animated transitions between entries
- [ ] Multi-module Gradle setup (`:core`, `:feature:diary`, `:feature:canvas`)
