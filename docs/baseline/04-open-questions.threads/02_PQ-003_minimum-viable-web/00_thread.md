# PQ-003 — Какой minimum viable web?

**Источник:** [04-open-questions.md / PQ-003](../../04-open-questions.md#pq-003--какой-minimum-viable-web)  
**Статус:** решён  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Какой минимальный web slice AI Diary уже достаточно полезен, чтобы считать его первой настоящей web-версией, а не просто демонстрацией?

## Варианты

1. **Read-first:** login + list/timeline + read + search/filter; создание и редактирование позже.
2. **Basic CRUD:** login + list/timeline + read + create + basic edit; search/filter можно частично отложить.
3. **Useful daily web:** login + list/timeline + read + create + edit + search/filter + tags + basic history visibility.
4. **Capture-first web:** прежде всего быстрый capture/create на desktop/mobile, а полноценный browse/edit на следующем шаге.

## Контекст

Baseline уже предполагает полноценный адаптивный web-клиент, а не старый thin/read-only UI. При этом первый slice должен оставаться небольшим и проверять продуктовую ценность, не затягивая в revisions UX, сложный AI UI, semantic search и admin/debug tooling.

Это голосовой тред: разговор не стенографируется. В файл попадают только смысловые сводки и явно принятые решения.

## Обсуждение

### Сводка 1 — старт обсуждения

Тред открыт. Пока решения нет.


### Сводка 2 — приоритеты первого web-цикла

Рабочее направление пользователя — развивать web по ступеням, а не пытаться сразу дать весь функционал:

1. **Сначала browse/read/search existing entries** — открыть старые записи, удобно их просматривать и находить.
2. **Затем editing + versioning** — редактирование существующих записей с сохранением истории изменений.
3. **Затем tags** — видеть теги и уметь их править.
4. **Затем processing/AI workflows** — запускать обработку записей из web UI.

Это пока рабочий порядок, а не окончательно закрытый scope. В частности, отдельно надо уточнить, входит ли создание новой записи через web в первый/второй этап или capture пока остаётся через другие каналы.



### Сводка 3 — создание записи через web

Создание новой записи через web **не является необходимостью для первых этапов**: основной capture может пока идти через голос, Calendar и другие каналы.

При этом пользователь не считает web-create принципиально нежелательным. Если простая форма создания записи почти не увеличивает сложность реализации, её можно добавить opportunistically, но она не должна расширять scope или задерживать read/search/edit/versioning.


### Сводка 4 — minimum search и закрытие scope

Для первого search достаточно:

- обычного текстового поиска по entry content/title;
- даты или диапазона дат;
- фильтра по tags.

Semantic search, embeddings, cross-entry Q&A и более сложные filters не входят в первый web slice.

Таким образом первый полезный web slice — **browse/list + read + search/filter по тексту, дате и tags для существующих записей**. Следующий этап — **editing + versioning/history**, затем **просмотр/редактирование tags**, затем **AI processing/workflows**. Создание новой записи через web не является requirement первых этапов, но может быть добавлено opportunistically, если это не увеличивает scope и не задерживает основные шаги.

**Решение:** [принято] (2026-09-26) Первый web slice — работа с существующими entries: browse/list, read и search по тексту, дате/date range и tags. Дальше по приоритету: editing + versioning/history → tags view/edit → AI processing/workflows. Web create не обязателен в первых этапах и допускается как дешёвое дополнительное действие.
