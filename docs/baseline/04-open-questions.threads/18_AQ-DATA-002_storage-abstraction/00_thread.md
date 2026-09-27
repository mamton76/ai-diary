# AQ-DATA-002 — Гранулярность storage abstraction

**Источник:** [04-open-questions.md / AQ-DATA-002](../../04-open-questions.md#aq-data-002--гранулярность-storage-abstraction)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Какой контракт должен видеть domain/backend core поверх storage: низкоуровневые file operations или domain-level repository operations?

## Контекст

Уже решено:
- первый MVP files-only;
- canonical data живут в user-owned Drive/files;
- отдельный data layer/repository abstraction нужен с самого начала;
- позже должен безболезненно подключаться rebuildable derived index;
- UI/domain logic не должны зависеть от Drive-specific деталей.

## Основные варианты

Низкоуровневый storage API:
- listFiles
- readFile
- writeFile
- moveFile

Domain-level repository API:
- listEntries
- getEntry
- saveRevision
- listChanges
- loadHistory

Гибрид:
- application/domain код использует domain-level repository;
- отдельные migration/import/repair tools могут использовать lower-level file adapter.

## Обсуждение

### Сводка 1 — старт

Вопрос в том, где проходит abstraction boundary и не протекают ли Drive/files детали в domain logic.

**Решение:** —
