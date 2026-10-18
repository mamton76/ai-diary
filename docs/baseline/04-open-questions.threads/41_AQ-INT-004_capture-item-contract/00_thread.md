# AQ-INT-004 — Unified CaptureItem contract

**Источник:** [04-open-questions.md / AQ-INT-004](../../04-open-questions.md#aq-int-004--unified-captureitem-contract)
**Статус:** обсуждаем
**Состояние:** in_discussion
**Claim:** active
**Ведёт:** ChatGPT conversation
**Режим фиксации:** written-turns
**Родитель:** —
**Дочерние треды:** —
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture integrations/capture design

## Вопрос

Как формализовать один normalized capture input, чтобы Telegram, Google Calendar, web и другие adapters не зависели от schema финальной Entry?

## Уже согласованный контекст

Product baseline: external source → normalized capture item → Inbox-to-Entry processing → canonical Entry. Raw capture сохраняется до последующей AI-нормализации; provenance и revisions должны оставаться доступными. Отдельная Entry и CaptureItem не одно и то же.

## Обсуждение

пользователь — «давай»

ChatGPT — Предлагаю разделять транспортный адаптер и canonical Entry. CaptureItem должен сохранять source identity / dedupe key, source type, received/source event timestamps, исходные text/media payload references и provenance, а также optional normalized/transcribed text. Данные могут быть неполными (например, только изображение, без текста). Не следует принудительно приводить timestamp сообщения к времени описанного события; событие определяется позже. Требуется решить, что делать с несколькими сообщениями одного сеанса capture.

**Нужно от пользователя:** CaptureItem представляет одно исходное сообщение/событие, а объединение нескольких CaptureItems в дневниковую Entry выполняется отдельной стадией, или один CaptureItem может включать сразу несколько сообщений одной сессии?

пользователь — «норм»

ChatGPT — Принят принцип гранулярности: один CaptureItem соответствует одному исходному сообщению/событию источника. Несколько CaptureItems могут быть позже сгруппированы или объединены в одну Entry отдельной стадией processing. Границы одной сессии не определяют атомарность записи raw capture; сохраняем каждую часть и provenance независимо.

**Частичное решение:** [принято] (2026-10-18) One source item → one CaptureItem; multi-item grouping/assembly before Entry separate from capture.

**Следующий вопрос:** какой минимальный состав обязательных полей для CaptureItem и как представлять отсутствующий текст / только медиа?

пользователь —

**Решение:** —
