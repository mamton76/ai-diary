# AQ-DATA-002 — Гранулярность storage abstraction

**Источник:** [04-open-questions.md / AQ-DATA-002](../../04-open-questions.md#aq-data-002--гранулярность-storage-abstraction)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

### Сводка 2 — решение

Пользователь подтвердил ранее обсуждавшееся направление: основной application/domain код работает через **высокоуровневый domain repository**, а не через file operations.

Основной контракт должен быть в терминах diary domain, например:
- `listEntries`
- `getEntry`
- `saveRevision`
- `loadHistory`
- при необходимости domain-level changes/listing methods.

Drive/files API остаётся внутренней implementation detail нижнего storage adapter.

Low-level file access допускается для migration/import/repair/admin tooling, но не должен протекать в основной domain/application слой.

**Решение:** [принято] основной storage abstraction — domain-level repository; low-level file adapter скрыт ниже и используется напрямую только специальными техническими инструментами.
