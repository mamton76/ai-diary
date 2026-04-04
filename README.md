# AI Diary

A personal journaling app for Android — the foundational layer for **ZoomAlbum**, a spatial media album with an infinite canvas.

## What it does

- Create text diary entries with title, body, and date
- View and browse entries sorted by date
- Offline-first: works without internet, syncs to Firebase when connected
- Google Sign-In for user authentication

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Kotlin |
| UI | Jetpack Compose + Material3 |
| Architecture | MVI + Clean Architecture |
| State | StateFlow + Channel (side effects) |
| DI | Hilt |
| Local DB | Room |
| Backend | Firebase Data Connect (PostgreSQL) |
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
- **Firebase Data Connect** is the sync target (write locally first, push in background)
- **Repository pattern**: interface in domain, implementation in data

## Setup

1. Clone the repo
2. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
3. Enable Authentication (Google Sign-In) and Data Connect
4. Download `google-services.json` and place it in `app/`
5. Open in Android Studio and run

## Roadmap

See [todo.md](todo.md) for detailed next steps.

- **Phase 1** — Firebase Auth + Data Connect sync
- **Phase 2** — Media attachments (Firebase Storage)
- **Phase 3** — AI enrichment (summaries, tagging)
- **Phase 4** — ZoomAlbum integration (infinite canvas, spatial layout)

## Related docs

- [PRD](prd.md) — product requirements
- [Architecture](architecture.md) — technical architecture decisions
