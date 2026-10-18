# Функциональное ТЗ — индекс обсуждений

**Source:** [Функциональное ТЗ](../AI-Diary-Functional-Spec-v0.1.md)  
**Workflow:** [discussion-threads](../../../skills/discussion-threads/SKILL.md)

Один вопрос — один canonical thread. FQ-01 хранится в ранее созданном дочернем узле PQ-004; здесь только ссылка, не параллельная история.

| № | ID | Вопрос | Статус | Lifecycle | Claim | Ведёт | Тред | Куда переносим решение |
|---|---|---|---|---|---|---|---|---|
| — | FQ-01 | Revision/Save/Apply/Restore и AI auto-apply | решён | resolved | none | — | [PQ-004/FQ-01](../04-open-questions.threads/04_PQ-004_raw-revisions-ux/01_FQ-01_revision-commit-actions/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 1 | FQ-02 | Merge tags / immutable revisions | решён | resolved | none | — | [Тред](01_FQ-02_tag-merge/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 2 | FQ-03 | Надёжный Save / partial failure / retry | ждём исследования | paused | active | Codex — текущий диалог требований AI Diary | [Тред](02_FQ-03_reliable-save/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 2.1 | FQ-03/SQ-01 | Save при незавершённом upload / attachments в Draft | решён | resolved | none | — | [Тред](02_FQ-03_reliable-save/01_SQ-01_upload-before-save/00_thread.md) | Functional/Screens Specs, file-format / Save design |
| 2.2 | FQ-03/SQ-02 | Manual Save без изменения content | решён | resolved | none | — | [Тред](02_FQ-03_reliable-save/02_SQ-02_no-change-save/00_thread.md) | Functional/Screens Specs, file-format / Save design |
| 3 | FQ-04 | Tag aliases / unlink text / normalizer | ждём исследования | paused | active | Codex — текущий диалог требований AI Diary | [Тред](03_FQ-04_tag-aliases/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 4 | FQ-08 (подпункт) | Готовые Asset после Discard / unlink | решён | resolved | none | — | [Тред](04_FQ-08_discard-uploads/00_thread.md) | Functional/Screens Specs, file-format / Save design |
| 4.1 | FQ-08/SQ-01 | Restore Entry из Trash → ACTIVE | решён | resolved | none | — | [Тред](04_FQ-08_discard-uploads/01_SQ-01_restore-lifecycle/00_thread.md) | Functional/Screens Specs, file-format / Save design |
| 5 | FQ-05 (подпункт) | Overlap интервальной записи с периодом фильтра | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 6 | FQ-06 | Updated sort при Draft | ждём пользователя | in_discussion | active | Codex — текущий диалог требований AI Diary | [Тред](06_FQ-06_updated-sort/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
