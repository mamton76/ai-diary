# AQ-SEARCH-003 — Rebuild semantics

**Источник:** [04-open-questions.md / AQ-SEARCH-003](../../04-open-questions.md#aq-search-003--rebuild-semantics)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation (2026-10-18)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и search index architecture

## Вопрос

Как гарантировать, что derived search index можно удалить, полностью пересобрать из canonical files и проверить его согласованность с файлами?

## Контекст

AQ-SEARCH-001: native FTS выбранной operational DB; асинхронное обновление индекса после successful canonical commit, небольшая eventual consistency задержка допустима. Пользователь уже согласовал rebuild из canonical files, но способ consistency checking ещё не обсуждён.

## Обсуждение

ChatGPT — Предлагаю предусмотреть ручную полную перестройку search index и проверку согласованности: сравнение списка ID и версий/ревизий canonical entries с индексом, без необходимости создавать новый сервис; автоматические проверки можно добавить после MVP.

**Нужно от пользователя:** достаточно ли для первого этапа ручного rebuild и запускаемой по необходимости consistency check по entry IDs/revisions, без постоянной автоматической сверки?

пользователь —

**Решение:** —
