# AQ-DATA-007 — Нужно ли позволять пользователю вручную редактировать canonical files?

**Источник:** [04-open-questions.md / AQ-DATA-007](../../04-open-questions.md#aq-data-007--нужно-ли-позволять-пользователю-вручную-редактировать-canonical-files)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Считать ли ручное изменение canonical files официально поддерживаемым способом изменения данных AI Diary, и если да — какие изменения допустимы и как они превращаются в revisions/asset updates без нарушения истории и связей?

## Контекст

Уже принято:

- canonical user data хранятся в user-owned portable files;
- backend при update проверяет storage metadata/version token;
- валидное внешнее content change может быть импортировано как новая immutable revision;
- silent overwrite запрещён;
- committed revisions immutable/append-only;
- Asset имеет stable identity, а historical EntryRevision должна восстанавливать свой asset set.

## Обсуждение

**Решение:** —
