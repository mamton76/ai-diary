# AQ-INT-001 — Calendar Inbox priority

**Источник:** [04-open-questions.md / AQ-INT-001](../../04-open-questions.md#aq-int-001--calendar-inbox-priority)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation (2026-11-08)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md, implementation roadmap / integrations design

## Вопрос

Когда в последовательности реализации новой web/backend версии подключать Google Calendar Inbox: как ранний capture adapter после unified CaptureItem pipeline или позже, после другого capture channel? Роль интеграции как optional production transport уже решена в PQ-009, здесь выбираем приоритет, а не пересматриваем её назначение.

## Уже принято

- [PQ-009](../09_PQ-009_calendar-inbox-role/00_thread.md): Calendar Inbox — optional production capture adapter, не canonical diary storage и не обязательная core dependency. Calendar Timeline Projection — отдельное derived направление.
- [AQ-INT-004](../41_AQ-INT-004_capture-item-contract/00_thread.md): все источники дают нормализованный CaptureItem, хранят original source/snapshot и provenance; дедупликация по source identity; CaptureItem не равен готовой Entry.
- Historical workflow `04_Workflow_Google_Calendar_Inbox.md` (в project source): Gemini/voice создаёт событие в выделенном календаре `AI Diary Inbox`; adapter строит raw inbox package; общая Inbox-to-Entry processing создаёт Entry; оригинал сохраняется; успешно обработанное событие переносится в `AI Diary Processed`. Статус обработанности не должен зависеть только от перемещения события: file-based idempotency needed if calendar operation fails.
- В product baseline указано, что нельзя рассчитывать на надёжное создание и последующее обновление одного события конкретным voice assistant. Calendar — удобный способ доставки raw input, но ограничения voice UX остаются.

## Обсуждение

пользователь — «давай - продолжаем»

ChatGPT — Проверены source AQ-INT-001, принятый PQ-009 и исторический workflow. Предлагается обсуждать только очередность реализации, а не заново решать, является ли Calendar постоянным каналом. Варианты: (A) ранняя интеграция сразу после готовности CaptureItem/Inbox-to-Entry, до Telegram; (B) подключение после первого Telegram capture; (C) оставить для поздней совместимости без близкого дедлайна. Рекомендация — A, поскольку пользователь уже использует Calendar как голосовой мост и реализация опирается на существующий workflow, но приоритет ещё не подтверждён.

**Нужно от пользователя:** ставим Calendar Inbox в первую очередь после общего capture pipeline или сначала реализуем Telegram, а Calendar подключим следующим этапом?

пользователь —

**Решение:** —
