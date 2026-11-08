# FQ-08/SQ-04 — Retention of Asset Trash

**Источник:** [Функциональное ТЗ, AST-04 / FQ-08](../../../AI-Diary-Functional-Spec-v0.1.md)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** ChatGPT  
**Режим фиксации:** written-turns  
**Родитель:** [FQ-08 — attachments after Discard](../00_thread.md)  
**Дочерние треды:** —  
**Куда переносим решение:** Functional/Screens Specs и inventory

## Вопрос

Нужно ли автоматически окончательно удалять Asset из Asset Trash по истечении некоторого срока или хранить удалённые материалы, пока пользователь сам не инициирует необратимое удаление?

Важно: вопрос **только о готовых Asset, уже помещённых в Asset Trash**. Он не определяет cleanup незавершённых upload/staging данных, orphaned uploads, late callbacks, preview/cache, backup retention и технические детали физического удаления.

## Обсуждение

ChatGPT — (2026-11-08): предлагаю для первой версии не удалять материалы из Asset Trash автоматически вообще. Они остаются до явного `Delete permanently` или `Empty Trash`, с подтверждением. Cleanup незавершённых загрузок обсудим отдельно.

пользователь — (2026-11-08): «да давай так».

## Решение

**[принято, 2026-11-08]** Для первой версии Asset Trash не имеет автоматического срока истечения и фонового permanent-delete таймера. Готовые Asset в Trash остаются доступными для восстановления до явного действия пользователя: `Delete permanently` для конкретного Asset либо `Empty Trash` для корзины материалов. Они инициируются только пользователем; детали дополнительного confirmation UX сохраняют свой прежний статус в Screens Spec. Физическое удаление применяется только к managed bytes/preview дневника; originals у сторонних провайдеров не удаляются. Существующие tombstone/placeholder правила после permanent delete сохраняются.

Вопросы retention/cleanup незавершённых uploads, временных staging-файлов, orphaned data и late completion **остаются открытыми** в FQ-08 и не решаются этим подпунктом.
