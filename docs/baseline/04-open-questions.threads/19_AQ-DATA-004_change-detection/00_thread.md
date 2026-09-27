# AQ-DATA-004 — Change detection

**Источник:** [04-open-questions.md / AQ-DATA-004](../../04-open-questions.md#aq-data-004--change-detection)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Как backend понимает, что canonical Drive/files изменились и derived state/cache/index надо обновить или reconciliate?

## Контекст

Уже решено:
- canonical data живут в user-owned Drive/files;
- первый MVP files-only, без обязательного persistent index;
- основной application/domain слой работает через domain-level repository;
- позже может появиться rebuildable derived index;
- manual editing canonical files обсуждается отдельно в AQ-DATA-007;
- concurrency / optimistic locking обсуждается отдельно в AQ-DATA-003.

## Основные варианты

- не отслеживать внешние изменения в первом MVP: canonical writes идут только через backend;
- Drive Changes API;
- ETag / modifiedTime / version tokens при чтении;
- периодический reconciliation;
- комбинация.

## Обсуждение

### Сводка 1 — старт

Нужно решить не конкретный Google API вызов, а MVP-policy: считаем ли изменения вне backend поддерживаемым сценарием уже сейчас или откладываем external change detection до появления такого требования.

### Сводка 2 — supported writers vs input sources

Уточнено: ограничение «writes только через backend» относится к **изменению canonical files**, а не к источникам capture.

Новые entries могут создаваться из любых официально поддержанных inputs/adapters — web, Calendar, Telegram, assistant integrations, imports и т. п. — но после normalization они должны проходить через общий application/domain pipeline и сохраняться в canonical storage через backend/repository boundary.

Для первого MVP прямое внешнее редактирование canonical files вне backend не считается штатно поддерживаемым сценарием. Поэтому постоянный Drive change watcher не обязателен на старте. При committed write всё равно нужен concurrency/version check, чтобы не делать silent overwrite, если файл неожиданно изменился.

**Решение:** [принято] official inputs may create entries from many channels, but canonical persistence/update funnels through backend/domain repository. External direct file edits are not an MVP-supported write path; dedicated Drive change detection can be deferred.
