# AQ-AUTH-002 — Drive/Calendar OAuth

**Источник:** [04-open-questions.md / AQ-AUTH-002](../../04-open-questions.md#aq-auth-002--drivecalendar-oauth)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

### Сводка 2 — scope details deferred

Для MVP уже существует рабочий access workaround, поэтому точная Drive scope/picker/folder-access схема не должна блокировать архитектуру. Предпочтение остаётся за минимально необходимыми permissions и отсутствием full-Drive access, если это можно реализовать разумно.

Точные scopes, folder access mechanics, refresh-token storage, revocation, account switch и re-auth UX считаются implementation/security details и определяются при техническом spike/реализации.

**Решение:** [принято] OAuth permissions выдаются incremental/per-feature; Drive/Calendar consent разделены. High-level contract зафиксирован, а точная scope/token/re-auth mechanics не блокирует MVP и откладывается до implementation.
