# AQ-DATA-001 — Files-only или files + derived DB/index?

**Источник:** [04-open-questions.md / AQ-DATA-001](../../04-open-questions.md#aq-data-001--files-only-или-files--derived-dbindex)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md, ../../02-requirements-inventory.md и architecture data design

## Вопрос

Нужен ли AI Diary только на canonical files/Drive или поверх них нужен derived DB/index для быстрых listing/filter/search?

## Контекст

Уже решено, что user-owned portable files — canonical source of truth. Derived DB/index/cache допустимы, если они rebuildable и не становятся единственной копией существенных diary data.

## Обсуждение

### Сводка 1 — старт

Обсуждаем варианты files-only, lightweight cache/index, relational DB projection и hybrid, а также UX/performance impact чистого Drive.

### Сводка 2 — решение

Для первого MVP начинаем **без database/index и без search**: canonical data читаются из Drive/files через отдельный data layer/repository abstraction.

Data layer должен быть изолирован от конкретного storage API, чтобы позже без переделки UI/domain logic можно было добавить rebuildable derived index.

Persistent database не должна становиться хранилищем canonical diary content. Причина — privacy и ownership: durable diary content/revisions остаются в user-owned storage.

При этом operational state (например drafts/proposals/jobs) может временно содержать приватные данные там, где это необходимо для работы продукта; принцип — минимизировать такие серверные копии и не превращать их в второй canonical store.

Когда появится search/performance need, добавляется rebuildable index. Что именно допустимо индексировать с точки зрения privacy (metadata-only vs title/tags/full text) решается отдельно вместе с search/indexing design.

**Решение:** [принято] MVP starts files-only behind a separate data layer; no DB/search required initially. Architecture must allow a later rebuildable derived index, while canonical diary content remains in user-owned storage rather than a server database.
