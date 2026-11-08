# AQ-WEB-001 — Frontend stack

**Источник:** [04-open-questions.md / AQ-WEB-001](../../04-open-questions.md#aq-web-001--frontend-stack)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Claude — уточнение требований (ветка `docs/requirements-sync`)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Связанные вопросы:** [AQ-WEB-006 — роль ChatGPT Sites](../60_AQ-WEB-006_sites-role/00_thread.md)  
**Куда переносим решение:** 02-requirements-inventory.md (WEB-007) / architecture.md / implementation-plan-web-mvp.md

## Вопрос

На чём писать web-клиент? Исходная формулировка: «React/TypeScript — кандидат, не решение». Критерии: responsive UI, ecosystem, Markdown/editor support, auth integration, AI-agent coding quality, testing, deployment, maintainability.

## Варианты

1. **React + TypeScript + Vite (SPA).** Статическая сборка, клиент к REST/OpenAPI API.
2. **Next.js (React с серверным рендерингом).**
3. **Kotlin/JS или Compose for Web** — один язык с backend.
4. **Svelte/SvelteKit или Vue.**

## Контекст

- Backend — Kotlin/Ktor, REST + JSON с OpenAPI ([AQ-API-001](../26_AQ-API-001_backend-language-framework/00_thread.md), [AQ-API-003](../27_AQ-API-003_api-style/00_thread.md)). Из OpenAPI можно генерировать типизированный TypeScript-клиент.
- Редактор: Markdown с кнопками форматирования ([AQ-WEB-003](../43_AQ-WEB-003_editor-semantics/00_thread.md)). Зрелые редакторы (TipTap/ProseMirror, CodeMirror, Milkdown) лучше всего поддержаны в React.
- Код будут писать Codex и Claude ([PQ-018](../56_PQ-018_portfolio-goal/00_thread.md)): в React + TypeScript у агентов больше всего примеров.
- Продукт приватный, SEO не нужен; обновления статусов через SSE (API-009).
- Портфолио (PQ-018): публичный репозиторий и демо-сайт.

## Обсуждение

Claude — Рекомендую **вариант 1: React + TypeScript + Vite, SPA**.
- Серверный рендеринг (вариант 2) нужен для SEO и первых экранов публичных страниц. Для приватного дневника за Google login он даёт в основном лишний серверный слой.
- Kotlin для frontend (вариант 3) объединяет язык с backend, но ecosystem редакторов и качество кода агентов там заметно слабее.
- Svelte/Vue (вариант 4) — нормальный выбор, но преимуществ перед React для этого проекта нет, а агентам проще с React.

Хостинг (WEB-008) из этого почти следует: статическую сборку можно отдавать с того же Cloud Run или со статического хостинга Google. Это решается при реализации.

**Нужно от пользователя:** подтвердить React + TypeScript + Vite SPA или выбрать другой вариант.

пользователь —

**Решение:** —
