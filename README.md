# Nirnay - AI Publication Title Similarity & Conflict Screening System

Nirnay is a production-grade MVP service designed to screen proposed publication titles against a dataset of 6,000+ existing titles using a multi-signal AI retrieval pipeline.

---

> [!IMPORTANT]
> **Prototype Disclaimer**: Nirnay is an automated screening assistant to help flag potential title conflicts. It is NOT an official legal decision system or official government title registration system.

---

## 🚀 Quickstart Commands

### 1. Environment Setup

```powershell
# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Dataset Validation & Ingestion

```powershell
# Step 1: Validate dataset workbook (6,000+ titles check & domain cleanup)
python -m app.scripts.validate_dataset

# Step 2: Ingest validated dataset into SQLite/PostgreSQL database
python -m app.scripts.ingest_dataset

# Step 3: Precompute Sentence-BERT embeddings & build FAISS vector index
python -m app.scripts.build_faiss_index

# Step 4: Build cluster centroids for fast scoped retrieval
python -m app.scripts.build_clusters
```

### 3. Run Application Server

```powershell
# Start FastAPI server on http://localhost:8000
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser for the web screening interface or [http://localhost:8000/docs](http://localhost:8000/docs) for OpenAPI documentation.

### 4. Testing & Benchmarking

```powershell
# Run pytest test suite
pytest -q

# Run benchmark script (100 queries performance analysis)
python -m app.scripts.benchmark
```

---

## 🏗️ Architecture & How It Works

TitleGuard uses a hybrid 4-pass candidate retrieval and scoring strategy:

1. **Exact Database Match**: Checks normalized title equality in SQLite/PostgreSQL.
2. **Fuzzy Lexical Retrieval**: Uses `RapidFuzz` `token_set_ratio` to capture typos, word order changes, and spelling variations.
3. **Semantic Vector Search**: Uses `SentenceTransformers` (`all-MiniLM-L6-v2`, 384 dimensions) and `FAISS` (`IndexFlatIP`) for top 20 semantic matches.
4. **Phonetic Matching**: Uses `Metaphone` / `Double Metaphone` on Latin-script titles to catch sound-alike variations.

```
Final Score = 0.50 * Semantic + 0.30 * Lexical + 0.20 * Phonetic
```

_(Note: If phonetic scoring is unavailable, weights automatically re-normalize to 0.625 Semantic + 0.375 Lexical)._

### Decision Risk Levels

- **`POTENTIAL_CONFLICT` / `HIGH`**: Score >= 0.75 or Exact Normalized Title Match found.
- **`REVIEW_REQUIRED` / `MEDIUM`**: 0.50 <= Score < 0.75.
- **`NO_STRONG_CONFLICT` / `LOW`**: Score < 0.50.

---

## 📊 Dataset Schema & Validation Rules

- Source file: `data/dataset_combined_all_6000-v2.xlsx`
- Sheet name: `Combined Dataset`
- Required columns: `titles`, `description`, `domain`, `contact_info`
- Domain normalization rules: Trims whitespace, lowercases, replaces `"news - sports"` with `"news-sports"`, `"news - technology"` with `"news-technology"`.

---

## 🛠️ API Contract

- `GET /api/health`: Health status of DB, FAISS vector count, and embedding model.
- `POST /api/verify`: Screen publication title and return detailed match breakdowns.
- `POST /api/submit`: Screen and store publication record (`approved`, `pending`, `rejected`).
- `POST /api/admin/rebuild-index`: Rebuild FAISS store from approved records (Protected by `X-Admin-Api-Key`).

---

## 🐳 Docker Deployment

```powershell
docker-compose up --build
```
