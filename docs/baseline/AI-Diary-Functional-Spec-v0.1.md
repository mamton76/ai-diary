# AI Diary — функциональное ТЗ системы

Версия: **0.1 — консолидация согласованных требований**  
Дата: **4 октября 2026**  
Статус: рабочая спецификация для разработки; открытые вопросы перечислены отдельно. Новым GitHub baseline автоматически не объявлена.

## 1. Назначение и комплект документации

Документ определяет, **что система делает с данными, какие правила обязана соблюдать и как проверять результат**, независимо от конкретного экрана. Он дополняет `AI-Diary-Screens-Spec-v0.1.md` с внутренней версией **0.5** (далее **UI-0.5**). Изменение имени файла экранного ТЗ не требуется для понимания его версии.

| Документ | Ответственность | Текущее состояние |
|---|---|---|
| Продуктовый baseline | Цели, границы продукта, приоритеты и принятые решения | Уже существует в ветке `docs/requirements-baseline`; требует последующей синхронизации с решениями 04.10 |
| Это функциональное ТЗ | Сущности, инварианты, сценарии, операции, хранение, обработка AI, backend, приёмка | Составлено по обсуждениям и UI-0.5 |
| UI-0.5 | Экраны, общие компоненты, controls, переходы, адаптивность, UI acceptance criteria | Сверено со всеми 49 разделами договорённостей 04.10 |
| Технический проект / ADR | Конкретные API, файловые схемы, commit protocol, concurrency, index/rebuild, deployment | Следующий документ после закрытия блокирующих вопросов; здесь не выдаётся за готовый |
| План реализации | Задачи и релизы на основе требований | Составляется по выбранному этапу, не заменяет ТЗ |

Смысловые изменения должны согласованно попадать в функциональное ТЗ и UI. История обсуждений служит основанием решения, но разработчику не требуется восстанавливать действующее поведение по переписке.

### Источники и статусы

- **D04:** предоставленный пользователем `AI-Diary_discussion_decisions_2026-10-04(1).md`, все 49 разделов. Основной источник новых решений.
- **UI-0.5:** текущая спецификация экранов; включает проверенный при первоначальной сборке GitHub baseline и уточнения D04. Репозиторий в рамках этой сборки повторно не проверялся.
- **[Д]** — принято в D04; **[Б]** — унаследовано из baseline, отражённого в UI-0.5; **[П]** — предложенная конкретизация, ещё не утверждена; **[О]** — открытый вопрос; **[F]** — future.

Приоритет имеют новые прямые решения пользователя. Неоднозначность между документами выносится в §14, а не разрешается молчаливым выбором разработчика. Правило «Revision только по Save» относится безусловно к ручному Draft; сочетание с Apply/Restore и прежними автоматическими AI-изменениями требует уточнения FQ-01.

Старые Android/Firebase документы — исторический контекст. Из них не переносятся требования к стеку текущего web-приложения или устаревшие lifecycle-статусы.

## 2. Цель, пользователи и границы

**[Б]** AI Diary — персональная система памяти: быстро сохранять записи и материалы, находить их по времени, содержанию и тегам, возвращаться к прежним версиям, получать проверяемую помощь AI. Принцип — capture first, structure later. Title и tags не должны становиться обязательным барьером для захвата материала.

**[Б]** Пользователь владеет своими данными; AI помогает обрабатывать их, не становится владельцем дневника и не переписывает исходный текст молча. Пользователи изолированы. Sharing и совместное редактирование не входят в текущий MVP.

**[Д/Б] В охвате полного продукта:** Entry и Draft/Revision; каталог Tags и Types; Asset library; фильтры/поиск и производные показатели; routines/runs/proposals; подключение user-owned storage; сохранность, восстановление и переносимость. Calendar capture/timeline — отдельный интеграционный этап.

**[F]** Full offline-first, merge/split Entries, bulk AI mutation/delete, custom Saved Filters, regex/раздельные title-body filters, inline assets/rich-text сценарии, advanced AI memory, сложная онтология людей/мест. Batch launch для анализа/предложений уже входит в охват и не равен разрешению произвольной bulk mutation.

Наличие требования в этом ТЗ не объявляет его обязательным для первого релиза. Этапы — §13.

## 3. Доменная модель

Это концептуальные сущности, не готовая SQL-схема или JSON Schema.

| Сущность | Назначение и минимальный смысл | Основные связи |
|---|---|---|
| Entry | Stable entryId, lifecycle, currentRevisionId при наличии сохранённой версии, системные metadata | Версии, raw/provenance, runs/proposals |
| EntryVersion | Состояние содержимого: Title, EventTimeRange, Text, tagIds, Asset links | Принадлежит Entry; DRAFT или COMMITTED |
| Draft | Изменяемая EntryVersion; максимум одна текущая на Entry; полный snapshot | Base revision/version, собственные updatedAt/session metadata |
| Revision | Immutable committed EntryVersion; слово Revision в UI применяется только к ней | Previous/base, origin, операция и provenance |
| EventTimeRange | from, optional to, timeZone; сохраняет точность date-only | Versioned content Entry |
| Tag | Stable tagId, canonical name, aliases, color, optional typeId; deleted или merge redirect | Current/historical Entry relations; TagType |
| TagType | Пользовательский справочник, не system enum | Необязательный тип Tag, без наследования цвета |
| Asset | Stable assetId, metadata, managed original либо external reference, deletion state | Связи с несколькими Entry; historical references |
| Raw input / provenance | Исходный материал и происхождение результата | Entry, revision, asset, capture operation |
| Routine | System либо user routine, версия, instructions, eligibility и application policy | Runs; пользовательская копия system routine |
| Run / AIResult | Запуск, inputs, фактические model/provider, результат и outcome | Routine/version, Entry/input Revision, proposals/revisions |
| Proposal | Сохранённое предложение изменения с base и resolution | Run; Entry; созданная Revision при Apply |
| Review item | Концептуальная причина Needs attention: proposal, conflict, uncertainty и др. | Точная модель пока [О], не новый lifecycle Entry |
| Filter expression / preset | Условия и вложенные AND/OR/NOT; системный шаблон выборки | ID тегов, поля Entry, производные признаки |

**[Д]** entryId, createdAt, raw/source/provenance, history и proposals не входят в обычное редактируемое содержимое EntryVersion. Archive/Delete — отдельные lifecycle-операции. Собственный updatedAt Draft не равен committed updatedAt Entry.

### Инварианты

| ID | Правило |
|---|---|
| INV-01 [Д] | Все authoritative пользовательские факты находятся в user-owned file storage; backend DB/cache/index полностью восстанавливаемы |
| INV-02 [Д] | У Entry не более одного текущего Draft; committed Revision immutable |
| INV-03 [Д] | Autosave сохраняет Draft и не меняет committed currentRevisionId/updatedAt; таймер не создаёт Revision |
| INV-04 [Д] | Draft — полный durable snapshot; история его autosave-снимков не ведётся |
| INV-05 [Д] | tagId и Asset links определяют связи; hashtag и display name не заменяют идентичность |
| INV-06 [Д] | Rename/merge/delete Tag не переписывают immutable Revisions |
| INV-07 [Д] | Draft не является lifecycle Entry; Needs attention тоже не является lifecycle |
| INV-08 [Д] | AI routine получает committed input; отдельный запуск требует Save существующего Draft, batch пропускает Draft |
| INV-09 [Б] | Потерявший mutation lease исполнитель не может commit поверх актуальной версии |
| INV-10 [Б] | Повтор после timeout не создаёт duplicate Entry/revision/Apply; отсутствие подтверждения не считается успешным Save |
| INV-11 [Д] | Permanent delete Asset удаляет bytes/preview, но сохраняет tombstone для исторических ссылок |
| INV-12 [Д] | Списки используют текущее Draft-state при его наличии, без второй строки той же Entry |

## 4. Entry, Draft, Save и история

### 4.1. Контракт операций

| ID / операция | Предусловие / вход | Результат | Что не должно произойти |
|---|---|---|---|
| ENT-01 [Д] Create | Пользователь создаёт Entry | Сразу entryId и папка; Draft без committed Revision; Entry видна с badge Draft | Пустая фиктивная Revision до Save |
| ENT-02 [Д] Edit | Новая Entry или редактирование existing | Тот же Draft принимает Title/Text/EventTimeRange/Tags/Asset links | Независимые drafts от inline и full editor |
| ENT-03 [Д] Autosave | Изменённый Draft | Полный snapshot в пользовательских файлах; отдельный Draft saved status | Commit, обновление committed timestamps или autosave-history |
| ENT-04 [Д] Save | Валидный Draft; проверены base и право mutation | Новая Revision с ID/номером, новый currentRevisionId; после успеха Draft удалён | Потеря Draft при failed commit |
| ENT-05 [Д] Discard | Есть Draft | Draft удалён, показана последняя committed Revision; новая несохранённая Entry отменяется | Новая content Revision; случайно созданный canonical tag остаётся в каталоге |
| ENT-06 [Д] Return later | Пользователь покидает изменённую запись | Draft сохранён, уход разрешён, badge остаётся | Неявный commit/discard |
| ENT-07 [Д] Compare | Выбраны Revision/Revision либо base Revision/Draft | Полный Entry diff; Draft editable, Revision read-only | Редактирование immutable исторической версии |
| ENT-08 [Б] Restore revision | Выбрана история; разрешены текущий Draft/conflict/lease | Новая Revision с restored-from reference; прежняя история сохранена | Перемотка указателя с удалением более новых revisions |

**[Б]** Ручная editing session начинается с первой правки, не от открытия записи для чтения. Операции одинаковы независимо от места входа. При сворачивании/смене карточки и уходе с нового unsaved Entry необходим явный Save / Discard / Return later; без изменений диалог не нужен.

**[Д]** После Save нормализуются tag mentions (§6) и создаются pending new tags из Draft; самопроизвольный `#word` не создаёт catalog tag. **[О]** Точный порядок и восстановление частично выполненного многофайлового Save — FQ-03.

**[П]** Save без фактических изменений не создаёт пустую Revision. Это предложение из UI-0.5, а не отдельно подтверждённое новое правило.

### 4.2. Lifecycle

**[Д]** Active / Archived / Trash. UI-0.5 содержит прежнее техническое обозначение DELETED для Trash; окончательный enum сериализации выбирается отдельно.

| ID | Операция | Семантика |
|---|---|---|
| ENT-09 | Archive | Меняет lifecycle/audit без content Revision; Entry переносится вместе с Draft; короткое confirmation; draft доступен при открытии архива |
| ENT-10 | Delete | Entry с Revision переходит в Trash вместе с Draft; новая Entry без Revision может быть удалена целиком |
| ENT-11 | Restore from Trash | Восстанавливает Entry; не является Restore исторической Revision и не создаёт content Revision |
| ENT-12 | Delete permanently | Доступно из Entry Trash; автоматический таймер permanent delete пока не нужен |

**[О]** В какой lifecycle возвращается восстановленная Entry, последствия её permanent delete для связанных объектов и audit retention — FQ-08. Само наличие Restore/permanent delete уже принято.

### 4.3. EventTimeRange

**[Д]** From date обязательна; From time optional. To может отсутствовать целиком, To time optional. Отсутствующее время не превращается в `00:00`. Одна редактируемая timezone на интервал, default из user/device settings, входит в versioned content. **[П/Б из UI-0.5]** Конец не должен предшествовать началу; обработка смешанной точности требует формализации.

Неполный ввод сохраняется как Draft; обязательность корректной даты при завершении ручной записи не даёт AI права выдумывать дату raw input. Physical serialization, интервальные сравнения и uncertain dates — FQ-05.

## 5. Хранение, конкурентность и восстановление

### 5.1. Authoritative и derived данные

| Данные | Статус | Требование |
|---|---|---|
| Entry metadata, versions, durable Draft, catalog Tags/Types, Asset metadata/managed originals | Authoritative | Переносимы в пользовательском файловом хранилище |
| Raw/provenance, runs/results/proposals/resolutions, user routines | Authoritative пользовательские факты | Потеря backend DB не должна их уничтожать; точные пути и схемы — технический проект |
| System presets | User-owned definitions | `_system/` пользовательского repository, миграция вместе с data format |
| Search/query DB, reverse relations, агрегаты, derived review state | Derived | Полный rebuild из authoritative данных |
| Derived index/checkpoint рядом с файлами | Derived | Ускоряют cold start, не заменяют source of truth |
| Local recovery snapshots | Дополнительная страховка | Не заменяют durable Draft и не выдаются за межустройственное хранение |
| Bytes внешней ссылки | Во внешнем сервисе | Наличие Asset reference не гарантирует доступность или владение original |

**STO-01 [Д].** Draft находится в папке Entry рядом с revisions. Пример согласованного расположения: `entries/.../<entryId>/draft/DRAFT.json` и `draft/entry.md`; рядом `ENTRY.json`, committed `entry.md`, `revisions/`. В DRAFT.json допустимы baseRevisionId, title, event time/timezone, tagIds, assetIds, собственный updatedAt и session metadata. Полный набор полей пока не JSON Schema.

**STO-02 [Д].** Rebuild индекса восстанавливает поиск/фильтры/relationships, Draft presence, routine history, proposals и derived review state без утраты пользовательских фактов. Временный cache hit не является доказательством durable Save.

**STO-03 [Б].** Save, Apply, Restore и переход ownership проверяют актуальность base/current. При конфликте — разрешение/rebase, без last-write-wins. Один mutation owner на Entry; разные Entries редактируются независимо. Takeover переводит предыдущую session в paused/read-only; её unsynced input остаётся доступным в recovery.

**STO-04 [Б].** Durable jobs переживают закрытие страницы. Отменённый или потерявший lease job не имеет права commit, даже если ответ внешнего AI уже пришёл.

**STO-05 [Б].** Recovery defaults из UI-0.5: до пяти локальных snapshots, не более 30 секунд между точками при изменениях, retention 24 часа после успешной Revision. Это конфигурируемые значения. Preview восстановления не создаёт Revision; восстановление local snapshot меняет Draft.

**STO-06 [О].** Multi-file commit в Drive, журнал восстановления, блокировки/lease после сбоя, согласованность индекса и миграции задаются техническим проектом. **[П]** Проект должен предусмотреть crash recovery и идемпотентный retry для промежуточных состояний; конкретный алгоритм сейчас не утверждается.

## 6. Tags и отношения

| ID | Требование [Д] |
|---|---|
| TAG-01 | Связь Entry–Tag хранится через canonical tagId; chips показывают этот набор; raw hashtag relationship не определяет |
| TAG-02 | Lookup ищет canonical name и aliases; прямой name match выше alias-only. При выборе alias вставляется именно он, chip показывает canonical name |
| TAG-03 | `Create #new` — явное действие; новый тег до Save существует только в Draft. Save создаёт canonical tag, Discard не оставляет мусор в каталоге |
| TAG-04 | При Save linked tag без canonical/alias hashtag дописывается обычным текстом в конец. Отдельного обязательного Tags: block нет |
| TAG-05 | Unlink меняет набор tagIds через Draft; удаление hashtag из body без удаления chip связь не снимает |
| TAG-06 | Rename сохраняет tagId, добавляет старое имя в aliases; ручное удаление alias не меняет relations |
| TAG-07 | Merge выбирает survivor; переносит имя/aliases с дедупликацией, current Entry/Draft relations на survivor; старый tagId становится mergedInto redirect |
| TAG-08 | Merge не переписывает immutable revisions. Survivor сохраняет type/color без дополнительных merge options |
| TAG-09 | Delete — soft delete, tagId и старые relations сохраняются. Новые links запрещены, autocomplete/cloud исключают тег. Used tag требует count/warning/confirmation |
| TAG-10 | Deleted filter и Restore доступны; permanent delete Tags пока отсутствует |
| TAG-11 | Types — пользовательский справочник; typeId optional; color непосредственно у Tag, без inheritance |
| TAG-12 | Entries count у Tag: уникальные Active Entries с текущими Draft, без Archived/Trash |

**[О]** Merge переназначает current relations, однако current committed snapshot immutable: техническая семантика переназначения ещё не определена. Возможные варианты — разрешение redirect в проекции либо отдельная versioned операция; они не выбраны этим документом (FQ-02). Аналогично открыты коллизии aliases и судьба оставшихся текстовых hashtags после удаления chip.

## 7. Assets

**AST-01 [Д/Б].** Entry изменяет связи с Asset, не bytes самого файла. Один Asset может быть связан с несколькими Entries. Поддержаны выбор из библиотеки и upload; baseline external references сохраняются. Rename/description относятся к Asset metadata; rename не меняет сам файл.

**AST-02 [Д].** Library показывает все active Assets, включая Unlinked; поиск по filename и Asset name. Unlinked означает ноль связей с **Active Entries**, поэтому не доказывает отсутствия archived/historical references. Счётчики и destructive warnings должны различать эти области.

**AST-03 [Д].** Unlink from Entry и Delete asset from library — разные операции; `×` сначала предлагает выбор. Global Delete требует confirmation и информации об использовании другими Entries. Soft delete сохраняет links и допускает Restore.

**AST-04 [Д].** Из Trash доступны Delete permanently и Empty Trash. Физически удаляются managed file и preview, Restore после этого невозможен. По assetId остаётся минимальный tombstone (например name/type/deletedAt), в Entry/history — нейтральный placeholder «Файл удалён».

**AST-05 [Д].** Display mode Grid/Gallery — UI preference, не content Entry. Captions и manual ordering в первой версии отсутствуют. **[F]** Inline placement между абзацами использует тот же assetId без копии файла, позиция versioned; удаление placement не обязано unlink/delete; embedded Asset нельзя silently unlink.

**[О]** Upload до Save, orphan cleanup при Discard, исторические warnings, очистка preview/cache при permanent delete и удаление external original у провайдера — FQ-08. Удаление ссылки само по себе не означает права физически удалить внешний файл.

## 8. Выборки, поиск и производные данные

**QRY-01 [Д].** Generic filter expression: atomic `field/operator/value` и рекурсивные AND/OR/NOT. NOT — общий логический оператор. Text contains ищет title+body; Tag использует tagId; доступны Has draft, Has assets, State, Source, Has open AI proposals и derived Needs attention.

**QRY-02 [Д].** Event date/time range: optional From и To, каждая граница содержит date, optional time, timezone. Только From — односторонняя нижняя граница, только To — верхняя. Это не EventTimeRange самой записи: optional From фильтра не отменяет обязательность From date в записи.

**QRY-03 [Д].** Sorting: Event date/Updated/Created asc/desc, Title A–Z/Z–A; default Event date newest first. При Draft используется текущее Draft-state, включая Event date. Отдельного приоритета Drafts нет. **[О]** Что означает Updated sort при разных Draft.updatedAt и committed Entry.updatedAt — FQ-06; autosave committed timestamp не меняет.

**QRY-04 [Д].** Current filters — ephemeral state. System preset задаёт initial expression; любая ручная правка отделяет фильтр от preset. Минимальный предварительный каталог: Drafts, Archived, Trash, Needs attention, Open AI proposals, Entries with assets, Last 7 days, Last 30 days и динамические Calendar/TagCloud/Statistics selections. Custom Saved Filters — future.

**QRY-05 [Д].** Entries из Main Navigation открывает Browser без filters; All entries не отдельная сущность. Явно Active-ограниченные виджеты сохраняют свой predicate. UI-0.5 трактует отсутствие фильтров буквально, без скрытого State=Active.

**QRY-06 [Д].** Needs attention — наличие unresolved review item, например proposal, conflict или uncertainty. Несколько items одной Entry не дают несколько Entries в счётчике. Has open AI proposals — отдельный предикат; модель прочих review items пока [О].

### Производные Home-выборки

| Потребитель | Контракт [Д] |
|---|---|
| EntryList | 7 Active Entries, без периода, Event date desc; current Draft-state при наличии |
| TagCloud | Active за всё время; число уникальных связанных Entry определяет размер, Tag.color определяет цвет; deleted tags исключены |
| Calendar | Наличие записей по дням; выбранный день/range преобразуется в универсальные From/To. Без counts/state clutter в UI |
| Total entries, Drafts, Needs attention | За всё время; конкретный lifecycle-охват counters остаётся открытым, его нельзя вывести только из слов «всё время» |
| Entries last 7 days | Сегодня + предыдущие 6 дней |
| Entries last 30 days | Сегодня + предыдущие 29 дней |
| Entries with assets | Has assets AND Event date в последних 30 днях |

**QRY-07 [Д].** Клик по показателю открывает выборку, совпадающую с областью подсчёта. Месяц Calendar не меняет all-time облако или rolling periods статистики. Timezone границы дня, overlap intervals и lifecycle counters — FQ-05/06.

## 9. AI Routines, Runs и Proposals

### 9.1. Routine и запуск

**AI-01 [Д].** System routine immutable; пользователь может Duplicate/Copy и редактировать свою копию. Минимум user routine: name, description, prompt/instructions, scope/eligibility, application policy. Точная модель/versioning routine и form ещё открыты.

**AI-02 [Д].** Selection scope (single Entry / current filtered set / all Entries) отличается от eligibility внутри routine. Filtered batch — результат текущего filter expression, дополнительно ограниченный eligibility. Draft Entries skip, без ожидания автокоммита. Отдельный запуск требует успешного Save; failed/отменённый Save не запускает AI.

**AI-03 [Д].** Run связан с routineId/routineVersion/entryId/baseRevisionId или input Revision/result/status. Already processed skip может применяться к той же routineVersion и Revision независимо от accepted/rejected outcome proposal. Явный Force rerun доступен; новая Revision или routineVersion допускает обычный запуск.

**AI-04 [Д/Б].** Результаты показывают processed/skipped/errors и time/duration; trace включает реально использованные model/provider, instructions/version, input references, validation, outputs, proposals, resolutions и созданные revisions. Failed/rejected/non-mutating run также доступен, даже без Revision.

**AI-05 [Б].** Effective model: run override → routine preference → global user preference → system default. Provider следует модели. Silent fallback на другую модель/provider запрещён.

**AI-06 [Б].** Jobs queued/running/done/failed с отменой. Закрытие страницы не отменяет durable job. Lease и freshness проверяются перед изменением данных. Read-only analysis не требует mutation lease, но правило Draft eligibility не отменяет.

### 9.2. Proposal и применение

**AI-07 [Б].** Изменения существующего текста и неоднозначных metadata оформляются persistent proposal. Base, актуальный Current, предлагаемые изменения и provenance позволяют проверить результат. Stale/conflicting proposal не применяется быстрым Apply без разрешения конфликта.

**AI-08 [Б].** Detailed review использует Base / editable Result / Proposal; при конфликте можно оставить Current, взять Proposal или вручную отредактировать Result. Перед Apply заново проверяются ownership/base compatibility; подтверждённый Result создаёт одну новую committed Revision.

**AI-09 [Д].** Accepted/rejected proposal не исчезает из history. Accepted перестаёт быть open, сохраняет provenance и может ссылаться на Revision. Reject не равен «run никогда не выполнялся» и не отменяет already processed semantics.

**AI-10 [Б].** Информационный результат остаётся AIResult и не превращается сам в body Entry. AI не удаляет user-added tags автоматически. Uncertainty не заменяется выдуманным фактом.

**[О]** Прежний baseline допускает автоматическую первую normalization и некоторые привязки существующих tags. D04 формулирует Revision только через Save; автоматические mutating policies нельзя окончательно реализовать без разрешения FQ-01. Batch launch уже принят, массовое бесконтрольное применение не принято. Partial apply и судьба непринятых частей proposal — FQ-07.

## 10. Capture и интеграции

**INT-01 [Б].** Raw capture сохраняет original/source/provenance; последующая нормализация не уничтожает исходник. Отдельный экран Inbox не является обязательным условием capture pipeline. Uncertainty и ошибки обработки остаются различимыми.

**INT-02 [Б].** Google login, разрешение Drive и Calendar consent — разные шаги. Без Calendar permissions можно пользоваться дневником. Внутренний account ID отделён от Google identity; данные аккаунтов изолированы.

**INT-03 [Б].** Calendar Inbox — внешний capture adapter. Calendar Timeline — отдельная односторонняя derived projection current committed Entry. Один Entry соответствует одному event; новая Revision обновляет event, proposals/Draft не публикуются как committed content. Проекция перестраиваема; внешние ручные изменения не обязаны импортироваться обратно.

**[О]** Payload/schema capture, idempotency keys внешних импортов, mapping lifecycle→Calendar и точный retry/sync contract проектируются на интеграционном этапе. Этот документ не задаёт неутверждённую двустороннюю синхронизацию.

## 11. Нефункциональные требования

| ID | Область | Требование / граница |
|---|---|---|
| NFR-01 [Б] | Сохранность | Ошибка Save/network/lease не уничтожает введённое; различаются local recovery, durable Draft и committed Revision |
| NFR-02 [Д] | Восстановимость | Полная потеря backend index/cache не означает потерю пользовательских фактов; проверяется rebuild из файлов |
| NFR-03 [Б] | Приватность | Изоляция дневников, ownership checks и явные разрешения внешних интеграций |
| NFR-04 [Б] | Надёжность | Идемпотентные повторы, freshness/concurrency checks, отсутствие silent overwrite |
| NFR-05 [Б] | Автономность базовых функций | Чтение/редактирование не зависят от доступности AI; online-first, full offline-first отложен |
| NFR-06 [Б] | Переносимость | Export/backup/restore; миграция с backup/snapshot, maintenance, validation и report |
| NFR-07 [Д/Б] | Проверяемость AI | Сохранённые inputs/version/model/result/outcome; rejected и failed runs доступны |
| NFR-08 [Д] | Согласованность выборок | Count и переход используют одну семантику; Draft не дублирует Entry |
| NFR-09 [Б] | Адаптивность | Web browse/read/search на desktop/mobile; конкретные layouts в UI-0.5 |
| NFR-10 [О] | Производительность | Объёмы дневника, latency search/Save, время cold start/rebuild и лимиты uploads пока не согласованы; численные SLA не придуманы |

## 12. Сквозные критерии приёмки

UI-0.5 содержит отдельные AC-01…62; ниже системные проверки, которые не заменяются демонстрацией экранов.

| ID | Проверка | Ожидаемый результат |
|---|---|---|
| SYS-AC-01 | Создать Entry, ввести текст, autosave, переоткрыть | Тот же entryId, durable Draft доступен; ни одной committed Revision до Save |
| SYS-AC-02 | Несколько autosave, затем один Save | Одна Revision, currentRevisionId обновлён; Draft удалён только после подтверждения |
| SYS-AC-03 | Оставить Draft на длительное время | Таймер не создаёт Revision |
| SYS-AC-04 | Ошибка/повтор Save | Ввод сохранён, duplicate Revision/Entry отсутствует; [П] fault injection между файловыми шагами после выбора commit protocol |
| SYS-AC-05 | Delete backend DB/cache и rebuild | Entry/Draft/relations/runs/proposals и выборки восстановлены из user-owned data |
| SYS-AC-06 | Takeover редактирования | Старая session не может commit, её unsynced input доступен для recovery |
| SYS-AC-07 | New tag в Draft → Discard / Save | В первом случае нет мусора в каталоге, во втором tagId создан и связан |
| SYS-AC-08 | Удалить hashtag, оставив chip → Save | Связь остаётся, недостающее упоминание добавлено в конец |
| SYS-AC-09 | Merge / Delete Tag → открыть старую Revision | Snapshot не переписан; merge разрешает redirect, delete сохраняет historical tag и relations |
| SYS-AC-10 | Asset permanent delete → читать history | Bytes и preview отсутствуют, tombstone/placeholder доступны, Restore не обещается |
| SYS-AC-11 | Archive Entry с Draft | Lifecycle/audit изменены без content Revision, Draft доступен в архиве |
| SYS-AC-12 | Batch содержит Draft и уже обработанные Revision | Draft skip; already processed определяется routineVersion/input Revision; Force rerun доступен |
| SYS-AC-13 | Reject proposal → повтор обычного batch | Reject не стирает run; правило already processed продолжает работать |
| SYS-AC-14 | Current изменился до Apply | Stale Result не перезаписывает новый Current; нужен conflict/review |
| SYS-AC-15 | Клик Home counter / фильтр Tag | Выборка и count совпадают по области и текущему Draft-state, без дублей |
| SYS-AC-16 | Date-only, optional end, timezone | Не появляется фиктивное midnight; точность/timezone сохраняются после Save/reload |
| SYS-AC-17 | Отключён AI или Calendar | Базовые доступные чтение/редактирование продолжают работать |

## 13. Этапы реализации

Сохранено разделение UI-0.5; это последовательность возможностей, не оценка сроков.

| Этап | Основной результат | Что требуется согласовать перед реализацией |
|---|---|---|
| E0 | Account/storage access, files-only чтение существующих Entries | Минимальные canonical read contracts |
| E1 | Поиск, filters, sorting, presets | Date semantics, области выборок, query contract; стратегия index при необходимости |
| E2 | Редактирование, durable Draft, Save, history/Compare/Restore | Commit protocol, concurrency, schemas/migrations, FQ-01 и FQ-03 |
| E3 | Каталоги Tags/Types, merge/delete, работа с Assets | FQ-02, collision policy, deletion/references |
| E4 | Routines/runs, proposals/review, model settings | Eligibility/run identity, application policy, cancellation/retry, FQ-07 |
| Дополнительные UX и интеграции | Home, web-create, полный Assets UI, Calendar adapters | Очерёдность поставки и adapter-specific contracts |

Если функция подключена раньше этапа каталога, минимальный полный сценарий уже должен работать: например Add tag без выбора/создания или Save без durable Draft недопустимы. Каталоги и UI могут поставляться постепенно, целостность данных не откладывается.

## 14. Открытые системные вопросы

| ID | Что нужно решить | Почему это влияет на реализацию |
|---|---|---|
| FQ-01 | Точная граница «Revision только по Save»: manual Draft против явных Apply/Restore и прежнего AI auto-apply | Необходимо единое правило источников committed изменений. Save-таймер уже отменён; этот вопрос его не переоткрывает |
| FQ-02 | Как tag merge меняет current relations при immutable committed snapshot | Нужна семантика redirect/projection/versioned operation и взаимодействия с Draft/lease |
| FQ-03 | Multi-file commit, recovery после частичного Save, idempotency и canonical location operational state | Иначе durable Draft, new tags и currentRevisionId могут расходиться после сбоя |
| FQ-04 | Коллизии aliases, удаление chip при сохранённом hashtag, формат suffix normalizer | Нужно предсказуемое tag lookup/normalization без потери текста |
| FQ-05 | EventTimeRange serialization, mixed precision/uncertainty, inclusivity/overlap/date timezone | Определяет фильтры, календарь и статистику |
| FQ-06 | Lifecycle counters, Updated sort при Draft, модель review items | Влияет на query/index и совпадение count с результатом |
| FQ-07 | User routine schema/versioning/application policy, failed-run retry vs already processed, partial proposal resolution | Нельзя смешивать завершённый запуск, успешное применение и возможность retry |
| FQ-08 | Entry permanent delete dependencies, Restore lifecycle, orphan uploads, external originals, retention/cache cleanup | Сохранность ссылок и корректность destructive operations |
| FQ-09 | API error/retry contract, index invalidation/rebuild, migrations | Нужны конкретные технические решения после доменных правил |
| FQ-10 | Объёмы данных, latency/availability targets, upload limits | Без них нельзя объективно оценить производительность |

Эти вопросы частично уже открыты в UI-0.5, частично выявлены здесь на пересечении принятых требований. Новые варианты решения не считаются утверждёнными. UI-only вопросы о размерах, цветовой теме и точной раскладке остаются в экранной спецификации.

## 15. Трассировка и следующий технический документ

| Область этого ТЗ | D04 | UI-0.5 |
|---|---|---|
| Хранение, index, rebuild | §§1, 3, 32, 49 | §§2.1, 9.4.1 |
| Entry/version/draft/lifecycle | §§2–8, 24 | §§8–11, C15 |
| Tags/types/relations | §§9–17, 45–46 | C09, §13 |
| Assets | §§18–23, 46 | C11/C12, §14 |
| Routines/proposals | §§25–31 | §15, S07/S10/S13 |
| Queries/presets/aggregates | §§33–44 | C06–C08/C13–C14, §§7–8 |
| Future/отменённое | §§47–48 | §§22, 26 |
| Auth/concurrency/recovery/integrations | Унаследованный baseline | §§6, 9.5–9.6, 12, 16–19 |

**Следующий технический проект должен дать:** versioned file schemas, logical commands/queries и API, ошибки/идемпотентность, commit/recovery protocol, leases/concurrency, index/rebuild/invalidation, job lifecycle и trace storage, migrations/backup, integration adapters и deployment. Выбор конкретной БД, framework, queue или протокола не следует автоматически из этого ТЗ.

Этот документ уже пригоден для декомпозиции требований и обсуждения контрактов. Реализация спорных операций должна опираться на закрытие соответствующих FQ, а не на предположения об отсутствующих решениях.
