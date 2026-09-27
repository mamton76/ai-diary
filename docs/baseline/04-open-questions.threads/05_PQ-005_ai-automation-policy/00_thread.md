# PQ-005 — Насколько AI автоматичен?

**Источник:** [04-open-questions.md / PQ-005](../../04-open-questions.md#pq-005--насколько-ai-автоматичен)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
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


### Сводка 9 — что реально зависит от policy

Пользователь согласен с общим правилом per-workflow policy, но отметил, что не видит необходимости сейчас классифицировать каждое возможное metadata field отдельно.

Практический смысл решения для MVP:
- система должна различать auto-applied результаты и pending proposals;
- proposal должен быть persistent, иметь target/scope/base state и lifecycle;
- Accept/Apply — граница между proposal и committed revision;
- конкретная policy для title/people/place и других будущих metadata может определяться позже при появлении реального workflow;
- точные confidence thresholds и перечень auto-apply полей не являются blocking product decisions для текущей архитектуры.

### Сводка 10 — гранулярность AIResult и Proposal

Уточнено, что core product model не фиксирует жёсткую гранулярность proposal:

- один AI run / AIResult может породить один или несколько proposals;
- один proposal может быть как маленьким, так и комплексным: например одновременно менять text, date и несколько tags;
- «три добавляемых тега» не обязаны автоматически становиться тремя proposals;
- конкретную гранулярность определяет workflow и его UX, а не глобальная схема;
- Proposal остаётся единицей пользовательского решения, но в подробном review его отдельные части могут быть разобраны и смержены вручную.

Для traceability пользователь должен иметь возможность из Entry провалиться в полную AI activity и затем в детали конкретного run/result: какой input revision использовался, какой workflow/model работал, какие proposals были получены, что было auto-applied/accepted/rejected и какие committed revisions в итоге появились. На продуктовом уровне AIResult связывает run с его proposals/outcomes; точная storage schema относится к архитектуре.


### Сводка 11 — быстрый review и трёхсторонний merge

Согласован UX применения proposals.

На обычном Entry screen proposal показывается компактной карточкой/snippet:

- для бесконфликтного proposal доступны быстрые **Apply**, **Reject** и **Подробнее**;
- для stale/conflicted proposal быстрого Apply нет: доступны **Reject** и **Подробнее**;
- Apply/Reject на карточке относятся к proposal целиком.

**Подробнее** открывает единый трёхпанельный review/merge view:

```text
Base              Result              Proposal
read-only         editable            read-only
```

Во всех трёх панелях используется одна и та же структура Entry. `Base` — состояние, на котором строился proposal; `Proposal` — предлагаемый результат; `Result` — реальный будущий результат применения.

Правила merge:

- если current state не изменился относительно base, начальный Result фактически совпадает с Proposal;
- независимые изменения Current и Proposal могут автоматически объединяться в Result;
- conflict подсвечивается локально на конкретном field/fragment, а не на всём proposal;
- пользователь может для конфликтного участка оставить Current, взять Proposal или исправить Result вручную;
- для complex proposal в detailed mode допустимо фактически частичное принятие через ручное редактирование Result;
- после подтверждения создаётся **одна новая committed revision** с итоговым Result;
- до подтверждения Result является только merge draft и не попадает в History.

Этот review view должен использовать тот же переиспользуемый Entry content component, что обычный view/edit Entry; Base и Proposal read-only, Result editable.

**Решение:** [принято] (2026-09-27) AI automation policy задаётся per workflow/type of change. Первая normalized entry может создаваться автоматически при сохранённом raw и явной uncertainty; существующие теги могут auto-apply при высокой уверенности, новые теги по умолчанию идут через proposal, user-added tags AI сам не удаляет. Изменения существующего content/metadata через AI сначала являются persistent proposal и становятся committed revision только после Accept/Apply. Proposal хранит target/scope/base state, может быть stale/conflicted или superseded и живёт до явного resolution. Один AIResult может содержать один или несколько proposals, а proposal может быть простым или комплексным — гранулярность задаёт workflow. Бесконфликтный proposal можно быстро Apply/Reject; stale/conflicted proposal применяется только через подробный review. Detailed review использует Base | editable Result | Proposal, автоматически сливает независимые изменения, локально показывает conflicts и позволяет вручную собрать Result; подтверждение создаёт одну новую revision. Entry должен давать drill-down в полную AI activity/run provenance. Точные confidence thresholds и policy для будущих metadata/workflows определяются позже; merge/split отложены, bulk/delete не входят в текущий scope.