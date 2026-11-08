# AQ-INT-002 — Calendar Timeline priority

**Источник:** [04-open-questions.md / AQ-INT-002](../../04-open-questions.md#aq-int-002--calendar-timeline-priority)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

пользователь — «мне кажется умение обновлять в календаре это очень удобно - до полученяи полнорабочего сайта есть другой интерфейс для валидации»

ChatGPT — Принято: Calendar Timeline Projection нужна рано, одновременно с развитием Calendar Inbox, а не после готовности полноценного web UI. Это позволяет визуально проверять результат обработки записей в привычном Calendar интерфейсе до завершения сайта. Существующий исторический workflow 05_Workflow_Google_Calendar_Timeline_Projection.md предусматривает идемпотентные create/update из canonical Entries, one-way sync, один Calendar event на Entry и overwrite ручных изменений Calendar при следующей проекции. Слово «валидация» не означает автоматически редактирование canonical Diary из Calendar: write-back остаётся отдельным открытым UX вопросом; нельзя незаметно менять ранее утверждённый one-way model.

**Решение:** [принято] (2026-11-08) Calendar Timeline Projection — часть раннего интеграционного этапа рядом с Calendar Inbox, до полнофункционального web UI. Использовать как альтернативный интерфейс просмотра и визуальной проверки Entry. Сохранить one-way canonical Entry → Calendar event с обновлением одного event при committed changes и независимостью от Calendar Inbox. Вопрос о корректировках/подтверждении записей непосредственно через Calendar требует отдельного явного решения; пока не включать calendar-to-diary write-back.
