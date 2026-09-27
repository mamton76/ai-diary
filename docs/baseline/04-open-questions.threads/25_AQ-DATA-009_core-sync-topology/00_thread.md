# AQ-DATA-009 — Какая именно модель core data synchronization нужна?

**Источник:** [04-open-questions.md / AQ-DATA-009](../../04-open-questions.md#aq-data-009--какая-именно-модель-core-data-synchronization-нужна)  
**Статус:** обсуждаем  
**Состояние:** in_discussion  
**Claim:** active  
**Ведёт:** ChatGPT conversation  
**Режим фиксации:** voice-summary  
**Родитель:** —  
**Дочерние треды:** —  
**Куда переносим решение:** ../../02-requirements-inventory.md и architecture data design

## Вопрос

Какой authority/topology model нужен для синхронизации core diary data между clients, backend и canonical user-owned storage, чтобы разные клиенты работали с одним логическим дневником без silent loss?

## Уже принятый контекст

- canonical user data живут в user-owned portable files;
- clients работают через backend/domain repository, а provider-specific storage operations скрыты adapter layer;
- full offline-first не входит в MVP;
- один server-side working draft на Entry + local recovery snapshots;
- per-entry soft lease координирует активного mutation owner;
- committed mutation использует base revision/domain version;
- storage write защищён native conditional token, если storage это поддерживает;
- неожиданные external canonical changes проходят validation/reconciliation, без silent overwrite;
- derived DB/index может появиться позже, но остаётся rebuildable и не становится вторым canonical source.

## Кандидатные topology

1. **Clients → Backend → Canonical files** — backend/domain service координирует чтения/изменения, canonical storage остаётся source of truth.
2. **Clients → Backend → Operational DB → file projection** — operational DB становится фактической рабочей authority, что конфликтует с уже принятым files-canonical принципом, если projection не строго derived.
3. **Clients напрямую ↔ file storage** — клиенты сами синхронизируются с canonical storage; усложняет auth, concurrency и единый domain contract.
4. **Hybrid** — backend authority для mutation protocol, canonical files для durable truth, локальные/client/server caches только operational/derived.

## Не смешивать

Core diary sync — отдельно от:
- Calendar projection;
- capture queue;
- backup/export;
- future full offline sync.

## Обсуждение

**Решение:** —
