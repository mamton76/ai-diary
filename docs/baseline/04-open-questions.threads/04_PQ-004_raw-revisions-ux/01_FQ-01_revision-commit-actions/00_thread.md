# FQ-01 — Revision / Save / Apply / Restore

**Источник:** [Функциональное ТЗ / FQ-01](../../../AI-Diary-Functional-Spec-v0.1.md#14-открытые-системные-вопросы)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** [PQ-004](../00_thread.md)  
**Дочерние треды:** —  
**Куда переносим решение:** AI-Diary-Functional-Spec-v0.1.md, AI-Diary-Screens-Spec-v0.1.md, 02-requirements-inventory.md, 03-product-baseline.md; связанные PQ-004/PQ-005/AQ-DATA-010 по применимости.

## Вопрос

Точная граница «Revision только по Save»: manual Draft против явных Apply/Restore и прежнего AI auto-apply.

Обсуждаем последовательно: сначала явные пользовательские операции, затем допустимые автоматические изменения. Отмену таймерного коммита не переоткрываем.

## Варианты

1. Save, Apply и Restore — самостоятельные явные commit-действия. Save фиксирует ручной Draft; Apply фиксирует подтверждённый AI Result; Restore создаёт новую Revision из старого snapshot. Дополнительный Save после Apply/Restore не нужен.
2. Только Save создаёт Revision. Apply/Restore сначала переносят результат в Draft, который пользователь затем сохраняет отдельным Save.

## Контекст

PQ-004 и PQ-005 ранее приняли прямое создание Revision при Apply и Restore; обычный Reject Revision не создаёт. Ручной autosave не создаёт Revision.

Решения 04.10 отменили коммит по inactivity и сохранили durable Draft, но формулировка «Revision только по Save» в консолидированном документе оставила неоднозначность её охвата. Поэтому FQ-01 выделен как уточнение на пересечении требований, а не повторная история всего PQ-004.

Старые PQ-004/AQ-DATA-010 пока содержат уже отменённый часовой таймер и server-only представление Draft; это исторический несинхронизированный текст, не основание вернуть старое поведение. После решения нужно синхронизировать соответствующие source-документы с сохранением истории.

AI auto-apply существующих тегов и первая normalized Entry из raw ранее допускались per-workflow policy (PQ-005). Этот отдельный хвост FQ-01 нужно разобрать после выбора для явных действий; он ещё не закрыт.

## Обсуждение

пользователь — (2026-10-18) «давай по очереди это все обсудлим»

пользователь — (2026-10-18) «**Revision/Save/Apply/Restore**, затем **merge тегов**, после этого — протокол надёжного сохранения.»

Codex — (2026-10-18) Предлагаю вариант 1: общее правило формулировать как «Ручной Draft становится Revision только при явном Save; подтверждённые Apply и Restore — самостоятельные операции создания Revision». Autosave/Return later/Discard/Reject Revision не создают. Restore добавляет новую Revision и не удаляет более новые исторические состояния. Это сохраняет прежнюю семантику Apply/Restore и не добавляет второе подтверждение после уже явного действия. Сначала нужен выбор по этой границе; auto-apply обсудим следующим вопросом.

пользователь — (2026-10-18) «**Выбираем первый вариант — Apply и Restore сразу создают Revision?**»

Codex — (2026-10-18) Фиксирую выбор первого варианта: Save ручного Draft, подтверждённый Apply и подтверждённый Restore исторической версии — самостоятельные commit-действия; дополнительный Save после Apply/Restore не нужен. Это частичное закрытие FQ-01. Restore из lifecycle Trash не тождественен Restore revision и content Revision не создаёт.

**Согласованная часть FQ-01 (2026-10-18):** ручные правки фиксирует Save; Apply подтверждённого AI proposal и Restore исторического snapshot сразу создают по одной новой Revision; autosave, Return later, Discard и Reject Revision не создают. Более поздние исторические версии при Restore сохраняются. Остался AI auto-apply.

Codex — (2026-10-18) Следующий подвопрос: сохранить ли прежние узкие исключения PQ-005 — автоматическую первую normalized Entry из сохранённого raw и высокоуверенную привязку existing tags. Предлагаю оставить их per-routine policy с trace и committed Revision для изменения existing Entry, без записи в ручной Draft и с пропуском Draft Entries. Изменения текста existing Entry и новые tags остаются proposals. Это предложение ещё не принято.

пользователь — (2026-10-18) «мне кажется оставляем»

Codex — (2026-10-18) Сохранены два исключения auto-apply, обсуждавшиеся непосредственно перед этой репликой: первая normalization из raw и добавление existing tags по routine policy. Это не разрешение на произвольные AI mutations. Решение перенесено в Functional/Screens Specs и baseline/inventory; FQ-01 закрыт. Следующий вопрос по согласованному порядку — FQ-02 (merge тегов).

**Решение:** [принято] (2026-10-18) Save ручного Draft, подтверждённые Apply и Restore исторической версии самостоятельно создают по одной новой Revision без второго Save. Autosave/inactivity/Return later/Discard/Reject Revision не создают. Restore добавляет новую версию без удаления последующей истории; Restore из Trash остаётся lifecycle-операцией. Первая normalized Entry может создаваться автоматически из сохранённого raw с явной uncertainty; existing tags могут добавляться автоматически при высокой уверенности, если это разрешено routine policy. Изменение existing Entry создаёт новую committed Revision с trace routine/input/result; первая обработка создаёт первую committed Revision. Existing Entries с Draft пропускаются, ручной Draft AI не переписывает. Изменения текста existing Entry и создание новых тегов по умолчанию остаются proposals. Конкретные confidence thresholds не фиксируются.
