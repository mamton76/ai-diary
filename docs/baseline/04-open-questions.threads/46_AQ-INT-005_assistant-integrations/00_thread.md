# AQ-INT-005 — Assistant-specific integrations

**Источник:** [04-open-questions.md / AQ-INT-005](../../04-open-questions.md#aq-int-005--assistant-specific-integrations)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и integration roadmap

## Вопрос

Когда ChatGPT, Gemini и другие AI assistants умеют создать Calendar event или направить вход в API/Telegram, считать ли это официальной интеграцией AI Diary или только external capture mechanism? Нужны ли специальные provider-specific assistant integrations уже в MVP?

## Уже решено

- PQ-009 / AQ-INT-001: Google Calendar Inbox — optional production capture adapter, ранний приоритет и развитие существующих scripts Calendar→Drive; сам конкретный ассистент не становится core dependency.
- AQ-INT-004: все источники через единый CaptureItem, original source preservation, idempotent import, provenance.
- AQ-INT-003: Telegram личный capture bot, реализация после раннего Calendar Inbox.
- AQ-INT-002: Calendar Timeline — ранний read-only projection; editing/write-back из Calendar в diary не поддерживается.

## Обсуждение

ChatGPT — Предлагает для MVP официально поддерживать AI Diary capture transports (сначала Calendar Inbox, затем Telegram), но считать ChatGPT/Gemini/другие голосовые assistants лишь внешними способами заполнения этих transports, без отдельных встроенных integrations/SDK на каждую модель. Тогда при смене ассистента ingestion в AI Diary не меняется. В будущем direct assistant→AI Diary API можно оформить отдельным официальным адаптером, когда будет понятен надёжный способ authentication, commit boundary и error handling.

**Нужно от пользователя:** достаточно ли в MVP принимать данные от любого ассистента через уже поддержанные каналы (Calendar/Telegram), без отдельной официальной интеграции с ChatGPT или Gemini?

пользователь — «ну в принципе конечно mcp интересно разработать, но кажется на первом этапе можно без него - или как раз оно бы и облегчило бы доступ разным ассистентам? что скажешь?»

ChatGPT — Сверены официальные документы по MCP (2026-11-08). Remote MCP server действительно может предоставить единые AI Diary tools для разных клиентов, но не гарантирует поддержку у всех пользовательских ассистентов, особенно в нужном voice UI. Claude поддерживает пользовательские remote MCP connectors; ChatGPT custom MCP writes сейчас доступны только на определённых business/workspace планах, а Pro упоминает read/fetch, поэтому MCP write capture нельзя считать универсальным для всех пользователей ChatGPT. У Google есть поддержка MCP через SDK/Interactions API/CLI, но доступность подключения своего сервера в Gemini consumer voice/Live отдельно не подтверждена. MCP также требует OAuth/identity, rights, idempotency, safe write confirmation и operating remote endpoint. Он должен быть тонким адаптером к уже принятому backend/domain API и единой CaptureItem boundary, а не альтернативной бизнес-логикой.

**Предложение:** сохранить Calendar Inbox как первый рабочий канал на существующих scripts; в architecture зафиксировать MCP-compatible API и небольшой optional MCP adapter/spike после базового API/Calendar flow. Не делать remote MCP условием работоспособности первого MVP и не обещать универсальную голосовую поддержку. Минимальный будущий набор tools: create/save_capture, finalize_capture_session, get_capture_status; позднее search_entries/get_entry. Деструктивные функции и rewrite revision не экспонировать в начальном MCP. Протестировать на конкретных клиентах и тарифах перед включением в roadmap.

**Официальные источники (проверено 2026-11-08):**
- MCP auth: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/authorization.mdx
- Claude remote MCP: https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp
- ChatGPT custom MCP: https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- Gemini API MCP: https://ai.google.dev/gemini-api/docs/function-calling

**Нужно от пользователя:** принять ли такой промежуточный подход: MCP обязательно учитываем в архитектуре и делаем ранний небольшой прототип, но не ставим его в critical path первого работающего Diary?

пользователь — «норм»

ChatGPT — Подтверждено промежуточное решение: не делать MCP обязательным для первого работающего Diary, но проектировать backend/domain API с возможностью добавить remote MCP как тонкий адаптер. Ранний ограниченный технический прототип после базовых API и Calendar flow без обязательной интеграции конкретного ассистента. Использовать те же CaptureItem, identity/auth, idempotency и явную границу завершения capture session; не дублировать domain logic в MCP. Начальные инструменты для прототипа: сохранение capture, завершение сессии, проверка статуса; чтение/поиск Entry можно добавить позднее. Поддержка в голосовом интерфейсе каждого ассистента должна проверяться отдельно, не обещать универсальной совместимости.

**Решение:** [принято] (2026-11-08) Calendar Inbox — первый production capture transport (с развитием существующих scripts), далее Telegram. MCP — предусмотренная архитектурой расширяемая интеграция и ранний optional spike после базового API/Calendar flow, но не critical path первого MVP. Ассистенты могут использовать общие capture transports без отдельных provider-specific backends. MCP server должен переиспользовать существующий API/business rules с безопасной авторизацией, оригиналами и идемпотентностью; точная поддержка и голосовые возможности ChatGPT/Claude/Gemini определяются опытной проверкой.
