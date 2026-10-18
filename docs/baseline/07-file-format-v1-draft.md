# AI Diary — проект файлового формата v1

**Дата:** 18.10.2026  
**Статус:** технический проект для review, **не утверждённый новый baseline и не применённая migration**.  
**Идентификатор примеров:** 1.0.0-draft.1. Наличие слова v1 в заголовке не меняет formatVersion существующего дневника.

## 1. Что уже принято и что предлагает этот документ

Принятые пользовательские правила остаются в [функциональном ТЗ](AI-Diary-Functional-Spec-v0.1.md). Здесь предлагается их физическое представление. [Протокол Save](08-save-recovery-design.md) описывает публикацию и recovery. [Проверяемый пример](examples/file-format-v1/save-with-new-tag.json) содержит состояния до и после Save.

| Основание | Уже принято | Предлагаемая конкретизация |
|---|---|---|
| INV-01, STO-01/02, AQ-DATA-001/009 | User-owned files — durable truth; backend — coordinator; первый срез без обязательной DB/search | JSON + Markdown + originals; восстанавливаемая карта актуальных объектов |
| INV-02/03/04, ENT-01–08 | Один durable Draft; immutable Revision; autosave без Revision и таймерного commit | Полные snapshots; независимые content и operational metadata |
| FQ-01 | Save/Apply/Restore сразу фиксируют Revision; два узких AI auto-apply случая сохраняются | Общий commit path с разными command kind |
| FQ-02 | Merge — catalog redirect, без переписывания history/Draft | Версионированный snapshot каталога с mergedInto |
| FQ-04 | Уникальность names/aliases без регистра, включая резервирование deleted labels; #_name; suffix | Pending tag definitions и unlink intent в Draft; validation при публикации |
| AQ-DATA-003/004 | Lease + base revision + provider condition где доступно; без silent overwrite | Fenced publication и внешние изменения через reconciliation |
| AQ-DATA-005/007 | Managed/external Assets; без media versioning; readable files | Asset identity отдельно от Entry; bytes вне content snapshots |
| AQ-DATA-006 | Общая версия storage, явные последовательные migrations | Один formatVersion; смена только через maintenance/backup/validation |

Исходный срез Git: c959b9bd15312dee1535e0e51cec54400ccc68e4, ветка docs/requirements-baseline. Проверены functional/screens specs и canonical решения AQ-DATA-001/002/003/004/005/006/007/009/010, FQ-01/02/03/04. Старые сводки про часовой auto-commit уступают решениям 04.10/18.10.

Приложенные File Storage Structure, File Storage Structure with calendar projection и Project Overview использованы как исходные эскизы папок/JSON/Markdown. Старый architecture_updated.md с Android/Firebase не считается выбранной архитектурой новой версии.

Новые layout, имена полей, способ публикации и алгоритмы ниже имеют статус **[П]**. Не считать этот документ выбором пользователя по открытым FQ-05/06/07/08. В частности, сериализация времени ниже сохраняет уже известные факты, но не утверждает overlap/inclusivity policy.

## 2. Представление данных

JSON — UTF-8, Markdown — UTF-8. JSON timestamps технических событий — RFC 3339 с offset/UTC. В примерах использован UTC; дата события не выводится из времени создания файла.

Stable IDs не зависят от title, имени тега, даты события и Drive file ID. Отдельно существуют entryId, revisionId, draftId, tagId, typeId, assetId, operationId. provider object ID принадлежит adapter layer.

Предлагаемый layout, а не требование создать все папки в E0:

~~~text
AI-Diary/
  _system/
    storage_manifest.json
    commits/                  # публикации и fencing, authoritative
    operations/<operationId>/ # durable input и результаты попыток
    presets/
  _formats/                   # схемы поставляемого formatVersion
  entries/<entryId>/
    ENTRY.json                # удобное текущее представление
    entry.md                  # удобный текущий committed текст
    states/<stateId>/ENTRY.json
    revisions/<revisionId>/
      revision.json
      text.md
    draft/
      DRAFT.json              # представление текущего durable Draft
      entry.md
      snapshots/<draftVersion>/
        DRAFT.json
        entry.md
    links/
  catalogs/
    tags/snapshots/<catalogVersion>/tags.json
    tags/tags.json            # удобное текущее представление
    tag-types/
    audit/
  assets/<assetId>/
    ASSET.json
    original/                 # только managed
  inbox/
  routines/
  runs/
  proposals/
  indexes/                    # derived, не обязательны на первом срезе
  exports/
  backups/
  migrations/
  trash/
~~~

Плоский entries/<entryId> предложен для отсутствия переносов при исправлении event date. Старый вариант entries/YYYY/MM/date__entryId тоже может читаться adapter через resolver; автоматического переименования существующих папок нет. Archive/Trash в этом проекте меняют lifecycle, а не обязаны физически переносить папку во время Save.

### 2.1. Где находится актуальная истина

Многофайловая запись не становится согласованной от того, что каждый файл валиден отдельно. Поэтому проект предлагает immutable snapshots + общую запись публикации:

- опубликованное состояние определяется последним валидным непрерывным префиксом commit chain;
- commit ссылается на полные snapshots изменённых объектов и их hashes;
- Entry state и catalog state, перечисленные в одном commit, становятся видимыми вместе;
- подготовленные файлы без публикации не являются committed Revision/активным catalog tag;
- ENTRY.json, entry.md, draft/DRAFT.json, draft/entry.md и tags.json по удобным стабильным путям — **materialized views**, которые можно восстановить из опубликованных snapshots;
- application repository всегда читает согласованный префикс публикаций, даже если materialized views ещё обновляются;
- standalone reader также должен учитывать commit chain. Просто открыть entry.md можно для чтения текста, но он может отставать от последней публикации.

Это **явное изменение старого эскиза**, где ENTRY.json и entry.md выглядели независимыми текущими canonical файлами. Authoritative данные остаются в user-owned storage, а не переезжают в backend DB. Принятие такой физической организации ещё не объявляется принятым baseline.

Materializer не является новым writer доменной истины. Только fenced materializer обновляет views; он записывает source publication sequence/hash. При отсутствии гарантии условной записи adapter не должен держать параллельные materializers одного view. Внешнее изменение view сохраняется для reconciliation до любых исправлений, а не затирается как обычный устаревший cache.

### 2.2. FileRef и проверка целостности

FileRef содержит path относительно storage root и SHA-256 **точных bytes**. Никакого неявного reformat JSON или смены line endings после вычисления hash. JSON request fingerprint вычисляется отдельным версионированным codec; это не произвольный stringify map.

Пример:

~~~json
{
  "path": "entries/entry_demo/revisions/rev_demo_2/revision.json",
  "sha256": "64 lowercase hexadecimal characters"
}
~~~

Это иллюстрация формы; реальные hashes находятся в JSON-примере. Запрещены absolute paths и выход через '..'. Обязательность существования target зависит от роли ссылки: current content и pending operation payload должны существовать; consumedDraftRef и вытесненные Draft refs в старых control records являются evidence об уже очищенном snapshot и не требуют бессрочного сохранения его текста. В Drive имя файла не считается уникальным ключом: adapter хранит/передаёт object locator и проверяет identity/hash. Поле nextSlot у publication дополнительно содержит provider binding для следующего create-once slot; оно durable, а не только cache.

## 3. Entry state

Entry state описывает identity и lifecycle, а содержимое берётся из Revision либо текущего Draft.

| Поле | Смысл |
|---|---|
| formatVersion, schema | Общая версия, entry-state |
| entryId, stateId | Identity Entry и конкретного immutable state |
| createdAt | Системное создание Entry, не event date |
| lifecycle | Предложенный enum ACTIVE / ARCHIVED / TRASH |
| currentRevisionId | null до первого Save |
| currentRevisionRef | FileRef либо null |
| committedUpdatedAt | Последний content commit; null до него; autosave не меняет |
| draftRef | Текущий durable snapshot Draft либо null |
| pendingOperationId | Текущая незавершённая commit-операция либо null |
| provenanceRefs | Raw/source references; не редактируются обычным Entry editor |

Title, eventTime, tagIds и assetIds не дублируются как самостоятельная истина в Entry state. API может собирать denormalized view для списка. Это устраняет случай, когда metadata Entry от одной версии, а текст — от другой.

У новой Entry после Create уже есть identity/state и durable Draft, currentRevisionId=null. Нулевая фиктивная Revision не создаётся. Lifecycle/audit mutation создаёт новый Entry state, но не content Revision. Restore из Trash не равен Restore Revision. **[Д, 18.10]** Restore из Trash всегда устанавливает lifecycle=ACTIVE, включая ранее Archived; currentRevisionId/ref, history и draftRef сохраняются. Предыдущее состояние может оставаться в audit, но не определяет target Restore. [FQ-08/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/01_SQ-01_restore-lifecycle/00_thread.md). Permanent-delete policy остаётся FQ-08.

## 4. Полный content snapshot и Revision

Content содержит:

| Поле | Представление |
|---|---|
| title | string, пустой title допускается |
| eventTime | from, optional to, timeZone; без подстановки полуночи |
| textRef | FileRef на text.md / entry.md |
| tagIds | Unique IDs; связи задаются ими, не текстовыми hashtags |
| assetIds | Unique Asset IDs; без копирования media bytes |

Revision дополнительно содержит revisionId, entryId, sequence, previousRevisionId, operationId, origin и provenance. Origin — USER_SAVE / AI_APPLY / HISTORY_RESTORE / AI_INITIAL_NORMALIZATION / AI_EXISTING_TAGS / EXTERNAL_FILE_CHANGE. У Restore есть restoredFromRevisionId; previousRevisionId указывает на Current перед Restore, поэтому история остаётся линейной.

Revision snapshot immutable. sequence присваивается при согласовании с актуальным Current. Подготовленный candidate не попадает в History до публикации; при неудаче он не считается дополнительной Revision.

Исторические tagIds сохраняются. Current lookup разрешает mergedInto и дедуплицирует canonical IDs; физический snapshot не меняется. Как именно показывать исторические tag labels/color — отдельная ещё открытая policy, не выводить её из текущего tags.json.

### 4.1. Время

Предлагаемый сохранительный codec:

~~~json
{
  "from": {"date": "2026-10-18", "time": null},
  "to": null,
  "timeZone": "Europe/Belgrade",
  "uncertainties": []
}
~~~

Draft может иметь from=null; ручной Save требует корректной from.date. Неизвестная дата raw/AI input сохраняется как uncertainty с исходными evidence, а не выдуманной датой. Применение такой первой normalization требует отдельной validation policy, согласованной с FQ-05. Mixed precision, inclusive/exclusive end, DST-ambiguity и overlap фильтров **не закрыты** этим примером; интеграция календаря не должна угадывать эти значения.

## 5. Durable Draft

Draft — полный snapshot с тем же content shape; максимальная текущая логическая копия одна на Entry.

Дополнительные поля:

- draftId, draftVersion (монотонный номер flush), baseRevisionId;
- updatedAt самого Draft, sessionId и mutationEpoch;
- pendingTags: новые определения с уже выделенными stable tagId, name, aliases, optional typeId, color;
- tagEditIntents: какие tagIds явно сняты через chip и какие обозначения были известны при снятии; re-add до Save отменяет intent;
- pendingUploads: durable upload IDs, filename, status и uploadRef на состояние upload/staging отдельно от готовых assetIds;
- storageStatus здесь не заменяет факт успешной публикации Draft.

tagIds Draft могут ссылаться на pendingTags того же Draft. Таких тегов ещё нет в активном каталоге. При Save сохраняются те же выделенные IDs, но только после проверки namespace и успешного совместного commit. Конфликт не приводит к silent rebind на чужой tagId.

### 5.1. Autosave и crash consistency

В проекте autosave также публикует цельный snapshot: подготовить DRAFT.json + entry.md, проверить hashes, затем одной записью сменить draftRef при том же base/current и актуальном owner. committedUpdatedAt/currentRevisionId остаются прежними.

snapshot directory — технический способ не порвать пару JSON/Markdown. После переключения draftRef старый autosave payload очищается, если он не нужен незавершённой операции. Приложение не предлагает autosave history, и старые Draft payload не сохраняются как постоянный архив. Короткие leftovers после crash — GC/recovery, а не функция истории.

Полный replay metadata chain может помнить старые draftRef; reader не обязан загружать payload уже вытесненного Draft. Rebuild сначала вычисляет актуальную карту объектов, затем загружает достижимые snapshots. Обязательная история Revision и текущий Draft при этом сохраняются.

Локальные bounded recovery snapshots остаются отдельной страховкой по STO-05 и не становятся серверной history.

### 5.2. Нормализация hashtags

Нормализатор получает замороженные content + pendingTags + unlink intents + catalog version + parserVersion. Он:

1. сохраняет произвольно набранные hashtags текстом без создания связей;
2. переводит распознанные mentions явно снятого тега в #_name, включая aliases и исходное написание;
3. исключает #_name из активных mentions и autocomplete;
4. проверяет remaining linked IDs с учётом catalog redirects;
5. дописывает только отсутствующие mentions одной строкой через пробел в конце, после пустой строки у непустого body;
6. повторное применение к тому же состоянию не меняет текст снова.

Удаление hashtag при оставшемся chip не снимает relation. Перестановка/переименование уже написанных mentions не выполняется. Грамматика составных имён, boundary matching, Unicode/whitespace и выбор отображаемого написания добавляемого mention ещё требуют FQ-04; в примере намеренно используются однословные однозначные имена.

## 6. Каталог Tags / Types

Предлагается один полный JSON snapshot каталога на catalogVersion; aliases входят в Tag, отдельный aliases.json при наличии — derived lookup. Это исключает две независимые authoritative копии aliases.

Tag: tagId, name, aliases[], optional typeId, color, state (ACTIVE / DELETED / MERGED), mergedInto, createdAt, updatedAt. У MERGED обязательно mergedInto, у остальных null. Deleted labels резервируются без учёта регистра.

Все Create/Rename/Alias/Restore/Merge и pending Create при Save проверяются против актуального snapshot каталога внутри публикации. Две Entries могут готовиться параллельно; collision двух новых обозначений разрешается до публикации второго, без автоматического merge/rebinding.

Merge:

- survivor сохраняет type/color;
- name/aliases old переносятся с дедупликацией;
- old остаётся redirect;
- циклы запрещены; resolver обязан обнаруживать повреждение;
- при цепочке redirects допустимо разрешение до конечного survivor, без перезаписи history/Draft;
- audit — authoritative событие каталога;
- catalog mutation не создаёт content Revision связанных Entries.

Сравнение без регистра принято. Конкретный Unicode case-fold codec и нормализация пробелов должны получить parser/normalization version перед runtime implementation; не подменять их текущим locale устройства.

TagType — пользовательский объект со stable typeId, не фиксированный system enum. Какие изменения/удаления Type допускаются при использовании, здесь не добавляется.

## 7. Assets и uploads

Asset: assetId, kind, name/filename, description, mimeType, size/dimensions/duration если известны, createdAt, provenance, lifecycle, original.

original.mode:

- MANAGED: provider-independent object reference на original bytes в user-owned storage;
- EXTERNAL: provider/URL/external locator; bytes могут оставаться у провайдера.

Preview/thumbnail — derived. Нет ожидания их генерации ради text Save. Внешняя недоступность не даёт права удалить original или считать внешний URL управляемой копией.

Entry Revision хранит assetIds. Asset metadata меняется отдельно; media versioning не вводится. Permanent delete сохраняет tombstone и удаляет managed bytes/preview по принятой policy. История Entry не обещает восстановить удалённые bytes.

**[Д, 18.10.2026, [FQ-03/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md)]** Save недоступен, пока хотя бы одно оставленное вложение имеет неразрешённый статус: выбрано, загружается, проверяется, ошибка или требуется повторный выбор файла. Для продолжения нужно завершить загрузку/проверку, повторить её либо явно убрать вложение. Все оставленные attachments должны быть готовы к включению в Revision; для managed файла это подтверждённый original, для external — сохранённый валидный reference без обязательного скачивания original. Генерация thumbnail/preview не блокирует Save. До начала commit текст продолжает autosave в Draft.

Draft сохраняет весь состав вложений: связи с готовыми Asset, pending upload IDs, имена файлов, статусы и ссылки на durable upload/staging records. Успешно загруженные originals сохраняются в user-owned storage и остаются достижимыми из Draft до завершения Save или явного действия пользователя; уход со страницы и повторное открытие не должны терять вложения. Pending запись не исчезает при ошибке или перезапуске. Bytes, ещё не полученные хранилищем, не выдаются за durable: если продолжить upload автоматически нельзя, Draft сохраняет attachment intent и показывает «Выберите файл повторно». Удалять staging/original, на который ссылается актуальный Draft или незавершённая операция, нельзя.

**[П, физическое представление]** pendingUploads содержит uploadId, filename, status (SELECTED / UPLOADING / VERIFYING / FAILED / NEEDS_FILE) и uploadRef на durable upload record. upload record связывает uploadId, Entry/Draft, original staging locator, доступные metadata и подтверждённый progress. Resume credentials не включаются в переносимый JSON как открытые секреты. После готовности original и публикации Asset reference очередной согласованный snapshot Draft переносит intent в content.assetIds; это не content Revision. Callback upload не перезаписывает более новый текст/Draft и проверяет актуальную связь с Draft/ownership. Для готового Asset после Discard применяется принятое условное предложение soft delete, описанное ниже; cleanup частичного upload остаётся FQ-08.

**[Д, 18.10]** При снятии связи Asset с записью, в том числе при Discard добавлений Draft, применяется одно правило: если снимаемая связь единственная, предложить удалить сам Asset; если есть другие логические связи, снять только текущую без предложения глобального удаления в этом flow. Удаление — только по явному подтверждению и означает soft delete в Asset Trash, не permanent delete. При отказе от удаления связь всё равно снимается, Asset остаётся в библиотеке; при отсутствии Active Entry links он виден в Unlinked.

Проверяются логические потребители по разным entryId во всех lifecycle-состояниях, в других Draft и связанных незавершённых операциях; исторические references других Entries не теряются. Несколько Revision/Draft одной и той же Entry не считаются отдельными записями; historical link той же Entry сам по себе не запрещает предложить soft delete, поскольку история/links сохраняются. При Discard рассматриваются только связи, реально исчезающие относительно восстанавливаемой Current: Asset, остающийся в Current, не является кандидатом на удаление из-за Discard. Проверка актуальна перед выполнением; при новой чужой связи выполняется только unlink. Состояние Unlinked по Active-счётчику не используется как доказательство единственности. Незавершённая операция с неизвестным исходом сначала требует reconciliation.

Soft delete сохраняет metadata/tombstone и исторические references; физические original bytes не стираются этим выбором. Файлы актуальных Draft/операций защищены до разрешения соответствующего flow. Cleanup неполных staging/late completion и срок последующего retention остаются FQ-08; отсутствие Active links не разрешает destructive GC. **История:** [FQ-08 — снятие связи / Discard](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/00_thread.md).

## 8. Raw / AI / audit / integrations

| Объект | Предложенное размещение и обязательный смысл |
|---|---|
| Raw input | inbox/... + immutable receipt/source refs; не обязана быть нулевой committed Revision |
| Routine | routines/<routineId>/versions/...; system presets отдельно; exact schema FQ-07 |
| Run / AIResult | runs/<runId>/; input Revision, routine/version, model/provider фактически использованные, outputs, validation, status; failed/non-mutating тоже сохраняются |
| Proposal | proposals/<proposalId>/; baseRevisionId, runId, proposed result и durable resolution |
| Apply receipt | Ссылка operationId → созданная Revision; proposal resolution публикуется вместе с Revision |
| Catalog/lifecycle audit | Snapshot/small event в той же публикации, без лишней content Revision |
| Calendar projection | Derived mapping/checkpoint, повторяемая доставка committed Current |
| Query/index/cache | Derived, при удалении восстанавливаются; первый MVP может обходиться без них |

Не создавать пользовательский факт только в operational DB. Job queue execution bookkeeping может жить отдельно, но вход/результат/решение пользователя и committed provenance должны восстанавливаться из storage.

Глобальный publication journal не должен случайно хранить удалённые media bytes или полные копии transient Draft навсегда. Политики permanent delete/retention старых object snapshots и audit требуют отдельной FQ-08 проработки до реализации destructive commands.

## 9. Обновление старых эскизов

| Старый пример | Актуальное требование / проект |
|---|---|
| status=processed у Entry | Lifecycle отдельно; processing принадлежит Run/Proposal |
| rawRevisionId как обязательная Revision 000 | Raw/provenance отдельно; первая committed Revision возникает по разрешённому commit path |
| Title/time/tags как независимая копия в ENTRY.json | Content в полном Draft/Revision; Entry state ссылается на него |
| Alias map и tag aliases как две истины | Один snapshot каталога; lookup derived |
| Номер папки raw/AI/user определяет смысл | Stable revisionId + origin/provenance; линейный sequence |
| Revision по часу бездействия | Отменено; autosave только Draft |
| Draft только в backend operational state | Durable полный Draft в пользовательских файлах |
| Удобные текущие файлы можно обновлять по очереди | В предлагаемом протоколе публикация определяет coherent state, views восстанавливаются |

Старые приложенные документы не изменяются и не удаляются этим проектом.

## 10. Границы готовности

Собран конкретный проект core records и Save-пример; это не полный production schema registry всего продукта. Машинная схема в комплекте проверяет core Entry/Draft/Revision/TagCatalog/Operation/Publication. Asset/AI/time-policy, limits, auth, API endpoints и destructive lifecycle contracts требуют своих завершённых спецификаций.

Перед первым настоящим storage v1: закрыть пользовательские вопросы, проверить Drive publication primitive, дописать domain validators, провести failure injection и migration dry run на копии. Существующий storage не мигрируется этим коммитом.

## 11. Manual Save с результатом NO_CHANGE — решение 18.10.2026

Manual Save, при котором итоговое сохраняемое content совпадает с текущей committed Revision, завершает эквивалентный Draft без новой Revision. Возвращается NO_CHANGE со ссылкой на существующую Revision; committedUpdatedAt и content History не меняются. Consume именно этого Draft и результат операции фиксируются durable с обычными ownership/base/idempotency checks. У новой Entry без Current первый успешный Save создаёт первую Revision. Согласованное создание Revision при Apply/Restore сохраняется.

Перед сравнением проверяются актуальные lease/base, готовность вложений и выполняется принятая нормализация mentions. Сравниваются title и итоговый text точно, EventTimeRange со всеми сохранёнными датами/временем/точностью/timezone, набор canonical tagIds после разрешения redirects и набор assetIds. Порядок IDs не является изменением содержимого в текущей версии без ручной сортировки вложений. Текстовые пробелы, переносы строк и регистр не игнорируются; case-insensitive lookup тегов не означает case-insensitive сравнение текста. Служебные draftId/draftVersion/updatedAt, session/lease/operation metadata, file paths и Drive IDs в content equality не участвуют. Сами media bytes заново не сравниваются: Entry меняет ссылки по assetId, а Asset metadata/original имеют отдельный контракт.

**[П, формат receipt]** Operation.status=NO_CHANGE; result.revisionId/revisionRef указывают на уже существующую Current, consumedDraftRef — на завершаемый snapshot. Новый Entry state имеет прежние currentRevisionId/ref и committedUpdatedAt, draftRef=null и pendingOperationId=null. Общая publication записывает Entry state + operation receipt; новый Revision payload и лишний catalog tag не создаются. Это служебная публикация, а не content Revision. Повтор возвращает исходный результат, даже если позднее появилась новая Current. **История:** [FQ-03/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md).
