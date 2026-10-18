# AI Diary — проект Save / commit / recovery

**Дата:** 18.10.2026  
**Статус:** техническое предложение по делегированной проработке; не реализовано и не утверждает новые пользовательские правила.  
**Canonical discussion:** [FQ-03](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/00_thread.md).  
**Данные и пример:** [формат v1](07-file-format-v1-draft.md), [JSON-сценарий](examples/file-format-v1/save-with-new-tag.json), [core schema](schemas/file-format-v1/core-record.schema.json).

## 1. Коротко о предлагаемом решении

Подготовить полные immutable snapshots, затем опубликовать **одну запись**, которая делает видимыми сразу новую Revision, нужные изменения каталога, результат операции и отсутствие сохранённого Draft. После этой публикации обновлять удобные текущие файлы и внешние проекции.

Это copy-on-write + publication record, а не последовательное изменение всех текущих файлов с надеждой на отсутствие сбоя. Журнал и snapshots находятся в user-owned files. Потеря backend cache/DB не уничтожает ни результат Save, ни возможность установить его исход.

Пользователь уже выбрал: временный read-only editor во время Save; automatic reconciliation после timeout; retry той же операции без новой Revision; без silent overwrite при конфликте/утрате owner. Эти требования не предлагаются на повторное подтверждение.

## 2. Что требуется от storage adapter

Domain repository предоставляет publishOnce(expectedHead, commitBytes), возвращающий PUBLISHED / HEAD_ADVANCED / UNKNOWN. Ни UI, ни domain не работают напрямую с Drive IDs.

Свойства primitive:

1. Публикуется целая небольшая JSON-запись либо не публикуется ничего.
2. Два writers одного next slot не могут опубликовать два разных результата.
3. Уже опубликованный slot immutable; retry не заменяет его bytes.
4. Unknown response разрешается чтением того же slot и проверкой bytes/hash.
5. После смены head старый delayed request не может перезаписать более новое состояние.
6. Читатели устанавливают опубликованный непрерывный префикс; отсутствие listing notification не равно отсутствию commit.

Простого check-then-write, in-process mutex или настройки Cloud Run на один instance недостаточно для обещания этих свойств во всех runtime roles/retries. Lease остаётся per Entry; serialization публикаций не блокирует редактирование разных Entries.

### 2.1. Предлагаемая реализация для первого Drive adapter

Выбранный для проработки кандидат — **append-only slots с заранее выделенным Drive file ID**, без предположения о недокументированном If-Match для media update.

- storage_manifest.json содержит genesis и binding первого пустого slot.
- Каждый commit содержит sequence, previous ref/hash, изменения объектов, nextSlot (logical path + заранее выделенный provider ID).
- Публикация slot выполняется create с **уже известным общим ID этого slot**, в одном multipart metadata+JSON content upload. Не создаём сначала пустой файл с тем же ID.
- Все contenders следующей позиции используют один ID из предыдущего commit, а не собственные новые ID.
- При успехе slot занят; при 409 читаем его и отличаем собственную публикацию от победившей чужой.
- Следующий writer использует nextSlot из победившего commit, пересчитывает preconditions на новом head и лишь затем пытается append.
- Имя файла и поиск по имени не являются create-if-absent примитивом.
- Candidate nextSlot ID выделяется до отправки publication. Неопубликованные pre-generated IDs не являются видимыми изменениями домена.
- Пока slot UNKNOWN, нельзя перескочить его и объявить свою операцию неуспешной. Читаем точный ID; отсутствие доступа/временная ошибка не трактуются как EMPTY.
- Если прочитан другой commit, прошлый delayed create получит occupied slot и не сможет повредить новый head. Тот же operationId в следующем slot разрешён только после replay и проверки, что он ещё не завершён.

Инициализация storage — отдельный однократный bootstrap под maintenance: создаётся один выбранный manifest/genesis и проверяется его identity. Две независимо созданные папки/manifest с одинаковым именем не объединяются автоматически. Если manifest/genesis неоднозначен или повреждён, mutations запрещены до reconciliation.

Для cold start можно кешировать проверенный checkpoint resource map, но безусловно доверять mutable HEAD.json нельзя. Актуальность проверяется чтением nextSlot по известному ID до подтверждённого хвоста; permission/network failures дают UNKNOWN. Старые commit records остаются источником восстановления checkpoint.

Предыдущий commit связывает logical path с provider ID. Для offline backup/export нужен полный набор commit records, referenced snapshots и manifest; при чтении локальной копии используются paths/hashes. Перенос на другой Drive/account требует явного rebind/bootstrap под maintenance с validation, новым storage incarnation и сохранением импортированной истории, а не слепого использования старых Drive IDs. Это часть future migration tooling, не runtime ручное редактирование manifest.

Это **архитектурный вывод из документированного create/retry behavior, не выполненный integration test**. Вариант с CAS одного root manifest короче, но для Drive v3 media update подтверждённая CAS-гарантия в проверенной reference не установлена; не выдаём её за существующую возможность. Если другой adapter имеет проверенный CAS, он может публиковать эквивалентный head с теми же domain guarantees.

### 2.2. Что подтверждено источниками, а что ещё проверить

Официальные материалы проверены 18.10.2026:

| Факт / основание | Источник | Следствие для проекта |
|---|---|---|
| Pre-generated file IDs допускают retry после timeout; успешный повтор получает 409 без дубликата; это не для обычных Workspace documents | [Drive uploads](https://developers.google.com/workspace/drive/api/guides/manage-uploads#use_a_pre-generated_id_to_upload_files), [generateIds](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/generateIds) | Publication — обычный JSON blob с известным file ID |
| Batch разбирается на отдельные calls, порядок исполнения не гарантируется; media uploads не поддерживаются batch | [Drive performance / batch](https://developers.google.com/workspace/drive/api/guides/performance#batch_requests) | Batch не используется как atomic Save |
| files.update меняет metadata/content; просмотренная reference не описывает If-Match precondition | [files.update](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update) | Отсутствие описания не доказывает невозможность CAS; capability надо отдельно проверять |
| Cloud Run может иметь разные instances/revisions; runtime координация не равна file commit guarantee | [Cloud Run autoscaling](https://docs.cloud.google.com/run/docs/about-instance-autoscaling) | Не опираемся только на локальный Mutex API process |

**Обязательный adapter spike до mutating release**, не вопрос пользователю: два конкурирующих multipart create одного pre-generated ID; потеря ответа; read after timeout; crash во время upload; schema/hash verification получившегося blob; 403/404 distinction при OAuth revoke; ID bindings при backup/rebind. Если возможно существование видимого неполного slot без безопасного восстановления, этот candidate не проходит gate и mutating release блокируется до другого проверенного primitive. Чужой/повреждённый существующий slot нельзя PATCH-нуть как способ исправить конкуренцию.

Не было доступа к low-level Drive test harness в этом проходе; реальный дневник не изменялся.

## 3. Публикуемые объекты и concurrency

Commit содержит изменения resource map: resourceKey, before (expected FileRef/null), after (новый полный snapshot/null). Для примера: entry:entry_demo, catalog:tags, operation:op_save_demo. Resource map восстанавливается replay; DB-проекция не является единственной копией карты.

Одной публикацией Save:

- Entry state: currentRevisionId/ref → новая Revision; committedUpdatedAt → assigned server timestamp; draftRef → null; pendingOperationId → null.
- Catalog state: включить новые pendingTags, если они есть.
- Operation result: COMMITTED, тот же operationId/input fingerprint и revisionId/ref.
- При Apply — durable proposal resolution с revisionId; при Restore — provenance restoredFromRevisionId.
- Lease/ownership changes, когда нужны, проходят тот же publication boundary, а не независимое blind update.

References на требуемые live snapshots заранее проверены по hash. Если required payload недоступен, это STORAGE_INCOMPLETE/recovery, а не тихое отображение половины commit. Committed история не считается потерянной из-за отставшего entry.md.

### 3.1. Fencing и catalog collisions

Entry owner имеет session/job ID и mutationEpoch. При takeover/cancel/revoke epoch меняется через публикацию. Writer проверяет одновременно:

- актуальный owner/epoch;
- baseRevisionId=currentRevisionId;
- текущий draftId/draftVersion совпадает с frozen input;
- pendingOperationId соответствует операции;
- operation не завершена и не отменена;
- текущий catalog snapshot допускает изменения;
- assets и schema удовлетворяют выбранным preconditions.

Проверка и append относятся к одному expected global head. Любая публикация между ними займёт этот slot, старый create не перезапишет победителя. После HEAD_ADVANCED нужно перечитать/replay и проверить всё заново. Нельзя просто послать прежний commit в новый slot.

Expiry timestamp позволяет инициировать revoke/takeover; новый owner не появляется только от изменения часов. Revocation и Save конкурируют в одной цепочке: выигравшая публикация определяет порядок. После опубликованного revoke старая epoch не может commit в следующий slot. Проверка timestamps не заменяет этот fencing.

Глобальный короткий append нужен для линейного согласования shared catalog; не вводится global editing lease. Параллельные Draft разных Entries допустимы. При высокой нагрузке chain/latency может потребовать иной adapter, checkpoint или шардирование; это implementation capacity question FQ-10.

При совпадении нового name/alias с чужим active/deleted владельцем — validation conflict с указанием тега, Draft остаётся. Нет silent reuse, rename, transfer или merge. Redirect dedupe существующих IDs допустим по принятому FQ-02.

## 4. Идентичность операции

operationId создаётся один раз на явное действие и сохраняется клиентом до отправки. Retry использует тот же ID.

Durable operation input включает command kind, entryId, baseRevisionId, draftId/version либо source proposal/restore ID, input snapshot refs/hash, parserVersion и owner epoch. Payload для Save фиксируется **после** финального flush Draft. Изменить тело под тем же operationId нельзя.

- same operationId + same fingerprint + published result → вернуть тот же result, даже если Entry уже имеет более новую Revision;
- same operationId + different fingerprint → IDEMPOTENCY_MISMATCH, никакого commit;
- operation ещё открыта → status/recovery той же операции;
- новая осознанная попытка с изменёнными данными после definite failure → новый operationId;
- operation ID не равен HTTP request ID и не пересоздаётся при reconnect.

Операционные retry metadata не меняют исходный input fingerprint. Snapshot нормализованного текста после подготовки также фиксируется; повтор после timeout не запускает заново произвольную AI обработку и не меняет текст из-за новой catalog spelling policy.

## 5. Save по шагам

| Шаг | Durable действие | Что видно пользователю |
|---|---|---|
| 0. Preflight | Проверить валидность полей/lease и готовность всех оставленных attachments; финальный flush полного Draft со связями/intent | Draft ещё не committed; незавершённые вложения держат Save disabled |
| 1. Register | Подготовить operation input; опубликовать pendingOperationId + durable operation PREPARING при совпавших draft/version/base/epoch | Saving; поля и повтор Save read-only |
| 2. Prepare | Нормализовать hashtags; подготовить immutable Revision JSON/text, новый catalog snapshot при pendingTags, новый Entry state и result receipt | Старый committed Current + Draft, без половины новой версии |
| 3. Revalidate | Прочитать актуальный head, проверить owner/base/draft/catalog/assets, все hashes | Saving / conflict при нарушении условий |
| 4. Publish | create-once одного next slot с совместными after refs | Новая версия становится committed целиком |
| 5. Confirm | Прочитать publication/result и вернуть revisionId той же операции | Saved; редактор доступен |
| 6. Materialize | Обновить удобные current files, убрать только consumed Draft payload, вызвать derived consumers | Save уже состоялся; отдельная проекция может отставать |

Register — тоже публикация, но не content Revision. Если клиент закрылся до Register, новый backend ничего не обещает о неотправленных правках; local recovery и ранее подтверждённый durable Draft остаются. Не обозначать browser-only ввод как durable.

Prepared candidates в operation refs сами по себе не меняют Current/catalog. Повторная подготовка после конкурентного catalog change использует новый candidate ID только при необходимой technical revalidation; внешний ответ Save всё равно один committed revisionId. Текст зафиксированного input не меняется молча.

**[Д, 18.10.2026]** Manual Save, при котором итоговое сохраняемое content совпадает с текущей committed Revision, завершает эквивалентный Draft без новой Revision. Возвращается NO_CHANGE со ссылкой на существующую Revision; committedUpdatedAt и content History не меняются. Consume именно этого Draft и результат операции фиксируются durable с обычными ownership/base/idempotency checks. У новой Entry без Current первый успешный Save создаёт первую Revision. Согласованное создание Revision при Apply/Restore сохраняется. [FQ-03/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md). Техническая ветка NO_CHANGE описана ниже.

## 6. Что происходит после сбоя

| Момент | Доказательство исхода | Восстановление |
|---|---|---|
| До Register | Операция отсутствует в опубликованной карте | Current прежний, подтверждённый Draft доступен; повтор с тем же ID допустим после checks |
| Register опубликован, ответ потерян | pendingOperationId и operation input в chain | Найти ту же операцию; оставить editor read-only |
| Upload candidate оборвался | Нет финальной publication; hashes неполны | Не считать Revision committed; восстановить кандидаты из frozen input либо definite failure с сохранением Draft |
| Часть Revision/catalog files записана | Файлы staged, но map не переключена | Current/catalog остаются прежними; retry той же операции |
| Другой tag/Entry/lease commit занял slot | Слот содержит другой operation/hash | Replay; перепроверить preconditions; safe retry или conflict, без overwrite |
| Publication request timeout | Исход UNKNOWN | Читать точный slot ID и chain/result; не объявлять fail только по timeout |
| Publication прошла, response потерян | В map есть COMMITTED operation result | Вернуть ту же Revision; новая не создаётся |
| Publish прошёл, Draft files не удалены | Entry state уже имеет draftRef=null и consumed draftVersion в result | Не показывать старый Draft; idempotent physical cleanup |
| Пользователь создал новый Draft после success | Новый draftId/version опубликован | Старый cleanup не удаляет его; удаляется конкретный consumed snapshot |
| Current уже стал более новым | Исторический receipt operationId остаётся | Вернуть исходный revisionId, не менять Current назад |
| Owner/base отозван до final publication | Новый head с epoch/base mismatch | Stop, записать conflict/failed result безопасной публикацией, сохранить Draft |
| Drive/OAuth недоступен | Доказательства commit нет | Storage unavailable / Checking save, local copy доступна для чтения/копирования; нет ложного успеха |
| Slot или snapshot повреждён внешним writer | Schema/hash/chain violation | Остановить дальнейшие mutations storage, recovery/reconciliation; не пропускать дыру |

Definite failure возможен, когда незавершённые publication attempts fenced: спорный slot занят известной записью, включая cancel/failure, а результат операции отсутствует. Один временный 404 или отсутствие файла в list не доказывает, что delayed create больше не завершится. При cancel выигрывает либо commit, либо cancel, в установленном chain порядке; уже совершившийся commit нельзя объявить отменённым.

Сбой после публикации не откатывается удалением committed файлов. После definite failure может быть удалён только неопубликованный staging; Draft и пользовательские originals не уничтожаются.

## 7. Cleanup, Draft и GC

Успех логически consume Draft **в том же commit**, где меняется currentRevisionId. Удаление draft directory по стабильному пути не является commit point.

Cleanup перечисляет конкретные object IDs/paths consumed snapshot, сверяется с текущими refs и pending operations, не удаляет достижимый новый Draft. Отложенный materializer/cleanup не имеет права blind-write поверх новой generation. После сбоя replay восстанавливает current Draft без сканирования случайных старых папок как активных.

Reachability включает: Current, обязательную Revision history, текущие Draft всех Entries, pending operations, raw/provenance и необходимые audit/results. Старые committed Revision payload не собираются как мусор. Неопубликованные candidates могут очищаться только после fencing всех возможных late publication requests. Одного возраста файла недостаточно.

Draft autosave generation хранится только пока актуальна или нужна незавершённой операции; не создаётся постоянная server autosave-history. Retention orphan uploads, operation receipts, tombstones и permanent-delete records согласуется с FQ-08. До утверждения retention не вводить автоматическое destructive GC пользовательских originals.

## 8. Проекции, background work и long-running jobs

Уже принято, что Calendar Timeline и индексы derived. Проект рекомендует: success Save зависит от durable canonical publication, не от Calendar, search index или thumbnail. Ошибка проекции не превращает состоявшийся commit в failed Save. Она имеет собственный retry/status.

Очередь может быть operational, но её потеря не должна навсегда потерять доставку. Consumer восстанавливает pending work сравнением canonical publication/version с собственным checkpoint; idempotency key содержит storage incarnation, consumer, entryId и targetRevisionId. Для Calendar при нескольких Revision до синхронизации можно проектировать доставку актуального Current; exact integration contract/lifecycle mapping ещё INT-03/FQ-09.

После restart recovery сканирует незавершённые operation refs из опубликованной map. Не рассчитывать, что background callback продолжится в умершем HTTP container. Выбор очереди/jobs API остаётся AQ-API-004; этот документ не забирает чужой active AQ-API-003 и не фиксирует HTTP endpoints.

## 9. Другие commands и внешние изменения

- Apply публикует result Revision и resolution proposal вместе. Retry не применяет proposal повторно.
- Restore historical создаёт новый snapshot с previousRevisionId=Current и restoredFromRevisionId=selected. Более поздняя история сохраняется.
- AI_INITIAL_NORMALIZATION и AI_EXISTING_TAGS используют тот же commit path с policy/trace; existing Entry с Draft пропускается. Внешний LLM ответ не обходит lease/base.
- Merge каталога — catalog/audit publication без content Revision Entries.
- Lifecycle operation — новый Entry state/audit, без content Revision. **[Д, 18.10]** Restore Entry из Trash всегда устанавливает ACTIVE, включая прежние Archived; сохраняет identity, Current/history и Draft. Прежний lifecycle не используется как target Restore. [FQ-08/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/01_SQ-01_restore-lifecycle/00_thread.md).
- External file change — сохранить bytes/evidence, schema validate, затем новая Revision или recovery. Не принимать ручные identity/system pointer правки автоматически.

Пока старые Calendar/Telegram pipelines пишут напрямую, общий протокол не обеспечивает атомарность их конкурентных записей. Targeted storage v1 подключается под maintenance после остановки/перевода writers либо сохраняется для read-only пилота. Это deployment/migration constraint; текущие рабочие pipelines не переписываются автоматически данным документационным коммитом.

## 10. Вопросы пользователю, по очереди

### SQ-01 — решён: вложения в Draft и Save до готовности

[FQ-03/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md).

**[Д, 18.10.2026]** Save недоступен, пока хотя бы одно оставленное вложение имеет неразрешённый статус: выбрано, загружается, проверяется, ошибка или требуется повторный выбор файла. Для продолжения нужно завершить загрузку/проверку, повторить её либо явно убрать вложение. Все оставленные attachments должны быть готовы к включению в Revision; для managed файла это подтверждённый original, для external — сохранённый валидный reference без обязательного скачивания original. Генерация thumbnail/preview не блокирует Save. До начала commit текст продолжает autosave в Draft.

Draft сохраняет весь состав вложений: связи с готовыми Asset, pending upload IDs, имена файлов, статусы и ссылки на durable upload/staging records. Успешно загруженные originals сохраняются в user-owned storage и остаются достижимыми из Draft до завершения Save или явного действия пользователя; уход со страницы и повторное открытие не должны терять вложения. Pending запись не исчезает при ошибке или перезапуске. Bytes, ещё не полученные хранилищем, не выдаются за durable: если продолжить upload автоматически нельзя, Draft сохраняет attachment intent и показывает «Выберите файл повторно». Удалять staging/original, на который ссылается актуальный Draft или незавершённая операция, нельзя.

Альтернатива сохранить готовую часть сейчас не выбрана. Условие готовности вложений проверяется и в UI, и backend preflight, затем перед публикацией. Успешный upload не создаёт Revision и не должен незаметно менять уже committed content. Lost Save response/read-only editor остаются отдельным уже принятым flow.

### SQ-02 — решён: manual Save без изменения content

**[Д, 18.10.2026]** Manual Save, при котором итоговое сохраняемое content совпадает с текущей committed Revision, завершает эквивалентный Draft без новой Revision. Возвращается NO_CHANGE со ссылкой на существующую Revision; committedUpdatedAt и content History не меняются. Consume именно этого Draft и результат операции фиксируются durable с обычными ownership/base/idempotency checks. У новой Entry без Current первый успешный Save создаёт первую Revision. Согласованное создание Revision при Apply/Restore сохраняется.

Перед сравнением проверяются актуальные lease/base, готовность вложений и выполняется принятая нормализация mentions. Сравниваются title и итоговый text точно, EventTimeRange со всеми сохранёнными датами/временем/точностью/timezone, набор canonical tagIds после разрешения redirects и набор assetIds. Порядок IDs не является изменением содержимого в текущей версии без ручной сортировки вложений. Текстовые пробелы, переносы строк и регистр не игнорируются; case-insensitive lookup тегов не означает case-insensitive сравнение текста. Служебные draftId/draftVersion/updatedAt, session/lease/operation metadata, file paths и Drive IDs в content equality не участвуют. Сами media bytes заново не сравниваются: Entry меняет ссылки по assetId, а Asset metadata/original имеют отдельный контракт.

**[П, реализация]** Для первого варианта достаточно прямого equality сравнения подготовленного content projection. Сравнивается фактический текст по textRef, а не путь/Revision ID JSON-файла. Full-file hash включает служебные поля и не является content equality. Cached content hash можно добавить позднее как ускорение; совпадение hash не отменяет checks и точное сравнение. Контракт сериализации времени/parser version должен оставаться явным.

NO_CHANGE публикует новый Entry state с прежней Current/committedUpdatedAt и без consumed Draft, плюс terminal operation receipt со ссылкой на существующую Revision. Не создаёт Revision/catalog snapshot без реальных catalog изменений, не обновляет Calendar как новую версию. Все base/ownership checks выполняются перед этой веткой, иначе возвращается conflict.

| Различие | Итог manual Save |
|---|---|
| Поправили текст и вернули исходный; весь content совпал | NO_CHANGE, без новой Revision |
| Добавили один пробел или изменили регистр текста | Новая Revision |
| Изменилась timezone или точность event time | Новая Revision |
| Изменился только Draft.updatedAt/session/путь к text snapshot | NO_CHANGE при прочем совпадении |
| Порядок tagIds/assetIds изменился, набор тот же | NO_CHANGE при прочем совпадении |
| Изменился набор связанных тегов или материалов | Новая Revision |
| Catalog merge дал тот же canonical набор, текст прежний | NO_CHANGE при прочем совпадении |
| Current отсутствует | Первая Revision при успешном Save |

**История:** [FQ-03/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md).

### Что не нужно выбирать пользователю сейчас

JSON layout, FileRef/hashes, operation ID, fencing, слот публикации, восстановление views и adapter spike — техническая проработка. Реальные ограничения/изменения пользовательского поведения выносятся отдельно. FQ-04 grammar, FQ-05 time policy и FQ-08 destructive retention остаются явно открытыми; этот проект их не закрывает.

## 11. Проверки перед реализацией

**Проверка комплекта 18.10.2026:** JSON Schema Draft 2020-12 прошла schema validation; 16 JSON records в 19 виртуальных файлах валидны; 33 FileRef/hashes совпали с точными bytes. Replay трёх фаз проверил Current/Draft/catalog/operation outcome; namespace/redirects, previous Revision и стабильный retry result согласованы. Негативные fixtures с duplicate tagIds, неверным hash и устаревшим before condition отклоняются проверкой примера. Это проверка спецификации и fixture, а не работающего backend.

Документационный комплект имеет core JSON Schema и пример before/prepared/after. Проверяется schema, точные hashes, foreign refs, previous revision chain, pending new tag → canonical tag, consumed Draft, операция → та же Revision, отсутствие new tag в before.

Это **не runtime тест Drive** и не доказательство distributed safety.

Перед mutating release обязательны:

1. Adapter spike §2.2 и failure injection на каждом шаге таблицы §6.
2. Две Entries одновременно создают одинаковые canonical name/alias; один победитель, второй conflict с сохранённым Draft.
3. Takeover/cancel между validate и publish; старый request не может дописать после fence.
4. Повтор Save/Apply/Restore после потери ответа и после следующего successful Save.
5. Удалить derived map/cache и rebuild; не потерять Draft, history, trace и operation outcome.
6. Crash после consume Draft, затем новый Draft и поздний cleanup.
7. Внешняя правка JSON/Markdown, revoked OAuth, неполный backup/rebind.
8. Отдельная проверка retention/permanent delete: никогда не возвращать удалённые media bytes из staged copies или audit snapshots.

Открытые gate: adapter spike, parser/time validators и destructive retention design по применимости. SQ-01 по вложениям и SQ-02 по NO_CHANGE закрыты. До их закрытия документ пригоден для review и декомпозиции, но не обещает готовый production commit protocol.

## 12. Уточнение 18.10.2026 — Discard / unlink готового Asset

При снятии связи Asset с записью, в том числе при Discard добавлений Draft, применяется одно правило: если снимаемая связь единственная, предложить удалить сам Asset; если есть другие логические связи, снять только текущую без предложения глобального удаления в этом flow. Удаление — только по явному подтверждению и означает soft delete в Asset Trash, не permanent delete. При отказе от удаления связь всё равно снимается, Asset остаётся в библиотеке; при отсутствии Active Entry links он виден в Unlinked.

Проверяются логические потребители по разным entryId во всех lifecycle-состояниях, в других Draft и связанных незавершённых операциях; исторические references других Entries не теряются. Несколько Revision/Draft одной и той же Entry не считаются отдельными записями; historical link той же Entry сам по себе не запрещает предложить soft delete, поскольку история/links сохраняются. При Discard рассматриваются только связи, реально исчезающие относительно восстанавливаемой Current: Asset, остающийся в Current, не является кандидатом на удаление из-за Discard. Проверка актуальна перед выполнением; при новой чужой связи выполняется только unlink. Состояние Unlinked по Active-счётчику не используется как доказательство единственности. Незавершённая операция с неизвестным исходом сначала требует reconciliation.

**[П, физический протокол]** Discard и действие над Asset используют согласованный mutation/revalidation path; сначала выясняется unknown Save, затем проверяются disappearing relations и остальные потребители. Durable результат выбора привязан к конкретным Draft/assetIds; retry не повторяет диалог и не удаляет другой Asset. Исчезновение Draft не разрешает позднему callback восстановить отменённую Entry. Soft delete не удаляет media bytes; permanent deletion остаётся отдельной явной операцией из Trash. Автоматическая судьба upload, закончившегося только после уже состоявшегося Discard, ещё требует FQ-08 решения. **История:** [FQ-08 — снятие связи / Discard](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/00_thread.md).
