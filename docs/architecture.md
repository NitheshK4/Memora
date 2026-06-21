# Architecture & System Design Paper: Memora Graph System

Memora is an Entity-Relationship (ER) Memory Graph layer designed to provide persistent, reconcilable, and explainable memory for AI agents.

```
                  ┌──────────────────────┐
                  │     User Input       │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Fact Extraction     │
                  │  (LLM / Regex rules) │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Normalization      │
                  │  (synonym mappings)  │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Type Validation    │
                  │  (plausibility check)│
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Conflict Detection  │
                  │  (registry rules)    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Resolution Engine   │
                  │  (recency/disputes)  │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌──────────────────────┐           ┌──────────────────────┐
│  Graph Node Edge DB  │◄─────────►│  Vector Index (BoW)  │
│       (SQLite)       │           │   Semantic Search    │
   └──────────────────────┘           └──────────────────────┘
            ▲
            │
┌───────────┴──────────┐
│  Reflection Engine   │ (Summarization & Dispute consolidation)
└──────────────────────┘
```

---

## 1. Graph Node/Edge Schema Representation

Instead of flat property key-value tables, Memora uses a structured graph representation:
*   **Nodes (`DB_Entity`)**: Represents objects, users, organizations, or pets.
    *   `id`: Primary Key
    *   `entity_type`: Category name (e.g. `self`, `organization`, `pet`, `location`)
    *   `name`: Canonical key identifier (e.g. `Google`, `Max`, `New York`)
*   **Edges (`DB_Relationship`)**: Direct links connecting two entity nodes.
    *   `source_entity_id`: Node tail identifier
    *   `target_entity_id`: Node head identifier
    *   `predicate`: Edge action/link label (e.g. `works_at`, `lives_in`, `has_pet`)
    *   `status`: Link status (`active`, `superseded`, `disputed`)
*   **Properties (`DB_Memory`)**: Key-value metadata fields attached directly to nodes or edges to model attributes.

This model allows traversal queries (e.g., retrieving the user's pet's name by tracing `User -[has_pet]-> Pet -> dog_name`).

---

## 2. Hybrid Retrieval (Relational SQL + Cosine Vector Index)

When querying context, the system executes a hybrid search:
1.  **Relational SQL Query**: Directly loads active graph states using structured relational schemas.
2.  **Semantic Vector Match**: Queries text representations of nodes and attributes using a vector index.
    *   Vectors are generated using TF-IDF word count values locally, or the OpenAI `text-embedding-3-small` API.
    *   Retrieval calculates the Cosine Similarity score:
        $$\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
    *   Results exceeding the threshold ($0.35$) are returned to form a consolidated agent memory profile.

---

## 3. Cognitive Reflection and consolidation cycles

A recurring issue in LLM agents is memory fragmentation and unresolved contradictions. Memora features a background **Reflection Engine**:
1.  **Duplicate Node Clustering**: Traces and merges nodes with matching categories and highly similar labels (e.g., "Google Inc." and "Google"). It updates related edges and memory targets, preventing duplicate graph paths.
2.  **LLM Dispute resolution**: Evaluates disputed records using LLM reasoning over timestamps, source contexts, and related parameters, resolving the dispute by updating states to active or rejected.
