# Agent Workflow — Tag Enrichment

## 1. Workflow goal

Suggest and optionally apply tags to existing AI Diary entries.

This workflow reads structured entries from:

```text
entries/
```

and the tag catalog from:

```text
catalogs/tags/tags.json
catalogs/tags/aliases.json
```

It should enrich entries with tags while avoiding aggressive or speculative tagging.

---

## 2. Important principle

Tags are navigation tools.

They should help the user find and group diary entries.

The agent should not create too many tags and should not over-categorize every small detail.

Prefer a few useful tags over many noisy tags.

---

## 3. Input files

### 3.1 Entry

Each entry folder may contain:

```text
ENTRY.json
entry.md
revisions/
links/
ai/
```

The workflow should primarily read:

```text
ENTRY.json
entry.md
```

It may also read revisions if needed.

---

### 3.2 Tag catalog

```text
catalogs/tags/tags.json
catalogs/tags/aliases.json
```

Example `tags.json`:

```json
{
  "formatVersion": "v0.1.0",
  "items": [
    {
      "id": "tag_lis",
      "name": "Lis",
      "slug": "lis",
      "type": "pet",
      "createdBy": "user",
      "aliases": ["dog", "Lisich"]
    },
    {
      "id": "tag_fedor_school",
      "name": "Fedor school",
      "slug": "fedor-school",
      "type": "topic",
      "createdBy": "user",
      "aliases": []
    }
  ]
}
```

Suggested tag types:

```text
topic
person
pet
place
event_cluster
project
activity
mood
system
```

The `type` field is a soft category.

Do not treat it as a strict ontology.

---

## 4. Output files

The workflow may create:

```text
entries/YYYY/MM/YYYY-MM-DD__entry_<id>/ai/tag_proposals.json
```

It may also update:

```text
entries/YYYY/MM/YYYY-MM-DD__entry_<id>/ENTRY.json
```

If the workflow is in proposal-only mode, do not update `ENTRY.json`.

---

## 5. Modes

### 5.1 Proposal-only mode

The agent only writes suggested tags to:

```text
ai/tag_proposals.json
```

This is the safest default mode for manual debugging.

---

### 5.2 Apply mode

The agent updates `ENTRY.json` by adding accepted tags.

Apply mode should be used only when explicitly requested.

---

## 6. Tag matching logic

For each entry:

1. Read current tags from `ENTRY.json`.
2. Read entry text from `entry.md`.
3. Read existing tags and aliases from the tag catalog.
4. Try to match entry content to existing tags.
5. Prefer existing tags over creating new tags.
6. Suggest new tags only when clearly useful.
7. Mark confidence and reason for each suggested tag.

---

## 7. Existing tag matching

A tag can match through:

- exact tag name;
- alias;
- clear semantic match;
- repeated theme in the entry.

Examples:

| Entry text | Existing tag | Match reason |
|---|---|---|
| "Walked with Lis" | `tag_lis` | direct pet name |
| "Fedor had school discussion" | `tag_fedor_school` | clear topic |
| "trip to Moscow" | `tag_trip_moscow_2025` | event cluster |

Do not match a tag if the connection is weak.

---

## 8. New tag suggestion

The agent may suggest a new tag if:

- the topic appears central to the entry;
- no existing tag or alias matches;
- the tag would likely be useful for future navigation;
- the tag is not too specific.

Bad new tags:

```text
sunny weather at 11:43
small blue notebook on kitchen table
slightly annoying phone call
```

Potentially useful new tags:

```text
veterinary clinic
school selection
Moscow trip
Lis
tax declaration
Google Drive storage
```

---

## 9. Tag proposal format

Create:

```text
ai/tag_proposals.json
```

Example:

```json
{
  "formatVersion": "v0.1.0",
  "entryId": "entry_01HWABC",
  "createdAt": "2026-04-25T14:00:00Z",
  "workflow": "tag_enrichment",
  "mode": "proposal_only",
  "proposals": [
    {
      "action": "add_existing_tag",
      "tagId": "tag_lis",
      "name": "Lis",
      "type": "pet",
      "confidence": 0.95,
      "reason": "The entry explicitly mentions walking with Lis."
    },
    {
      "action": "create_new_tag",
      "name": "Veterinary clinic",
      "slug": "veterinary-clinic",
      "type": "topic",
      "confidence": 0.82,
      "reason": "The entry describes a visit to the vet, and no existing tag matches this topic."
    }
  ],
  "notApplied": true
}
```

---

## 10. Updating `ENTRY.json` in apply mode

If apply mode is enabled, update the `tags` field.

Example:

```json
"tags": [
  {
    "tagId": "tag_lis",
    "source": "ai",
    "confidence": 0.95,
    "addedAt": "2026-04-25T14:00:00Z",
    "workflow": "tag_enrichment"
  }
]
```

Do not remove existing user tags.

Do not overwrite existing tag objects unless explicitly requested.

---

## 11. Creating a new tag

If a new tag is accepted or apply mode allows new tags, update:

```text
catalogs/tags/tags.json
```

Example:

```json
{
  "id": "tag_veterinary_clinic",
  "name": "Veterinary clinic",
  "slug": "veterinary-clinic",
  "type": "topic",
  "createdBy": "ai",
  "aliases": ["vet", "animal clinic"]
}
```

Rules:

1. Prefer lowercase kebab-case slugs.
2. Avoid duplicate tags.
3. Check aliases before creating.
4. If uncertain, propose only; do not create.
5. Keep names human-readable.

---

## 12. Confidence levels

Suggested interpretation:

```text
0.90–1.00  strong direct evidence
0.75–0.89  likely relevant
0.50–0.74  weak or contextual
below 0.50 do not suggest
```

For MVP, prefer suggesting only tags with confidence >= 0.75.

---

## 13. What not to tag

Do not tag:

- every object mentioned once;
- generic words;
- temporary details;
- private guesses;
- inferred emotions unless the entry clearly supports them;
- people or places not actually present in the entry.

Example:

If the entry says:

> I was thinking about school while walking with Lis.

Useful tags may be:

```text
Lis
school
```

Not useful:

```text
walking path
thinking
weather
sidewalk
```

unless those are important recurring diary categories.

---

## 14. Handling conflicts

### 14.1 Existing similar tag

If a new suggested tag is similar to an existing one, do not create it.

Instead propose using the existing tag and optionally adding an alias.

Example:

Existing tag:

```text
Fedor school
```

New text mentions:

```text
Fedor's classes
```

Propose:

```json
{
  "action": "add_alias",
  "tagId": "tag_fedor_school",
  "alias": "Fedor's classes",
  "reason": "This appears to refer to the existing Fedor school topic."
}
```

---

### 14.2 Ambiguous person/place/topic

Since there are no separate people or places catalogs yet, use tags.

If unsure whether something should be a `person`, `place`, or `topic`, use `topic` or mark `needs_review`.

---

## 15. Manual debugging mode

For early testing:

1. Select one entry.
2. Run proposal-only mode.
3. Create `ai/tag_proposals.json`.
4. Do not update `ENTRY.json`.
5. Review the proposal manually.
6. Only then run apply mode.

Report:

- entry inspected;
- existing tags;
- proposed existing tags;
- proposed new tags;
- uncertain decisions;
- files changed.

---

## 16. Success criteria

The workflow succeeds if:

- existing tags are reused when appropriate;
- new tags are suggested only when useful;
- user-created tags are not overwritten;
- tag proposals include reasons and confidence;
- apply mode updates `ENTRY.json` safely;
- raw entry text remains unchanged.

---

## 17. Minimal first test

Input:

```text
entries/2026/04/2026-04-25__entry_01HWABC/
  ENTRY.json
  entry.md
```

Existing catalog:

```text
catalogs/tags/tags.json
```

Expected output in proposal-only mode:

```text
entries/2026/04/2026-04-25__entry_01HWABC/ai/tag_proposals.json
```

No changes to `ENTRY.json` unless apply mode is explicitly enabled.

