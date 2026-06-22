# Contributing to Memora

Thank you for your interest in contributing to **Memora**! This guide will help you get started.

---

## 🏁 Getting Started

### Prerequisites

- Python 3.11+
- Git

### Local Setup

```bash
git clone https://github.com/NitheshK4/Memora.git
cd Memora
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Locally

```bash
./start.sh
```

This starts both the FastAPI backend (port 8002) and Streamlit frontend (port 8503).

### Running Tests

```bash
python tests/run_all_tests.py
```

---

## 🔀 Contribution Workflow

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** — keep commits focused and atomic.

3. **Run the test suite** to ensure nothing is broken:
   ```bash
   python tests/run_all_tests.py
   ```

4. **Push** to your fork and open a **Pull Request** against `main`.

---

## 📝 Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/) with emoji prefixes:

| Prefix | Meaning |
|---|---|
| `🐛` | Bug fix |
| `✨` | New feature |
| `📝` | Documentation / logging |
| `🔒` | Security improvement |
| `🐳` | Docker / infrastructure |
| `♻️` | Refactor |
| `🧪` | Tests |

**Example:** `🐛 Fix typo in ChatResponse field name`

---

## 🏗️ Project Architecture

```
app/
├── api.py              # FastAPI routes (JWT-protected)
├── auth.py             # Authentication (PBKDF2 + pure-Python JWT)
├── memory_agent.py     # Chat orchestrator & response generation
├── memory_db.py        # CRUD operations & similarity search
├── graph_store.py      # Entity-Relationship graph engine
├── extractor.py        # Hybrid fact extraction (LLM / regex)
├── conflict_detector.py# Contradiction detection
├── resolver.py         # Stability-aware conflict resolution
├── reflection.py       # Background consolidation engine
├── validator.py        # Type & plausibility checks
├── normalizer.py       # Value canonicalization
├── embeddings.py       # Local BoW cosine similarity
├── vector_store.py     # TF-IDF + OpenAI embedding store
└── property_registry.py# Stability metadata registry
```

---

## 🧪 Adding Tests

- Place test files in `tests/` with the naming pattern `test_*.py`.
- Use `pytest` fixtures from `tests/conftest.py` for database sessions.
- Aim for both unit tests (single component) and integration tests (full pipeline).

---

## 💡 Ideas for Contributions

Check the **Future Enhancements** section in the [README](README.md) or look for open issues.

Some areas we'd love help with:
- pgvector / ChromaDB integration for dense embeddings
- Multi-entity relationship tracking
- WebSocket-based real-time memory streaming
- Expanded rule-based extraction patterns
- Additional validator rules (email, phone number, URL formats)

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
