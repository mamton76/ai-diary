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
**Решение:** current Entry и History/Revisions разделены; AI mutation создаёт revision; manual editing session начинается с первой правки и фиксирует одну revision при Save или после 1 часа inactivity; autosave сам revision не создаёт; подряд идущие manual revisions группируются только в UI; история линейная без branches; Restore создаёт новую revision из старого snapshot и сохраняет provenance-ссылку на source revision.  
**История обсуждения:** [PQ-004 thread](04-open-questions.threads/04_PQ-004_raw-revisions-ux/00_thread.md)

Техническое хранение autosave/working draft вынесено в AQ-DATA-010.

## PQ-005 — Насколько AI автоматичен?

**Статус:** решён  
**Обсуждение:** [PQ-005 thread](04-open-questions.threads/05_PQ-005_ai-automation-policy/00_thread.md)

**Решение:** policy задаётся per workflow/type of change. Безопасные reversible изменения могут auto-apply, а изменения существующего содержимого через AI сначала оформляются как persistent proposal и становятся revision только после Accept/Apply. Первая normalized entry может создаваться автоматически при сохранённом raw; existing tags могут auto-apply при высокой уверенности; новые теги по умолчанию предлагаются. Точные thresholds и future metadata policies не блокируют MVP.


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

---

# 2. Data / storage вопросы

## AQ-DATA-001 — Files-only или files + derived DB/index?

Web UI нужен быстрый listing/filter/search.

Реалистичные варианты:

- прямое чтение Drive при небольшом объёме;
- in-memory/cache index;
- rebuildable server index;
- relational DB как derived projection;
- search-specific store;
- комбинация.

Ключевое ограничение: добавление operational index не должно молча менять ownership canonical data.

## AQ-DATA-002 — Гранулярность storage abstraction

Два полюса:

### Низкоуровневый

```text
listFiles
readFile
writeFile
moveFile
```

### Доменный

```text
listEntries
getEntry
saveRevision
listChanges
```

Текущее направление предпочитает domain-level API, но migration/import tools могут потребовать lower-level access.

## AQ-DATA-003 — Concurrency / optimistic locking

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

Если Drive/files canonical, как backend эффективно узнаёт про изменения?

Варианты:

- Drive Changes API;
- ETags/modified timestamps;
- derived sync/index state;
- MVP-ограничение: canonical writes только через backend;
- периодический reconciliation.

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

Google account — естественный first path.

Нужно решить, использовать ли:

- Firebase Auth;
- direct Google OIDC/OAuth;
- другой auth middleware.

## AQ-AUTH-002 — Drive/Calendar OAuth

Нужно определить:

- где хранится refresh token;
- какие scopes запрашиваются;
- incremental consent;
- token revocation;
- account switch;
- expired permissions;
- re-auth UX.

## AQ-AUTH-003 — Single-user vs multi-user readiness

Первый production может быть только для одного владельца.

Вопрос: стоит ли с первого дня иметь explicit `userId/ownerId` в domain/API, чтобы не делать болезненную миграцию позже.

## AQ-AUTH-004 — Доступ backend к user-owned Drive

Нужно решить модель:

- backend действует от имени пользователя по OAuth token;
- service account + shared folder;
- другой pattern.

Это сильно влияет на security и deployment.

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