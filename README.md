<div align="center">

<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-1.24+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
<img src="https://img.shields.io/badge/Tests-26%20Passing-00C853?style=for-the-badge&logo=pytest&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

# 🧠 Memora
### *Persistent & Reconcilable Memory Graph for LLM Agents*

> A stateful memory layer that gives AI agents the ability to **remember**, **reconcile conflicts**, **validate facts**, and **explain every decision** across sessions.

</div>

---

## 🎯 The Problem

Traditional AI agents fail in four critical ways:

| Problem | Description |
|---|---|
| 🔴 **Context Loss** | Facts are forgotten when conversations span multiple sessions |
| 🟠 **Silent Inconsistencies** | Contradictory facts are stored without resolution (e.g. "lives in SF" and "lives in NYC" simultaneously) |
| 🟡 **Hallucinations** | Agents fabricate answers instead of recalling stored memory |
| 🔵 **Opaque Decisions** | No explanation for why a fact was accepted, rejected, or superseded |

**Memora solves all four.**

---

## ✨ Features

- 🔐 **JWT Authentication** — Multi-user system with secure PBKDF2 password hashing
- 🕸️ **Entity-Relationship Graph** — Visual node-edge memory graph with real-time updates
- ⚖️ **Conflict Detection & Resolution** — Stability-aware rules distinguish stable facts (birthday) from time-varying facts (employer, city)
- 🔍 **Fact Extraction** — Hybrid pipeline: LLM-based (OpenAI) with rule-based offline fallback
- ✅ **Validation Layer** — Type checking and plausibility guards before any fact is stored
- 📜 **Full Audit Trail** — Every memory state transition (created → superseded → disputed) is logged
- 🔄 **Reflection Engine** — Background consolidation worker that resolves stale disputes
- 🧮 **Local Vector Similarity** — Offline TF-IDF matching with no external dependencies
- 📊 **Interactive Dashboard** — Dark-mode Streamlit UI with live graph visualization

---

## 🏗️ Architecture

```
[ User Message ]
       │
       ▼
[ Fact Extractor ] ────► Extracts Candidate Facts (LLM or Rule-based)
       │
       ▼
[ Normalizer ] ─────────► Standardizes values  (SF → San Francisco)
       │
       ▼
[ Validator ] ──────────► Plausibility checks  (age range, date format)
       │
       ▼
[ Conflict Detector ] ──► Finds overlapping active memories
       │
       ▼
[ Resolution Engine ] ──► Applies stability rules (supersede / dispute / merge)
       │
       ▼
[ Memory Graph (SQLite) ] ► Persists state transitions & logs Audit Event
       │
       ▼
[ Response Generator ] ──► Answers using resolved active profile context
```

---

## 🧠 Memory Reconciliation Logic

Not every contradiction is the same. Memora distinguishes between **stable** and **time-varying** properties:

| Property | Stability | Conflict Behaviour |
|---|---|---|
| `birthday` | 🔒 Stable | New value marked `disputed`, original stays `active` |
| `dog_name` | 🔒 Stable | New value marked `disputed`, original stays `active` |
| `city` | 🔄 Time-varying | Original marked `superseded`, new value becomes `active` |
| `employer` | 🔄 Time-varying | Original marked `superseded`, new value becomes `active` |
| `preference` | 🔄 Time-varying | History preserved, most recent value is `active` |
| `hobby` | 🔄 Multi-value | All values coexist as `active` |

### Example Scenarios

<details>
<summary><b>📍 Scenario A: Relocation & Job Change</b></summary>

```
Session 1: "I work at Google in San Francisco"
Session 2: "I just moved to New York for my new job at Meta"

Result:
  employer: Google  → superseded ✗
  employer: Meta    → active ✓
  city: San Francisco → superseded ✗
  city: New York    → active ✓
```
</details>

<details>
<summary><b>🐶 Scenario B: Stable Fact Recall</b></summary>

```
Session 1: "My dog's name is Max"
Session 5: "What's my dog's name?"

Result: Agent answers "Max" — no hallucination
```
</details>

<details>
<summary><b>🎂 Scenario C: Stable Fact Conflict</b></summary>

```
Session 1: "My birthday is July 15th"
Session 3: "My birthday is July 20th"

Result:
  birthday: July 15 → active ✓ (stable, kept)
  birthday: July 20 → disputed ⚠️ (requires clarification)
```
</details>

<details>
<summary><b>🌶️ Scenario D: Preference Reversal</b></summary>

```
Session 1: "I hate spicy food"
Session 2: "I love spicy food actually"

Result: Preference history preserved, latest value is active
```
</details>

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/NitheshK4/Memora.git
cd Memora
pip install -r requirements.txt
```

### 2. Run (One Command)

```bash
./start.sh
```

| Service | URL |
|---|---|
| 📊 **Dashboard** | http://localhost:8503 |
| 📖 **API Docs** | http://localhost:8002/docs |

**Default login:** `seed_user` / `password123`

### 3. Optional: Enable LLM Mode

Copy `.env.example` to `.env` and add your OpenAI key for richer fact extraction:
```bash
cp .env.example .env
# Add: OPENAI_API_KEY=sk-...
```

Without a key, Memora runs fully **offline** using built-in rules.

---

## 🧪 Testing

```bash
python tests/run_all_tests.py
```

```
====================================================
  ✅ All 26 Tests Passed (100%)
====================================================
```

**Test coverage includes:**
- Unit tests: conflict detector, resolver, validator, memory DB
- Integration tests: full pipeline, multi-session learning
- Graph tests: entity merging, JWT auth, reflection engine
- Performance tests: memory matching latency under load

---

## 📁 Project Structure

```
Memora/
├── app/
│   ├── api.py              # FastAPI routes (JWT-protected)
│   ├── auth.py             # PBKDF2 hashing + pure-Python JWT
│   ├── memory_agent.py     # Chat orchestrator
│   ├── memory_db.py        # CRUD + similarity search
│   ├── graph_store.py      # Entity-Relationship graph engine
│   ├── extractor.py        # Hybrid fact extraction (LLM/rules)
│   ├── conflict_detector.py# Contradiction detection
│   ├── resolver.py         # Stability-aware resolution rules
│   ├── reflection.py       # Background consolidation engine
│   ├── validator.py        # Type & plausibility checks
│   ├── normalizer.py       # Value canonicalization
│   ├── embeddings.py       # Local TF-IDF vector similarity
│   └── property_registry.py# Stability metadata registry
├── frontend/
│   └── app.py              # Streamlit dashboard
├── tests/                  # 26 automated tests
├── scripts/
│   ├── seed_db.py          # Demo data seeder
│   ├── backup_db.py        # Database backup utility
│   └── benchmark.py        # Performance benchmarks
├── docs/
│   ├── architecture.md     # System design paper
│   ├── api_spec.md         # OpenAPI documentation
│   └── research_rationales.md
├── deploy/
│   ├── nginx.conf          # Reverse proxy config
│   └── prometheus.yml      # Metrics scraper config
├── requirements.txt
└── start.sh                # One-command startup script
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Create a new user account |
| `POST` | `/token` | Login and receive JWT token |
| `POST` | `/chat` | Send a message and store facts |
| `GET` | `/memories` | Get active memory profile |
| `GET` | `/memories/history` | Full fact version history |
| `GET` | `/memories/audit` | Complete audit event log |
| `GET` | `/memories/search?q=` | Semantic similarity search |
| `POST` | `/memories/clear` | Reset user memory graph |
| `GET` | `/graph/snapshot` | ER graph node-edge data |
| `POST` | `/reflection/trigger` | Run consolidation cycle |
| `GET` | `/health` | Backend health check |

---

## ⚠️ Known Limitations

- **Local Vector Similarity**: TF-IDF is lightweight and offline-friendly but lacks deep semantic understanding — connect OpenAI embeddings or ChromaDB for production use
- **Rule Extractor Scope**: The offline regex extractor covers core scenarios; complex natural language benefits from the OpenAI key

## 🔮 Future Enhancements

- [ ] pgvector / ChromaDB integration for dense semantic embeddings
- [ ] Multi-entity relationship tracking (e.g. multiple pets with individual profiles)
- [ ] LLM-driven dispute resolution with explanation generation
- [ ] WebSocket-based real-time memory update streaming
- [ ] Export memory graph as JSON / RDF


