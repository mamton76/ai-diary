# AI Diary — карта источников baseline

**Дата:** 2026-09-26

Этот документ перечисляет источники, использованные для построения baseline, и объясняет, какую роль каждый из них играет. Наличие источника здесь **не означает**, что все решения внутри него считаются актуальными.

---

# 1. GitHub-репозиторий `mamton76/ai-diary`

## `README.md`

Содержит старое/текущее repo-описание Android-first приложения, Kotlin/Compose stack, Room/Firebase направление и roadmap.

**Использовано для:**

- понимания исторического implementation state;
- выявления старых architectural assumptions;
- поиска доменных идей, которые могут быть переиспользованы.

**Не используется как:**

- авторитетная будущая архитектура.

## `docs/prd.md`

Содержит продуктовые требования старого Android/Firebase поколения: быстрый capture, entries, sync, AI enrichment, future phases и некоторые вертикали.

**Использовано для:**

- устойчивых продуктовых идей;
- core user flows;
- terminology;
- future feature candidates.

**Известный конфликт:**

- storage/backend assumptions отличаются от поздней file-first ветки.

## `docs/architecture.md`

Описывает Room/Firebase/Data Connect архитектурные поколения.

**Использовано для:**

- исторического сравнения;
- понимания того, какие решения уже пробовались.

**Статус:** legacy architecture.

## `docs/data-model-proposal.md`

Богатая relational/domain модель:

- Entry;
- EntryRevision;
- tags;
- assets;
- provenance;
- AI request/result/feedback;
- user AI context.

**Использовано для:**

- revisions/provenance;
- separation of lifecycle/AI review concerns;
- stable IDs;
- candidate domain concepts.

**Не используется как:**

- обязательная DB schema.

## `docs/todo.md`

Checklist реализации и roadmap.

**Использовано для:**

- примерного понимания того, что когда-то считалось реализованным.

**Ограничение:**

- checkbox сам по себе не доказывает, что функция сейчас реально работает end-to-end.

## `docs/agent-idea.md`

Описывает hybrid agent:

- deterministic workflow;
- LLM decision layer;
- context;
- rules;
- user control.

**Использовано для:**

- принципа «prompt != agent»;
- идеи разделения workflow и model reasoning;
- AI as assistant, not blocker.

---

# 2. File-first project documents

## `00_AIDiary_Project_Overview.md`

Один из наиболее важных поздних документов.

Определяет AI Diary как file-based personal diary на user-owned storage, с принципом:

> Capture first. Structure later.

Также фиксирует:

- raw preservation;
- Markdown + JSON;
- conservative agents;
- traceability;
- storage usability without DB.

**Вес в baseline:** высокий.

## `01_File_Storage_Structure.md`

Описывает portable folder structure:

- `_system`;
- `_formats`;
- `_prompts`;
- `_agents`;
- `_runs`;
- `inbox`;
- `entries`;
- `assets`;
- `catalogs`;
- `indexes`;
- migrations/backups/export.

**Использовано для:**

- portability;
- format versioning;
- prompts-as-files;
- derived indexes;
- storage abstraction direction;
- stable entry folders/IDs.

## `02_Workflow_Inbox_To_Entry.md`

Описывает переход raw/structured inbox material в entries.

Ключевые идеи:

- raw input сохраняется;
- один input может дать несколько entries;
- несколько inputs могут объединяться;
- uncertainty -> `needs_review`;
- traceable link from entry back to source;
- safe/manual debugging.

**Использовано для:**

- capture normalization boundary;
- provenance;
- review semantics;
- idempotency/reliability expectations.

## `03_Workflow_Tag_Enrichment.md`

Описывает conservative tag enrichment.

Ключевые идеи:

- reuse existing tags;
- не over-tag;
- proposal-only mode;
- reason/confidence;
- protection of user tags;
- soft tag types.

**Использовано для:**

- product behavior вокруг tagging.

## `04_Workflow_Google_Calendar_Inbox.md`

Описывает Google Calendar как voice-friendly external inbox/queue.

Ключевой принцип:

- Calendar не diary storage;
- Calendar adapter создаёт normalized inbox package;
- затем работает обычный Inbox-to-Entry;
- successfully processed event переводится в Processed calendar;
- retries не должны создавать duplicate entries.

**Использовано для:**

- Calendar capture role;
- adapter boundary;
- raw event preservation;
- duplicate resistance.

## `05_Workflow_Google_Calendar_Timeline_Projection.md`

Описывает отдельную pipeline:

```text
entries -> Google Calendar timeline
```

Ключевой принцип:

- diary files остаются source of truth;
- Calendar timeline — derived/rebuildable projection.

**Использовано для:**

- отделения capture Calendar от timeline Calendar;
- external sync state semantics.

## `01_File_Storage_Structure_with_calendar_projection.md`

Расширяет file structure integration-конфигами, индексами и run logs для Calendar projection.

**Использовано для:**

- подтверждения принципа derived integration state.

## `01_File_Storage_Structure_calendar_projection_relative_diff.md`

Показывает минимальные изменения, необходимые для Calendar projection, не меняя canonical entries.

**Использовано для:**

- подтверждения adapter/projection подхода.

---

# 3. Более старые project-документы

## `prd_updated.md`

Старый Firebase/cloud product baseline:

- mobile-first;
- fast capture;
- AI structuring;
- basic web;
- Firebase Data Connect/Storage.

**Использовано для:**

- product principles;
- non-functional requirements;
- historical feature ideas.

**Не считается актуальным автоматически в части:**

- Firebase as canonical storage;
- cloud-first assumptions.

## `architecture_updated.md`

Firebase Data Connect-centered architecture, basic web client, Drive как optional archive.

**Использовано для:**

- historical comparison only.

## `diary_market.md`

Конкурентный анализ AI journals, PKM, lifelogging и visual memory products.

Среди полезных направлений:

- «personal memory system»;
- privacy/user-control;
- voice-first trend;
- multimodal capture;
- personalized AI;
- visual exploration.

**Использовано как:**

- product framing;
- source of hypotheses;
- support for strategic positioning.

**Не используется как:**

- автоматический список обязательных features.

## `Используемые-в-проекте-репозитории.txt`

Фиксирует:

- основной AI Diary repo;
- ZoomAlboom repo;
- дополнительный OpenClaw reference.

---

# 4. Обсуждения, восстановленные из истории проекта

## 2026-04-25 — File-first storage и agent workflows

В обсуждениях формировались:

- Google Drive / local files как active storage;
- Markdown/JSON;
- preservation raw input;
- inbox -> entry;
- tag enrichment;
- простой tag `type` вместо сложной ранней ontology;
- debug-friendly workflows;
- storage portability;
- format migrations.

**Вклад в baseline:**

- основа file-first направления.

## 2026-04-26 — Calendar inbox и Calendar timeline

Обсуждались:

- Calendar voice capture;
- normalized inbox package;
- Processed calendar;
- duplicate prevention;
- separate diary -> Calendar timeline projection;
- files остаются canonical в этой ветке.

**Вклад в baseline:**

- разделение двух ролей Calendar.

## 2026-08-02 — Простой web UI к Drive entities

Обсуждались:

- read-only browser prototype;
- entry list/detail;
- date/status/tags;
- search/filter;
- mobile usability;
- осторожность с edit без revisions;
- Google Sites / Apps Script как shortcut.

**Вклад в baseline:**

- ранние web requirements;
- Google Sites признан не продуктовым требованием, а prototype option.

## 2026-08-28 — Voice capture experiments

Практически тестировались ChatGPT/Gemini сценарии.

Выводы:

- нужен естественный длинный voice capture;
- желательно explicit save boundary;
- нельзя полагаться на стабильный create-then-update во время partial dictation;
- Calendar удобен как capture adapter;
- конкретные voice capabilities ассистентов нестабильны и меняются.

**Вклад в baseline:**

- voice first-class requirement;
- assistant/vendor independence.

## 2026-09-26 — Новое web/backend/storage/LLM направление

Обсуждались:

- adaptive web desktop + phone;
- separate backend API;
- future native clients поверх того же API;
- replaceable storage abstraction;
- Google Drive как v1 storage backend;
- DB не считать обязательной заранее;
- cheap/simple hosting;
- Google auth/integration;
- Kotlin/Ktor vs Python/FastAPI vs TypeScript/Node;
- Cloud Run как кандидат;
- multi-provider LLM: OpenAI/Gemini/Claude;
- prompts/workflows как отдельный layer;
- AI subsystem перпендикулярна обычному diary UI;
- GitHub как место актуальной документации;
- requirements -> architecture -> ADR/issues/implementation;
- сначала собрать baseline, потом проектировать архитектуру.

**Вклад в baseline:**

- current direction имеет наивысший приоритет там, где оно явно заменяет старое решение.

---

# 5. Правило приоритета источников

Если источники конфликтуют, baseline использует следующий порядок интерпретации:

1. явные текущие решения пользователя из более поздних обсуждений;
2. более поздние file-first project-документы;
3. продуктовые принципы, повторяющиеся в нескольких поколениях;
4. старые PRD/domain-model идеи;
5. старые technology/architecture choices.

Это **не означает**, что новое автоматически лучше старого. Это только правило, которое не даёт устаревшему implementation choice незаметно победить более позднее explicit requirement.

---

# 6. Основные противоречия, которые baseline НЕ скрывает

## Противоречие A — canonical storage

### Старое поколение

Room/Firebase/Data Connect как центр persistence.

### Новое поколение

Files/Drive как durable canonical diary, derived indexes.

### Текущая трактовка

- portability/user ownership — подтверждено;
- file-canonical — рабочее направление;
- точная operational mechanics — архитектурный вопрос.

## Противоречие B — Android-first vs reusable API

### Старое поколение

Android — центр системы.

### Текущее направление

Web + backend API, native clients позже.

### Текущая трактовка

- web/API — current requirements;
- old Android — reuse candidate, не constraint.

## Противоречие C — роль Google Drive

### Старое поколение

Optional archive/backup/original storage.

### Новое направление

Первый active storage backend.

### Текущая трактовка

Для новой архитектуры Drive считается первым concrete backend, но storage abstraction обязательна.

## Противоречие D — Offline-first

### Старое поколение

Полный offline-first — core principle.

### Новое направление

Устойчивость к плохой сети обязательна, но full offline edit/sync ещё не подтверждён.

### Текущая трактовка

Full offline-first — открытый вопрос.

## Противоречие E — Обязательность DB

### Старое поколение

Relational DB assumed.

### Новое направление

Сначала требования, потом решение о DB.

### Текущая трактовка

DB — optional derived/operational layer, пока архитектура не докажет обратное.

## Противоречие F — AI как встроенная функция vs отдельная subsystem

### Старое поколение

AI чаще описывается как future feature внутри приложения.

### Новое направление

LLM layer — отдельная provider-independent subsystem с workflows/context/prompt versioning.

### Текущая трактовка

Отделение AI subsystem принято как более устойчивое направление.

---

# 7. Что в baseline сознательно не использовалось как источник истины

Не считались автоматически авторитетными:

- TODO checkbox;
- наличие старого класса в коде;
- название старой Firebase schema;
- выбранный когда-то framework;
- market-рекомендация;
- единичная гипотеза из разговора, если позже она была пересмотрена.

Baseline пытается восстановить **намерение продукта**, а не историю каждого commit.