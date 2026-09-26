# AI Diary — индекс обсуждений открытых вопросов

**Source:** [`../04-open-questions.md`](../04-open-questions.md)  
**Workflow:** [`../../../skills/discussion-threads/SKILL.md`](../../../skills/discussion-threads/SKILL.md)

Эта папка содержит только те вопросы из `04-open-questions.md`, которые **реально начали обсуждаться**.

Треды создаются лениво. Отсутствие папки для вопроса означает только «детальное обсуждение ещё не заведено», а не «вопрос решён».

## Активные треды

| № | ID | Вопрос | Статус | Чей ход | Тред | Куда переносим решение |
|---|---|---|---|---|---|---|
| 1 | PQ-001 | Что считается canonical source of truth? | решён | — | [тред](01_PQ-001_source-of-truth/00_thread.md) | 03-product-baseline.md / 02-requirements-inventory.md |

| 2 | PQ-003 | Какой minimum viable web? | решён | — | [тред](02_PQ-003_minimum-viable-web/00_thread.md) | 03-product-baseline.md / 02-requirements-inventory.md |
| 3 | PQ-002 | Насколько обязателен full offline-first? | обсуждаем | совместное обсуждение | [тред](03_PQ-002_offline-first/00_thread.md) | 03-product-baseline.md / 02-requirements-inventory.md |

| 4 | PQ-004 | Нужно ли сразу показывать raw/revisions? | обсуждаем | совместное обсуждение | [тред](04_PQ-004_raw-revisions-ux/00_thread.md) | 03-product-baseline.md / 02-requirements-inventory.md |

| 5 | PQ-005 | Насколько AI автоматичен? | обсуждаем | совместное обсуждение | [тред](05_PQ-005_ai-automation-policy/00_thread.md) | 03-product-baseline.md / 02-requirements-inventory.md |

## Структура узла

```text
NN_<QUESTION-ID>_<slug>/
  00_thread.md

  NN_SQ-XX_<child-slug>/       # только если вопрос реально раскололся
    00_thread.md
```

Шаблон нового узла лежит в [`_template/00_thread.md`](_template/00_thread.md).

## Важно

- Один выбор — один канонический тред.
- Решения не принимаются от имени пользователя без явного делегирования.
- После решения обновляется source-документ.
- Тред сохраняет rationale и историю пересмотров.
