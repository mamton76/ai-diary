# FQ-08 / SQ-01 — Lifecycle Entry после Restore из Trash

**Источник:** [Функциональное ТЗ, ENT-11/FQ-08](../../../AI-Diary-Functional-Spec-v0.1.md#42-lifecycle)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Codex — текущий диалог требований AI Diary  
**Режим фиксации:** written-turns  
**Родитель:** [FQ-08, группа lifecycle/retention](../00_thread.md)  
**Дочерние треды:** —  
**Куда переносим решение:** Functional/Screens Specs, file-format / Save design, inventory/product baseline

## Вопрос

Entry могла быть Active либо Archived перед удалением. В какой lifecycle возвращает Restore из Trash?

Этот вопрос относится только к восстановлению Entry из корзины. Restore исторической Revision — отдельное уже согласованное content commit действие.

## Уже принято

- Active / Archived / Trash — lifecycle Entry.
- Delete существующей Entry переносит её вместе с Draft в Trash.
- Restore из Trash не создаёт content Revision.
- История и существующий durable Draft сохраняются.
- Вопрос целевого lifecycle явно открыт в FQ-08.

## Варианты

1. **Рекомендация:** вернуть состояние до удаления: Active → Trash → Active; Archived → Trash → Archived. При Delete сохранить прежний lifecycle в metadata/audit. Восстановление не означает автоматическую разархивацию.
2. Любой Restore из Trash возвращает Entry в Active, даже если она была архивной.

## Контекст

Прежнее состояние не определяется текущими фильтрами экрана и не угадывается по наличию Draft. Повторный запрос Restore не создаёт отдельной content Revision. Для legacy data без сохранённого прежнего lifecycle нужен явно определённый recovery/migration путь; текущий вопрос не утверждает silent fallback.

Исходный узел FQ-08 про готовые uploads после Discard остаётся resolved в своей области. Этот дочерний узел группирует самостоятельный следующий подпункт общего FQ-08 и не переоткрывает принятое правило Asset unlink/delete.

## Обсуждение

пользователь — (2026-10-18) «лальше»

Codex — (2026-10-18) Рекомендую Restore в состояние до удаления. Архивная Entry возвращается в архив, активная — в активные; сохранённый Draft остаётся у той же Entry, content Revision не создаётся. Вариант пока не принят.

**Нужно от пользователя:** Restore из Trash возвращает Entry в прежнее состояние, включая возврат архивной записи в архив?

пользователь —

**Решение:** —
