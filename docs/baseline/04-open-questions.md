# AI Diary — открытые вопросы перед архитектурой

**Дата:** 2026-09-26  
**Назначение:** не дать нерешённым вопросам превратиться в неявные технические решения. Здесь собраны вопросы, которые нужно либо решить до архитектуры, либо явно принять как допущения первого архитектурного draft.

## Как ведём обсуждения

Этот файл остаётся обзором **текущих открытых вопросов**. Длинная аргументация не накапливается прямо здесь.

Когда конкретный пункт начинает обсуждаться, рядом создаётся канонический файловый тред:

```text
04-open-questions.threads/
  NN_<QUESTION-ID>_<slug>/
    00_thread.md
```

Если вопрос раскалывается на самостоятельные подрешения, внутри его папки можно создавать дочерние узлы. Пустые треды для всех вопросов заранее не создаются.

В самом пункте этого документа при появлении треда добавляется ссылка вида:

```markdown
**Обсуждение:** [тред](04-open-questions.threads/01_PQ-001_source-of-truth/00_thread.md)
```

После принятия решения:

1. тред сохраняет историю аргументов и пересмотров;
2. этот пункт получает статус и краткий итог;
3. принятое требование/ограничение переносится в соответствующий product/requirements/architecture source-документ;
4. ссылка на тред остаётся как decision history.

Индекс активных обсуждений: [`04-open-questions.threads/00_index.md`](04-open-questions.threads/00_index.md).

Правила ведения тредов: [`skills/discussion-threads/SKILL.md`](../../skills/discussion-threads/SKILL.md).

---

# 1. Продуктовые вопросы

## PQ-001 — Что именно считается canonical source of truth?

**Статус:** РЕШЕНО  
**Решение:** user-owned portable files являются canonical source of truth. Operational DB/index/cache допустимы как rebuildable derived layers и не должны содержать единственную копию существенных diary data.  
**История обсуждения:** [PQ-001 thread](04-open-questions.threads/01_PQ-001_source-of-truth/00_thread.md)

Manual Drive edits, conflict UX и конкретный механизм optimistic concurrency остаются отдельными data/architecture вопросами и не меняют этот продуктовый принцип.

## PQ-002 — Насколько обязателен full offline-first?

**Статус:** РЕШЕНО  
**Решение:** первый web/backend MVP — online-first. Full offline browsing/editing и conflict-aware offline sync откладываются. Уже введённый текст/capture не должен тихо теряться при кратковременной потере сети; safe retry и видимые failures обязательны. Архитектура не должна блокировать будущий offline-capable native/mobile client.  
**История обсуждения:** [PQ-002 thread](04-open-questions.threads/03_PQ-002_offline-first/00_thread.md)
**Будущее:** [FQ-OFFLINE-001 — full offline editing и version sync](06-future-questions.md#fq-offline-001--full-offline-editing-и-синхронизация-версий)


## PQ-003 — Какой minimum viable web?

**Статус:** РЕШЕНО  
**Решение:** первый полезный web slice работает с существующими entries: browse/list, read и search/filter по тексту, дате/date range и tags. Следующий этап — editing + versioning/history, затем tags view/edit, затем AI processing/workflows. Web-create не обязателен для первых этапов и может быть добавлен opportunistically, если почти не увеличивает scope.  
**История обсуждения:** [PQ-003 thread](04-open-questions.threads/02_PQ-003_minimum-viable-web/00_thread.md)

## PQ-004 — Нужно ли сразу показывать raw/revisions пользователю?

**Статус:** РЕШЕНО  
**Решение:** current Entry и History/Revisions разделены; AI proposal до Apply не является revision; применённая AI mutation создаёт отдельную revision; manual editing session начинается с первой правки и фиксирует одну revision при Save или после 1 часа inactivity; autosave сам revision не создаёт; подряд идущие manual revisions группируются только в UI; committed revisions immutable/append-only, история линейная без branches; Restore/Undo создаёт новую revision с provenance и не удаляет прежнюю историю.  
**История обсуждения:** [PQ-004 thread](04-open-questions.threads/04_PQ-004_raw-revisions-ux/00_thread.md)  
**Будущее:** [FQ-REVISION-002 — revision history compaction / retention](06-future-questions.md#fq-revision-002--revision-history-compaction--retention)

Техническое хранение autosave/working draft вынесено в AQ-DATA-010.

## PQ-005 — Насколько AI автоматичен?

**Статус:** решён  
**Обсуждение:** [PQ-005 thread](04-open-questions.threads/05_PQ-005_ai-automation-policy/00_thread.md)

**Решение:** policy задаётся per workflow/type of change. Безопасные reversible изменения могут auto-apply, а изменения существующего содержимого через AI сначала оформляются как persistent proposal и становятся revision только после Accept/Apply. Первая normalized entry может создаваться автоматически при сохранённом raw; existing tags могут auto-apply при высокой уверенности; новые теги по умолчанию предлагаются. Один AIResult может дать один или несколько proposals, а proposal может быть простым или комплексным — гранулярность задаёт workflow. Бесконфликтный proposal имеет быстрый Apply/Reject; stale/conflicted proposal требует detailed review. Detailed review использует `Base | editable Result | Proposal`, auto-merges независимые изменения и позволяет локально разрешать conflicts; подтверждение создаёт одну новую revision. Entry должен позволять drill-down в полную AI activity/run provenance. Точные thresholds и future metadata policies не блокируют MVP.


## PQ-006 — Насколько пользователь выбирает LLM provider/model?

**Статус:** решён  
**Обсуждение:** [PQ-006 thread](04-open-questions.threads/07_PQ-006_llm-provider-model-choice/00_thread.md)

**Решение:** пользователь выбирает LLM model, а provider определяется выбранной моделью. Иерархия: task/run override → workflow preference → global user preference → system default. Global preference — основной пользовательский сценарий. Если preferred model недоступна, система не должна молча переключаться на другую модель/provider без явного согласия пользователя. Детали retry/deprecation/fallback UX относятся к implementation policy.


## PQ-007 — Sharing входит в обозримый MVP?

**Статус:** решён  
**Обсуждение:** [PQ-007 thread](04-open-questions.threads/08_PQ-007_sharing-mvp/00_thread.md)  
**Future:** [FQ-SHARING-001 — Selective sharing](06-future-questions.md#fq-sharing-001--selective-sharing)

**Решение:** sharing не входит в обозримый MVP и не должен сейчас определять auth/data model. Сохраняется как future requirement.


## PQ-008 — Какова судьба старого Android-приложения?

**Статус:** решён  
**Обсуждение:** [PQ-008 thread](04-open-questions.threads/10_PQ-008_android-legacy/00_thread.md)

**Решение:** старый Android/Firebase codebase остаётся historical prototype/reference и не развивается в текущем цикле. Новая web/backend архитектура не должна от него зависеть; отдельные идеи можно переиспользовать opportunistically. К native Android возвращаемся позже при реальной потребности, в частности вместе с offline-first. Уникальных ценных данных в старом Firebase/Room, требующих отдельной миграции, нет; migration tooling сейчас не нужен.


## PQ-009 — Нужен ли Calendar inbox как постоянная production feature?

**Статус:** решён  
**Обсуждение:** [PQ-009 thread](04-open-questions.threads/09_PQ-009_calendar-inbox-role/00_thread.md)

**Решение:** Calendar inbox остаётся optional production transport/adapter и не является core dependency. Calendar timeline — отдельная derived one-way projection: одна diary entry соответствует одному Calendar event; при новой committed revision/current-state change существующий event обновляется, а отдельные events для каждой revision не создаются.


## PQ-011 — Как устроен Entry detail/edit и переиспользуемый EntryPanel?

**Статус:** ОБСУЖДАЕМ  
**Обсуждение:** [PQ-011 thread](04-open-questions.threads/17_PQ-011_entry-detail-editor/00_thread.md)

Нужно зафиксировать состав переиспользуемого представления одного Entry state и границу между ним и surrounding EntryScreen, чтобы один и тот же content component работал в обычном view, manual edit и proposal merge.

Уже согласовано: EntryPanel показывает Title, Event date + optional start/end, Text, Assets, Tags и вторичные created/updated timestamps; в edit mode соответствующие поля становятся редактируемыми, а у Tags/Assets появляются add/remove actions. EntryScreen отдельно содержит Proposals, History/Revisions, Sources/Lineage, AI activity/details и screen-level actions. Layout/order секций ещё обсуждается.

---

# 2. Data / storage вопросы

## AQ-DATA-001 — Files-only или files + derived DB/index?

**Статус:** решён  
**Обсуждение:** [AQ-DATA-001 thread](04-open-questions.threads/15_AQ-DATA-001_files-vs-derived-index/00_thread.md)

**Решение:** первый MVP работает files-only через отдельный data layer/repository abstraction; database и полноценный search на старте не обязательны. Архитектура должна позволять позже добавить rebuildable derived index для listing/filter/search/performance. Canonical diary content и revisions остаются в user-owned storage; server-side DB не должна становиться их второй durable копией. Operational state может содержать приватные данные только там, где это необходимо. Privacy policy будущего search index определяется отдельно.


## AQ-DATA-002 — Гранулярность storage abstraction

**Статус:** решён  
**Обсуждение:** [AQ-DATA-002 thread](04-open-questions.threads/18_AQ-DATA-002_storage-abstraction/00_thread.md)

**Решение:** основной application/domain слой использует высокоуровневый domain repository в терминах `Entry`, `Revision`, history/listing и других diary concepts (`listEntries/getEntry/saveRevision/loadHistory` и т. п.). Drive/files operations скрыты в нижнем storage adapter и не должны протекать в основной domain logic. Прямой low-level file access допустим для migration/import/repair/admin tooling.


## AQ-DATA-003 — Concurrency / optimistic locking

**Обсуждение:** [AQ-DATA-003 thread](04-open-questions.threads/16_AQ-DATA-003_concurrency-locking/00_thread.md)

Что происходит, если:

- две browser tabs редактируют одну entry;
- web и Android меняют её одновременно;
- пользователь вручную меняет `entry.md` в Drive;
- AI создаёт proposal, пока пользователь пишет;
- background import обновляет related metadata.

Возможные механизмы:

- revision IDs;
- ETag/version tokens;
- append-only revisions;
- compare-and-swap;
- explicit conflict UI.

## AQ-DATA-004 — Change detection

**Статус:** решён  
**Обсуждение:** [AQ-DATA-004 thread](04-open-questions.threads/19_AQ-DATA-004_change-detection/00_thread.md)

**Решение:** на update существующей canonical entry backend выполняет cheap storage metadata/version check. Если обнаружено валидное содержательное внешнее изменение, оно фиксируется как новая immutable revision с provenance, после чего pending change проходит rebase/merge/conflict относительно нового current state. Silent overwrite недопустим. Если изменился только metadata marker без content change, revision не создаётся. Invalid/unparseable external state уходит в review/recovery path. Постоянный Drive watcher в первом MVP не обязателен; opportunistic check при read/update достаточен. Текущие Calendar/Telegram/file-based workflows могут мигрировать к общему backend/capture boundary постепенно.


## AQ-DATA-005 — Asset storage

Где хранятся originals:

- в том же Drive/file backend;
- object storage;
- hybrid.

Нужно учитывать:

- размер;
- previews/thumbnails;
- streaming;
- portability;
- backup;
- cost.

## AQ-DATA-006 — Format schema и migrations

Нужно определить:

- format version granularity;
- migration runner;
- backward compatibility;
- backup before migration;
- validation;
- возможность rebuild derived indexes после migration.

## AQ-DATA-007 — Нужно ли позволять пользователю вручную редактировать canonical files?

File-first ценность подразумевает inspectability, но manual editing резко усложняет:

- schema validation;
- conflict handling;
- change detection.

Можно различать:

- readable/exportable files;
- officially supported manual editing.

## AQ-DATA-008 — Migration со старого Firebase/Room

Сначала нужно выяснить:

- есть ли там реальные уникальные пользовательские данные;
- это test/prototype data или ценный diary history;
- что нельзя восстановить из Drive.

Только после этого решать, нужен ли migration tooling.


## AQ-DATA-009 — Какая именно модель core data synchronization нужна?

Требование к синхронизации теперь считаем явным: разные клиенты должны работать с одним логическим дневником без тихой потери изменений.

Архитектуре нужно выбрать topology/authority model, например:

- clients -> backend -> canonical files;
- clients -> backend -> operational DB -> canonical file projection;
- clients/backend напрямую синхронизируются с file storage через version tokens;
- hybrid с локальным cache и reconciliation.

Нужно отдельно определить:

- кто авторитетен при конфликте;
- какой version/revision token участвует в compare-and-swap;
- как обнаруживаются external/manual Drive edits;
- какую consistency ожидаем между canonical storage и derived indexes;
- какие операции должны работать offline;
- как выполняются retry/idempotency и duplicate prevention.

Важно не смешивать core diary sync с Calendar projection, capture queue и backup/export — это разные sync contracts.


## AQ-DATA-010 — Как хранить autosave / working state незавершённой editing session?

**Статус:** РЕШЕНО  
**Решение:** один server-side current working draft хранится в operational state; локально клиент держит bounded recovery snapshots. Canonical revisions и operational draft семантически разделены, хотя физически могут жить в одном storage на MVP. Для manual editing используется soft lease с одним active editor и безопасным takeover между sessions. AI mutations используют mutation lease, могут ждать в очереди, уступают ручному редактированию и при устаревшем base state проходят compatibility/revalidation. MVP-defaults: до 5 local snapshots, не более 30 секунд между recovery points, retention 24 часа после successful revision, auto-revision после 1 часа inactivity. Server draft очищается после successful revision; при failed commit сохраняется. Draft sync: debounce + guaranteed flush, точные интервалы configurable.  
**История обсуждения:** [AQ-DATA-010 thread](04-open-questions.threads/04_1_AQ-DATA-010_autosave-working-state/00_thread.md)


---

# 3. Backend / API вопросы

## AQ-API-001 — Язык/framework backend

Кандидаты, обсуждавшиеся сейчас:

- Kotlin/Ktor;
- Python/FastAPI;
- TypeScript/Node.

Критерии сравнения:

- насколько удобно владельцу читать и исправлять код;
- качество AI-generated implementation;
- Google API ecosystem;
- background/async jobs;
- type safety;
- testability;
- library maturity;
- deployment simplicity;
- долгосрочное сопровождение.

## AQ-API-002 — Hosting/runtime

Cloud Run выглядит сильным кандидатом благодаря container model и scale-to-zero.

Но нужно сравнить реальную потребность с альтернативами по:

- стоимости;
- cold starts;
- background execution;
- scheduler/queue integration;
- Google OAuth/Drive convenience;
- logs;
- deployment complexity.

## AQ-API-003 — API style

REST выглядит простым default, но нужно определить:

- endpoint/resource model;
- versioning;
- pagination;
- errors;
- optimistic concurrency fields;
- long-running job semantics;
- download/upload semantics;
- auth scheme.

## AQ-API-004 — Background processing

Нужно выполнять:

- capture normalization;
- indexing;
- Calendar sync;
- AI workflows;
- migrations/backfills;
- retries.

Варианты:

- inline execution;
- queue/jobs;
- scheduler;
- Cloud Run jobs;
- external agent runner;
- комбинация.

## AQ-API-005 — Dev/staging/prod

Минимум вероятны:

- local/dev;
- personal production.

Нужно понять, нужен ли staging или он только усложнит личный проект.

## AQ-API-006 — Monorepo структура

Репозиторий может содержать:

```text
android/
web/
backend/
docs/
```

Но нужно решить:

- один Gradle root или независимые builds;
- где frontend package manager;
- shared schemas/types;
- CI boundaries;
- release versioning.

Это не повод делить продукт на несколько repo заранее.

---

# 4. Web frontend вопросы

## AQ-WEB-001 — Frontend stack

React/TypeScript — кандидат, не решение.

Критерии:

- responsive/adaptive UI;
- ecosystem;
- Markdown/editor support;
- auth integration;
- AI-agent coding quality;
- testing;
- deployment;
- maintainability.

## AQ-WEB-002 — Feature parity на телефоне

Нужно точно определить обязательный mobile web scope.

Вероятно обязательно:

- browse;
- read;
- capture/create;
- basic edit;
- search/filter.

Можно оставить desktop-first:

- revision diff;
- bulk operations;
- complex AI workflow configuration;
- debugging/admin.

## AQ-WEB-003 — Editor semantics

Варианты:

- textarea;
- Markdown editor;
- rich text с сериализацией в Markdown;
- structured block editor.

Продуктовое требование склоняет к durable human-readable representation, но UX не обязан выглядеть как сырой Markdown.

## AQ-WEB-004 — Live updates

Нужны ли:

- WebSocket/SSE/push;
- polling;
- manual refresh;
- обновление после завершения background job.

Для MVP real-time может быть излишним.

## AQ-WEB-005 — Работа с revisions

Нужно решить первый UX:

- просто history list;
- diff;
- restore old revision;
- compare AI proposal;
- merge conflict screen.


## AQ-WEB-006 — ChatGPT Sites или обычный web-проект?

ChatGPT Sites можно рассмотреть как быстрый способ собрать и захостить первый интерактивный web-прототип AI Diary.

Нужно отдельно решить, какую роль Sites играет в проекте:

- только disposable UX prototype на mock/demo data;
- ранний настоящий frontend поверх отдельного AI Diary backend API;
- внутренний/admin/debug UI;
- полноценный production frontend;
- не использовать и сразу развивать обычный web-клиент в репозитории.

Критерии сравнения:

- возможность работать с нашим отдельным backend API и live data;
- Google OAuth / Drive / Calendar integration;
- versioning и data synchronization;
- background jobs и long-running AI workflows;
- source-code ownership и GitHub workflow;
- testability;
- portability между hosting providers;
- custom domain/deployment;
- ограничения публичной beta;
- работа с sensitive diary data;
- насколько легко ChatGPT/Codex и Claude Code могут совместно поддерживать один и тот же код.

Рабочая гипотеза на 2026-09-26: Sites хорошо подходит для быстрого UI/UX prototype или лёгкого приложения, но не следует автоматически выбирать его production runtime для AI Diary до проверки перечисленных ограничений.

---

# 5. Authentication / Authorization

## AQ-AUTH-001 — Identity model

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-001 thread](04-open-questions.threads/12_AQ-AUTH-001_identity-model/00_thread.md)

**Решение:** AI Diary использует собственный stable internal user/account ID, независимый от конкретного login provider. Google — первый login method для MVP, но external identities должны привязываться к internal user отдельно, чтобы позже можно было добавить другие способы входа без миграции основной user model. Конкретный auth service/framework сейчас не фиксируется и выбирается вместе с backend/hosting.


## AQ-AUTH-002 — Drive/Calendar OAuth

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-002 thread](04-open-questions.threads/14_AQ-AUTH-002_google-oauth/00_thread.md)

**Решение:** Google API permissions выдаются incremental/per-feature: login отдельно, Drive consent при подключении diary storage, Calendar consent только при включении Calendar features. Предпочтение — минимально необходимые permissions и отсутствие full-Drive access, если это реализуемо разумно. Точные scopes, folder access mechanics, refresh-token storage, revocation, account switch и re-auth UX относятся к implementation/security details и не блокируют MVP.


## AQ-AUTH-003 — Single-user vs multi-user readiness

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-003 thread](04-open-questions.threads/11_AQ-AUTH-003_multi-user-readiness/00_thread.md)

**Решение:** AI Diary с самого начала считается multi-user application: один backend/application может обслуживать нескольких авторизованных пользователей, у каждого свой логический дневник и изолированные данные. Shared operational/server-side state должен быть user-scoped. При user-owned canonical storage explicit ownerId не обязан дублироваться внутри каждого diary file. Sharing/ACL между пользователями остаются отдельной future feature и не входят в MVP.

## AQ-AUTH-004 — Доступ backend к user-owned Drive

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-004 thread](04-open-questions.threads/13_AQ-AUTH-004_drive-access/00_thread.md)

**Решение:** backend получает доступ к Google Drive каждого пользователя через OAuth и действует от имени этого пользователя. Service account + shared folder не является основным access pattern для multi-user приложения. Детали scopes, refresh-token storage, revocation и re-auth определяются отдельно в AQ-AUTH-002.


---

# 6. AI subsystem вопросы

## AQ-AI-001 — Provider adapter contract

Нужен общий интерфейс, но нельзя потерять полезные provider-specific capabilities.

Нужно определить common denominator и extension mechanism.

## AQ-AI-002 — Где живёт workflow definition

Возможный split:

- code-defined orchestration;
- versioned prompts/config;
- user instructions;
- output schema;
- validators;
- tools.

Нужно решить, что принадлежит repo/code, а что user diary data/config.

## AQ-AI-003 — Где хранить run records

Потенциальные поля:

- workflow/version;
- prompt/version;
- provider/model;
- input references/snapshot;
- parameters;
- output;
- validation;
- timing;
- token/cost;
- user review/apply state.

Вопрос: canonical file, operational DB, оба слоя?

## AQ-AI-004 — Context building

Как workflow выбирает материал дневника:

- date range;
- tags;
- explicit selected entries;
- recent context;
- semantic retrieval;
- long-term AI memory.

Provider должен получать уже подготовленный context, а не сам лазить по storage.

## AQ-AI-005 — Prompt customization

Варианты:

- только developer prompts;
- user overrides;
- user-created prompts;
- full custom workflows.

Вероятен гибрид, но нужна permission/versioning model.

## AQ-AI-006 — Sensitive-data policy

До полноценного multi-provider AI нужно определить:

- что можно отправлять provider;
- надо ли подтверждение;
- как показывается provider;
- можно ли запретить отдельному workflow external AI;
- retention/logging policy.

## AQ-AI-007 — Structured outputs / validation

Для workflows, которые меняют metadata, желательно использовать schema validation.

Нужно определить:

- JSON schema/Pydantic/Kotlin model и т. п.;
- retry/repair;
- invalid output handling;
- user review.

---

# 7. Integrations / Calendar / Telegram

## AQ-INT-001 — Calendar inbox priority

Оставляем production feature или считаем transition adapter?

## AQ-INT-002 — Calendar timeline priority

Полезная derived feature, но вероятно не critical path для новой web/backend архитектуры.

## AQ-INT-003 — Telegram scope

Какие inputs поддержать сначала:

- text;
- voice;
- photo;
- links;
- forwarded files;
- multi-message session.

## AQ-INT-004 — Unified CaptureItem contract

Нужно формализовать один normalized input, чтобы каждый adapter не знал final persistence schema.

## AQ-INT-005 — Assistant-specific integrations

Если ChatGPT/Gemini/другие ассистенты умеют напрямую писать в Calendar или API, нужно решить, считать ли это официальным integration path или просто удобным external capture mechanism.

---

# 8. Search / Indexing

## AQ-SEARCH-001 — MVP search semantics

Минимум определить поддержку:

- title/body substring/full-text;
- tags;
- date range;
- source;
- status.

## AQ-SEARCH-002 — Semantic search timing

Cross-entry AI почти наверняка со временем потребует semantic retrieval, но можно оставить extension point и не тащить vector DB в MVP.

## AQ-SEARCH-003 — Rebuild semantics

Если index derived, должен существовать способ:

- удалить его;
- пересобрать из canonical data;
- проверить consistency.

---

# 9. Reliability / Observability / Operations

## AQ-OPS-001 — Минимальный run log

Что обязаны хранить capture, sync и AI workflows?

Нужно найти баланс между debuggability и лишним объёмом sensitive data.

## AQ-OPS-002 — Retry/idempotency contract

Каждый external/background workflow должен определять:

- deterministic source identity;
- safe retry;
- partial failure behavior;
- duplicate prevention.

## AQ-OPS-003 — Backup и restore test

Недостаточно иметь кнопку «backup».

Нужно в будущем проверить сценарий:

1. потерять derived state;
2. взять canonical storage/backup;
3. восстановить indexes;
4. открыть entries в UI;
5. убедиться, что provenance/revisions сохранились.

## AQ-OPS-004 — Cost guardrails

Нужны разумные лимиты/наблюдение для:

- hosting;
- storage;
- LLM;
- logs;
- network egress.

## AQ-OPS-005 — CI/CD

Нужно решить:

- что тестируется на PR;
- как deploy backend/web;
- нужен ли manual approval;
- как хранить secrets;
- как rollback.

---

# 10. Вопросы, которые НЕ должны блокировать первый архитектурный draft

Можно оставить placeholders для:

- финального sharing model;
- advanced AI memory;
- provider comparison UI;
- ZoomAlboom-specific export format;
- semantic search implementation;
- сложной people/place ontology;
- full media processing;
- real-time collaboration;
- on-device LLM;
- полноценного Android migration plan.

Перед сравнением архитектур обязательно должны быть **решены или явно приняты как assumptions** следующие пункты:

1. canonical data direction;
2. роль Drive/files;
3. required web capabilities;
4. отдельный backend API;
5. capture normalization boundary;
6. revision/provenance guarantees;
7. full offline-first: да/нет/позже;
8. auth + Google integration model на высоком уровне;
9. multi-provider LLM requirement;
10. отношение к старому Android/Firebase implementation;
11. ожидаемый single-user/multi-user horizon;
12. допустимая operational complexity/cost.