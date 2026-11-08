# AQ-SEARCH-002 — Semantic search timing

**Источник:** [04-open-questions.md / AQ-SEARCH-002](../../04-open-questions.md#aq-search-002--semantic-search-timing)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и search architecture

## Вопрос

Когда вводить semantic retrieval/embeddings для cross-entry AI?

## Обсуждение

пользователь — «давай начнем с простого поиска - а потмо уже будем думать про какой-т оеще. и вообще - мы можем использовать какие-то стандартные либы механизмы для этого?»

ChatGPT — Рекомендован обычный полнотекстовый поиск и фильтры без semantic/vector search в MVP.

пользователь — «норм»

пользователь — «давай - смысловой - на будущее плиз»

ChatGPT — Смысловой поиск отложен на будущее. Сохраняем архитектурную возможность подключить semantic retrieval позже, но не внедряем embeddings, vector DB и связанные pipelines в MVP.

**Решение:** [принято] (2026-10-18) Semantic search/retrieval — будущий этап, вне MVP; на текущем этапе только обычный поиск и фильтры. Не разворачивать vector DB и embedding pipeline сейчас.
