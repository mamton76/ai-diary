# AQ-DATA-005 — Asset storage

**Источник:** [04-open-questions.md / AQ-DATA-005](../../04-open-questions.md#aq-data-005--asset-storage)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Где физически хранятся originals и производные media/assets AI Diary: в том же user-owned Drive/file backend, в отдельном object storage или в hybrid-модели?

## Варианты

1. **Drive/file storage only** — originals и при необходимости previews/thumbnails живут в user-owned file storage.
2. **Object storage only** — media живёт в отдельном managed object storage, а canonical diary files содержат ссылки/metadata.
3. **Hybrid** — originals остаются в user-owned storage, а производные previews/thumbnails/cache могут жить в отдельном rebuildable storage.

## Контекст

Уже принято:

- user-owned portable files являются canonical source of truth;
- Google Drive — первая практическая реализация storage, но domain не должен зависеть от Drive;
- Asset имеет собственную identity и может быть связан с несколькими Entries;
- versioned связь мыслится как `EntryRevision ↔ Asset`;
- originals media должны сохраняться;
- Entry edit различает link existing Asset и create new Asset;
- unlink Asset от Entry и system-wide delete — разные операции;
- конкретный media backend до сих пор оставался открытым;
- нужно учитывать размер файлов, previews/thumbnails, streaming, portability, backup и cost.

## Обсуждение

### Сводка 1 — вопрос шире, чем Drive vs object storage

В ходе обсуждения уточнено, что Asset не всегда обязан быть файлом, физически скопированным в storage AI Diary. Нужны как минимум два storage/source mode:

- **managed** — AI Diary управляет original в своём/user-owned storage;
- **external** — authoritative original остаётся у внешнего provider/source, а AI Diary хранит устойчивый reference/locator и metadata.

Пример external mode — media из Google Photos или другой внешний URL/provider reference. Импорт внешнего original в managed storage может быть отдельной операцией, но не является обязательным свойством каждого Asset.

### Сводка 2 — сначала контракт Asset, потом storage implementation

Минимальное ядро Asset:

- stable `assetId`;
- `kind`: image / video / audio / document / link / other;
- описание authoritative original:
  - mode: managed | external;
  - storage/provider identifier;
  - locator/objectRef/path/externalId/url;
- минимальные технические metadata:
  - mimeType;
  - filename/title fallback;
  - size, если известно;
  - dimensions/duration, если применимо и известно;
- provenance/source: upload, import, Google Photos, Telegram и т. п.;
- createdAt;
- checksum/hash для managed files допускается как implementation detail/optional metadata.

Точный provider-specific locator не должен протекать в domain contract.

### Сводка 3 — derivatives не являются original Asset

Thumbnail, preview, transcoded media, waveform и другие представления не входят в authoritative original Asset. Они считаются **derivatives/cache**:

- могут храниться отдельно;
- могут быть provider-supplied или сгенерированы приложением;
- должны быть rebuildable там, где это возможно;
- их отсутствие не разрушает identity Asset и ссылку на original.

Это позволяет не требовать собственного preview storage для каждого external Asset и не заставляет заранее строить сложный media pipeline.

### Сводка 4 — совместимость с общей media library

Asset не должен быть жёстко owned конкретной Entry или только AI Diary. Уже принятая отдельная identity Asset должна позволять позднее использовать тот же Asset из ZoomAlboom или другого consumer:

`AI Diary EntryRevision ↔ Asset`

`ZoomAlboom Composition/Album/Scene ↔ Asset`

Отдельный Media Library service сейчас не вводится: это архитектурная граница/направление, а не требование строить новый сервис в MVP.

### Сводка 5 — storage choice остаётся adapter-level

Для первого managed storage естественным остаётся user-owned Drive/file backend. External Assets могут оставаться внешними references. Поэтому система по факту допускает hybrid-модель, но без обязательного отдельного object-storage слоя.

Отдельный object storage, собственные previews/transcodes и media CDN вводятся только при реальной необходимости по размеру, streaming/performance или cost.

**Решение:** [принято] (2026-09-27) Asset имеет stable identity и минимальный storage-independent contract: kind, authoritative original reference, basic technical metadata и provenance/source. Original поддерживает как минимум managed и external modes; external media не обязана автоматически копироваться в AI Diary storage. Preview/thumbnail/transcode/waveform и другие представления являются отдельными rebuildable derivatives/cache, а не частью authoritative original. Managed originals в первом MVP могут жить в user-owned Drive/file backend; конкретные provider/object-storage механизмы остаются adapter/implementation detail. Asset не должен быть жёстко owned Entry и модель должна допускать позднее общую media library для AI Diary и ZoomAlboom без требования выделять отдельный media service сейчас.

