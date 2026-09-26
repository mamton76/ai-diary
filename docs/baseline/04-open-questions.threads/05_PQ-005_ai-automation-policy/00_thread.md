# PQ-005 — Насколько AI автоматичен?

**Источник:** [04-open-questions.md / PQ-005](../../04-open-questions.md#pq-005--насколько-ai-автоматичен)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Насколько самостоятельно AI Diary может применять результаты AI workflows, а где требуется явное подтверждение пользователя?

## Варианты

1. **Suggestion only** — AI только предлагает изменения.
2. **User confirmation by default** — AI готовит изменение, пользователь подтверждает.
3. **Auto-apply safe metadata** — безопасные структурные изменения можно применять автоматически, содержательные — только после подтверждения.
4. **Per-workflow policy** — каждый workflow имеет свою policy: suggestion, confirm, auto-apply, confidence threshold.

## Контекст

## Связанные источники

- [Product baseline §15 — LLM / AI](../../03-product-baseline.md#15-llm--ai-как-отдельная-подсистема)
- [Source ledger](../../05-source-ledger.md), где перечислены исходные workflow-документы:
  - `02_Workflow_Inbox_To_Entry.md`
  - `03_Workflow_Tag_Enrichment.md`
  - `04_Workflow_Google_Calendar_Inbox.md`

Вопрос PQ-005 возникает на границе между AI-result и изменением diary state: при создании/очистке entry из inbox, tag/metadata enrichment, изменении существующей entry, background workflows и массовой обработке.

Нужно отделить удобство автоматизации от риска незаметно переписать личную историю. Уже принятые принципы требуют сохранять raw/provenance и не терять пользовательские изменения.

Это голосовой тред: разговор не стенографируется. В файл попадают только смысловые сводки и явно принятые решения.

## Обсуждение

### Сводка 1 — старт обсуждения

Тред открыт. Решения пока нет.

### Сводка 2 — release

Обсуждение PQ-005 отложено до следующего захода. Содержательного решения ещё не принимали; claim снят, вопрос снова свободен для обсуждения.


### Сводка 3 — согласованные границы auto-apply

Согласовано:
- при сохранённом raw capture AI может автоматически создавать первую нормализованную версию entry;
- неоднозначности должны помечаться для review;
- существующие теги можно привязывать автоматически при высокой уверенности;
- числовой threshold пока не фиксируем;
- новые теги по умолчанию только предлагаем;
- user-added tags AI автоматически не удаляет.

Следующая часть обсуждения — изменение текста существующей entry и более рискованные структурные действия.


### Сводка 4 — AI text changes через runtime proposal

Для изменений текста существующей entry пользователь предпочитает proposal-based flow даже когда AI workflow запущен вручную самим пользователем.

Рабочая граница:

- запуск AI-команды означает «сгенерируй вариант», а не «автоматически перепиши current entry»;
- результат показывается как runtime proposal/preview, желательно с diff там, где это полезно;
- пользователь может принять результат, отклонить его или при необходимости изменить/перезапустить;
- только **Apply/Accept** превращает proposal в новую revision и делает её current;
- уже применённое изменение должно оставаться обратимым через revision history/restore;
- background AI тем более не должен автоматически менять canonical text;
- ранее согласованные исключения остаются: первая processed entry из сохранённого raw может создаваться автоматически; high-confidence existing tags могут auto-apply.

Отдельный открытый UX-вопрос: должны ли непринятые proposals переживать reload/session или достаточно runtime-only состояния.


### Сводка 5 — proposal как uncommitted state

Связка с PQ-004: пользователь не хочет сохранять в revision history промежуточные AI-варианты, которые ещё не приняты.

Рабочая продуктовая модель:
- AI result для существующей entry сначала является proposal / uncommitted state;
- proposal может содержать snapshot/diff и provenance, но ещё не входит в committed History;
- Accept/Apply создаёт новую revision;
- Reject не создаёт revision;
- если proposal нужно переживать reload/session, он может храниться как pending state; если нет — оставаться runtime-only;
- будет ли proposal технически отдельной сущностью или той же записью со статусом pending — архитектурная деталь. На продуктовом уровне важно различие pending vs committed.

Связанный note добавлен в [PQ-004](../04_PQ-004_raw-revisions-ux/00_thread.md).

Открытый вопрос: нужен ли отдельный rollback именно для последних committed revisions, или proposal-before-commit + обычный restore уже закрывают этот UX.


### Сводка 6 — proposal живёт до явного разбора

Пользователь предпочитает, чтобы proposal не был ephemeral runtime state. Он должен сохраняться до тех пор, пока пользователь с ним явно не разберётся.

Продуктовое следствие:
- proposal переживает reload/закрытие страницы и следующий session;
- pending proposal должен быть видим как незавершённое действие;
- нормальные terminal outcomes: Accept/Apply или Reject;
- техническое место хранения pending proposal пока не фиксируется;
- proposal по-прежнему не является committed revision и не должен попадать в обычную History до Apply.


### Сводка 7 — scope, stale и supersede

Proposal должен явно знать, к чему он относится и на каком состоянии был построен. На продуктовом уровне достаточно фиксировать:
- target (entry / tags / metadata / другое);
- kind/workflow (grammar, rewrite, add existing tags, create tags и т.п.);
- base revision/state, относительно которого proposal рассчитан;
- affected scope/fields;
- lifecycle status.

Несколько proposals могут существовать параллельно, если их scope не конфликтует (например, tags + grammar).

Если underlying target изменился, proposal не обязательно удалять: его лучше пометить stale/conflicted. Применять его в один клик нельзя, пока он не проверен/перегенерирован/rebased.

Новый rerun того же workflow для того же target/scope может supersede предыдущий proposal. Временного auto-expiry по умолчанию не предполагается: pending proposal живёт до явного resolution или supersede.


### Сводка 8 — scope current vs future

Пользователь предложил не раздувать PQ-005 гипотетическими destructive workflows, которых сейчас нет.

Уточнение scope:
- merge/split entries откладываются в future backlog;
- массовые AI-изменения и AI-delete не являются текущими заявленными workflows и не должны влиять на MVP-policy без отдельного реального use case;
- смена/уточнение даты остаётся релевантной, потому что Inbox-to-Entry уже умеет infer `entryDate`;
- отдельный риск смены даты не столько в самом metadata field, сколько в последствиях для chronology/derived views и текущей file convention, где дата входит в folder path/name;
- при первоначальном ingestion дата может быть inferred автоматически с confidence/needs_review; изменение даты уже существующей entry AI-ом лучше рассматривать как proposal, если это не прямое действие пользователя.

**Решение:** —
