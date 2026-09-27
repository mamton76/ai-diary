# AQ-API-001 — Язык/framework backend

**Источник:** [04-open-questions.md / AQ-API-001](../../04-open-questions.md#aq-api-001--языкframework-backend)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

### Сводка — основной backend и специализированный Python

В качестве основного backend stack выбран **Kotlin + Ktor**: он лучше соответствует навыкам владельца проекта и хорошо подходит для domain-heavy core с Entry/Revision/Proposal/Asset semantics, leases, optimistic concurrency, reconciliation и storage abstractions.

Python не исключается из архитектуры. Если позже появляются задачи, где Python даёт явное преимущество (AI/ML, embeddings, media/data processing, специализированные batch jobs), допускаются отдельные Python workers/services/jobs. Они не должны становиться независимым writer canonical diary state: применение результатов к core data проходит через backend/domain rules.

Для MVP не вводится второй runtime без конкретной необходимости. Kotlin/Ktor — default core backend; Python добавляется только под обоснованный use case. Оба стека совместимы с выбранным направлением Cloud Run/container deployment.

**Решение:** [принято] (2026-09-28) Основной backend AI Diary — Kotlin/Ktor. Python допускается позднее для специализированных workers/jobs, когда это оправдано конкретной задачей; в MVP второй runtime не вводится без необходимости.
