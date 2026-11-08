# PQ-009 — Нужен ли Calendar inbox как постоянная production feature?

**Источник:** [04-open-questions.md / PQ-009](../../04-open-questions.md#pq-009--нужен-ли-calendar-inbox-как-постоянная-production-feature)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Google Calendar inbox — временный мост для voice capture или нормальный optional transport/adapter, который можно оставить поддерживаемым наряду с другими capture channels?

## Связанный контекст

- [Product baseline §17 — Calendar timeline](../../03-product-baseline.md#17-calendar-timeline-как-optional-projection)
- [Source ledger](../../05-source-ledger.md): отдельно фиксирует Calendar Inbox и Calendar Timeline Projection.
- Historical workflow `04_Workflow_Google_Calendar_Inbox.md`: Calendar выступает external inbox/queue, после чего используется обычный Inbox-to-Entry.
- Historical workflow `05_Workflow_Google_Calendar_Timeline_Projection.md`: отдельная one-way projection из diary entries в Calendar.

## Обсуждение

### Сводка 1 — Calendar как transport

Пользователь склоняется к тому, чтобы оставить Calendar inbox как один из возможных transport/adapters. Calendar не должен быть ядром diary model или canonical storage; это просто удобный способ доставки capture в общий Inbox-to-Entry pipeline.

Рабочая позиция: не считать Calendar ни обязательным core-компонентом, ни обязательно временным hack. Он может оставаться optional production integration, пока полезен.

### Сводка 2 — отдельно от inbox существует timeline projection

Пользователь уточнил: речь не о публикации revision history отдельными Calendar events. Для одной diary entry должен существовать один Calendar event; при появлении новой committed revision этого entry существующий event обновляется до текущего состояния.

Это соответствует уже описанному historical projection workflow: one-entry -> one-calendar-event mapping с update существующего event при изменении entry.

Pending proposals в Calendar не публикуются, потому что они ещё не committed состоянием diary entry.

**Решение:** [принято] (2026-09-27) Google Calendar остаётся optional production transport/adapter для capture, а не core dependency и не обязательно временный hack. Отдельно Calendar timeline остаётся derived one-way projection: одна diary entry соответствует одному Calendar event, который обновляется при новых committed revisions/current-state changes; отдельные events на каждую revision не создаются.
