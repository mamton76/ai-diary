# AQ-AUTH-001 — Identity model

**Источник:** [04-open-questions.md / AQ-AUTH-001](../../04-open-questions.md#aq-auth-001--identity-model)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Как AI Diary аутентифицирует пользователя приложения?

## Варианты

- direct Google OIDC/OAuth;
- Firebase Auth поверх Google sign-in;
- другой auth middleware/provider.

## Контекст

Уже решено, что AI Diary — multi-user application с изолированными данными каждого пользователя. Login/identity нужно отделять от разрешений на Google Drive/Calendar: это связанные, но разные контракты.

## Обсуждение

### Сводка 1 — старт

Сначала нужно выбрать identity layer. После этого отдельно решается AQ-AUTH-004 — как backend получает доступ к user-owned Drive.

**Решение:** —
