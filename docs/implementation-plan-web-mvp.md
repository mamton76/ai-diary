# AI Diary — план реализации Web/API MVP

**Актуально на:** 2026-11-08  
**Статус:** предлагаемый delivery roadmap **из уже принятых архитектурных и продуктовых решений**, не календарный график. Фазы и приоритеты — рабочая организация выполнения; это **не отметки о готовом коде**.  
**Основная архитектура:** [architecture.md](architecture.md)  
**Требования:** [requirements inventory](baseline/02-requirements-inventory.md) · [architecture questions](baseline/04-open-questions.md)  
**Legacy Android plan:** [todo.md](todo.md) отражает прежний стек и не является планом нового web/backend MVP.

**Этапы продукта:** каноническая таблица E0–E4, интеграционного этапа и Later — [03-product-baseline.md §22.1](baseline/03-product-baseline.md#221-канонические-этапы-продукта) ([PQ-012](baseline/04-open-questions.threads/47_PQ-012_mvp-stage-scope/00_thread.md)). Этот план задаёт порядок работ и сопоставляет с ними фазы P0–P7.

## Принципы последовательности

1. Сначала получать проверяемую пользу на **существующих данных и имеющихся Calendar→Drive scripts**, а не переписывать всё ради идеальной архитектуры.
2. Границы `CaptureItem`, canonical Entry/Revision/Asset и backend/domain mutation authority — foundation для всех каналов; не дублировать это в scripts, Telegram, Calendar Timeline или MCP.
3. **Calendar Inbox и read-only Timeline ранние**: календарь позволяет видеть реальные обработанные записи и валидировать результат до полного сайта.
4. Реализовать web **маленькими полезными срезами**, а не ждать всей функциональности большого Screens Spec. Mobile/desktop адаптивность учитывать с первого slice.
5. Не смешивать **согласованное поведение** с **техническими drafts** и **проверенной реализацией**. Никаких принудительных миграций по одному лишь design draft.
6. Одна развёрнутая среда; PR CI → manual deployment, с rollback. Без обязательной параллельной staging infrastructure.

## P0. Проверка существующих активов и определение тестового набора

**Статус (2026-11-08):** статический аудит user-provided Abacus scripts **проведён**: [точная карта файлов, risks, приоритет fixes](audits/2026-11-08-abacus-diary-scripts.md). Все девять Python модулей синтаксически компилируются без выполнения. Live deployment, реальные Google API операции и crash recovery **не проверялись**; весь P0 не завершён.

**Особенно важно:** текущий `gcal_to_inbox.py` переносит событие в «Processed» после сохранения raw package, **до** `input_to_entry_2.py`; при падении второго шага возможен разрыв. Сквозная идемпотентность `source event → Entry` и recovery — следующий обязательный gate до изменения живого workflow.

## P0.1. Оставшиеся изолированные проверки

**Зачем:** пользователь сообщил, что уже есть scripts, переносящие записи из Calendar на Drive. Состав и код ещё не аудированы в рамках этого roadmap.

**Временные правила оператора до storage v1 ([AQ-OPS-006](baseline/04-open-questions.threads/51_AQ-OPS-006_live-scripts-interim/00_thread.md)):** скрипты пишут в реальный дневник. После сбоя `/sync2` не перезапускать, пока не проверены `inbox/` и `entries/`; не запускать `--apply-exact-duplicates`; дубли искать отчётом report-only. Изменения кода скриптов вносятся через Abacus отдельной задачей.

**Работы:**
- Найти реальные scripts и workflows (их репозиторий, точные пути, конфигурацию, права Google API); пометить, что запускается сейчас, а что осталось только в документации.
- Сопоставить текущие входы/выходы с historical project workflow `04_Workflow_Google_Calendar_Inbox.md` / [CaptureItem contract](baseline/04-open-questions.threads/41_AQ-INT-004_capture-item-contract/00_thread.md).
- Проверить source event IDs, повторный импорт, raw snapshots, output filenames, idempotency, provenance, ошибки и ручные шаги.
- Подготовить небольшой синтетический тестовый календарь/набор CaptureItems и Entry (без реальных личных текстов в тестовых logs/fixtures).
- Выделить reusable части скриптов и необходимые изменения, не обещая автоматический перенос старых файлов без migration plan.

**Готово, когда:** есть короткая карта `existing component → keep/adapt/replace` с точными путями; локально воспроизводится минимальный импорт одного тестового input с фиксацией результата и повтор без дубля. **Не считать этот пункт выполненным до code audit.**

## P1. Backend, portable canonical repository и надёжный capture

**Минимум:**
- Kotlin/Ktor backend skeleton и REST+JSON/OpenAPI; stable internal user ID, Google login и отдельно Google Drive/Calendar OAuth permissions.
- Domain-level storage/repository contract поверх portable user-owned canonical files (первым — Drive). Первый files-only slice без обязательной permanent DB.
- Entry / immutable Revision / provenance / CaptureItem / Asset identity + исходные payload references.
- Durable command envelope + worker/queue для canonical mutations. `Save` подтверждать только после committed result; safe retry/idempotency и видимые failure/conflict states.
- Draft/working state и storage-level concurrency checks в соответствии с [functional requirements](baseline/AI-Diary-Functional-Spec-v0.1.md). Не утверждать физический v1 format до review draft.
- Базовые структурированные технические логи и app-level run status, без журналирования приватного содержимого.

**Готово, когда:** тестовый CaptureItem безопасно превращается в читаемую Entry с raw/provenance, повтор той же операции не создаёт вторую Entry/Revision; Save/Restore проверены на сбоях и не показывают ложный success. Есть безопасный путь восстановления state после рестарта. Реальные данные ещё не нужны.

**Технические решения по ходу реализации:** выбрать конкретный durable queue provider/storage и схему публикации commit; пройти review [file-format draft](baseline/07-file-format-v1-draft.md) и [save/recovery draft](baseline/08-save-recovery-design.md).

## P2. Ранний Calendar Inbox + Calendar Timeline

**Не ждать полной web-панели.**

**Calendar Inbox:**
- Адаптировать найденные Calendar→Drive scripts к нормализованному CaptureItem вместо локальной финальной Entry schema.
- Idempotent import по Google event identity/version; raw event snapshot сохранён; ошибки и повторный запуск предсказуемы.
- Начать с ручного запуска импорта небольшого набора, не блокируя сценарий на расписании sync.
- Web-кнопка «Синхронизировать сейчас» и счётчик «ожидает импорта» на Обзоре появляются с первой web-версией (INT-009, [PQ-017](baseline/04-open-questions.threads/55_PQ-017_web-calendar-sync/00_thread.md)); до этого — ручной запуск без web.
- Не удалять внешние события/исходные записи; если workflow переносит event в processed calendar, эта операция не должна быть единственным подтверждением успешного canonical commit.

**Calendar Timeline:**
- Из committed Entries создавать/обновлять derived Calendar events, **один event на Entry**.
- Тестировать update того же event после новой Revision; раздельное ведение внешнего sync state.
- Исключить обратные изменения дневника от ручных edits Calendar event (view-only, no write-back).
- Отметить реальную разницу между event time / capturedAt / entry event date в тестах.

**Готово, когда:** на тестовых данных можно проследить полный путь `Calendar Inbox → canonical Entry → Calendar Timeline`, увидеть результат в Google Calendar и повторить pipeline без дублей и потери provenance. **Это наш первый end-to-end milestone для визуальной проверки.**

## P3. Web slice: техническое чтение, первая пользовательская версия, поиск и Обзор

Этапы экранов определены в [Screens Spec](baseline/AI-Diary-Screens-Spec-v0.1.md). Веб-клиент хранится как исходный код проекта, использует общий API и поддерживает телефон и desktop.

1. **E0 — технический срез чтения.** Вход и доступ к дневнику, список существующих записей, открытие записи и уже связанных материалов, состояния загрузки и ошибок. Читаем canonical files через backend; DB/index для этого среза не требуется.
2. **Первая пользовательская веб-версия — лёгкая правка.** В том же EntryScreen можно изменить заголовок и текст существующей записи, сохранить или отменить правки. Редактор поддерживает базовое форматирование, тело хранится в Markdown. Уже действуют Draft/recovery, проверки конкурентных правок и надёжный Save: изменения создают новую immutable Revision, исходник, прежние версии и связи с материалами сохраняются. Поиск и интерфейс истории не являются условиями этой поставки.
3. **E1 — поиск, фильтры и Обзор.** Подключаем поиск по заголовку и тексту, фильтры и сортировки через восстанавливаемый индекс. Календарь, облако тегов и доступные счётчики Обзора открывают соответствующие выборки; счётчики черновиков и предложений AI подключаются по готовности функций. После canonical changes индекс обновляется асинхронно; предусмотрены reconciliation и полная перестройка.

**Готово, когда:** E0 читает существующие записи с телефона и desktop; первая пользовательская версия надёжно сохраняет правку без потери исходника и вложений; E1 позволяет находить записи и открывать те же выборки из Обзора. Готовность проверяется отдельно для каждого среза.

**Решения для реализации:** [AQ-WEB-001](baseline/04-open-questions.md#aq-web-001--frontend-stack), [AQ-WEB-002](baseline/04-open-questions.md#aq-web-002--feature-parity-на-телефоне), [AQ-WEB-006](baseline/04-open-questions.md#aq-web-006--chatgpt-sites-или-обычный-web-проект); для статусов фоновых задач — [AQ-WEB-004](baseline/04-open-questions.md#aq-web-004--live-updates).

## P4. Полный веб-редактор, история и управление записями (E2)

- Расширить общий EntryPanel: полноценное редактирование, создание записи через тот же редактор, архив и корзина записей.
- Добавить галерею ревизий, сравнение Previous / Selected и Restore как новую ревизию с provenance.
- В редакторе доступны загрузка и выбор существующего материала. Отдельный лёгкий экран «Материалы» показывает сохранённые файлы, включая непривязанные, позволяет просмотреть или открыть файл и восстановить его из корзины. Он использует тот же каталог и хранилище. Расширенные поиск, фильтры, метаданные и окончательное удаление материалов поставляются позже.
- Сохраняются общие Draft/Save/lease/conflict rules. Каталог тегов остаётся этапом E3; AI-запуски и проверка предложений — E4.

**Готово, когда:** можно создать и отредактировать запись, архивировать, удалить в корзину и восстановить по согласованным правилам; можно сравнить версии, восстановить старое содержимое новой ревизией и повторно использовать материал из общей библиотеки.

## P5. Telegram capture — после Calendar, независимо от AI editor

- Приватный 1:1 bot, безопасная revocable account linking; первая очередь text/voice.
- Сохранение каждого исходного Telegram message отдельно, дедупликация source ID; два уведомления: `Сохранено в Inbox`, затем реальный processing outcome.
- Telegram Reply на сообщение незавершённой сессии — продолжение независимо от времени; без Reply — новая открытая сессия.
- Явное `Готово` завершает серию; привязка к конкретному рассказу, при неоднозначности — выбор. Голосовое «готово» — целевое UX с безопасным fallback; не запускать AI автоматически по тайм-ауту.
- Незавершённые рассказы видны в web Inbox. Media/video/files/links/forwarded content — в целевом scope, **внедрить отдельной итерацией после text/voice**.

**Готово, когда:** с одного привязанного аккаунта можно создать, продолжить, завершить и проверить обработку серии сообщений, не смешивая другие рассказы, без лишних AI calls и без приёма сообщений от чужих пользователей.

## P6. AI workflows: минимальная полезная обработка

- Сначала provider-neutral Kotlin adapter с одним подтверждённым provider/model, capabilities, error/usage data.
- Первый полезный workflow: например, извлечение существующих тегов / метаданных с traceable proposal/result. Не начинать с полного AI suite или semantic memory.
- User-owned versioned workflow definitions, trusted executors / capability profiles, Draft → Publish и snapshot Test runs по [AI workflow baseline](baseline/07-ai-workflow-architecture.md); editor UX [AQ-AI-008](baseline/04-open-questions.threads/39_AQ-AI-008_workflow-editor-ux/00_thread.md) уже описан.
- На Entry — отдельный AI workflow runner и review/apply, без inline-AI editing в text editor.
- Monthly AI budget + cost alerts, blocked queue `Ожидает бюджета`, ручное возобновление по default, optional auto resume.
- Не запускать sending real personal content to external LLM до согласования [AQ-AI-006 sensitive-data policy](baseline/04-open-questions.md#aq-ai-006--sensitive-data-policy). Также закрыть [AQ-AI-003](baseline/04-open-questions.md#aq-ai-003--где-хранить-run-records), [AQ-AI-004](baseline/04-open-questions.md#aq-ai-004--context-building), [AQ-AI-005](baseline/04-open-questions.md#aq-ai-005--prompt-customization), [AQ-AI-007](baseline/04-open-questions.md#aq-ai-007--structured-outputs--validation) до соответствующей production-функции.

**Готово, когда:** один run с явными inputs/provider/version и spend limit воспроизводимо создаёт проверяемый результат/Proposal, пользователь может принять/отклонить его, а неудачный или отменённый run не портит canonical Entry.

## P7. Ранний optional MCP proof of concept

**Не blocking milestone.** Может быть выполнен после P1/P2 параллельно web/Telegram в небольшом изолированном spike.

- Тонкий remote MCP server поверх существующего backend/domain API, без второго механизма записи canonical files.
- Тестовые tools: `save_capture`, `finish_capture`, `get_capture_status`; продумать identity/OAuth, права, write confirmation и idempotency.
- Проверить конкретный клиент (например, Claude remote MCP), ограничения подписки/voice mode; не утверждать, что MCP автоматически работает в Gemini Live/ChatGPT Voice.
- Результат — записанный outcome test и решение `promote / defer`; ни один другой milestone не зависит от MCP.

## Обязательные поперечные проверки

| Область | Gate |
|---|---|
| Canonical safety | raw, Entry, Revisions, Assets и provenance сохраняются; conflict/restore не удаляют историю |
| Import/idempotency | повтор источника или команды не создаёт duplicate entries/commits |
| Single writer | к первому mutating release web единственный писатель canonical-данных — backend; Abacus-скрипты вызывают API или не пишут в canonical-хранилище ([AQ-OPS-006](baseline/04-open-questions.threads/51_AQ-OPS-006_live-scripts-interim/00_thread.md)) |
| Operations | queued/committed/failed различаются; safe restart/retry; нет автоповтора ambiguous paid LLM |
| Backup | документированные on-demand restore scripts проверены в изолированном хранилище |
| Security | Google auth/OAuth separation, минимальные scopes, server-side credentials, no diary content in debug logs |
| Costs | Cloud budgets/alerts; monthly AI budget и pause/notification/resume policy |
| Quality | PR build/test/lint, ручное развёртывание единственного окружения, возможен rollback |
| Portability | canonical можно прочитать без operational DB; derived indexes/timeline восстанавливаются |

## Решения, которые ещё не следует считать принятыми

### Web — 5

| ID | Вопрос | Когда нужен |
|---|---|---|
| AQ-WEB-001 | Frontend framework/tooling | До P3 |
| AQ-WEB-002 | Mobile feature scope/parity | До P3/P4 |
| AQ-WEB-004 | Live refresh: polling, SSE, WebSocket | До job-status UX |
| AQ-WEB-005 | Первый implementation scope History/Diff/Restore | До P4 |
| AQ-WEB-006 | Роль ChatGPT Sites vs обычный web client | До P3 |

**AQ-WEB-003 закрыт:** toolbar Markdown editor; inline AI не нужен в первом редакторе.

### AI — 5

| ID | Вопрос | Когда нужен |
|---|---|---|
| AQ-AI-003 | Canonical/operational storage run records | До persistent production runs |
| AQ-AI-004 | Context building/material selection | До cross-entry workflows |
| AQ-AI-005 | Prompt customization boundaries | До user prompt customization |
| AQ-AI-006 | Sensitive data, consent, retention | **Решён** ([тред](baseline/04-open-questions.threads/48_AQ-AI-006_sensitive-data-policy/00_thread.md)); PRIV-002, PRIV-005…009 — gate до реальных external AI calls |
| AQ-AI-007 | Structured outputs validation/repair | До metadata-changing AI workflows |

**AQ-AI-008 закрыт:** workflow editor UX принят и внесён в Screens Spec. Не открывать заново.

## Ближайшее конкретное действие

**P0 — audit существующего Calendar→Drive pipeline и сопоставление с CaptureItem + Entry/Revision contracts.** Это лучший старт для нашего нового плана: он опирается на уже работающие пользовательские инструменты и даёт список реальных файлов/изменений, а не очередное архитектурное предположение.

Не разворачивать новое production окружение и не мигрировать реальный diary storage, пока не проверены скрипты, схемы и восстановление на тестовом наборе.
