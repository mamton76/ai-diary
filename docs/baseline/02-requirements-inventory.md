# AI Diary — инвентаризация требований

**Дата среза:** 2026-09-26  
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
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Особенно при web/multi-device и параллельной AI-обработке.


### REV-007 — Current Entry и History/Revisions разделены в UX
**Статус:** ПОДТВЕРЖДЕНО  
Основной экран Entry показывает актуальное состояние записи и действия над ним. Raw/original и история изменений доступны через отдельный History/Revisions view и не обязаны постоянно занимать место рядом с текущей записью.

### REV-008 — Manual revision соответствует завершённой editing session
**Статус:** ПОДТВЕРЖДЕНО  
Manual editing session начинается с первой фактической правки. Autosave внутри session не создаёт revisions. Одна завершённая session создаёт одну manual revision: при явном Save или после 1 часа inactivity. Не вводится эвристика «мелкое/крупное изменение».

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

### ASSET-004 — Конкретный media backend
**Статус:** ОТКРЫТО  
Старое решение — Firebase Storage; file-first направление допускает Drive/file storage. Архитектура должна решить это отдельно.

### ASSET-005 — Одна media сущность может быть связана с несколькими entries
**Статус:** ПОДТВЕРЖДЕНО.

### ASSET-006 — Remove asset из Entry различает unlink и delete
**Статус:** ПОДТВЕРЖДЕНО  
В edit UX действие удаления asset открывает явный выбор: отвязать от текущей Entry и оставить в Asset Library либо удалить asset из системы. Если asset используется несколькими entries, destructive delete предупреждает о затрагиваемых связях; если после unlink asset станет orphaned, это также явно показывается.

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

### DATA-009 — Нужны versioning формата и migrations
**Статус:** ПОДТВЕРЖДЕНО.

### DATA-010 — Нужны backup/export/restore semantics
**Статус:** ПОДТВЕРЖДЕНО.

### DATA-011 — Manual file edits не должны приводить к тихой потере данных
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Особенно важно, если canonical data остаётся в Drive и пользователь теоретически может открыть файлы напрямую.


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
`EntryScreen` содержит surrounding UX: navigation/actions, Proposals, History/Revisions, Sources/Lineage, AI activity/details. `EntryPanel` показывает одно состояние самой записи и переиспользуется в view/edit/merge.

### WEB-011 — EntryPanel имеет общую структуру для view/edit/merge
**Статус:** ПОДТВЕРЖДЕНО  
Минимальные области: Title; Event date + optional start/end; Text; Assets; Tags; вторичная read-only system metadata created/updated. Title и Text редактируются в edit/result mode; date/start/end получают date/time controls; Tags и Assets получают add/remove actions. Add поддерживает выбор существующей сущности или создание новой (Asset Library/new asset; tag catalog/new tag). Base/Proposal в merge read-only, Result editable.

### WEB-012 — EntryPanel адаптируется по собственной ширине
**Статус:** ПОДТВЕРЖДЕНО  
При достаточной ширине Text занимает основную content column, а Assets, Tags и secondary created/updated metadata показываются справа. При узкой panel эти секции переходят под Text. Правило зависит от ширины самой EntryPanel, а не только viewport, чтобы тот же component автоматически работал в обычном Entry detail и в узких `Base | Result | Proposal` колонках. Точные breakpoint/column ratios — UI implementation detail.

---

# I. Backend / API

### API-001 — Нужен отдельный backend API
**Статус:** ПОДТВЕРЖДЕНО.

### API-002 — API должен быть client-agnostic
**Статус:** ПОДТВЕРЖДЕНО.

### API-003 — Backend framework/language
**Статус:** ОТКРЫТО  
Kotlin/Ktor удобен владельцу проекта; Python/FastAPI и TypeScript/Node остаются кандидатами.

### API-004 — Production runtime/hosting
**Статус:** ОТКРЫТО  
Cloud Run сейчас выглядит сильным кандидатом, но это ещё не архитектурный факт.

### API-005 — Низкая стоимость и низкая операционная нагрузка
**Статус:** ПОДТВЕРЖДЕНО  
Для личного проекта предпочтительны free/very-low-cost tiers и минимум DevOps.

### API-006 — Нужны background jobs
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
AI, indexing, import, Calendar sync и migrations не всегда стоит выполнять синхронно в HTTP-request.

### API-007 — Один repo может содержать web/backend/android
**Статус:** ПОДТВЕРЖДЕНО КАК ДОПУСТИМОЕ  
Нет требования немедленно разделять продукт по разным репозиториям. Точная структура — архитектурный вопрос.

---

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
**Статус:** РАБОЧЕЕ_НАПРАВЛЕНИЕ  
Вероятно понадобится для cross-entry AI, но не обязательно для первого MVP.

### SEARCH-004 — Search index не обязан быть canonical
**Статус:** ПОДТВЕРЖДЕНО.

---

# N. Reliability / operations

### OPS-001 — Ошибки workflow должны быть видимыми
**Статус:** ПОДТВЕРЖДЕНО.

### OPS-002 — Должны быть safe retry semantics
**Статус:** ПОДТВЕРЖДЕНО.

### OPS-003 — Нужна восстанавливаемость из canonical data
**Статус:** ПОДТВЕРЖДЕНО.

### OPS-004 — Cost guardrails
**Статус:** ПОДТВЕРЖДЕНО  
Hosting, storage, LLM usage, logs/egress не должны неожиданно создавать большой счёт.

### OPS-005 — Полный observability stack enterprise-уровня
**Статус:** УСТАРЕЛО/НЕ ТРЕБУЕТСЯ СЕЙЧАС  
Нужен достаточный debug/trace, но не overengineering.

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

### LEG-004 — Firebase Data Connect обязательно мигрировать
**Статус:** ОТКРЫТО  
Сначала нужно понять, есть ли там реальные пользовательские данные, которые нельзя просто отбросить.

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
