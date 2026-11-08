# AQ-DATA-008 — Migration со старого Firebase/Room

**Источник:** [04-open-questions.md / AQ-DATA-008](../../04-open-questions.md#aq-data-008--migration-со-старого-firebaseroom)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md

## Вопрос

Нужен ли migration tooling со старого Android/Firebase/Room проекта в новую AI Diary architecture?

## Контекст

Ранее в PQ-008 уже зафиксировано:
- старый Android/Firebase codebase — historical prototype/reference;
- новая web/backend architecture от него не зависит;
- уникальных ценных пользовательских данных, требующих переноса, нет;
- отдельное migration tooling сейчас не требуется.

## Решение

Отдельную migration со старого Firebase/Room **не делаем**.

AQ-DATA-008 закрыт как superseded / answered by PQ-008 и LEGACY-002. Если позже неожиданно обнаружатся уникальные данные, это будет новый scoped import/migration task, а не сохранение этого требования как постоянного архитектурного обязательства.
