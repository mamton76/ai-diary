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

### Сводка 1 — manual edits не должны тащить Asset versioning в текущую архитектуру

Пользователь подтвердил: отдельное versioning media Assets сейчас не планируется и не должно становиться условием поддержки ручных canonical edits.

Для AQ-DATA-007 поэтому различаем:
- ручное изменение canonical text/metadata files, которое при валидном и консистентном состоянии может быть принято как external content change и зафиксировано новой Entry revision;
- destructive replacement/историческое versioning media originals — отдельная более сложная тема, которую не решаем в текущем MVP.

Если позднее появится реальная потребность сохранять исторические версии одного и того же media Asset (например original vs enhanced/restored photo), это возвращается как отдельный future-вопрос и не блокирует AQ-DATA-007.

### Сводка 2 — граница manual edit и MVP scope

Если manual editing canonical files когда-либо считается официально поддерживаемым, поддерживаемыми считаются прежде всего **содержательные поля** Entry: текст, title, date/time, tags и ссылки на уже существующие Assets. Изменение identity/system invariants (`entryId`, `revisionId`, current revision pointers, provenance/system metadata) и произвольное изменение storage layout не считаются обычным supported edit path.

При обнаружении внешнего изменения backend должен различать:
- валидное изменение поддерживаемых content fields → может быть принято как external manual edit и оформлено новой revision;
- изменение system/invariant fields или нарушение integrity → validation/recovery path, без автоматического принятия.

При этом пользователь отдельно отметил, что **полноценную поддержку manual canonical editing не обязательно тянуть в MVP**. Возможный MVP-подход: canonical files остаются readable/portable, backend умеет безопасно заметить неожиданные изменения и не потерять данные, но официальный manual-edit workflow откладывается.

**Решение:** —
