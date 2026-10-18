# FQ-02 — Merge тегов и неизменяемые Revision

**Источник:** [Функциональное ТЗ / FQ-02](../../AI-Diary-Functional-Spec-v0.1.md#14-открытые-системные-вопросы)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Codex — текущий диалог требований AI Diary  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** Functional/Screens Specs, requirements inventory и product baseline

## Вопрос

Как tag merge меняет current relations при immutable committed snapshot? Нужна семантика redirect/projection/versioned operation и взаимодействия с Draft/lease.

## Варианты

1. Canonical redirect: merge задаёт oldTagId → survivingTagId в каталоге, все текущие lookup/query/count/Entry representations разрешают redirect. Stored committed snapshots не переписываются и ради merge не создаются новые content Revisions; последующий обычный Save может записать surviving ID. Нужна отдельная audit запись merge.
2. Versioned migration: merge создаёт новые Revision для затронутых current Entries с surviving tagId; старые Revision остаются нетронутыми, historical redirect также сохраняется. Draft/base и batch migration требуют протокола.
3. Разделённая семантика: текущие записи разрешают redirect, historical UI показывает имена на момент версии. Для этого нужен дополнительный исторический snapshot каталога/labels, сейчас не согласованный.

## Контекст

Уже принято 04.10: пользователь выбирает canonical survivor, его type/color сохраняются; имя и aliases второго переходят в aliases с дедупликацией, oldTagId сохраняет mergedInto redirect; текущие связи должны разрешаться в survivor, immutable revisions не переписываются. Merge не равен Delete: delete сохраняет самостоятельный deleted tag и старые relations.

Функциональное ТЗ §6 оставило открытым, означает ли переназначение текущих связей физическое изменение versioned snapshot или canonical ID resolution. Новой уверенной трактовки до выбора пользователя нет.

FQ-01 завершён: Save/Apply/Restore и узкие AI auto-apply cases создают committed revisions; это не решает автоматически семантику catalog merge.

Canonical thread FQ-02 раньше в ветке не найден; существующие PQ/AI треды касаются других вопросов. Очерёдность пользователя: Revision/Save/Apply/Restore → merge тегов → протокол надёжного сохранения.

## Обсуждение

пользователь — (2026-10-18, порядок тем) «**Revision/Save/Apply/Restore**, затем **merge тегов**, после этого — протокол надёжного сохранения.»

Codex — (2026-10-18) Предлагаю вариант 1. Пример: объединяем «Велосипед» в «Велопрогулки». Каталог сохраняет redirect; текущие записи, фильтры и счётчики используют один surviving tag и не удваивают Entry, даже если раньше Entry содержала оба tagId. Старые snapshots остаются как были; merge сам не создаёт content Revision в каждой Entry. Его видно как отдельную операцию каталога. Вариант 2 нужен, если пользователь ожидает видеть merge как content change в истории каждой затронутой Entry. Сейчас нужно выбрать эту продуктовую границу; детали изменения Draft под lease/rollback обсудим после неё.

**Нужно от пользователя:** выбрать: merge — перенаправление в каталоге без новых Revision у Entries или content change с новой Revision в каждой затронутой Entry.

пользователь —

**Решение:** —
