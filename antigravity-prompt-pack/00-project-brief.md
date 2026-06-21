# Project Brief: Memora

## Full Title

Memora: A Persistent and Reconcilable Memory System for LLM Agents

## Core Problem

AI agents often fail in four ways:

1. They forget user facts across sessions.
2. They store conflicting facts without reconciling them.
3. They hallucinate answers even when memory already exists.
4. They do not explain why one memory was kept, updated, or rejected.

## Product Goal

Build a memory layer for AI agents that:

- persists user facts across sessions
- detects contradictions
- reconciles conflicting information
- validates facts before using them
- maintains a full audit trail of memory changes

## Important Design Principle

Not every contradiction is the same.

Some facts are stable:

- birthday
- dog name
- family relation

Some facts are time-varying:

- city
- employer
- job title
- preferences

So the system must support memory states such as:

- active
- superseded
- disputed
- expired
- confirmed

It must never keep two incompatible active values for a stable property.

## Example Scenarios

### Employer and city update

Session 1:
"I work at Google in San Francisco"

Session 2:
"I just moved to New York for my new job at Meta"

Expected behavior:

- employer Google becomes superseded
- employer Meta becomes active
- city San Francisco becomes superseded
- city New York becomes active
- full history is preserved

### Dog name recall

Session 1:
"My dog's name is Max"

Session 2:
"What's my dog's name?"

Expected behavior:

- the agent answers "Max"

### Birthday stability

Session 1:
"My birthday is July 15th"

Session 5:
"When is my birthday?"

Expected behavior:

- the agent uses stored memory
- the agent must not hallucinate a different date

### Preference reversal

Session 1:
"I hate spicy food"

Session 2:
"I love spicy food actually"

Expected behavior:

- detect preference reversal
- update the active preference or mark change over time
- preserve history

## Deliverable Shape

This should become a final-year-project-worthy MVP with:

- FastAPI backend
- Streamlit frontend
- SQLite persistence
- rule-based fallback when no API key is present
- structured memory records
- conflict detection and resolution
- validation layer
- audit log
- tests
