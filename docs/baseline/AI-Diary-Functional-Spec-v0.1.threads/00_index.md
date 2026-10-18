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
| 6 | FQ-06 (подпункт) | Updated sort учитывает Draft | решён | resolved | none | — | [Тред](06_FQ-06_updated-sort/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 6.1 | FQ-06/SQ-01 | Lifecycle-охват Drafts / Needs attention на Home | решён | resolved | none | — | [Тред](06_FQ-06_updated-sort/01_SQ-01_home-queue-scope/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 6.2 | FQ-06/SQ-02 | Lifecycle-охват Total entries на Home | решён | resolved | none | — | [Тред](06_FQ-06_updated-sort/02_SQ-02_total-entries-scope/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 6.3 | FQ-06/SQ-03 | Lifecycle периодных статистических counters Home | решён | resolved | none | — | [Тред](06_FQ-06_updated-sort/03_SQ-03_period-counter-scope/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 5.1 | FQ-05/SQ-01 | Timezone границы rolling days на Home | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/01_SQ-01_rolling-day-timezone/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 5.2 | FQ-05/SQ-02 | Время события и отображение в пользовательской зоне | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/02_SQ-02_event-time-display/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 5.3 | FQ-05/SQ-03 | Дата события при группировании Calendar | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/03_SQ-03_calendar-event-date/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 5.4 | FQ-05/SQ-04 | EventTimeRange записи без окончания | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/04_SQ-04_missing-event-end/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 5.5 | FQ-05/SQ-05 | Последний день date-only интервала | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/05_SQ-05_date-only-end-inclusion/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 5.6 | FQ-05/SQ-06 | Date-only запись в фильтре по часам | решён | resolved | none | — | [Тред](05_FQ-05_period-overlap/06_SQ-06_date-only-clock-filter/00_thread.md) | Functional/Screens Specs, file-format, inventory/product baseline |
| 6.4 | FQ-06/SQ-04 | Ошибка AI / мягкий статус работы / счётчик Needs attention | решён | resolved | none | — | [Тред](06_FQ-06_updated-sort/04_SQ-04_failed-ai-attention/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 6.5 | FQ-06/SQ-05 | Убрать конкретную ошибку AI из внимания | решён | resolved | none | — | [Тред](06_FQ-06_updated-sort/05_SQ-05_dismiss-ai-error/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 7 | FQ-07 (подпункт) | Исход complex proposal после частичного Apply | решён | resolved | none | — | [Тред](07_FQ-07_partial-proposal/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 7.1 | FQ-07/SQ-01 | Сохранить прогресс незавершённого review | решён | resolved | none | — | [Тред](07_FQ-07_partial-proposal/01_SQ-01_review-draft-resume/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
| 7.2 | FQ-07/SQ-02 | Обычный повтор после failed AI Run | ждём пользователя | in_discussion | active | Codex — текущий диалог требований AI Diary | [Тред](07_FQ-07_partial-proposal/02_SQ-02_failed-run-retry/00_thread.md) | Functional/Screens Specs, inventory/product baseline |
