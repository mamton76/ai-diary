# AQ-DATA-010 — Как хранить autosave / working state незавершённой editing session?

**Источник:** [04-open-questions.md / AQ-DATA-010](../../04-open-questions.md#aq-data-010--как-хранить-autosave--working-state-незавершённой-editing-session)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и будущий architecture/data design

## Вопрос

Как технически хранить промежуточное autosave-состояние manual editing session до того, как оно станет полноценной revision?

## Уже принято в PQ-004

- editing session начинается с первой реальной ручной правки;
- autosave защищает текущую работу от потери;
- autosave сам по себе не создаёт revision;
- manual revision создаётся при явном Save или после **1 часа inactivity**.

## Обсуждение

### Сводка 1 — hybrid draft + local recovery snapshots

Принята гибридная модель:

- у entry есть один server-side **current working draft**;
- локально клиент хранит ограниченные **recovery snapshots**;
- local snapshots не являются revisions и не входят в обычную History;
- snapshots создаются только при изменении содержимого;
- интервал между локальными recovery points — не более **30 секунд**;
- MVP-default: **5 local snapshots**;
- после успешного создания revision local snapshots живут ещё **24 часа**, затем очищаются;
- все численные значения считаются настраиваемыми policy constants.

### Сводка 2 — operational state

- server-side `current working draft` хранится в **operational state**;
- canonical и operational storage могут физически совпадать на MVP, но семантически разделены;
- canonical data — зафиксированные revisions и другие долговечные данные;
- operational state — working draft, leases/locks, sync metadata и другие временные данные;
- auto-revision создаётся из server-side working draft, а не из local snapshots;
- после успешного создания revision server draft больше не нужен и очищается;
- если revision commit не удался, draft сохраняется до успешного завершения операции.

### Сводка 3 — recovery UX

Если server-side draft существует, при открытии entry пользователь автоматически продолжает его:

- entry сразу открывается в editing state;
- Save/статус визуально показывают наличие несохранённых изменений;
- отображается время последней синхронизации draft;
- recovery points показываются компактной шкалой:
  **previous revision → local snapshots → current draft**;
- previous revision и current draft обозначаются крупными точками, local snapshots — маленькими;
- hover/tap показывает timestamp и тип точки;
- выбор snapshot сначала даёт preview;
- restore snapshot заменяет current working draft и сам по себе revision не создаёт.

### Сводка 4 — editing lease и multi-device

Принята модель **одного active editor**:

- при начале ручного редактирования session получает soft editing lease;
- при открытии той же entry в другой вкладке/на другом устройстве автоматически подгружается текущий server draft;
- второй клиент видит предупреждение и может открыть read-only либо выбрать **«Редактировать всё равно»**;
- при force-edit lease переходит новой session;
- прежняя session получает уведомление и переходит в paused/read-only state;
- она может позже снова забрать lease;
- перед передачей lease новый владелец должен получить свежий server draft;
- локальные несинхронизированные изменения старой session не теряются и остаются в local recovery snapshots.

### Сводка 5 — AI mutation и очередь jobs

У entry в каждый момент есть только один mutation owner: manual editing session либо AI job.

- AI mutation не запускается при active manual editing lease;
- informational/read-only AI может работать без mutation lease;
- пользователь может поставить AI mutation в очередь как **run after current editing session**;
- queued jobs видимы в UI компактным статусом/бейджем, с состояниями queued/running/done/failed и возможностью отмены;
- manual editing имеет приоритет: если пользователь снова начинает редактировать до старта job, job продолжает ждать свободного окна;
- когда AI mutation уже выполняется, job получает mutation lease;
- если пользователь хочет редактировать, он может прервать AI job и забрать lease;
- job получает `cancel_requested` и после потери lease не имеет права записать revision;
- уже отправленный внешний LLM request может физически завершиться, но его результат не применяется автоматически без повторной проверки lease/version.

### Сводка 6 — rebase / compatibility check AI result

Если AI job работала от старой revision, а пользователь успел внести изменения:

- AI result остаётся привязан к base revision;
- сначала выполняется **deterministic compatibility check** между base и current revision;
- если изменение явно совместимо с типом workflow, результат можно перенести;
- если совместимость неочевидна, допускается отдельная **AI revalidation**;
- metadata workflows могут чаще rebase/revalidate;
- текстовые mutation workflows по умолчанию не auto-merge;
- при сомнении результат остаётся proposal или workflow запускается заново;
- после revalidation job должна заново получить mutation lease перед записью.

### Сводка 7 — sync strategy

Для sync local working state → server draft принята комбинированная стратегия:

- быстрый debounce после паузы во вводе;
- гарантированный periodic flush, если есть unsynced changes;
- обязательный flush перед Save, передачей lease и auto-revision;
- конкретные интервалы debounce/forced flush подбираются позже и являются configurable constants.

## Решение

[принято] (2026-09-26) Используем hybrid autosave model: один server-side current working draft в operational state + bounded local recovery snapshots. Draft и canonical revisions семантически разделены. Для manual editing действует soft lease с одним active editor и безопасным takeover между sessions. AI mutations используют тот же mutation-lease принцип, могут ждать в очереди, уступают ручному редактированию и при устаревшем base state проходят deterministic compatibility check с AI revalidation только при необходимости. Local snapshots: MVP-default 5 точек, не более 30 секунд между recovery points, retention 24 часа после successful revision. Auto-revision — после 1 часа inactivity. Server draft очищается после successful revision; при failed commit сохраняется. Sync draft — debounce + guaranteed flush, точные интервалы configurable.
