# AI Diary — продуктовый baseline

**Версия:** draft 0.1  
**Дата:** 2026-09-26  
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

Для MVP current state и history разделяются:

- основной экран **Entry** показывает актуальную запись и действия над ней;
- **History / Revisions** открывается отдельно;
- raw/original остаётся доступным через history, но не обязан постоянно отображаться рядом с текущей записью.

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

Точный storage backend для media пока не является продуктовым решением.

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

Новая версия **не исходит из предположения, что DB обязательно нужна**.

DB может быть оправдана как:

- derived index;
- cache;
- search layer;
- concurrency aid;
- operational projection.

Но появление DB не должно автоматически означать, что переносимые пользовательские files перестали быть meaningful source data.


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

### 12.1 Первый полезный web slice

Первый web slice ориентирован на уже существующие diary entries:

- browse/list или timeline;
- открыть и прочитать entry;
- обычный текстовый поиск;
- фильтр по дате/date range;
- фильтр по tags.

Создание новой записи через web **не является обязательным requirement первых этапов**. Если простая форма create почти не увеличивает сложность, её можно добавить opportunistically, но она не должна задерживать основной read/search flow.

Следующие продуктовые этапы:

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

Минимальный search первого web slice должен позволять находить entries по:

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

Каждый существенный AI run желательно уметь связать с:

- workflow/version;
- prompt/version;
- provider/model;
- input references/snapshot;
- output;
- validation;
- timestamps;
- user acceptance/rejection;
- token/cost metadata при необходимости.

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