# AI Diary — инвентаризация требований

**Дата среза:** 2026-09-27  
**Цель:** перечислить требования и решения, найденные в repo-документах, project-файлах и наших обсуждениях, не скрывая противоречий и не превращая старые технические решения в новые требования.

## Легенда статусов

- **ПОДТВЕРЖДЕНО** — устойчивое текущее требование/решение.
- **РАБОЧЕЕ_НАПРАВЛЕНИЕ** — текущий предпочтительный вариант, который ещё можно оспорить на архитектурном этапе.
- **УСТАРЕЛО** — историческое техническое или архитектурное решение; полезно как контекст, но не обязательно для новой версии.
- **ОТКРЫТО** — вопрос не решён.

---

# A. Идентичность продукта и границы

### PROD-001 — AI Diary — персональная система памяти/дневник
**Статус:** ПОДТВЕРЖДЕНО  
AI Diary должен помогать пользователю захватывать повседневные события, воспоминания, мысли, ссылки и media, а затем постепенно структурировать и обогащать этот материал.

### PROD-002 — Сначала захватить, структурировать потом
**Статус:** ПОДТВЕРЖДЕНО  
Пользователь не должен сначала заполнять структуру и metadata, чтобы сохранить мысль. Структура может быть добавлена позже вручную или workflows/AI.

### PROD-003 — Минимизировать усилия на ведение дневника
**Статус:** ПОДТВЕРЖДЕНО  
Продукт должен быть существенно проще традиционного «сесть и написать дневниковую запись».

### PROD-004 — AI Diary и ZoomAlboom — разные продукты
**Статус:** ПОДТВЕРЖДЕНО  
AI Diary отвечает за содержание, события, смысл, связи и историю. ZoomAlboom — будущий визуально-пространственный слой и integration target.

### PROD-005 — Позиционирование как «personal memory system»
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Исследование рынка и поздние обсуждения позволяют описывать продукт шире, чем therapy journal или PKM: система личной памяти, которая помогает захватывать, структурировать и исследовать собственную историю.

### PROD-006 — Несколько вертикалей поверх одного движка
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Ранее рассматривались Life Diary, Baby/Early Years Diary, Travel Diary как разные «линзы» над одной и той же базовой моделью.

### PROD-007 — Продукт должен оставаться полезным без AI
**Статус:** ПОДТВЕРЖДЕНО  
Capture/read/edit не должны зависеть от доступности конкретной LLM или успешного AI-run.

---

# B. Capture / inbox

### CAP-001 — Захват должен быть низкофрикционным
**Статус:** ПОДТВЕРЖДЕНО  
Сохранение мысли не должно требовать длинного UI-flow.

### CAP-002 — Голосовой capture — первоклассный сценарий
**Статус:** ПОДТВЕРЖДЕНО  
Пользователь должен иметь возможность естественно диктовать длинный и неструктурированный материал.

### CAP-003 — У голосового capture должна быть явная граница commit
**Статус:** ПОДТВЕРЖДЕНО  
Предпочтительный interaction: диктовка частями -> явное «сохранить» -> одна операция создания/коммита, а не серия неустойчивых create/update во время речи.

### CAP-004 — Разные capture-каналы должны сходиться в общую pipeline
**Статус:** ПОДТВЕРЖДЕНО  
Calendar, Telegram, web, Android/native, import scripts и raw files не должны каждый писать финальные записи по собственной схеме.

### CAP-005 — Google Calendar может быть внешним voice-friendly inbox
**Статус:** ПОДТВЕРЖДЕНО  
Calendar полезен как очередь/адаптер для голосового ввода через ассистентов.

### CAP-006 — Google Calendar не является каноническим хранилищем
**Статус:** ПОДТВЕРЖДЕНО.

### CAP-007 — Raw input должен сохраняться после обработки
**Статус:** ПОДТВЕРЖДЕНО  
Исходный текст/event/media не должен исчезать после создания структурированной entry.

### CAP-008 — Повторная обработка не должна создавать дубликаты
**Статус:** ПОДТВЕРЖДЕНО  
Capture adapters и background workflows должны быть идемпотентными или duplicate-resistant.

### CAP-009 — Telegram как capture channel
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Желаемый канал, но конкретный UX пока не определён.

### CAP-010 — Web create/capture
**Статус:** ОТЛОЖЕНО / НЕ ОБЯЗАТЕЛЬНО ДЛЯ ПЕРВЫХ ЭТАПОВ  
Первый полезный web slice работает с существующими entries. Простую форму create можно добавить opportunistically, если она почти не увеличивает scope, но она не должна задерживать browse/read/search/edit/versioning.

### CAP-011 — Raw file drop / import
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
File-first модель это поддерживает; нужно решить, насколько это пользовательская feature первого релиза.

### CAP-012 — Источник capture должен сохраняться в provenance
**Статус:** ПОДТВЕРЖДЕНО  
Должно быть возможно понять, откуда появилась запись: Calendar, Telegram, web, import и т. п.

---

# C. Diary Entry и модель содержания

### ENTRY-001 — Entry — главный пользовательский объект
**Статус:** ПОДТВЕРЖДЕНО  
Пользователь должен уметь просматривать, открывать, читать и редактировать entries.

### ENTRY-002 — Дата записи не равна времени технического создания
**Статус:** ПОДТВЕРЖДЕНО  
Запись относится к содержательной дате/времени, которые могут отличаться от времени capture/process.

### ENTRY-003 — Стабильная идентичность записи
**Статус:** ПОДТВЕРЖДЕНО  
Entry нужен стабильный ID, независимый от title/tag/path rename.

### ENTRY-004 — Человекочитаемое представление
**Статус:** ПОДТВЕРЖДЕНО  
Текст дневника должен быть понятен вне приложения.

### ENTRY-005 — Машиночитаемая metadata
**Статус:** ПОДТВЕРЖДЕНО  
Нужна структура для дат, статусов, tags, provenance, workflow state, integrations.

### ENTRY-006 — Редактирование не должно уничтожать историю
**Статус:** ПОДТВЕРЖДЕНО  
Значимые user edits должны сохранять предыдущие состояния через revisions или эквивалентную механику.

### ENTRY-007 — Пользовательский текст имеет приоритет над AI
**Статус:** ПОДТВЕРЖДЕНО  
AI не может молча переписать то, что пользователь уже отредактировал.

### ENTRY-008 — Явная неопределённость
**Статус:** ПОДТВЕРЖДЕНО  
Если дата, grouping, person/place identity и т. п. неясны, система должна хранить неопределённость/review state вместо выдуманного факта.

### ENTRY-009 — Один input может дать несколько entries, и наоборот
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Существующий Inbox-to-Entry это допускает при уверенной связи.

### ENTRY-010 — Lifecycle Entry: ACTIVE / ARCHIVED / DELETED
**Статус:** ПОДТВЕРЖДЕНО  
Для пользовательского lifecycle достаточно `ACTIVE`, `ARCHIVED`, `DELETED`. `ACTIVE` участвует в обычных browse/search/timeline; `ARCHIVED` сохраняется, но скрывается из обычного потока по умолчанию; `DELETED` — soft delete / trash и исключается из обычных представлений, не уничтожая историю. Постоянный `DRAFT`-status для Entry не нужен: незавершённый manual edit — operational working draft, непринятый AI output — Proposal.

### ENTRY-011 — Запись может иметь точное время или только дату
**Статус:** ПОДТВЕРЖДЕНО  
Модель должна поддерживать day-level и timestamp/interval-level содержание.

### ENTRY-012 — Entry — стабильный контейнер, content versioned через Revision
**Статус:** ПОДТВЕРЖДЕНО  
`Entry` хранит stable identity/lifecycle/current revision reference и технические timestamps. Состояние, которое должно восстанавливаться исторически — title, event date/start/end, text, tags, asset links и source/composition references — относится к `EntryRevision` или эквивалентному versioned snapshot. Конкретная физическая schema — архитектурная.

---

# D. Revisions и provenance

### REV-001 — Сохранять оригинал/raw state
**Статус:** ПОДТВЕРЖДЕНО.

### REV-002 — Сохранять значимую историю изменений
**Статус:** ПОДТВЕРЖДЕНО  
AI cleanup, user edit и другие трансформации должны быть различимы и инспектируемы.

### REV-003 — Provenance — first-class concern
**Статус:** ПОДТВЕРЖДЕНО  
Для derived content должно быть понятно, из каких входов и каким процессом он получен.

### REV-004 — Workflow run должен быть трассируемым
**Статус:** ПОДТВЕРЖДЕНО  
Минимум: workflow/version, prompt/version, входы, выходы, время; для LLM также provider/model.

### REV-005 — Формат хранения revisions
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
File-first ветка использует отдельные revision files/folders. Сам принцип обязателен, on-disk форма — архитектурная.

### REV-006 — Revisions должны помогать разрешать конфликты
**Статус:** ПОДТВЕРЖДЕНО  
Committed mutation должна знать base revision/domain version. Если current revision ушла вперёд, silent last-write-wins запрещён; изменение проходит compatibility/rebase/merge/conflict flow.


### REV-007 — Current Entry и History/Revisions различаются, но History видна на EntryScreen
**Статус:** ПОДТВЕРЖДЕНО  
Current Entry остаётся главным состоянием EntryScreen. Под ней показывается компактная scrollable History/Revisions gallery/timeline revision snippets. Raw/original и полные revision details не обязаны постоянно занимать место рядом с текущим состоянием и доступны через history drill-down.

### REV-008 — Manual revision соответствует завершённой editing session
**Статус:** ПОДТВЕРЖДЕНО  
Manual editing session начинается с первой фактической правки. Autosave внутри session не создаёт revisions. Ручной Draft создаёт manual revision только при явном Save; autosave/inactivity её не создают (уточнение 04.10, подтверждено 18.10). Apply подтверждённого AI proposal и Restore исторической версии самостоятельно создают новую Revision, без дополнительного Save. Не вводится эвристика «мелкое/крупное изменение».

### REV-009 — Последовательные manual revisions могут группироваться только визуально
**Статус:** ПОДТВЕРЖДЕНО  
Подряд идущие manual revisions остаются отдельными revision records, но в History могут отображаться одним раскрываемым блоком. Это presentation rule и не меняет data model.

### REV-010 — Revision history линейная
**Статус:** ПОДТВЕРЖДЕНО  
Для MVP не используется Git-подобное branching revision tree. Новые изменения продолжают одну линейную историю.

### REV-011 — Restore старой revision создаёт новую revision
**Статус:** ПОДТВЕРЖДЕНО  
Restore не удаляет и не переписывает последующую историю. Snapshot выбранной старой revision копируется в новую revision поверх текущей. Новая revision сохраняет provenance-ссылку на источник, например `restoredFromRevisionId`.

### REV-012 — Применённая AI mutation существующей entry создаёт отдельную revision
**Статус:** ПОДТВЕРЖДЕНО  
AI proposal до Apply не является revision. Любое **применённое** AI-действие, изменяющее существующую entry, создаёт отдельную committed revision и не перезаписывает предыдущую версию.

### REV-013 — Committed revisions immutable / append-only
**Статус:** ПОДТВЕРЖДЕНО  
Committed revision уже является историческим фактом и не требует lifecycle status `pending/accepted/rejected`. Пользователь не удаляет отдельные revisions вручную. Undo/Restore создаёт новую revision с нужным snapshot/provenance, не уничтожая старую историю.

### REV-014 — Набор assets является частью revision state
**Статус:** ПОДТВЕРЖДЕНО  
Историческая revision должна восстанавливать тот набор asset links, который был у записи в этот момент. На продуктовом уровне связь рассматривается как `EntryRevision ↔ Asset`; текущие assets Entry получаются из current revision.

### REV-015 — History compaction не входит в MVP
**Статус:** ОТЛОЖЕНО  
Если revision history станет слишком большой, future maintenance может создать synthetic full-state checkpoint и применять retention/archive policy к старым промежуточным revisions. Это не пользовательский delete/rollback. См. `FQ-REVISION-002`.

---

# E. Tags, catalogs и организация

### TAG-001 — Tags нужны для навигации и группировки
**Статус:** ПОДТВЕРЖДЕНО.

### TAG-002 — Лучше немного полезных tags, чем агрессивный over-tagging
**Статус:** ПОДТВЕРЖДЕНО.

### TAG-003 — User-created tags нельзя молча перезаписывать
**Статус:** ПОДТВЕРЖДЕНО.

### TAG-004 — AI tag proposal должен быть объяснимым
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
В текущих workflows используются reason + confidence и proposal-only mode.

### TAG-005 — Мягкие типы tags
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Например `topic`, `person`, `pet`, `place`, `event_cluster`, `project`, `activity`, `mood`, `system` без жёсткой онтологии.

### TAG-006 — Отдельные сущности People/Places
**Статус:** ОТКРЫТО  
Пока эти понятия можно выражать tags; richer catalogs могут появиться позже.

---

# F. Media / Assets

### ASSET-001 — Entries могут ссылаться на фото, audio, video, links, files
**Статус:** ПОДТВЕРЖДЕНО.

### ASSET-002 — Asset должен иметь отдельную идентичность
**Статус:** ПОДТВЕРЖДЕНО.

### ASSET-003 — Оригиналы media нужно сохранять
**Статус:** ПОДТВЕРЖДЕНО.

### ASSET-004 — Asset storage поддерживает managed и external originals
**Статус:** ПОДТВЕРЖДЕНО  
Asset имеет storage-independent identity и authoritative original reference. Как минимум поддерживаются managed originals и external references. Managed media в первом MVP может храниться в user-owned Drive/file backend; external media может оставаться у внешнего provider/source без обязательного копирования. Конкретные provider-specific locator/storage детали скрываются adapter layer.

### ASSET-005 — Одна media сущность может быть связана с несколькими entries
**Статус:** ПОДТВЕРЖДЕНО.

### ASSET-006 — Remove asset из Entry различает unlink и delete
**Статус:** ПОДТВЕРЖДЕНО  
В edit UX действие удаления asset открывает явный выбор: отвязать от текущей Entry и оставить в Asset Library либо удалить asset из системы. Если asset используется несколькими entries, destructive delete предупреждает о затрагиваемых связях; если после unlink asset станет orphaned, это также явно показывается.

### ASSET-007 — Минимальный Asset contract не зависит от storage provider
**Статус:** ПОДТВЕРЖДЕНО  
Минимум: stable asset identity, kind, authoritative original mode/reference, basic technical metadata (mimeType, filename/title fallback, size и media dimensions/duration когда известны), provenance/source и createdAt. Checksum/hash для managed files допустим как optional implementation metadata.

### ASSET-008 — Previews и transcodes являются derivatives
**Статус:** ПОДТВЕРЖДЕНО  
Thumbnail, preview, transcoded media, waveform и подобные представления не являются authoritative original. Они могут быть provider-supplied или храниться как отдельный rebuildable cache/derivative; их отсутствие не должно ломать Asset identity или original reference.

### ASSET-009 — Asset identity допускает shared media library
**Статус:** ПОДТВЕРЖДЕНО  
Asset не должен быть жёстко owned одной Entry или только AI Diary. Модель должна позволять одному Asset использоваться AI Diary и позднее ZoomAlboom/другими consumers. Это не требует выделения отдельного Media Library service в MVP.


---

# G. Storage и владение данными

### DATA-001 — Данные должны быть переносимыми
**Статус:** ПОДТВЕРЖДЕНО  
Дневник не должен превращаться в непрозрачную БД, из которой тяжело восстановить собственную историю.

### DATA-002 — Данные должны быть инспектируемыми вне приложения
**Статус:** ПОДТВЕРЖДЕНО  
Human-readable text, explicit metadata и exportability — устойчивое требование.

### DATA-003 — Google Drive — первый желаемый storage backend новой версии
**Статус:** ПОДТВЕРЖДЕНО.

### DATA-004 — Storage должен быть заменяемым
**Статус:** ПОДТВЕРЖДЕНО  
Domain/client logic не должны быть напрямую завязаны на Drive-specific детали.

### DATA-005 — Основная storage abstraction — domain-level repository
**Статус:** ПОДТВЕРЖДЕНО  
Application/domain код работает в терминах `Entry`, `Revision`, history/listing и других diary concepts, например `listEntries/getEntry/saveRevision/loadHistory`. Drive/files operations скрыты в нижнем storage adapter. Прямой low-level file access допустим для migration/import/repair/admin tooling, но не должен протекать в основной domain logic.

### DATA-006 — Files как canonical source of truth
**Статус:** ПОДТВЕРЖДЕНО  
User-owned portable files являются canonical source of truth. Operational DB/index/cache допустимы как rebuildable derived layers и не должны содержать единственную копию существенных diary data. Concurrency, indexing, search, manual edits и multi-device behavior остаются архитектурными вопросами реализации этого принципа.

### DATA-007 — Первый MVP работает без database
**Статус:** ПОДТВЕРЖДЕНО  
Первый MVP читает canonical Drive/files через отдельный data layer/repository abstraction. Persistent DB для diary content на старте не требуется.

### DATA-008 — Будущий index/cache — derived и rebuildable
**Статус:** ПОДТВЕРЖДЕНО  
Архитектура должна позволять позже добавить derived index/cache для listing/filter/search/performance без изменения canonical ownership. Index не является source of truth и должен быть rebuildable из canonical files.

### DATA-017 — Canonical diary content не дублируется долговременно в server DB
**Статус:** ПОДТВЕРЖДЕНО  
Canonical content и revisions остаются в user-owned storage. Operational state может временно содержать приватный content только там, где это необходимо для работы продукта; серверные копии должны быть минимизированы и иметь понятный lifecycle.

### DATA-009 — Нужны versioning формата и безопасные migrations
**Статус:** ПОДТВЕРЖДЕНО  
Storage имеет одну общую `formatVersion`. Migration запускается как явная операция с backup/snapshot и maintenance/read-only lock: на время migration запрещены user edits и любые mutating workflows, включая legacy Calendar/Telegram/file-based writers. Migration переписывает только реально изменившиеся типы данных, затем проходит schema/integrity/data-loss validation; новая format version активируется только после успешной полной проверки. Пользователь получает migration report и может точечно открыть before/after для изменённых или проблемных объектов.

### DATA-010 — Нужны backup/export/restore semantics
**Статус:** ПОДТВЕРЖДЕНО.

### DATA-011 — External canonical changes не должны приводить к silent overwrite
**Статус:** ПОДТВЕРЖДЕНО ДЛЯ MVP  
Прямое внешнее редактирование Drive/files не является основным штатным write path, но при update существующей entry backend должен дешёво проверить storage metadata/version token. Валидное содержательное external change фиксируется как новая immutable revision с provenance; pending update после этого проходит rebase/merge/conflict относительно нового current state. Если изменился только storage marker без content change, новая revision не нужна. Invalid/unparseable external state не перезаписывается молча и переводится в review/recovery path. Постоянный Drive watcher для первого MVP не обязателен.


### DATA-012 — Незавершённое редактирование хранится как operational working draft
**Статус:** ПОДТВЕРЖДЕНО  
Для entry допускается один server-side current working draft как временное operational state. Он не является canonical revision. Canonical и operational storage могут физически совпадать на MVP, но их роли и lifecycle должны оставаться различимыми.

### DATA-013 — Нужны local recovery snapshots
**Статус:** ПОДТВЕРЖДЕНО  
Клиент хранит bounded local recovery snapshots для защиты от случайных пользовательских действий и кратких сбоев. MVP-default: до 5 snapshots, не более 30 секунд между recovery points, retention 24 часа после successful revision. Эти значения являются configurable policy constants. Local snapshots не входят в обычную revision history.

### DATA-014 — Один active mutation owner на entry
**Статус:** ПОДТВЕРЖДЕНО  
Для ручного редактирования и AI mutation используется lease-based модель: у entry в каждый момент один active mutation owner. Manual editing может перехватить lease у другой session или AI job; активная AI mutation не вытесняет пользователя.

### DATA-015 — AI mutation должна быть безопасна относительно новых revisions
**Статус:** ПОДТВЕРЖДЕНО  
AI result привязан к base revision. Если entry изменилась, сначала выполняется deterministic compatibility check; AI revalidation используется только когда совместимость неочевидна. Текстовые mutation workflows по умолчанию не auto-merge при содержательных изменениях.

### DATA-016 — Working draft синхронизируется debounce + guaranteed flush
**Статус:** ПОДТВЕРЖДЕНО  
Локальное working state синхронизируется на backend комбинированно: debounce после паузы во вводе плюс гарантированный flush при наличии unsynced changes. Обязательный flush выполняется перед Save, передачей lease и auto-revision. Конкретные интервалы настраиваемы.

### DATA-018 — Commit требует актуального per-entry lease и base revision
**Статус:** ПОДТВЕРЖДЕНО  
Editing/mutation lease scoped на конкретную Entry: разные Entries могут редактироваться параллельно независимыми sessions. Потерявшая lease session не имеет права committed write, пока заново не получит lease и не синхронизируется со свежим server draft. Перед committed mutation backend проверяет и актуальное lease ownership, и `baseRevisionId`/эквивалентный domain version. Несовпадение base/current revision не приводит к overwrite; используется compatibility/rebase/merge/conflict path.

### DATA-019 — Canonical write использует storage-level conditional version check
**Статус:** ПОДТВЕРЖДЕНО  
Storage adapter при физической canonical записи использует storage-native conditional token (`ETag`, generation/version token или эквивалент), если backend это поддерживает. Если token изменился между read/check и write, запись не перетирает новое состояние: backend перечитывает canonical state и запускает reconciliation/external-change flow. Точный provider-specific token является architecture/adapter detail.


---

# G2. Версионирование и синхронизация данных

Этот блок выделен отдельно намеренно: раньше эти требования были размазаны между revisions, storage, reliability и integration workflows, из-за чего легко было решить, что системного требования к versioning/sync нет.

### VER-001 — Версионность данных является first-class свойством системы
**Статус:** ПОДТВЕРЖДЕНО  
Значимые изменения пользовательского и AI-производного содержимого не должны сводиться к destructive overwrite. Система должна сохранять достаточную историю, чтобы понять, что изменилось, кем/чем и в какой последовательности.

### VER-002 — Версии контента, формата и AI-конфигурации — разные виды versioning
**Статус:** ПОДТВЕРЖДЕНО  
Не следует смешивать в один механизм:
- revisions пользовательских entries;
- версии file/schema format;
- версии prompts/workflows;
- version/model metadata конкретного AI run;
- версии integration/config при необходимости.

Для каждого вида должна быть явная идентичность и понятная семантика.

### VER-003 — Предыдущие значимые версии entry должны оставаться инспектируемыми и восстанавливаемыми
**Статус:** ПОДТВЕРЖДЕНО  
Пользовательская правка, AI cleanup, merge/import и другие значимые изменения должны оставлять историю. Конкретный UI restore/diff может появиться не сразу, но данные для восстановления предыдущего состояния должны сохраняться.

### VER-004 — Формат canonical data должен быть версионирован и мигрируем
**Статус:** ПОДТВЕРЖДЕНО  
Schema/file format должен иметь явную версию. Миграции не должны уничтожать оригинальные данные и должны позволять проверить/восстановить состояние при ошибке.

### VER-005 — Prompt/workflow version входит в provenance AI-результата
**Статус:** ПОДТВЕРЖДЕНО  
Для существенного AI output должно быть возможно определить, какой workflow и какая версия prompt/config использовались.

### SYNC-001 — Один логический дневник должен синхронизироваться между клиентами
**Статус:** ПОДТВЕРЖДЕНО  
Web, будущий Android/iOS и другие клиенты должны видеть одну логическую историю пользователя через общий backend/domain слой, а не поддерживать независимые несовместимые копии данных.

### SYNC-002 — Синхронизация не должна приводить к тихой потере конкурирующих изменений
**Статус:** ПОДТВЕРЖДЕНО  
Если два клиента, пользователь и AI, либо backend и ручная правка storage изменили одну сущность параллельно, система должна обнаружить конфликт или создать совместимую revision history. Простое silent last-write-wins не является приемлемым default для значимых diary data.

### SYNC-003 — Для синхронизации нужны стабильная identity и версия состояния
**Статус:** ПОДТВЕРЖДЕНО  
Сущности, участвующие в sync, должны иметь stable IDs и version/revision token либо эквивалент, позволяющий понять, какое состояние было прочитано и что изменилось после него.

### SYNC-004 — Retry должен быть безопасным
**Статус:** ПОДТВЕРЖДЕНО  
Повтор после network/API failure не должен создавать дубликаты или повторно применять одну и ту же операцию. Sync/capture/background operations должны быть идемпотентными или duplicate-resistant.

### SYNC-005 — Canonical data, operational indexes и external projections синхронизируются по разным правилам
**Статус:** ПОДТВЕРЖДЕНО  
Нужно различать:
- синхронизацию собственно diary data;
- rebuildable index/cache/DB projection;
- Google Calendar timeline projection;
- Calendar/Telegram capture state;
- backup/export.

Derived слой можно пересобрать; его рассинхронизация не должна менять каноническую историю.

### SYNC-006 — Изменения canonical storage должны обнаруживаться и согласовываться
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Если Google Drive/file storage остаётся canonical или допускает ручные изменения, backend должен иметь механизм change detection/reconciliation. Конкретная технология (Drive Changes API, ETag, polling и т. п.) — архитектурный вопрос.

### SYNC-007 — Полный offline-first sync для новой web/backend версии пока не подтверждён
**Статус:** ОТКРЫТО  
Обязательны защита от потери capture при плохой сети, safe retry и устойчивость к временной недоступности. Нужна ли полноценная offline editing + later merge model для всего web-клиента — отдельное решение.

### DATA-020 — Manual canonical file edits не являются обязательной MVP feature
**Статус:** ПОДТВЕРЖДЕНО / ОТЛОЖЕНО  
Canonical files должны оставаться readable/portable. Если валидное внешнее изменение content fields обнаружено, оно может быть импортировано как external manual edit и оформлено новой Entry revision. Изменения identity/system invariants или storage layout не должны silently приниматься и идут в validation/recovery. Отдельный UX/workflow для ручного редактирования canonical files не обязателен для MVP.



### DATA-021 — Core diary mutations проходят через backend/domain API
**Статус:** ПОДТВЕРЖДЕНО  
Обычные clients и internal processes не пишут canonical diary data напрямую в provider-specific storage. Backend/domain layer является coordinator/mutation authority и применяет domain rules, leases, revisions, optimistic concurrency и reconciliation. Canonical durable state при этом остаётся в user-owned portable files; derived DB/index/cache не становятся authority.


# H. Web client

### WEB-001 — Нужен полноценный web-интерфейс
**Статус:** ПОДТВЕРЖДЕНО.

### WEB-002 — Web должен адаптироваться под desktop и phone
**Статус:** ПОДТВЕРЖДЕНО.

### WEB-003 — Пошаговый scope web
**Статус:** ПОДТВЕРЖДЕНО  
Первый slice: browse/list + read + search/filter существующих entries. Следующий этап: edit + versioning/history. Затем tags view/edit. Затем AI processing/workflows. Web create не является обязательным для первых этапов.

### WEB-004 — Нужны search/filter/navigation
**Статус:** ПОДТВЕРЖДЕНО  
Минимум первого slice: текст, date/date range и tags. Status/source и другие filters можно добавить позже.

### WEB-005 — Web не должен быть единственным местом бизнес-логики
**Статус:** ПОДТВЕРЖДЕНО  
Бизнес-логика должна быть доступна через backend/API, чтобы её могли использовать и будущие native clients.

### WEB-006 — Google Sites / Apps Script как основной UI
**Статус:** УСТАРЕЛО  
Это был ранний shortcut для прототипа.

### WEB-007 — Frontend framework
**Статус:** ОТКРЫТО  
React/TypeScript обсуждался как естественный кандидат, но решения нет.

### WEB-008 — Frontend hosting
**Статус:** ОТКРЫТО.

### WEB-009 — На телефоне допустим упрощённый layout
**Статус:** ПОДТВЕРЖДЕНО  
Но базовый сценарий не должен ломаться.

### WEB-010 — EntryScreen отделён от переиспользуемого EntryPanel
**Статус:** ПОДТВЕРЖДЕНО  
`EntryScreen` содержит navigation/actions, reusable EntryPanel, текущие Proposals и History/Revisions. Sources/Lineage и полная AI activity не занимают отдельные постоянные блоки основного экрана; историческая трассировка открывается через details конкретных revisions.

### WEB-011 — EntryPanel имеет общую структуру для view/edit/merge
**Статус:** ПОДТВЕРЖДЕНО  
Минимальные области: Title; Event date + optional start/end; Text; Assets; Tags; вторичная read-only system metadata created/updated. Created/updated видны всегда, но визуально вторично: внизу secondary column на широкой panel и внизу panel на узкой; они не являются versioned content для revision diff. Title и Text редактируются в edit/result mode; date/start/end получают date/time controls; Tags и Assets получают add/remove actions. Add поддерживает выбор существующей сущности или создание новой (Asset Library/new asset; tag catalog/new tag). Base/Proposal в merge read-only, Result editable.

### WEB-012 — EntryPanel адаптируется по собственной ширине
**Статус:** ПОДТВЕРЖДЕНО  
При достаточной ширине Text занимает основную content column, а Assets, Tags и secondary created/updated metadata показываются справа. При узкой panel эти секции переходят под Text. Правило зависит от ширины самой EntryPanel, а не только viewport, чтобы тот же component автоматически работал в обычном Entry detail и в узких `Base | Result | Proposal` колонках. Точные breakpoint/column ratios — UI implementation detail.

### WEB-013 — Provenance/Lineage открываются из revision details
**Статус:** ПОДТВЕРЖДЕНО  
Sources/provenance/lineage считаются свойствами/trace metadata конкретной committed revision и показываются через History/Revisions: компактный indicator/details affordance, краткий tooltip/popover/hover view и optional `Подробнее`. Отдельный постоянный Sources/Lineage block на EntryScreen не нужен. Полную историческую AI activity также не нужно дублировать на основном экране; actionable AI state там представлен Proposals.

### WEB-014 — EntryScreen даёт запуск AI workflow/custom prompt
**Статус:** ПОДТВЕРЖДЕНО  
На уровне EntryScreen пользователь может вручную запустить доступный workflow для текущей Entry либо разовый `Custom prompt / Ask AI`. Это screen-level action, а не часть reusable EntryPanel; UI использует заметную кнопку/menu `AI ▾` рядом с обычными действиями Entry (например Edit).

### WEB-015 — Dirty manual draft использует Save & Run перед Entry workflow
**Статус:** ПОДТВЕРЖДЕНО  
Полноценные Entry workflows запускаются от committed revision. Если в manual editor есть unsaved changes, UI предлагает `Save & Run`: сначала working draft фиксируется как manual revision, затем эта revision становится base/input для AI run. AI workflow не работает скрытно по эфемерному draft.
### WEB-016 — Revision gallery открывает Previous vs Selected comparison
**Статус:** ПОДТВЕРЖДЕНО  
На EntryScreen History/Revisions показывается как компактная scrollable gallery/timeline карточек/snippets revisions. Карточка должна позволять быстро понять тип/время и характер изменения. Выбор revision открывает read-only comparison: слева предыдущая revision, справа выбранная. Оба состояния переиспользуют EntryPanel/diff components; provenance/metadata изменения показывается отдельно. Это не proposal merge: в History обе стороны read-only.

### WEB-017 — Revision diff field-aware и не сравнивает provenance
**Статус:** ПОДТВЕРЖДЕНО  
В Previous-vs-Selected comparison provenance/lineage/source/AI run/workflow/restoredFrom и другая trace metadata показываются отдельным details block и не участвуют в content diff. Для Tags и Assets added/removed состояния маркируются `+ / −`; порядок Assets незначим и reorder не считается изменением. Для Text желательно подсвечивать изменённые фрагменты; точный diff algorithm и visual style выбираются при реализации по читаемости.

### WEB-018 — Отдельный постоянный AI-note block не нужен
**Статус:** ПОДТВЕРЖДЕНО  
EntryScreen не содержит отдельный постоянный `AI note / annotation` block. Actionable AI mutation представлена Proposal, применённое изменение — committed Revision, историческая причина и trace — provenance/AI run details, а non-mutating AI analysis может оставаться workflow result без отдельной постоянной секции EntryScreen.


---

### AI-PROVIDER-ADAPTER — Общий интерфейс LLM providers
**Статус:** ПОДТВЕРЖДЕНО  
Kotlin/Ktor backend предоставляет минимальный provider-neutral adapter для text/structured outputs с нормализацией результата, usage/error metadata. Capabilities явно определяются per model/provider; уникальные функции доступны через optional extensions без чрезмерного унифицирования. API credentials остаются server-side; workflow layer не зависит от HTTP форматов OpenAI/Anthropic/Gemini. Можно начинать с одного provider adapter, сохраняя возможность добавления остальных. Выбор model/provider и запрет silent fallback определяются PQ-006. Решение: [AQ-AI-001](04-open-questions.threads/31_AQ-AI-001_provider-adapter/00_thread.md).

# I. Backend / API

### API-001 — Нужен отдельный backend API
**Статус:** ПОДТВЕРЖДЕНО.

### API-002 — API должен быть client-agnostic
**Статус:** ПОДТВЕРЖДЕНО.

### API-API-CONTRACT — REST + OpenAPI contract-first
**Статус:** ПОДТВЕРЖДЕНО  
Основной client-agnostic API использует REST + JSON. Версионируемая OpenAPI-спецификация в repo является общим контрактом frontend/backend и развивается итерационно из согласованных user flows/use cases. Не нужно заранее проектировать все endpoints. Новые операции должны отражать уже принятые domain semantics revisions/base version, conflict handling, working drafts, durable asynchronous jobs, asset access и auth. Точные структуры конкретных endpoints разрабатываются при реализации сценариев. Решение: [AQ-API-003](04-open-questions.threads/27_AQ-API-003_api-style/00_thread.md).

### API-003 — Backend framework/language
**Статус:** ОТКРЫТО  
Kotlin/Ktor удобен владельцу проекта; Python/FastAPI и TypeScript/Node остаются кандидатами.

### API-004 — Production runtime/hosting
**Статус:** ПОДТВЕРЖДЕНО  
Для первого web/backend MVP выбирается Google Cloud Run ecosystem: Cloud Run Service для request-driven backend API и SSE, Cloud Run Jobs для run-to-completion background workloads, Cloud Scheduler для scheduled triggers. Выбор конкретного durable queue/task mechanism остаётся отдельным architecture decision.

### API-005 — Низкая стоимость и низкая операционная нагрузка
**Статус:** ПОДТВЕРЖДЕНО  
Для личного проекта предпочтительны free/very-low-cost tiers, scale-to-zero там, где это уместно, и минимум постоянной DevOps-нагрузки. Редкие initial setup/admin действия допустимы вручную, если они понятны и документированы; routine deploy/update желательно воспроизводить из repo/scripts/CI без обязательного полного Infrastructure-as-Code на старте.

### API-006 — Нужны durable background jobs
**Статус:** ПОДТВЕРЖДЕНО  
AI workflows, indexing, import, Calendar sync, migrations/backfills и другие долгие/ненадёжные операции не должны зависеть от lifetime пользовательского HTTP request или открытой browser session. Event-triggered, user-triggered и schedule-triggered workflows должны сходиться в durable job model; точные queue/retry/idempotency semantics определяются отдельно.

### API-006A — Queue-first mutations и вычисления
**Статус:** ПОДТВЕРЖДЕНО  
Все изменения canonical diary state, включая Save, Apply/Restore, изменение тегов, выполняются через durable async command queue; фоновые вычисления, ingestion, AI workflows и indexing также исполняются асинхронно. Read/search queries не ставятся в очередь. Принятая команда и committed результат различаются: UI сообщает «Сохраняется» до подтверждения successful commit и отображает failures/conflicts явно. Autosave draft допускает coalescing/debounce вместо задачи на каждую клавишу. Конкретная queue provider, retry/idempotency и ordering semantics уточняются в AQ-OPS-002 и architecture design. Решение: [AQ-API-004](04-open-questions.threads/28_AQ-API-004_background-processing/00_thread.md).

### API-006B — Одно рабочее окружение для прототипа
**Статус:** ПОДТВЕРЖДЕНО
Для раннего прототипа используется одно deployed окружение без отдельного staging/test deployment. Локальный запуск допустим при разработке; потенциально разрушительные тесты выполняются на тестовых данных или при наличии backup. Дополнительные окружения создаются по конкретной необходимости. См. [AQ-API-005](04-open-questions.threads/29_AQ-API-005_environments/00_thread.md).

### API-007 — Monorepo с независимыми builds
**Статус:** ПОДТВЕРЖДЕНО  
Один репозиторий содержит web, Kotlin/Ktor backend и docs; frontend/backend используют независимые builds/toolchains, а OpenAPI specification остаётся общим версионируемым контрактом. Не требуется сейчас общий Gradle root, обязательный Android build или единый release pipeline; CI/deploy components можно разделять по мере необходимости. Решение: [AQ-API-006](04-open-questions.threads/30_AQ-API-006_monorepo/00_thread.md).

### API-008 — Backend остаётся modular monolith с несколькими runtime roles
**Статус:** ПОДТВЕРЖДЕНО  
Первый backend проектируется как одна codebase с общими domain/repository/workflow layers и отдельными runtime roles/entry points для API, worker/job execution и scheduled jobs. Бизнес-микросервисы вроде Entry/Tag/Calendar/AI services не вводятся без реальной нагрузки, security boundary или технологической причины.

### API-009 — Для открытого web UI достаточно SSE
**Статус:** ПОДТВЕРЖДЕНО  
Для lightweight server-to-browser уведомлений о завершении/изменении background state используется SSE. WebSocket не нужен без отдельного bidirectional realtime use case. При закрытой странице push/Web Push не требуется; при следующем открытии клиент перечитывает актуальное authoritative state. Потеря SSE notification не должна означать потерю результата.

---



### API-007 — Основной backend stack — Kotlin/Ktor
**Статус:** ПОДТВЕРЖДЕНО  
Core backend AI Diary реализуется на Kotlin/Ktor и содержит domain/API logic, storage coordination, revisions, leases, concurrency/reconciliation и integrations. Python может добавляться позднее как специализированный worker/service/job для AI/ML/media/data задач, когда это оправдано конкретным use case; такие workers не обходят domain mutation rules и не становятся независимыми writers canonical diary state. Для MVP второй runtime не обязателен.

# J. Authentication и Google integration

### AUTH-001 — Internal user identity независима от login provider
**Статус:** ПОДТВЕРЖДЕНО  
AI Diary имеет собственный stable internal user/account ID. Google — первый login method для MVP, но Google account ID не должен быть единственным внутренним user identity. External login identities должны привязываться к internal user отдельно, чтобы позже можно было добавить другие способы входа без миграции основной user model.

### AUTH-002 — Login и доступ к Google API — разные вещи
**Статус:** ПОДТВЕРЖДЕНО  
Нельзя путать app session/identity с Drive/Calendar OAuth scopes и refresh tokens.

### AUTH-003 — Минимально необходимые permissions/scopes
**Статус:** ПОДТВЕРЖДЕНО  
Приложение должно просить только те Google permissions, которые реально нужны.


### AUTH-006 — Backend получает доступ к Drive от имени пользователя
**Статус:** ПОДТВЕРЖДЕНО  
Для user-owned Google Drive backend использует OAuth grant конкретного пользователя и действует от его имени. Service account + shared folder не является основным multi-user access pattern. Детали token storage, revocation, re-auth и scopes определяются отдельно.

### AUTH-004 — Конкретный auth service/framework не фиксируется заранее
**Статус:** ПОДТВЕРЖДЕНО  
Firebase Auth, direct OIDC или другой auth middleware выбирается вместе с backend/hosting. Продуктовый контракт важнее конкретного провайдера: internal user identity должна оставаться независимой от login method.

### AUTH-005 — Multi-user application с изолированными данными
**Статус:** ПОДТВЕРЖДЕНО  
AI Diary с самого начала проектируется как multi-user application: один backend/application может обслуживать нескольких авторизованных пользователей, у каждого свой логический дневник и изолированные данные.

Authenticated user context обязателен для shared operational/server-side state. Drafts, leases, jobs, proposals, indexes/cache, OAuth tokens, settings и AI run records должны быть user-scoped.

Explicit ownerId не обязан дублироваться внутри каждого canonical diary file, если ownership уже задаётся user-owned storage boundary. Sharing и сложные ACL между пользователями остаются отдельной future feature.

---

# K. AI / LLM subsystem

### AI-001 — AI является enhancement, а не blocker
**Статус:** ПОДТВЕРЖДЕНО.

### AI-002 — Нужна provider-independent abstraction
**Статус:** ПОДТВЕРЖДЕНО  
Система должна уметь работать как минимум с OpenAI, Gemini и Anthropic/Claude без переписывания продукта под конкретный vendor API.

### AI-003 — Workflow и provider — разные уровни
**Статус:** ПОДТВЕРЖДЕНО  
Workflow определяет задачу/контекст/валидацию; provider выполняет model call.

### AI-004 — Model/provider должен быть заменяемым
**Статус:** ПОДТВЕРЖДЕНО.

### AI-005 — Prompt/version должны быть трассируемыми
**Статус:** ПОДТВЕРЖДЕНО.

### AI-006 — Prompts не должны быть полностью hardcoded в UI
**Статус:** ПОДТВЕРЖДЕНО.

### AI-007 — Нужен слой стабильных system/base contracts
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Например output schema, safety/behavioral rules, workflow contract.

### AI-008 — Пользователь должен иметь возможность задавать свои instructions/overrides
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ.

### AI-009 — Custom user workflows
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Например «проанализировать прогресс верховой езды за месяц».

### AI-010 — AI run должен сохранять достаточную трассировку и быть доступен для drill-down
**Статус:** ПОДТВЕРЖДЕНО  
Пользователь должен из Entry/AI activity открыть детали конкретного run/result: workflow/prompt versions, provider/model, input/base revision, output/AIResult, proposals, validation, timestamps, auto/user outcome и resulting committed revisions; позже usage/cost.

### AI-011 — AI output не должен автоматически становиться истиной
**Статус:** ПОДТВЕРЖДЕНО  
Для рискованных/семантически значимых трансформаций нужны proposal/review/accept semantics.

### AI-012 — Сравнение разных моделей на одном workflow
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Технически желательно, UI может появиться позже.


### AI-017 — Model preference имеет иерархию
**Статус:** ПОДТВЕРЖДЕНО  
Выбор LLM model разрешается по иерархии: explicit task/run override → workflow preference → global user preference → system default. Global user preference является основным пользовательским сценарием; более локальные уровни используются как override.

### AI-018 — Provider отдельно не выбирается
**Статус:** ПОДТВЕРЖДЕНО  
Пользователь выбирает конкретную LLM model; provider определяется выбранной моделью. Отдельная provider-настройка не требуется как самостоятельный пользовательский выбор.

### AI-019 — Silent fallback на другую model/provider не допускается
**Статус:** ПОДТВЕРЖДЕНО  
Если preferred model недоступна, система не должна молча переключаться на другую модель/provider. Для такого fallback требуется явное согласие пользователя. Конкретный UX, retry и обработка deprecated models относятся к implementation policy.

### AI-013 — User AI context / memory
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Старые модели уже различали explicit preferences и learned context. Точная реализация позже.

### AI-014 — Provider не должен знать структуру Google Drive
**Статус:** ПОДТВЕРЖДЕНО  
Context building и storage access выполняются внутри приложения/backend; provider получает подготовленный контекст, а не knowledge of diary storage internals.

### AI-015 — Pending AI proposals должны быть first-class state
**Статус:** ПОДТВЕРЖДЕНО  
Для AI-изменений существующей entry результат до принятия пользователя является proposal, а не committed revision.

Proposal должен:

- переживать reload/session;
- иметь target/scope/base revision или эквивалентное base state;
- поддерживать Accept/Reject и supersede;
- становиться stale/conflicted при несовместимом изменении base state;
- не попадать в обычную revision history до Accept/Apply;
- иметь собственный lifecycle и различать application mode (`USER` / `AUTO`) без переноса этого lifecycle на committed revision.

Несколько proposals могут существовать параллельно; новый state может сделать ранее созданные proposals stale/conflicted.

### AI-016 — Auto-apply policy определяется per workflow/type of change
**Статус:** ПОДТВЕРЖДЕНО  
Первая normalized entry может создаваться автоматически при сохранённом raw и явной uncertainty. Existing tags могут auto-apply при высокой уверенности; новые tags по умолчанию предлагаются. Точные confidence thresholds и policy для будущих metadata не являются blocking requirement для MVP.

### AI-020 — Proposal granularity определяется workflow
**Статус:** ПОДТВЕРЖДЕНО  
Один AIResult может дать один или несколько proposals. Один proposal может быть простым или комплексным и затрагивать text, date, tags и другие поля одновременно. Core product model не заставляет разбивать каждое атомарное изменение в отдельный proposal.

### AI-021 — Proposal review имеет быстрый и подробный путь
**Статус:** ПОДТВЕРЖДЕНО  
Бесконфликтный proposal на Entry card можно Apply/Reject или открыть подробно. Stale/conflicted proposal не имеет быстрого Apply. Detailed review использует `Base | Result | Proposal`: Base/Proposal read-only, Result editable; независимые изменения auto-merge, конфликты подсвечиваются локально, пользователь выбирает Current/Proposal/manual edit. Подтверждение Result создаёт одну committed revision; до этого merge result не входит в History.

### AI-022 — Inline AI editor assistance
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ / MVP CANDIDATE  
Желательна AI-помощь непосредственно внутри manual editor: команда над selection/current working draft, например rewrite, shorten, fix или continue. Это отдельная семантика от Entry workflow над committed revision. Перед реализацией нужно определить draft-level undo, связь с autosave и нужно ли создавать Proposal/Revision для таких операций. Фича не блокирует базовый MVP, но может войти в него opportunistically, если editor implementation делает её дешёвой и понятной.

---

# L. Calendar / integrations

### INT-001 — Calendar inbox — adapter, не ядро
**Статус:** ПОДТВЕРЖДЕНО.

### INT-002 — Calendar timeline — derived projection
**Статус:** ПОДТВЕРЖДЕНО.

### INT-003 — Timeline projection можно перестроить из diary data
**Статус:** ПОДТВЕРЖДЕНО.

### INT-004 — Внешний sync state не должен засорять canonical entry
**Статус:** ПОДТВЕРЖДЕНО.

### INT-005 — Telegram adapter должен использовать общую capture boundary
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ.

### INT-006 — Интеграции должны быть заменяемыми
**Статус:** ПОДТВЕРЖДЕНО.

### INT-007 — Calendar projection обновляет существующий event на committed revision
**Статус:** ПОДТВЕРЖДЕНО.

Для одной diary entry должен существовать один Calendar event. При новой committed revision или другом изменении current state существующий event обновляется. Отдельные Calendar events для каждой revision не создаются; pending proposals не считаются current diary state.

---

# M. Search / navigation

### SEARCH-001 — Обычный текстовый поиск нужен, но не в самом первом MVP
**Статус:** ПОДТВЕРЖДЕНО / ОТЛОЖЕНО  
Search остаётся продуктовым требованием следующего этапа, но первый files-only MVP может стартовать без него.

### SEARCH-002 — Date/tag filters нужны после базового files-only MVP
**Статус:** ПОДТВЕРЖДЕНО / ОТЛОЖЕНО  
Date/date range и tags входят в ближайший следующий web slice вместе с index/search layer, а не блокируют самый первый MVP.

### SEARCH-003 — Semantic search / embeddings
**Статус:** ОТЛОЖЕНО НА БУДУЩЕЕ  
Semantic retrieval для cross-entry AI возможно в будущем; embeddings, vector DB и semantic query pipeline не входят в MVP. Оставить архитектурную точку расширения. Решение: [AQ-SEARCH-002](04-open-questions.threads/34_AQ-SEARCH-002_semantic-search-timing/00_thread.md).

### SEARCH-MVP-SEMANTICS — Простой поиск и фильтры
**Статус:** ПОДТВЕРЖДЕНО (следующий web slice после самого первого files-only MVP)  
Текстовый поиск по title/body без учёта регистра и фильтрация по tags, date range, source, status. Использовать штатный full-text index выбранной operational БД (SQLite FTS5, PostgreSQL FTS либо подходящий эквивалент), индекс rebuildable из canonical files. Без отдельного поискового сервиса; семантический/vector, нечёткий/синонимический поиск и гарантированная русская морфология не входят в этот этап. Решение: [AQ-SEARCH-001](04-open-questions.threads/33_AQ-SEARCH-001_mvp-search-semantics/00_thread.md).

### SEARCH-INDEX-UPDATE — Асинхронная индексация и восстановление
**Статус:** ПОДТВЕРЖДЕНО  
После каждого successful canonical Save/commit в очередь направляется обновление derived search index. Поиск eventual consistent: небольшая задержка появления изменений допустима. Примерно раз в 12 часов автоматическая сверка canonical files/ревизий с indexed state выявляет пропущенные изменения, удалённые записи и запускает incremental reindex только по необходимости. Полный rebuild из canonical files поддерживается как recovery operation. Точная реализация и интервал настраиваются позже. Решения: [AQ-SEARCH-001](04-open-questions.threads/33_AQ-SEARCH-001_mvp-search-semantics/00_thread.md), [AQ-SEARCH-003](04-open-questions.threads/35_AQ-SEARCH-003_rebuild-semantics/00_thread.md).

### SEARCH-004 — Search index не обязан быть canonical
**Статус:** ПОДТВЕРЖДЕНО.

---

# N. Reliability / operations

### OPS-001 — Ошибки workflow должны быть видимыми
**Статус:** ПОДТВЕРЖДЕНО.

### OPS-RUN-LOG — История всех запусков
**Статус:** ПОДТВЕРЖДЕНО  
Для capture, sync, import и AI workflows сохраняются все запуски: run ID, время, этап, статус, число попыток, ошибка, модель (если применимо). Журнал ссылается на точные исходные и результирующие ревизии, а при отсутствии новой ревизии — на proposal/result. Полные личные данные по умолчанию не копируются; расширенная диагностика включается отдельно. Решение: [AQ-OPS-001](04-open-questions.threads/36_AQ-OPS-001_run-log/00_thread.md).

### OPS-002 — Safe retries и пользовательская политика AI-повторов
**Статус:** ПОДТВЕРЖДЕНО  
Технические retries должны сохранять identity операции и не приводить к повторному canonical commit; conscious rerun создаёт новый run. Для потенциально платных повторных AI вызовов нужна пользовательская настройка. Default — «экономия токенов»: при неопределённом исходе не выполнять повторный LLM вызов автоматически, предложить ручной повтор. Safe retries чтения, индексации и сохранения уже полученного результата допускаются отдельно. Число попыток, backoff, классификация ошибок и UI будут конкретизированы при реализации. Решение: [AQ-OPS-002](04-open-questions.threads/37_AQ-OPS-002_safe-retries/00_thread.md).

### OPS-003 — Нужна восстанавливаемость из canonical data
**Статус:** ПОДТВЕРЖДЕНО.  
После рестарта backend продолжает незавершённые технические работы на основе durable queue/state. При неизвестном исходе платного LLM-вызова повтор не инициируется автоматически в экономном режиме; пользователь решает о новом запуске. Проверка backup/restore как отдельная процедура обсуждается в [AQ-OPS-003](04-open-questions.threads/38_AQ-OPS-003_backup-restore-test/00_thread.md).

### OPS-004 — Cost guardrails
**Статус:** ПОДТВЕРЖДЕНО  
Hosting, storage, LLM usage, logs/egress не должны неожиданно создавать большой счёт.

### OPS-005 — Полный observability stack enterprise-уровня
**Статус:** УСТАРЕЛО/НЕ ТРЕБУЕТСЯ СЕЙЧАС  
Нужен достаточный debug/trace, но не overengineering.

### OPS-006 — Нужны structured application logs
**Статус:** ПОДТВЕРЖДЕНО  
Backend, background jobs и integrations должны писать структурированные логи, достаточные для диагностики ошибок и восстановления хода операции. Минимально полезный контекст включает request/job/workflow identity, timestamps, operation/result/status, retries и error details. Логи не должны без необходимости содержать полный diary content, OAuth tokens, prompts/responses или другие sensitive data.

### OPS-007 — Product analytics отделены от operational logging
**Статус:** ПОДТВЕРЖДЕНО  
Продуктовые события пользовательского поведения, например `entry_opened`, `workflow_started`, `proposal_applied`, являются отдельным telemetry layer и не должны смешиваться с backend/debug logs. Конкретный analytics provider, включая Firebase Analytics, не является обязательной частью архитектуры и может быть выбран позже отдельно для web/native clients.

---

# O. Offline и connectivity

### OFF-001 — Capture должен переживать плохую связь настолько, насколько практически возможно
**Статус:** ПОДТВЕРЖДЕНО  
Это особенно заметно из голосовых сценариев на велосипеде/в дороге.

### OFF-002 — Полный offline-first для нового web/native
**Статус:** ОТКРЫТО  
Старый Android делал offline-first центральным принципом, но для новой версии это не было повторно подтверждено как обязательное MVP-требование.

### OFF-003 — Потеря сети не должна приводить к тихой потере уже введённого текста
**Статус:** ПОДТВЕРЖДЕНО.

---

# P. Privacy и data ownership

### PRIV-001 — Дневник — чувствительные пользовательские данные
**Статус:** ПОДТВЕРЖДЕНО.

### PRIV-002 — Пользователь должен понимать, когда данные отправляются внешнему LLM provider
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ.

### PRIV-003 — Архитектура должна минимизировать ненужную передачу diary data третьим сторонам
**Статус:** ПОДТВЕРЖДЕНО КАК ПРИНЦИП.

### PRIV-004 — Локальный/on-device AI обязателен
**Статус:** ОТКРЫТО  
Это интересное будущее направление, не требование первого релиза.

---

# Q. Sharing

### SHARE-001 — Selective sharing потенциально полезен
**Статус:** FUTURE / PARKED  
Market/PRD материалы связывали sharing с retention и семейными сценариями.

### SHARE-002 — Sharing обязателен для ближайшего MVP
**Статус:** НЕТ  
Selective sharing не входит в обозримый MVP и не должен сейчас определять auth/data model. Возвращаемся к access/sharing requirements только при появлении реального near-term use case.

См. `06-future-questions.md / FQ-SHARING-001`.

---

# R. Наследие старого Android/Firebase проекта

### LEG-001 — Старый Android codebase определяет новую архитектуру
**Статус:** УСТАРЕЛО.

### LEG-002 — Старую доменную модель можно использовать как источник идей
**Статус:** ПОДТВЕРЖДЕНО.

### LEG-003 — Старый Android-клиент может позже стать native client нового API
**Статус:** ОТКРЫТО.

### LEG-004 — Firebase Data Connect migration не требуется
**Статус:** ЗАКРЫТО / НЕ ТРЕБУЕТСЯ  
В старом Android/Firebase/Room проекте нет уникальных ценных пользовательских данных, требующих отдельного migration tooling. Если позже обнаружится исключение, оно оформляется как отдельный scoped import/migration task.

---

# S. Требования к процессу разработки

### DEV-001 — Требования должны быть отделены от архитектуры
**Статус:** ПОДТВЕРЖДЕНО.

### DEV-002 — GitHub должен стать основным местом актуальной документации
**Статус:** ПОДТВЕРЖДЕНО.

### DEV-003 — Требования и архитектура должны лежать отдельно
**Статус:** ПОДТВЕРЖДЕНО  
Например `docs/requirements/` и `docs/architecture/` с cross-links.

### DEV-004 — Спорные архитектурные решения желательно фиксировать ADR
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ.

### DEV-005 — Сначала baseline требований, потом архитектура
**Статус:** ПОДТВЕРЖДЕНО.

### DEV-006 — В будущем архитектуру можно независимо прорабатывать несколькими coding/reasoning agents
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Это относится к следующей фазе, не к текущей инвентаризации.

---

# T. Старые технические решения, которые НЕ являются требованиями

Следующие вещи должны рассматриваться именно как исторические варианты, а не как обязательства:

- Firebase Data Connect;
- Firebase Storage;
- Room как source of truth;
- Cloud Functions;
- Google Sites;
- Apps Script как основной web runtime;
- Ktor;
- FastAPI;
- React;
- Cloud Run;
- конкретный формат REST/GraphQL;
- конкретная DB;
- конкретный search engine.

Их можно выбрать снова, но только после архитектурного сравнения.

## Legacy / migration

### LEGACY-001 — Старый Android codebase не является базой новой реализации
**Статус:** ПОДТВЕРЖДЕНО  
Старое Android/Firebase приложение сохраняется как historical prototype/reference. Текущий web/backend MVP не должен зависеть от его архитектуры или требовать постепенной миграции кода.

### LEGACY-002 — Миграция старых Firebase/Room данных не требуется
**Статус:** ПОДТВЕРЖДЕНО  
В старом Android/Firebase/Room нет уникальных ценных данных, требующих отдельного migration tooling. Native Android может быть спроектирован позже как новый клиент общего backend/API, когда появится реальная потребность, включая offline-first.


## Уточнение revision commit actions — 18.10.2026

Save фиксирует ручной Draft; Apply и Restore исторической версии сразу создают по одной новой committed Revision, без второго Save. Preview и Reject Revision не создают. FQ-01 закрыт: сохранены первая normalization raw и auto-apply existing tags по routine policy; изменение existing Entry создаёт Revision и trace, Draft Entries skip. [История FQ-01](04-open-questions.threads/04_PQ-004_raw-revisions-ux/01_FQ-01_revision-commit-actions/00_thread.md). Это уточняет прежнюю границу ручной editing session; история решений сохранена в PQ-004/FQ-01.


### AI auto-apply — подтверждение FQ-01 от 18.10.2026

Первая normalized Entry может создаваться автоматически из сохранённого raw с явной uncertainty; existing tags могут добавляться автоматически при высокой уверенности, если это разрешено routine policy. Изменение existing Entry создаёт новую committed Revision с trace routine/input/result; первая обработка создаёт первую committed Revision. Existing Entries с Draft пропускаются, ручной Draft AI не переписывает. Изменения текста existing Entry и создание новых тегов по умолчанию остаются proposals. Конкретные confidence thresholds не фиксируются.


## Уточнение 18.10.2026 — canonical merge тегов

Merge — операция каталога: oldTagId разрешается в survivingTagId через mergedInto redirect. Current Entry/Draft, поиск и счётчики используют canonical ID с дедупликацией; snapshots committed Revision и существующие Draft физически не переписываются, новые content Revision ради merge не создаются. Операция фиксируется в audit каталога. Следующий обычный Save может записать surviving ID; отдельной массовой миграции Entry нет. Type/color survivor и перенос aliases сохраняют ранее принятые правила.

**История:** [FQ-02](AI-Diary-Functional-Spec-v0.1.threads/01_FQ-02_tag-merge/00_thread.md). Коллизии aliases и подробное отображение historical labels остаются отдельными вопросами.


## Уточнение 18.10.2026 — неизвестный исход Save

Если подтверждение Save потеряно, приложение показывает «Проверяем сохранение» и после восстановления связи автоматически выясняет исход операции. При уже состоявшемся commit возвращается та же Revision; если commit не состоялся, безопасно повторяется та же операция с тем же operationId и зафиксированным snapshot. Повтор не создаёт дубликат и разрешён только при актуальных base/ownership checks, без отмены/замены операции. При conflict или потере права записи автоматический commit прекращается с понятным сообщением; введённые данные сохраняются. Неизвестный исход не выдаётся ни за успешное, ни за достоверно неуспешное сохранение.

**История:** [FQ-03](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/00_thread.md). Физический commit/recovery protocol ещё обсуждается; принятие автоматического retry не означает утверждения конкретной файловой реализации.


## Уточнение 18.10.2026 — editor read-only во время Save

В первой версии после начала Save редактируемые поля этой Entry и повторный Save временно блокируются до определения результата операции. Просмотр, прокрутка и копирование текста доступны. При потерянном подтверждении действует автоматическая проверка/безопасный retry той же операции, статус «Проверяем сохранение»; редактор остаётся read-only. После подтверждённого успеха редактор доступен с сохранённым состоянием. После достоверного отказа без commit и без конфликта блокировка снимается, исходный Draft сохраняется для исправления/повтора. Conflict или утрата lease разрешаются соответствующим flow; сохранённый текст не очищается и право записи самовольно не восстанавливается. Продолжение ввода параллельно неподтверждённому Save в первую версию не включается.

**История:** [FQ-03](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/00_thread.md). Выбор временной блокировки не определяет физический commit/recovery protocol; этот технический вопрос остаётся открытым.


## Уточнение 18.10.2026 — уникальность aliases

Один и тот же alias не может принадлежать двум самостоятельным активным canonical tags. Если alias уже занят, добавление его второму тегу отклоняется с указанием существующего тега; существующие теги автоматически не объединяются. Повторы aliases внутри одного canonical tag дедуплицируются. Merge redirect разрешается в survivor и не считается вторым самостоятельным владельцем alias.

**История:** [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Позднее 18.10 также принят запрет пересечений canonical name/alias между разными активными тегами; сравнение без учёта регистра также принято; резервирование обозначений удалённых тегов также принято; остальные правила Unicode/пробелов ещё открыты.


## Уточнение 18.10.2026 — names/aliases и границы scope

Canonical names и aliases образуют единое пространство уникальных обозначений между самостоятельными активными canonical tags. Нельзя создать отдельный тег с именем, уже занятым как name или alias другого тега, либо назначить ему такое имя/alias. При конфликте показывается существующий тег; запись дубликата отклоняется без автоматического merge, переноса обозначения или перепривязки Entry relations. Идея отдельного переноса имени/alias между тегами сохранена на будущее; в текущий scope такой сценарий не включён.

**История:** [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Transfer обозначения не требуется реализовывать сейчас и не означает автоматическую смену существующих relations по tagId.


## Уточнение 18.10.2026 — маркер снятого тега

При Save упоминания явно снятого через chip тега преобразуются из #name в #_name, включая употреблённые aliases, с сохранением написанного обозначения. Маркер #_name остаётся в тексте, чтобы такие места можно было найти Text search; он не является активным hashtag, не создаёт связь и не восстанавливает chip. Не считать #_name присутствующим активным упоминанием при нормализации linked tags; обычный Tag filter по-прежнему работает по tagId/relations. Преобразование затрагивает упоминания снятого тега, а не все символы # в документе; повторный Save не добавляет второй underscore. Если тег добавлен обратно до Save, его упоминания не помечаются как снятые. Дополнительный вопрос на каждом Save для этого преобразования не требуется.

**История:** [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Сам маркер не означает действующую связь и не является новым catalog tag.

## Уточнение 18.10.2026 — регистр names/aliases

Canonical names и aliases сравниваются без учёта регистра при проверке уникальности и lookup, включая autocomplete. Спорт, спорт и СПОРТ считаются одним обозначением; различие только в регистре не позволяет создать второй самостоятельный тег или занять его обозначение. Выбранное пользователем написание сохраняется для отображения, автоматическое приведение отображаемого текста к нижнему регистру не требуется. Это правило не меняет tagId и не переписывает существующий текст или immutable snapshots.

**История:** [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Обозначения удалённых тегов остаются занятыми; остальные правила Unicode/пробелов пока открыты.

## Уточнение 18.10.2026 — обозначения удалённых тегов

После soft delete тега его canonical name и aliases остаются занятыми за тем же tagId, в общем пространстве обозначений без учёта регистра. Нельзя создать другой тег или назначить ему name/alias, совпадающий с обозначением удалённого тега. При таком конфликте интерфейс показывает удалённый тег и предлагает явный Restore существующего тега вместо создания нового. Сам ввод имени не восстанавливает тег автоматически. До Restore сохраняется запрет новых links и исключение удалённого тега из обычных autocomplete/cloud; прежние tagId, relations и история сохраняются.

**История:** [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Отдельный перенос имени/alias между tagIds в текущий scope не добавляется.

## Уточнение 18.10.2026 — формат дописываемых hashtags

При Save недостающие упоминания связанных тегов дописываются в конец body одной строкой, hashtags разделяются одним пробелом. От непустого текста эта строка отделяется пустой строкой; отдельного заголовка Tags: нет. Уже имеющиеся canonical/alias упоминания остаются на своих местах и не дублируются. Если все связанные теги уже упомянуты, новая строка не добавляется; повторный Save не создаёт повторный suffix. В пустом body добавляется только строка hashtags, без ведущей пустой строки. Маркер #_name не считается активным упоминанием.

**История:** [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Это уточняет оформление уже принятого добавления linked hashtags в конец текста.

## Техническая проработка хранения и Save — 18.10.2026

По поручению пользователя подготовлены [проект формата v1](07-file-format-v1-draft.md), [Save/recovery design](08-save-recovery-design.md), core schema и пример before/register/after. Статус: **РАБОЧЕЕ_НАПРАВЛЕНИЕ / техническое предложение**, не новый утверждённый baseline и не выполненная migration. Предложены immutable snapshots + единая publication для Entry/catalog/operation result/consume Draft; Drive adapter требует integration spike. Уже принятые Save/Apply/Restore, retry, read-only editor и правила тегов сохраняются.

Решён [FQ-03/SQ-01: Save при незавершённом upload](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md): Save disabled до готовности всех оставленных вложений; состав attachments и upload state сохраняются в Draft. Retention/orphan cleanup, hashtag grammar и time semantics не закрываются техническим проектом; no-change manual Save согласован отдельно в SQ-02.

## Уточнение 18.10.2026 — вложения входят в durable Draft

Save недоступен, пока хотя бы одно оставленное вложение имеет неразрешённый статус: выбрано, загружается, проверяется, ошибка или требуется повторный выбор файла. Для продолжения нужно завершить загрузку/проверку, повторить её либо явно убрать вложение. Все оставленные attachments должны быть готовы к включению в Revision; для managed файла это подтверждённый original, для external — сохранённый валидный reference без обязательного скачивания original. Генерация thumbnail/preview не блокирует Save. До начала commit текст продолжает autosave в Draft.

Draft сохраняет весь состав вложений: связи с готовыми Asset, pending upload IDs, имена файлов, статусы и ссылки на durable upload/staging records. Успешно загруженные originals сохраняются в user-owned storage и остаются достижимыми из Draft до завершения Save или явного действия пользователя; уход со страницы и повторное открытие не должны терять вложения. Pending запись не исчезает при ошибке или перезапуске. Bytes, ещё не полученные хранилищем, не выдаются за durable: если продолжить upload автоматически нельзя, Draft сохраняет attachment intent и показывает «Выберите файл повторно». Удалять staging/original, на который ссылается актуальный Draft или незавершённая операция, нельзя.

**История:** [FQ-03/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md). Retention после Discard/orphan cleanup остаётся отдельным FQ-08; физический commit protocol этим решением не утверждён.

## Уточнение 18.10.2026 — manual Save без изменения content

Manual Save, при котором итоговое сохраняемое content совпадает с текущей committed Revision, завершает эквивалентный Draft без новой Revision. Возвращается NO_CHANGE со ссылкой на существующую Revision; committedUpdatedAt и content History не меняются. Consume именно этого Draft и результат операции фиксируются durable с обычными ownership/base/idempotency checks. У новой Entry без Current первый успешный Save создаёт первую Revision. Согласованное создание Revision при Apply/Restore сохраняется.

Технически сравнивается итоговый snapshot Title/Text/EventTimeRange/канонические Tag relations/Asset links; служебные Draft/session timestamps не участвуют. Текст сравнивается точно, включая пробелы и регистр. **История:** [FQ-03/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md).

## Уточнение 18.10.2026 — Asset после снятия связи / Discard

При снятии связи Asset с записью, в том числе при Discard добавлений Draft, применяется одно правило: если снимаемая связь единственная, предложить удалить сам Asset; если есть другие логические связи, снять только текущую без предложения глобального удаления в этом flow. Удаление — только по явному подтверждению и означает soft delete в Asset Trash, не permanent delete. При отказе от удаления связь всё равно снимается, Asset остаётся в библиотеке; при отсутствии Active Entry links он виден в Unlinked.

Проверяются логические потребители по разным entryId во всех lifecycle-состояниях, в других Draft и связанных незавершённых операциях; исторические references других Entries не теряются. Несколько Revision/Draft одной и той же Entry не считаются отдельными записями; historical link той же Entry сам по себе не запрещает предложить soft delete, поскольку история/links сохраняются. При Discard рассматриваются только связи, реально исчезающие относительно восстанавливаемой Current: Asset, остающийся в Current, не является кандидатом на удаление из-за Discard. Проверка актуальна перед выполнением; при новой чужой связи выполняется только unlink. Состояние Unlinked по Active-счётчику не используется как доказательство единственности. Незавершённая операция с неизвестным исходом сначала требует reconciliation.

**История:** [FQ-08 — снятие связи / Discard](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/00_thread.md). Готовые attachments получили policy; прочие FQ-08 — partial staging/late completion, permanent delete и retention — остаются открытыми; lifecycle после Restore согласован отдельно в SQ-01. Ранее предложенные безусловные keep/Trash не приняты.

## Уточнение 18.10.2026 — Restore Entry из Trash всегда в ACTIVE

Restore Entry из Trash всегда возвращает запись в ACTIVE, независимо от того, была она Active или Archived перед удалением. Сохраняются тот же entryId, Current/content history и существующий durable Draft. Операция меняет lifecycle/audit и не создаёт content Revision; это не Restore исторической Revision.

**История:** [FQ-08/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/01_SQ-01_restore-lifecycle/00_thread.md). Прежнее архивное состояние не возвращается автоматически. Остальные FQ-08 остаются открытыми.

## Уточнение 18.10.2026 — overlap при фильтрации по периоду

Фильтр по периоду включает интервальную Entry, если хотя бы часть её EventTimeRange пересекается с выбранным периодом; не требуется попадание начала или всего интервала внутрь фильтра. Например, поездка 1–10 июля видна при фильтре 5–7 июля. Одна Entry показывается один раз, независимо от количества пересекающихся дней. Это общее правило date filter; выбор календаря и связанные выборки используют ту же semantics при неизменном lifecycle scope.

**История:** [FQ-05 — пересечение периодов](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/00_thread.md). Остальные FQ-05 (границы/timezone/precision/uncertainty/отсутствующий To) остаются открытыми.

## Уточнение 18.10.2026 — сортировка Updated учитывает Draft

Сортировка «По изменению» учитывает последние содержательные правки Draft ещё до Save: при текущем Draft используется его content updatedAt, без Draft — committedUpdatedAt Entry. Это производный effectiveUpdatedAt для сортировки, а не изменение committed metadata и не новая Revision. Повторный autosave неизменного содержимого, heartbeat и технический progress загрузки не поднимают Entry заново. После Discard/NO_CHANGE без Draft используется прежний committedUpdatedAt.

**История:** [FQ-06 — Updated sort](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/00_thread.md). Принятое правило относится именно к Updated sort. Scope двух рабочих очередей Home согласован ниже; scope Total entries согласован отдельно ниже; scope периодных counters согласован ниже; timezone rolling days согласована ниже; полная модель review items остаётся открытой.

## Уточнение 18.10.2026 — lifecycle рабочих очередей Home

Очереди «Черновики» / «Требует внимания» на Home включают ACTIVE и ARCHIVED Entries за всё время и исключают TRASH. Счётчик и список по клику используют одинаковые условия lifecycle и соответствующего признака; одна Entry считается один раз, независимо от числа review items.

Это решение не меняет ACTIVE scope Home EntryList/TagCloud и не выбирает lifecycle-охват Total entries/остальных counters. Архивирование в текущем ТЗ выполняется явным действием пользователя; автоматический перенос по возрасту не задан. Запись, история и имеющийся Draft сохраняются. **История:** [FQ-06/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/01_SQ-01_home-queue-scope/00_thread.md).

## Уточнение 18.10.2026 — Total entries включает архив

«Всего записей» / Total entries на Home считает уникальные ACTIVE и ARCHIVED Entries за всё время, исключая TRASH. Переход по числу открывает список с теми же условиями lifecycle и без ограничения периода. Архивация не уменьшает этот показатель; число Revision одной Entry на него не влияет.

Это не меняет ACTIVE scope Home EntryList/TagCloud. Периодные статистические counters согласованы отдельно ниже; полная модель review items остаётся открытой. **История:** [FQ-06/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/02_SQ-02_total-entries-scope/00_thread.md).

## Уточнение 18.10.2026 — lifecycle периодной статистики Home

Показатели Home «За 7 дней», «За 30 дней» и «С вложениями за 30 дней» включают уникальные ACTIVE и ARCHIVED Entries и исключают TRASH. Сохраняются соответствующие периоды Event date (сегодня + предыдущие 6 / 29 дней), принятое пересечение интервалов и условие Has assets у третьего показателя. Число и список по клику используют одинаковые условия; архивация не исключает запись из статистики периода.

Это не меняет ACTIVE scope Home EntryList/TagCloud. Timezone границы rolling days и прочие аспекты FQ-05/FQ-06 этим решением не закрываются. **История:** [FQ-06/SQ-03](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/03_SQ-03_period-counter-scope/00_thread.md).

## Уточнение 18.10.2026 — время события и default timezone

Основное отображение Entry использует местные дату и время события в его сохранённом часовом поясе. При ручном создании пояс события по умолчанию берётся из настроек пользователя, если он там задан; иначе сохраняется прежний fallback на пояс устройства. Явно выбранный пояс события имеет приоритет над default. Пояс сохраняется в EventTimeRange записи; последующая смена пользовательских настроек не пересчитывает и не переписывает её местные дату/время или timezone. Если время суток отсутствует, оно не подставляется.

Выбор основного отображения не утверждает физическую сериализацию instant/offset, обработку неоднозначного времени, отдельный UI пересчёта или правило группирования Calendar. Настройка rolling days обсуждается отдельно. **История:** [FQ-05/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/02_SQ-02_event-time-display/00_thread.md).

## Уточнение 18.10.2026 — Calendar по местным датам событий

Calendar относит Entry к местной дате события в сохранённой timezone самой записи. Событие «19 октября, 00:30, Токио» показывается на 19 октября, даже если в пользовательской timezone в этот момент ещё 18-е. Выбор дня/диапазона в Calendar открывает список с той же семантикой местных дат и принятым period overlap; индикатор и список используют одинаковый lifecycle scope. Смена пользовательской timezone не переносит сохранённые события между днями Calendar. Date-only сохраняется как дата без выдуманного времени.

Выбранный lifecycle scope не расширяется автоматически. Источник «сегодня» для rolling days, точные временные границы и mixed precision остаются отдельными аспектами FQ-05. **История:** [FQ-05/SQ-03](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/03_SQ-03_calendar-event-date/00_thread.md).

## Уточнение 18.10.2026 — timezone пользователя для «сегодня»

«Сегодня» и границы календарных rolling days Home определяются по сохранённому часовому поясу из настроек пользователя. При первоначальной настройке предлагается пояс устройства. Если обнаружено отличие пояса устройства от сохранённого пользовательского, приложение предлагает сменить настройку и применяет изменение только после подтверждения. Смена настройки может изменить текущее «сегодня» и период статистики, но не переписывает даты/время/timezone сохранённых событий и не переносит их между днями Calendar.

Периоды остаются «сегодня + 6 / 29 предыдущих дней»; число и список по клику используют одинаковый период. Точный layout настройки и частота повторного предложения смены зоны этим выбором не определены. **История:** [FQ-05/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/01_SQ-01_rolling-day-timezone/00_thread.md).

## Уточнение 18.10.2026 — запись без окончания

Отсутствие To у Entry означает одиночное событие на указанную From дату/время, без автоматического продолжения до текущего дня или в будущее. Если указана только дата, дневной Calendar и связанный date filter относят запись к этой местной дате без выдуманного времени суток. Если задано время, опорой служит указанный момент без придуманной длительности. Это правило не меняет односторонние границы query filter.

Отдельное ongoing-состояние не вводится. Точные граничные и mixed-precision comparisons этим решением не утверждаются. **История:** [FQ-05/SQ-04](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/04_SQ-04_missing-event-end/00_thread.md).

## Уточнение 18.10.2026 — последний день date-only интервала включён

У интервала записи с From/To, заданными датами без времени, последний указанный день To включается целиком в пользовательском смысле. «Поездка 1–10 июля» видна и при выборе 10 июля. Date-only верхняя граница фильтра «по 10 июля» также включает весь указанный день. Сохранённые значения остаются date-only: фиктивные 00:00/23:59:59 в EventTimeRange не записываются.

Это правило не выбирает автоматически точные clock/mixed-precision/DST comparisons. **История:** [FQ-05/SQ-05](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/05_SQ-05_date-only-end-inclusion/00_thread.md).

## Уточнение 18.10.2026 — date-only запись в фильтре по часам

Запись с известной датой, но без времени суток, включается в фильтр по часам того же дня как возможное совпадение. Например, «18 октября» без времени попадает в «18 октября, 12:00–14:00». В результате сохраняется явная пометка «время не указано»; запись не получает выдуманные часы, длительность на весь день или новое content-значение.

Точная формализация разных timezone, mixed precision и DST этим решением не закрывается. **История:** [FQ-05/SQ-06](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/06_SQ-06_date-only-clock-filter/00_thread.md).

## Уточнение 18.10.2026 — визуальная важность AI-работы

**[Д, направление UX пользователя]** Пока AI-обработка ожидает запланированного запуска, выполняется или ожидает автоматического продолжения/повтора, её состояние показывается менее заметно, чем причины, требующие действия пользователя. Scope Needs attention согласован ниже: фоновая работа сама по себе не входит в очередь и счётчик.

Статусы/предупреждения для штатной работы, автоматического retry и остановки до действия пользователя предложены отдельно в экранном ТЗ §26.31. Scope очереди и счётчика согласован отдельным решением ниже; конкретные цвета и retry-policy остаются открытыми. **Обсуждение:** [FQ-06/SQ-04](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/04_SQ-04_failed-ai-attention/00_thread.md).

## Уточнение 18.10.2026 — сводный статус параллельных AI runs на Entry

**Статус:** ПОДТВЕРЖДЕНО пользователем. Если над одной Entry одновременно выполняются несколько AI workflows, карточка показывает один ненавязчивый агрегированный статус, например «AI обрабатывает · 2 задачи». По клику раскрывается список отдельных runs с названием workflow, выбранной моделью, текущим состоянием/этапом и доступом к деталям запуска. Не показывать отдельный статус на карточке для каждого параллельного run. Технический worker не требуется выводить как «кто обрабатывает»; показываем понятные пользователю workflow и provider/model. Агрегированный статус штатной работы не добавляет запись в Needs attention; независимые актуальные проблемы, требующие действия, по-прежнему показываются отдельно. **Согласовано в разговоре 18.10.2026.**

## Уточнение 18.10.2026 — Needs attention требует пользователя

В очередь, фильтр и счётчик «Требует внимания» входят только актуальные причины, требующие действия пользователя, в том числе ошибка AI-обработки, после которой без пользователя продолжить нельзя. Ожидание запланированного запуска, выполняющаяся обработка и назначенный автоматический повтор сами по себе не добавляют Entry в Needs attention: они показываются спокойным статусом, а временная ошибка с автоповтором — мягким предупреждением. Независимые причины внимания, например открытый proposal или conflict, при этом сохраняются. Одна Entry считается один раз; старый уже разрешённый failed run сам по себе причиной не является.

Lifecycle Home очереди — ACTIVE + ARCHIVED, без TRASH; число и список имеют одинаковый predicate. Возможность ручного снятия причины ошибки без повторного запуска согласована отдельным решением ниже. **История:** [FQ-06/SQ-04](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/04_SQ-04_failed-ai-attention/00_thread.md).

## Уточнение 18.10.2026 — убрать конкретную ошибку AI из внимания

Пользователь может явно убрать из «Требует внимания» конкретную причину ошибки AI без успешного повторного запуска, если обработка больше не нужна. Снимается только эта причина; неуспешный Run и его история сохраняются и не помечаются успешными. Другие причины внимания Entry остаются; при отсутствии остальных причин Entry выходит из очереди и счётчика. Новая ошибка нового запуска может снова потребовать внимания и не наследует снятие прежней. Действие не удаляет Entry/историю, не создаёт content Revision, не выключает routine глобально и не отменяет выполняющийся job.

Снятие причины фиксируется как явное пользовательское решение; физическая структура resolution/audit относится к техническому проекту. **История:** [FQ-06/SQ-05](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/05_SQ-05_dismiss-ai-error/00_thread.md).

## Уточнение 18.10.2026 — трёхпанельный review и «Принято частично»

Подробный review использует три панели: исходник Base — сохранённое состояние, на котором работал AI, только чтение; Result — редактируемый будущий итог; Proposal — исходное предложение AI, только чтение. В Result и Proposal подсвечиваются изменения относительно Base. Если пользователь принимает только часть предложения и подтверждает итоговый Result, proposal получает понятный статус «Принято частично» и закрывается целиком как разобранный. Создаётся одна committed Revision с подтверждённым Result, без дополнительного Save. Исходный Proposal и итоговый Result/Revision сохраняются в AI history; непринятые части не остаются pending и автоматически не превращаются в новые proposals. Причина внимания этого proposal снимается, остальные причины Entry сохраняются.

Точный storage outcome enum требует технической конкретизации; восстановление незавершённого review Result согласовано ниже; общий manual Apply/Restore Revision contract сохраняется. **История:** [FQ-07](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/00_thread.md).

## Уточнение 18.10.2026 — автосохранение прогресса AI review

Незавершённый Result подробного AI review автоматически сохраняется как черновик разбора и восстанавливается после выхода, reload и следующего сеанса — по тому же принципу, что Draft записи. Пока Apply не подтверждён, исходный proposal остаётся pending, Current Entry и committed History не меняются. При возвращении ручные правки Result сохраняются; если Current изменился, выполняется обычная проверка base/current и разрешение conflicts без silent overwrite. Черновик разбора не подменяет существующий WorkingDraft ручного редактирования.

При неприменённых изменениях сохраняется принцип явного выбора при уходе: применить, отбросить правки разбора или вернуться позже. Неприменённый Result не создаёт content Revision; точные file paths/schema и recovery относятся к техническому проекту. **История:** [FQ-07/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/01_SQ-01_review-draft-resume/00_thread.md).

## Уточнение 18.10.2026 — обычный повтор после ошибки AI

Достоверно failed AI Run без успешного результата не считается успешно already processed. Обычный повтор той же routineVersion/input Revision разрешён даже без изменения записи; обычный batch не пропускает запись только из-за такого failure. Неуспешный Run остаётся в истории. Для успешно выполненной обработки прежние already-processed правила сохраняются независимо от принятия/отклонения proposal; сознательный повтор успешной обработки использует Force rerun. Это правило не разрешает слепой повтор при неизвестном исходе и не меняет пользовательскую политику платных автоматических AI retries.

Queued/running работа не дублируется; неизвестный исход сначала требует определения результата. Уже принятое в [AQ-OPS-002](04-open-questions.threads/37_AQ-OPS-002_safe-retries/00_thread.md) разделение safe technical retry и potentially paid AI rerun сохраняется; текущий выбор определяет eligibility после failure, а не новый автоматический бюджет. **История:** [FQ-07/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/02_SQ-02_failed-run-retry/00_thread.md).
