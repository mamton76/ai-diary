# PRD — AI Diary (MVP)

## 1. Overview

Product name: AI Diary  
Type: Mobile-first application (Android MVP) with cloud backend  
Role: Foundational layer for ZoomAlbum

AI Diary is a personal journaling system that allows users to quickly capture their daily experiences (text, voice, links, media), and uses AI to structure and enrich this data for future transformation into interactive albums.

---

## 2. Product Vision

People want to remember their lives, but:

- writing structured diaries is hard  
- media is scattered across apps  
- memories are not connected  

AI Diary solves this by:

- making capture fast and effortless  
- structuring data automatically with AI  
- preparing data for visual storytelling (ZoomAlbum)

---

## 3. MVP Scope

### Goal
Enable fast daily capture and reliable storage.

### Included

- Create text entry
- Automatic timestamps
- Entry list
- Entry detail view
- Cloud persistence (Firebase)
- Basic loading/error states

### Not included (yet)

- media attachments
- tagging UI
- album generation
- AI summaries

---

## 4. Core Concepts

### Entry

Represents a normalized diary record.

Fields:

- id
- rawText
- cleanedText (optional)
- createdAt
- entryDate
- eventDateTime (optional)
- source (TEXT / VOICE / IMPORT)
- status (RAW / PROCESSED)

---

### Asset (future)

Represents external content:

- photo
- audio
- video
- link

Fields:

- id
- type
- storageType
- url
- previewUrl
- metadata

---

### Relations (future)

- Entry → Assets
- Entry → Tags
- Entry → People / Places

---

## 5. User Flow

### Create Entry

1. Open app
2. Tap "New Entry"
3. Enter text
4. Save
5. Entry appears in list

---

### View Entries

1. Open app
2. See list sorted by date
3. Tap entry
4. View detail

---

## 6. AI Role (Post-MVP)

AI will:

- clean text
- extract topics
- detect structure (tasks, events, reflections)

Important:
- rawText is always preserved
- AI output is optional and replaceable

---

## 7. Storage Strategy

### Structured data

Stored in Firebase Data Connect:

- Entry
- Asset metadata
- relations

---

### Asset storage

Hybrid model:

#### Firebase Storage (primary)
- uploads
- previews
- active files

#### Google Drive (optional)
- backups
- user-owned originals
- archive/export

---

## 8. Android Architecture

Stack:

- Kotlin
- Jetpack Compose
- MVI
- Clean Architecture
- StateFlow
- Hilt
- Coroutines

Layers:

- Presentation
- Domain
- Data

---

## 9. Screens (MVP)

- Entry List
- Entry Detail
- Create Entry

---

## 10. Non-functional Requirements

- fast input (<1s)
- stable storage
- simple UX
- scalable model

---

## 11. Future Extensions

### Phase 2
- media attachments
- voice input

### Phase 3
- AI summaries
- tagging
- search

### Phase 4
- ZoomAlbum integration

---

## 12. Design Principles

- capture first, structure later  
- minimal friction  
- AI is assistant, not blocker  
- user data is always preserved  

---

## 13. Success Criteria

- entry created in <10 seconds  
- reliable storage  
- clean architecture  
- ready for extension  

---

## 14. Open Questions

- rawText retention policy  
- AI trigger timing  
- offline strategy  

---

## 15. Development Strategy

1. Build minimal flow  
2. Validate architecture  
3. Expand gradually  

---

End of document
