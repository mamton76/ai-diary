# FQ-06 — Сортировка Updated при наличии Draft

**Источник:** [Функциональное ТЗ, QRY-03/FQ-06](../../AI-Diary-Functional-Spec-v0.1.md#14-открытые-системные-вопросы)  
**Статус:** решён (подпункт Updated sort; остальные FQ-06 открыты)  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** [FQ-06/SQ-04 — ошибки AI в Needs attention](04_SQ-04_failed-ai-attention/00_thread.md); [FQ-06/SQ-03 — lifecycle периодных counters](03_SQ-03_period-counter-scope/00_thread.md); [FQ-06/SQ-01 — lifecycle-охват очередей Home](01_SQ-01_home-queue-scope/00_thread.md); [FQ-06/SQ-02 — scope Total entries](02_SQ-02_total-entries-scope/00_thread.md)  
**Куда переносим решение:** Functional/Screens Specs, file-format, inventory/product baseline

## Вопрос

Что означает сортировка «По изменению», если текущий видимый content Entry находится в durable Draft и последняя content Revision старее? Остальные FQ-06 — lifecycle counters и review items — пока отдельно не обсуждаются.

## Варианты

1. **Рекомендация:** сортировать по последним содержательным правкам видимого content: при Draft — его updatedAt, без Draft — committedUpdatedAt. Пользователь начал менять старую запись, ещё не нажал Save — при Updated desc она поднимается.
2. Учитывать только committedUpdatedAt: пока Save не создал новую Revision, правки Draft не двигают Entry в Updated-сортировке.

## Контекст

- Списки уже используют текущее Draft-state, включая Event date; Draft не отдельная строка и не имеет отдельного приоритета.
- Autosave не меняет committed Entry.updatedAt/currentRevisionId.
- Draft имеет собственный updatedAt; generic sort может использовать производный effectiveUpdatedAt, не переписывая committed metadata.
- Техническая повторная синхронизация тех же bytes/статусов или heartbeat не должна изображаться новой содержательной правкой.
- При выборе варианта 1 Discard/NO_CHANGE убирает Draft и возвращает сортировку к committed timestamp; NO_CHANGE не обновляет его.
- Save/Apply/Restore content timestamps и lifecycle audit timestamps не смешиваются.
- У новой Entry без committed Revision нужно иметь определённую позицию, а не исключать её из списка; конкретный fallback задаётся implementation contract.

## Обсуждение

Codex — (2026-10-18) Предлагаю вариант 1: сортировка Updated отражает последние правки, включая Draft. Иначе пользователь изменяет старую запись, но не видит её среди недавно изменённых. committedUpdatedAt остаётся прежним до content commit; текущий выбор не создаёт Revision по autosave. Это предложение, не принятое правило.

пользователь — (2026-10-18) «в этой сортирвоке да конечно»

Codex — (2026-10-18) Принят вариант 1 именно для Updated sort; это не разрешение менять committedUpdatedAt при autosave. Решение перенесено в Functional/Screens Specs, file-format и inventory/product baseline. Обсуждавшийся подпункт завершён; сразу переходим к отдельному [SQ-01 — охват очередей Home](01_SQ-01_home-queue-scope/00_thread.md), не переоткрывая default Event date sort.

Codex — (2026-10-18) SQ-01 завершён: рабочие очереди включают ACTIVE + ARCHIVED, исключая TRASH. Сразу открыт отдельный SQ-02 — lifecycle-охват Total entries; этот выбор ещё не принят.

Codex — (2026-10-18) SQ-02 завершён: Total entries включает ACTIVE + ARCHIVED, исключая TRASH. Открыт SQ-03 — аналогичный отдельный выбор для периодных статистических counters. Его рекомендация ещё не принята.

Codex — (2026-10-18) SQ-03 завершён: три периодных статистических counters учитывают ACTIVE + ARCHIVED, исключая TRASH. Следующий вопрос — timezone rolling days — обсуждается в FQ-05/SQ-01. Полная модель review items и scope прочих агрегатов не объявляются решёнными.

Codex — (2026-10-18) После продуктовых уточнений FQ-05 открывается отдельный SQ-04: включать ли актуальную ошибку AI Run, требующую действия пользователя, в Needs attention. Предложение не выбирает техническую retry-policy FQ-07 и не переоткрывает Updated sort.

**Решение:** [принято] (2026-10-18) Сортировка «По изменению» учитывает последние содержательные правки Draft ещё до Save: при текущем Draft используется его content updatedAt, без Draft — committedUpdatedAt Entry. Это производный effectiveUpdatedAt для сортировки, а не изменение committed metadata и не новая Revision. Повторный autosave неизменного содержимого, heartbeat и технический progress загрузки не поднимают Entry заново. После Discard/NO_CHANGE без Draft используется прежний committedUpdatedAt.
