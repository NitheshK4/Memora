<!-- Animated gradient wave header -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0b0c10,25:0f3460,50:66fcf1,75:0f3460,100:0b0c10&height=220&section=header&text=🧠%20MEMORA&fontSize=72&fontColor=ffffff&fontAlignY=35&desc=Persistent%20%26%20Reconcilable%20Memory%20Graph%20for%20LLM%20Agents&descSize=18&descColor=c5c6c7&descAlignY=55&animation=fadeIn"/>

<div align="center">

<!-- Animated typing effect -->
<a href="#">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=1000&color=66FCF1&center=true&vCenter=true&multiline=true&repeat=true&width=700&height=80&lines=Give+your+AI+agents+permanent+memory.;Detect+contradictions.+Resolve+conflicts.;Full+audit+trail+for+every+decision.;Zero+vendor+lock-in.+Runs+fully+offline." alt="Typing SVG" />
</a>

<br/><br/>

<!-- Animated tech stack icons -->
<a href="https://python.org"><img src="https://skillicons.dev/icons?i=python" height="40" alt="Python"/></a>
&nbsp;&nbsp;
<a href="https://fastapi.tiangolo.com"><img src="https://skillicons.dev/icons?i=fastapi" height="40" alt="FastAPI"/></a>
&nbsp;&nbsp;
<a href="https://sqlite.org"><img src="https://skillicons.dev/icons?i=sqlite" height="40" alt="SQLite"/></a>
&nbsp;&nbsp;
<a href="https://docker.com"><img src="https://skillicons.dev/icons?i=docker" height="40" alt="Docker"/></a>
&nbsp;&nbsp;
<a href="https://nginx.org"><img src="https://skillicons.dev/icons?i=nginx" height="40" alt="Nginx"/></a>
&nbsp;&nbsp;
<a href="https://prometheus.io"><img src="https://skillicons.dev/icons?i=prometheus" height="40" alt="Prometheus"/></a>

<br/><br/>

<!-- Animated status badges -->
<img src="https://img.shields.io/badge/v2.2.0-stable-0ea5e9?style=for-the-badge&labelColor=0b0c10"/>
<img src="https://img.shields.io/badge/tests-26%20passing-00C853?style=for-the-badge&labelColor=0b0c10&logo=pytest&logoColor=white"/>
<img src="https://img.shields.io/badge/security-OWASP-7B1FA2?style=for-the-badge&labelColor=0b0c10&logo=owasp&logoColor=white"/>
<img src="https://img.shields.io/badge/license-MIT-F7DF1E?style=for-the-badge&labelColor=0b0c10"/>
<img src="https://img.shields.io/badge/offline-ready-66fcf1?style=for-the-badge&labelColor=0b0c10"/>

<br/><br/>

[**🚀 Quick Start**](#-quick-start) &nbsp;·&nbsp; [**🏗️ Architecture**](#%EF%B8%8F-architecture) &nbsp;·&nbsp; [**🧠 Reconciliation**](#-how-memora-thinks) &nbsp;·&nbsp; [**📡 API**](#-api-reference) &nbsp;·&nbsp; [**🤝 Contributing**](CONTRIBUTING.md)

</div>

<br/>

<!-- Animated separator -->
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 💀 The Problem

> *Every AI agent today suffers from the same fatal flaw:* ***amnesia.***

<table>
<tr>
<td width="70" align="center">

```diff
- ██
```

</td>
<td>
<strong>Context Evaporation</strong><br/>
Facts silently vanish when conversations span multiple sessions. Yesterday's context? Gone.
</td>
</tr>
<tr>
<td align="center">

```diff
! ██
```

</td>
<td>
<strong>Silent Contradictions</strong><br/>
<em>"Lives in SF"</em> and <em>"Lives in NYC"</em> coexist in memory. No detection. No resolution. Just chaos.
</td>
</tr>
<tr>
<td align="center">

```
⬜
```

</td>
<td>
<strong>Confident Hallucination</strong><br/>
When agents can't recall, they don't say "I don't know." They <strong>invent</strong> — fluently, confidently, dangerously.
</td>
</tr>
<tr>
<td align="center">

```
🟦
```

</td>
<td>
<strong>Black-Box Decisions</strong><br/>
Why was a fact accepted? Rejected? There's no log. No trail. No explanation. Just vibes.
</td>
</tr>
</table>

<div align="center">
<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=24&duration=2000&pause=3000&color=66FCF1&center=true&vCenter=true&repeat=true&width=500&height=40&lines=Memora+eliminates+all+four." alt="Memora eliminates all four." />

<br/><br/>
</div>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🔐 &nbsp; Secure Multi-User Auth
> JWT tokens + PBKDF2-SHA256 hashing. Every user gets an isolated memory space.

### 🕸️ &nbsp; Entity-Relationship Graph
> Visual node-edge memory graph with real-time updates. See your agent's knowledge as a **living network**.

### ⚖️ &nbsp; Intelligent Conflict Resolution
> Stability-aware rules that *understand context*. Birthdays are stable. Job titles aren't. Memora knows the difference.

### 🔍 &nbsp; Hybrid Fact Extraction
> LLM-powered (OpenAI) with a zero-dependency regex fallback. Works online **or fully offline**.

### 🧮 &nbsp; Local Vector Similarity
> TF-IDF matching with zero external dependencies. Optional OpenAI embeddings for production.

### 📊 &nbsp; Memory Analytics
> Property distribution, graph metrics, and live stats via the `/stats` endpoint.

</td>
<td width="50%" valign="top">

### ✅ &nbsp; Multi-Rule Validation
> Type checking, length limits, plausibility guards. Bad data gets rejected **before** it touches the graph.

### 📜 &nbsp; Full Audit Trail
> Every transition — `created → superseded → disputed` — is logged with timestamps and provenance.

### 🔄 &nbsp; Background Reflection Engine
> Autonomous consolidation worker that resolves stale disputes and cleans the graph while you sleep.

### 🛡️ &nbsp; Production Hardened
> Rate limiting (60 req/min), OWASP headers, input sanitization, Docker Compose + Nginx + Prometheus.

### 📊 &nbsp; Interactive Dashboard
> Dark-mode Streamlit UI with glassmorphism design and live graph visualization.

### 🐳 &nbsp; One-Command Deploy
> Docker Compose with Nginx reverse proxy and optional Prometheus monitoring. `docker compose up`.

</td>
</tr>
</table>

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 🏗️ Architecture

> Every message flows through a **six-stage pipeline** designed for correctness, not shortcuts.

```mermaid
flowchart TB
    A["💬 User Message"] --> B["🔍 Fact Extractor"]
    B --> C["📐 Normalizer"]
    C --> D["✅ Validator"]
    D --> E["⚡ Conflict Detector"]
    E --> F["⚖️ Resolution Engine"]
    F --> G[("🗄️ Memory Graph\n─────────\nSQLite")]
    G --> H["💬 Response Generator"]
    
    I["🔄 Reflection\nEngine"] -.->|"Background\nConsolidation"| G
    G -.->|"Semantic\nSearch"| J["🧮 Vector Index\nTF-IDF / OpenAI"]

    style A fill:#1a1a2e,stroke:#66fcf1,stroke-width:2px,color:#e6e6e6
    style B fill:#16213e,stroke:#0f3460,stroke-width:2px,color:#e6e6e6
    style C fill:#16213e,stroke:#0f3460,stroke-width:2px,color:#e6e6e6
    style D fill:#16213e,stroke:#0f3460,stroke-width:2px,color:#e6e6e6
    style E fill:#1a1a2e,stroke:#e94560,stroke-width:2px,color:#e6e6e6
    style F fill:#1a1a2e,stroke:#e94560,stroke-width:2px,color:#e6e6e6
    style G fill:#0f3460,stroke:#66fcf1,stroke-width:3px,color:#e6e6e6
    style H fill:#1a1a2e,stroke:#66fcf1,stroke-width:2px,color:#e6e6e6
    style I fill:#1a1a2e,stroke:#a78bfa,stroke-width:2px,color:#e6e6e6
    style J fill:#1a1a2e,stroke:#a78bfa,stroke-width:2px,color:#e6e6e6
```

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 🧠 How Memora Thinks

> **Not all contradictions are bugs.** Some are life updates.
> 
> Memora's reconciliation engine understands the *semantic stability* of every property.

<br/>

```mermaid
graph LR
    subgraph stable["🔒 STABLE — Conflicts are DISPUTED"]
        A["🎂 birthday"] ---|"conflict?"| B["⚠️ DISPUTE\nOriginal stays active"]
        C["🐶 dog_name"] ---|"conflict?"| D["⚠️ DISPUTE\nRequires clarification"]
    end
    
    subgraph varying["🔄 TIME-VARYING — New values SUPERSEDE"]
        E["💼 employer"] ---|"new value?"| F["✅ SUPERSEDE\nOld value archived"]
        G["📍 city"] ---|"new value?"| H["✅ SUPERSEDE\nMost recent wins"]
    end

    subgraph multi["📚 MULTI-VALUE — All values COEXIST"]
        I["🎨 hobby"] ---|"new value?"| J["✅ COEXIST\nAll values remain active"]
    end

    style stable fill:#1a1133,stroke:#a78bfa,stroke-width:2px,color:#e6e6e6
    style varying fill:#0d2818,stroke:#06d6a0,stroke-width:2px,color:#e6e6e6
    style multi fill:#2d1215,stroke:#ef476f,stroke-width:2px,color:#e6e6e6
    
    style A fill:#2d1b69,stroke:#a78bfa,color:#e6e6e6
    style C fill:#2d1b69,stroke:#a78bfa,color:#e6e6e6
    style B fill:#1a1a2e,stroke:#ffd166,color:#e6e6e6
    style D fill:#1a1a2e,stroke:#ffd166,color:#e6e6e6
    style E fill:#1b3a4b,stroke:#06d6a0,color:#e6e6e6
    style G fill:#1b3a4b,stroke:#06d6a0,color:#e6e6e6
    style F fill:#1a1a2e,stroke:#06d6a0,color:#e6e6e6
    style H fill:#1a1a2e,stroke:#06d6a0,color:#e6e6e6
    style I fill:#3a1b1b,stroke:#ef476f,color:#e6e6e6
    style J fill:#1a1a2e,stroke:#06d6a0,color:#e6e6e6
```

<br/>

### 🎬 Real-World Scenarios

<details>
<summary>&nbsp;📍 <b>Relocation & Job Change</b> — Time-varying properties auto-supersede</summary>
<br/>

```diff
  Session 1: "I work at Google in San Francisco"
  Session 2: "I just moved to New York for my new job at Meta"

  ╔══════════════════════════════════════════════════╗
  ║  employer: Google          →  superseded    ✗   ║
+ ║  employer: Meta            →  active        ✓   ║
  ║  city: San Francisco       →  superseded    ✗   ║
+ ║  city: New York            →  active        ✓   ║
  ╚══════════════════════════════════════════════════╝
```

</details>

<details>
<summary>&nbsp;🐶 <b>Stable Fact Recall</b> — Zero hallucination, even after 5 sessions</summary>
<br/>

```
  Session 1: "My dog's name is Max"
  Session 5: "What's my dog's name?"

  ╔══════════════════════════════════════════════════╗
  ║  ✅ Agent answers "Max"                          ║
  ║     Sourced from memory graph, not hallucinated. ║
  ╚══════════════════════════════════════════════════╝
```

</details>

<details>
<summary>&nbsp;🎂 <b>Contradictory Stable Facts</b> — Flagged, never silently overwritten</summary>
<br/>

```diff
  Session 1: "My birthday is July 15th"
  Session 3: "My birthday is July 20th"

  ╔══════════════════════════════════════════════════╗
  ║  birthday: July 15  →  active     ✓   (kept)   ║
! ║  birthday: July 20  →  disputed   ⚠️   (flagged)║
  ╚══════════════════════════════════════════════════╝
  
  Agent asks for clarification instead of
  silently accepting the contradiction.
```

</details>

<details>
<summary>&nbsp;🌶️ <b>Preference Reversal</b> — History preserved, latest value promoted</summary>
<br/>

```diff
  Session 1: "I hate spicy food"
  Session 2: "I love spicy food actually"

  ╔══════════════════════════════════════════════════╗
- ║  preference: hates spicy  →  superseded    ✗   ║
+ ║  preference: loves spicy  →  active        ✓   ║
  ║                                                 ║
  ║  Full history preserved in audit trail.         ║
  ╚══════════════════════════════════════════════════╝
```

</details>

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 🚀 Quick Start

### ⚡ One-Command Launch

```bash
git clone https://github.com/NitheshK4/Memora.git
cd Memora
pip install -r requirements.txt
./start.sh
```

<div align="center">

| &nbsp; | Service | URL |
|:---:|:---|:---|
| 📊 | **Interactive Dashboard** | [`localhost:8503`](http://localhost:8503) |
| 📖 | **Swagger API Explorer** | [`localhost:8002/docs`](http://localhost:8002/docs) |

> **Default login** &nbsp;→&nbsp; `seed_user` / `password123`

</div>

<br/>

### 🐳 Docker Compose (Full Stack)

```bash
# API + Frontend + Nginx reverse proxy
docker compose up --build

# With Prometheus monitoring
docker compose --profile monitoring up --build
```

<div align="center">

| &nbsp; | Service | URL |
|:---:|:---|:---|
| 🌐 | Nginx Proxy | [`localhost`](http://localhost) |
| 📊 | Dashboard | [`localhost:8503`](http://localhost:8503) |
| 📖 | API Docs | [`localhost:8002/docs`](http://localhost:8002/docs) |
| 📈 | Prometheus | [`localhost:9090`](http://localhost:9090) *(monitoring profile)* |

</div>

<br/>

### 🤖 Enable LLM Mode *(Optional)*

```bash
cp .env.example .env
# Add your key:  OPENAI_API_KEY=sk-...
```

> Without a key, Memora runs **fully offline** using built-in regex rules.
> No external API calls. No data leaves your machine. Ever.

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 📡 API Reference

> All endpoints are JWT-protected except `/register`, `/token`, and `/health`.

```
BASE URL  →  http://localhost:8002
```

<div align="center">

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/register` | Create a new user account |
| `POST` | `/token` | Authenticate & receive JWT |
| `POST` | `/chat` | Send a message — facts extracted, validated & stored |
| `GET` | `/memories` | Retrieve active memory profile |
| `GET` | `/memories/history` | Full fact version history with state transitions |
| `GET` | `/memories/audit` | Complete audit event log |
| `GET` | `/memories/search?q=` | Semantic similarity search across memories |
| `POST` | `/memories/clear` | Reset user memory graph |
| `GET` | `/graph/snapshot` | Entity-Relationship graph (nodes + edges) |
| `POST` | `/reflection/trigger` | Manually invoke the consolidation engine |
| `GET` | `/stats` | Memory analytics & property distribution |
| `GET` | `/health` | Backend health check |

</div>

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 🧪 Testing

```bash
python tests/run_all_tests.py
```

```
====================================================
  ✅ All 26 Tests Passed (100%)
====================================================
```

<details>
<summary><strong>&nbsp;📋 Test coverage breakdown</strong></summary>
<br/>

| Category | What's Tested |
|:---|:---|
| **Unit** | Conflict detector, resolver, validator, memory DB |
| **Integration** | Full pipeline, multi-session learning, fact lifecycle |
| **Graph** | Entity merging, JWT auth flows, reflection engine |
| **Performance** | Memory matching latency under load |

</details>

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 🛡️ Security

| Layer | Implementation |
|:---|:---|
| **Authentication** | JWT tokens with PBKDF2-SHA256 password hashing |
| **Rate Limiting** | Sliding window — 60 requests/min per user |
| **Input Sanitization** | All user inputs sanitized before processing |
| **Security Headers** | Full OWASP recommended header suite |
| **Disclosure** | See [`SECURITY.md`](SECURITY.md) for vulnerability reporting |

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 📁 Project Structure

```
Memora/
│
├── app/                            ← Core engine
│   ├── api.py                      FastAPI routes (JWT-protected)
│   ├── auth.py                     PBKDF2 hashing + pure-Python JWT
│   ├── memory_agent.py             Chat orchestrator
│   ├── memory_db.py                CRUD + similarity search
│   ├── graph_store.py              Entity-Relationship graph engine
│   ├── extractor.py                Hybrid fact extraction (LLM / regex)
│   ├── conflict_detector.py        Contradiction detection
│   ├── resolver.py                 Stability-aware resolution rules
│   ├── reflection.py               Background consolidation engine
│   ├── validator.py                Multi-rule type & plausibility checks
│   ├── normalizer.py               Value canonicalization
│   ├── embeddings.py               Local TF-IDF vector similarity
│   ├── vector_store.py             TF-IDF + OpenAI embedding store
│   ├── property_registry.py        Stability metadata registry
│   ├── rate_limiter.py             Sliding window rate limiting
│   └── security_headers.py         OWASP security headers
│
├── frontend/
│   └── app.py                      Streamlit dashboard (dark glassmorphism)
│
├── tests/                          26 automated tests
├── scripts/                        seed_db · backup_db · benchmark
├── docs/                           architecture · api_spec · rationales
├── deploy/                         nginx.conf · prometheus.yml
│
├── docker-compose.yml              Full-stack orchestration
├── Dockerfile                      Multi-stage container build
├── SECURITY.md                     Vulnerability disclosure policy
├── CONTRIBUTING.md                 Contribution guidelines
├── requirements.txt                Python dependencies
└── start.sh                        One-command startup
```

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## 🔮 Roadmap

> What's coming next for Memora.

- [ ] 🧬 &nbsp; **Dense Embeddings** — pgvector / ChromaDB for semantic search
- [ ] 👥 &nbsp; **Multi-Entity Relationships** — Multiple pets, family members, vehicles
- [ ] 🤖 &nbsp; **LLM Dispute Resolution** — AI-powered arbitration with explanations
- [ ] ⚡ &nbsp; **WebSocket Streaming** — Real-time memory update notifications
- [ ] 📦 &nbsp; **Export Formats** — JSON-LD / RDF for interoperability
- [ ] 🏢 &nbsp; **Enterprise SSO** — OAuth2 / SAML integration
- [ ] 🎚️ &nbsp; **Role-Based Rate Limits** — Configurable tiers per user role

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

## ⚠️ Limitations

| Limitation | Context |
|:---|:---|
| **TF-IDF Similarity** | Lightweight & offline-friendly but lacks deep semantics. Use OpenAI embeddings or ChromaDB for production. |
| **Regex Extractor** | Covers core scenarios (employer, city, birthday, pets, preferences, hobbies). Complex NL benefits from the OpenAI key. |

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:0b0c10,50:1a1a2e,100:0b0c10&height=2"/>

<br/>

<div align="center">

## 🤝 Contributing

Contributions welcome — please read the **[Contributing Guide](CONTRIBUTING.md)** before opening a PR.

<br/>

## 📄 License

Released under the [MIT License](LICENSE) &nbsp;·&nbsp; © 2025 NitheshK4

<br/>

---

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=14&duration=4000&pause=2000&color=45858B&center=true&vCenter=true&repeat=true&width=450&height=30&lines=Built+with+obsessive+attention+to+memory+correctness." alt="Footer" />

<br/>

**[⬆ Back to top](#)**

</div>

<!-- Animated gradient wave footer -->
<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:0b0c10,25:0f3460,50:66fcf1,75:0f3460,100:0b0c10&height=120&section=footer"/>
