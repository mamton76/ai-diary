# AQ-API-006 — Monorepo structure

**Источник:** [04-open-questions.md / AQ-API-006](../../04-open-questions.md#aq-api-006--monorepo-структура)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture repository/build design

## Вопрос

Хранить web/frontend, backend и docs в одном репозитории или разделить их? Как организовать сборки и границы компонентов?

## Варианты

1. Раздельные репозитории для frontend/backend.
2. Один monorepo с независимыми builds и общей документацией/контрактом API.

## Контекст

Существующий репозиторий mamton76/ai-diary уже содержит требования и реализацию. Backend Kotlin/Ktor и REST/OpenAPI contract-first приняты ранее; старый Android код — historical prototype, не активная обязательная часть MVP. Не требуется заранее привязывать frontend package manager к Gradle или вводить общую систему релизов.

## Обсуждение

ChatGPT — Рекомендую один репозиторий с самостоятельными сборками frontend и backend и разделёнными каталогами (например, web/, backend/, docs/). OpenAPI specification — разделяемый контракт, но не повод делать общий build root. Android можно добавить позднее по потребности. CI и release boundaries должны позволять изменять/развёртывать компоненты отдельно.

пользователь — «норм»

**Решение:** [принято] (2026-10-18) Сохранить один репозиторий (monorepo) для web, backend и docs. Frontend и Kotlin/Ktor backend — самостоятельные builds/toolchains; OpenAPI contract версионируется в этом же repo. Не вводить сейчас общий Gradle root для web, обязательный shared runtime code, Android build, разделение по нескольким repo или сложную единую release систему. CI/deploy можно настраивать отдельно на компонент по мере необходимости; конкретные directory/tooling details уточняются при реализации.
