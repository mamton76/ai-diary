# PQ-009 — Нужен ли Calendar inbox как постоянная production feature?

**Источник:** [04-open-questions.md / PQ-009](../../04-open-questions.md#pq-009--нужен-ли-calendar-inbox-как-постоянная-production-feature)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
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

Пользователь отдельно поднял вопрос о публикации обновлений/ревизий готовых записей в Calendar.

Текущий historical projection уже предполагает one-entry -> one-calendar-event mapping и обновление существующего event при изменении entry. Это покрывает публикацию текущего committed состояния записи.

Отдельно не решено, нужно ли публиковать/показывать revision history в Calendar как отдельные события/версии или только отображать current state. Это вынесено в future question.

**Решение:** —
