# AQ-WEB-006 — ChatGPT Sites или обычный web-проект?

**Источник:** [04-open-questions.md / AQ-WEB-006](../../04-open-questions.md#aq-web-006--chatgpt-sites-или-обычный-web-проект)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Claude — уточнение требований (ветка `docs/requirements-sync`)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Связанные вопросы:** [AQ-WEB-001 — frontend stack](../59_AQ-WEB-001_frontend-stack/00_thread.md)  
**Куда переносим решение:** 02-requirements-inventory.md / architecture.md / implementation-plan-web-mvp.md

## Вопрос

Какую роль ChatGPT Sites играет в проекте: disposable UX prototype на mock data, ранний frontend поверх backend API, admin/debug UI, production frontend или не использовать?

## Варианты

1. **Не использовать.** Сразу обычный web-клиент в репозитории.
2. **Только disposable UX-прототип** на вымышленных данных, без доступа к API и реальному дневнику.
3. **Ранний frontend поверх backend API.**
4. **Production frontend.**

## Контекст

- Рабочая гипотеза 2026-09-26 (source): Sites подходит для быстрого UI/UX prototype, но production runtime выбирать не следует до проверки.
- [PQ-018](../56_PQ-018_portfolio-goal/00_thread.md): публичный репозиторий и демо-сайт — часть портфолио. Значит, нужен код в репозитории.
- Критерии source: source-code ownership и GitHub workflow, совместная поддержка кода ChatGPT/Codex и Claude, sensitive diary data, OAuth/Drive.
- [PRIV-010…012](../49_AQ-SEC-001_content-protection/00_thread.md): реальный дневник не должен попадать в сторонние среды без необходимости.

## Обсуждение

Claude — Рекомендую **вариант 1, с допуском варианта 2**.
- Варианты 3 и 4 противоречат PQ-018 и критериям source: код должен жить в репозитории, а реальные данные дневника не должны проходить через ещё одну стороннюю платформу.
- Вариант 2 безопасен и может быть полезен для быстрой проверки UX на вымышленных данных, но он не обязателен и не становится частью продукта.

**Нужно от пользователя:** подтвердить «обычный web-клиент в репозитории; Sites — максимум как одноразовый UX-прототип на вымышленных данных» или выбрать иначе.

пользователь —

**Решение:** —
