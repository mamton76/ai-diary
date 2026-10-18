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

Приоритет имеют новые прямые решения пользователя. Неоднозначность между документами выносится в §14, а не разрешается молчаливым выбором разработчика. Правило «Revision только по Save» относится безусловно к ручному Draft; 18.10.2026 подтверждено: Apply и Restore исторической версии сразу создают по одной новой Revision без дополнительного Save. Также сохранены два случая автоматического AI commit: первая normalization из raw и добавление existing tags по разрешённой routine policy (§9.2). FQ-01 закрыт.

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
| INV-11 [Д] | Permanent delete Asset удаляет только управляемые дневником bytes/preview и сохраняет tombstone для исторических ссылок; внешние originals не удаляются |
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
| ENT-08 [Б/Д, 18.10] Restore revision | Выбрана история; разрешены текущий Draft/conflict/lease | Новая Revision с restored-from reference; прежняя история сохранена | Перемотка указателя с удалением более новых revisions |

**[Б]** Ручная editing session начинается с первой правки, не от открытия записи для чтения. Операции одинаковы независимо от места входа. При сворачивании/смене карточки и уходе с нового unsaved Entry необходим явный Save / Discard / Return later; без изменений диалог не нужен.

**[Д]** После Save нормализуются tag mentions (§6) и создаются pending new tags из Draft; самопроизвольный `#word` не создаёт catalog tag. **[О]** Точный порядок и восстановление частично выполненного многофайлового Save — FQ-03.

**[Д, 18.10.2026]** Manual Save, при котором итоговое сохраняемое content совпадает с текущей committed Revision, завершает эквивалентный Draft без новой Revision. Возвращается NO_CHANGE со ссылкой на существующую Revision; committedUpdatedAt и content History не меняются. Consume именно этого Draft и результат операции фиксируются durable с обычными ownership/base/idempotency checks. У новой Entry без Current первый успешный Save создаёт первую Revision. Согласованное создание Revision при Apply/Restore сохраняется. [FQ-03/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md).

**[Техническая конкретизация]** Перед сравнением проверяются актуальные lease/base, готовность вложений и выполняется принятая нормализация mentions. Сравниваются title и итоговый text точно, EventTimeRange со всеми сохранёнными датами/временем/точностью/timezone, набор canonical tagIds после разрешения redirects и набор assetIds. Порядок IDs не является изменением содержимого в текущей версии без ручной сортировки вложений. Текстовые пробелы, переносы строк и регистр не игнорируются; case-insensitive lookup тегов не означает case-insensitive сравнение текста. Служебные draftId/draftVersion/updatedAt, session/lease/operation metadata, file paths и Drive IDs в content equality не участвуют. Сами media bytes заново не сравниваются: Entry меняет ссылки по assetId, а Asset metadata/original имеют отдельный контракт.


**[Д, 18.10.2026] Явные commit-действия:** Save, Apply и Restore исторической версии сразу создают по одной новой committed Revision после успешного выполнения. Apply/Restore не требуют дополнительного Save. Preview, ручное редактирование Result до Apply и обычный autosave ещё не commit. Эта формулировка не распространяется на восстановление Entry из Trash.

### 4.2. Lifecycle

**[Д]** Active / Archived / Trash. UI-0.5 содержит прежнее техническое обозначение DELETED для Trash; окончательный enum сериализации выбирается отдельно.

| ID | Операция | Семантика |
|---|---|---|
| ENT-09 | Archive | Явное действие пользователя «Архивировать»; автоматический перенос по возрасту не задан. Меняет lifecycle/audit без content Revision; Entry переносится вместе с Draft; короткое confirmation; draft доступен при открытии архива |
| ENT-10 | Delete | Entry с Revision переходит в Trash вместе с Draft; новая Entry без Revision может быть удалена целиком |
| ENT-11 [18.10] | Restore from Trash | Всегда возвращает Entry в ACTIVE, включая ранее Archived; сохраняет identity, history и Draft. Не является Restore исторической Revision и не создаёт content Revision |
| ENT-12 | Delete permanently | Доступно из Entry Trash; автоматический таймер permanent delete пока не нужен |

**[Д, 18.10.2026]** Restore Entry из Trash всегда возвращает запись в ACTIVE, независимо от того, была она Active или Archived перед удалением. Сохраняются тот же entryId, Current/content history и существующий durable Draft. Операция меняет lifecycle/audit и не создаёт content Revision; это не Restore исторической Revision. [FQ-08/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/01_SQ-01_restore-lifecycle/00_thread.md). Предложение вернуть Archived Entry в архив не принято. **[О]** Последствия permanent delete для связанных объектов и audit retention остаются FQ-08; [объём удаления содержимого обсуждается в SQ-03](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/03_SQ-03_entry-permanent-delete-content/00_thread.md); само наличие Restore/permanent delete уже принято.

### 4.3. EventTimeRange

**[Д]** From date обязательна; From time optional. To может отсутствовать целиком, To time optional. Отсутствующее время не превращается в `00:00`. Одна редактируемая timezone на интервал, default из user/device settings, входит в versioned content. **[П/Б из UI-0.5]** Конец не должен предшествовать началу; обработка смешанной точности требует формализации.

**[Д, 18.10.2026]** Основное отображение Entry использует местные дату и время события в его сохранённом часовом поясе. При ручном создании пояс события по умолчанию берётся из настроек пользователя, если он там задан; иначе сохраняется прежний fallback на пояс устройства. Явно выбранный пояс события имеет приоритет над default. Пояс сохраняется в EventTimeRange записи; последующая смена пользовательских настроек не пересчитывает и не переписывает её местные дату/время или timezone. Если время суток отсутствует, оно не подставляется. **История:** [FQ-05/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/02_SQ-02_event-time-display/00_thread.md). Физическая сериализация точного момента/offset, неоднозначности перевода часов и UI вторичного пересчёта остаются открытыми.

**[Д, 18.10.2026]** Отсутствие To у Entry означает одиночное событие на указанную From дату/время, без автоматического продолжения до текущего дня или в будущее. Если указана только дата, дневной Calendar и связанный date filter относят запись к этой местной дате без выдуманного времени суток. Если задано время, опорой служит указанный момент без придуманной длительности. Это правило не меняет односторонние границы query filter. **История:** [FQ-05/SQ-04](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/04_SQ-04_missing-event-end/00_thread.md). **[Д, 18.10.2026]** У интервала записи с From/To, заданными датами без времени, последний указанный день To включается целиком в пользовательском смысле. «Поездка 1–10 июля» видна и при выборе 10 июля. Date-only верхняя граница фильтра «по 10 июля» также включает весь указанный день. Сохранённые значения остаются date-only: фиктивные 00:00/23:59:59 в EventTimeRange не записываются. [История SQ-05](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/05_SQ-05_date-only-end-inclusion/00_thread.md). **[Д, 18.10.2026]** Запись с известной датой, но без времени суток, включается в фильтр по часам того же дня как возможное совпадение. Например, «18 октября» без времени попадает в «18 октября, 12:00–14:00». В результате сохраняется явная пометка «время не указано»; запись не получает выдуманные часы, длительность на весь день или новое content-значение. [История SQ-06](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/06_SQ-06_date-only-clock-filter/00_thread.md). Точное сопоставление разных timezone, DST и смешанных границ остаётся технической проработкой FQ-05.

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

**[П, техническая проработка 18.10.2026]** Подготовлены [файловый формат v1](07-file-format-v1-draft.md) и [Save/recovery design](08-save-recovery-design.md): immutable snapshots, общая publication record, operation outcome и логическое consume Draft. Это проект, а не принятое физическое решение; Drive adapter spike и validation gates указаны в документе. [SQ-01 — незавершённый managed upload](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md) решён: Save ждёт готовности всех оставленных attachments; состав вложений и upload state сохраняются в Draft (§7). Сам физический publication protocol остаётся техническим предложением.

**STO-07 [Д, 18.10.2026].** Если подтверждение Save потеряно, приложение показывает «Проверяем сохранение» и после восстановления связи автоматически выясняет исход операции. При уже состоявшемся commit возвращается та же Revision; если commit не состоялся, безопасно повторяется та же операция с тем же operationId и зафиксированным snapshot. Повтор не создаёт дубликат и разрешён только при актуальных base/ownership checks, без отмены/замены операции. При conflict или потере права записи автоматический commit прекращается с понятным сообщением; введённые данные сохраняются. Неизвестный исход не выдаётся ни за успешное, ни за достоверно неуспешное сохранение. [FQ-03](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/00_thread.md). Механизм durable operation journal и multi-file commit/recovery остаётся техническим вопросом STO-06.

**STO-08 [Д, 18.10.2026].** В первой версии после начала Save редактируемые поля этой Entry и повторный Save временно блокируются до определения результата операции. Просмотр, прокрутка и копирование текста доступны. При потерянном подтверждении действует автоматическая проверка/безопасный retry той же операции, статус «Проверяем сохранение»; редактор остаётся read-only. После подтверждённого успеха редактор доступен с сохранённым состоянием. После достоверного отказа без commit и без конфликта блокировка снимается, исходный Draft сохраняется для исправления/повтора. Conflict или утрата lease разрешаются соответствующим flow; сохранённый текст не очищается и право записи самовольно не восстанавливается. Продолжение ввода параллельно неподтверждённому Save в первую версию не включается. [FQ-03](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/00_thread.md).

## 6. Tags и отношения

| ID | Требование [Д] |
|---|---|
| TAG-01 | Связь Entry–Tag хранится через canonical tagId; chips показывают этот набор; raw hashtag relationship не определяет |
| TAG-02 | Lookup ищет canonical name и aliases; прямой name match выше alias-only. При выборе alias вставляется именно он, chip показывает canonical name |
| TAG-03 | `Create #new` — явное действие; новый тег до Save существует только в Draft. Save создаёт canonical tag, Discard не оставляет мусор в каталоге |
| TAG-04 [18.10] | При Save недостающие linked hashtags дописываются в конец одной строкой через пробел, отделённой от непустого body пустой строкой. Имеющиеся canonical/alias упоминания не перемещаются и не дублируются; повторный Save не повторяет suffix. Заголовка Tags: нет |
| TAG-05 | Unlink меняет tagIds через Draft; при Save упоминания снятого тега переходят в #_name для поиска. Удаление hashtag из body без удаления chip связь не снимает |
| TAG-06 | Rename сохраняет tagId, добавляет старое имя в aliases; ручное удаление alias не меняет relations |
| TAG-07 | Merge выбирает survivor, переносит имя/aliases с дедупликацией; oldTagId становится mergedInto redirect. Current Entry/Draft relations разрешаются в survivor через каталог, без переписывания snapshots или новых content Revision |
| TAG-08 | Merge не переписывает immutable revisions. Survivor сохраняет type/color без дополнительных merge options |
| TAG-09 | Delete — soft delete, tagId и старые relations сохраняются. Name/aliases остаются занятыми без учёта регистра; при конфликтующем Create предлагается Restore прежнего тега. Новые links запрещены, autocomplete/cloud исключают тег. Used tag требует count/warning/confirmation |
| TAG-10 | Deleted filter и Restore доступны; permanent delete Tags пока отсутствует |
| TAG-11 | Types — пользовательский справочник; typeId optional; color непосредственно у Tag, без inheritance |
| TAG-12 | Entries count у Tag: уникальные Active Entries с текущими Draft, без Archived/Trash |
| TAG-13 [18.10] | Names/aliases — единое уникальное пространство между самостоятельными активными tags, сравнение и lookup без учёта регистра, отображение сохраняет выбранное написание. Конфликтующее обозначение не сохраняется, показывается существующий тег; автоматических merge/transfer/rebinding нет |

**[Д, 18.10.2026] Формат suffix:** При Save недостающие упоминания связанных тегов дописываются в конец body одной строкой, hashtags разделяются одним пробелом. От непустого текста эта строка отделяется пустой строкой; отдельного заголовка Tags: нет. Уже имеющиеся canonical/alias упоминания остаются на своих местах и не дублируются. Если все связанные теги уже упомянуты, новая строка не добавляется; повторный Save не создаёт повторный suffix. В пустом body добавляется только строка hashtags, без ведущей пустой строки. Маркер #_name не считается активным упоминанием. [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md).

**[Д, 18.10.2026] Снятые упоминания:** При Save упоминания явно снятого через chip тега преобразуются из #name в #_name, включая употреблённые aliases, с сохранением написанного обозначения. Маркер #_name остаётся в тексте, чтобы такие места можно было найти Text search; он не является активным hashtag, не создаёт связь и не восстанавливает chip. Не считать #_name присутствующим активным упоминанием при нормализации linked tags; обычный Tag filter по-прежнему работает по tagId/relations. Преобразование затрагивает упоминания снятого тега, а не все символы # в документе; повторный Save не добавляет второй underscore. Если тег добавлен обратно до Save, его упоминания не помечаются как снятые. Дополнительный вопрос на каждом Save для этого преобразования не требуется. [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). Редактор/парсер не выделяет #_name как активный тег и не запускает для него обычный tag autocomplete/Create.

**[Д, 18.10.2026] Политика aliases:** Один и тот же alias не может принадлежать двум самостоятельным активным canonical tags. Если alias уже занят, добавление его второму тегу отклоняется с указанием существующего тега; существующие теги автоматически не объединяются. Повторы aliases внутри одного canonical tag дедуплицируются. Merge redirect разрешается в survivor и не считается вторым самостоятельным владельцем alias. [FQ-04](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md). **[Д, 18.10]** Canonical names и aliases образуют единое пространство уникальных обозначений между самостоятельными активными canonical tags. Нельзя создать отдельный тег с именем, уже занятым как name или alias другого тега, либо назначить ему такое имя/alias. При конфликте показывается существующий тег; запись дубликата отклоняется без автоматического merge, переноса обозначения или перепривязки Entry relations. Идея отдельного переноса имени/alias между тегами сохранена на будущее; в текущий scope такой сценарий не включён. Уникальность проверяется всеми путями изменения каталога, включая pending tag Create при Save. **[Д, 18.10.2026]** Canonical names и aliases сравниваются без учёта регистра при проверке уникальности и lookup, включая autocomplete. Спорт, спорт и СПОРТ считаются одним обозначением; различие только в регистре не позволяет создать второй самостоятельный тег или занять его обозначение. Выбранное пользователем написание сохраняется для отображения, автоматическое приведение отображаемого текста к нижнему регистру не требуется. Это правило не меняет tagId и не переписывает существующий текст или immutable snapshots. **[Д, 18.10.2026]** После soft delete тега его canonical name и aliases остаются занятыми за тем же tagId, в общем пространстве обозначений без учёта регистра. Нельзя создать другой тег или назначить ему name/alias, совпадающий с обозначением удалённого тега. При таком конфликте интерфейс показывает удалённый тег и предлагает явный Restore существующего тега вместо создания нового. Сам ввод имени не восстанавливает тег автоматически. До Restore сохраняется запрет новых links и исключение удалённого тега из обычных autocomplete/cloud; прежние tagId, relations и история сохраняются. **[О]** Остальные правила Unicode/пробелов ещё уточняются; столкновения Rename/Create/Restore с другим активным владельцем обозначения не дают права молча перепривязать отношения.

**[Д, 18.10.2026]** Merge — операция каталога: oldTagId разрешается в survivingTagId через mergedInto redirect. Current Entry/Draft, поиск и счётчики используют canonical ID с дедупликацией; snapshots committed Revision и существующие Draft физически не переписываются, новые content Revision ради merge не создаются. Операция фиксируется в audit каталога. Следующий обычный Save может записать surviving ID; отдельной массовой миграции Entry нет. Type/color survivor и перенос aliases сохраняют ранее принятые правила. [Решение FQ-02](AI-Diary-Functional-Spec-v0.1.threads/01_FQ-02_tag-merge/00_thread.md). **[О]** Цепочки/циклы redirect, конкурентные операции каталога и их надёжная запись проектируются в протоколе хранения; уникальность names/aliases и маркер #_name уже согласованы в FQ-04; регистр при сравнении не учитывается; имена и aliases удалённых тегов также остаются занятыми; остальные правила Unicode/пробелов ещё открыты. Это не переоткрывает принятое отсутствие массовых Revision при merge.

## 7. Assets

**AST-01 [Д/Б].** Entry изменяет связи с Asset, не bytes самого файла. Один Asset может быть связан с несколькими Entries. Поддержаны выбор из библиотеки и upload; baseline external references сохраняются. Rename/description относятся к Asset metadata; rename не меняет сам файл.

**AST-02 [Д].** Library показывает все active Assets, включая Unlinked; поиск по filename и Asset name. Unlinked означает ноль связей с **Active Entries**, поэтому не доказывает отсутствия archived/historical references. Счётчики и destructive warnings должны различать эти области.

**AST-03 [Д; уточнение 18.10].** Unlink from Entry и Delete Asset from library — разные операции. При снятии связи Asset с записью, в том числе при Discard добавлений Draft, применяется одно правило: если снимаемая связь единственная, предложить удалить сам Asset; если есть другие логические связи, снять только текущую без предложения глобального удаления в этом flow. Удаление — только по явному подтверждению и означает soft delete в Asset Trash, не permanent delete. При отказе от удаления связь всё равно снимается, Asset остаётся в библиотеке; при отсутствии Active Entry links он виден в Unlinked. Отдельный явный Global Delete из библиотеки сохраняет свой confirmation/usage-warning contract. Soft delete сохраняет historical links и допускает Restore. [FQ-08 — снятие связи / Discard](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/00_thread.md).

**AST-04 [Д].** Из Trash доступны Delete permanently и Empty Trash. Физически удаляются только управляемые дневником managed file и preview; external originals у провайдеров не удаляются. Restore Asset внутри дневника после permanent delete невозможен. По assetId остаётся минимальный tombstone (например name/type/deletedAt), в Entry/history — нейтральный placeholder «Файл удалён».

**AST-05 [Д].** Display mode Grid/Gallery — UI preference, не content Entry. Captions и manual ordering в первой версии отсутствуют. **[F]** Inline placement между абзацами использует тот же assetId без копии файла, позиция versioned; удаление placement не обязано unlink/delete; embedded Asset нельзя silently unlink.

**AST-06 [Д, 18.10.2026].** Save недоступен, пока хотя бы одно оставленное вложение имеет неразрешённый статус: выбрано, загружается, проверяется, ошибка или требуется повторный выбор файла. Для продолжения нужно завершить загрузку/проверку, повторить её либо явно убрать вложение. Все оставленные attachments должны быть готовы к включению в Revision; для managed файла это подтверждённый original, для external — сохранённый валидный reference без обязательного скачивания original. Генерация thumbnail/preview не блокирует Save. До начала commit текст продолжает autosave в Draft. [FQ-03/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md).

**AST-07 [Д, 18.10.2026].** Draft сохраняет весь состав вложений: связи с готовыми Asset, pending upload IDs, имена файлов, статусы и ссылки на durable upload/staging records. Успешно загруженные originals сохраняются в user-owned storage и остаются достижимыми из Draft до завершения Save или явного действия пользователя; уход со страницы и повторное открытие не должны терять вложения. Pending запись не исчезает при ошибке или перезапуске. Bytes, ещё не полученные хранилищем, не выдаются за durable: если продолжить upload автоматически нельзя, Draft сохраняет attachment intent и показывает «Выберите файл повторно». Удалять staging/original, на который ссылается актуальный Draft или незавершённая операция, нельзя.

**AST-08 [Д, 18.10; техническая конкретизация подсчёта].** Проверяются логические потребители по разным entryId во всех lifecycle-состояниях, в других Draft и связанных незавершённых операциях; исторические references других Entries не теряются. Несколько Revision/Draft одной и той же Entry не считаются отдельными записями; historical link той же Entry сам по себе не запрещает предложить soft delete, поскольку история/links сохраняются. При Discard рассматриваются только связи, реально исчезающие относительно восстанавливаемой Current: Asset, остающийся в Current, не является кандидатом на удаление из-за Discard. Проверка актуальна перед выполнением; при новой чужой связи выполняется только unlink. Состояние Unlinked по Active-счётчику не используется как доказательство единственности. Незавершённая операция с неизвестным исходом сначала требует reconciliation.

**[Д, 18.10.2026]** AI Diary не удаляет originals внешних Asset у сторонних провайдеров (например, Google Photos или внешний Drive-файл). Unlink, soft delete, permanent delete и Empty Trash действуют на связь/Asset внутри дневника и собственные управляемые копии. Физическое удаление допустимо только для managed originals и производных файлов в хранилище, которым управляет дневник, по уже принятой политике Trash/permanent delete. Само наличие ссылки, доступа к внешнему файлу или прав API не делает его managed. Если внешний файл отдельно импортирован, удаляется только импортированная managed-копия, внешний original сохраняется. Для external Asset после permanent delete сохраняется принятый минимальный tombstone/placeholder без preview; его внешнее существование не обещает Restore Asset внутри дневника. Команд удаления original у внешнего провайдера нет. [История FQ-08/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/02_SQ-02_external-original-delete/00_thread.md).

**[О]** Cleanup частичных uploads/late completion, подробности historical warnings и техническая очистка собственных preview/cache при permanent delete — FQ-08. Для готового Asset после Discard уже принято условное предложение soft delete; автоматическое удаление не выбиралось. Удаление внешних originals закрыто запретом выше.

## 8. Выборки, поиск и производные данные

**QRY-01 [Д].** Generic filter expression: atomic `field/operator/value` и рекурсивные AND/OR/NOT. NOT — общий логический оператор. Text contains ищет title+body; Tag использует tagId; доступны Has draft, Has assets, State, Source, Has open AI proposals и derived Needs attention.

**QRY-02 [Д].** Event date/time range: optional From и To, каждая граница содержит date, optional time, timezone. Только From — односторонняя нижняя граница, только To — верхняя. Это не EventTimeRange самой записи: optional From фильтра не отменяет обязательность From date в записи.

**QRY-03 [Д].** Sorting: Event date/Updated/Created asc/desc, Title A–Z/Z–A; default Event date newest first. При Draft используется текущее Draft-state, включая Event date. Отдельного приоритета Drafts нет. **[Д, 18.10]** Сортировка «По изменению» учитывает последние содержательные правки Draft ещё до Save: при текущем Draft используется его content updatedAt, без Draft — committedUpdatedAt Entry. Это производный effectiveUpdatedAt для сортировки, а не изменение committed metadata и не новая Revision. Повторный autosave неизменного содержимого, heartbeat и технический progress загрузки не поднимают Entry заново. После Discard/NO_CHANGE без Draft используется прежний committedUpdatedAt. [FQ-06 — Updated sort](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/00_thread.md). Для новой Entry без committed Revision используется Draft.updatedAt (createdAt — fallback до первой content-правки); ни новая Entry, ни её Draft не исключаются из сортировки.

**QRY-04 [Д].** Current filters — ephemeral state. System preset задаёт initial expression; любая ручная правка отделяет фильтр от preset. Минимальный предварительный каталог: Drafts, Archived, Trash, Needs attention, Open AI proposals, Entries with assets, Last 7 days, Last 30 days и динамические Calendar/TagCloud/Statistics selections. Custom Saved Filters — future.

**QRY-05 [Д].** Entries из Main Navigation открывает Browser без filters; All entries не отдельная сущность. Переходы из Home передают явный lifecycle-фильтр единой настройки главной и условия выбранного виджета. UI-0.5 трактует отсутствие фильтров буквально, без скрытого State=Active.

**QRY-06 [Д].** Needs attention — наличие unresolved review item, например proposal, conflict или uncertainty. Несколько items одной Entry не дают несколько Entries в счётчике. Has open AI proposals — отдельный предикат; модель прочих review items пока [О].

**[Д, 18.10.2026]** В очередь, фильтр и счётчик «Требует внимания» входят только актуальные причины, требующие действия пользователя, в том числе ошибка AI-обработки, после которой без пользователя продолжить нельзя. Ожидание запланированного запуска, выполняющаяся обработка и назначенный автоматический повтор сами по себе не добавляют Entry в Needs attention: они показываются спокойным статусом, а временная ошибка с автоповтором — мягким предупреждением. Независимые причины внимания, например открытый proposal или conflict, при этом сохраняются. Одна Entry считается один раз; старый уже разрешённый failed run сам по себе причиной не является. **История:** [FQ-06/SQ-04](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/04_SQ-04_failed-ai-attention/00_thread.md). **[Д, 18.10.2026]** Пользователь может явно убрать из «Требует внимания» конкретную причину ошибки AI без успешного повторного запуска, если обработка больше не нужна. Снимается только эта причина; неуспешный Run и его история сохраняются и не помечаются успешными. Другие причины внимания Entry остаются; при отсутствии остальных причин Entry выходит из очереди и счётчика. Новая ошибка нового запуска может снова потребовать внимания и не наследует снятие прежней. Действие не удаляет Entry/историю, не создаёт content Revision, не выключает routine глобально и не отменяет выполняющийся job. [История SQ-05](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/05_SQ-05_dismiss-ai-error/00_thread.md).

**[Д, 18.10.2026]** Пока AI может продолжить работу автоматически, его статус визуально спокойнее причины, требующей пользователя. Конкретная палитра и thresholds автоматических retry требуют технической конкретизации; выбранный scope Needs attention уже задан выше. [FQ-06/SQ-04](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/04_SQ-04_failed-ai-attention/00_thread.md).

### Производные Home-выборки

**[Д, 18.10.2026] Единая область главной.** Пользовательская настройка «Учитывать архивные» действует на всю главную: Calendar, все показатели Statistics (включая Total entries, Drafts и Needs attention), TagCloud и EntryList. По умолчанию включена: ACTIVE + ARCHIVED; при выключении — только ACTIVE. TRASH исключён всегда. Настройка сохраняется между посещениями. Индикация, числа, размер тегов и показ записей используют эту область; переходы в Browser передают тот же lifecycle-фильтр вместе с условиями выбранного виджета. Переключение пересчитывает всю главную согласованно. Это позднее решение заменяет прежнее Active-only ограничение Home TagCloud/EntryList; периоды, сортировка и лимит 7 записей сохраняются. [История FQ-06/SQ-07](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/07_SQ-07_archive-visibility-setting/00_thread.md).

| Потребитель | Контракт [Д] |
|---|---|
| EntryList | 7 Entries в выбранной области главной, без периода, Event date desc; current Draft-state при наличии |
| TagCloud | Выбранная область главной за всё время; число уникальных связанных Entry определяет частоту и размер, Tag.color определяет цвет; deleted tags исключены. Первоначально до 30 самых частых; «Показать все» раскрывает остальные в том же облаке. Лимит не ограничивает подсчёт или результат клика. [UI-Q03](AI-Diary-Screens-Spec-v0.1.threads/01_UI-Q03_tag-cloud-limit/00_thread.md) |
| Calendar | Наличие записей по местным датам событий в сохранённых зонах; выбранный день/range преобразуется в универсальные From/To с той же date semantics. Без counts/state clutter в UI. [FQ-05/SQ-03](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/03_SQ-03_calendar-event-date/00_thread.md) Lifecycle Home Calendar по умолчанию — ACTIVE + ARCHIVED, без TRASH. [FQ-06/SQ-06](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/06_SQ-06_home-calendar-scope/00_thread.md). Общая настройка всей главной принята в [SQ-07](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/07_SQ-07_archive-visibility-setting/00_thread.md). |
| Total entries | За всё время; выбранная область главной; уникальные Entry, одинаковый scope счётчика и списка по клику. [FQ-06/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/02_SQ-02_total-entries-scope/00_thread.md) |
| Drafts, Needs attention | За всё время; выбранная область главной; одинаковый scope счётчика и списка по клику. [FQ-06/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/01_SQ-01_home-queue-scope/00_thread.md) |
| Entries last 7 days | Сегодня + предыдущие 6 дней; выбранная область главной. [FQ-06/SQ-03](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/03_SQ-03_period-counter-scope/00_thread.md) |
| Entries last 30 days | Сегодня + предыдущие 29 дней; выбранная область главной |
| Entries with assets | Has assets AND Event date в последних 30 днях; выбранная область главной |

**QRY-07 [Д].** Клик по показателю открывает выборку, совпадающую с областью подсчёта. Месяц Calendar не меняет all-time облако или rolling periods статистики. **[Д, 18.10]** Фильтр по периоду включает интервальную Entry, если хотя бы часть её EventTimeRange пересекается с выбранным периодом; не требуется попадание начала или всего интервала внутрь фильтра. Например, поездка 1–10 июля видна при фильтре 5–7 июля. Одна Entry показывается один раз, независимо от количества пересекающихся дней. Это общее правило date filter; выбор календаря и связанные выборки используют ту же semantics при неизменном lifecycle scope. [FQ-05 — пересечение периодов](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/00_thread.md). Точные границы/mixed precision/timezone остаются FQ-05; [timezone rolling days](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/01_SQ-01_rolling-day-timezone/00_thread.md) принята: используется настройка пользователя, смена по предложению только после подтверждения. Модель review items и scope прочих агрегатов остаются FQ-06; lifecycle перечисленных Home counters согласован в таблице.

**[Д, 18.10.2026]** «Сегодня» и границы календарных rolling days Home определяются по сохранённому часовому поясу из настроек пользователя. При первоначальной настройке предлагается пояс устройства. Если обнаружено отличие пояса устройства от сохранённого пользовательского, приложение предлагает сменить настройку и применяет изменение только после подтверждения. Смена настройки может изменить текущее «сегодня» и период статистики, но не переписывает даты/время/timezone сохранённых событий и не переносит их между днями Calendar. [Обсуждение FQ-05/SQ-01](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/01_SQ-01_rolling-day-timezone/00_thread.md). [Основное отображение времени события](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/02_SQ-02_event-time-display/00_thread.md) принято: местные дата/время и сохранённая зона события, default из пользовательских настроек. Пересчёт в пользовательскую зону не является вторым независимо редактируемым временем; необходимость отдельного UI не утверждена. [Группирование по дням Calendar](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/03_SQ-03_calendar-event-date/00_thread.md) принято: местные даты события, одинаковая семантика индикатора и списка по выбранному дню/диапазону. Смена пользовательской timezone не переносит старые события между днями.

## 9. AI Routines, Runs и Proposals

### 9.1. Routine и запуск

**AI-01 [Д].** System routine immutable; пользователь может Duplicate/Copy и редактировать свою копию. Минимум user routine: name, description, prompt/instructions, scope/eligibility, application policy. Точная модель/versioning routine и form ещё открыты.

**AI-02 [Д].** Selection scope (single Entry / current filtered set / all Entries) отличается от eligibility внутри routine. Filtered batch — результат текущего filter expression, дополнительно ограниченный eligibility. Draft Entries skip, без ожидания автокоммита. Отдельный запуск требует успешного Save; failed/отменённый Save не запускает AI.

**[Д, 18.10.2026]** Продолжение и полный повтор конкретного batch используют исходный список Entry IDs этого запуска. Состав не пересчитывается заново по изменившемуся filter: новые совпадения автоматически не добавляются. Обработка актуальной выборки Browser запускается отдельным новым заданием. Обычные eligibility/Draft/lifecycle/ownership checks сохраняются; исходный список IDs не разрешает принудительно обрабатывать недоступную Entry. Этот выбор фиксирует состав записей, но не замораживает автоматически версии их content или routine. **История:** [FQ-07/SQ-05](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/05_SQ-05_batch-selection-snapshot/00_thread.md).

**[Д, 18.10.2026]** При новом явном пользовательском продолжении или полном повторе обработки существующих Entry берётся актуальная committed Revision каждой допущенной к обработке записи при фиксации input нового Run. Состав Entry IDs остаётся исходным. Несохранённый WorkingDraft не используется: действуют прежние Draft skip/Save guards. После фиксации input конкретного Run он не переключается на следующую Revision; технический retry той же операции сохраняет исходный input. Изменения Current после фиксации input обрабатываются прежними freshness/base/conflict checks. **История:** [FQ-07/SQ-06](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/06_SQ-06_repeat-entry-version/00_thread.md). Выбор routineVersion при повторе и точная граница input capture требуют отдельной конкретизации.

**AI-03 [Д].** Run связан с routineId/routineVersion/entryId/baseRevisionId или input Revision/result/status. Already processed skip может применяться к той же routineVersion и Revision независимо от accepted/rejected outcome proposal. Явный Force rerun доступен; новая Revision или routineVersion допускает обычный запуск.

**[Д, 18.10.2026]** Достоверно failed AI Run без успешного результата не считается успешно already processed. Обычный повтор той же routineVersion/input Revision разрешён даже без изменения записи; обычный batch не пропускает запись только из-за такого failure. Неуспешный Run остаётся в истории. Для успешно выполненной обработки прежние already-processed правила сохраняются независимо от принятия/отклонения proposal; сознательный повтор успешной обработки использует Force rerun. Это правило не разрешает слепой повтор при неизвестном исходе и не меняет пользовательскую политику платных автоматических AI retries. **История:** [FQ-07/SQ-02](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/02_SQ-02_failed-run-retry/00_thread.md). Платные автоматические повторы подчиняются [AQ-OPS-002](04-open-questions.threads/37_AQ-OPS-002_safe-retries/00_thread.md); eligibility сама по себе не включает автоматический платный вызов.

**AI-04 [Д/Б].** Результаты показывают processed/skipped/errors и time/duration; trace включает реально использованные model/provider, instructions/version, input references, validation, outputs, proposals, resolutions и созданные revisions. Failed/rejected/non-mutating run также доступен, даже без Revision.

**AI-05 [Б].** Effective model: run override → routine preference → global user preference → system default. Provider следует модели. Silent fallback на другую модель/provider запрещён.

**AI-06 [Б].** Jobs queued/running/done/failed с отменой. Закрытие страницы не отменяет durable job. Lease и freshness проверяются перед изменением данных. Read-only analysis не требует mutation lease, но правило Draft eligibility не отменяет.

**[Д, 18.10.2026]** При отмене пакетной AI-обработки сохраняются уже успешно опубликованные результаты: pending proposals и разрешённые routine policy committed изменения. Оставшаяся работа останавливается по общему cancellation contract; отмена не выполняет массовый Undo/Reject уже готовых результатов. Pending proposal не становится применённым от сохранения после отмены. Отменённый job не получает право позднего commit; история batch различает завершённую и отменённую/неисполненную части. **История:** [FQ-07/SQ-03](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/03_SQ-03_batch-cancel-results/00_thread.md). **[Д, 18.10.2026]** После подтверждённой отмены пользователь может обычным повтором обработать отменённую/необработанную часть без успешного результата. Для того же выбранного набора и неизменных routineVersion/input Revision уже успешно обработанная часть пропускается; отмена без результата сама по себе не означает already processed. Сознательный полный повтор выбранного набора, включая уже успешную часть, доступен отдельным явным действием Force rerun. Общие eligibility/Draft/ownership checks сохраняются; прежняя queued/running работа не дублируется, неизвестный исход сначала требует reconciliation. История предыдущих запусков сохраняется. [История SQ-04](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/04_SQ-04_interrupted-batch-retry/00_thread.md).

### 9.2. Proposal и применение

**AI-07 [Б].** Изменения существующего текста и неоднозначных metadata оформляются persistent proposal. Base, актуальный Current, предлагаемые изменения и provenance позволяют проверить результат. Stale/conflicting proposal не применяется быстрым Apply без разрешения конфликта.

**AI-08 [Б].** Detailed review использует Base / editable Result / Proposal; при конфликте можно оставить Current, взять Proposal или вручную отредактировать Result. Перед Apply заново проверяются ownership/base compatibility; подтверждённый Result создаёт одну новую committed Revision.

**AI-12 [Д, 18.10.2026].** Подробный review использует три панели: исходник Base — сохранённое состояние, на котором работал AI, только чтение; Result — редактируемый будущий итог; Proposal — исходное предложение AI, только чтение. В Result и Proposal подсвечиваются изменения относительно Base. Если пользователь принимает только часть предложения и подтверждает итоговый Result, proposal получает понятный статус «Принято частично» и закрывается целиком как разобранный. Создаётся одна committed Revision с подтверждённым Result, без дополнительного Save. Исходный Proposal и итоговый Result/Revision сохраняются в AI history; непринятые части не остаются pending и автоматически не превращаются в новые proposals. Причина внимания этого proposal снимается, остальные причины Entry сохраняются. **История:** [FQ-07 — частичный Apply](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/00_thread.md). **[Д, 18.10.2026]** Незавершённый Result подробного AI review автоматически сохраняется как черновик разбора и восстанавливается после выхода, reload и следующего сеанса — по тому же принципу, что Draft записи. Пока Apply не подтверждён, исходный proposal остаётся pending, Current Entry и committed History не меняются. При возвращении ручные правки Result сохраняются; если Current изменился, выполняется обычная проверка base/current и разрешение conflicts без silent overwrite. Черновик разбора не подменяет существующий WorkingDraft ручного редактирования. [История SQ-01](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/01_SQ-01_review-draft-resume/00_thread.md).

**AI-09 [Д].** Accepted/rejected proposal не исчезает из history. Accepted перестаёт быть open, сохраняет provenance и может ссылаться на Revision. Reject не равен «run никогда не выполнялся» и не отменяет already processed semantics.

**AI-10 [Б].** Информационный результат остаётся AIResult и не превращается сам в body Entry. AI не удаляет user-added tags автоматически. Uncertainty не заменяется выдуманным фактом.

**AI-11 [Д, 18.10.2026].** Первая normalized Entry может создаваться автоматически из сохранённого raw с явной uncertainty; existing tags могут добавляться автоматически при высокой уверенности, если это разрешено routine policy. Изменение existing Entry создаёт новую committed Revision с trace routine/input/result; первая обработка создаёт первую committed Revision. Existing Entries с Draft пропускаются, ручной Draft AI не переписывает. Изменения текста existing Entry и создание новых тегов по умолчанию остаются proposals. Конкретные confidence thresholds не фиксируются. [Решение FQ-01](04-open-questions.threads/04_PQ-004_raw-revisions-ux/01_FQ-01_revision-commit-actions/00_thread.md). Batch launch не разрешает массовое бесконтрольное применение; partial review и исход «Принято частично» согласованы в AI-08/12; прочие аспекты FQ-07 остаются открытыми.

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
| SYS-AC-08 | Оставить chips при отсутствующих hashtags → Save дважды | Связи остаются; недостающие hashtags добавлены в конце одной строкой через пробел после пустой строки. Имеющиеся mentions на прежних местах, повторов нет; пустой body получает только строку hashtags |
| SYS-AC-09 | Merge / Delete Tag → открыть старую Revision | Snapshot не переписан; merge разрешает redirect и не создаёт новых content Revision, не меняет физически Draft, дедуплицирует счётчики; delete сохраняет historical tag/relations |
| SYS-AC-10 | Asset permanent delete → читать history | Bytes и preview отсутствуют, tombstone/placeholder доступны, Restore не обещается |
| SYS-AC-11 | Archive Entry с Draft | Lifecycle/audit изменены без content Revision, Draft доступен в архиве |
| SYS-AC-12 | Batch содержит Draft и уже обработанные Revision | Draft skip; already processed определяется routineVersion/input Revision; Force rerun доступен |
| SYS-AC-13 | Reject proposal → повтор обычного batch | Reject не стирает run; правило already processed продолжает работать |
| SYS-AC-14 | Current изменился до Apply | Stale Result не перезаписывает новый Current; нужен conflict/review |
| SYS-AC-15 | Клик Home counter / фильтр Tag | Выборка и count совпадают по области и текущему Draft-state, без дублей |
| SYS-AC-16 | Date-only, optional end, timezone | Не появляется фиктивное midnight; точность/timezone сохраняются после Save/reload |
| SYS-AC-17 | Отключён AI или Calendar | Базовые доступные чтение/редактирование продолжают работать |
| SYS-AC-18 | Разрешённый auto-apply existing tags / первая normalization raw | Сохранены raw/trace; создана новая/первая committed Revision; existing Entry с Draft пропущена; произвольные text mutations не auto-apply |
| SYS-AC-19 | Commit произошёл, ответ потерян; связь восстановлена | Автопроверка возвращает ту же Revision; при незавершённой операции retry с тем же ID/snapshot, без дубликата и обхода conflict/ownership checks |
| SYS-AC-20 | Save выполняется / исход неизвестен / достоверный отказ | Editor и повторный Save заблокированы во время операции; чтение/копирование доступны; success возвращает saved state, definitive failure сохраняет Draft и разрешает исправление без обхода lease/conflict |
| SYS-AC-21 | Снять chip при наличии #name / #alias и Save дважды | В тексте #_name / #_alias без потери слова и удвоения underscore; текстовый поиск находит маркер, Tag filter не создаёт связь; добавление chip обратно до первого Save отменяет пометку снятия |
| SYS-AC-22 | Есть тег Спорт / alias Вело; Create или Rename другого тега в спорт / ВЕЛО; lookup СПОРТ / вело | Дубликат отклоняется с указанием владельца обозначения; lookup находит существующий canonical tag, отображение сохраняет выбранное написание |
| SYS-AC-23 | Удалить тег Спорт с alias Вело; попробовать Create / Rename / добавить alias спорт или ВЕЛО другому тегу | Дубликат отклонён; показан удалённый владелец и предложен явный Restore того же tagId; сам ввод не восстанавливает тег и не создаёт новые links |
| SYS-AC-24 | Прикрепить файл, получить uploading/failed, уйти и открыть Draft | Save недоступен до готовности/явного снятия вложения; текст, готовые связи и pending upload IDs/имена/статусы восстановлены; загруженный original сохранён. При невозможности возобновить неполученные bytes показан повторный выбор файла; pending intent не исчезает |
| SYS-AC-25 | Изменить текст, вернуть исходный вариант, manual Save и retry | При совпадении всего content возвращается прежняя Revision, Draft завершён, History/committedUpdatedAt не меняются. Изменение текста на один пробел или timezone требует новой Revision; stale base не обходится веткой NO_CHANGE |
| SYS-AC-26 | Снять связь / Discard добавлений Draft: единственный потребитель либо несколько | При единственной связи предложен soft delete с явным выбором; при отказе Asset остаётся в Library. При других потребителях только unlink; история одной Entry не умножает число потребителей. Asset, остающийся в восстановленной Current, не предлагается удалить из-за Discard |
| SYS-AC-27 | Active / Archived Entry с Draft → Trash → Restore | В обоих случаях ACTIVE; тот же entryId, Current, history и Draft. Новая content Revision не создаётся; прежний Archived lifecycle не восстанавливается |
| SYS-AC-28 | Entry 1–10 июля; фильтр 5–7 июля | Entry включена один раз по overlap; список/связанный count используют одинаковый predicate и lifecycle scope |
| SYS-AC-29 | Править Draft старой Entry при Updated desc; затем autosave тех же bytes и Discard/NO_CHANGE | Содержательная правка меняет позицию по Draft.updatedAt; служебная синхронизация — нет. Без Draft сортировка использует прежний committedUpdatedAt; committed metadata/History от autosave не меняются |

## 13. Этапы реализации

Сохранено разделение UI-0.5; это последовательность возможностей, не оценка сроков.

| Этап | Основной результат | Что требуется согласовать перед реализацией |
|---|---|---|
| E0 | Account/storage access, files-only чтение существующих Entries | Минимальные canonical read contracts |
| E1 | Поиск, filters, sorting, presets | Date semantics, области выборок, query contract; стратегия index при необходимости |
| E2 | Редактирование, durable Draft, Save, history/Compare/Restore | Commit protocol, concurrency, schemas/migrations, FQ-03; ручные Save/Restore уже определены |
| E3 | Каталоги Tags/Types, merge/delete, работа с Assets | Merge через redirect уже определён; остаются collision policy, catalog concurrency, deletion/references |
| E4 | Routines/runs, proposals/review, model settings | Eligibility/run identity, application policy, cancellation/retry, FQ-07 |
| Дополнительные UX и интеграции | Home, web-create, полный Assets UI, Calendar adapters | Очерёдность поставки и adapter-specific contracts |

Если функция подключена раньше этапа каталога, минимальный полный сценарий уже должен работать: например Add tag без выбора/создания или Save без durable Draft недопустимы. Каталоги и UI могут поставляться постепенно, целостность данных не откладывается.

## 14. Открытые системные вопросы

**FQ-01 решён (18.10.2026):** [канонический подтред PQ-004](04-open-questions.threads/04_PQ-004_raw-revisions-ux/01_FQ-01_revision-commit-actions/00_thread.md). Save / Apply / Restore самостоятельно создают Revision; сохранены два исключения автоматического AI commit (§9.2). Согласованный порядок продолжается: merge тегов → протокол надёжного сохранения.

**FQ-02 решён (18.10.2026):** [merge тегов](AI-Diary-Functional-Spec-v0.1.threads/01_FQ-02_tag-merge/00_thread.md) — redirect в каталоге, без новых content Revision и переписывания Draft/snapshots.

**FQ-03 обсуждается:** [надёжное сохранение](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/00_thread.md). Автоматическая проверка исхода и безопасный retry одной операции согласованы 18.10. Для первой версии выбрана блокировка редактирования и повторного Save до определения исхода (STO-08). Подготовлен [конкретный технический проект](08-save-recovery-design.md), но protocol не объявлен утверждённым: Drive adapter spike ещё не выполнен. [SQ-01](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md) решён: ожидание всех вложений и их сохранение в Draft; [SQ-02 — manual Save без изменения content](AI-Diary-Functional-Spec-v0.1.threads/02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md) также решён: NO_CHANGE без новой Revision, с durable завершением Draft.

| ID | Что нужно решить | Почему это влияет на реализацию |
|---|---|---|
| FQ-01 — РЕШЕНО | Источники committed Revision | Save/Apply/Restore и два узких AI auto-apply случая согласованы 18.10; история в FQ-01 thread |
| FQ-02 — РЕШЕНО | Merge current relations при immutable snapshot | Canonical redirect в каталоге, без массовых Revision и переписывания snapshots/Draft; audit операции |
| FQ-03 — ЧАСТИЧНО | Multi-file commit/recovery и canonical location operational state | Автопроверка/retry и временный read-only editor приняты (STO-07/08); нужна техническая проработка физического протокола |
| FQ-04 — ЧАСТИЧНО | Технические правила Unicode/пробелов и грамматики hashtag mentions | Уникальность без учёта регистра, резервирование deleted labels, #_name после unlink и формат suffix приняты; transfer workflow сейчас не включён; [канонический тред](AI-Diary-Functional-Spec-v0.1.threads/03_FQ-04_tag-aliases/00_thread.md) |
| FQ-05 — ЧАСТИЧНО | EventTimeRange serialization, mixed precision/uncertainty, inclusivity/date timezone | [Overlap при фильтрации](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/00_thread.md) принят; [timezone rolling days](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/01_SQ-01_rolling-day-timezone/00_thread.md) принята; [отображение времени события](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/02_SQ-02_event-time-display/00_thread.md) принято; [дата группирования Calendar](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/03_SQ-03_calendar-event-date/00_thread.md) принята; [отсутствующий To](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/04_SQ-04_missing-event-end/00_thread.md) согласован как одиночное событие; [включение последнего дня date-only интервала](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/05_SQ-05_date-only-end-inclusion/00_thread.md) принято; [date-only запись и фильтр по часам](AI-Diary-Functional-Spec-v0.1.threads/05_FQ-05_period-overlap/06_SQ-06_date-only-clock-filter/00_thread.md) согласованы; прочие точные границы и uncertainty требуют проработки |
| FQ-06 — ЧАСТИЧНО | Модель review items, scope прочих агрегатов | [Updated sort учитывает Draft](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/00_thread.md) и [охват очередей Home](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/01_SQ-01_home-queue-scope/00_thread.md) и [Total entries](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/02_SQ-02_total-entries-scope/00_thread.md) и [lifecycle периодных счётчиков](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/03_SQ-03_period-counter-scope/00_thread.md) — приняты; [ошибки AI в Needs attention и scope счётчика](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/04_SQ-04_failed-ai-attention/00_thread.md) согласованы; [ручное снятие причины ошибки](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/05_SQ-05_dismiss-ai-error/00_thread.md) разрешено; [default lifecycle Home Calendar](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/06_SQ-06_home-calendar-scope/00_thread.md) принят; [единая настройка архива для всей главной](AI-Diary-Functional-Spec-v0.1.threads/06_FQ-06_updated-sort/07_SQ-07_archive-visibility-setting/00_thread.md) принята; остальная модель review items и прочие агрегаты открыты |
| FQ-07 — ЧАСТИЧНО | User routine schema/versioning/application policy, failed-run retry vs already processed, partial proposal resolution | [Исход «Принято частично»](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/00_thread.md) принят; [автосохранение незавершённого review](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/01_SQ-01_review-draft-resume/00_thread.md) принято; [обычный повтор после failed Run](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/02_SQ-02_failed-run-retry/00_thread.md) разрешён; [готовые результаты при отмене batch](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/03_SQ-03_batch-cancel-results/00_thread.md) сохраняются; [повтор отменённой части и явный полный rerun](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/04_SQ-04_interrupted-batch-retry/00_thread.md) согласованы; [исходный набор при продолжении/повторе](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/05_SQ-05_batch-selection-snapshot/00_thread.md) принят; [актуальная committed Revision при новом продолжении/повторе](AI-Diary-Functional-Spec-v0.1.threads/07_FQ-07_partial-proposal/06_SQ-06_repeat-entry-version/00_thread.md) выбрана; остальные аспекты открыты. Нельзя смешивать завершённый запуск, успешное применение и возможность retry |
| FQ-08 — ЧАСТИЧНО | Entry permanent delete dependencies, partial uploads, retention/cache cleanup | [Asset после Discard/unlink](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/00_thread.md): условное предложение soft delete; [Restore Entry из Trash](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/01_SQ-01_restore-lifecycle/00_thread.md): всегда ACTIVE; [внешние originals не удаляются](AI-Diary-Functional-Spec-v0.1.threads/04_FQ-08_discard-uploads/02_SQ-02_external-original-delete/00_thread.md). Остальные части FQ-08 открыты |
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
