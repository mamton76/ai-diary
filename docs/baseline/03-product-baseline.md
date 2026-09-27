# AI Diary — продуктовый baseline

**Версия:** draft 0.1  
**Дата:** 2026-09-27  
**Назначение:** описать, что такое AI Diary и что продукт должен уметь, до выбора новой технической архитектуры.

---

## 1. Определение продукта

AI Diary — это **персональная система памяти**, задача которой — сделать фиксацию и последующее осмысление повседневной жизни значительно проще, чем традиционное ведение структурированного дневника.

Пользователь должен иметь возможность с минимальным усилием сохранить:

- мысль;
- событие;
- воспоминание;
- ссылку;
- голосовую заметку;
- фотографию;
- файл;
- другой фрагмент жизненного контекста.

Система сохраняет исходный материал, превращает его в устойчивые diary entries, добавляет структуру тогда, когда это полезно, и позже помогает пользователю:

- искать;
- перечитывать;
- группировать;
- связывать;
- суммировать;
- анализировать;
- замечать паттерны во времени.

Главный рабочий принцип:

> **Сначала захватить. Структурировать потом.**

AI должен уменьшать объём ручной работы, а не становиться обязательным посредником между пользователем и его собственным дневником.

---

## 2. Проблема, которую решает продукт

Обычный дневник требует дисциплины и специальных усилий:

- нужно помнить, что пора писать;
- нужно выделять время;
- нужно самому структурировать мысли;
- media и ссылки часто остаются в других приложениях;
- старые записи трудно исследовать как единую историю;
- при большом объёме дневника становится трудно видеть долгосрочные темы и связи.

AI Diary должен переносить часть этой нагрузки с пользователя на систему.

Идеальный сценарий выглядит не как «сесть и заполнить дневник», а как:

1. быстро зафиксировать то, что происходит;
2. не потерять исходный материал;
3. позже дать системе помочь привести его в читаемый и связный вид;
4. при необходимости поправить результат;
5. через месяцы и годы иметь возможность исследовать собственную историю.

---

## 3. Основное обещание продукта

AI Diary должен давать пользователю три вещи одновременно:

### 3.1 Минимум трения при capture

Запись должна появляться быстро и без необходимости заранее решить:

- к какой категории она относится;
- какие у неё tags;
- кто в ней упомянут;
- как её назвать;
- как она будет использоваться потом.

### 3.2 Контроль и сохранность

Пользователь должен быть уверен, что:

- исходный материал не исчез;
- AI не переписал его историю молча;
- изменения можно проследить;
- данные можно экспортировать и восстановить;
- система не зависит безвозвратно от одного vendor/backend.

### 3.3 Помощь в осмыслении накопленного материала

С ростом дневника система должна помогать:

- находить записи;
- видеть тематические группы;
- находить повторяющиеся события и темы;
- строить summaries;
- анализировать выбранный период;
- создавать производные narratives/episodes;
- подготавливать материал для ZoomAlboom.

---

## 4. Границы продукта

AI Diary отвечает за:

- capture;
- diary entries;
- временную привязку;
- текст;
- связи с media/assets;
- revisions;
- tags и другую структуру;
- provenance;
- search/navigation;
- AI enrichment;
- анализ истории;
- export/integration.

AI Diary **не равен** ZoomAlboom.

ZoomAlboom может позже использовать записи AI Diary для:

- визуальной композиции;
- spatial navigation;
- интерактивных альбомов;
- narrative presentation.

Хорошая граница между продуктами:

> **AI Diary хранит события, содержание и смысл.**  
> **ZoomAlboom хранит визуальную композицию и навигацию.**

---

## 5. Центральный объект продукта — Entry

Entry — это пользовательски понятная дневниковая запись.

Она должна иметь:

- стабильную идентичность;
- текстовое содержимое;
- содержательную дату или интервал;
- технические timestamps;
- источник capture;
- при необходимости tags;
- связи с assets;
- историю изменений;
- provenance.

Точная JSON/DB/file schema относится к архитектуре.

### 5.0 Stable Entry и versioned state

На продуктовом уровне нужно различать стабильную identity записи и её versioned content.

`Entry` — стабильный контейнер/identity. Для него нужны как минимум:

- stable `id`;
- lifecycle status;
- ссылка на current committed revision;
- технические timestamps создания/обновления.

Versioned состояние, которое должно восстанавливаться вместе с выбранной revision, включает содержимое записи: title, содержательную дату/интервал, text, tags, связанные assets и source/composition references. Точная физическая schema остаётся архитектурным решением.

Для пользовательского lifecycle Entry достаточно трёх состояний:

- `ACTIVE` — обычная запись, участвует в нормальном browse/search/timeline;
- `ARCHIVED` — сохранена, но по умолчанию скрыта из обычного потока; доступна через archive/filter;
- `DELETED` — soft-deleted / trash, исключена из обычных представлений, но сохраняется для recovery policy.

Постоянный `DRAFT`-status для Entry сейчас не нужен: незавершённое ручное редактирование хранится как operational working draft, а непринятый AI output — как Proposal.


### 5.1 Дата записи

Нужно различать:

- когда пользователь что-то **захватил**;
- когда произошло событие, о котором запись;
- когда запись была обработана/изменена.

Например, пользователь может 26 сентября надиктовать воспоминание про поездку 20 сентября. Entry должна логически относиться к 20 сентября.

### 5.2 Запись не обязана иметь точное время

Система должна поддерживать:

- date-only entry;
- точное время;
- временной интервал;
- неопределённое/приблизительное время с явной confidence/review semantics.

---

## 6. Capture как отдельный слой продукта

Capture не должен быть привязан к одному UI или одному ассистенту.

Желаемые источники:

- web;
- Google Calendar;
- Telegram;
- Android/native app;
- raw files/import;
- другие будущие adapters.

### 6.1 Общая capture boundary

Все источники должны сходиться в логически общую модель входа.

Принцип:

```text
external source
   -> normalized capture item
   -> Inbox-to-Entry processing
   -> canonical Entry
```

Это позволяет менять Calendar на Telegram, добавлять native app или импорт, не переписывая сам diary core.

### 6.2 Голосовой capture

Голос должен быть first-class способом записи.

Пользователь должен иметь возможность:

- говорить свободно;
- делать паузы;
- продолжать мысль;
- в конце явно сказать «сохранить»;
- получить одну законченную запись.

Не следует строить продукт на предположении, что конкретный voice assistant всегда умеет надёжно создавать и потом обновлять одно external event.

### 6.3 Calendar inbox

Google Calendar может быть удобным промежуточным capture channel, особенно пока голосовые интерфейсы ассистентов умеют хорошо работать с Calendar.

Но Calendar event — это **сырой вход**, а не дневник.

---

## 7. Сохранение raw и история

Для системы личной памяти особенно важно не уничтожать источник.

### 7.1 Raw preservation

После обработки должен существовать способ восстановить исходный input:

- оригинальный текст;
- исходный event snapshot;
- исходный media file;
- импортированный документ.

### 7.2 Revisions

Значимые изменения должны быть историческими, а не destructive overwrite.

Источники revisions могут включать:

- raw;
- AI cleanup;
- user edit;
- merge;
- synthetic summary;
- импорт/миграцию.

### 7.3 User wins over AI

Если пользователь поправил текст, AI не должен молча вернуть старую AI-версию поверх пользовательской.

При конфликте лучше:

- создать proposal;
- создать новую revision;
- показать conflict;
- попросить review.

### 7.4 UX текущей записи и истории

Для MVP current state остаётся главным содержимым EntryScreen, а History/Revisions доступна прямо под ним как компактная scrollable gallery/timeline revision snippets.

- карточка revision помогает быстро понять, когда и какого типа изменение произошло и что примерно поменялось;
- клик по revision открывает подробное read-only сравнение **предыдущей revision слева** и **выбранной revision справа**;
- raw/original остаётся доступным через history/details, но не обязан постоянно отображаться рядом с текущей записью;
- provenance/metadata изменения показываются отдельно от двух content panels.

### 7.5 Manual editing session и revision boundary

Manual revision создаётся по границе editing session, а не по «размеру» правки:

- session начинается с первой фактической ручной правки;
- autosave внутри session не создаёт revision;
- session завершается явным Save или после 1 часа inactivity;
- одна завершённая session создаёт одну manual revision;
- исправление одной запятой и большая правка подчиняются одному правилу.

Подряд идущие manual revisions могут визуально группироваться в один раскрываемый блок History, но в данных остаются отдельными revisions.

### 7.6 Линейная история и Restore

Revision history для MVP остаётся линейной, без Git-подобных веток.

Restore старой revision не откатывает историю назад и не удаляет более новые изменения. Вместо этого система создаёт новую revision из snapshot выбранной старой версии и сохраняет provenance-ссылку на source revision, например `restoredFromRevisionId`.

Применённая AI mutation существующей entry также всегда создаёт отдельную revision.

### 7.7 Immutable committed revisions

Committed revision — уже зафиксированная часть истории. Для MVP:

- revisions immutable / append-only;
- у committed revision нет lifecycle статусов `pending/accepted/rejected`: эти состояния принадлежат Proposal;
- пользователь не удаляет отдельные revisions вручную;
- Undo/Restore уже применённого изменения создаёт новую revision с нужным snapshot/provenance, а не уничтожает прежнюю;
- Apply proposal, а затем Undo — это два исторических действия и две committed revisions.

Если history со временем станет слишком большой, отдельная future maintenance-механика может делать compaction через synthetic full-state checkpoint и retention policy. Это не часть обычного editing UX и не блокирует MVP. См. [FQ-REVISION-002](06-future-questions.md#fq-revision-002--revision-history-compaction--retention).


---

## 8. Неопределённость и доверие

AI Diary должен быть способен сказать «я не уверен».

Примеры:

- неясная дата;
- два возможных человека с одинаковым именем;
- непонятно, относится ли фото к записи;
- неясно, разбить ли длинную диктовку на две entries;
- модель предполагает emotion, но текст этого явно не подтверждает.

В таких случаях система должна использовать review/confidence/inferred semantics, а не производить уверенный выдуманный факт.

Это важная часть доверия к персональной памяти.

---

## 9. Tags и организация

Tags нужны в первую очередь для:

- поиска;
- навигации;
- группировки;
- построения cluster/episode;
- подготовки дальнейшего анализа.

AI должен:

- сначала пытаться использовать существующие tags;
- не создавать новый tag на каждую мелочь;
- объяснять спорные предложения;
- не удалять пользовательские tags без явного действия;
- уметь работать proposal-only.

На раннем этапе достаточно мягких типов (`person`, `place`, `topic`, `project` и т. п.), без сложной онтологии.

---

## 10. Media / Assets

В долгосрочном продукте entries должны уметь связываться с:

- photos;
- video;
- audio;
- links;
- documents;
- screenshots;
- другими файлами.

Оригиналы должны сохраняться.

Желательно отделять asset identity от конкретной entry, чтобы один asset можно было использовать в нескольких связанных memories/entries.

Asset не обязан означать физическую копию файла внутри AI Diary. Поддерживаются два базовых режима authoritative original: **managed** (original находится под управлением приложения/user-owned storage) и **external** (original остаётся у внешнего provider/source, а AI Diary хранит reference и metadata). Для первого MVP managed media может использовать тот же user-owned Drive/file backend; отдельный object-storage слой не обязателен.

Preview/thumbnail/transcode и другие производные представления не являются authoritative original Asset и могут существовать отдельно как rebuildable derivatives/cache.

### 10.1 Assets и revisions

Asset имеет identity независимо от Entry и может использоваться более чем в одной записи. При этом набор assets является частью versioned состояния Entry: открытие/restore исторической revision должно восстанавливать тот набор asset links, который относился к этой revision.

Поэтому на продуктовом уровне связь нужно мыслить как `EntryRevision ↔ Asset`; `Entry` получает текущий набор assets через current revision. Конкретная join/schema — архитектурная деталь.

### 10.1.1 Asset как общая media identity

Asset не должен быть жёстко owned одной Entry или только AI Diary. Его identity/storage contract должен позволять позднее использовать тот же Asset из ZoomAlboom или другого consumer. Это не означает, что в MVP нужен отдельный Media Library service: достаточно сохранить такую границу модели.

### 10.2 Удаление asset из Entry

В edit mode удаление asset из записи не должно молча означать только unlink или только физическое удаление.

Действие Remove/Delete открывает явный выбор:

- отвязать asset от этой Entry и оставить его в Asset Library;
- удалить asset из системы целиком.

Если asset используется несколькими entries, destructive delete должен явно предупреждать, что затронет все связи. Если asset связан только с текущей Entry, вариант «оставить в библиотеке» должен предупреждать, что asset станет unlinked/orphaned. Это снижает риск незаметно накопить большое количество забытых assets.


---

## 11. Data ownership и переносимость

Для AI Diary это одно из ключевых отличий от обычного SaaS-дневника.

Пользователь должен иметь возможность:

- получить собственные данные;
- прочитать существенную часть данных без приложения;
- экспортировать дневник;
- восстановить систему из canonical data;
- мигрировать на другой storage backend без полной потери смысла.

Отсюда следует принятое продуктовое правило: **user-owned portable files являются canonical source of truth**.

Operational DB, search index, cache и другие ускоряющие/служебные слои допустимы, но должны быть rebuildable из canonical files и не должны содержать единственную копию существенных diary data.

### 11.1 Google Drive

Google Drive рассматривается как первая практическая реализация storage, потому что:

- уже есть file-first данные и workflows;
- это user-owned storage;
- удобно для ручной инспекции;
- хорошо сочетается с Calendar/Google identity;
- не требует немедленно строить отдельное дорогое storage infrastructure.

Но Google Drive не должен быть навсегда зашит в diary domain.

### 11.2 Database

Первый MVP сознательно стартует **без database для diary content**: backend читает canonical Drive/files через отдельный data layer/repository abstraction.

Позже DB/index может быть оправдан как:

- derived index;
- cache;
- search layer;
- concurrency aid;
- operational projection.

Такой слой должен быть rebuildable и не становится source of truth. Canonical diary content и revisions остаются в user-owned storage. Operational state может временно содержать приватные данные только там, где это необходимо для работы продукта; лишние долговременные серверные копии нужно минимизировать.

Отдельный data layer обязателен с самого начала, чтобы добавление index/DB позже не требовало переписывать UI/domain logic.


### 11.3 Версионирование как свойство продукта

AI Diary хранит личную историю, поэтому versioning нельзя считать только внутренней технической деталью.

Нужно различать несколько независимых типов версий:

- **entry revisions** — история значимых изменений содержания записи;
- **format/schema versions** — версия структуры canonical data;
- **prompt/workflow versions** — какая логика и инструкция породила AI output;
- **run/model metadata** — какой provider/model реально использовался;
- при необходимости — версии integration/config.

Для значимых изменений должно быть возможно:

- увидеть, что состояние изменилось;
- понять источник изменения;
- сохранить предыдущую версию;
- восстановить или переиспользовать старое состояние;
- не смешивать пользовательскую правку с AI proposal;
- провести миграцию формата без уничтожения исходной истории.

Точный UX diff/restore можно развивать постепенно, но данные, необходимые для истории и восстановления, должны сохраняться с самого начала.

### 11.4 Синхронизация данных

AI Diary должен восприниматься как **один логический дневник**, даже если к нему обращаются через разные клиенты и интеграции.

Это означает, что synchronization — отдельная продуктовая способность, а не побочный эффект конкретного storage SDK.

В перспективе одни и те же данные могут использовать:

- web;
- Android;
- iOS;
- backend/background workers;
- capture adapters;
- AI workflows;
- пользователь, напрямую работающий с user-owned files.

Основные требования к sync:

1. изменения должны сходиться к согласованному состоянию;
2. повтор операции после сбоя не должен создавать дубликаты;
3. competing edits не должны тихо теряться через last-write-wins;
4. для конфликтов должна сохраняться достаточная revision/provenance history;
5. stable IDs и version/revision tokens либо их эквивалент должны позволять определить, какое состояние редактировалось;
6. derived indexes/cache/DB projection должны быть rebuildable и не подменять canonical data;
7. внешние проекции вроде Google Calendar имеют собственную sync policy и не равны core diary synchronization;
8. если canonical files могут меняться вне backend, такие изменения нужно обнаруживать и reconciliate.

Для первого web/backend MVP принят **online-first** режим. Full offline browsing/editing и conflict-aware offline sync откладываются. Минимально обязательны:

- не терять capture из-за кратковременного отсутствия сети;
- уметь безопасно повторять операции;
- явно показывать failure;
- не уничтожать параллельные пользовательские изменения.

Архитектура не должна необратимо закрывать путь к будущему offline-capable native/mobile client. Конкретный механизм local persistence/autosave/sync определяется отдельно.


### 11.5 Legacy Android

Старое Android/Firebase приложение не является основой новой реализации и не развивается в текущем цикле. Оно остаётся historical prototype/reference: отдельные идеи или domain/UI решения можно переиспользовать, если это действительно полезно, но специальная миграция codebase не планируется.

К native Android возвращаемся позже, когда появится конкретная потребность, в том числе полноценный offline-first client. Уникальных ценных данных в старом Firebase/Room, которые требовали бы отдельной миграции, нет.

---

## 12. Web-клиент

Новый web — полноценный продуктовый интерфейс.

### 12.1 Первый web MVP и следующий slice

Самый первый files-only MVP может быть ещё уже: browse/list существующих entries и открыть/прочитать entry через backend data layer, без database/index и без полноценного search.

Следующий полезный web slice добавляет:

- обычный текстовый поиск;
- фильтр по дате/date range;
- фильтр по tags.

Создание новой записи через web **не является обязательным requirement первых этапов**. Если простая форма create почти не увеличивает сложность, её можно добавить opportunistically.

Далее:

1. editing existing entries + versioning/history;
2. просмотр и редактирование tags;
3. AI processing/actions/workflows.

### 12.2 Mobile web

Телефонный интерфейс может быть проще, но первый базовый сценарий должен позволять:

- открыть дневник;
- найти запись по тексту/дате/tags;
- прочитать запись.

Editing добавляется на следующем этапе вместе с versioning/history. Capture/create может поначалу оставаться во внешних каналах и не является обязательным mobile-web сценарием первого slice.

Сложные debug/admin/bulk/revision comparison функции могут сначала остаться desktop-oriented.

### 12.4 EntryScreen и переиспользуемый EntryPanel

Экран одной записи разделяется на два уровня:

- `EntryScreen` — page/screen shell: navigation, screen-level actions, reusable EntryPanel, текущие Proposals и компактная History/Revisions gallery/timeline;
- `EntryPanel` — переиспользуемое представление **самого состояния записи**.

`EntryPanel` должен использоваться как минимум в обычном view, manual edit и proposal merge/review. Его смысловые области:

- `Title` — отдельно от основного текста;
- `Event time` — содержательная date и опциональные start/end time;
- `Text` — основной текст записи;
- `Assets`;
- `Tags`;
- вторичная read-only system metadata: created/updated timestamps; она видна всегда, но визуально тихо — внизу secondary column на широкой panel и внизу panel на узкой.

Режимы поведения:

- в view mode title/text/event time read-only;
- в edit mode title и text становятся редактируемыми;
- date/start/end получают date/time controls;
- для Tags и Assets в edit mode появляются действия add и remove; Add должен позволять выбрать уже существующую сущность или создать новую (для assets — через Asset Library/new upload-or-link flow, для tags — через существующий catalog/new tag flow);
- Base/Proposal в merge view используют тот же panel read-only, Result — editable.

EntryPanel использует adaptive layout по **собственной доступной ширине**:

- при достаточной ширине Text занимает основную content column, а Assets, Tags и вторичные created/updated metadata показываются в правой secondary column;
- при недостаточной ширине Assets, Tags и secondary metadata переходят под Text в одну вертикальную колонку;
- Title и Event time остаются верхней частью panel;
- точные breakpoint и пропорции колонок определяются на UI/implementation уровне.

Такой container-responsive layout обязателен именно из-за reuse: одна EntryPanel на широком detail screen может иметь правую колонку, а три более узкие панели в `Base | Result | Proposal` автоматически складываются вертикально без отдельной merge-specific структуры.

### 12.5 History gallery, revision comparison, provenance и lineage

`Sources / Lineage` не являются отдельным постоянным блоком основного EntryScreen. Provenance относится к конкретным committed revisions.

Под текущей Entry показывается компактная scrollable History/Revisions gallery/timeline. Revision card/snippet позволяет быстро увидеть тип/время изменения, короткий content preview и компактное summary того, что поменялось.

Выбор revision открывает revision details с read-only comparison:

- слева — **предыдущая revision**;
- справа — **выбранная revision**;
- обе стороны переиспользуют EntryPanel/diff building blocks;
- это отличается от proposal merge `Base | Result | Proposal`, где Result редактируется.

Metadata/provenance отделено от content comparison и не сравнивается как часть diff. Оно может включать raw/source links, previous/base revision, manual/AI/restore/import origin, proposal/workflow/AI run references, timestamps и другие trace данные. Краткие provenance details могут показываться через indicator/tooltip/popover, а полные — через `Подробнее`.

Diff versioned content остаётся лёгким и field-aware:

- Tags и Assets показывают добавления/удаления через `+ / −`; порядок Assets не считается значимым и reorder не является change;
- Text желательно подсвечивать на уровне изменённых фрагментов; точный diff algorithm/visual style выбирается при реализации по читаемости;
- для title и event date/time достаточно явно показать факт/значение изменения без отдельной сложной history model.

Actionable AI state на основном EntryScreen представлен текущими Proposals; полную историческую AI activity не нужно дублировать отдельной секцией рядом с EntryPanel.


### 12.6 AI actions и inline editor assistance

EntryScreen должен давать screen-level AI actions над текущей записью через заметную кнопку/menu `AI ▾`, расположенную рядом с обычными screen actions (например Edit):

- запуск готового workflow;
- `Custom prompt / Ask AI` для разовой инструкции.

Такие Entry workflows работают от committed revision. Если в manual editor есть dirty working draft, используется `Save & Run`: сначала создаётся manual revision, затем именно она становится input/base revision для AI run. Изменяющий workflow дальше создаёт Proposal и не переписывает Entry напрямую.

Отдельно сохраняется кандидатная функция **inline AI editor assistance**: AI-команда над selection/current working draft (например rewrite, shorten, fix, continue). Это может оказаться полезным уже в MVP, но не является blocking requirement. Решение о включении принимается при реализации editor slice с учётом стоимости и необходимости отдельно определить undo/proposal/revision semantics для draft-level AI.

Отдельный постоянный `AI note / annotation` block на EntryScreen не нужен: actionable AI mutation представлена Proposal, применённое изменение — Revision, историческая причина/trace — provenance/AI run details, а non-mutating analysis остаётся workflow result.

### 12.3 UI не владеет бизнес-логикой

Web должен обращаться к backend API, а не становиться единственным местом, где живут правила хранения, revisions, capture и AI.

---

## 13. Backend как product service boundary

Backend нужен, потому что продукт должен жить дольше одного web UI.

Он должен дать общий interface для:

- web;
- будущего Android;
- возможно iOS;
- capture adapters;
- external integrations.

Backend должен быть местом, где концентрируются:

- domain rules;
- storage access;
- revision/conflict semantics;
- auth;
- search/indexing;
- integrations;
- background processing;
- LLM workflows.

Язык и hosting здесь сознательно не фиксируются.

---

## 14. Search и исследование истории

Search не блокирует самый первый files-only MVP. На следующем web slice он должен позволять находить entries по:

- тексту;
- date/date range;
- tags.

Source/status и другие filters можно добавлять позже, если они окажутся полезны.

Позже могут появиться:

- semantic search;
- embedding-based retrieval;
- cross-entry Q&A;
- поиск паттернов;
- тематические clusters;
- people/place exploration.

Search index может быть производным и перестраиваемым.

---

## 15. LLM / AI как отдельная подсистема

LLM subsystem должна быть **перпендикулярна обычной работе дневника**.

Базовый diary flow не должен зависеть от конкретного model provider.

### 15.1 Provider abstraction

Желаемая модель:

```text
AI Workflow
   -> Context Builder
   -> LLM Provider
        -> OpenAI
        -> Gemini
        -> Anthropic
        -> другие
```

Workflow не должен знать Drive paths, а provider не должен знать diary storage internals.

### 15.2 Типы AI-задач

Потенциальные workflows:

- cleanup;
- title suggestion;
- tag suggestion;
- extraction;
- summarization;
- clustering;
- synthetic entry;
- period review;
- пользовательский custom analysis.

### 15.3 Traceability

Каждый существенный AI run должен быть доступен для drill-down из пользовательского Entry/AI activity и связываться с:

- workflow/version;
- prompt/version;
- provider/model;
- input references/snapshot и base/input revision;
- output / AIResult;
- созданными proposals;
- validation;
- timestamps;
- auto-apply / user acceptance / rejection / supersede outcome;
- committed revisions, появившимися в результате применения;
- token/cost metadata при необходимости.

Обычный Entry screen может показывать только актуальные actionable proposals, но пользователь должен иметь возможность открыть полную AI activity и детали конкретного run/result, чтобы понять, что именно происходило с записью.

### 15.4 Prompts

Рабочая модель:

- базовые system contracts принадлежат приложению;
- user instructions/overrides могут быть данными;
- пользователь может со временем создавать собственные workflows;
- prompts версионируются.

### 15.5 Пользовательский контроль

AI automation policy определяется per workflow/type of change, а не одной глобальной настройкой.

Для MVP:

- informational/derived AI output может создаваться автоматически;
- если raw capture сохранён, первая normalized/processed entry может создаваться автоматически; uncertainty должна оставаться явной;
- существующие tags могут auto-apply при высокой уверенности;
- создание новых tags по умолчанию идёт через proposal;
- AI не удаляет user-added tags автоматически;
- изменение существующего content или неоднозначного metadata через AI сначала создаёт **persistent proposal**, даже если workflow запущен пользователем вручную;
- proposal не является revision до Accept/Apply;
- pending proposal хранит target/scope/base state и живёт до Accept/Reject либо supersede;
- если base state изменился, proposal может стать stale/conflicted и не должен silently применяться;
- несколько proposals могут существовать параллельно, если их scopes не конфликтуют;
- точные confidence thresholds и policy для будущих metadata определяются при появлении соответствующего workflow.

Merge/split entries отложены на future stage; bulk AI mutation/delete не являются текущими MVP workflows.

### 15.5.1 Proposal granularity и review UX

Жёсткое правило «один AI run = один proposal» или «одно изменение = один proposal» не вводится.

- один AIResult может содержать один или несколько proposals;
- один proposal может быть простым или комплексным и затрагивать несколько полей/типов данных;
- гранулярность определяется конкретным workflow;
- proposal должен различать способ применения (`USER` / `AUTO`) и собственный lifecycle; эти состояния не переносятся на committed revision.

На Entry screen proposals показываются компактными карточками/snippets:

- бесконфликтный proposal: быстрые `Apply`, `Reject`, `Подробнее`;
- stale/conflicted proposal: `Reject`, `Подробнее`, без быстрого Apply.

`Подробнее` открывает трёхсторонний review:

```text
Base              Result              Proposal
read-only         editable            read-only
```

`Result` всегда показывает реальное будущее состояние после применения. Независимые изменения Current и Proposal могут auto-merge. Конфликт подсвечивается локально на конкретном field/fragment; пользователь может оставить Current, взять Proposal или отредактировать Result вручную. Для complex proposal detailed mode может фактически принять только часть предложенных изменений.

Подтверждение Result создаёт одну новую committed revision. До подтверждения Result остаётся merge draft и в History не попадает.



### 15.6 Выбор LLM model

Пользователь может задавать preferred model на нескольких уровнях. Приоритет:

1. override для конкретной task/run;
2. preferred model workflow;
3. global preferred model пользователя;
4. system default.

Ожидаемый основной сценарий — один global preferred model, который наследуют большинство workflows. Отдельный provider пользователю выбирать не нужно: provider определяется выбранной model.

Если preferred model недоступна, AI Diary не должен тихо переключаться на другую model/provider без явного согласия пользователя. Детали fallback/retry/deprecation относятся к implementation и UX policy.


---

## 16. AI memory / персонализация

Перспективное направление — различать:

- явные user preferences;
- накопленный learned context;
- snapshot контекста, реально использованный конкретным AI run.

Это полезно для того, чтобы AI со временем понимал:

- recurring people/projects;
- привычные tags;
- preferred writing cleanup style;
- rejected suggestions;
- личные patterns.

Но advanced AI memory не должна блокировать первый web/backend MVP.

---

## 17. Calendar timeline как optional projection

Помимо capture, Calendar может быть удобным native timeline viewer.

В таком сценарии:

- diary entries остаются canonical;
- Calendar inbox — optional transport/adapter, а не core dependency;
- timeline projection работает отдельно от capture;
- одна diary entry соответствует одному Calendar event;
- при новой committed revision или другом изменении current state существующий Calendar event обновляется;
- отдельные Calendar events для каждой revision не создаются;
- pending AI proposals не публикуются как current diary state;
- projection может быть удалена и перестроена;
- внешние IDs остаются integration state;
- Calendar manual edits не обязаны становиться diary edits.

Эта функция полезна, но не является обязательной для первого нового web/backend skeleton.

---

## 18. Authentication и user model

Поскольку Drive/Calendar находятся в Google ecosystem, Google — естественный первый login method для MVP. При этом AI Diary использует собственный stable internal user/account ID, а external login identities привязываются к нему отдельно. Google account ID не является единственным внутренним identity, чтобы позже можно было добавить другие способы входа без миграции основной user model.

Конкретный auth service/framework (Firebase Auth, direct OIDC или другой middleware) сейчас не фиксируется и выбирается вместе с backend/hosting.

Необходимо различать:

- кто залогинен в AI Diary;
- какие scopes пользователь дал для Drive;
- какие scopes дал для Calendar;
- где хранятся refresh tokens;
- как пользователь отзывает доступ.


Для доступа к user-owned Google Drive backend действует **от имени пользователя через OAuth**. Service account + shared folder не является основной моделью доступа для multi-user приложения. Пользователь явно предоставляет приложению Google API permissions, а canonical files продолжают принадлежать его Drive.

AI Diary с самого начала считается **multi-user application**: один backend/application может обслуживать нескольких авторизованных пользователей, и у каждого пользователя свой логический дневник и изолированные данные.

User ownership должен быть явным в authenticated backend context и во всём shared operational/server-side state. При этом canonical files в user-owned storage не обязаны содержать дублирующий `ownerId`, если ownership уже задаётся storage/account boundary.

Это не означает social/collaborative модель: sharing между пользователями и сложные ACL остаются вне MVP.

---

## 19. Reliability

Для персональной памяти важнее надёжность и объяснимость, чем сложная «магия».

Система должна стремиться к следующим свойствам:

- не терять уже введённый текст при сетевых сбоях;
- safe retries;
- duplicate resistance;
- видимые failures;
- восстановление из canonical data;
- migration/versioning;
- backup/restore;
- прозрачный AI provenance.

Первый web/backend MVP — online-first; полный offline-first отложен, но защита уже введённого текста от кратковременных сетевых сбоев обязательна.

---

## 20. Privacy

Diary data потенциально очень чувствительны.

Продукт должен по возможности:

- хранить минимум лишних копий;
- давать пользователю понятный контроль;
- не отправлять весь дневник LLM provider без необходимости;
- ясно отделять локальное хранение от external AI processing;
- позволять в будущем выбирать provider/policies.

Privacy-first является сильным направлением и соответствует идее user-owned data.

---

## 21. Sharing

Selective sharing остаётся потенциально полезной **future feature**:

- поделиться конкретной записью;
- family memory;
- trip narrative;
- AI-generated summary;
- ZoomAlboom story.

Для текущего MVP sharing **out of scope** и не должен определять auth/data model. Это не social-network requirement и не collaborative editing. К access/sharing model возвращаемся только при появлении реального near-term use case.

См. [FQ-SHARING-001](06-future-questions.md#fq-sharing-001--selective-sharing).

---

## 22. Предлагаемый функциональный scope новой базовой версии

Это не финальный roadmap, а продуктовый минимум для архитектурного сравнения.

### Обязательно учитывать

- Google login/identity direction;
- Google Drive storage adapter;
- browse/read/create/edit entries;
- adaptive web;
- backend API;
- stable entry identity;
- revisions/history;
- raw/provenance preservation;
- search/filter;
- storage abstraction;
- capture normalization boundary;
- Calendar inbox adapter как минимум на уровне совместимости;
- LLM provider abstraction и extension point;
- traceable AI workflows;
- low-cost deployment.

### Можно отложить

- сложный semantic search;
- advanced AI memory;
- full media processing;
- people/place ontology;
- sharing;
- collaborative editing;
- sophisticated Calendar timeline;
- ZoomAlboom export format;
- native Android migration;
- on-device AI.

---

## 23. Критерии качества продукта

AI Diary должен стремиться быть:

### Быстрым
Capture — секунды, а не ритуал.

### Надёжным
Личная история не должна исчезать из-за сбоя workflow или LLM.

### Прозрачным
Пользователь понимает, что написал он, что предложил AI и откуда взялась derived информация.

### Переносимым
Данные не заперты навечно в одной backend-схеме.

### Расширяемым
Новые capture channels, clients и LLM providers можно добавлять без переписывания всей системы.

### Простым в эксплуатации
Для персонального проекта инфраструктура не должна требовать постоянного DevOps и больших расходов.

---

## 24. Основные non-goals на текущем этапе

Сейчас не требуется заранее проектировать:

- социальную сеть;
- enterprise collaboration;
- сложные ACL между множеством пользователей;
- real-time collaborative editor;
- recommendation feed;
- собственную foundation model;
- тяжёлую microservice architecture;
- отдельную БД только «потому что так принято»;
- сложную ontology engine до появления реальной потребности.

---

## 25. Резюме продуктового baseline

AI Diary — это не просто приложение для написания заметок и не просто AI-чат над историей пользователя.

Это система, которая должна соединить четыре слоя:

```text
1. Capture
   быстро сохранить жизнь как она есть

2. Durable Memory
   сохранить raw, entries, revisions, media и provenance

3. Structure & AI
   помочь организовать и понять накопленное

4. Exploration
   поиск, timeline, patterns, summaries и позже ZoomAlboom
```

При этом пользователь должен сохранять контроль над собственными данными и не зависеть критически ни от одной конкретной модели, UI или storage vendor.