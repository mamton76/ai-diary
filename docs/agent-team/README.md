# AI Diary — команда разработки Claude + Codex

**Статус:** протокол v0.1, предлагается к утверждению в PR. Документ описывает желаемый процесс, а не утверждает, что облачная автоматизация уже подключена.

## Принципы

- **Repository-first:** существенные задания, решения и результаты хранятся в переносимых Markdown-файлах репозитория.
- **GitHub-as-adapter:** Issues, PR, comments, Actions — рабочая интеграция, а не единственный источник истины. Переход на другую платформу не должен лишать проект истории.
- **Documentation-as-deliverable:** каждая задача включает проверку влияния на документацию. Без неё задача не завершена.
- **Human control:** агенты вправе планировать, писать, тестировать и рецензировать, но не переопределять принятые продуктовые решения и не выполнять merge/deploy без разрешения.
- **No live data:** агенты и тесты не работают с реальным дневником, Abacus, живыми Google Drive/Calendar и пользовательскими секретами.

## Где что живёт

| Назначение | Источник |
|---|---|
| Текущие правила сотрудничества | [collaboration/README.md](collaboration/README.md) |
| Текущий протокол исполнения | [orchestration/README.md](orchestration/README.md) |
| История решений о команде | collaboration/decisions/ и orchestration/decisions/ |
| Реестр и жизненный цикл задач | [tasks/README.md](tasks/README.md) |
| Активные и завершённые задачи | tasks/active/ и tasks/completed/ |
| Шаблоны переносимых записей | [templates/](templates/) |
| Публикация презентаций | [publishing/README.md](publishing/README.md) — переносимый HTML, allowlist и настройки preview |
| Продуктовые требования | [../baseline/](../baseline/) |
| Текущая архитектура продукта | [../architecture.md](../architecture.md) |
| Реализация Web/API MVP | [../implementation-plan-web-mvp.md](../implementation-plan-web-mvp.md) |

Детальные обсуждения по задаче хранятся в её **discussion/threads/**. Файл **discussion/00_all.md** — автоматически собранная конкатенация, а не отдельное место редактирования.

## Перед работой агента

1. Прочитать корневой AGENTS.md, а для Claude — ещё CLAUDE.md.
2. Прочитать текущие collaboration/README.md, orchestration/README.md и task.md.
3. Найти актуальные source-документы задачи; отличать принятое требование от draft, а реализованное от запланированного.
4. Если возник проектный спорный вопрос — следовать [skills/discussion-threads/SKILL.md](../../skills/discussion-threads/SKILL.md) и уже существующим canonical threads.
5. Проверить Documentation Impact при планировании, ревью и завершении задачи.

## Статус реализации автоматизации

В этом PR создаются **документы, шаблоны и проверка конкатенации**. Запуск Claude Cloud, Codex Cloud, синхронизация GitHub Issues и автоматический возврат ревью в исполнение **не реализованы**. Их подключение требует отдельной задачи, проверки доступных API/авторизации и безопасности. Не выдавать описанный ниже workflow за запущенный сервис.

Начальная задача, фиксирующая эту договорённость: [TASK-0001_agent-team-protocol](tasks/active/TASK-0001_agent-team-protocol/task.md).
