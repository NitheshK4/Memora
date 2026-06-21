# Memora: A Persistent and Reconcilable Memory System for LLM Agents

Memora is a stateful, reconcilable memory layer designed to sit underneath AI agents. It ensures user facts persist across sessions, detects contradictions, canonicalizes properties and entities, resolves conflicts using stability-aware rules, and logs every change in a detailed audit history.

## 📋 Problem Statement

Traditional AI agents struggle with conversational context over long periods:
1. **Context Loss**: They forget facts when conversations span multiple sessions.
2. **Silent Inconsistencies**: They overwrite facts or store contradictory claims (e.g. stating the user lives in SF and NYC simultaneously) without addressing the conflict.
3. **Hallucinations**: They make up answers when memory retrieval is weak.
4. **Opaque Decisions**: They do not log *why* a fact was updated, superseded, or rejected.

Memora solves this by applying strict **stability registry metadata** to different properties (e.g. birthday is stable; city is time-varying) and routing updates through a validation, conflict-detection, and resolution pipeline.

---

## 🏗️ Architecture

The processing pipeline for any incoming message follows these steps:

```
[ User Message ]
       │
       ▼
[ Fact Extractor ] ────► Extracts Candidate Facts (Rule-based or LLM)
       │
       ▼
[ Normalizer ] ────────► Standardizes properties (SF -> San Francisco)
       │
       ▼
[ Validator ] ─────────► Verifies plausibility (e.g. age range check)
       │
       ▼
[ Conflict Detector ] ─► Identifies overlaps with active memories
       │
       ▼
[ Resolution Engine ] ─► Applies rules (supersede, dispute, merge)
       │
       ▼
[ Memory DB (SQLite) ] ─► Persists fact state transitions & logs Audit Event
       │
       ▼
[ Response Generator ] ─► Drafts answer using resolved active profile context
```

### Module File Structure
- `app/api.py`: FastAPI endpoints.
- `app/models.py`: Database tables and validation schemas.
- `app/memory_db.py`: CRUD operations and similarity search on SQLite.
- `app/extractor.py`: Hybrid fact extraction (LLM with rule fallback).
- `app/normalizer.py`: Word & property canonicalization.
- `app/property_registry.py`: Registry for stable/time-varying property metadata.
- `app/conflict_detector.py`: Identity and contradiction comparison.
- `app/resolver.py`: Resolution rules (recency vs stability-conflict).
- `app/validator.py`: Type verification and check limits.
- `app/embeddings.py`: Local bag-of-words similarity matching.
- `app/memory_agent.py`: Orchestrator of the chat flow.
- `frontend/app.py`: Streamlit dashboard client.

---

## 🚀 Setup & Installation

### 1. Requirements
Ensure you have Python 3.11+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `OPENAI_API_KEY` to `.env` to enable LLM-based fact extraction. If left empty, the app runs fully offline using local rules.

### 4. Start Everything with One Command
```bash
./start.sh
```

This starts both the **FastAPI backend** (port 8002) and **Streamlit frontend** (port 8502) and seeds the database automatically.

| Service | URL |
|---|---|
| **Dashboard** | http://localhost:8502 |
| **API Docs** | http://localhost:8002/docs |

Default login: **`seed_user`** / **`password123`**

### 5. Run Manually (Optional)
If you prefer starting services separately:

**Terminal 1 — Backend:**
```bash
python3 -m uvicorn app.api:app --host 127.0.0.1 --port 8002 --reload
```

**Terminal 2 — Frontend:**
```bash
BACKEND_URL=http://localhost:8002 python3 -m streamlit run frontend/app.py --server.port 8502
```

## 🧪 Testing Suite

Automated tests are located in `tests/` using `pytest`.

### Run all tests programmatically:
```bash
python tests/run_all_tests.py
```
Or directly:
```bash
pytest tests/ -v
```

---

## 💡 How Memory Reconciliation Works

Memory updates are governed by the `PropertyRegistry`.

| Property | Type | Stability | Multi-Value | Conflict Handling |
|---|---|---|---|---|
| **Birthday** | date | Stable | No | Marks new value `disputed`, keeps original `active`. Requires clarification. |
| **Dog Name** | string | Stable | No | Marks new value `disputed`, keeps original `active`. |
| **City** | string | Time-varying | No | Supersedes original (status `superseded`, sets `effective_to` timestamp), stores new as `active`. |
| **Employer** | string | Time-varying | No | Supersedes original, stores new as `active`. |
| **Preference** | string | Time-varying | Yes | Keeps history of preferences, updates with recency. |
| **Hobby** | string | Time-varying | Yes | Appends as coexisting active facts. |

---

## ⚠️ Known Limitations
- **Local Similarity**: The pure-Python TF-IDF similarity matcher is lightweight and offline-friendly but lacks deep semantic vector understanding.
- **Rule Extractor Scope**: The fallback regex extractor is tailored to the demo scenarios; unstructured natural text outside these formats will benefit significantly from an OpenAI API key.

## 🔮 Future Enhancements
- **Vector Database**: Connect to pgvector or ChromaDB for dense embeddings.
- **Entity Resolution**: Support complex relationships (e.g. tracking multiple dogs with individual profiles).
- **Proactive Consolidation**: Periodically run background routines to consolidate disputed facts with LLM reasoning.
