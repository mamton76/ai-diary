# TASK-0001 — Протокол команды Claude + Codex

**ID:** TASK-0001
**Status:** reviewing
**Owner / executor:** Product Owner / ChatGPT (документация)
**Created:** 2026-11-15
**Source:** обсуждение Product Owner с ChatGPT от 2026-11-08 и 2026-11-15
**Related tasks:** —
**External links:** PR — добавляется после создания

## Цель и границы

Зафиксировать переносимый процесс совместной облачной работы Claude и Codex: роли, согласования, состояния, учёт задач, требования к документации, сводки и безопасные ограничения. Создать шаблоны и проверку синхронизации дискуссий.

**Не входит:** реализация/запуск облачного оркестратора, выдача токенов, GitHub event wiring, изменение runtime продукта, тесты реального Google API.

## Канонический контекст

- Корневые AGENTS.md и CLAUDE.md, project skills.
- docs/architecture.md — целевая архитектура продукта; docs/implementation-plan-web-mvp.md — текущий план, а не отчёт о выполнении.
- docs/baseline/ и skills/discussion-threads/SKILL.md — принятые требования и механизм спорных решений.
- [Обсуждения задачи](discussion/00_all.md).

## План и исполнители

1. Создать docs/agent-team/ с collaboration/, orchestration/, tasks/, templates/.
2. Определить task lifecycle, file-first records, формат TASK-NNNN_slug и Documentation Impact gate.
3. Завести discussion/threads и генератор discussion/00_all.md, проверку генератора.
4. Обновить входные инструкции AGENTS.md и CLAUDE.md, шаблоны GitHub.
5. Провести ревью и предложить PR на утверждение.

## Acceptance criteria

- [x] Документация ролей и исполнения разделена на актуальные README и исторические decisions.
- [x] Шаблоны task, result, discussion и GitHub adapter добавлены.
- [x] TASK-0001 хранится в active/ с номером, кратким slug и переносимой историей.
- [x] discussion/00_all.md формируется детерминированно из threads/ и может быть проверен скриптом.
- [x] Скрипт и проверки запущены в GitHub Actions (run 43766624892, successful) и результат отражён в result.md.
- [ ] Независимое ревью проведено, замечания закрыты; PR утверждён.

## Documentation Impact

- **Обновляем:** AGENTS.md, CLAUDE.md; добавляем docs/agent-team/ и .github templates.
- **Проверяем без изменений:** docs/architecture.md, docs/implementation-plan-web-mvp.md и docs/baseline/.
- **Изменение продуктовых требований:** отсутствует; протокол команды не меняет архитектуру AI Diary.

## Безопасность

Не касаться реальных Abacus, Google Drive/Calendar и приватных дневниковых данных; не мержить в master автоматически.

## Открытые вопросы

Какие конкретные авторизованные облачные API использовать для Claude/Codex и каким сервисом маршрутизировать события — отдельная следующая задача, не предпосылка успешности документационного PR.
