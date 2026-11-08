# AQ-API-002 — Hosting/runtime

**Источник:** [04-open-questions.md / AQ-API-002](../../04-open-questions.md#aq-api-002--hostingruntime)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

**Решение:** [принято] (2026-09-28) Для первого web/backend MVP выбираем Google Cloud Run ecosystem. Cloud Run Service используется для request-driven backend API и SSE; Cloud Run Jobs — для run-to-completion background workloads; Cloud Scheduler — для scheduled triggers. Durable queue/task mechanism, retry/idempotency и детальная job state model выбираются отдельно в AQ-API-004/AQ-OPS-002. Backend остаётся modular monolith в одной кодовой базе с несколькими runtime roles, без бизнес-микросервисов на старте.


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


### Сводка 3 — выбор hosting/runtime

После сравнения Cloud Run, Render и Railway выбран **Google Cloud Run ecosystem** для первого web/backend MVP.

Почему он лучше совпадает с текущим профилем проекта:
- request-driven API может работать как Cloud Run Service и scale-to-zero;
- SSE поддерживается как обычный long-lived HTTP response; reconnect допустим, потому что SSE несёт только change notification, а authoritative job/result state хранится отдельно;
- долгие run-to-completion операции естественно ложатся на Cloud Run Jobs;
- периодические workflows запускаются через Cloud Scheduler;
- Google Drive/OAuth не требует Cloud Run, но общий Google Cloud environment уменьшает количество разных operational surfaces;
- container model сохраняет portability и оставляет возможность позже переехать на другой container hosting.

Render и Railway остаются возможными alternatives, если operational complexity GCP окажется непропорциональной пользе, но не являются выбранным MVP runtime.

Operational principle для deployment:
- редкие initial setup/admin действия допустимо делать вручную;
- должно быть документировано, что и зачем настраивается;
- routine deploy/update не должен зависеть от ручного "кликания" в cloud console;
- deployment по возможности воспроизводится из repo/scripts/CI, без требования полного Infrastructure-as-Code с первого дня.

Не закрывается этим решением:
- Cloud Tasks vs Pub/Sub vs прямой запуск Cloud Run Job;
- job lifecycle/status;
- retry/backoff/idempotency/deduplication;
- точный CI/CD и environment layout.
Эти вопросы относятся к AQ-API-004, AQ-OPS-002, AQ-OPS-005 и AQ-API-005.
