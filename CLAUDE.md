# AI Diary — Claude Code project instructions

Read the root [AGENTS.md](AGENTS.md) first. It contains the shared, canonical instructions for all agents.

Project skills are canonical under **skills/**. Claude-specific adapters under **.claude/skills/** must not duplicate or override the canonical rules.

For disputed product questions and architecture decisions, read **.claude/skills/discussion-threads/SKILL.md** before changing a thread. Verify the canonical thread, its lifecycle state, and its claim; never silently resolve a user-owned decision.

The current target architecture and delivery status are in **docs/architecture.md** and **docs/implementation-plan-web-mvp.md**. The old Android/Firebase implementation is a historical prototype and reference, not a required architecture.

## Claude + Codex collaboration

Before taking an agent-team task, read:
- **docs/agent-team/README.md**
- **docs/agent-team/collaboration/README.md**
- **docs/agent-team/orchestration/README.md**
- the specific **docs/agent-team/tasks/active/TASK-NNNN_slug/task.md**

Treat repository task files as canonical and GitHub Issues/PRs as adapters. Preserve substantial decisions and review findings in the task's discussion threads. Never edit **discussion/00_all.md** manually; regenerate it using **python3 scripts/agent-team/build_discussions.py --write** and verify it with **--check**.

Document the impact of every task on current project documentation; update affected source documents in the same PR or explicitly explain why no update is required. Do not rewrite product requirements merely to match an implementation.

Do not auto-merge, deploy, alter live Abacus or Google user data, expose secrets, or claim cloud orchestration has been deployed when only its protocol exists. An Issue does not grant permission to execute; follow the canonical ready state and human approval gates.
