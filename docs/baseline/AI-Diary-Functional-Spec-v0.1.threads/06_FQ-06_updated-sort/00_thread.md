# FQ-06 — Сортировка Updated при наличии Draft

**Источник:** [Функциональное ТЗ, QRY-03/FQ-06](../../AI-Diary-Functional-Spec-v0.1.md#14-открытые-системные-вопросы)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Codex — текущий диалог требований AI Diary  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
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

**Нужно от пользователя:** сортировка «По изменению» учитывает последние содержательные правки Draft ещё до Save?

пользователь —

**Решение:** —
