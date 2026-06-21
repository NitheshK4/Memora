# Research Rationale: Cognitive Consolidation in LLM Memory Systems

This document discusses the theoretical foundation and research justifications for building a persistent, graph-based reconcilable memory layer rather than relying on standard RAG (Retrieval-Augmented Generation) or raw vector databases.

## 1. The Fragmentation Problem in Vector-Only Memory

Many current AI frameworks store history as flat chunks of text inside a vector store. When the agent queries memory, it retrieves the top-$K$ matching chunks and feeds them into the prompt. This has severe failure modes:
1.  **Semantic Drift**: If a user states "I love spicy food" in Session 1, and "I hate spicy food actually" in Session 2, the vector search will return both chunks because they are semantically highly similar. The LLM is forced to reconcile the contradiction on-the-fly, often resulting in hallucinations or conflicting output.
2.  **Lack of Deletion/Superseding**: Vector chunks cannot easily be updated. If the user moves from San Francisco to New York, the SF facts remain in the database, polluting search results.

**Memora's Rationale**: By mapping extracted statements to a schema registry (stable vs. time-varying), Memora enforces structural updates:
*   Time-varying facts are superseded (updating status to `superseded` and setting `effective_to` timestamps).
*   Stable facts are disputed, keeping the database in a clean, solvable state.

---

## 2. Graph Node structures vs. Flat Property Stores

A flat key-value property store limits the agent's ability to model entity relations. For example, knowing that "the user works at Google" and "Google is in SF" requires a graph representation to infer that the user's office location is likely San Francisco.

By refactoring Memora into an **Entity-Relationship (ER) Memory Graph**:
*   Nodes represent discrete physical entities (`User`, `Pet`, `Organization`, `Location`).
*   Edges capture direct relationship linkages (`works_at`, `lives_in`, `has_pet`).
*   This structure enables graph traversals (e.g. tracing node linkages) to construct a highly relevant context subgraph for the agent prompt, which is much more precise than simple property matching.

---

## 3. Cognitive Reflection Cycles (Summarization & Dispute Resolution)

In biological brains, short-term memories are consolidated into long-term structures during rest phases, pruning duplicates and resolving conflicts.

Memora models this via the **Reflection Engine**:
1.  **Entity Merging**: Simplifies the graph index by clustering duplicate labels (e.g., merging "Google Inc." into "Google"), which is a common extraction issue when LLMs parse natural conversation.
2.  **Dispute Consolidation**: Instead of forcing the active agent to resolve stable conflicts during dialog (which increases latency and risks dialogue derailment), the engine flags contradictions as `disputed` and resolves them off-cycle using slow-thinking LLM prompts to analyze the timeline and conversational contexts.
