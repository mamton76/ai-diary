# AQ-INT-002 — Calendar Timeline priority

**Источник:** [04-open-questions.md / AQ-INT-002](../../04-open-questions.md#aq-int-002--calendar-timeline-priority)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation (2026-11-08)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и roadmap/deployment planning

## Вопрос

Когда реализовывать Google Calendar Timeline Projection — derived, one-way представление дневниковых Entries в Google Calendar? Включать в первый полезный этап или после основного web browse/read/edit и Calendar Inbox integration?

## Уже принято

- [PQ-009](../09_PQ-009_calendar-inbox-role/00_thread.md): Calendar Timeline Projection — отдельная от Inbox derived integration, не canonical source of truth; одна Entry ↔ один Calendar event; при committed revision изменять существующий event, а не создавать по событию на каждую revision. Pending AI proposals не публикуются.
- [AQ-INT-001](../44_AQ-INT-001_calendar-inbox-priority/00_thread.md): ранний Calendar Inbox после unified CaptureItem/Inbox-to-Entry, до Telegram, с развитием существующих скриптов Calendar→Drive.
- Source `04-open-questions.md` считает Timeline полезной, но вероятно не critical path новой web/backend архитектуры. Исторический workflow `05_Workflow_Google_Calendar_Timeline_Projection.md` существует отдельно от Inbox.

## Обсуждение

ChatGPT — Рекомендация для MVP: Timeline Projection не делать обязательной частью первого работающего web/capture slice, но сохранить как ближайший отдельный следующий этап, после завершения базового Calendar Inbox + просмотра реальных Entries в web. Это сохраняет one-way projection contract и позволяет не задерживать основной путь от голоса к дневнику. Альтернатива — включить в первую интеграционную итерацию, если пользователь уже активно пользуется Calendar как viewer и существующий projection workflow легко переиспользуется.

**Нужно от пользователя:** Calendar Timeline Projection реализовываем одновременно с ранним Calendar Inbox или отдельно следующим этапом, после первых рабочих записей в web?

пользователь —

**Решение:** —
