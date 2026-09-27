# AQ-DATA-003 — Concurrency / optimistic locking

**Источник:** [04-open-questions.md / AQ-DATA-003](../../04-open-questions.md#aq-data-003--concurrency--optimistic-locking)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

## Обсуждение

### Сводка 1 — lease и optimistic locking решают разные задачи

Уточнено, что soft editing/mutation lease из AQ-DATA-010 уже является первой линией защиты от одновременной записи в одну Entry:

- lease scoped **per Entry**, а не на весь дневник;
- разные вкладки могут независимо редактировать разные Entries и владеть отдельными leases;
- если вторую session принудительно делают editor той же Entry, lease переходит ей, предыдущая session становится paused/read-only;
- прежняя session не имеет права просто сохранить поверх: чтобы снова писать, она должна заново получить lease и сначала синхронизироваться со свежим server draft;
- локальные unsynced изменения потерявшей lease session сохраняются через local recovery snapshots.

При этом lease не заменяет optimistic concurrency: race может возникнуть между backend requests, после process failure/retry, при внешнем изменении canonical storage или если AI job физически завершилась уже после потери lease.

### Сводка 2 — две проверки перед committed mutation

Для committed mutation должны одновременно выполняться два условия:

1. операция всё ещё владеет актуальным editing/mutation lease для этой Entry;
2. current committed revision всё ещё совместима с `baseRevisionId` / domain version, от которой операция работала.

Если lease потерян — commit запрещён. Если base revision устарела — silent last-write-wins запрещён; выполняется compatibility/rebase/merge/conflict flow в зависимости от типа изменения.

### Сводка 3 — storage-level conditional write остаётся последней защитой

Domain/API concurrency token — `baseRevisionId` или эквивалентный domain version. На нижнем storage layer адаптер дополнительно использует storage-native conditional version token (`ETag`, generation/version token или эквивалент), если backend его предоставляет.

Если storage token изменился между проверкой и физической записью, conditional write должен провалиться. Backend перечитывает актуальное canonical state и запускает уже согласованный external-change/reconciliation path из AQ-DATA-004; storage race не превращается в silent overwrite.

Таким образом:

`lease ownership` → координация mutation owner;
`baseRevisionId/domain version` → optimistic concurrency на уровне модели Entry;
`storage ETag/version token` → compare-and-swap защита физической canonical записи.

Точный provider-specific вид storage token остаётся architecture/adapter detail и не требует привязки baseline к Google Drive API.

**Решение:** [принято] (2026-09-27) Committed mutation для Entry разрешена только актуальному владельцу per-entry editing/mutation lease и должна быть привязана к `baseRevisionId` (или эквивалентному domain version). Потеря lease запрещает commit; несовпадение base/current revision запрещает silent last-write-wins и ведёт в compatibility/rebase/merge/conflict flow. Storage adapter дополнительно использует native conditional write/version token (`ETag`/generation/version или эквивалент), если storage это поддерживает; storage race приводит к reload/reconcile, а не overwrite. Lease, domain optimistic locking и storage compare-and-swap являются дополняющими уровнями защиты.

