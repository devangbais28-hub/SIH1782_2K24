# Nirnay

### AI-Powered Publication Title Similarity & Conflict Screening

**Nirnay** is a production-grade MVP that helps identify potentially conflicting publication titles by comparing proposed titles against a curated dataset of **6,000+ existing publications**.

It combines **semantic AI search, lexical similarity, phonetic matching, and exact database matching** into a unified multi-signal screening pipeline.

> **Prototype Disclaimer**
>
> Nirnay is an automated screening assistant intended to flag potential title conflicts for human review. It is **not** an official legal decision system, trademark authority, or government publication-registration system.

---

## ✨ Why Nirnay?

Traditional title searches often rely on exact keyword matching, which can miss titles that are:

* Semantically similar
* Spelled differently
* Reordered
* Slightly misspelled
* Phonetically similar
* Worded differently but conveying the same concept

Nirnay addresses this using a **hybrid AI retrieval pipeline** that evaluates multiple similarity signals before producing a risk classification.

### Core capabilities

| Capability               | Technology                   |
| ------------------------ | ---------------------------- |
| Exact title detection    | SQLite / PostgreSQL          |
| Fuzzy title matching     | RapidFuzz                    |
| Semantic similarity      | Sentence Transformers        |
| Vector retrieval         | FAISS                        |
| Phonetic matching        | Metaphone / Double Metaphone |
| REST API                 | FastAPI                      |
| Data validation          | Pandas / OpenPyXL            |
| Automated testing        | Pytest                       |
| Containerization         | Docker                       |
| API documentation        | OpenAPI / Swagger            |
| Performance benchmarking | Custom benchmark suite       |

---

# 🧠 Technology Stack

### Backend

**Python** · **FastAPI** · **Pydantic** · **SQLAlchemy**

### AI / Search

**Sentence Transformers** · **all-MiniLM-L6-v2** · **FAISS** · **RapidFuzz** · **Metaphone**

### Data

**Pandas** · **OpenPyXL** · **SQLite / PostgreSQL**

### DevOps

**Docker** · **Docker Compose** · **Uvicorn**

### Quality & Testing

**Pytest** · **Benchmarking suite** · **Dataset validation pipeline**

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │       Web Interface     │
                    │    Title Screening UI   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI API        │
                    │                          │
                    │  /verify   /submit      │
                    │  /health   /admin/*     │
                    └────────────┬────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │        Nirnay Retrieval Engine       │
              └─────────────────┬───────────────────┘
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
┌───────────────┐      ┌────────────────┐      ┌─────────────────┐
│ Exact Match   │      │ Fuzzy Lexical  │      │ Semantic Search │
│               │      │                │      │                 │
│ SQLite /      │      │ RapidFuzz      │      │ Sentence        │
│ PostgreSQL    │      │ token_set      │      │ Transformers    │
└───────────────┘      └────────────────┘      │ + FAISS         │
                                                └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌──────────────────┐
                                               │ Phonetic Search  │
                                               │                  │
                                               │ Metaphone /      │
                                               │ Double Metaphone │
                                               └────────┬─────────┘
                                                        │
                                                        ▼
                                             ┌────────────────────┐
                                             │ Multi-Signal Score │
                                             └─────────┬──────────┘
                                                       │
                                                       ▼
                                         ┌────────────────────────┐
                                         │ Conflict Risk Engine   │
                                         │                        │
                                         │ HIGH / MEDIUM / LOW    │
                                         └────────────────────────┘
```

---

# 🔍 How the Matching Engine Works

Nirnay uses a **four-pass retrieval strategy**.

### 01 — Exact Database Match

The proposed title is normalized and checked against stored titles.

This provides an immediate high-confidence signal for exact normalized matches.

---

### 02 — Fuzzy Lexical Retrieval

**RapidFuzz `token_set_ratio`** is used to identify titles that remain similar despite:

* Typos
* Word-order changes
* Additional words
* Missing words
* Minor spelling variations

---

### 03 — Semantic Vector Search

Titles are converted into **384-dimensional embeddings** using:

`all-MiniLM-L6-v2`

These embeddings are indexed with **FAISS `IndexFlatIP`** to retrieve semantically similar titles even when the wording is substantially different.

---

### 04 — Phonetic Matching

For Latin-script titles, Nirnay additionally evaluates phonetic similarity using:

* Metaphone
* Double Metaphone

This helps identify titles that may sound similar despite spelling differences.

---

# 📐 Scoring Model

The final conflict score combines the three primary similarity signals:

```text
Final Score =
    0.50 × Semantic Similarity
  + 0.30 × Lexical Similarity
  + 0.20 × Phonetic Similarity
```

If phonetic matching is unavailable:

```text
Final Score =
    0.625 × Semantic Similarity
  + 0.375 × Lexical Similarity
```

This approach prevents the system from relying exclusively on keyword overlap or semantic embeddings.

---

# 🚦 Conflict Risk Classification

| Risk          |        Score | Meaning                       |
| ------------- | -----------: | ----------------------------- |
| 🔴 **HIGH**   |       ≥ 0.75 | Strong potential conflict     |
| 🟠 **MEDIUM** | 0.50 – 0.749 | Requires human review         |
| 🟢 **LOW**    |       < 0.50 | No strong similarity detected |

An **exact normalized title match** is automatically treated as a high-risk condition.

### API status values

```text
POTENTIAL_CONFLICT
REVIEW_REQUIRED
NO_STRONG_CONFLICT
```

---

# 📊 Dataset Pipeline

Nirnay currently works with a dataset containing **6,000+ publication titles**.

### Source

```text
data/dataset_combined_all_6000-v2.xlsx
```

### Sheet

```text
Combined Dataset
```

### Required fields

```text
titles
description
domain
contact_info
```

### Domain normalization

The ingestion pipeline automatically:

* Trims whitespace
* Converts domains to lowercase
* Normalizes inconsistent domain labels
* Converts `news - sports` → `news-sports`
* Converts `news - technology` → `news-technology`

---

# ⚡ Data & Indexing Pipeline

```text
Excel Dataset
      │
      ▼
Dataset Validation
      │
      ▼
Domain & Title Normalization
      │
      ▼
Database Ingestion
      │
      ▼
Sentence-BERT Embeddings
      │
      ▼
FAISS Vector Index
      │
      ▼
Cluster Centroids
      │
      ▼
Production Retrieval
```

Cluster centroids are additionally generated to enable faster scoped retrieval as the dataset grows.

---

# 🔌 API

## Health Check

```http
GET /api/health
```

Returns:

* Database health
* FAISS vector count
* Embedding model status
* Service health information

---

## Verify Publication Title

```http
POST /api/verify
```

Screens a proposed title and returns detailed similarity information, including candidate matches and conflict scoring.

Example workflow:

```text
Proposed Title
      ↓
Normalization
      ↓
Candidate Retrieval
      ↓
Multi-Signal Scoring
      ↓
Risk Classification
      ↓
Detailed Match Report
```

---

## Submit Publication

```http
POST /api/submit
```

Screens and stores a publication record.

Possible submission states:

```text
approved
pending
rejected
```

---

## Rebuild Search Index

```http
POST /api/admin/rebuild-index
```

Protected using:

```http
X-Admin-Api-Key
```

The endpoint rebuilds the FAISS index using approved publication records.

---

# 🛠️ Quick Start

## 1. Create the environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure environment variables

```powershell
cp .env.example .env
```

---

# 📥 Prepare the Dataset

Run the pipeline in order.

### Validate

```powershell
python -m app.scripts.validate_dataset
```

### Ingest

```powershell
python -m app.scripts.ingest_dataset
```

### Build FAISS Index

```powershell
python -m app.scripts.build_faiss_index
```

### Build Clusters

```powershell
python -m app.scripts.build_clusters
```

---

# 🚀 Run Nirnay

```powershell
uvicorn app.main:app --reload
```

Then open:

**Application**

```text
http://localhost:8000
```

**Interactive API Documentation**

```text
http://localhost:8000/docs
```

---

# 🧪 Testing

Run the complete test suite:

```powershell
pytest -q
```

Run the performance benchmark:

```powershell
python -m app.scripts.benchmark
```

The benchmark evaluates retrieval and screening performance across **100 queries**.

---

# 🐳 Docker Deployment

Build and start the complete stack:

```powershell
docker-compose up --build
```

The containerized deployment is designed to provide a reproducible environment for:

```text
FastAPI
    +
Database
    +
Embedding Model
    +
FAISS Index
```

---

# 📁 Project Structure

```text
nirnay/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── scripts/
│   │   ├── validate_dataset.py
│   │   ├── ingest_dataset.py
│   │   ├── build_faiss_index.py
│   │   ├── build_clusters.py
│   │   └── benchmark.py
│   └── main.py
│
├── data/
│   └── dataset_combined_all_6000-v2.xlsx
│
├── tests/
│
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

# 🧩 Engineering Highlights

### Hybrid Retrieval

Combines deterministic database matching with AI-powered semantic retrieval.

### Explainable Scoring

Every result can be decomposed into:

```text
Semantic
Lexical
Phonetic
Exact Match
```

rather than returning an opaque AI decision.

### Scalable Search Architecture

FAISS provides efficient vector retrieval while cluster centroids allow the retrieval layer to narrow its search space.

### Human-in-the-Loop

Nirnay is intentionally designed as a **screening and decision-support system**, rather than an autonomous legal authority.

### Production-Oriented API

The system exposes health, verification, submission, and administrative index-management endpoints through FastAPI.

---

# 🔐 Security Considerations

Administrative index rebuilding is protected through an API key:

```http
X-Admin-Api-Key
```

For production deployment, additional controls should be added around:

* Authentication
* Authorization
* Rate limiting
* API-key rotation
* Audit logging
* Input validation
* Secrets management
* Database access controls

---

# 📈 Future Roadmap

Potential next-stage improvements include:

* Multilingual / Indic-language embeddings
* Cross-script phonetic matching
* PostgreSQL + `pgvector`
* Redis-based caching
* Advanced reranking models
* Admin dashboard
* Authentication & role-based access
* Title similarity analytics
* Dataset versioning
* Human reviewer feedback loops
* Model evaluation dashboards
* Continuous benchmark tracking
* Kubernetes deployment

---

# 🏁 Project Status

**Nirnay — Production-Grade MVP**

| Component                       | Status |
| ------------------------------- | ------ |
| Dataset validation              | ✅      |
| Database ingestion              | ✅      |
| Exact matching                  | ✅      |
| Fuzzy matching                  | ✅      |
| Semantic retrieval              | ✅      |
| FAISS indexing                  | ✅      |
| Phonetic matching               | ✅      |
| Risk classification             | ✅      |
| REST API                        | ✅      |
| Submission workflow             | ✅      |
| Automated tests                 | ✅      |
| Benchmarking                    | ✅      |
| Docker deployment               | ✅      |
| Advanced multilingual retrieval | 🔜     |

---

## 🎯 Nirnay in One Sentence

> **Nirnay combines traditional search, semantic AI, and phonetic intelligence to identify potentially conflicting publication titles before they enter the publication workflow.**
