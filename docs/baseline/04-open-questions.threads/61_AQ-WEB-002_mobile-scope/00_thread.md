# AQ-WEB-002 — Feature parity на телефоне

**Источник:** [04-open-questions.md / AQ-WEB-002](../../04-open-questions.md#aq-web-002--feature-parity-на-телефоне)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Claude — уточнение требований (ветка `docs/requirements-sync`)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** 03-product-baseline.md §12.2 / §22.1 / AI-Diary-Screens-Spec-v0.1.md / 02-requirements-inventory.md (WEB-002, WEB-009)

## Вопрос

Какой web scope обязателен на телефоне? Source: «Вероятно обязательно: browse, read, capture/create, basic edit, search/filter. Можно оставить desktop-first: revision diff, bulk operations, complex AI workflow configuration, debugging/admin».

## Варианты

1. **Полный паритет** всех экранов.
2. **Паритет по этапам с desktop-first исключениями:** всё из E0, первой версии, E1 и E2 работает на телефоне; desktop-first остаются только перечисленные сложные экраны.
3. **Телефон только для чтения и поиска;** правка — на desktop.

## Контекст

- WEB-002: web адаптируется под desktop и phone; WEB-009: на телефоне допустим упрощённый layout, но базовый сценарий не должен ломаться.
- Screens Spec §3: E1 уже включает «mobile browse/read/search».
- [PQ-012](../47_PQ-012_mvp-stage-scope/00_thread.md) явно оставил объём правки на телефоне этому вопросу.
- [UI-Q06](../../AI-Diary-Screens-Spec-v0.1.threads/04_UI-Q06_mobile-proposal-review/00_thread.md): AI review на телефоне уже настроен (два режима).

## Обсуждение

Claude — Рекомендую **вариант 2**:
- **на телефоне работает:** чтение (E0), лёгкая правка (первая версия), поиск и Обзор (E1), полный редактор с созданием записи и прикреплением фото (E2), просмотр истории и Restore, AI review по UI-Q06;
- **desktop-first:** подробное сравнение версий бок о бок (на телефоне — упрощённое, по одной версии), workflow editor, массовые операции, debug/admin.

Создание записи и прикрепление фото с телефона особенно важны: это основной сценарий захвата в дороге (OFF-001).

**Нужно от пользователя:** подтвердить вариант 2 со списком desktop-first или поменять список.

пользователь —

**Решение:** —
