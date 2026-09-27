# AQ-DATA-006 — Format schema и migrations

**Источник:** [04-open-questions.md / AQ-DATA-006](../../04-open-questions.md#aq-data-006--format-schema-и-migrations)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

## Первоначальное рабочее направление

На старте обсуждения рассматривался вариант, где reader основного приложения умеет читать текущую и ограниченное число старых версий. В ходе обсуждения этот вариант был уточнён и заменён финальным решением ниже: historical readers/transformers относятся к migration tooling, а core runtime не обязан постоянно поддерживать старые formats.

Неизменившаяся часть направления:
- migration создаёт новый canonical state безопасно и не уничтожает recoverability;
- derived indexes после migration пересобираются, а не мигрируются как источник истины.


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

### Уточнение — runtime-reader старых форматов

Для `before / after` не обязательно заставлять основное приложение навсегда поддерживать все исторические storage formats.

Предпочтительное направление:
- migration runner умеет читать **source version**, из которой он мигрирует;
- до изменения сохраняется immutable pre-migration snapshot/backup;
- migration report сохраняет достаточно данных для comparison (например, ссылки на before snapshot и after entity плюс normalized/rendered comparison snapshot);
- обычный application repository после успешной migration может работать только с current format (или небольшим окном совместимости), а исторические readers остаются частью migration tooling, а не core runtime.

Этот вариант подтверждён итоговым решением ниже.


### Сводка 4 — последовательные migration steps и отложенный UX comparison

Дополнительно согласовано:
- migrations логически последовательные: если storage на `v1`, а current format `v5`, одна пользовательская операция выполняет цепочку `v1 -> v2 -> v3 -> v4 -> v5`;
- direct migrations вроде `v1 -> v5` не обязательны;
- каждый migration step знает только соседние source/target formats;
- core application не обязан постоянно поддерживать чтение всех исторических форматов;
- historical readers/transformers остаются в migration tooling;
- before/after review должен быть semantic/domain-level, а raw JSON — secondary technical detail;
- конкретный UI `before / after` сейчас не фиксируется.

**Важно для первой реальной migration:** при реализации первой migration обязательно вернуться к UX migration report и способу отображения `before / after`; это отдельный implementation/design checkpoint и не должно потеряться.

**Решение:** [принято] одна общая storage format version; явные последовательные migrations с maintenance lock, backup, validation и report; historical format support живёт в migration tooling; детали визуального comparison решаются при реализации первой migration.
