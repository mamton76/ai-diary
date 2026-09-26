# AI Diary — Claude Code project instructions

Сначала прочитай корневой `AGENTS.md`.

Канонические project skills лежат в `skills/`. Claude-specific adapters лежат в `.claude/skills/`, но они не должны дублировать или переопределять канонические правила.

Для open questions и design decisions используй:

```text
.claude/skills/discussion-threads/SKILL.md
```

До утверждения новой архитектуры старый Android/Firebase код рассматривай как prototype и источник доменных идей, а не как автоматически обязательную основу новой системы.
