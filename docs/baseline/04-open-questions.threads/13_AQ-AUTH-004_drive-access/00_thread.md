# AQ-AUTH-004 — Доступ backend к user-owned Drive

**Источник:** [04-open-questions.md / AQ-AUTH-004](../../04-open-questions.md#aq-auth-004--доступ-backend-к-user-owned-drive)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Как backend получает доступ к canonical data в Google Drive каждого пользователя?

## Варианты

- backend действует от имени пользователя по OAuth token;
- service account + shared folder;
- другой delegated/access pattern.

## Контекст

Уже решено:
- AI Diary — multi-user application;
- у каждого пользователя свои изолированные данные;
- internal user identity отделена от login provider;
- Google login и Google API permissions — разные контракты.

## Обсуждение

### Сводка 1 — старт

Нужно выбрать high-level access model. Детали scopes, refresh-token storage, revocation и incremental consent относятся к AQ-AUTH-002.

**Решение:** —
