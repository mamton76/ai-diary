# AQ-AI-002 — Где живёт workflow definition

**Источник:** [04-open-questions.md / AQ-AI-002](../../04-open-questions.md#aq-ai-002--где-живёт-workflow-definition)  
**Статус:** обсуждаем  
**Состояние:** open  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** written-turns  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture AI workflow design

## Вопрос

Где хранить определения AI workflows: кодовая orchestration, prompts/config, user instructions, output schemas, validators и tools? Как отделять пользовательское содержимое workflow от доверенного исполняемого backend кода?

## Варианты

1. Workflows в repo/backend code, prompts/config как версионируемые файлы приложения.
2. Определения workflows как user-owned portable files рядом с дневником; backend предоставляет generic engine и безопасные разрешённые capabilities.
3. Гибрид: user-owned workflow definitions/prompts/settings и code-defined versioned executors, validators и tools.

## Контекст

Принято: user-owned portable files — canonical source of truth (PQ-001), operational DB/cache — rebuildable derivatives; workflows запускаются в backend через durable jobs (AQ-API-004), используют provider-neutral adapters (AQ-AI-001). В file-based prototype уже предусмотрен каталог _prompts/, PROMPTSET.json и versioned prompt files; эти проектные примеры не определяют сами по себе полную форму workflow definition.

## Обсуждение

пользователь — «я считаю что AI workflows так же хранятся в базе/файлах недалеко от данных пользователя -»

ChatGPT — Это подразумевает, что пользовательские workflows, их инструкции и настройки являются частью user-owned diary storage, а не только backend deployment config. Runtime engine может быть общим и находиться в коде приложения. Нужно отдельно определить границу: сохраняем ли сами workflow definitions как переносимые пользовательские файлы, а backend лишь интерпретирует их, или вместе с ними допускается пользовательский исполняемый код? Для MVP безопаснее декларативные workflow definitions (шаги, prompt refs, model choice, input/output contracts) и заранее определённые tools/validators backend.

**Нужно от пользователя:** подтверждаем ли, что workflow — редактируемый и переносимый user-owned declarative definition, без произвольного исполняемого кода в MVP?

пользователь — «дальше AI workflow обсуждаем с сессии Уточнение разных требований для ТЗ - можешь передать туда данные - с тобой давай обсуждать что-то сниим не связанное пока»

ChatGPT — **handoff (2026-10-18):** освобождаю claim для сессии «Уточнение разных требований для ТЗ». Уже выраженная позиция пользователя: definitions AI workflows должны храниться в базе/файлах рядом с пользовательскими diary data, не исключительно в backend repo. Это направление, а не окончательно закрытое решение о format/security. Пример возможного layout: workflows/<workflow-id>/workflow.json + prompt.md (иллюстрация, не утверждённая схема). Backend Kotlin engine выполняет workflows; ранее приняты PQ-001, AQ-AI-001, AQ-API-004. **Открытая развилка:** допускаем ли исполняемый пользовательский код или ограничиваем MVP декларативными workflows + разрешёнными backend tools. Не считать рекомендацию ChatGPT («начать с декларативных») согласованной позицией пользователя. Следующая сессия должна перечитать source, thread, index и занять claim перед продолжением.

**Нужно от пользователя:** ответить на вопрос о декларативных workflow versus custom executable code в сессии «Уточнение разных требований для ТЗ».

**Решение:** —
