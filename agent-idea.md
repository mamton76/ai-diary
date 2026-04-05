    # AI Agent Concept — AI Diary

## 1. Purpose

This document describes the conceptual model of the AI Agent used in AI Diary.

The agent is responsible for transforming raw user input (text, media, signals)
into structured, meaningful diary data while preserving user intent and control.

---

## 2. Core Definition

An AI Agent is NOT:

- a single prompt
- a single API call
- a standalone model

An AI Agent IS:

- application logic (code)
- + LLM-based reasoning
- + user context
- + rules and policies

Agent = Workflow + Decision Layer

---

## 3. Two Execution Paradigms

### Workflow (Deterministic)

A predefined sequence of steps:

- clean text
- extract metadata
- analyze text
- link media
- save results

Properties:
- predictable
- debuggable
- rigid

---

### Agentic Flow (Goal-driven)

Instead of fixed steps:

- define goal
- provide tools
- provide constraints

The agent decides dynamically:

- what to do next
- which tools to use
- whether to act or ask the user

Properties:
- flexible
- adaptive
- less predictable

---

## 4. Hybrid Model (Recommended)

The system should combine both approaches.

### Fixed (code-driven)
- metadata extraction
- persistence
- safety constraints
- lifecycle control

### Agent (LLM-driven)
- interpretation of text
- tag selection
- mood detection
- media linking decisions
- draft generation
- suggestion strategy

---

## 5. Core Principle

capture first → clarify second → structure later

The agent must NOT:

- interrupt user during capture
- require structured input upfront
- over-interpret meaning
- auto-publish generated content

---

## 6. Inputs

The agent operates on:

- user text (raw input)
- media (photo, video, link)
- metadata (timestamp, geo)
- user history
- user preferences

---

## 7. Tools

The agent has access to predefined capabilities:

- extract_media_metadata
- analyze_text (LLM)
- find_entries_by_time
- suggest_tags
- link_media
- generate_draft
- ask_user

---

## 8. Decision Model

All decisions are based on:

- confidence scores
- thresholds
- rules
- user preferences

---

## 9. Prompt Is Not the Agent

A prompt is only a reasoning step.

The agent includes:

- prompt templates
- context builder
- execution logic
- memory
- rule system

---

## 10. Context Construction

The agent dynamically builds context using:

- recent entries
- time proximity
- known tags
- rejected tags
- user behavior patterns

---

## 11. Media → Event Pipeline (Deferred)

media → signals → event candidate → draft → user confirmation

This feature is intentionally postponed.

---

## 12. User Preference Learning

The system should track:

- accepted tags
- rejected tags
- frequency of use

---

## 13. Configuration-driven Behavior

Example:

thresholds:
  strong_match: 0.8
  possible_match: 0.45

policies:
  require_confirmation_for_generated_text: true
  prefer_suggestions_over_actions: true

---

## 14. Rule Layer

IF media_present AND no_text:
    generate_draft (but do not auto-save)

---

## 15. Development Strategy

1. Hardcoded pipeline
2. Extract config
3. Add rule system
4. Add LLM decisions

---

## 16. UX Principles

- suggestions over automatic actions
- reversible operations
- transparency ("AI-generated")
- minimal interruption

---

## 17. Key Insight

The agent works because:

- boundaries are defined
- tools are provided
- model operates within constraints
