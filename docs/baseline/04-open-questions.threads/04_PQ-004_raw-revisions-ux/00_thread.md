# PQ-004 — Нужно ли сразу показывать raw/revisions пользователю?

**Источник:** [04-open-questions.md / PQ-004](../../04-open-questions.md#pq-004--нужно-ли-сразу-показывать-rawrevisions-пользователю)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Как raw source и revision history должны быть представлены пользователю в обычном web UX, и какие пользовательские действия создают/восстанавливают revisions?

## Контекст

Хранить raw и revisions считаем обязательным. Здесь решается их UX, границы manual revisions и restore semantics.

## Обсуждение

### Сводка 1 — Entry UI

Рабочая модель принята как MVP-направление:

- основной tab **Entry** показывает актуальную запись и действия над ней;
- отдельный tab **History / Revisions** показывает историю изменений;
- raw/original доступен через историю, но не обязан постоянно занимать место на основном экране;
- desktop может показывать более богатую timeline/history, mobile — более компактное представление.

### Сводка 2 — AI revisions

Любое AI-действие, которое изменяет существующую запись, создаёт отдельную revision. Предыдущая версия сохраняется. AI proposal до Apply может оставаться proposal; применённая AI mutation становится revision.

### Сводка 3 — manual editing session

Manual revision определяется не «размером» правки, а границей editing session:

- простое открытие записи на просмотр не начинает editing session;
- session начинается с **первой реальной ручной правки**;
- с этого момента работает autosave;
- autosave сохраняет промежуточный working state, но сам по себе **не создаёт revision**;
- session завершается явным **Save** или после **1 часа без изменений**;
- при завершении session последнее autosaved состояние фиксируется как manual revision.

Не вводим эвристику «мелкая/крупная правка»: даже исправление одной запятой может быть отдельной revision, если это отдельная завершённая editing session.

Техническая модель хранения autosave/working draft вынесена в отдельный открытый вопрос AQ-DATA-010.

### Сводка 4 — представление manual revisions

Для MVP подряд идущие manual revisions визуально группируются в один раскрываемый блок History. Все исходные revisions остаются отдельными данными и доступны при раскрытии.

Это только presentation rule: позднее UI можно заменить на timeline/points/другое представление без миграции revision data.

### Сводка 5 — restore

История entry остаётся **линейной**, Git-подобные ветки не создаём.

Restore старой revision:

- не удаляет последующие revisions;
- не переключает «активную ветку» назад;
- берёт snapshot выбранной старой revision и создаёт из него **новую revision поверх текущей**;
- новая revision хранит provenance-ссылку на источник, например `restoredFromRevisionId`.

Таким образом, история сохраняется полностью и остаётся линейной.


### Сводка 6 — proposal vs revision

Из PQ-005 возникло уточнение: AI-результат до принятия пользователем лучше считать proposal, а не revision. Proposal не входит в committed History. Apply создаёт revision; Reject оставляет History без новой revision. Поэтому вопрос об очистке последних committed revisions нужно обсуждать отдельно: для непринятых AI-вариантов он, возможно, не нужен.

См. [PQ-005](../05_PQ-005_ai-automation-policy/00_thread.md).

### Сводка 7 — committed revisions не имеют pending lifecycle

После отделения Proposal от Revision уточнена семантика committed history:

- revision появляется только когда состояние уже committed;
- revisions считаются immutable / append-only snapshots и не требуют lifecycle-статуса вроде pending/accepted/rejected;
- пользователь не удаляет отдельные committed revisions вручную;
- Restore, Undo уже применённого AI proposal и другие возвраты состояния создают **новую revision поверх истории**, а не удаляют/откатывают предыдущую;
- поэтому Apply proposal → затем Undo остаются двумя понятными историческими действиями с provenance.


### Сводка 8 — compaction истории отложен

Физическое уменьшение длинной revision history не является обычным пользовательским delete/rollback и не нужно для MVP.

В future backlog вынесена отдельная maintenance-механика: создать synthetic checkpoint revision с полным состоянием и затем по retention policy архивировать/удалять старые промежуточные revisions, не меняя текущую пользовательскую историю и сохраняя необходимые provenance/raw guarantees.

См. [FQ-REVISION-002 — Revision history compaction / retention](../../06-future-questions.md#fq-revision-002--revision-history-compaction--retention).

### Сводка 9 — уточнение History UX из PQ-011

27 сентября 2026 в PQ-011 пересмотрена только presentation-часть раннего решения о History. История больше не обязана открываться отдельным tab/view по умолчанию.

На основном EntryScreen под текущей Entry показывается компактная scrollable gallery/timeline revision snippets. Выбор revision открывает подробное read-only сравнение `Previous revision | Selected revision`; provenance/metadata изменения показываются отдельно от content comparison.

Это не меняет revision semantics: история остаётся линейной и append-only, proposals не являются revisions до Apply, Restore/Undo создают новые revisions.

**Решение (снято частично, 2026-09-27):** прежняя формулировка пункта 1 требовала разделять Current Entry и History/Revisions как отдельные UX views; это ограничение заменено встроенной gallery/timeline под Entry с drill-down в revision details.

### Предыдущее решение до уточнения presentation

Для MVP:

1. Current Entry и History/Revisions разделены в UX.
2. AI proposal до Apply не является revision; применённая AI mutation существующей записи создаёт отдельную revision.
3. Manual editing session начинается с первой правки и создаёт одну revision при Save или после 1 часа inactivity.
4. Autosave не является revision.
5. Подряд идущие manual revisions группируются в раскрываемый блок только на уровне UI.
6. Revision history линейная, без branches; committed revisions immutable/append-only и не удаляются пользователем по одной.
7. Restore или Undo уже применённого изменения создаёт новую revision из нужного snapshot и сохраняет provenance, не удаляя старую историю.
8. History compaction/retention через synthetic checkpoint откладывается в future backlog.

## Решение

Для MVP:

1. Current Entry остаётся главным состоянием экрана; непосредственно под ней доступна компактная scrollable History/Revisions gallery/timeline со snippet-карточками revisions. Клик по revision открывает read-only comparison предыдущей и выбранной revision; raw/original доступен через history/details, но не обязан постоянно занимать место рядом с current state.
2. AI proposal до Apply не является revision; применённая AI mutation существующей записи создаёт отдельную revision.
3. Manual editing session начинается с первой правки и создаёт одну revision при Save или после 1 часа inactivity.
4. Autosave не является revision.
5. Подряд идущие manual revisions могут группироваться только на уровне presentation; базовые revision records сохраняются.
6. Revision history линейная, без branches; committed revisions immutable/append-only и не удаляются пользователем по одной.
7. Restore или Undo уже применённого изменения создаёт новую revision из нужного snapshot и сохраняет provenance, не удаляя старую историю.
8. History compaction/retention через synthetic checkpoint откладывается в future backlog.
