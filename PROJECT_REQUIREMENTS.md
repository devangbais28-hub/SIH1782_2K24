# TitleGuard — Project Requirements & Setup Guide

> **Last Updated:** August 2026
> Everything you need to know to set up, run, and deploy the TitleGuard system.

---

## 1. System Prerequisites

| Requirement | Minimum | Recommended | Notes |
|---|---|---|---|
| **Python** | 3.10 | 3.11.x | Python 3.12+ may have compatibility issues with some ML libraries |
| **pip** | 23.0+ | Latest | `python -m pip install --upgrade pip` |
| **Git** | 2.30+ | Latest | For version control |
| **OS** | Windows 10, Ubuntu 20.04, macOS 12 | Ubuntu 22.04 / Windows 11 | All three are tested |
| **RAM** | 4 GB | 8 GB+ | Sentence-BERT model + FAISS index can use ~2 GB |
| **Disk Space** | 2 GB | 5 GB+ | Includes model download cache (~500 MB) |
| **Docker** *(optional)* | 20.10+ | Latest | Only needed for containerised deployment |
| **Docker Compose** *(optional)* | 2.0+ | Latest | Only needed for containerised deployment |

---

## 2. Python Libraries (requirements.txt)

All dependencies are pinned for reproducibility. Install with:

```bash
pip install -r requirements.txt
```

### Core Framework

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.115.0 | Web framework for REST API |
| `uvicorn[standard]` | 0.30.6 | ASGI server to run FastAPI |
| `pydantic` | 2.9.2 | Data validation & serialization |
| `pydantic-settings` | 2.6.1 | `.env` file → Settings class binding |
| `python-dotenv` | 1.0.1 | `.env` file loading |

### Database

| Package | Version | Purpose |
|---|---|---|
| `sqlalchemy` | 2.0.36 | ORM / database engine (SQLite) |
| `alembic` | 1.13.3 | Database migration management |
| `aiosqlite` | 0.20.0 | Async SQLite driver (for async queries) |

### Machine Learning & Vector Search

| Package | Version | Purpose |
|---|---|---|
| `sentence-transformers` | 3.2.1 | Sentence-BERT embeddings (auto-downloads `all-MiniLM-L6-v2` model) |
| `faiss-cpu` | 1.9.0 | Facebook AI Similarity Search — vector index |
| `numpy` | 1.26.4 | Numerical operations for embeddings |
| `scikit-learn` | 1.5.2 | K-Means clustering for title groups |
| `hdbscan` | 0.8.39 | Density-based clustering (optional, experimental) |

### Text Similarity & NLP

| Package | Version | Purpose |
|---|---|---|
| `rapidfuzz` | 3.12.1 | Fast fuzzy string matching (lexical scoring) |
| `metaphone` | 0.6 | Double Metaphone phonetic codes for Latin-script text |

### Data Processing

| Package | Version | Purpose |
|---|---|---|
| `openpyxl` | 3.1.5 | Read `.xlsx` dataset files |
| `pandas` | 2.2.3 | DataFrame processing for ingestion/validation |

### Testing

| Package | Version | Purpose |
|---|---|---|
| `pytest` | 8.3.3 | Test runner |
| `pytest-asyncio` | 0.24.0 | Async test support |
| `httpx` | 0.27.2 | HTTP test client for FastAPI (TestClient) |

---

## 3. Environment Variables (.env)

Copy the example file and edit it:

```bash
cp .env.example .env
```

### Variable Reference

| Variable | Required? | Default | Description |
|---|---|---|---|
| `APP_ENV` | No | `development` | `development` or `production`. Controls logging verbosity. |
| `DATABASE_URL` | **Yes** | `sqlite:///./storage/titleguard.db` | SQLAlchemy database connection string. Default uses local SQLite. |
| `EMBEDDING_MODEL` | **Yes** | `all-MiniLM-L6-v2` | Sentence-BERT model name from HuggingFace. First run auto-downloads ~80 MB. |
| `FAISS_INDEX_PATH` | **Yes** | `./storage/faiss/title_index.faiss` | Path to the serialised FAISS index binary. |
| `FAISS_ID_MAP_PATH` | **Yes** | `./storage/faiss/id_map.json` | JSON mapping FAISS internal IDs → database record IDs. |
| `FAISS_METADATA_PATH` | **Yes** | `./storage/faiss/index_metadata.json` | FAISS index metadata (dimensions, count, build date). |
| `FAISS_TOP_K` | No | `20` | Number of top-K candidates FAISS returns per query. |
| `CLUSTER_METADATA_PATH` | **Yes** | `./storage/clusters/cluster_metadata.json` | K-Means cluster centroids + assignments JSON. |
| `CLUSTER_TOP_N` | No | `3` | Number of closest clusters to scope during retrieval. |
| `SEMANTIC_WEIGHT` | No | `0.50` | Weight for semantic (embedding) similarity in final score. |
| `LEXICAL_WEIGHT` | No | `0.30` | Weight for lexical (RapidFuzz) similarity. |
| `PHONETIC_WEIGHT` | No | `0.20` | Weight for phonetic (Metaphone) similarity. |
| `SCORE_THRESHOLD_CONFLICT` | No | `0.75` | Score >= this → **POTENTIAL_CONFLICT** decision. |
| `SCORE_THRESHOLD_REVIEW` | No | `0.50` | Score >= this → **NEEDS_REVIEW** decision. Score < this → **CLEAR**. |
| `ADMIN_API_KEY` | **Yes** | `replace-with-secure-value` | API key for admin endpoints (ingestion, rebuild). **Change this!** |
| `CORS_ORIGINS` | No | `http://localhost:8000,http://localhost:3000` | Comma-separated allowed CORS origins. |

> **WARNING:** Before going to production, you **must** change `ADMIN_API_KEY` to a strong, unique secret value.

---

## 4. Required Data Files

| File | Location | How to Obtain |
|---|---|---|
| Dataset (`.xlsx`) | `data/dataset_combined_all_6000-v2.xlsx` | Provided with the project. Contains ~6,000 publication titles. |

### Generated Files (built by scripts)

These files are created during the setup pipeline and **must exist** before the API starts:

| File | Location | Generated By |
|---|---|---|
| SQLite database | `storage/titleguard.db` | `python -m app.scripts.ingest_dataset` |
| FAISS index | `storage/faiss/title_index.faiss` | `python -m app.scripts.build_faiss_index` |
| FAISS ID map | `storage/faiss/id_map.json` | `python -m app.scripts.build_faiss_index` |
| FAISS metadata | `storage/faiss/index_metadata.json` | `python -m app.scripts.build_faiss_index` |
| Cluster metadata | `storage/clusters/cluster_metadata.json` | `python -m app.scripts.build_clusters` |

---

## 5. Required Directories

These directories must exist before running scripts:

```
Nirnay/
├── storage/
│   ├── faiss/          # FAISS index files
│   └── clusters/       # Cluster metadata
├── data/               # Source dataset files
└── output/             # Validation/benchmark output reports
```

Create them with:

```bash
# Linux/macOS
mkdir -p storage/faiss storage/clusters data output

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path storage/faiss, storage/clusters, data, output
```

---

## 6. First-Time Setup (Step-by-Step)

```bash
# 1. Clone / navigate to the project
cd Nirnay

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
#    Linux/macOS:
source .venv/bin/activate
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env from template
cp .env.example .env
# EDIT .env — set ADMIN_API_KEY to a secure value

# 6. Create required directories
mkdir -p storage/faiss storage/clusters data output

# 7. Place dataset
# Ensure data/dataset_combined_all_6000-v2.xlsx exists in the data/ folder

# 8. Validate the dataset
python -m app.scripts.validate_dataset

# 9. Ingest data into SQLite
python -m app.scripts.ingest_dataset

# 10. Build the FAISS index
python -m app.scripts.build_faiss_index

# 11. Build cluster metadata
python -m app.scripts.build_clusters

# 12. Run tests
pytest -q

# 13. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 7. API Keys & External Services

| Service | Key Required? | Details |
|---|---|---|
| **HuggingFace** | **No** | The `all-MiniLM-L6-v2` model is open and free to download. No API key needed. On first run, `sentence-transformers` will auto-download it to `~/.cache/huggingface/`. |
| **Admin API** | **Yes (self-configured)** | Set via `ADMIN_API_KEY` in `.env`. Used as `X-Admin-Api-Key` HTTP header for admin endpoints. |
| **External Database** | **No** | SQLite is bundled. No external DB server required. |
| **Cloud Storage** | **No** | All files are local. |

> **No paid API keys, cloud services, or external accounts are required.** The entire system runs locally and offline after the initial model download.

---

## 8. Network Requirements

| Event | Internet Required? | When |
|---|---|---|
| `pip install -r requirements.txt` | Yes | First-time dependency installation |
| First call to EmbeddingService | Yes | One-time download of `all-MiniLM-L6-v2` (~80 MB) |
| All subsequent API operations | No | Runs fully offline |

### Firewall / Proxy Notes

If you're behind a corporate firewall:
- `pip` needs access to `pypi.org`
- `sentence-transformers` needs access to `huggingface.co` for model download
- Set `HTTP_PROXY` / `HTTPS_PROXY` environment variables if needed

---

## 9. API Endpoints Quick Reference

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| `GET` | `/` | — | Frontend dashboard (HTML) |
| `GET` | `/verify.html` | — | Verification form (HTML) |
| `GET` | `/api/health` | — | Health check |
| `GET` | `/api/health/detailed` | — | Detailed system health (DB, FAISS, clusters) |
| `POST` | `/api/verify` | — | Submit a title for conflict screening |
| `POST` | `/api/verify/batch` | — | Batch verify multiple titles |
| `GET` | `/api/admin/stats` | `X-Admin-Api-Key` | System statistics |
| `POST` | `/api/admin/rebuild-index` | `X-Admin-Api-Key` | Rebuild FAISS index |
| `GET` | `/docs` | — | Swagger UI (auto-generated) |
| `GET` | `/redoc` | — | ReDoc documentation |

---

## 10. Docker Deployment (Optional)

```bash
# Build & run with Docker Compose
docker-compose up --build -d

# The API will be available at http://localhost:8000
```

> **Note:** The Docker image expects `storage/`, `data/`, and `output/` to already contain the dataset and built indexes. Run the setup pipeline locally first, then mount the volumes.

---

## 11. Build Pipeline Order (CRITICAL)

The data pipeline **must** run in this exact order:

```
1. validate_dataset  →  2. ingest_dataset  →  3. build_faiss_index  →  4. build_clusters  →  5. Start API
```

| Step | Command | What It Does |
|---|---|---|
| 1 | `python -m app.scripts.validate_dataset` | Checks dataset quality, normalises titles, outputs report |
| 2 | `python -m app.scripts.ingest_dataset` | Reads `.xlsx` → inserts into SQLite |
| 3 | `python -m app.scripts.build_faiss_index` | Generates embeddings → builds FAISS index files |
| 4 | `python -m app.scripts.build_clusters` | Runs K-Means on embeddings → produces cluster metadata |
| 5 | `uvicorn app.main:app --reload` | Starts the API server |

> **WARNING:** Skipping steps or running them out of order will cause runtime failures. The API will refuse to start properly without the FAISS index and cluster metadata.

---

## 12. Testing

```bash
# Run all tests (27 tests expected)
pytest -q

# Run with verbose output
pytest -v

# Run a specific test file
pytest app/tests/test_retrieval.py -v

# Run with coverage (requires pytest-cov)
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

### Test Files

| File | Tests | What It Covers |
|---|---|---|
| `test_smoke.py` | 1 | Basic import check |
| `test_models.py` | 2 | SQLAlchemy models, field defaults |
| `test_normalization.py` | 4 | Title normalisation logic |
| `test_scoring.py` | 3 | Weighted score calculations |
| `test_decision.py` | 5 | CLEAR / NEEDS_REVIEW / POTENTIAL_CONFLICT decisions |
| `test_ingestion.py` | 3 | Dataset ingestion pipeline |
| `test_retrieval.py` | 3 | End-to-end retrieval & scoring |
| `test_api.py` | 6 | HTTP endpoint integration tests |

---

## 13. Scoring System Quick Reference

The final similarity score for each candidate title is:

```
final_score = (SEMANTIC_WEIGHT x semantic_score)
            + (LEXICAL_WEIGHT x lexical_score)
            + (PHONETIC_WEIGHT x phonetic_score)
```

**Default weights:** `0.50 / 0.30 / 0.20`

**Decision thresholds:**
- `final_score >= 0.75` → **POTENTIAL_CONFLICT**
- `0.50 <= final_score < 0.75` → **NEEDS_REVIEW**
- `final_score < 0.50` → **CLEAR**

---

## 14. Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Run from the project root directory (`Nirnay/`), not from inside `app/` |
| `FAISS index is not yet built or missing` | Run `python -m app.scripts.build_faiss_index` |
| `Cluster metadata not found` | Run `python -m app.scripts.build_clusters` |
| `sentence-transformers` download fails | Check internet connection and HuggingFace access |
| `ADMIN_API_KEY` rejected | Verify the `X-Admin-Api-Key` header matches your `.env` value |
| SQLite `database is locked` | Ensure only one writer process at a time |
| Out of memory during index build | Close other applications; 4 GB RAM minimum needed |
| `ImportError: numpy` version conflict | Run `pip install numpy==1.26.4` to pin the compatible version |
