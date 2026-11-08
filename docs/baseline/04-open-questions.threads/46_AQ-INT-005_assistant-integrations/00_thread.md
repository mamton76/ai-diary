# AQ-INT-005 — Assistant-specific integrations

**Источник:** [04-open-questions.md / AQ-INT-005](../../04-open-questions.md#aq-int-005--assistant-specific-integrations)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation (2026-11-08)  
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

пользователь —

**Решение:** —
