# PQ-007 — Sharing входит в обозримый MVP?

**Источник:** [04-open-questions.md / PQ-007](../../04-open-questions.md#pq-007--sharing-входит-в-обозримый-mvp)  
**Статус:** решён  
**Состояние:** resolved  
**Claim:** none  
**Ведёт:** —  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../03-product-baseline.md и ../../02-requirements-inventory.md

## Вопрос

Нужен ли selective sharing в обозримом MVP настолько, чтобы уже сейчас влиять на auth/data model, или его можно оставить будущей функцией?

## Что здесь означает sharing

Речь не о социальной сети и не о совместном редактировании дневника.

Исторический PRD описывает sharing как selective sharing memory artifacts с близкими людьми:
- конкретная diary entry / moment;
- AI-generated summary;
- family memory;
- trip narrative;
- ZoomAlboom visual story.

Мотивация в старом PRD — retention/family use case: возможность иногда делиться памятью с партнёром/семьёй может повышать ценность и мотивацию вести дневник.

## Связанные источники

- [Product baseline §21 — Sharing](../../03-product-baseline.md#21-sharing)
- [Requirements inventory — Q. Sharing](../../02-requirements-inventory.md#q-sharing)
- [Historical PRD — Sharing and retention](../../../prd.md#sharing-and-retention)

## Варианты

1. **Out of scope** — не учитывать sharing в MVP и архитектуре.
2. **Future requirement** — сохранить как важный будущий сценарий, но не строить текущую auth/data model вокруг него.
3. **Near-term requirement** — уже сейчас заложить ownership/access model, потому что sharing нужен вскоре после MVP.

## Контекст

Текущий baseline уже говорит, что selective sharing потенциально полезен, но не должен определять базовую архитектуру без отдельного решения включить его в ближайший MVP.

**Решение:** [принято] (2026-09-27) Selective sharing не входит в обозримый MVP и не должен сейчас определять auth/data model. Сценарий сохраняется как future requirement / parking-lot item и возвращается в активную проработку только при появлении реального near-term use case.
