# Diary App — Next Steps

## Phase 5: Firebase Auth
- [ ] Create Firebase project in Firebase Console
- [ ] Download real `google-services.json` and replace placeholder in `app/`
- [ ] Create `FirebaseModule.kt` (provides `FirebaseAuth` singleton)
- [ ] Create `AuthViewModel.kt` (Google Sign-In flow via Credential Manager)
- [ ] Create `AuthScreen.kt` (sign-in UI)
- [ ] Add `Auth` route to `Screen.kt`
- [ ] Gate navigation in `DiaryNavHost.kt` (redirect to auth if not signed in)
- [ ] Test sign-in flow on emulator/device

## Phase 6: Firebase Data Connect
- [ ] Set up Data Connect in Firebase Console (enable PostgreSQL)
- [ ] Define GraphQL schema (`dataconnect/schema.gql` — Entry table with `uid`)
- [ ] Define queries (`dataconnect/queries.gql` — ListEntriesByUser, GetEntryById)
- [ ] Define mutations (`dataconnect/mutations.gql` — UpsertEntry)
- [ ] Create `connector.yaml` config
- [ ] Run `firebase dataconnect:sdk:generate` to generate Kotlin SDK
- [ ] Create `EntryRemoteDataSource.kt` (wraps generated SDK)
- [ ] Update `EntryMapper.kt` with remote DTO mappings
- [ ] Update `FirebaseModule.kt` to provide Data Connect connector
- [ ] Wire real sync logic in `EntryRepositoryImpl.kt`
- [ ] Test end-to-end: create entry locally → syncs to Firebase → pull from Firebase

## Phase 7: Polish
- [ ] Empty state illustrations or improved messaging
- [ ] Better date formatting (relative: "Today", "Yesterday", etc.)
- [ ] Loading skeleton / shimmer for entry list
- [ ] Swipe-to-delete entries
- [ ] Edit existing entries
- [ ] Search / filter entries
- [ ] Material3 styling refinements

## Future (To ZoomAlboom Evolution)
- [ ] Media attachments (images, audio) on entries
- [ ] Spatial positioning model (x, y, scale on canvas)
- [ ] Infinite canvas view with pinch/zoom
- [ ] Frame/card UI for entries on canvas
- [ ] Animated transitions between entries
- [ ] Multi-module Gradle setup (`:core`, `:feature:diary`, `:feature:canvas`)
