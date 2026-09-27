# PQ-011 — Как устроен Entry detail/edit и переиспользуемый EntryPanel?

**Источник:** [04-open-questions.md / PQ-011](../../04-open-questions.md#pq-011--как-устроен-entry-detailedit-и-переиспользуемый-entrypanel)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Как должен выглядеть основной экран одной Entry и какое представление состояния записи нужно сделать переиспользуемым между обычным просмотром, ручным редактированием и proposal merge/review?

## Варианты

Точный layout пока не выбираем. Основная развилка — что относится к переиспользуемому Entry content component, а что должно жить только в surrounding EntryScreen.

## Контекст

В PQ-005 уже согласован detailed proposal review `Base | Result | Proposal`. Чтобы этот экран не имел отдельное несовместимое представление записи, Base/Result/Proposal должны использовать тот же content component, что обычный Entry view/edit.

Это голосовой тред: сохраняются смысловые сводки, а не стенограмма.

## Обсуждение

### Сводка 1 — EntryScreen и EntryPanel разделяются

Согласована двухуровневая модель:

- `EntryScreen` — оболочка страницы/экрана;
- `EntryPanel` — переиспользуемое представление одного состояния Entry.

`EntryPanel` должен использоваться как минимум в:

- обычном просмотре Entry;
- manual edit;
- трёхпанельном proposal review/merge: Base и Proposal read-only, Result editable.

В `EntryPanel` не должны встраиваться screen-level сущности, которые не описывают само состояние записи: Proposals list, History/Revisions, Sources/Lineage, полная AI activity/details, navigation и общие screen actions.


### Сводка 2 — состав EntryPanel

На текущем этапе согласованы смысловые области:

- **Title** — отдельное поле, не часть основного текста;
- **Event time** — содержательная date и опциональные start/end time;
- **Text** — основной текст записи;
- **Assets**;
- **Tags**;
- вторичная system metadata — created/updated timestamps.

Важно различать содержательное время события и технические timestamps самой записи.


### Сводка 3 — view/edit behaviour

В view mode панель показывает текущее состояние read-only.

В edit mode:

- Title становится редактируемым;
- Text становится редактируемым;
- date/start/end получают date/time controls;
- у Tags появляются add/remove actions;
- у Assets появляются add/remove actions.

Расположение секций (`Assets` до/после `Tags`, side column vs vertical layout) пока сознательно не фиксируется; сначала фиксируем состав и одинаковую semantics панели.


### Сводка 4 — Assets: unlink vs delete

Удаление asset из Entry требует явного выбора, а не тихого unlink.

В edit mode Remove/Delete asset открывает modal:

- отвязать asset от текущей Entry и оставить в Asset Library;
- удалить asset из системы целиком.

Если asset используется несколькими entries, destructive delete должен предупредить, что затронет все связанные записи. Если asset связан только с текущей Entry и пользователь выбирает unlink, UI должен предупредить, что asset останется unlinked/orphaned.

Причина: не плодить незаметно зависшие assets и при этом не смешивать «убрать из этой записи» с «удалить объект вообще».


### Сводка 5 — связь с versioned Entry state

Ранее в этом же обсуждении принято, что stable Entry является контейнером identity/lifecycle/currentRevision, а versioned content относится к EntryRevision. В частности, title, event time, text, tags, assets и source/composition state должны восстанавливаться вместе с revision.

Для assets на продуктовом уровне принята связь `EntryRevision ↔ Asset`: текущая Entry получает текущий набор assets через current revision. Это позволяет Restore вернуть не только text, но и соответствующий исторический asset set.


### Сводка 6 — Entry lifecycle и committed revision semantics

В ходе разбора того, что именно отображает/редактирует EntryPanel, уточнены роли Entry, Revision и Proposal:

- `Entry` — стабильный контейнер identity/lifecycle/currentRevision;
- пользовательский lifecycle Entry: `ACTIVE`, `ARCHIVED`, `DELETED`; постоянный `DRAFT` не нужен;
- `ACTIVE` участвует в обычном browse/search/timeline, `ARCHIVED` по умолчанию скрыт из основного потока, `DELETED` — soft-delete/trash;
- versioned content (title, event time, text, tags, assets и source/composition state) относится к committed EntryRevision;
- committed revision immutable/append-only и не имеет proposal-подобного lifecycle status;
- pending/accepted/rejected/superseded принадлежат Proposal, а не Revision.


### Сводка 7 — Add existing vs create new

Для Tags и Assets в edit mode действие Add должно различать два сценария:

- выбрать уже существующую сущность и привязать её;
- создать новую сущность и сразу привязать.

Для assets это означает выбор из Asset Library либо создание нового asset (например upload/local file или external link — конкретные варианты UI ещё можно уточнять). Для tags — выбор из существующего catalog либо создание нового tag.


### Ранее обсуждавшиеся UX-идеи, которые сохраняем как контекст

Эти идеи не считаются окончательно зафиксированным layout, но их не нужно терять при следующем проходе:

- Sources/Lineage не являются отдельным постоянным блоком EntryScreen; они доступны как provenance/details конкретных revisions через History;
- manual content editing и редактирование source/composition — разные по смыслу операции; не стоит случайно смешивать их в один незаметный режим;
- старая идея отдельной AI-note/annotation должна быть переоценена уже с учётом новой Proposal/revision-details модели, а не переноситься автоматически;
- старые варианты placement History/Lineage/Tags/Assets считать историческим контекстом: позже в этом треде уже принято, что History идёт gallery/timeline под Entry, Sources/Lineage живут в revision details, а Tags/Assets переходят вправо только при достаточной ширине EntryPanel.

### Сводка 8 — adaptive layout по ширине самой EntryPanel

Зафиксировано, что EntryPanel должна адаптироваться **по собственной доступной ширине**, а не только по ширине viewport/устройства.

При достаточной ширине:

- Title и Event time остаются верхней частью panel;
- Text занимает основную левую/content column;
- Assets и Tags переезжают в правую secondary column;
- created/updated metadata также естественно располагаются внизу secondary column;
- точные пропорции колонок и breakpoint не являются продуктовым решением.

При недостаточной ширине:

- panel складывается в одну колонку;
- Assets, Tags и secondary metadata идут под Text.

Это правило особенно важно для reuse в proposal merge: на обычном широком Entry screen одна panel может показывать правую колонку, а в `Base | Result | Proposal` каждая panel становится уже и автоматически переходит в stacked layout без отдельной специальной версии компонента.

Предпочтение продукта: **справа на широком, снизу на узком**.

### Сводка 9 — Sources / Lineage живут у revisions

Уточнена граница surrounding EntryScreen: отдельный постоянный блок `Sources / Lineage` на основном экране не нужен.

Sources/provenance/lineage семантически относятся прежде всего к конкретной committed revision: от каких raw/source inputs она получена, из какой previous/base revision произошла, какой workflow/proposal/restore создал её и какие related provenance links есть.

Поэтому эти данные показываются из **History / Revisions**:

- у revision может быть компактный provenance/details affordance;
- краткая информация может открываться во всплывающей/hover/popover панели;
- из неё или прямо из revision item можно открыть `Подробнее` / revision details;
- отдельный глубокий details screen допускается, но его внутренний UX сейчас сознательно не проектируется.

На основном EntryScreen не нужно держать отдельные `Sources / Lineage` и `AI Activity / Details` блоки. Actionable AI state остаётся в Proposals; историческая трассировка доступна через revisions/details drill-down.

Итого основной EntryScreen сейчас состоит из reusable EntryPanel, текущих Proposals (если они есть) и History/Revisions плюс обычного navigation/actions chrome.

### Сводка 10 — AI actions на EntryScreen

На EntryScreen нужен screen-level запуск AI над текущей записью. Это не часть reusable EntryPanel.

Предусматриваются два сценария:

- запуск готового workflow для текущей Entry (cleanup, tags, title, date/time и другие доступные workflows);
- `Custom prompt / Ask AI` — разовый пользовательский prompt относительно этой Entry.

Полноценный workflow запускается от **committed revision**. Если пользователь находится в manual edit и есть unsaved/dirty working draft, AI workflow не запускается прямо по эфемерному draft. UI предлагает `Save & Run`: сначала завершается manual editing session и создаётся manual revision, затем эта новая committed revision становится base/input для AI run.

Если workflow предлагает изменить существующую Entry, дальше действует уже согласованный flow `AIResult → Proposal → Apply/Reject → committed revision`.


### Сводка 11 — inline AI editor assistance как кандидат в MVP

Отдельно от полноценных Entry workflows зафиксирована желаемая возможность AI-помощи **непосредственно внутри редактора working draft**: например выделить фрагмент и попросить переписать, сократить, исправить или продолжить текст.

Это другой interaction, чем workflow над committed Entry:

- он может работать с selection/current working draft;
- он потенциально должен поддерживать обычный editor undo;
- не решено, должен ли каждый такой шаг проходить через Proposal/Revision semantics;
- точный UX и data semantics нужно обсудить непосредственно перед реализацией.

Фича не считается обязательной для базового MVP, но сохраняется как **MVP candidate**: если при реализации editor slice она оказывается недорогой и не ломает revision semantics, её можно включить сразу. Решение об этом сознательно откладывается до начала editor implementation.

### Сводка 12 — History/Revisions как gallery/timeline под Entry

History/Revisions не прячется по умолчанию в отдельный tab. На EntryScreen под текущей записью показывается компактная прокручиваемая **gallery/timeline revisions**.

Каждая revision представлена небольшим snippet/card, чтобы можно было быстро листать историю и понимать характер изменения. Карточка может показывать:

- короткий content snippet;
- тип изменения (`manual`, AI-applied, restore/import и т. п.);
- время/дату revision;
- компактное summary/diff-сигналы вроде `text changed`, `+2 tags`, `date changed`, `asset +1`.

Точный визуальный стиль карточек и mobile behaviour остаются UI tuning, но принцип быстрого пролистывания snippets является продуктовым решением.

Клик по revision открывает подробный **read-only comparison**:

- слева показывается **предыдущая revision**;
- справа — выбранная revision;
- обе стороны используют тот же EntryPanel/diff building blocks, но read-only;
- по умолчанию это не сравнение с original/raw и не сравнение с первой revision.

Revision comparison семантически отличается от proposal merge: proposal review использует `Base | Result | Proposal` с editable Result, а History details — `Previous | Selected revision`, обе стороны read-only.

Metadata/provenance изменения отделяется от самого content comparison. Рядом/сверху/снизу может показываться отдельный details block: manual edit / AI workflow / Restore / Import, timestamp, previous/base revision, proposal/AI run/source links и другие provenance данные. Точное placement этого metadata block сейчас не фиксируется.

Для первой revision отдельный edge case (что именно показывать слева: raw/source/empty state) можно определить при реализации details UX.

### Сводка 13 — diff presentation для revision comparison

В revision details сравнивается versioned content, а provenance/lineage/source/AI run/workflow/restoredFrom и другая trace metadata **не сравниваются между панелями**. Они показываются отдельным metadata/provenance блоком под/рядом с выбранной revision.

Для diff presentation согласованы простые правила:

- **Tags:** добавленные и удалённые tags явно маркируются `+ / −`; неизменившиеся показываются обычно.
- **Assets:** та же семантика `+ / −` для добавленных/удалённых assets. Порядок assets не является значимым и reorder не считается изменением.
- **Text:** желательно подсвечивать изменённые фрагменты, чтобы не заставлять пользователя глазами сравнивать две длинные версии. Точный алгоритм/визуальный стиль diff пока не фиксируется — его нужно подобрать при реализации так, чтобы результат был читаемым и не шумным.

Для остальных versioned полей (title, event date/start/end) конкретное визуальное представление изменения можно подобрать вместе с общим diff UI; отдельной сложной механики сейчас не требуется.

### Что ещё не решено

- точный визуальный стиль/адаптация revision gallery, first-revision comparison и text diff — UI/detail decision;

- точные breakpoint/пропорции adaptive EntryPanel — implementation/UI tuning, а не отдельное продуктовое решение;
- какие именно secondary controls/metadata видны всегда, а какие раскрываются;
- нужен ли отдельный AI-note/annotation после появления Proposals и revision details;
- точный placement/menu для Entry-level AI actions;
- inline AI editor assistance не блокирует PQ-011: её UX/semantics и включение в MVP обсуждаются при начале editor implementation.

**Нужно от пользователя:** добить оставшиеся детали PQ-011: placement/menu для Entry-level AI actions, видимость secondary metadata и судьбу старой AI-note/annotation.

пользователь —

**Решение:** —