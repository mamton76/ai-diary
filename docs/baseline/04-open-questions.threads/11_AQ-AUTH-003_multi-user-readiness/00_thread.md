# AQ-AUTH-003 — Single-user vs multi-user readiness

**Источник:** [04-open-questions.md / AQ-AUTH-003](../../04-open-questions.md#aq-auth-003--single-user-vs-multi-user-readiness)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Должен ли первый production быть только single-user deployment, или AI Diary с самого начала считается multi-user приложением с раздельными данными каждого пользователя?

## Обсуждение

### Сводка 1 — решение

AI Diary с самого начала считается **multi-user application**: один backend/application может обслуживать нескольких авторизованных пользователей, и у каждого пользователя свой логический дневник и собственные данные.

Это не означает, что `ownerId` обязан дублироваться внутри каждого canonical diary file. Если canonical data лежат в user-owned storage (например, Google Drive), ownership может задаваться authenticated user context и самим storage boundary.

Зато любой shared operational/server-side state должен быть user-scoped: drafts, leases, jobs, proposals, indexes/cache, OAuth tokens, settings, run records и т. п.

Sharing между пользователями и сложные ACL остаются вне MVP и не следуют автоматически из multi-user readiness.

**Решение:** [принято] AI Diary проектируется как multi-user application с изолированными данными каждого пользователя; authenticated user context обязателен для backend/operational state, но ownerId не требуется без необходимости внутри каждого canonical file.
