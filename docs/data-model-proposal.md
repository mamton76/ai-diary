You are helping design the data model for an AI Diary product.

Please read the following model carefully and treat it as the current intended architecture, not as a random draft. Your task is to understand it, preserve its core principles, and then help refine / critique / extend it without collapsing its distinctions.

## Product idea

This is a personal AI Diary / memory system.

The product should support:
- normal user-created diary entries
- AI-generated synthetic entries (summaries, inferred episodes, life periods, clusters)
- canonical history of edits and AI transformations
- tags and assets
- provenance / derivation tracking
- long-lived user AI context
- future AI learning / debugging / training workflows

The key principle is:

**Entry is the current product object.  
EntryRevision is the canonical historical truth.**

In other words:
- the user sees and interacts with Entry
- the system preserves the real historical content in EntryRevision
- current state is denormalized back onto Entry for performance and simpler UI

---

## High-level model

### 1. Entry
Entry is the main product object shown in lists and screens.

It stores the current snapshot:
- current primary text / title
- current date interval
- current tags/assets
- pointer to current revision

Entry can be:
- user-created
- imported
- AI-synthetic

Synthetic entries are **not** a separate table.
They are normal Entry records with:
- `originType = ai_synthetic`

This is important because synthetic objects should:
- appear in the same lists as normal entries
- be filterable like entries
- have their own revisions
- be further processed by AI
- behave like first-class product objects

---

### 2. EntryRevision
EntryRevision stores canonical historical content.

This is the source of truth for:
- text/title
- date interval
- event timestamps
- revision metadata
- historical tag and asset relations
- provenance / derivation

The model assumes:
- every meaningful content change creates a new EntryRevision
- Entry stores the current denormalized state
- historical reconstruction should come from revisions, not from current Entry only

---

### 3. Date handling
The model uses:

- `entryDateStart`
- `entryDateEnd`

Both are required and represent an inclusive calendar interval.

For a single-day entry:
- `entryDateStart = entryDateEnd`

This is preferred over a nullable end date.

Exact event timestamps are separate:
- `eventStartAt`
- `eventEndAt`

Important distinction:
- entryDateStart / entryDateEnd = calendar span where the entry belongs
- eventStartAt / eventEndAt = more precise event time, if known

Canonical dates live in EntryRevision.
Current dates are denormalized into Entry.

---

### 4. Tags
Tags are separate objects.

A Tag itself does **not** directly store a single name field.
Instead, text forms are stored in a separate label/synonym table.

#### Tag
Stores:
- identity
- owner
- optional type
- source
- createdAt / updatedAt

`type` is optional, not required.
A tag may simply be a generic user tag.

Possible tag types later may include:
- topic
- mood
- activity
- person_like
- place_like

But the model must not require every tag to have a type.

#### TagLabel
Stores:
- tagId
- text
- normalizedText
- isPrimary
- locale
- source
- createdAt / updatedAt

This table is used for:
- primary display label
- synonyms
- alternative spellings
- normalization
- future merge / search / alias handling

Rule:
- each Tag should have exactly one primary TagLabel

---

### 5. Tag relations
Tag relations exist on two levels:

#### EntryRevisionTag
Canonical historical relation between a revision and a tag.

#### EntryTag
Current denormalized relation between an entry and a tag.

This is intentional.

The model assumes:
- the real historical state belongs to EntryRevision
- the fast current state belongs to Entry

---

### 6. Assets
Assets represent:
- photo
- video
- audio
- link
- file

Assets also exist on two levels:

#### EntryRevisionAsset
Canonical historical relation to a revision.

#### EntryAsset
Current denormalized relation to an entry.

This mirrors the text/tag model:
- history on revision level
- current snapshot on entry level

---

### 7. Provenance / derivation
The model includes:

#### EntryRevisionSourceLink

This is used to record what a revision was derived from.

This is especially important for synthetic entries and AI-generated revisions.

A revision may be derived from:
- other EntryRevisions
- AI results
- assets
- tags
- synthetic entries

This layer should make it possible to answer:
- what evidence was used
- what this synthetic object was built from
- which earlier records contributed to this result

This is a provenance layer, not just a simple many-to-many link.

---

### 8. AI layer
AI processing is explicitly split into request and result.

#### AIRequest
Represents what was sent to the model.

It should store:
- request type
- model name
- prompt version
- input payload
- context snapshot used
- timestamps

This separation is important for:
- debugging
- training
- reproducibility
- prompt iteration
- understanding what the model actually received

#### AIResult
Represents what came back from the model.

It should store:
- request reference
- output payload
- status
- timestamps

#### AIFeedback
Stores user feedback on AIResult.

Important principle:
- feedback should attach to the AI result, not to the entry in general

---

### 9. User AI memory
The product distinguishes between explicit preferences and accumulated AI context.

#### UserPreferences
Explicit user-configured settings.

Examples:
- summary style
- AI aggressiveness
- whether AI suggestions are shown

#### UserAIContext
Current accumulated AI memory/profile of the user.

This is not just UI settings.
It is the long-lived AI-oriented context built over time.

It may include:
- learned stylistic preferences
- recurring entities
- preferred cleanup behavior
- patterns in accepted/rejected suggestions
- rendered summary for LLM use
- structured signals

#### UserAIContextVersion
History of UserAIContext over time.

This exists because the evolution of the user AI profile matters independently from individual AI calls.

#### AIContextSnapshot
Snapshot of the exact AI context actually used in one AI request.

This is important because:
- current UserAIContext may later change
- but the system should still know what context was actually sent during a specific AI request

Important distinction:
- UserAIContext = current long-lived accumulated profile
- UserAIContextVersion = history of that profile
- AIContextSnapshot = exact snapshot used in one specific AI call

---

## Core structural principles to preserve

Please preserve these principles in any refinement:

1. **Entry and EntryRevision must remain distinct**
    - Entry = current product object
    - EntryRevision = canonical history

2. **History belongs on revision level**
    - text history
    - canonical dates
    - canonical tag relations
    - canonical asset relations
    - provenance

3. **Current state may be denormalized onto Entry**
    - current text
    - current date interval
    - current tags
    - current assets

4. **Synthetic entries are first-class entries**
    - not just hidden AI artifacts
    - not just temporary clustering objects
    - not just tags

5. **AIRequest and AIResult are separate**
    - request = what was sent
    - result = what came back

6. **User AI memory is separate from simple settings**
    - UserPreferences != UserAIContext

7. **Tag labels / synonyms are modeled explicitly**
    - do not collapse them back into a single name field unless you have a strong reason

---

## What I want from you

Please do the following:

1. Summarize this model in your own words.
2. Identify its strongest architectural choices.
3. Identify possible weak points / complexity risks.
4. Suggest improvements, but only if they preserve the core principles above.
5. If relevant, propose:
    - database schema refinements
    - naming improvements
    - indexing ideas
    - lifecycle rules
    - validation rules
    - migration concerns
6. Explicitly say if you think any table is unnecessary or missing.
7. Be careful not to oversimplify away the historical model.

When analyzing this model, prioritize:
- conceptual clarity
- future extensibility
- support for AI workflows
- support for provenance
- support for synthetic entries as first-class objects
