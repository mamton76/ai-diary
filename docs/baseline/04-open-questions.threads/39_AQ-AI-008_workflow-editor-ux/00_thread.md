# AQ-AI-008 — Workflow editor UX

**Источник:** выделено из resolved AQ-AI-002 (2026-10-18)  
**Статус:** открыто  
**Состояние:** open  
**Claim:** none  
**Ведёт:** —  
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

Пока не начато.

**Нужно от пользователя:** вернуться к UX workflow editor отдельной сессией/этапом.

**Решение:** —
