# PQ-006 — Насколько пользователь выбирает LLM provider/model?

**Источник:** [04-open-questions.md / PQ-006](../../04-open-questions.md#pq-006--насколько-пользователь-выбирает-llm-providermodel)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Насколько выбор LLM provider/model должен быть виден и управляем пользователем?

## Варианты

1. **System choice** — система сама выбирает provider/model.
2. **Global preference** — пользователь задаёт один preferred provider/model.
3. **Per-workflow choice** — provider/model выбирается отдельно для workflow.
4. **Advanced compare mode** — пользователь может запускать/сравнивать несколько моделей.

## Контекст

Архитектурно multi-provider support желательна независимо от того, насколько эта настройка видна в обычном UX.

Это голосовой тред: разговор не стенографируется. Смысловая сводка сохраняется по команде пользователя, при паузе или завершении обсуждения.

## Обсуждение

### Сводка 1 — старт обсуждения

PQ-006 был взят в активное обсуждение, но содержательное обсуждение не началось.

### Сводка 2 — release

Пользователь решил переключиться на AQ-DATA-010. Claim снят; PQ-006 снова свободен.

### Сводка 3 — выбор модели

Согласовано:
- пользователь выбирает модель; provider определяется моделью;
- приоритет: task override → workflow preference → global user preference → system default;
- global user preference — основной сценарий;
- silent fallback на другую модель/provider при недоступности preferred model не делаем без явного согласия пользователя;
- детали retry/deprecation/fallback UX относятся к implementation policy.

**Решение:** [принято] Иерархия выбора модели: task override → workflow preference → global user preference → system default. Выбор модели определяет provider; тихий fallback на другую модель/provider не допускается.
