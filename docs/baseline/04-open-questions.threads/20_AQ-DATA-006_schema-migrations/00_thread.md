# AQ-DATA-006 — Format schema и migrations

**Источник:** [04-open-questions.md / AQ-DATA-006](../../04-open-questions.md#aq-data-006--format-schema-и-migrations)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Как версионировать canonical file format и как безопасно обновлять старые diary files при изменении schema?

## Контекст

Уже существует историческое направление с `formatVersion` в важных JSON-файлах и папкой `_formats/`, но нужно решить продуктово-архитектурный контракт новой версии.

Нужно определить:
- где хранится schema/version;
- version granularity;
- backward compatibility;
- когда migration выполняется автоматически, а когда требует явного шага;
- backup/rollback;
- validation;
- как rebuild derived indexes после migration.

## Рабочее направление

Минимально разумно:
- каждый canonical structured file имеет явный schema/format version;
- reader умеет читать текущую и ограниченное число старых версий;
- migration создаёт новый canonical state безопасно и не уничтожает recoverability;
- derived indexes после migration пересобираются, а не мигрируются как источник истины.

**Решение:** —


### Сводка 2 — общая версия формата

Пользователь предпочитает не усложнять versioning по типам сущностей.

Согласовано:
- используется **одна общая версия формата storage** для всего AI Diary;
- migration переводит storage на новую общую format version;
- при этом migration меняет только те файлы/сущности, чья структура реально изменилась;
- если, например, schema tags между версиями не изменилась, tag files переписывать не нужно;
- отдельные независимые `entrySchemaVersion` / `assetSchemaVersion` / `tagSchemaVersion` как основной публичный versioning contract не вводятся.

Это оставляет formatVersion простой для пользователя и tooling, не заставляя делать бессмысленные rewrites неизменившихся данных.
