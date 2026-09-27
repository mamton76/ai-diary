# AI Diary — вопросы прекрасного будущего

**Дата создания:** 2026-09-26  
**Назначение:** parking lot для важных вопросов, которые сознательно **не должны блокировать текущий MVP/архитектурный этап**, но которые легко потерять после того, как соответствующий продуктовый вопрос закрыт.

Это не второй список текущих open questions.

- `04-open-questions.md` — то, что нужно решить сейчас или явно принять как assumption перед архитектурой.
- `06-future-questions.md` — то, что мы намеренно отложили и хотим вернуться к этому позже.
- Если future-вопрос становится актуальным, он переносится/промотируется в `04-open-questions.md` с новым ID или дочерним вопросом и получает обычный discussion thread.

---

## FQ-OFFLINE-001 — Full offline editing и синхронизация версий

**Статус:** PARKED / FUTURE  
**Происхождение:** [PQ-002 — full offline-first](04-open-questions.threads/03_PQ-002_offline-first/00_thread.md)  
**Триггер для возвращения:** когда offline editing становится реальной целью web/native клиента, особенно при возвращении к Android/native app.

### Что уже решено сейчас

Для первого web/backend MVP принят **online-first** подход. Полный offline browsing/editing и conflict-aware offline sync отложены.

При этом уже сейчас обязательны:

- не терять введённый текст/capture при кратковременном сетевом сбое;
- safe retry;
- видимые failures;
- stable IDs и version/revision tokens либо эквивалент;
- отсутствие silent last-write-wins для значимых diary data.

### Почему offline становится отдельной большой задачей

Проблема не только в том, чтобы «положить копию данных на устройство». Как только пользователь может менять дневник offline, появляются **несколько независимых состояний одной записи**, которые позже нужно корректно свести.

Пример:

1. телефон ушёл offline на revision 12;
2. на ноутбуке запись изменилась до revision 13;
3. на телефоне пользователь независимо отредактировал старую revision 12;
4. телефон вернулся online.

Система должна понять, что изменения расходятся от общего предка, и не может просто считать последнее пришедшее состояние правильным.

### Вопросы, к которым нужно вернуться

- Какой локальный durable store используется offline?
- Как отличать **working draft/autosave** от committed revision?
- Как представлять локальные изменения: snapshot, operation log/change set или комбинация?
- Как клиент показывает, на базе какой revision/version он редактировал запись?
- Как backend определяет concurrent edits?
- Нужны ли только optimistic version tokens или более богатая causal/version model?
- Какие изменения можно merge автоматически, а какие требуют conflict UI?
- Как синхронизировать content и metadata/tags, если они менялись параллельно?
- Что делать, если во время offline manual edit AI или другой клиент создал новую revision?
- Как обрабатывать delete/tombstone и restore?
- Как гарантировать idempotent retry и duplicate prevention после долгого offline периода?
- Как reconciliate внешние изменения canonical files/Drive с offline client state?
- Как пересобирать derived indexes/cache после серии offline изменений?
- Нужно ли хранить sync journal/provenance так, чтобы пользователь мог понять, почему возник конфликт?

### Рабочая мысль на будущее

Существующая линейная revision history может остаться пользовательской историей, даже если внутри sync-механизма временно существует несколько конкурирующих состояний. После разрешения конфликта результат можно фиксировать новой revision поверх текущей истории, сохраняя provenance исходных версий.

Это пока **не решение архитектуры**, а полезная гипотеза для будущего обсуждения.

---


## FQ-ASSET-001 — Asset/media versioning

**Статус:** PARKED / FUTURE  
**Происхождение:** [AQ-DATA-007 — manual canonical edits](04-open-questions.threads/24_AQ-DATA-007_manual-canonical-edits/00_thread.md)  
**Триггер для возвращения:** когда появится реальный сценарий, где нужно сохранять несколько исторических версий одного media Asset — например original photo и enhanced/restored/re-encoded variant — и различать их в старых и новых diary/ZoomAlboom references.

### Что сознательно не решаем сейчас

В текущем MVP Asset имеет stable identity и authoritative original, но отдельная история версий самого media Asset не проектируется. AQ-DATA-007 не должен зависеть от Asset versioning.

### Что потребуется решить позже

- является ли улучшенное media новой Asset identity или новой version существующего Asset;
- должны ли старые Entry revisions продолжать указывать на старую media version;
- как хранить provenance преобразования original -> enhanced/restored/transcoded;
- как versioning взаимодействует с shared media library и ZoomAlboom;
- retention/cleanup старых media versions;
- как не дублировать большие originals без необходимости.

До появления такого use case не усложнять текущую Asset/storage модель.

## Как добавлять сюда новые вопросы

Для каждого future-вопроса достаточно:

- устойчивого ID `FQ-<AREA>-NNN`;
- причины, почему он отложен;
- ссылки на исходное решение/тред;
- списка того, что потребуется решить;
- понятного trigger-а, когда его пора вернуть в активную работу.

Не создавать discussion thread, пока вопрос действительно не возвращён в активное обсуждение.

## FQ-SEARCH-001 — Advanced search / semantic exploration

**Статус:** PARKED / FUTURE  
**Происхождение:** PQ-003 / product baseline search scope  
**Триггер для возвращения:** когда обычного text/date/tag search перестанет хватать или появятся cross-entry AI сценарии.

### Что уже решено сейчас

Первый web slice использует обычный поиск по:

- тексту;
- date/date range;
- tags.

### Что сознательно отложено

Позже можно вернуться к:

- semantic search;
- embedding-based retrieval;
- cross-entry Q&A;
- поиску паттернов;
- тематическим clusters;
- people/place exploration;
- дополнительным source/status filters, если они окажутся полезны.

Главный будущий вопрос — какой из этих сценариев реально нужен пользователю и какой retrieval/index слой оправдан под него. Не тянуть vector/semantic infrastructure в MVP только ради будущей возможности.

---

## FQ-REVISION-001 — Advanced History / Revisions UX

**Статус:** PARKED / FUTURE  
**Происхождение:** PQ-004 / PQ-011 — revision history UX  
**Триггер для возвращения:** когда базовой revision gallery и Previous-vs-Selected details станет недостаточно для длинной или сложной истории.

### Что уже решено сейчас

Для MVP:

- Current Entry остаётся главным состоянием EntryScreen;
- под ней показывается компактная scrollable History/Revisions gallery/timeline со snippet-карточками revisions;
- карточки помогают увидеть тип/время и характер изменения;
- клик открывает read-only comparison предыдущей и выбранной revision;
- provenance/metadata показывается отдельно от content comparison;
- restore создаёт новую revision поверх текущей истории;
- revision history остаётся линейной.

### Что сознательно оставлено на потом

- сравнение произвольных двух revisions (`Compare with…`), а не только previous vs selected;
- более богатая diff-навигация и visual timeline для очень длинной истории;
- фильтры/grouping по типам revision beyond базового presentation grouping;
- специализированный desktop history workspace;
- отдельная mobile presentation, если обычной adaptive gallery/details станет недостаточно;
- дополнительные способы навигации по raw/source/provenance graph.

Это presentation layer: данные revisions должны позволять улучшать UI позже без миграции истории.

---

## FQ-REVISION-002 — Revision history compaction / retention

**Статус:** PARKED / FUTURE  
**Происхождение:** [PQ-004 — raw/revisions UX](04-open-questions.threads/04_PQ-004_raw-revisions-ux/00_thread.md)  
**Триггер для возвращения:** когда объём revision history начнёт заметно влиять на storage, performance или удобство обслуживания.

### Что уже решено сейчас

Для MVP committed revisions остаются immutable / append-only. Пользователь не удаляет отдельные revisions; Restore и Undo создают новую revision поверх линейной истории.

### Будущая идея

Если история станет слишком большой, compaction можно выполнять отдельной maintenance-операцией:

- создать synthetic checkpoint revision, содержащую полный актуальный state;
- после успешного checkpoint по retention policy архивировать или удалять часть старых промежуточных revisions;
- не превращать compaction в обычный пользовательский rollback/delete;
- сохранить достаточный provenance и гарантии восстановления.

### Что потребуется решить позже

- какие revisions нельзя удалять никогда: raw/original, restore sources, migration checkpoints и т. п.;
- retention policy: по возрасту, количеству, размеру или типу revision;
- что происходит со ссылками `restoredFromRevisionId`, AI run/proposal provenance и другими references на compacted revisions;
- нужно ли архивировать старые revisions отдельно вместо физического удаления;
- как compaction влияет на assets, связанные с историческими revisions;
- как валидировать checkpoint до удаления/архивации старой истории.

Это future maintenance requirement и не должно усложнять текущий MVP.

---

## FQ-ENTRY-001 — Merge / split entries

**Статус:** PARKED / FUTURE  
**Происхождение:** PQ-005 — AI automation policy  
**Триггер для возвращения:** когда появится реальный пользовательский сценарий объединения нескольких entries или разделения одной существующей entry на несколько.

### Почему отложено

Для текущего MVP merge/split не нужен и только усложняет semantics identity, revisions, provenance и links.

### Что потребуется решить позже

- сохраняется ли identity одной из entries при merge или создаётся новая;
- как хранить provenance исходных entries;
- что происходит с revisions и raw sources;
- как ведут себя tags, links и timeline;
- split создаёт новые entry IDs или производные identities;
- нужен ли proposal/preview перед применением;
- как представить undo/restore без ветвления пользовательской revision history.

До появления такого use case не учитывать merge/split при проектировании текущей AI automation policy.


---

## FQ-SHARING-001 — Selective sharing

**Статус:** PARKED / FUTURE  
**Происхождение:** [PQ-007 — Sharing входит в обозримый MVP?](04-open-questions.threads/08_PQ-007_sharing-mvp/00_thread.md)  
**Триггер для возвращения:** когда selective sharing станет реальным near-term use case, например появится задача делиться конкретной entry, family memory, trip narrative, AI-generated summary или ZoomAlboom story с близкими людьми.

### Что уже решено сейчас

Sharing не входит в обозримый MVP и не должен сейчас определять auth/data model.

Речь идёт не о социальной сети и не о collaborative editing, а о selective sharing отдельных memory artifacts.

### Что потребуется решить позже

- что именно можно шарить: entry, summary, collection/story;
- read-only ли sharing или появляются comments/collaboration;
- кому выдаётся доступ и как он отзывается;
- нужен ли account у получателя или достаточно share link;
- какие privacy defaults и expiration нужны;
- как sharing взаимодействует с user-owned canonical data;
- что происходит с revisions/proposals после публикации;
- нужен ли отдельный export/publication snapshot;
- как ZoomAlboom stories используют ту же access model или отдельную.

До появления такого use case не усложнять текущую auth/data model ради sharing.




**Статус:** PARKED / FUTURE  
**Происхождение:** [PQ-009 — Calendar inbox role](04-open-questions.threads/09_PQ-009_calendar-inbox-role/00_thread.md)  
**Триггер для возвращения:** когда Calendar timeline projection станет реальной пользовательской feature и понадобится решить, как в ней отражать историю изменений entry.

### Что уже есть

Текущий projection workflow использует one-entry -> one-calendar-event mapping и обновляет существующий Calendar event, когда изменилось проецируемое состояние entry. Calendar остаётся derived/rebuildable view, diary files — source of truth.

### Что нужно решить позже

- Calendar event должен показывать только current committed state или ещё и revision history;
- если revision history нужна, показывать её отдельными events, ссылкой/summary внутри основного event или отдельным audit/debug view;
- нужно ли показывать current revision id / updatedAt / provenance;
- что происходит с Calendar event при restore старой revision;
- должны ли pending AI proposals вообще быть видимы в Calendar;
- как избежать превращения life timeline в timeline редакторских действий.

Рабочая гипотеза: обычный Calendar timeline показывает одно событие на entry и обновляет его до current committed state; полноценную revision history туда по умолчанию не публиковать.
