# FQ-06 / SQ-01 — Lifecycle-охват Drafts / Needs attention на Home

**Источник:** [Функциональное ТЗ, Home-выборки и FQ-06](../../../AI-Diary-Functional-Spec-v0.1.md#8-выборки-поиск-и-производные-данные)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Codex — текущий диалог требований AI Diary  
**Режим фиксации:** written-turns  
**Родитель:** [FQ-06](../00_thread.md)  
**Дочерние треды:** —  
**Куда переносим решение:** Functional/Screens Specs, inventory/product baseline

## Вопрос

Включать ли Archived Entries в счётчики и переходы «Черновики» / «Требует внимания» на Home? Trash предлагается исключить в обоих вариантах.

Этот узел не выбирает lifecycle-охват Total entries и остальных статистических показателей автоматически.

## Уже принято

- Drafts / Needs attention — виджеты/фильтры, не отдельный lifecycle.
- Archived Entry может иметь durable Draft, который сохраняется.
- Несколько unresolved review items одной Entry дают одну Entry, не несколько.
- Count и список по клику имеют одинаковый predicate.
- Home EntryList и TagCloud имеют свои явно Active scope.
- Entries из navigation открывает Browser без скрытого Active-фильтра.
- «За всё время» определяет период, но не включает автоматически все lifecycle.

## Варианты

1. **Рекомендация:** Drafts / Needs attention на Home включают ACTIVE и ARCHIVED, исключают TRASH. Так незавершённая работа и unresolved items не пропадают только из-за архивации. Список по клику передаёт тот же явный State scope.
2. Только ACTIVE; архивные Draft/review items доступны при явном выборе архива в Browser.

## Контекст

Это scope двух рабочих очередей, а не объявление всех Home counters одинаковыми. Источники review items, точные статусы failed/conflict/uncertainty и их resolution остаются отдельной частью FQ-06. Draft из Trash не уничтожается, но его наличие само по себе не требует показывать его в рабочей очереди Home.

## Обсуждение

Codex — (2026-10-18) Предлагаю включать активные и архивные Entry в два Home counters «Черновики» / «Требует внимания», а Trash оставить вне этих очередей. И число, и список по клику имеют один и тот же scope. Это рекомендация, ещё не выбранная policy.

**Нужно от пользователя:** включать в «Черновики» / «Требует внимания» на Home Active + Archived, исключая Trash?

пользователь —

**Решение:** —
