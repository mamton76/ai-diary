# FQ-08 / SQ-02 — Удаление external Asset и внешнего original

**Источник:** [Functional Spec, FQ-08](../../../AI-Diary-Functional-Spec-v0.1.md#14-открытые-системные-вопросы)  
**Статус:** ждём пользователя  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** Codex — текущий диалог требований AI Diary  
**Режим фиксации:** written-turns  
**Родитель:** [FQ-08](../00_thread.md)  
**Дочерние треды:** —  
**Куда переносим решение:** Functional/Screens Specs, inventory/product baseline

## Вопрос

Что означает удаление external Asset для original, который остаётся у внешнего провайдера (например, Google Photos)?

## Варианты

1. В текущей версии удаление действует только внутри дневника: soft delete/Restore и permanent delete external Asset сохраняют уже заданные placeholder/history semantics, но не удаляют original у провайдера. Отдельной команды удаления внешнего original сейчас нет.
2. Предусмотреть отдельное явно подтверждаемое действие удаления original у провайдера; это потребует дополнительных прав и provider-specific сценариев.

## Контекст

- Managed и external originals уже приняты в AQ-DATA-005; external не требует физического импорта.
- Unlink, глобальный soft delete и permanent delete Asset — разные уже заданные операции; этот вопрос не переоткрывает их.
- Functional AST / Screens §14 прямо оставляют удаление внешнего original открытым: удаление reference само по себе его не подразумевает.
- Existing placeholder/minimal metadata contract после permanent delete сохраняется.
- Existing AQ-DATA-005 resolved по storage; отдельного canonical thread для удаления external original при проверке каталога не найдено.
- Удаление managed original из хранилища дневника этим вопросом не пересматривается.

## Обсуждение

Codex — (2026-10-18) После лимита облака следующий самостоятельный продуктовый вопрос FQ-08: судьба внешнего original при удалении материала. Рекомендую в текущей версии удалять только объект/ссылку внутри дневника по принятому lifecycle, а файл в Google Photos или другом внешнем сервисе оставлять. Отдельную команду удаления original у провайдера сейчас не добавлять. Это предложение, ещё не принятое требование.

**Нужно от пользователя:** согласовать, что удаление external Asset не удаляет original во внешнем сервисе и отдельная команда такого удаления сейчас не нужна.

пользователь —

**Решение:** —
