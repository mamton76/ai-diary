# AQ-AI-008 — Workflow editor UX

**Источник:** выделено из resolved AQ-AI-002 (2026-10-18)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT  
**Режим фиксации:** written-turns  
**Родитель:** AQ-AI-002  
**Дочерние треды:** —  
**Куда переносим решение:** AI-Diary-Screens-Spec-v0.1.md / workflow editor UX

## Вопрос

Как выглядит пользовательский editor user-owned workflow/routine поверх уже принятой архитектурной модели?

Нужно определить как минимум:

- представление linear pipeline и simple conditions;
- поля шага и workflow-level settings;
- выбор/default executor и capability profile;
- редактирование prompt/instructions/output schema;
- trust UX для executable modules;
- Draft / Test run / Publish tested version;
- version history, diff, Restore as new version;
- адаптацию editor для desktop/mobile.

Формат canonical storage и runtime contracts сюда не смешивать: они относятся к architecture/data design.

## Контекст

Архитектурная база закрыта в [AQ-AI-002](../32_AQ-AI-002_workflow-definition/00_thread.md). MVP workflow — linear pipeline + simple conditions, executable modules и capability profiles являются отдельными versioned сущностями, user workflow имеет Draft → Publish version semantics.

## Обсуждение

ChatGPT — **старт обсуждения (2026-10-18):** AQ-AI-008 продолжается поверх закрытой архитектуры AQ-AI-002. Существующий S13 уже задаёт Routines / Runs, system/user routines, запуск из Entry/Browser/Routines, scope/eligibility и Run Detail. Здесь обсуждаем только сам editor user routine: визуальную структуру шагов, поля, trust/permissions, Draft/Test/Publish/history и adaptive UX.

**Нужно от пользователя:** выбрать базовое представление workflow editor.


пользователь — «да - толкьо бы еще обсудить на конкретных примерах наших форкфлоу»

ChatGPT — **решение о способе проработки editor UX (2026-10-18):** базовое представление принимаем как вертикальный список раскрываемых шагов с простыми inline conditions/branches, без node-canvas в MVP. Дальнейшие поля и controls editor нельзя проектировать только абстрактно: UX нужно прогнать на конкретных существующих workflows проекта, как минимум Tag Enrichment, Inbox → Entry и Google Calendar Timeline Projection, и только затем обобщать повторяющиеся primitives.

**Нужно от пользователя:** начать разбор с Tag Enrichment как наиболее показательным user-facing AI workflow.

**Решение:** —
