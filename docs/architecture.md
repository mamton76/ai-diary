# AI Diary — целевая архитектура Web/API MVP

**Срез:** 2026-11-08  
**Статус:** консолидированная архитектура на основе принятых решений. Это **не отчёт о реализованном коде**: состояние реализации и возможность повторного использования отдельных скриптов требуют code audit.  
**Историческая версия:** [Android / Room / Firebase architecture](architecture-legacy-android-firebase.md). Не использовать её как текущий design baseline.  
**План реализации:** [implementation-plan-web-mvp.md](implementation-plan-web-mvp.md).

## 1. Приоритеты и архитектурные границы

AI Diary — file-first personal memory system: сначала безопасно захватить raw input, потом превратить его в Entries с прозрачной историей. Новая версия ориентирована на адаптивный web UI и самостоятельный backend/domain API; существующее Android/Firebase приложение — исторический prototype/reference, а не платформа для обязательного продолжения.

- **Canonical source of truth:** portable user-owned diary files. Google Drive — первый storage backend, но не встроен в domain contracts.
- **Backend — mutation authority:** обычные клиенты и фоновые процессы не изменяют canonical files в обход проверок domain layer.
- **Derived:** индексы, operational DB/cache, поисковые структуры и Calendar Timeline могут быть восстановлены из canonical data; не хранить там единственную существенную копию дневника.
- **Entry и CaptureItem — разные сущности.** Raw capture никогда не заменяется AI-результатом.
- **Data ownership, revisions, provenance, low cost, provider-neutral AI, security** важнее привязки к конкретному UX или поставщику AI.

[Product baseline](baseline/03-product-baseline.md) · [requirements inventory](baseline/02-requirements-inventory.md) · [open architecture questions](baseline/04-open-questions.md)

## 2. Логическая схема

```text
Gemini / ChatGPT / other assistants
           |                Telegram bot (later)       Web client
           v                       |                        |
  Google Calendar Inbox            |                        |
           |                       |                        |
           +---------- capture adapters -------------------+
                               |
                    normalized CaptureItem
                               |
          Kotlin/Ktor backend / domain API / auth
              |          |            |
         Inbox→Entry   Commands      Queries
              |          |            |
           durable commands / jobs    |
              |          |            |
      canonical repository (portable files)
              |
       Google Drive first / replaceable storage
              |
       Entries + Revisions + Assets + raw/provenance
              |
      +----------------+------------------+
      |                |                  |
 rebuildable index   AI workflows   Calendar Timeline
 / read projections  + run trace    (read-only projection)
      |
    Search API

Optional later: remote MCP adapter → same backend/domain API.
```

Это логические обязанности, **не обязательное количество сервисов**. Начальный deployment должен быть небольшим и недорогим.

## 3. Client / Backend / API

**Core backend:** Kotlin + Ktor ([AQ-API-001](baseline/04-open-questions.threads/26_AQ-API-001_backend-language-framework/00_thread.md)). Специализированные Python workers допустимы позднее, если дадут измеримую пользу; второй runtime на старте не требуется.

**API:** REST + JSON, контракт и схемы описаны OpenAPI contract-first ([AQ-API-003](baseline/04-open-questions.threads/27_AQ-API-003_api-style/00_thread.md)). Read/list/search — обычные request/response операции. Изменения canonical state — **queue-first commands**: Save, Apply, Restore, tag mutations, capture processing и AI/indexing. Accepted/queued ≠ committed/saved. UI показывает `Сохранено` только после подтверждённого durable commit ([AQ-API-004](baseline/04-open-questions.threads/28_AQ-API-004_background-processing/00_thread.md)).

**Web:** полноценный адаптивный интерфейс с одним API; бизнес-правила остаются в backend. Первый рабочий поток — список/чтение существующих Entries, затем search/filters, edit/revision/history, tags, AI workflows. Reusable EntryPanel используется в view/edit/proposal review. Текстовый editor первого релиза поддерживает bold/italic/lists/links и хранит текст как Markdown; встроенный inline-AI editing не нужен ([AQ-WEB-003](baseline/04-open-questions.threads/43_AQ-WEB-003_editor-semantics/00_thread.md)).

**Frontend:** React + TypeScript + Vite SPA, обычный проект в репозитории, TypeScript-клиент из OpenAPI ([AQ-WEB-001](baseline/04-open-questions.threads/59_AQ-WEB-001_frontend-stack/00_thread.md), [AQ-WEB-006](baseline/04-open-questions.threads/60_AQ-WEB-006_sites-role/00_thread.md)); на телефоне — всё из E0–E2 ([AQ-WEB-002](baseline/04-open-questions.threads/61_AQ-WEB-002_mobile-scope/00_thread.md)). **Не зафиксировано:** конкретный frontend hosting (WEB-008). Обновление UI — SSE (API-009, AQ-WEB-004); revision UX — PQ-004/PQ-011, этап E2 (AQ-WEB-005). См. §11, не принимать эти решения по умолчанию.

## 4. Canonical data, Drive и безопасный Save

- Domain-level repository abstractions скрывают Google Drive и поддерживают будущую замену provider.
- Первый files-only slice не требует persistent database. Позже FTS/index/cache можно ввести как **derived** layer, сохранив files source of truth.
- Entry — стабильная identity и current committed state; Revision — immutable linear history. Save/Apply/Restore создают соответствующие новые committed revisions. Draft/autosave не является Revision до commit. Proposal до Apply не является Revision.
- Manual working drafts допускают debounce + guaranteed flush/recovery; конфликтующие writes проверяются lease/base revision/conditional storage version. Не делать silent overwrite.
- Raw CaptureItems, source snapshots, asset originals/references и provenance сохраняются независимо от получившейся Entry.
- Asset имеет отдельный ID и storage-independent original reference; previews/transcodes — производные. Внешние originals не удаляются при удалении diary links.

**Важно:** [file-format v1 draft](baseline/07-file-format-v1-draft.md) и [Save/recovery design](baseline/08-save-recovery-design.md) — технические **предложения для review**, а не утверждённые/развёрнутые migrations. Конкретные names/JSON layout/publication algorithm нельзя выдавать за реализованные решения.

## 5. Capture integration / Inbox

Все источники создают normalized CaptureItem: internal ID, source, source ID если есть, source timestamp и receivedAt, original text/media references, source metadata. Повторная доставка одного source event идемпотентна; два отдельных одинаковых сообщения — разные CaptureItems.

Несколько CaptureItems могут стать одной Entry через manual grouping без AI или optional AI assistance. Для ручного объединения доступных текстов открывается editable Draft Entry; только successful Save отмечает исходники обработанными. В MVP один CaptureItem служит максимум одной Entry; split отложен ([AQ-INT-004](baseline/04-open-questions.threads/41_AQ-INT-004_capture-item-contract/00_thread.md)).

**Calendar Inbox — ранний приоритет.** Развиваем существующие по словам пользователя scripts Calendar → Google Drive после аудита; adapter должен принять общую границу CaptureItem, source snapshots, idempotency и provenance. Calendar является optional production transport, а не canonical storage и не зависимостью diary core ([AQ-INT-001](baseline/04-open-questions.threads/44_AQ-INT-001_calendar-inbox-priority/00_thread.md)).

**Calendar Timeline — тоже рано, до полного web UI.** Это отдельная one-way projection **Entry → Calendar event**, один event на Entry, обновление на committed change. Календарь предназначен для просмотра и визуальной проверки: **никакого write-back, исправлений или подтверждений Entry из Calendar**. Ручные изменения проекции могут быть перезаписаны ([AQ-INT-002](baseline/04-open-questions.threads/45_AQ-INT-002_calendar-timeline-priority/00_thread.md)).

**Telegram — следующим capture adapter.** Личный чат 1:1 после revocable account linking; первый этап text/voice, медиа/links/forwarded content входят в target requirements, но будут позже. Each message persisted and acknowledged separately; processing begins on explicit `Готово`. Reply to a message in an open session continues it regardless of elapsed time; unthreaded message starts another session. Web Inbox shows unfinished sessions, and bot sends later processing outcome; voice `готово` is desired with safe fallback. UX пробный ([AQ-INT-003](baseline/04-open-questions.threads/42_AQ-INT-003_telegram-scope/00_thread.md)).

**MCP:** backend/API проектируется MCP-ready; небольшой optional remote MCP spike после базового API и Calendar flow. MCP не блокирует MVP и не гарантирует voice/tool support в каждом consumer-assistant ([AQ-INT-005](baseline/04-open-questions.threads/46_AQ-INT-005_assistant-integrations/00_thread.md)).

## 6. AI workflows / provider boundaries

Минимальный provider-neutral adapter для LLM text/structured outputs нормализует usage, errors и declared capabilities; модели/provider добавляются постепенно. Ключи остаются server-side, silent fallback к другой модели не допускается.

Workflow definitions — **user-owned versioned canonical data**; runtime/engine — backend. User workflow Draft → immutable Publish; system workflows versioned read-only. Trusted/versioned executors и least-privilege capability profiles являются отдельными объектами; Run фиксирует конкретные versions/bindings и overrides. MVP flow — linear steps + simple conditions; output contracts versioned. AI не переписывает молча пользовательские изменения. Run logs охватывают success/failure/canceled и указывают на inputs/results/proposals без копирования личного содержимого в логи.

**Первый продуктовый AI** ([AQ-AI-012](baseline/04-open-questions.threads/58_AQ-AI-012_ai-runtime-first-stage/00_thread.md), [PQ-019](baseline/04-open-questions.threads/57_PQ-019_digest-first-stage/00_thread.md)): только в Kotlin backend — два системных workflow в коде (извлечение данных из записи, недельный дайджест), параллельно E0 и первой версии; до этого — прототип ценности через внешнего ассистента без записи в дневник.

[AI workflow architecture](baseline/07-ai-workflow-architecture.md) · [AQ-AI-008 resolved editor UX](baseline/04-open-questions.threads/39_AQ-AI-008_workflow-editor-ux/00_thread.md)

**Открыты:** storage canonical AI run records vs operational DB, context assembly, prompt customization boundaries, sensitive-data/provider disclosure and consent, exact structured-output validation and repair policy (§11). Эти решения не следует незаметно заменять настройками конкретного провайдера.

## 7. Runtime, identity, operations

- **Runtime:** Google Cloud Run Service для backend/API, Cloud Run Jobs для run-to-completion задач, Cloud Scheduler для расписаний; конкретный durable queue mechanism ещё нужно спроектировать. Асинхронные задачи переживают закрытие браузера.
- **Environments:** одно развёрнутое рабочее окружение, локальный запуск по необходимости; отдельного постоянно развёрнутого staging пока нет.
- **Authentication:** stable internal user ID, Google login сначала; app authentication отделён от Google Drive/Calendar OAuth grant и токенов. Минимально необходимые permissions.
- **Security / хранение содержимого:** модель угроз и минимум защиты — [AQ-SEC-001](baseline/04-open-questions.threads/49_AQ-SEC-001_content-protection/00_thread.md) (PRIV-010…012). Долговременные копии содержимого (drafts, run records, debug-копии, proposals, routines, настройки) — в Drive пользователя в технической подпапке; на сервере только очередь команд, derived индекс и OAuth tokens. Облачное шифрование at rest + TLS, refresh tokens только в secret/KMS-хранилище, тест изоляции пользователей, тест отсутствия содержимого в логах.
- **Observability:** structured technical logs + run history с job/run/request identities, статусами и ошибками; без безусловного логирования raw diary/prompts/secrets.
- **Retries:** idempotent technical retries; unknown-outcome paid AI calls не повторять автоматически при cost-saving default.
- **Budget:** пользовательский monthly AI budget и warnings; при достижении лимита новые paid AI jobs не dispatch; queued jobs — `Ожидает бюджета`, видимы, отменяемы. По умолчанию возобновление вручную, opt-in auto resume. Это application guardrail, не гарантированный provider billing cap.
- **Recovery:** воспроизводимый backup/restore test по команде в изолированном месте, с проверкой canonical entries/revisions/assets/provenance и rebuild derived indices. Необходимые technical jobs восстанавливаются после рестарта.
- **CI/CD:** PR checks автоматические, deploy backend/web **по ручному действию**, secrets вне Git, документированный rollback ([AQ-OPS-005](baseline/04-open-questions.threads/40_AQ-OPS-005_ci-cd/00_thread.md)).

## 8. Search/indexing

Сначала canonical files/browse без обязательного search DB. Следующий этап — обычный title/body FTS + фильтры, используя derived index выбранной operational DB, без отдельного dedicated search server. После successful committed revision индекс обновляется асинхронно; примерно каждые 12 часов — incremental reconciliation, возможен full rebuild из canonical. Embeddings/semantic retrieval — вне MVP.

## 9. Проверки перед первым реальным использованием

**Результат статического аудита текущих Abacus scripts (08.11.2026):** [audits/2026-11-08-abacus-diary-scripts.md](audits/2026-11-08-abacus-diary-scripts.md). Найдены готовые Python модули для Calendar→Drive→Entry→Timeline и Telegram operator bot; код не выполнялся и состояние live Abacus не проверялось. Выявлены риск partial commits/duplicate Entries при retry, преждевременный move из Calendar Inbox и сканирование лишь первых N Entries в Timeline projection. Эти риски должны быть закрыты изолированными fixture/recovery tests до работы с реальными diary data.



- Durable Save и recovery после прерывания операции; не подтверждать Save до commit.
- Единственный писатель canonical-данных к первому mutating release — backend; до этого для Abacus-скриптов действуют временные операторские правила ([AQ-OPS-006](baseline/04-open-questions.threads/51_AQ-OPS-006_live-scripts-interim/00_thread.md)).
- Idempotent Calendar import, no duplicate Entries; сохранение raw/source metadata.
- Calendar Timeline обновляет тот же event и не изменяет canonical diary.
- История revisions, Restore, provenance, assets переживают backup/restore.
- Секреты, Google OAuth scopes, user isolation, отсутствие утечек содержимого в logs.
- Ограничение AI spending, видимость очередей, безопасные retries.
- Один воспроизводимый restore drill с отдельным хранилищем.
- Конкретные checks/deployment скрипты согласовать с фактическим кодом, а не считать существующими без проверки.

## 10. Scope и реализация

Полный план этапов с dependencies, acceptance criteria и учётом уже имеющихся Calendar→Drive scripts: [implementation-plan-web-mvp.md](implementation-plan-web-mvp.md).

Важная последовательность: **basic canonical backend / CaptureItem → ранние Calendar Inbox + read-only Calendar Timeline → минимальный web → полноценные revisions/edit/search → Telegram → AI workflows**. Отдельный ранний MCP spike допускается после появления basic API/Calendar path и не тормозит основные этапы. План — последовательность интеграционных проверок, не обещание, что текущий код соответствует ей.

## 11. Нерешённые вопросы (по source 04-open-questions.md на 2026-11-08)

**Web:** открытых вопросов нет (AQ-WEB-001…006 решены).

**AI (7):**
- [AQ-AI-003](baseline/04-open-questions.md#aq-ai-003--где-хранить-run-records) — где durable run records.
- [AQ-AI-004](baseline/04-open-questions.md#aq-ai-004--context-building) — context selection/assembly.
- [AQ-AI-005](baseline/04-open-questions.md#aq-ai-005--prompt-customization) — user overrides/user-defined prompts boundary.
- [AQ-AI-007](baseline/04-open-questions.md#aq-ai-007--structured-outputs--validation) — schema validation and repair.
- [AQ-AI-009](baseline/04-open-questions.md#aq-ai-009--навык-для-внешнего-ассистента-с-текущими-трекерами) — навык внешнего ассистента с текущими трекерами.
- [AQ-AI-010](baseline/04-open-questions.md#aq-ai-010--модель-трекеров-и-политика-вопросов) — модель трекеров и политика вопросов.
- [AQ-AI-011](baseline/04-open-questions.md#aq-ai-011--детали-дайджеста-и-детекции-эпизодов) — детали дайджеста и детекции эпизодов.

**Уже решены, не спрашивать заново:** AQ-WEB-001 (React + TS + Vite SPA), AQ-WEB-002 (паритет на телефоне по этапам), AQ-WEB-006 (обычный клиент, не Sites), AQ-WEB-003 Markdown editor, AQ-WEB-004 (SSE), AQ-WEB-005 (revision UX, E2), AQ-AI-006 (данные для внешнего AI), AQ-AI-008 workflow editor UX. Подробные требования находятся в source inventory/screens specs.

Не закрывать оставшиеся 7 вопросов AI без отдельного решения; не выдавать технические drafts file format/Save recovery за утверждённый release design.
