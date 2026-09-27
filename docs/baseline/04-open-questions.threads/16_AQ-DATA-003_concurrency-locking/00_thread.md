# AQ-DATA-003 — Concurrency / optimistic locking

**Источник:** [04-open-questions.md / AQ-DATA-003](../../04-open-questions.md#aq-data-003--concurrency--optimistic-locking)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Как AI Diary должен предотвращать тихую потерю изменений, когда одна и та же entry меняется из нескольких мест или процессов одновременно?

## Уже принятый контекст

- canonical diary data живут в user-owned files;
- MVP online-first;
- revisions append-only и user-facing history линейная;
- manual editing использует server-side working draft/soft lease;
- AI proposal знает base state/revision и при несовместимом изменении может стать stale/conflicted;
- старый Android сейчас не активный client, но архитектура не должна блокировать будущие клиенты;
- derived DB/index в первом MVP не обязателен.

## Сценарии

- две browser tabs открыли одну entry;
- user edit и AI proposal/mutation пересеклись;
- backend пишет revision, а canonical file уже изменился;
- позже появится второй client;
- возможная ручная правка canonical files обсуждается отдельно в AQ-DATA-007.

## Рабочее направление

Для committed write нужен optimistic concurrency check: операция должна явно указывать base revision/version token (или эквивалент). Если current state уже изменился, backend не делает silent last-write-wins, а возвращает conflict/stale result.

Точный механизм — revision id, storage ETag/version token или комбинация — ещё нужно выбрать.

**Решение:** —
