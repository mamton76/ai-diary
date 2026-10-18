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


пользователь — «автоматически к латест при обновлении конечно (можно при обноылении говорить что там у него поменялось)»

ChatGPT — **решение о versioning system workflows (2026-10-18):** новые запуски system workflow автоматически используют latest опубликованную версию. Пользователю не требуется отдельно подтверждать переход на каждую новую системную версию. При обновлении UI должен позволять сообщить/показать, что изменилось (version/changelog). Каждый Run сохраняет точную workflow version, которая реально выполнялась. User-owned копия, созданная через Duplicate/Copy, является самостоятельным workflow и не обновляется автоматически вслед за system workflow.

**Нужно от пользователя:** нужно ли versioning и для пользовательских workflows: сохранять историю опубликованных/сохранённых версий и привязывать Run к точной версии, или достаточно хранить только текущее definition плюс snapshot definition внутри каждого Run?


пользователь — «ну да - у нас же у пользователея будут хранится все версии системных файлов до-после обновлений - копирвоать ее в каждый ран не лишнее? может только для совсем каких-то ручных?»

ChatGPT — **уточнение versioning/run trace (2026-10-18):** если workflow versions являются immutable и все их версии сохраняются в user-owned storage, Run не должен дублировать полный workflow definition. Достаточно ссылки на точную workflowVersion + content hash/идентификатор, а также реально использованных runtime-параметров (model/provider и overrides). Полный snapshot execution definition нужен только для эфемерных/ручных запусков, где нет устойчивой versioned сущности, например Custom prompt или временный одноразовый override. Это избегает дублирования, сохраняя воспроизводимость.

**Нужно от пользователя:** считать ли Custom prompt и другие одноразовые ручные overrides отдельным ephemeral workflow snapshot, который целиком сохраняется внутри Run, без создания постоянного user workflow?


пользователь — «ну такой кастом коненчо, но я так понимаю он заведет себе библиотеку рутин если ему это надо»

ChatGPT — **решение по Custom prompt / библиотеке routines (2026-10-18):** одноразовый Custom prompt не создаёт постоянный workflow и сохраняется как ephemeral execution snapshot внутри Run. Если пользователь хочет переиспользовать такой сценарий, он явно сохраняет его в свою библиотеку routines (например, Save as routine); тогда создаётся самостоятельный user-owned workflow с первой version и дальше он живёт по обычным правилам versioning.

**Нужно от пользователя:** при Save as routine сохранять только prompt/instructions текущего ad hoc запуска или весь фактический execution setup (scope defaults, model override, tools/capabilities, script-steps и прочие настройки)?


пользователь — «мне кажется весь»

ChatGPT — **решение по Save as routine (2026-10-18):** при сохранении ad hoc запуска как постоянной routine переносится весь фактический execution setup, а не только prompt/instructions: prompt, model override при наличии, tools/capabilities, script-steps, eligibility/scope defaults и другие настройки, влияющие на поведение. Это создаёт первую версию user-owned workflow, максимально соответствующую запуску, который пользователь решил сохранить.

**Нужно от пользователя:** различать ли в user routine два класса настроек — постоянные defaults в definition и launch-time overrides, которые можно менять для конкретного запуска без создания новой workflow version?


пользователь — «да это норм»

ChatGPT — **решение о definition defaults и launch-time overrides (2026-10-18):** user/system routine хранит постоянные default-настройки в своём versioned definition. Перед конкретным Run допустимы временные launch-time overrides для разрешённых параметров; такие overrides не создают новую workflow version и сохраняются в Run trace как фактически использованная конфигурация.

**Нужно от пользователя:** какие параметры нельзя менять как launch-time override и следует менять только через новую версию routine? В частности, считать ли script-step/code и набор permissions/capabilities частью versioned definition, а не временным override?


пользователь — «я думаю могут быть какие-то общие абстрактные воркфлоу к которым можно подцеплять код - из доверенных. ща считаем одно потом другое - не?»

ChatGPT — **уточнение модели executable steps (2026-10-18):** да, workflow definition и executable code лучше не склеивать. Возможна отдельная библиотека versioned trusted executors/scripts/tools, а workflow лишь ссылается на них и передаёт параметры/inputs. Один и тот же generic workflow может использовать разные совместимые trusted implementations. Trust относится к конкретной версии исполняемого модуля, а не обязательно ко всей workflow. Нужно отдельно решить, является ли выбор конкретного trusted executor частью versioned workflow definition или допустимым launch-time binding/override.

**Нужно от пользователя:** разрешать ли generic workflow выбирать/подключать совместимый trusted executor при запуске, не создавая новую версию самого workflow, если interface/capabilities executor подходят?


пользователь — «и аналогично про пермишены же?»

ChatGPT — **уточнение capabilities/permissions (2026-10-18):** да, permissions/capabilities также не обязаны быть жёстко зашиты в конкретную workflow version. Workflow может объявлять контракт: какие capabilities обязательны, какие опциональны и какие типы доступа допустимы. Конкретный Run связывает workflow с выбранным permission/capability profile и сохраняет фактически выданный набор. Такой profile может быть отдельной user-owned versioned/trusted сущностью и переиспользоваться разными workflows. При этом workflow не должна получать capability, которое не совместимо с её объявленным контрактом; выдача более широкого профиля не означает автоматического доступа ко всему профилю, если шаги workflow его не запрашивают.

**Нужно от пользователя:** хотим ли мы отдельную библиотеку reusable permission/capability profiles (например «read-only diary», «read + proposals», «read assets + external web»), которые можно выбирать при запуске и переиспользовать между workflows?


пользователь — «ну да выглядит так»

ChatGPT — **решение о capability profiles (2026-10-18):** вводится отдельная user-owned библиотека reusable capability/permission profiles. Профиль является самостоятельной versioned сущностью и может переиспользоваться разными workflows. Workflow объявляет требуемые/опциональные capabilities и совместимый контракт доступа; конкретный Run фиксирует выбранный profile и фактически выданные permissions.

**Нужно от пользователя:** хранить ли в workflow default executor и default capability profile, которые подставляются при запуске автоматически, но могут быть заменены совместимыми trusted вариантами в launch sheet без создания новой workflow version?


пользователь — «да»

ChatGPT — **решение о defaults для запуска (2026-10-18):** workflow может хранить default executor и default capability profile. Они автоматически подставляются при обычном запуске, чтобы не требовать ручной настройки каждый раз. В launch sheet пользователь может заменить их на другие совместимые trusted варианты без создания новой workflow version. Run сохраняет фактически выбранные executor/version и capability profile/version.

**Нужно от пользователя:** нужно ли показывать executor/profile в обычном launch sheet всегда, или скрывать под Advanced и показывать по умолчанию только scope/eligibility/итоговые counts?

**Решение:** —
