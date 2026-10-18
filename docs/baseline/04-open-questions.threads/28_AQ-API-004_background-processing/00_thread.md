# AQ-API-004 — Background processing

**Источник:** [04-open-questions.md / AQ-API-004](../../04-open-questions.md#aq-api-004--background-processing)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

пользователь — «мне кажется проще все делать через очередь (ну операции записи и ычислений т.е, запросы навернео ставить в очередь бессмысленно? )»

ChatGPT — Согласен с направлением разделить read queries (синхронно) и writes/computations (через durable queue), но важно различать принятие команды и committed result: пользователь не должен видеть «Сохранено», пока canonical mutation не завершена. Частые autosave обновления draft можно coalesce/debounce; не требуется отдельная задача на каждый keystroke. Для mutation-команд очередь должна сохранять порядок и concurrency guarantees; отдельный вопрос — допустима ли задержка для обычного Save или он должен завершаться синхронным подтверждением commit, пока тяжёлые изменения и AI работают через очередь.

**Нужно от пользователя:** для обычной кнопки Save допустим ли статус «в очереди / сохраняется» с последующим подтверждением, или Save должен подтверждать committed revision в рамках самого запроса?

пользователь — «Для AQ-API-004 выбираем асинхронный Save через очередь с подтверждением committed result после обработки.»

ChatGPT — Принято: Save регистрирует durable queued command; пользователь видит «Сохраняется», а «Сохранено» только после успешного committed result. Ошибка или конфликт видимы, не приравниваются к success. Read queries выполняются синхронно. Для autosave draft не нужна отдельная задача на каждую клавишу. Точный queue transport и retry/idempotency относятся к implementation и AQ-OPS-002.

**Нужно от пользователя:** распространяем ли тот же queue-first принцип на остальные пользовательские mutations (Apply, Restore, изменение тегов), или есть исключения?

пользователь — «думаю да»

ChatGPT — Фиксируем единый queue-first путь для всех изменений canonical diary state (Save/Apply/Restore/tag mutations, capture processing, AI and indexing), без очереди для обычных read/search queries. Принятие команды и успешный commit — разные состояния; возможность закрыть браузер не отменяет принятую задачу. Autosave draft разрешено coalesce/debounce; технический механизм доставки, гарантии idempotency, fairness и retry конкретизируются в AQ-OPS-002 и implementation design. Для scheduled/batch сохраняются уже принятые Cloud Scheduler/Cloud Run Jobs.

**Решение:** [принято] (2026-10-18) Queue-first architecture для canonical writes и вычислительных/background workflows. Синхронные read/search запросы остаются обычными API calls. Mutating commands асинхронно ставятся в durable очередь; UI различает accepted/queued, processing, committed и failed/conflicted. Статус «Сохранено» возможен только после committed revision. Draft autosave coalescing допускается. Долгие и scheduled tasks исполняются независимо от browser session; детальные queue provider, retry/idempotency/ordering/atomicity правила вынесены в AQ-OPS-002 и architecture design.
