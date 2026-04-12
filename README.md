# AI Diary

An Android-first, offline-first personal diary app. The foundational layer for **ZoomAlboom**, a spatial media album with an infinite canvas.

## Product direction

AI Diary lets users quickly capture daily experiences as text entries. Entries are stored locally first (Room) and synced to the cloud (Firebase Data Connect) in the background. The app is designed to work fully offline and sync when connectivity is available.

Long-term, AI Diary will expand into media capture, AI enrichment, and integration with ZoomAlboom for visual storytelling.

## MVP scope

- Create text diary entries (title, body, date)
- View and browse entries sorted by date
- Local persistence with Room (works fully offline)
- Pull-to-refresh, loading/error/empty states

## Current status

**Implemented:**
- Project skeleton: Compose + Hilt + Room + MVI
- Domain layer: Entry model (with `entryDate`, `source` fields), repository interface, use cases
- Data layer: Room database, DAO, offline-first repository (local only)
- UI: Entry list screen, entry detail/create screen, navigation
- Firebase dependencies added (Auth, Data Connect, Storage)

**Prepared (dependency added, not yet wired):**
- Firebase Auth (Google Sign-In) — `google-services.json` connected
- Firebase Data Connect — no schema or sync logic yet
- Firebase Storage — dependency ready for future media

**Planned next:**
- Auth screen + sign-in flow
- Data Connect schema + background sync
- Edit/delete entries

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Kotlin |
| UI | Jetpack Compose + Material3 |
| Architecture | MVI + Clean Architecture |
| State | StateFlow + Channel (side effects) |
| DI | Hilt |
| Local DB | Room (single source of truth) |
| Cloud backend | Firebase Data Connect (PostgreSQL) |
| File storage | Firebase Storage |
| Auth | Firebase Auth (Google Sign-In) |
| Async | Coroutines |

## Project structure

```
com.mamton.aidiary/
├── core/          DI modules, navigation, theme
├── domain/        Pure Kotlin models, repository interfaces, use cases
├── data/          Room entities, DAO, mappers, repository implementation
└── feature/
    ├── entrylist/     Entry list screen (MVI)
    └── entrydetail/   Entry detail/create screen (MVI)
```

## Architecture

- **Domain layer** is pure Kotlin — no Android or Firebase dependencies
- **Room** is the single source of truth; UI observes Room via Flow
- **Writes happen locally first**, then sync to Firebase Data Connect in the background
- **Repository pattern**: interface in domain, implementation in data

## Setup

1. Clone the repo
2. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
3. Enable Authentication (Google Sign-In) and Data Connect
4. Download `google-services.json` and place it in `app/`
5. Open in Android Studio and run

## Roadmap

See [todo.md](docs/todo.md) for detailed next steps.

- **Phase 2** — Auth + cloud sync (Firebase Data Connect)
- **Phase 3** — Edit, delete, polish, search
- **Phase 4** — Media attachments (Firebase Storage)
- **Phase 5** — AI enrichment
- **Phase 6** — ZoomAlboom integration

## Related docs

- [PRD](docs/prd.md) — product requirements
- [Architecture](docs/architecture.md) — technical architecture decisions
