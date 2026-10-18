# FQ-03 / SQ-02 — Manual Save без изменения content

**Источник:** [Функциональное ТЗ, §4.1](../../../AI-Diary-Functional-Spec-v0.1.md#41-контракт-операций)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

пользователь — (2026-10-18) «да норм - только как понять что ничего не поменялось ? сравнивать?»

Codex — (2026-10-18) Принят вариант 1. Да: сравнивать итоговый content snapshot с актуальной Current после обычных validation/base/lease checks. Ни fact autosave, ни новый Draft timestamp сами по себе не считаются изменением. Для первой реализации достаточно прямого сравнения content-полей; hashing не обязателен.

**Техническая конкретизация:** Перед сравнением проверяются актуальные lease/base, готовность вложений и выполняется принятая нормализация mentions. Сравниваются title и итоговый text точно, EventTimeRange со всеми сохранёнными датами/временем/точностью/timezone, набор canonical tagIds после разрешения redirects и набор assetIds. Порядок IDs не является изменением содержимого в текущей версии без ручной сортировки вложений. Текстовые пробелы, переносы строк и регистр не игнорируются; case-insensitive lookup тегов не означает case-insensitive сравнение текста. Служебные draftId/draftVersion/updatedAt, session/lease/operation metadata, file paths и Drive IDs в content equality не участвуют. Сами media bytes заново не сравниваются: Entry меняет ссылки по assetId, а Asset metadata/original имеют отдельный контракт.

Codex — Решение перенесено в source-документы и Save/file-format проект. Apply/Restore не переоткрываются. Физический Drive protocol остаётся отдельным техническим gate FQ-03.

**Решение:** [принято] (2026-10-18) Manual Save, при котором итоговое сохраняемое content совпадает с текущей committed Revision, завершает эквивалентный Draft без новой Revision. Возвращается NO_CHANGE со ссылкой на существующую Revision; committedUpdatedAt и content History не меняются. Consume именно этого Draft и результат операции фиксируются durable с обычными ownership/base/idempotency checks. У новой Entry без Current первый успешный Save создаёт первую Revision. Согласованное создание Revision при Apply/Restore сохраняется.
