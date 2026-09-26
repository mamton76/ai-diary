# AQ-DATA-010 — Как хранить autosave / working state незавершённой editing session?

**Источник:** [04-open-questions.md / AQ-DATA-010](../../04-open-questions.md#aq-data-010--как-хранить-autosave--working-state-незавершённой-editing-session)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и будущий architecture/data design

## Вопрос

Как технически хранить промежуточное autosave-состояние manual editing session до того, как оно станет полноценной revision?

## Уже принято в PQ-004

- editing session начинается с первой реальной ручной правки;
- autosave должен защищать текущую работу от потери;
- autosave сам по себе не создаёт revision;
- manual revision создаётся при явном Save или после **1 часа inactivity**.

## Что нужно решить

- один mutable working draft или несколько autosave snapshots;
- где хранится working state: canonical files, derived/operational layer или комбинация;
- как восстанавливать draft после reload/crash/network failure;
- когда и как working state очищается после создания revision;
- нужен ли TTL/cleanup для abandoned drafts;
- как autosave взаимодействует с optimistic concurrency и параллельным редактированием;
- что происходит, если AI mutation запускается во время активной manual editing session.

## Обсуждение

### Сводка 1 — старт обсуждения

Вопрос перенесён рядом с PQ-004, из которого он возник, и взят в активное обсуждение.

### Сводка 2 — hybrid draft + local recovery snapshots

Зафиксирована рабочая модель autosave:

- основное незавершённое состояние хранится как **один current working draft**, который синхронизируется с backend;
- локально в браузере дополнительно хранится ограниченный набор **recovery snapshots** как защита от случайных действий пользователя;
- local snapshots не являются revisions и не появляются в обычной History/Revisions;
- snapshots создаются только при наличии изменений и реальном отличии от предыдущего snapshot;
- интервал между такими локальными autosave/snapshot точками — **не более 30 секунд**;
- snapshots ограничены по количеству/времени и автоматически очищаются, чтобы не превращаться во вторую скрытую историю;
- после завершения editing session и успешного создания revision локальные recovery snapshots этой session могут быть удалены;
- при кратком отсутствии сети локальное состояние продолжает сохраняться, а backend draft синхронизируется после восстановления соединения.

Дополнительно зафиксированы MVP-defaults:

- `maxLocalSnapshots = 5`;
- локальные snapshots считаются настраиваемой policy constant, а не жёсткой частью модели;
- после успешного создания revision snapshots не удаляются сразу, а переходят в grace period;
- grace period по умолчанию — **24 часа**;
- после grace period snapshots этой editing session удаляются;
- это правило одинаково применяется и к manual Save, и к auto-revision после inactivity.

### Сводка 3 — operational working draft

Зафиксировано:

- server-side `current working draft` живёт в **operational state**;
- canonical и operational storage могут на первом этапе физически совпадать;
- при этом они должны быть **семантически разделены** по роли и lifecycle;
- canonical data — это зафиксированные revisions и другие долговечные данные;
- operational state — временный working draft, autosave/sync metadata, locks и подобное;
- auto-revision создаётся из server-side `current working draft`, а не из local recovery snapshots;
- inactivity timeout для auto-revision по умолчанию — **1 час**;
- local recovery snapshots хранятся **24 часа после успешного создания revision**.

Все численные значения считаются настраиваемыми policy constants.

Остаются открытыми детали: recovery UX, concurrency и поведение при AI mutation во время активной session.

## Решение

—
