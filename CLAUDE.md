# AI Diary — Claude Code project instructions

Сначала прочитай корневой [`AGENTS.md`](AGENTS.md): в нём общие канонические правила для всех агентов, включая текущие источники, язык, правила решений, личные данные в репозитории и совместную работу Claude + Codex.

Канонические project skills лежат в `skills/`. Claude-specific adapters лежат в `.claude/skills/`, но они не должны дублировать или переопределять канонические правила. Этот файл тоже не повторяет правила из `AGENTS.md`, а только указывает на них.

Для open questions и design decisions используй:

```text
.claude/skills/discussion-threads/SKILL.md
```

Для задач команды Claude + Codex — [`docs/agent-team/README.md`](docs/agent-team/README.md) и конкретный `docs/agent-team/tasks/active/TASK-NNNN_slug/task.md`.
