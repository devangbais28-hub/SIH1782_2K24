import os
import sys

print("=== LIBRARY CHECK ===")
libs = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "pydantic": "pydantic",
    "pydantic-settings": "pydantic_settings",
    "sqlalchemy": "sqlalchemy",
    "alembic": "alembic",
    "aiosqlite": "aiosqlite",
    "python-dotenv": "dotenv",
    "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss",
    "numpy": "numpy",
    "rapidfuzz": "rapidfuzz",
    "metaphone": "metaphone",
    "openpyxl": "openpyxl",
    "pandas": "pandas",
    "pytest": "pytest",
    "pytest-asyncio": "pytest_asyncio",
    "httpx": "httpx",
    "scikit-learn": "sklearn",
    "hdbscan": "hdbscan",
}
all_ok = True
for pkg, imp in libs.items():
    try:
        mod = __import__(imp)
        ver = getattr(mod, "__version__", "OK")
        print(f"  [OK] {pkg:25s} -> {ver}")
    except ImportError as e:
        print(f"  [FAIL] {pkg:25s} -> {e}")
        all_ok = False

print()
print("=== .ENV CONFIG CHECK ===")
from app.config import get_settings
s = get_settings()
checks = [
    ("APP_ENV", s.APP_ENV),
    ("DATABASE_URL", s.DATABASE_URL),
    ("EMBEDDING_MODEL", s.EMBEDDING_MODEL),
    ("FAISS_INDEX_PATH", s.FAISS_INDEX_PATH),
    ("FAISS_ID_MAP_PATH", s.FAISS_ID_MAP_PATH),
    ("FAISS_METADATA_PATH", s.FAISS_METADATA_PATH),
    ("FAISS_TOP_K", s.FAISS_TOP_K),
    ("CLUSTER_METADATA_PATH", s.CLUSTER_METADATA_PATH),
    ("CLUSTER_TOP_N", s.CLUSTER_TOP_N),
    ("SEMANTIC_WEIGHT", s.SEMANTIC_WEIGHT),
    ("LEXICAL_WEIGHT", s.LEXICAL_WEIGHT),
    ("PHONETIC_WEIGHT", s.PHONETIC_WEIGHT),
    ("SCORE_THRESHOLD_CONFLICT", s.SCORE_THRESHOLD_CONFLICT),
    ("SCORE_THRESHOLD_REVIEW", s.SCORE_THRESHOLD_REVIEW),
    ("ADMIN_API_KEY", "***" + s.ADMIN_API_KEY[-4:]),
    ("CORS_ORIGINS", s.CORS_ORIGINS),
]
for name, val in checks:
    print(f"  [OK] {name:30s} = {val}")

print()
print("=== FILE CONNECTIVITY CHECK ===")
files = [
    ("Database", s.DATABASE_URL.replace("sqlite:///", "").lstrip(".")),
    ("FAISS Index", s.FAISS_INDEX_PATH),
    ("FAISS ID Map", s.FAISS_ID_MAP_PATH),
    ("FAISS Metadata", s.FAISS_METADATA_PATH),
    ("Cluster Metadata", s.CLUSTER_METADATA_PATH),
    ("Dataset", "data/dataset_combined_all_6000-v2.xlsx"),
]
for label, path in files:
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    status = f"EXISTS ({size:,} bytes)" if exists else "MISSING"
    icon = "[OK]" if exists else "[FAIL]"
    print(f"  {icon} {label:25s} -> {status}")
    if not exists:
        all_ok = False

print()
w = s.SEMANTIC_WEIGHT + s.LEXICAL_WEIGHT + s.PHONETIC_WEIGHT
weight_ok = abs(w - 1.0) < 0.001
weight_status = "[OK]" if weight_ok else "[FAIL] Weights must sum to 1.0!"
print(f"=== WEIGHT VALIDATION: {s.SEMANTIC_WEIGHT} + {s.LEXICAL_WEIGHT} + {s.PHONETIC_WEIGHT} = {w} {weight_status}")
if not weight_ok:
    all_ok = False

print()
if all_ok:
    print("ALL CHECKS PASSED! Project is fully connected and operational.")
else:
    print("SOME CHECKS FAILED. See [FAIL] items above.")
