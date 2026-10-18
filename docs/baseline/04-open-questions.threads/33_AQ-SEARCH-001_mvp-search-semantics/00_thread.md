# AQ-SEARCH-001 — MVP search semantics

**Источник:** [04-open-questions.md / AQ-SEARCH-001](../../04-open-questions.md#aq-search-001--mvp-search-semantics)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и search/index architecture

## Вопрос

Какая функциональность MVP search нужна по title/body, tags, date range, source, status? Нужны ли semantic/vector search сейчас?

## Контекст

Canonical user-owned files — source of truth. Поисковые индексы — перестраиваемые производные. Background updates через очередь; read/search queries непосредственно через API. Для MVP пользователь хочет начать с простого поиска, semantic/AI search отложить. Стандартные технические возможности: SQLite FTS5 (https://www.sqlite.org/fts5.html), PostgreSQL Full Text Search (https://www.postgresql.org/docs/current/textsearch.html), Java Apache Lucene. Выбор реализации должен зависеть от уже выбранной operational database, а не создавать дополнительную службу.

## Обсуждение

пользователь — «давай начнем с простого поиска - а потмо уже будем думать про какой-т оеще. и вообще - мы можем использовать какие-то стандартные либы механизмы для этого?»

ChatGPT — Поддерживаю MVP без semantic search. Для title/body возможно использовать нативный full-text search в существующей БД (например, SQLite FTS5 или PostgreSQL FTS), плюс обычные индексированные SQL-фильтры по tags, date range, source, status. Индекс остаётся перестраиваемым из canonical files. Стоит заранее проверить русский поиск и регистронезависимость; нечёткий/синонимический поиск не обещать.

**Нужно от пользователя:** достаточно ли для MVP сочетания простого полнотекстового поиска title/body и фильтров по tags, date, source, status, оставив смысловой поиск на потом?

пользователь — «норм»

ChatGPT — Подтверждено: в поисковом web slice достаточно простого текстового поиска без semantic/vector features и фильтров по тегам, датам, источнику и статусу. Использовать существующий DB search/index mechanism (например, встроенный FTS в выбранной БД), не отдельный сервер. Индекс rebuildable из canonical files. Из прежнего roadmap сохраняется граница: search не обязателен в самом первом files-only MVP, относится к следующему web slice.

**Решение:** [принято] (2026-10-18) Simple title/body full-text search с регистронезависимостью плюс filters tags, date range, source, status; semantic/vector search, fuzzy/synonyms и гарантии морфологии откладываются. Использовать стандартные средства FTS в выбранной операционной БД, не писать собственный engine и не разворачивать отдельный поисковый сервис. Search index — derived/rebuildable; не блокирует самый первый files-only MVP.
