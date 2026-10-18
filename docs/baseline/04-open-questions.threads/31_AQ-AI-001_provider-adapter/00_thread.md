# AQ-AI-001 — Provider adapter contract

**Источник:** [04-open-questions.md / AQ-AI-001](../../04-open-questions.md#aq-ai-001--provider-adapter-contract)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture AI subsystem design

## Вопрос

Как подключать несколько LLM providers (OpenAI, Anthropic, Google) через общий backend contract, сохраняя provider-specific capabilities? Где граница между generic adapter и различиями API?

## Варианты

1. Непосредственные provider-specific вызовы из каждого workflow (проще первый прототип, больше coupling).
2. Один унифицированный provider adapter c minimal common operations (generate text/structured output, usage, error/status) и explicit capabilities/optional extensions.
3. Унификация всех provider features под максимально широкий интерфейс, рискуя хрупкими абстракциями.

## Контекст

Принято ранее (PQ-006): пользователь выбирает модель, provider выводится из выбранной модели; приоритет task/run override → workflow preference → global preference → system default; нельзя молча делать fallback на другую модель. Backend — Kotlin/Ktor, asynchronous workflow jobs. Canonical state не изменяется моделью напрямую, AI output валидируется и проходит workflow-specific proposal/apply policy.

Актуальные официальные API (проверено 2026-10-18):
- OpenAI Responses API: https://developers.openai.com/api/reference/resources/responses/methods/create
- Anthropic Messages API: https://platform.claude.com/docs/en/api/messages/create
- Google Gemini generateContent: https://ai.google.dev/api/generate-content
Все поддерживают text generation, structured output и tool/function calling с различиями в request/response форматах; availability конкретных features зависит от модели/provider.

## Обсуждение

пользователь — «да давай. вообще пока не понимаю как их подключать и какие у них апи есть»

ChatGPT — У провайдеров есть отдельные HTTPS API и API credentials, которые backend использует без передачи секретов браузеру. Для MVP можно дать общую операцию generateStructured/generateText плюс model selection, capabilities и provider-specific options при необходимости. Internal workflows получают нормализованный результат и usage/diagnostic metadata, а provider adapters переводят его в OpenAI/Anthropic/Gemini requests. Готовые приложения ChatGPT/Claude Code/Gemini не равны API вызову; подписки на потребительские приложения не обязательно включают API billing.

**Нужно от пользователя:** принять минимальный общий adapter с явными capabilities и расширениями или сначала подробно сравнить operational отличия API и цену.

пользователь — «да все звучит норм»

ChatGPT — Принят минимальный общий контракт, с явными model capabilities и расширениями конкретных providers. Backend Kotlin/Ktor владеет API credentials, вызывает providers, возвращает нормализованный результат workflows и usage/diagnostics. Конкретные SDK, schema details, error taxonomy и support matrix реализуются постепенно. Достаточно начать с одного adapter, сохраняя multi-provider architecture; автоматический fallback без согласия запрещён ранее принятым PQ-006.

**Решение:** [принято] (2026-10-18) Использовать минимальный provider-neutral LLM adapter для генерации текста/structured output и нормализации результата, usage и ошибок. Выбор модели определяет provider. Provider/model capabilities объявляются явно; специальные features доступны через optional extensions/options без искусственной унификации всех API. Workflow engine не зависит от конкретных HTTP форматов OpenAI/Anthropic/Gemini. Реализацию adapter-ов можно вводить поэтапно, начав с одного провайдера. API keys хранятся server-side. Не менять модель/provider автоматически без явного разрешения.
