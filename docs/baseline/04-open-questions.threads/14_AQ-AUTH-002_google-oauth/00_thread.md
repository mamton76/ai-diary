# AQ-AUTH-002 — Drive/Calendar OAuth

**Источник:** [04-open-questions.md / AQ-AUTH-002](../../04-open-questions.md#aq-auth-002--drivecalendar-oauth)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Как AI Diary запрашивает и управляет Google API permissions для Drive/Calendar?

## Контекст

Уже решено:
- login identity отделена от Google API permissions;
- backend получает доступ к user-owned Drive от имени пользователя через OAuth;
- приложение multi-user, access state user-scoped.

Нужно определить:
- scopes;
- incremental consent;
- refresh-token storage;
- revocation;
- account switch;
- expired permissions / re-auth UX.

## Обсуждение

### Сводка 1 — incremental consent

Согласовано: Google API permissions запрашиваются **по мере необходимости**, а не единым пакетом при первом login.

- login/authentication — отдельно;
- Drive consent — когда пользователь подключает/начинает использовать diary storage;
- Calendar consent — только если пользователь включает Calendar inbox/timeline или другую Calendar feature.

Цель — не просить permissions раньше, чем они реально нужны, и держать Drive/Calendar integrations независимыми.

**Решение:** пока частичное; остальные OAuth policy details обсуждаются дальше.
