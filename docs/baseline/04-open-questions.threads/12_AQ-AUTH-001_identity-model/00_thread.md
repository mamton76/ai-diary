# AQ-AUTH-001 — Identity model

**Источник:** [04-open-questions.md / AQ-AUTH-001](../../04-open-questions.md#aq-auth-001--identity-model)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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

### Сводка 2 — решение

Identity model должна быть независима от конкретного login provider. Внутри AI Diary существует собственный стабильный internal user/account ID, а внешние login identities привязываются к нему отдельно.

Google — естественный первый login method для MVP, но data model не должна делать Google account ID единственным user identity. Позже можно добавить другие способы входа (например Apple, email/passkey) без миграции основной user model.

Конкретный auth service/framework (Firebase Auth, direct OIDC, Auth0/Supabase и т. п.) сейчас не фиксируется; его выбираем вместе с backend/hosting.

**Решение:** [принято] Internal user identity отделена от login providers; Google — первый login method, но не единственно возможный. Конкретная auth implementation откладывается до выбора backend/hosting.
