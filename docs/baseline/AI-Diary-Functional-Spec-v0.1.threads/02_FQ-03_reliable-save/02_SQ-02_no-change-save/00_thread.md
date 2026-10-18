# FQ-03 / SQ-02 — Manual Save без изменения content

**Источник:** [Функциональное ТЗ, §4.1](../../../AI-Diary-Functional-Spec-v0.1.md#41-контракт-операций)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Codex — текущий диалог требований AI Diary  
**Режим фиксации:** written-turns  
**Родитель:** [FQ-03](../00_thread.md)  
**Дочерние треды:** —  
**Куда переносим решение:** Functional/Screens Specs, file-format / Save design, inventory/product baseline

## Вопрос

Если manual Save получает content, эквивалентный текущей committed Revision, нужна ли новая Revision? Например, пользователь поправил текст, затем вернул исходный вариант и сохраняет.

Это другой случай, чем retry одной операции после timeout: идемпотентный retry уже обязан вернуть прежний результат и не создаёт Revision.

## Уже принято

- Manual autosave не создаёт Revision.
- Save/Apply/Restore — самостоятельные commit paths.
- Apply/Restore исторической версии создают Revision без второго Save.
- При failed/conflicted Save Draft сохраняется.
- Перед Save должны быть разрешены все оставленные attachments (SQ-01).
- В исходном §4.1 правило no-change Save пока помечено [П].

## Варианты

1. **Рекомендация:** manual Save при эквивалентности Current завершает Draft, возвращает NO_CHANGE / существующую Revision и не создаёт новую. committedUpdatedAt и content history не меняются. Успех и consume только этого Draft фиксируются durable, чтобы retry не возвращал удалённый Draft и не создавал Revision.
2. Каждый новый явный manual Save при наличии Draft создаёт отдельную Revision, даже с идентичным content; временные autosave по-прежнему Revision не создают.

## Контекст

Сравниваются title, eventTime с сохранением точности/timezone, нормализованный текст, canonical tag relations и Asset links. Техническая эквивалентность parser/catalog redirects не разрешает silent text rewrite. Отсутствие Current у новой Entry не является no-change: первый успешный Save создаёт первую Revision.

Вариант 1 не распространяется автоматически на Apply/Restore: их согласованная семантика сохраняется. Catalog-only изменение не повод притвориться новым content commit, а реальные новые links/pending tags делают snapshot отличающимся.

## Обсуждение

Codex — (2026-10-18) Рекомендую не добавлять в History две одинаковые версии после manual Save. Если итог совпал с Current, закрываем эквивалентный Draft, показываем saved state и сохраняем durable результат NO_CHANGE с ссылкой на существующую Revision. Это предложение, не принятое требование.

**Нужно от пользователя:** manual Save без фактического изменения content завершает Draft без новой Revision?

пользователь —

**Решение:** —
