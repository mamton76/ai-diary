# AQ-API-003 — API style

**Источник:** [04-open-questions.md / AQ-API-003](../../04-open-questions.md#aq-api-003--api-style)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture API design

## Вопрос

Какой API contract/style нужен между web/future clients и Kotlin/Ktor backend, чтобы он оставался простым для MVP, но явно поддерживал уже принятые semantics: resources, revisions, optimistic concurrency, long-running jobs, assets/downloads и auth?

## Контекст

Уже принято:

- core backend — Kotlin/Ktor;
- hosting — Cloud Run Service + Jobs/Scheduler;
- clients и internal processes работают с core diary через backend/domain API;
- canonical storage скрыт за domain repository;
- committed mutation использует base revision/domain version;
- per-entry lease и storage conditional writes защищают mutations;
- долгие AI/background workflows durable и не должны держать browser request до завершения;
- открытый web UI может получать lightweight updates через SSE;
- Asset поддерживает managed/external originals.

## Исходная развилка

REST выглядит простым default, но нужно определить минимальные правила для:

- endpoint/resource model;
- API versioning;
- pagination;
- errors;
- optimistic concurrency fields;
- long-running job semantics;
- upload/download semantics;
- auth scheme.

Важно не превращать этот вопрос в полное проектирование всех endpoint-ов заранее.

## Обсуждение

**Решение:** —
