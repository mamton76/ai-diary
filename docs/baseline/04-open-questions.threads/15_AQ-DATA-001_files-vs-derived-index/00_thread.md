# AQ-DATA-001 — Files-only или files + derived DB/index?

**Источник:** [04-open-questions.md / AQ-DATA-001](../../04-open-questions.md#aq-data-001--files-only-или-files--derived-dbindex)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
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

**Решение:** —
