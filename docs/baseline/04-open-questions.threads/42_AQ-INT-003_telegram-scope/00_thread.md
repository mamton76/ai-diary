# AQ-INT-003 — Telegram scope

**Источник:** [04-open-questions.md / AQ-INT-003](../../04-open-questions.md#aq-int-003--telegram-scope)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation (2026-10-18)  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md, functional spec Telegram capture и architecture integrations design

## Вопрос

Каков полный целевой scope Telegram capture и в каком порядке его реализуем (text, voice, photo/media, links, forwarded files, multi-message sessions)?

## Уже принято в смежном вопросе

[AQ-INT-004](../41_AQ-INT-004_capture-item-contract/00_thread.md): одно Telegram source message → один CaptureItem; оригинальный текст/медиа сохраняется, деривативы/транскрипции отдельно; source-ID dedup; несколько CaptureItems можно объединять вручную или с AI, при ручном объединении Draft создаётся из доступного текста и Inbox отмечает обработку после Save. Продуктовые ASSET-001…009 уже подтверждают общую media/Asset model.

## Обсуждение

ChatGPT — Для первого Telegram-адаптера предложено реализовать text и voice сразу, а фотографии, ссылки, пересылаемые файлы и другие вложения постепенно.

пользователь — «ну я бы ассеты бы тоже добавила в ТЗ но реализацию просто не сразу делала»

ChatGPT — Принято: целевое ТЗ Telegram не ограничивается текстом/голосом. Указываем поддержку assets/attachments (фотографии, видео, аудио, документы/файлы, в том числе пересылаемые), ссылок и связи с исходными сообщениями, captions и provenance там, где Telegram предоставляет данные. Приём текстовых и голосовых сообщений остаётся первым implementation slice; конкретную последовательность остальных типов пока не фиксируем. Это отложенная реализация, а не исключение из требований. Технический Asset contract берётся из общих требований ASSET-001…009 и AQ-INT-004.

**Частичное решение:** [принято] (2026-10-18) Telegram captures text, voice and eventually assets/attachments/links/forwarded content; assets documented in requirements now, implemented in later slice.

**Следующий вопрос:** первый способ взаимодействия с Telegram — личный чат с собственным ботом, которому отправляем сообщения/голос, или предполагаем также добавление бота в группы/каналы в MVP?

пользователь — «да личные записи»

ChatGPT — Принято: в MVP пользователь отправляет личные дневниковые записи напрямую в приватный диалог с ботом AI Diary (1:1). Приём сообщений из групп и каналов не входит в первую реализацию. Это не публичный канал для публикации дневника; не следует трактовать Telegram chat как публичный storage. Дальнейшее расширение на группы/каналы возможно, но сейчас не требуется.

**Частичное решение:** [принято] (2026-10-18) Telegram MVP supports direct private 1:1 chat to capture personal entries only; no group/channel ingestion.

**Следующий вопрос:** нужно ли ограничить прием записей только заранее привязанным Telegram-аккаунтом (например, подтверждением через разовый код в web AI Diary), чтобы посторонние пользователи бота не могли писать в личный Inbox?

пользователь —

**Решение:** —
