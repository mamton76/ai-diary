# AQ-API-001 — Язык/framework backend

**Источник:** [04-open-questions.md / AQ-API-001](../../04-open-questions.md#aq-api-001--языкframework-backend)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture backend design

## Вопрос

Какой язык и framework выбрать для backend AI Diary с учётом уже принятой архитектуры и того, что проект должен оставаться понятным и поддерживаемым владельцу?

## Кандидаты из source

- Kotlin/Ktor;
- Python/FastAPI;
- TypeScript/Node.

## Критерии

- насколько удобно владельцу читать и исправлять код;
- качество AI-generated implementation;
- Google API ecosystem;
- background/async jobs;
- type safety;
- testability;
- library maturity;
- deployment simplicity;
- долгосрочное сопровождение.

## Уже принятый контекст

- backend/domain API — единая обычная точка работы clients и internal processes с core diary data;
- canonical durable state остаётся в user-owned files;
- backend держит domain rules, leases, revisions, concurrency/reconciliation, integrations и AI workflows;
- Google Drive/Calendar/OAuth являются важными integration points;
- project owner — Android/Kotlin developer;
- hosting/runtime решается отдельно в AQ-API-002 и не должен заранее диктовать язык.

## Обсуждение

**Решение:** —
