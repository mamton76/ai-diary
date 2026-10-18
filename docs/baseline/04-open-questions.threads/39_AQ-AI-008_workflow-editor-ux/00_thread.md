# AQ-AI-008 — Workflow editor UX

**Источник:** выделено из resolved AQ-AI-002 (2026-10-18)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT  
**Режим фиксации:** written-turns  
**Родитель:** AQ-AI-002  
**Дочерние треды:** —  
**Куда переносим решение:** AI-Diary-Screens-Spec-v0.1.md / workflow editor UX

## Вопрос

Как выглядит пользовательский editor user-owned workflow/routine поверх уже принятой архитектурной модели?

Нужно определить как минимум:

- представление linear pipeline и simple conditions;
- поля шага и workflow-level settings;
- выбор/default executor и capability profile;
- редактирование prompt/instructions/output schema;
- trust UX для executable modules;
- Draft / Test run / Publish tested version;
- version history, diff, Restore as new version;
- адаптацию editor для desktop/mobile.

Формат canonical storage и runtime contracts сюда не смешивать: они относятся к architecture/data design.

## Контекст

Архитектурная база закрыта в [AQ-AI-002](../32_AQ-AI-002_workflow-definition/00_thread.md). MVP workflow — linear pipeline + simple conditions, executable modules и capability profiles являются отдельными versioned сущностями, user workflow имеет Draft → Publish version semantics.

## Обсуждение

ChatGPT — **старт обсуждения (2026-10-18):** AQ-AI-008 продолжается поверх закрытой архитектуры AQ-AI-002. Существующий S13 уже задаёт Routines / Runs, system/user routines, запуск из Entry/Browser/Routines, scope/eligibility и Run Detail. Здесь обсуждаем только сам editor user routine: визуальную структуру шагов, поля, trust/permissions, Draft/Test/Publish/history и adaptive UX.

**Нужно от пользователя:** выбрать базовое представление workflow editor.


пользователь — «да - толкьо бы еще обсудить на конкретных примерах наших форкфлоу»

ChatGPT — **решение о способе проработки editor UX (2026-10-18):** базовое представление принимаем как вертикальный список раскрываемых шагов с простыми inline conditions/branches, без node-canvas в MVP. Дальнейшие поля и controls editor нельзя проектировать только абстрактно: UX нужно прогнать на конкретных существующих workflows проекта, как минимум Tag Enrichment, Inbox → Entry и Google Calendar Timeline Projection, и только затем обобщать повторяющиеся primitives.

**Нужно от пользователя:** начать разбор с Tag Enrichment как наиболее показательным user-facing AI workflow.


пользователь — «оки»

ChatGPT — **решение по Application policy (2026-10-18):** для Tag Enrichment и аналогичных workflows выбор `auto-apply / proposal / review` относится к Application policy routine, а не моделируется отдельными визуальными ветками pipeline. Ветки `Condition` в editor используются для реального изменения control flow, например «если есть Assets → выполнить image analysis, иначе пропустить шаг».

**Нужно от пользователя:** разобрать следующий реальный workflow — Inbox → Entry — и определить, какие из его стадий должны быть самостоятельными шагами в editor.


пользователь — «да похоже на правду»

ChatGPT — **решение по Input / Trigger section (2026-10-18):** `Input / Trigger` является отдельной верхней секцией workflow editor и не моделируется как первый reorderable processing step. В этой секции задаются источник/trigger запуска и eligibility/selection contract. Ниже расположен собственно pipeline. Примеры: Tag Enrichment — Entries matching eligibility / manual launch; Inbox → Entry — new Inbox item из допустимого capture source.

**Нужно от пользователя:** разобрать Google Calendar Timeline Projection и решить, нужен ли симметричный отдельный Output / Side effects block после pipeline.


пользователь — «да норм вроде»

ChatGPT — **решение по Output / Side effects section (2026-10-18):** после processing pipeline в workflow editor есть отдельная декларативная секция `Output / Side effects`. Она не является reorderable step и показывает, что workflow производит наружу: analysis result, Proposal, committed mutation при разрешённой policy, создание/обновление внешней projection, обновление derived state и т.п. Секция также явно показывает запрещённые/отсутствующие мутации canonical data, когда это важно. Application policy остаётся отдельной настройкой и определяет, как допустимые изменения применяются/reviewed.

**Нужно от пользователя:** решить форму карточки processing step: универсальная карточка с Type + Inputs + Config + Outputs + Error policy, или разные визуальные формы для AI step / executor step / condition / validator?


пользователь — «да так вроде лучше»

ChatGPT — **решение по карточке processing step (2026-10-18):** все processing steps используют общий каркас карточки `Type / Inputs / Config / Outputs / Error policy`, но содержимое `Config` и часть presentation зависят от типа шага. AI step, executor/script, condition и validator не превращаются в четыре полностью независимых editor-а, но и не маскируются под одну безликую универсальную форму.

**Нужно от пользователя:** определить collapsed/expanded UX карточки шага: что видно в свёрнутом состоянии и открыта ли одновременно одна карточка или несколько.


пользователь — «да»

ChatGPT — **решение по collapsed/expanded step cards (2026-10-18):** свёрнутая карточка шага должна показывать достаточно контекста для чтения pipeline без раскрытия: номер/тип/название шага, краткие input→output, ключевые runtime hints и error policy. В workflow editor можно держать раскрытыми несколько шагов одновременно; ограничение «только одна раскрытая карточка» не применяется, потому что при настройке pipeline полезно сравнивать соседние шаги и их contracts.

**Нужно от пользователя:** определить UX связывания outputs одного шага с inputs следующего: автоматическое связывание по совместимым типам с возможностью явного remap, или только ручное mapping.


пользователь — «вроде норм»

ChatGPT — **решение по input/output mapping (2026-10-18):** editor автоматически связывает совместимые outputs предыдущих шагов с inputs следующего шага, когда соответствие однозначно/безопасно. В раскрытой карточке шага доступен явный `Inputs mapping` для просмотра и ручного remap. Полностью ручное связывание не является default UX.

**Нужно от пользователя:** определить, как визуально показывать simple condition/branch внутри вертикального pipeline.


пользователь — «да норм наверное - надо пробовать - мы же сможем в прототипе эт осделать?»

ChatGPT — **решение по presentation condition/branch (2026-10-18):** в MVP simple condition отображается внутри вертикального editor как вложенные ветки/группы, а не node-canvas с проводами. Ветви могут визуально снова сходиться в общий следующий шаг. Решение считаем проверяемым через UI-прототип: достаточно интерактивного mock/editor surface с nested step cards, без реализации полноценного workflow runtime.

**Нужно от пользователя:** определить минимальный набор типов шагов, который должен быть виден в + Add step в первом прототипе.


пользователь — «вроде так»

ChatGPT — **решение по минимальному набору типов шагов для первого прототипа (2026-10-18):** в `+ Add step` первого прототипа достаточно четырёх типов: `AI step`, `Executor / Tool`, `Condition`, `Validator`. Дополнительные специализированные типы не вводим, пока реальные workflows не покажут необходимость.

**Нужно от пользователя:** определить поля AI step на примере Tag Enrichment: prompt/instructions, model override, input mapping, output schema, validator и error policy.


пользователь — «да»

ChatGPT — **решение по AI step model override (2026-10-18):** AI step по умолчанию использует `Inherit workflow default`, но может иметь собственный step-specific model override. Это позволяет простым routines использовать одну модель, а многошаговым workflows при необходимости назначать разные модели разным AI steps без изменения общей архитектуры provider/model hierarchy.

**Нужно от пользователя:** решить UX prompt/instructions внутри AI step: обычное большое поле с возможностью раскрыть в полноэкранный editor, или сразу отдельный dedicated prompt editor surface.


пользователь — «ну давай так»

ChatGPT — **решение по prompt/instructions editor (2026-10-18):** в раскрытой карточке AI step есть встроенное большое поле `Instructions / Prompt` для обычного редактирования. Для длинного или сложного prompt доступно действие `Open full editor`, открывающее более просторную dedicated editor surface. Отдельный экран не является обязательным для каждого изменения prompt.

**Нужно от пользователя:** определить, что именно показывает full prompt editor помимо текста: только большой editor, или ещё справа/снизу live preview доступных inputs/variables и output schema.


пользователь — «норм»

ChatGPT — **решение по full prompt editor (2026-10-18):** full prompt editor показывает не только большое поле prompt/instructions, но и контекст шага: доступные `inputs / variables` и ожидаемый `output schema`. Это помогает редактировать длинный prompt без потери связи с contract шага.

**Нужно от пользователя:** определить UX Executor / Tool step на примере trusted script/module: показывать выбранный module/version + trust status + parameters + capabilities в одной карточке или уводить trust/details в отдельный экран.


пользователь — «да норм»

ChatGPT — **решение по Executor / Tool step card (2026-10-18):** карточка Executor / Tool step показывает выбранный module/executor, version, trust status, parameters, capabilities, inputs/outputs и error policy. Полный код и подробный trust review не занимают место в pipeline и открываются отдельным действием вроде `View code / Review trust`. Trust status при этом всегда виден в карточке.

**Нужно от пользователя:** определить, что делать в editor, если выбранный executor/module ещё untrusted: разрешать сохранить Draft, но блокировать Test run/Publish/обычный Run до trust, или требовать trust уже при выборе модуля.


пользователь — «норм»

ChatGPT — **решение по untrusted executor в editor (2026-10-18):** untrusted executor/module можно выбрать и сохранить внутри Draft workflow без немедленного trust-review. Publish также допустим: опубликованная routine может существовать с явным статусом `requires trust before run`. Test run и обычный Run блокируются до explicit trust конкретной module version. Trust не навязывается пользователю в момент выбора модуля.

**Нужно от пользователя:** определить UX Validator step: показывать простые declarative rules прямо в карточке, а сложный code validator оформлять как ссылку на trusted executor/tool.


пользователь — «да»

ChatGPT — **решение по Validator step (2026-10-18):** простые declarative validation rules редактируются прямо в карточке Validator step: required fields, types, enum/range/pattern/non-empty и аналогичные structural checks. Если проверка требует исполняемого кода, Validator step ссылается на отдельный trusted/versioned executor/tool; код не прячется внутрь declarative validator.

**Нужно от пользователя:** определить UX capability profile на уровне workflow: показывать выбранный default profile в верхних Workflow settings и только локальные capability requirements внутри конкретных steps.


пользователь — «да»

ChatGPT — **решение по capability profile в workflow editor (2026-10-18):** default capability profile показывается на уровне верхних Workflow settings. Конкретные processing steps не дублируют полный profile, а объявляют только свои локальные required capabilities. Editor проверяет совместимость: если выбранный/default profile не покрывает requirement шага, это явно подсвечивается как conflict до запуска.

**Нужно от пользователя:** определить состав верхнего блока Workflow settings и решить, какие поля всегда видны, а какие можно свернуть.


пользователь — «ну ладно наверное ты права»

ChatGPT — **решение по Eligibility / Scope default placement (2026-10-18):** `Eligibility` и `Scope default` относятся к секции `Input / Trigger`, а не к общему `Workflow settings`. Eligibility задаёт постоянный contract допустимых Entries, а Scope default — стартовый объём выборки для запуска (`This Entry / Current filtered set / All eligible` или совместимый вариант).

**Нужно от пользователя:** определить окончательный состав верхнего блока Workflow settings без Input/Trigger-полей.


пользователь — «ну давай»

ChatGPT — **решение по placement Application policy (2026-10-18):** `Application policy` выносится из верхнего `Workflow settings` в отдельную секцию после processing pipeline, рядом с `Output / Side effects`. Верхний блок остаётся компактным и содержит общие defaults/identity workflow, а policy описывает, как допустимые результаты workflow применяются, отправляются в Proposal/Review или auto-apply.

**Нужно от пользователя:** определить, какие поля остаются в компактном Workflow settings и нужен ли отдельный блок Version/Draft status в header.


пользователь — «норм»

ChatGPT — **решение по editor header/version status (2026-10-18):** versioning state не входит в редактируемый `Workflow settings`. В header editor показывается текущий статус, например `Draft based on v3`, последняя published version и основные actions `Test run`, `Publish`, `History`. Это отделяет identity/defaults workflow от lifecycle/version controls.

**Нужно от пользователя:** определить поведение Test run: запускать его из header и открывать сразу Run Detail, сохраняя текущий Draft snapshot.


пользователь — «норм»

ChatGPT — **решение по Test run flow (2026-10-18):** кнопка `Test run` находится в header workflow editor и запускает текущий Draft snapshot. После старта открывается Run Detail с пошаговыми статусами и outputs. Успешный Test run предоставляет действие `Publish tested version`, публикующее именно протестированный snapshot по правилам AQ-AI-002.

**Нужно от пользователя:** определить UX History для workflow: отдельная panel/page со списком published versions, diff и Restore as new version, доступная из header.


пользователь — «норм»

ChatGPT — **решение по workflow History UX (2026-10-18):** `History` открывается из header как отдельный режим/panel/page, а не встраивается под pipeline. Показывается список immutable published versions с датой и кратким changelog/summary. Для user workflow доступны `Compare` и `Restore as new version`; для system workflow — read-only history/diff и `Duplicate this version`.

**Нужно от пользователя:** определить adaptive/mobile UX workflow editor: сохранять тот же вертикальный pipeline, а secondary settings открывать в sheet/full-screen editor на узких экранах.


пользователь — «норм»

ChatGPT — **решение по adaptive/mobile workflow editor (2026-10-18):** на mobile сохраняется та же вертикальная модель pipeline, без отдельной мобильной семантики. Step cards занимают доступную ширину; сложные secondary editors (Config, Inputs mapping, Output schema) могут открываться в bottom sheet или full-screen surface. Condition branches остаются вложенными группами, а History, full prompt editor и trust/code review на узком экране открываются как отдельные full-screen режимы.

**Нужно от пользователя:** определить publish validation UX: что именно должно блокировать Publish и что допускается опубликовать с warning.


пользователь — «ок»

ChatGPT — **решение по publish validation UX (2026-10-18):** Publish блокируется только structural/configuration errors, из-за которых workflow definition некорректен или внутренне несовместим: broken input/output mapping, обязательный input без source, invalid Condition, несовместимый output contract, отсутствующий обязательный executor/tool или capability requirement, который невозможно удовлетворить конфигурацией. Runtime-readiness проблемы вроде untrusted executor, временно недоступной model или отсутствующего default capability profile оформляются как warnings: Publish разрешён, но routine получает явный статус `requires setup / not ready to run`.

**Нужно от пользователя:** определить UX создания новой user routine: стартовать с пустого workflow, из шаблона/system routine через Duplicate, либо из успешного Custom prompt / Run через Save as routine; какие entry points считаются основными.

**Решение:** —
