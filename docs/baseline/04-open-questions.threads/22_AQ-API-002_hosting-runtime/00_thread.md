# AQ-API-002 — Hosting/runtime

**Источник:** [04-open-questions.md / AQ-API-002](../../04-open-questions.md#aq-api-002--hostingruntime)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture deployment/runtime design

## Вопрос

Где и как запускать backend AI Diary в первом web/backend MVP?

## Контекст

Текущий source отмечает Cloud Run как сильного кандидата из-за container model и scale-to-zero, но выбор ещё не зафиксирован.

Сравниваем по:
- стоимости;
- cold starts;
- background execution;
- scheduler/queue integration;
- Google OAuth/Drive convenience;
- logs;
- deployment complexity.

Нужно сначала решить не конкретный vendor feature-list, а какой operational profile нам реально нужен: always-on server или request-driven container/runtime с отдельными jobs/background tasks.

**Решение:** —
