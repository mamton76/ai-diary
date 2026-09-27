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


### Сводка 3 — migration lock, validation report и before/after review

Согласован пользовательский flow migration:

1. приложение обнаруживает старую общую `formatVersion`;
2. migration запускается как отдельная явная операция, а не как незаметное переписывание storage;
3. перед изменениями создаётся backup/snapshot;
4. на время migration storage переводится в maintenance/read-only mode: **редактирование и все mutating workflows запрещены**;
5. это ограничение должны уважать не только web/backend, но и существующие Calendar/Telegram/file-based writers, пока они могут писать напрямую в storage;
6. migration изменяет только те типы файлов, чья структура реально поменялась;
7. выполняются schema validation, integrity checks, counts/hashes и migration-specific invariants;
8. новая общая `formatVersion` считается принятой только после успешной полной validation;
9. после migration пользователь получает report;
10. report даёт возможность точечно открыть `before / after` для изменённых объектов, особенно для warning/review cases; массовая ручная проверка всех записей не требуется.

Автоматическая validation является основной гарантией. Human review — дополнительный spot-check и обязательный путь для случаев, которые validator отметил как uncertain/problematic.

### Открытый под-вопрос — нужен ли runtime-reader всех старых форматов?

Для `before / after` не обязательно заставлять основное приложение навсегда поддерживать все исторические storage formats.

Предпочтительное направление:
- migration runner умеет читать **source version**, из которой он мигрирует;
- до изменения сохраняется immutable pre-migration snapshot/backup;
- migration report сохраняет достаточно данных для comparison (например, ссылки на before snapshot и after entity плюс normalized/rendered comparison snapshot);
- обычный application repository после успешной migration может работать только с current format (или небольшим окном совместимости), а исторические readers остаются частью migration tooling, а не core runtime.

Нужно подтвердить этот вариант перед закрытием AQ-DATA-006.
