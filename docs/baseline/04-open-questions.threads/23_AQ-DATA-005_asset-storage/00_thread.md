# AQ-DATA-005 — Asset storage

**Источник:** [04-open-questions.md / AQ-DATA-005](../../04-open-questions.md#aq-data-005--asset-storage)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Где физически хранятся originals и производные media/assets AI Diary: в том же user-owned Drive/file backend, в отдельном object storage или в hybrid-модели?

## Варианты

1. **Drive/file storage only** — originals и при необходимости previews/thumbnails живут в user-owned file storage.
2. **Object storage only** — media живёт в отдельном managed object storage, а canonical diary files содержат ссылки/metadata.
3. **Hybrid** — originals остаются в user-owned storage, а производные previews/thumbnails/cache могут жить в отдельном rebuildable storage.

## Контекст

Уже принято:

- user-owned portable files являются canonical source of truth;
- Google Drive — первая практическая реализация storage, но domain не должен зависеть от Drive;
- Asset имеет собственную identity и может быть связан с несколькими Entries;
- versioned связь мыслится как `EntryRevision ↔ Asset`;
- originals media должны сохраняться;
- Entry edit различает link existing Asset и create new Asset;
- unlink Asset от Entry и system-wide delete — разные операции;
- конкретный media backend до сих пор оставался открытым;
- нужно учитывать размер файлов, previews/thumbnails, streaming, portability, backup и cost.

## Обсуждение

**Решение:** —
