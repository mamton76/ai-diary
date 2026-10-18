# AQ-API-004 — Background processing

**Источник:** [04-open-questions.md / AQ-API-004](../../04-open-questions.md#aq-api-004--background-processing)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation (2026-10-18)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture jobs/runtime design

## Вопрос

Как организовать background processing для capture normalization, indexing, Calendar sync, AI workflows, migrations/backfills и retries, не потеряв задачи при сбое и не усложняя MVP ненужными сервисами?

## Варианты

1. Inline HTTP processing: просто, но длительные и прерванные операции ненадёжны.
2. Durable task queue + worker/job execution: запрос регистрирует работу, ответ быстрый, worker обрабатывает повторно при сбое; больше инфраструктуры.
3. Scheduler + Cloud Run Jobs только для пакетных/scheduled workflows: хорош для периодических запусков, но сам не закрывает durable per-user trigger.
4. Гибрид: короткие чтения/валидация inline; долгие/повторяемые операции через durable task/job execution; scheduled/batch через Scheduler + Cloud Run Jobs.

## Контекст

Уже принято в AQ-API-002: Cloud Run Service (Kotlin/Ktor API + SSE), Cloud Run Jobs для run-to-completion, Cloud Scheduler для periodic triggers, один modular monolith с разными runtime roles. Долгие workflows не зависят от browser session. В AQ-API-003 принят REST + JSON с OpenAPI контрактом. AQ-OPS-002 отдельно разберёт детали idempotency/retry; конкретная queue/task implementation ранее сознательно оставлена открытой.

## Обсуждение

ChatGPT — **2026-10-18:** Рекомендую гибрид (вариант 4), с durable статусом задачи до подтверждения пользователю, что она принята; не держать длинный AI workflow внутри HTTP request. Для первого MVP предлагаю обсудить только принцип запуска/исполнения, не фиксируя заранее все очереди, retry/backoff и operational параметры. Для немедленных долгих задач нужна durable dispatch модель (например, Cloud Tasks -> worker/API endpoint), а Cloud Run Jobs разумнее использовать для batch/backfill, но выбор конкретного dispatch продукта можно оставить реализации с явно заданными гарантиями.

**Нужно от пользователя:** подтвердить гибридную модель или попросить сравнить варианты подробнее.

пользователь —

**Решение:** —
