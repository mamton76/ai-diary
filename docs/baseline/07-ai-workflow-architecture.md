# AI Diary — AI workflow architecture baseline

**Дата:** 2026-10-18  
**Источник решения:** [AQ-AI-002](04-open-questions.threads/32_AQ-AI-002_workflow-definition/00_thread.md)

Этот документ фиксирует архитектурную границу workflow subsystem. Формат файлов/JSON и конкретный editor UX определяются отдельно.

## 1. Ownership и runtime

- User workflow definitions — canonical user-owned versioned data рядом с diary data.
- Backend предоставляет workflow engine/runtime и durable execution.
- System workflows поставляются приложением, имеют immutable version history и для новых Runs автоматически используют latest published version.
- Конкретный Run всегда фиксирует точные versions/bindings, которые реально выполнялись.

## 2. Workflow versions

### User workflows

- Редактирование идёт через mutable Draft definition.
- Immutable version появляется только при явном Publish / Save version.
- Published versions не переписываются и сохраняются как history.
- Restore старой version создаёт новую current version.
- Удаление user workflow — soft delete; permanent delete пока отсутствует.

### System workflows

- История versions доступна read-only с diff/changelog.
- System version нельзя редактировать или восстанавливать как system current.
- Любую historical system version можно Duplicate в user-owned workflow.
- User copy после Duplicate развивается независимо от system workflow.

## 3. Test runs и ad hoc runs

- Draft workflow можно запускать как Test run.
- Test run сохраняет snapshot реально выполненного Draft.
- Успешный Test run можно Publish as tested version; публикуется именно tested snapshot.
- Если current Draft уже изменился, он не теряется; после публикации tested snapshot его base переводится на новую published version.
- Custom prompt / ad hoc run не создаёт workflow автоматически: Run хранит ephemeral execution snapshot.
- Save as routine создаёт новый user-owned workflow из полного фактического execution setup.

## 4. Definition, bindings и overrides

Workflow definition содержит versioned логику, contracts и defaults. Конкретный Run может переопределять разрешённые launch-time параметры без создания новой workflow version и сохраняет фактическую конфигурацию.

Workflow может иметь:
- default executor;
- default capability profile;
- model/default runtime preferences;
- eligibility/scope defaults.

В launch sheet executor и capability profile пока остаются явно видимыми, а не скрываются под Advanced.

## 5. Executable modules и trust

Executable code не обязан быть встроен в workflow definition.

- Reusable executors/scripts/tools — отдельные versioned сущности/модули.
- Workflow ссылается на совместимый executor contract и может использовать default implementation.
- При запуске default executor можно заменить на другой совместимый trusted executor без новой workflow version.
- Trust относится к конкретной code version/hash.
- Перед первым использованием конкретная version требует explicit user approval.
- Неизменённая trusted version может выполняться повторно без нового подтверждения.
- Изменение кода создаёт новую untrusted version.
- Executor/script может быть написан пользователем, создан AI по прямой просьбе или предложен AI; AI не может молча сделать его trusted.
- Runtime/sandbox/language policy определяется отдельно; архитектура не ограничивается только Python.

## 6. Capabilities / permissions

- По умолчанию применяется least privilege.
- Workflow/executor не получает весь diary/storage автоматически.
- Workflow объявляет required/optional capability contract.
- Reusable capability profiles — отдельные user-owned versioned сущности.
- Один capability profile может использоваться разными workflows.
- Run сохраняет выбранную profile version и фактически выданные permissions.
- Более широкий profile не даёт workflow доступ к capabilities, которые оно не запрашивает/не поддерживает.

## 7. Workflow structure MVP

- Linear pipeline шагов.
- Простые conditions/branching поддерживаются.
- Полноценные loops/iteration constructs не входят в MVP без конкретного use case.
- Для step errors поддерживаются policies: `stop`, `skip`, `continue-with-warning`; default — `stop`.

## 8. Output contracts и validators

- Output schema и declarative validation rules входят в versioned workflow definition.
- Простые structural checks описываются декларативно.
- Сложные validators с исполняемым кодом оформляются как отдельные trusted/versioned executors/tools.

## 9. Run trace

Обычный Run не дублирует полный immutable workflow definition. Он хранит references/hashes на точные workflow/executor/capability-profile versions и фактические runtime overrides. Полный snapshot нужен для ephemeral/ad hoc execution и Test runs Draft definitions.

## 10. Отдельный вопрос

Конкретные поля редактора workflow, presentation шагов, drag/drop, формы conditions, UX trust/permissions и прочие editor details обсуждаются отдельно от этой архитектурной модели.
