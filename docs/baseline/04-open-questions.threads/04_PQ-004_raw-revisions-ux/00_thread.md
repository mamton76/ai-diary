# PQ-004 — Нужно ли сразу показывать raw/revisions пользователю?

**Источник:** [04-open-questions.md / PQ-004](../../04-open-questions.md#pq-004--нужно-ли-сразу-показывать-rawrevisions-пользователю)  
**Статус:** решён  
**Состояние:** completed  
**Claim:** released  
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
- session завершается явным **Save** или после **10 минут без изменений**;
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

## Решение

Для MVP:

1. Current Entry и History/Revisions разделены в UX.
2. AI mutation существующей записи всегда создаёт revision.
3. Manual editing session начинается с первой правки и создаёт одну revision при Save или после 10 минут inactivity.
4. Autosave не является revision.
5. Подряд идущие manual revisions группируются в раскрываемый блок только на уровне UI.
6. Revision history линейная, без branches.
7. Restore создаёт новую revision из snapshot старой и сохраняет ссылку на source revision.
