# AQ-DATA-010 — Как хранить autosave / working state незавершённой editing session?

**Источник:** [04-open-questions.md / AQ-DATA-010](../../04-open-questions.md#aq-data-010--как-хранить-autosave--working-state-незавершённой-editing-session)  
**Статус:** открытый  
**Состояние:** paused  
**Claim:** released  
**Ведёт:** —  
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
- manual revision создаётся при явном Save или после 10 минут inactivity.

## Что нужно решить

- один mutable working draft или несколько autosave snapshots;
- где хранится working state: canonical files, derived/operational layer или комбинация;
- как восстанавливать draft после reload/crash/network failure;
- когда и как working state очищается после создания revision;
- нужен ли TTL/cleanup для abandoned drafts;
- как autosave взаимодействует с optimistic concurrency и параллельным редактированием;
- что происходит, если AI mutation запускается во время активной manual editing session.

## Решение

—
