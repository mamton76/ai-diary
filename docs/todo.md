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

## Phase 2: Auth + Cloud Sync (done)
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

## Phase 2.5: Data Model Expansion (done)
- [x] Implement full data model from `data-model-proposal.md`
- [x] Entry updated: `entryDateStart`/`entryDateEnd` date interval, `eventStartAt`/`eventEndAt`, `originType`, `status`, `currentRevisionId`
- [x] EntryRevision table with monotonic `revisionNumber` per entry
- [x] Tag + TagLabel tables (labels support synonyms, normalization, locale)
- [x] Asset table (photo, video, audio, link, file)
- [x] Join tables: EntryRevisionTag, EntryTag, EntryRevisionAsset, EntryAsset
- [x] Provenance: EntryRevisionSourceLink (sourceType + sourceId + role)
- [x] AI layer: AIRequest, AIResult, AIFeedback
- [x] User AI memory: UserPreferences, UserAIContext, UserAIContextVersion, AIContextSnapshot (FK to version, not blob)
- [x] Room v2 with 17 tables, composite indexes, unique constraints
- [x] Validation: `entryDateStart <= entryDateEnd` enforced in domain model
- [x] EntryRevisionMapper, TagMapper, AssetMapper
- [x] TagRepository + TagRepositoryImpl (create tag with label, search, add/remove from entry)
- [x] AssetRepository + AssetRepositoryImpl (create, link/unlink from entry)
- [x] DI wiring for all DAOs and repositories
- [x] EntryRepository updated: `createEntry` creates Entry + initial EntryRevision atomically; `updateEntry` creates new revision
- [x] Data Connect schema deployed with new Entry fields + 9 new table types
- [x] Data Connect SDK regenerated, EntryRemoteDataSource updated for new fields
- [x] Data migration: existing remote entries migrated from `entry_date` → `entry_date_start`/`entry_date_end`

## Phase 2.6: Data Model Refinement (pending)
- [ ] Entry.status: update enum to DRAFT, ACTIVE, ARCHIVED, DELETED (remove MERGED)
- [ ] Add `userId` to Entry, EntryRevision, AIRequest, AIResult, AIFeedback, UserPreferences, UserAIContext
- [ ] Add `EntryRevision.aiStatus` field (NOT_REQUESTED, QUEUED, PROCESSING, SUCCEEDED, FAILED, STALE)
- [ ] Add `AIResult.aiReviewStatus` field (NOT_NEEDED, PENDING_REVIEW, ACCEPTED, REJECTED, PARTIALLY_ACCEPTED)
- [ ] Add `Tag.state` field (ACTIVE, HIDDEN, BLOCKED, CANDIDATE, MERGED)
- [ ] Update EntryRevisionTag: add `source`, `sourceAiResultId?`, `createdAt`, `removedAt?`
- [ ] Update EntryRevisionSourceLink: rename `role` → `sourceRole` (INPUT, EVIDENCE, CONTEXT, TRIGGER)
- [ ] Add `AIFeedback.feedbackType` (explicit, implicit)
- [ ] Update Room schema version, write migration
- [ ] Update Data Connect schema for synced tables
- [ ] Regenerate Data Connect SDK, update EntryRemoteDataSource
- [ ] Update domain models, enums, mappers

## Phase 3: Edit, Delete, Polish
- [ ] Edit existing entries (repository supports it; wire to UI)
- [ ] Delete entries (soft delete via `status = DELETED`, local + remote sync)
- [ ] Entry draft flow (`status = DRAFT` → `ACTIVE` on save)
- [ ] Archive entries (`status = ARCHIVED`, hidden from default list)
- [ ] Time picker UI for eventStartAt/eventEndAt
- [ ] Basic search / filter entries (by status, originType, date range, userId-scoped)
- [ ] Better date formatting (relative: "Today", "Yesterday")
- [ ] Empty state improvements
- [ ] Loading skeleton / shimmer
- [ ] Material3 styling refinements

## Phase 4: Media and Assets
- [ ] Firebase Storage upload/download integration
- [ ] Photo attachment on entries (use AssetRepository)
- [ ] Voice note attachment on entries
- [ ] Asset previews in entry list and detail
- [ ] Sync assets to Data Connect (add queries/mutations for Asset, EntryAsset)

## Phase 5: AI Enrichment
- [ ] Research: text processing libraries (tokenization, cleaning, spell correction) — OpenNLP, LanguageTool, on-device vs server-side LLM
- [ ] AI Agent implementation (see [agent-idea.md](agent-idea.md) — hybrid model: deterministic pipeline + LLM decisions)
- [ ] AI processing flow: AIRequest → EntryRevision.aiStatus transitions → AIResult → user review
- [ ] AI pipeline: text cleaning (body → cleanedText)
- [ ] AI pipeline: summarization
- [ ] AI pipeline: tagging and topic extraction (use TagRepository)
- [ ] Candidate grouping tags (`Tag.state = CANDIDATE`) — AI-discovered clusters before full synthesis
- [ ] Synthetic entries (`originType = AI_SYNTHETIC`) — summaries, inferred episodes, life periods
- [ ] Provenance tracking for all AI-derived content (EntryRevisionSourceLink with sourceRole)
- [ ] User review flow: AIResult.aiReviewStatus (ACCEPTED / REJECTED / PARTIALLY_ACCEPTED → new EntryRevision)
- [ ] AIFeedback capture: explicit ratings + implicit behavioral feedback (which changes survived, what user edited)
- [ ] Display AI-generated content alongside original
- [ ] Auto-generate text entry from media (media → signals → draft → user confirmation)
- [ ] Wire AIRequest/AIResult/AIFeedback tables to Data Connect (add userId scoping)
- [ ] Wire UserAIContext/UserAIContextVersion for accumulated AI memory
- [ ] AIContextSnapshot used to record exact context per AI call

## Phase 6: ZoomAlboom Integration
- [ ] Spatial positioning model (x, y, scale on canvas)
- [ ] Infinite canvas view with pinch/zoom
- [ ] Frame/card UI for entries on canvas
- [ ] Animated transitions between entries
- [ ] Multi-module Gradle setup (`:core`, `:feature:diary`, `:feature:canvas`)
