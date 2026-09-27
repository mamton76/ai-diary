# AQ-API-002 — Hosting/runtime

**Источник:** [04-open-questions.md / AQ-API-002](../../04-open-questions.md#aq-api-002--hostingruntime)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture deployment/runtime design

## Вопрос

Где и как запускать backend AI Diary в первом web/backend MVP?

## Контекст

Текущий source отмечает Cloud Run как сильного кандидата из-за container model и scale-to-zero, но выбор ещё не зафиксирован.

Сравниваем по:
- стоимости;
- cold starts;
- background execution;
- scheduler/queue integration;
- Google OAuth/Drive convenience;
- logs;
- deployment complexity.

Нужно сначала решить не конкретный vendor feature-list, а какой operational profile нам реально нужен: always-on server или request-driven container/runtime с отдельными jobs/background tasks.

**Решение:** —


### Сводка 1 — runtime profile, durable AI jobs и live updates

В ходе обсуждения уточнён реальный runtime profile AI Diary.

Backend не сводится к обычному request/response API. Нужны:
- быстрый request-driven API для web/integrations;
- **durable asynchronous jobs/workers** для долгих или ненадёжных операций;
- scheduler/event triggers для фоновых workflows;
- lightweight server-to-browser updates для открытого web UI.

AI/background workflows могут запускаться тремя основными способами:
- **event-triggered** — например после capture/commit запуск cleanup, normalization, tagging/enrichment;
- **user-triggered** — пользователь вручную запускает workflow / custom analysis;
- **schedule-triggered** — например period review «как прошёл ваш месяц».

Все три способа должны сходиться в одну durable job model. Job не должна зависеть от открытой browser session и не должна держать пользовательский HTTP request до завершения. Длительные LLM calls, retries и temporary failures являются штатным сценарием.

Результат job сначала сохраняется на backend/canonical/operational state согласно workflow semantics; открытый web UI получает только lightweight change notification и перечитывает актуальное состояние. Потерянное live notification не должно означать потерю результата.

Для **открытой страницы** предварительно выбран **SSE (Server-Sent Events)** как достаточный server -> browser канал. WebSocket не нужен без отдельного двустороннего realtime use case. Когда страница закрыта, notifications/push **не требуются**; при следующем открытии клиент просто читает актуальное состояние.

Следствие для hosting/runtime: кандидат должен хорошо поддерживать request-driven API, durable background execution/scheduler/queue semantics и SSE/long-lived HTTP connections либо разумный fallback.

Детальная job state/retry/idempotency policy остаётся в AQ-API-004 / AQ-OPS-002; здесь это constraint на выбор runtime.


### Сводка 2 — modular monolith, несколько runtime roles

Пользователь подтвердил направление: не вводить бизнес-микросервисы на старте.

Рабочая модель:
- один backend codebase / modular monolith;
- общие domain/repository/workflow layers;
- несколько runtime roles / entry points из одной кодовой базы:
  - API service — HTTP API + SSE;
  - worker/job runtime — AI workflows, retries, backfills, indexing;
  - scheduled job runtime — периодические workflows и maintenance;
- при необходимости роли могут собираться из одного container image и запускаться разными hosting primitives;
- позже отдельный runtime можно выделить в самостоятельный service, если появится реальная нагрузка, security boundary или технологическая причина.

Не планируем отдельные бизнес-сервисы вроде Entry Service / Tag Service / Calendar Service / AI Service без необходимости.
