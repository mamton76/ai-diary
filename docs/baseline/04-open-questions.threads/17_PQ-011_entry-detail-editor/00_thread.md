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

- Sources/Lineage должны быть доступны с EntryScreen, но не входить в reusable EntryPanel;
- manual content editing и редактирование source/composition — разные по смыслу операции; не стоит случайно смешивать их в один незаметный режим;
- старая идея отдельной AI-note/annotation должна быть переоценена уже с учётом новой Proposal/AI activity модели, а не переноситься автоматически;
- конкретное положение History, Lineage, Tags и Assets на desktop/mobile пока остаётся открытым.

### Что ещё не решено

- окончательный порядок/placement секций EntryPanel на desktop;
- адаптация того же layout на narrow/mobile;
- какие именно secondary controls/metadata видны всегда, а какие раскрываются;
- финальная компоновка surrounding EntryScreen вокруг panel.

**Нужно от пользователя:** продолжить с layout/placement EntryPanel и затем surrounding EntryScreen.

пользователь —

**Решение:** —