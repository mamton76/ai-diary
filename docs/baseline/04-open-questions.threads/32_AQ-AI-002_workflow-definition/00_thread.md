# AQ-AI-002 — Где живёт workflow definition

**Источник:** [04-open-questions.md / AQ-AI-002](../../04-open-questions.md#aq-ai-002--где-живёт-workflow-definition)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT  
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


пользователь — «давай в каком-то доверенном варианте оставим возможность выполнениия скриптов питонячих и не только - только как-то надо будет поджумать в какой момент они нужны и кто их пишет и так далее - но мне кажется возможность крутая»

ChatGPT — **обновление (2026-10-18):** подтверждено направление, что user workflows/routines являются частью user-owned data и должны храниться рядом с diary data, а backend остаётся engine/runtime. При этом архитектуру нельзя ограничивать только декларативными шагами: workflow model должна допускать trusted/controlled executable steps (Python и потенциально другие runtimes). Не зафиксированы конкретный язык, sandbox/runtime, момент использования script-step, автор скрипта, permissions и trust UX. Эти детали остаются открытыми; произвольный код внутри основного backend-процесса не следует считать принятым вариантом.

**Нужно от пользователя:** решить trust UX для executable step: достаточно ли один раз просмотреть/подтвердить конкретную версию скрипта и затем разрешить ей выполняться автоматически, или подтверждение нужно перед каждым запуском?


пользователь — «да давай»

ChatGPT — **решение по trust UX (2026-10-18):** конкретная версия executable script-step до первого запуска считается untrusted. Пользователь один раз просматривает и явно подтверждает её; после этого именно этот hash/version считается trusted и может выполняться автоматически в workflow. Любое изменение кода создаёт новую untrusted version и снова требует подтверждения. Подтверждение перед каждым повторным запуском неизменённой trusted version не требуется.

пользователь — «да норм»

ChatGPT — **решение об авторстве script-step (2026-10-18):** executable step может быть создан самим пользователем; AI может написать его по прямой просьбе пользователя; AI также может сам предложить script-step как подходящий шаг workflow. AI не активирует и не делает такой код trusted молча: код/изменение показывается пользователю, а trust для конкретной версии выдаётся только явным подтверждением пользователя.

**Нужно от пользователя:** определить, какие данные и capabilities executable step получает по умолчанию: весь user-owned diary/storage или только явно переданные workflow inputs и разрешённые tools?


пользователь — «да»

ChatGPT — **решение о permissions executable step (2026-10-18):** по умолчанию script-step работает по принципу least privilege. Он не получает весь diary/Drive автоматически, а видит только явно переданные workflow inputs и разрешённые этому workflow tools/capabilities. Доступ к поиску по дневнику, Assets, внешним данным или записи результата должен быть объявлен отдельно и выдан как capability/permission.

**Нужно от пользователя:** определить versioning system workflows: системный workflow может обновляться приложением на новую версию автоматически, или пользователь должен явно выбирать/подтверждать переход на новую версию?

**Решение:** —
