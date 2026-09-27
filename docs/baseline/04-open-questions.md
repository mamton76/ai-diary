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

<details>
<summary>Нужно было решить, что считать canonical source of truth: user-owned files, operational storage или hybrid, не потеряв web/multi-device/search возможности.</summary>

Наиболее сильное новое направление — user-owned file-based diary, где canonical content хранится в переносимом формате, а индексы/БД — derived.

Но архитектуре нужно проверить, насколько это совместимо с:

- web editing;
- multi-device;
- concurrency;
- search;
- background jobs;
- manual Drive edits.

Нужно выбрать формулировку уровня продукта:

- files — канонический источник;
- files — канонический пользовательский export, а operational source иной;
- hybrid с чётко определённым ownership.

</details>

**Статус:** РЕШЕНО  
**Решение:** user-owned portable files являются canonical source of truth. Operational DB/index/cache допустимы как rebuildable derived layers и не должны содержать единственную копию существенных diary data.  
**История обсуждения:** [PQ-001 thread](04-open-questions.threads/01_PQ-001_source-of-truth/00_thread.md)

Manual Drive edits, conflict UX и конкретный механизм optimistic concurrency остаются отдельными data/architecture вопросами и не меняют этот продуктовый принцип.

## PQ-002 — Насколько обязателен full offline-first?

<details>
<summary>Нужно было определить, обязателен ли full offline-first для нового web/backend MVP или достаточно online-first с защитой от потери capture при сбоях связи.</summary>

Старый Android проект делал offline-first центральным принципом.

В новых обсуждениях точно требуется:

- не терять capture при плохой сети;
- быть устойчивым к временным сбоям;
- не зависеть от постоянной идеальной connectivity.

Но пока не подтверждено, что новый web/backend MVP должен полностью редактироваться offline с последующим conflict-aware sync.

</details>

**Статус:** РЕШЕНО  
**Решение:** первый web/backend MVP — online-first. Full offline browsing/editing и conflict-aware offline sync откладываются. Уже введённый текст/capture не должен тихо теряться при кратковременной потере сети; safe retry и видимые failures обязательны. Архитектура не должна блокировать будущий offline-capable native/mobile client.  
**История обсуждения:** [PQ-002 thread](04-open-questions.threads/03_PQ-002_offline-first/00_thread.md)
**Будущее:** [FQ-OFFLINE-001 — full offline editing и version sync](06-future-questions.md#fq-offline-001--full-offline-editing-и-синхронизация-версий)


## PQ-003 — Какой minimum viable web?

<details>
<summary>Нужно было определить минимальный первый web slice: какие из browse/read/create/edit/search/tags/history обязательны сразу, а что можно перенести на следующий этап.</summary>

Нужно утвердить точный минимум первой полезной web-версии.

Предварительно:

- login;
- list/timeline;
- read;
- create;
- edit;
- search/filter;
- tags;
- basic revision/history visibility.

Вопрос: какие из этих пунктов обязательны в первом работающем slice, а какие во втором?

</details>

**Статус:** РЕШЕНО  
**Решение:** первый полезный web slice работает с существующими entries: browse/list, read и search/filter по тексту, дате/date range и tags. Следующий этап — editing + versioning/history, затем tags view/edit, затем AI processing/workflows. Web-create не обязателен для первых этапов и может быть добавлен opportunistically, если почти не увеличивает scope.  
**История обсуждения:** [PQ-003 thread](04-open-questions.threads/02_PQ-003_minimum-viable-web/00_thread.md)

## PQ-004 — Нужно ли сразу показывать raw/revisions пользователю?

<details>
<summary>Нужно было решить, как показывать raw и revision history: всегда, через History/Details или только в специальных сценариях вроде conflict/AI proposal.</summary>

Продукт требует их сохранять. UX может:

- показывать их всегда;
- прятать под History/Details;
- показывать только при конфликте/AI proposal.

</details>

**Статус:** РЕШЕНО  
**Решение:** current Entry остаётся главным состоянием, а History/Revisions показывается под ней как компактная scrollable gallery/timeline с drill-down в read-only comparison `previous revision | selected revision`; AI proposal до Apply не является revision; применённая AI mutation создаёт отдельную revision; manual editing session начинается с первой правки и фиксирует одну revision при Save или после 1 часа inactivity; autosave сам revision не создаёт; подряд идущие manual revisions могут группироваться только в UI; committed revisions immutable/append-only, история линейная без branches; Restore/Undo создаёт новую revision с provenance и не удаляет прежнюю историю.  
**История обсуждения:** [PQ-004 thread](04-open-questions.threads/04_PQ-004_raw-revisions-ux/00_thread.md)  
**Будущее:** [FQ-REVISION-002 — revision history compaction / retention](06-future-questions.md#fq-revision-002--revision-history-compaction--retention)

Техническое хранение autosave/working draft вынесено в AQ-DATA-010.

## PQ-005 — Насколько AI автоматичен?

<details>
<summary>Нужно было выбрать policy AI automation: suggestion-only, auto-apply, user confirmation или разные правила per workflow/type of change.</summary>

Для разных workflows можно выбрать разные policies:

- suggestion only;
- auto-apply metadata;
- user confirmation;
- auto-apply при confidence threshold.

Нужна общая policy или per-workflow policy.

</details>

**Статус:** решён  
**Обсуждение:** [PQ-005 thread](04-open-questions.threads/05_PQ-005_ai-automation-policy/00_thread.md)

**Решение:** policy задаётся per workflow/type of change. Безопасные reversible изменения могут auto-apply, а изменения существующего содержимого через AI сначала оформляются как persistent proposal и становятся revision только после Accept/Apply. Первая normalized entry может создаваться автоматически при сохранённом raw; existing tags могут auto-apply при высокой уверенности; новые теги по умолчанию предлагаются. Один AIResult может дать один или несколько proposals, а proposal может быть простым или комплексным — гранулярность задаёт workflow. Бесконфликтный proposal имеет быстрый Apply/Reject; stale/conflicted proposal требует detailed review. Detailed review использует `Base | editable Result | Proposal`, auto-merges независимые изменения и позволяет локально разрешать conflicts; подтверждение создаёт одну новую revision. Entry должен позволять drill-down в полную AI activity/run provenance. Точные thresholds и future metadata policies не блокируют MVP.


## PQ-006 — Насколько пользователь выбирает LLM provider/model?

<details>
<summary>Нужно было решить, насколько пользователь управляет LLM model/provider: global preference, per-workflow override, автоматический выбор или compare mode.</summary>

Варианты UX:

- система выбирает сама;
- один global preferred provider/model;
- выбор per workflow;
- advanced compare mode.

Архитектурно multi-provider поддержка желательна независимо от того, насколько эта настройка видима пользователю.

</details>

**Статус:** решён  
**Обсуждение:** [PQ-006 thread](04-open-questions.threads/07_PQ-006_llm-provider-model-choice/00_thread.md)

**Решение:** пользователь выбирает LLM model, а provider определяется выбранной моделью. Иерархия: task/run override → workflow preference → global user preference → system default. Global preference — основной пользовательский сценарий. Если preferred model недоступна, система не должна молча переключаться на другую модель/provider без явного согласия пользователя. Детали retry/deprecation/fallback UX относятся к implementation policy.


## PQ-007 — Sharing входит в обозримый MVP?

<details>
<summary>Нужно было понять, входит ли sharing в обозримый MVP и должен ли он уже сейчас влиять на auth/data model.</summary>

Ранее sharing рассматривался как полезный retention/family механизм.

Нужно определить:

- out of scope;
- future requirement;
- near-term requirement, влияющий уже сейчас на auth/data model.

</details>

**Статус:** решён  
**Обсуждение:** [PQ-007 thread](04-open-questions.threads/08_PQ-007_sharing-mvp/00_thread.md)  
**Future:** [FQ-SHARING-001 — Selective sharing](06-future-questions.md#fq-sharing-001--selective-sharing)

**Решение:** sharing не входит в обозримый MVP и не должен сейчас определять auth/data model. Сохраняется как future requirement.


## PQ-008 — Какова судьба старого Android-приложения?

<details>
<summary>Нужно было решить судьбу старого Android/Firebase приложения: развивать, мигрировать, переиспользовать части или оставить только как historical prototype.</summary>

Варианты:

- оставить как исторический prototype;
- сохранить доменные куски;
- превратить позже в native client нового API;
- мигрировать постепенно;
- отказаться от кода, но сохранить идеи.

Этот вопрос можно решить после лёгкого code audit и не блокировать первую архитектуру web/backend.

</details>

**Статус:** решён  
**Обсуждение:** [PQ-008 thread](04-open-questions.threads/10_PQ-008_android-legacy/00_thread.md)

**Решение:** старый Android/Firebase codebase остаётся historical prototype/reference и не развивается в текущем цикле. Новая web/backend архитектура не должна от него зависеть; отдельные идеи можно переиспользовать opportunistically. К native Android возвращаемся позже при реальной потребности, в частности вместе с offline-first. Уникальных ценных данных в старом Firebase/Room, требующих отдельной миграции, нет; migration tooling сейчас не нужен.


## PQ-009 — Нужен ли Calendar inbox как постоянная production feature?

<details>
<summary>Нужно было понять, является ли Calendar inbox постоянной production-интеграцией или лишь удобным переходным voice/capture adapter.</summary>

Он удобен как прагматичный voice adapter, но long-term могут стать удобнее:

- Telegram;
- собственный web/mobile voice capture;
- assistant integrations другого типа.

Нужно понять: Calendar — первая полноценная интеграция или временный мост.

</details>

**Статус:** решён  
**Обсуждение:** [PQ-009 thread](04-open-questions.threads/09_PQ-009_calendar-inbox-role/00_thread.md)

**Решение:** Calendar inbox остаётся optional production transport/adapter и не является core dependency. Calendar timeline — отдельная derived one-way projection: одна diary entry соответствует одному Calendar event; при новой committed revision/current-state change существующий event обновляется, а отдельные events для каждой revision не создаются.


## PQ-011 — Как устроен Entry detail/edit и переиспользуемый EntryPanel?

<details>
<summary>Нужно было определить границу между reusable EntryPanel и surrounding EntryScreen, чтобы view/edit и proposal review использовали одну совместимую модель представления.</summary>

Как должен выглядеть основной экран одной Entry и какое представление состояния записи нужно сделать переиспользуемым между обычным просмотром, ручным редактированием и proposal merge/review?

Главная развилка была в границе между reusable Entry content component и surrounding EntryScreen. Уже согласованный proposal review `Base | Result | Proposal` требовал, чтобы обычный Entry view/edit и proposal merge не расходились на разные несовместимые представления записи.

</details>

**Статус:** РЕШЕНО  
**История обсуждения:** [PQ-011 thread](04-open-questions.threads/17_PQ-011_entry-detail-editor/00_thread.md)

**Решение:** EntryScreen разделён на reusable EntryPanel и screen-level chrome. EntryPanel единообразно используется для view/edit и proposal review, содержит title, event date/start/end, text, assets, tags и тихую created/updated metadata; на широкой panel Assets/Tags/metadata находятся справа, на узкой — под Text. AI actions живут на EntryScreen как `AI ▾` рядом с обычными actions и содержат workflows + Custom prompt; dirty draft использует Save & Run, inline AI assistance остаётся отдельным MVP-candidate для editor. History/Revisions показывается под Entry как scrollable gallery/timeline; клик открывает read-only `Previous revision | Selected revision`, provenance показывается отдельно, Tags/Assets diff используют `+/-`, порядок Assets незначим, text diff определяется при реализации. Отдельный постоянный AI-note/annotation block не нужен.

Visual polish, точный text-diff, first-revision edge case и breakpoint values считаются implementation details и не блокируют продуктовый baseline.

---

# 2. Data / storage вопросы

## AQ-DATA-001 — Files-only или files + derived DB/index?

<details>
<summary>Нужно было решить, достаточно ли files-only для первого MVP или нужен persistent derived DB/index ради listing/filter/search, не меняя ownership canonical data.</summary>

Web UI нужен быстрый listing/filter/search.

Реалистичные варианты:

- прямое чтение Drive при небольшом объёме;
- in-memory/cache index;
- rebuildable server index;
- relational DB как derived projection;
- search-specific store;
- комбинация.

Ключевое ограничение: добавление operational index не должно молча менять ownership canonical data.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-DATA-001 thread](04-open-questions.threads/15_AQ-DATA-001_files-vs-derived-index/00_thread.md)

**Решение:** первый MVP работает files-only через отдельный data layer/repository abstraction; database и полноценный search на старте не обязательны. Архитектура должна позволять позже добавить rebuildable derived index для listing/filter/search/performance. Canonical diary content и revisions остаются в user-owned storage; server-side DB не должна становиться их второй durable копией. Operational state может содержать приватные данные только там, где это необходимо. Privacy policy будущего search index определяется отдельно.


## AQ-DATA-002 — Гранулярность storage abstraction

<details>
<summary>Нужно было выбрать уровень storage abstraction: low-level file operations или domain repository в терминах Entry/Revision, оставив низкий уровень только специальным tools.</summary>

Два полюса:

#### Низкоуровневый

```text
listFiles
readFile
writeFile
moveFile
```

#### Доменный

```text
listEntries
getEntry
saveRevision
listChanges
```

Текущее направление предпочитает domain-level API, но migration/import tools могут потребовать lower-level access.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-DATA-002 thread](04-open-questions.threads/18_AQ-DATA-002_storage-abstraction/00_thread.md)

**Решение:** основной application/domain слой использует высокоуровневый domain repository в терминах `Entry`, `Revision`, history/listing и других diary concepts (`listEntries/getEntry/saveRevision/loadHistory` и т. п.). Drive/files operations скрыты в нижнем storage adapter и не должны протекать в основной domain logic. Прямой low-level file access допустим для migration/import/repair/admin tooling.


## AQ-DATA-003 — Concurrency / optimistic locking

<details>
<summary>Нужно было определить, как предотвратить silent lost updates при одновременных изменениях из нескольких tabs/devices, AI jobs и внешнего storage.</summary>

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

</details>

**Статус:** РЕШЕНО  
**История обсуждения:** [AQ-DATA-003 thread](04-open-questions.threads/16_AQ-DATA-003_concurrency-locking/00_thread.md)

**Решение:** mutation ownership scoped per Entry. Committed mutation разрешена только актуальному владельцу editing/mutation lease и должна указывать `baseRevisionId`/эквивалентный domain version. Потеря lease запрещает commit; устаревшая base revision не перезаписывает current state, а проходит compatibility/rebase/merge/conflict. На storage layer canonical write дополнительно защищается native conditional version token (`ETag`/generation/version или эквивалент), если storage его поддерживает; race приводит к reload/reconcile, не к last-write-wins. Разные Entries могут независимо редактироваться параллельно.

## AQ-DATA-004 — Change detection

<details>
<summary>Нужно было решить, как backend обнаруживает внешние изменения canonical Drive/files и как не перезаписать их молча.</summary>

Если Drive/files canonical, как backend эффективно узнаёт про изменения?

Варианты:

- Drive Changes API;
- ETags/modified timestamps;
- derived sync/index state;
- MVP-ограничение: canonical writes только через backend;
- периодический reconciliation.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-DATA-004 thread](04-open-questions.threads/19_AQ-DATA-004_change-detection/00_thread.md)

**Решение:** на update существующей canonical entry backend выполняет cheap storage metadata/version check. Если обнаружено валидное содержательное внешнее изменение, оно фиксируется как новая immutable revision с provenance, после чего pending change проходит rebase/merge/conflict относительно нового current state. Silent overwrite недопустим. Если изменился только metadata marker без content change, revision не создаётся. Invalid/unparseable external state уходит в review/recovery path. Постоянный Drive watcher в первом MVP не обязателен; opportunistic check при read/update достаточен. Текущие Calendar/Telegram/file-based workflows могут мигрировать к общему backend/capture boundary постепенно.


## AQ-DATA-005 — Asset storage

<details>
<summary>Нужно было решить, где хранить media originals и derivatives, сохранив portability и возможность позднее отделить object storage/CDN без переделки domain model.</summary>

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

</details>

**Статус:** РЕШЕНО  
**История обсуждения:** [AQ-DATA-005 thread](04-open-questions.threads/23_AQ-DATA-005_asset-storage/00_thread.md)

**Решение:** Asset имеет storage-independent identity и contract: kind, authoritative original reference, basic technical metadata и provenance/source. Original поддерживает managed и external modes: managed media хранится под контролем AI Diary/user-owned storage, external media может оставаться у внешнего provider (например Google Photos/URL) без обязательного копирования. Preview/thumbnail/transcode и другие представления считаются отдельными rebuildable derivatives/cache. Для MVP managed originals могут жить в user-owned Drive/file backend; отдельный object storage/CDN не обязателен и добавляется только при реальной необходимости. Модель Asset не должна быть жёстко owned Entry и должна позволять позднее использовать общую media library с ZoomAlboom без выделения отдельного media service сейчас.


## AQ-DATA-006 — Format schema и migrations

<details>
<summary>Нужно было определить versioning canonical format и безопасную migration policy: backup, lock, validation, backward compatibility и rebuild derived state.</summary>

Нужно определить:

- format version granularity;
- migration runner;
- backward compatibility;
- backup before migration;
- validation;
- возможность rebuild derived indexes после migration.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-DATA-006 thread](04-open-questions.threads/20_AQ-DATA-006_schema-migrations/00_thread.md)

**Решение:** storage имеет одну общую `formatVersion`. Migrations выполняются как явная операция с backup/snapshot и maintenance/read-only lock, последовательно по соседним версиям (`v1 -> v2 -> ... -> current`). Migration меняет только реально изменившиеся типы данных, затем проходит schema/integrity/data-loss validation; новая format version активируется только после успешной проверки. После migration пользователь получает report и возможность точечно проверить `before / after`; конкретный UX этого comparison откладывается до реализации первой реальной migration и должен быть тогда рассмотрен отдельно. Core runtime не обязан поддерживать все исторические formats; old readers/transformers остаются в migration tooling.


## AQ-DATA-007 — Нужно ли позволять пользователю вручную редактировать canonical files?

**Статус:** РЕШЕНО  
**История обсуждения:** [AQ-DATA-007 thread](04-open-questions.threads/24_AQ-DATA-007_manual-canonical-edits/00_thread.md)  
**Будущее:** [FQ-ASSET-001 — Asset/media versioning](06-future-questions.md#fq-asset-001--assetmedia-versioning)

**Решение:** canonical files остаются readable/portable; полноценный ручной file-edit workflow не обязателен для MVP. Валидное внешнее изменение поддерживаемых content fields может быть импортировано как external manual edit и зафиксировано новой Entry revision. Изменение identity/system invariants или storage layout не считается обычным supported edit path и требует validation/recovery. Asset/media versioning не входит в текущий scope.


## AQ-DATA-008 — Migration со старого Firebase/Room

<details>
<summary>Нужно было понять, есть ли в старом Firebase/Room уникальные ценные данные, ради которых вообще нужен отдельный migration tooling.</summary>

Сначала нужно выяснить:

- есть ли там реальные уникальные пользовательские данные;
- это test/prototype data или ценный diary history;
- что нельзя восстановить из Drive.

Только после этого решать, нужен ли migration tooling.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-DATA-008 thread](04-open-questions.threads/21_AQ-DATA-008_legacy-firebase-migration/00_thread.md)

**Решение:** отдельная migration со старого Android/Firebase/Room не нужна. В старом проекте нет уникальных ценных пользовательских данных, требующих migration tooling; новая web/backend architecture от legacy storage не зависит. Если позже обнаружатся уникальные данные, это будет отдельный scoped import/migration task.


## AQ-DATA-009 — Какая именно модель core data synchronization нужна?

**Статус:** РЕШЕНО  
**История обсуждения:** [AQ-DATA-009 thread](04-open-questions.threads/25_AQ-DATA-009_core-sync-topology/00_thread.md)

**Решение:** ordinary clients и internal processes работают с diary через backend/domain API. Backend координирует mutations, leases, revisions, concurrency и reconciliation, но canonical durable state остаётся в user-owned files. Прямые изменения storage считаются external changes; derived DB/index/cache не являются authority. Offline sync, Calendar projection, capture queue и backup/export имеют отдельные contracts.


## AQ-DATA-010 — Как хранить autosave / working state незавершённой editing session?

<details>
<summary>Нужно было определить, где хранить autosave/working draft до revision, как восстанавливаться после сбоев и как сочетать это с multi-device editing и AI mutations.</summary>

Как технически хранить промежуточное autosave-состояние manual editing session до того, как оно станет полноценной revision?

К этому моменту уже было принято, что editing session начинается с первой реальной ручной правки, autosave защищает работу от потери, сам autosave revision не создаёт, а manual revision появляется при явном Save или после 1 часа inactivity. Нужно было определить server/local working state, recovery, multi-device editing и взаимодействие с AI mutations.

</details>

**Статус:** РЕШЕНО  
**Решение:** один server-side current working draft хранится в operational state; локально клиент держит bounded recovery snapshots. Canonical revisions и operational draft семантически разделены, хотя физически могут жить в одном storage на MVP. Для manual editing используется soft lease с одним active editor и безопасным takeover между sessions. AI mutations используют mutation lease, могут ждать в очереди, уступают ручному редактированию и при устаревшем base state проходят compatibility/revalidation. MVP-defaults: до 5 local snapshots, не более 30 секунд между recovery points, retention 24 часа после successful revision, auto-revision после 1 часа inactivity. Server draft очищается после successful revision; при failed commit сохраняется. Draft sync: debounce + guaranteed flush, точные интервалы configurable.  
**История обсуждения:** [AQ-DATA-010 thread](04-open-questions.threads/04_1_AQ-DATA-010_autosave-working-state/00_thread.md)


---

# 3. Backend / API вопросы

## AQ-API-001 — Язык/framework backend

**Статус:** РЕШЕНО  
**История обсуждения:** [AQ-API-001 thread](04-open-questions.threads/26_AQ-API-001_backend-language-framework/00_thread.md)

**Решение:** основной backend stack — Kotlin/Ktor. Это основной runtime для domain/API logic, storage coordination, revisions, leases, concurrency/reconciliation и integrations. Python допускается позднее для специализированных AI/ML/media/data workers/jobs, если появляется конкретная выгода; в MVP второй runtime не вводится без необходимости. Specialized workers не становятся независимыми writers canonical diary state.


## AQ-API-002 — Hosting/runtime

<details>
<summary>Нужно было выбрать production runtime для request-driven API, SSE и долгих/scheduled background jobs, сохранив низкую стоимость и умеренную operational complexity.</summary>

Cloud Run рассматривался вместе с Render и Railway. Критерии: стоимость и scale-to-zero, cold starts, SSE/long-lived HTTP, long-running background execution, scheduler/queue integration, Google OAuth/Drive convenience, logs и deployment complexity.

В ходе обсуждения уточнился целевой runtime profile: один modular-monolith backend codebase, но несколько runtime roles — API service, worker/job runtime и scheduled jobs. Background workflows должны быть durable и не зависеть от открытой browser session; открытая страница получает lightweight updates через SSE, без Web Push для закрытой страницы.

</details>

**Статус:** РЕШЕНО  
**Решение:** для первого web/backend MVP выбираем Google Cloud Run ecosystem: Cloud Run Service для backend API + SSE, Cloud Run Jobs для run-to-completion background workloads, Cloud Scheduler для scheduled triggers. Backend остаётся modular monolith в одной кодовой базе с несколькими runtime roles; отдельные бизнес-микросервисы на старте не вводятся. Durable queue/task mechanism и точные retry/idempotency/job-state semantics выбираются отдельно в AQ-API-004/AQ-OPS-002. Редкие initial setup/admin действия можно делать вручную, но они должны быть понятны и документированы; routine deploy/update желательно воспроизводить из repo/scripts/CI без обязательного полного IaC на старте.  
**История обсуждения:** [AQ-API-002 thread](04-open-questions.threads/22_AQ-API-002_hosting-runtime/00_thread.md)

## AQ-API-003 — API style

**Обсуждение:** [AQ-API-003 thread](04-open-questions.threads/27_AQ-API-003_api-style/00_thread.md)

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

<details>
<summary>Нужно было выбрать identity model: привязывать пользователя к Google/Firebase напрямую или иметь независимый internal account с внешними login identities.</summary>

Google account — естественный first path.

Нужно решить, использовать ли:

- Firebase Auth;
- direct Google OIDC/OAuth;
- другой auth middleware.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-001 thread](04-open-questions.threads/12_AQ-AUTH-001_identity-model/00_thread.md)

**Решение:** AI Diary использует собственный stable internal user/account ID, независимый от конкретного login provider. Google — первый login method для MVP, но external identities должны привязываться к internal user отдельно, чтобы позже можно было добавить другие способы входа без миграции основной user model. Конкретный auth service/framework сейчас не фиксируется и выбирается вместе с backend/hosting.


## AQ-AUTH-002 — Drive/Calendar OAuth

<details>
<summary>Нужно было определить Google OAuth policy: scopes, incremental consent, refresh tokens, revocation, account switching и re-auth.</summary>

Нужно определить:

- где хранится refresh token;
- какие scopes запрашиваются;
- incremental consent;
- token revocation;
- account switch;
- expired permissions;
- re-auth UX.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-002 thread](04-open-questions.threads/14_AQ-AUTH-002_google-oauth/00_thread.md)

**Решение:** Google API permissions выдаются incremental/per-feature: login отдельно, Drive consent при подключении diary storage, Calendar consent только при включении Calendar features. Предпочтение — минимально необходимые permissions и отсутствие full-Drive access, если это реализуемо разумно. Точные scopes, folder access mechanics, refresh-token storage, revocation, account switch и re-auth UX относятся к implementation/security details и не блокируют MVP.


## AQ-AUTH-003 — Single-user vs multi-user readiness

<details>
<summary>Нужно было решить, проектировать ли приложение сразу multi-user или оптимизировать первый production только под одного владельца.</summary>

Первый production может быть только для одного владельца.

Вопрос: стоит ли с первого дня иметь explicit `userId/ownerId` в domain/API, чтобы не делать болезненную миграцию позже.

</details>

**Статус:** решён  
**Обсуждение:** [AQ-AUTH-003 thread](04-open-questions.threads/11_AQ-AUTH-003_multi-user-readiness/00_thread.md)

**Решение:** AI Diary с самого начала считается multi-user application: один backend/application может обслуживать нескольких авторизованных пользователей, у каждого свой логический дневник и изолированные данные. Shared operational/server-side state должен быть user-scoped. При user-owned canonical storage explicit ownerId не обязан дублироваться внутри каждого diary file. Sharing/ACL между пользователями остаются отдельной future feature и не входят в MVP.

## AQ-AUTH-004 — Доступ backend к user-owned Drive

<details>
<summary>Нужно было выбрать модель доступа backend к user-owned Drive: delegated OAuth пользователя, service account/shared folder или другой pattern.</summary>

Нужно решить модель:

- backend действует от имени пользователя по OAuth token;
- service account + shared folder;
- другой pattern.

Это сильно влияет на security и deployment.

</details>

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