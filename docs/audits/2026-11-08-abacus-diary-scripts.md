# AI Diary — статический аудит действующих Abacus scripts

**Дата:** 2026-11-08  
**Источник:** пользовательский архив `ai-diary-scripts.zip` из текущего разговора (18 файлов: 9 `.py`, 6 `.md`, README, `.env.example`, `.gitignore`).  
**Scope:** статическое чтение Python-кода и bundled docs, проверка компиляции Python source без выполнения. **Никакого запуска Google API, Telegram, Abacus, реального Drive или Calendar не было.** Факт реальной эксплуатации предоставлен пользователем.  
**Target:** [архитектура](../architecture.md), [план](../implementation-plan-web-mvp.md), [CaptureItem contract](../baseline/04-open-questions.threads/41_AQ-INT-004_capture-item-contract/00_thread.md).

## 1. В действительности уже существует

```text
Google Calendar diary inbox
  → gcal_to_inbox.py
  → Google Drive inbox/new/<source package>/
  → input_to_entry_2.py
  → Google Drive entries/YYYY/MM/<entry>/
  → gcal_projection.py
  → Google Calendar diary timeline

diary_sync_agent.py = Telegram command/control bot
  /sync, /sync1, /sync2, /sync3, /status
  (orchestration, НЕ сохранение пользовательских voice/text messages)
```

Это **реально написанные операции**, а не только описание будущей функциональности. `input_to_entry_2.py` строит Entry из raw text + metadata с эвристиками даты/заголовка, создаёт raw revision, копию originals и links; **LLM-преобразования, AI proposal/review и tag enrichment в этом 3-step sync отсутствуют**.

### Карта компонентов

| Файл | Назначение | Рекомендация |
|---|---|---|
| `gcal_client.py` | OAuth, calendar lookup/list/move | **Reuse/adapt**: thin adapter, пересмотреть scopes/credentials/event identity |
| `mamton_drive_client.py` | Google Drive list/create/copy/move, JSON/text | **Reuse/adapt**, но перенос canonical mutations только под backend/domain policy, concurrency |
| `drive_client.py` | Import alias | **Keep** лишь для старых скриптов, новый contract отдельно |
| `gcal_to_inbox.py` | Calendar → raw Drive inbox package | **Reuse/adapt**: source snapshots уже есть; улучшить transaction/retry/idempotency |
| `input_to_entry_2.py` | Raw inbox → Entry/Revision/originals | **Reuse logic & fixtures**, но **заменить прямую multi-file запись** на unified durable backend/domain commit |
| `gcal_projection.py` | Entry → Calendar event с external sync index | **Reuse/adapt**: one-way sync соответствует продукту; исправить limited scan, retry window/idempotency |
| `diary_sync_agent.py` | Telegram-пульт последовательного запуска трёх Python процессов | **Keep as temporary operator tool**; не путать с Telegram diary capture adapter; позже заменить orchestration durable jobs |
| `find_entry_duplicates_drive.py` | Отчёты по дубликатам Drive; optional archive | **Reuse report-only**, не запускать auto-archive на реальных данных до аудита |
| `find_entry_duplicates_v2.py` | Аналог для локальных папок | **Reuse matching/test heuristics** после исправления; offline validation/forensic utility |

Полезные baseline/fixtures: `MESSAGE.json`, `source_event.json`, `raw_text.md`, `ENTRY.json`, `entry.md`, `revision.json`, `PROCESSING_RESULT.json`, `source_raw_inputs.json` и внешние index/log records. Названия файлов и версия `v0.1.0` отражают **нынешний legacy format**, а не автоматически утверждённый будущий format v1.

## 2. Конкретные расхождения/риски (по исходным строкам)

### S1 — High: «Processed Calendar» фактически означает *imported*, а не готовую Entry

- `gcal_to_inbox.py:567–637`: после `create_calendar_package()` событие сразу переносится в processed Calendar, **без вызова `input_to_entry_2.py`**. Комментарий в header (lines 14–16) это явно подтверждает.
- Исторический `04_Workflow_GCal_Inbox_To_Entry.md` описывает перемещение после успешной Entry creation. Это две разные семантики.
- Если второй шаг не создаёт Entry, событие уже не находится в Calendar Inbox. Raw package может остаться в `inbox/new/`, но пользовательский Calendar создаёт впечатление завершённости.
- **Рекомендация:** в новом end-to-end status различать `raw_imported`, `entry_committed`, `projection_synced`; перевод в «Processed» либо делать после Entry commit, либо явно переименовать календарь/статус в «Imported». Пока не менять поведение live workflow без отдельной проверки.

### S2 — Critical: Inbox → Entry не имеет атомарного commit/idempotent recovery

- `input_to_entry_2.py:699`: новый случайный Entry ID для каждой попытки.
- `input_to_entry_2.py:742–801`: последовательные Drive операции — копирование/перенос raw, создание folder, `ENTRY.json`, `entry.md`, revision, links, архивирование raw, потом `PROCESSING_RESULT.json`. Не атомарны как один commit.
- После прерывания между отдельными шагами могут остаться частичные Entries, уже перемещённый raw или повторные Entries при повторном запуске. Для flat files raw перемещается **до создания Entry** (line 753).
- **Рекомендация:** stable idempotency key от source ID, per-input durable processing state, staged write + explicit commit/publication, retry/reconciliation, verified raw references. Согласовать с техническими review drafts file-format и Save/recovery.

### S3 — High: ограничения dedup и recovery у Calendar import

- `gcal_to_inbox.py:114–127`: raw identity = hash(`calendarId|eventId|start_dt`). Изменение времени события изменит raw ID; single event не обязан становиться новым исходником при изменении даты.
- `gcal_to_inbox.py:303–324`: guard ищет в JSONL import log, затем только `inbox/new/`, **не сканирует `inbox/archived` и `_processed_raw`**. Потеря/несогласованность индекса ухудшает защиту от повторного импорта.
- `gcal_to_inbox.py:420–440`: package folder создаётся перед тремя файлами; partial folder при error блокирует следующий `create_calendar_package` по одному только существованию папки (lines 421–423).
- `gcal_to_inbox.py:327–353`: import log переписывается read-modify-write в одной Google Drive JSONL; concurrent writers могут потерять update.
- **Рекомендация:** immutable source ID + source revision/version отдельно, recoverable per-source import state и reconciliation по canonical raw, запрет «skip because log says so» без проверки данных. Event move/mark done — отдельный recoverable action.

### S4 — High: Timeline ограничен **первыми** N Entries, поэтому новые записи могут не синхронизироваться

- `gcal_projection.py:617–634, 637–660`: recursive traversal прекращается при `len(results) >= limit`, до сортировки по датам; это первые папки в лексикографическом порядке.
- `diary_sync_agent.py:211`: `--limit 100` для projection. Если доступных записей больше ста, поздние могут никогда не попасть в рассмотрение при повторных `/sync` (первые сто каждый раз те же).
- **Рекомендация:** cursor/delta/updatedSince или полный проход с ограничением **числа мутаций**, а не кандидатов; dirty/reconciliation queue, full rebuild mode.

### S5 — High: Calendar event может создаться, а index не обновиться

- `gcal_projection.py:1172–1213`: внешнее создание/обновление event идёт до `upsert_sync_record`. Если второй шаг упадёт, следующая попытка может создать ещё один event (нет сохранённого `googleEventId`).
- `gcal_projection.py:1149–1158`: при равном hash index говорит `up to date` без проверки, не был ли event удалён вручную. Внешние manual edits не пишут обратно в diary, как и требуется, но могут оставаться до следующей canonical change.
- **Рекомендация:** deterministic mapping через private `aiDiaryEntryId` и reconciliation external event lookup, безопасный retry after unknown outcome; index derived, rebuildable.

### S6 — Medium/High: Telegram orchestration сообщает успех по exit code процесса, а не итогам items

- `input_to_entry_2.py:827–849, 899–919`: отдельные failures собираются как `ProcessResult(status="failed")`, после чего `main()` обычно заканчивается exit code 0.
- `gcal_to_inbox.py:566–638, 681–744`: ошибки отдельных events учитываются в results, но `main()` обычно выходит с code 0.
- `diary_sync_agent.py:151–155, 221–238`: `ok = result.returncode == 0` → Telegram может сообщить «✅ шаг успешно», несмотря на failed items; выполнение следующего шага не останавливается при ошибке предыдущего.
- Bot в lines 267–291 поддерживает **только команды оператора**, не Telegram voice/text diary captures; запрещено считать его уже готовым Telegram capture channel.
- **Рекомендация:** structured machine-readable outcome per command/job, normalized success/partial/failure, durable job status, separate capture bot later.

### S7 — Medium: Duplicate finder **не сравнивает похожие тексты**, а сравнивает хеши

- `find_entry_duplicates_drive.py:367–373`: `jaccard_tokens(a.normalized_hash,b.normalized_hash)` / `sequence_similarity(a.normalized_hash[:2000],b.normalized_hash[:2000])`, не сами normalized bodies. Аналогичный алгоритм в `find_entry_duplicates_v2.py`.
- Из-за avalanche property SHA-256 похожие тексты почти всегда имеют непохожие hashes; эвристика `similar_text` практически не работает. Exact duplicates hash groups полезны, но `--apply-exact-duplicates` может перемещать целые Entry folders по совпадению одного текста, **не учитывая ценность разных revisions/assets/provenance**.
- **Рекомендация:** сохранять normalized text/tokens для similarity, hash — только для exact match. Только отчёты до user-approved merge/archive по canonical domain rules.

### S8 — Medium: безопасность, формат, документация

- `gcal_client.py:31–36` и `gcal_projection.py:68–71`: broad `drive` и `calendar` scopes объединены в один token. В новой системе scopes следует минимизировать по назначению.
- `diary_sync_agent.py:88–104`: текущий доступ к боту по одному configured chat ID; нет revocable привязки Telegram user ↔ account по кодам из AQ-INT-003.
- `input_to_entry_2.py:163`: default local timezone Europe/Belgrade; `infer_date_from_name_or_metadata` и Calendar `entryDate` требуют проверки различия capture time и event date.
- `README.md` называет `ai_diary_drive_client.py`/`inbox_to_entry_drive.py`, но в архиве актуальные имена `mamton_drive_client.py`/`input_to_entry_2.py`. `04_Workflow_GCal_Inbox_To_Entry.md` ссылается на `gcal_inbox_to_entry.py`, которого нет.
- Архив содержит `.env.example` c placeholders и `.gitignore`, **не содержит** `.env`, `google_token.json`, `google_credentials.json` или явных файлов ключей. Это не гарантирует отсутствие секретов в любых runtime локациях Abacus; хранилище секретов и grants отдельно не проверялись.

## 3. Статус проверки

- Прочитаны все 9 Python files (names + code structure), README, env example и relevant workflows.
- Все 9 Python modules успешно прошли **static Python syntax compilation** без запуска; это **не тест API behaviour**.
- **Не выполнены**: запуск against Abacus, подтверждение версий развернутых scripts, проверка auth, Google scopes/permissions, live Drive/Calendar, восстановление с simulated crash, тесты end-to-end, реальные объемы/скорость и review of runtime logs. Если живые файлы отличаются от ZIP, результаты надо пересмотреть.
- **P0 частично выполнен:** static inventory and risk audit done; live compatibility verification и isolated fixture tests remain.

## 4. Предложенный ближайший безопасный change set

**Не менять работающие Abacus scripts прямо сейчас.** Сначала открыть отдельную ветку/копию с тестовыми Google calendars/folders или полностью mock Drive/Calendar.

1. Добавить минимальные fake Drive/Calendar integration tests: normal event, duplicate delivery, same event time edited, missing `source_event.json`, interrupted package creation, interrupted Entry commit, interrupted Timeline create/index, `>100` entries.
2. Сделать `source event → CaptureItem → Entry` идемпотентным по стабильному source identity; гарантировать recovery после interruption **без рандомной новой Entry при повторе**.
3. Ввести явные статусы `raw_imported / entry_committed / calendar_projected`; согласовать, когда именно move в Calendar Processed должен происходить.
4. Убрать лимит scan первых N для Calendar projection или заменить delta/cursor strategy.
5. Отделить operator Telegram bot от будущего Telegram capture UX и сделать statuses machine-readable.
6. После этого перенести проверенную логику в Kotlin/Ktor adapter/domain API, а Python scripts оставить временным совместимым источником и инструментом теста.

**Один следующий шаг для реализации:** подготовить **изолированный replay test** из нескольких синтетических Calendar events и fake Drive operations, демонстрирующий дубликат на interrupted Inbox→Entry Save, после чего исправить его через stable source ID + recoverable processing state. Это уменьшает риск повреждения реального дневника и создаёт foundation для остальных интеграций.
