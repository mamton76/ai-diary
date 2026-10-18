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

### Сводка восстановления обсуждения — 2026-10-18

пользователь — «а можешь поискать в какой соседней сессии мы его уже обсуждали AQ-API-003 - и давай продожим тут ?»

ChatGPT — Восстановлена соседняя беседа от 2026-09-27: API следует выводить из экранов и сценариев (Browse/Search, EntryScreen/EntryPanel, Draft/edit/commit, leases, History/Revisions, proposal review, AI workflows). Рабочее направление: REST + JSON; ресурсы Entries/Drafts/Revisions/Proposals/Jobs; optimistic concurrency через baseRevisionId и явные conflicts; долгие jobs через 202 + jobId; SSE для lightweight notifications. Эти позиции были рекомендациями обсуждения, не окончательно принятым AQ-API-003. Отдельные сессии в настоящее время разбирают экраны, поэтому здесь разумно согласовать минимальные API principles без параллельного проектирования screen-specific endpoints.

**Нужно от пользователя:** согласовать REST + JSON и минимальные API principles сейчас или сначала разобрать один конкретный спорный аспект контракта.

**Решение:** —
