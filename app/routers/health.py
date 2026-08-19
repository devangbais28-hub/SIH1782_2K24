from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.config import get_settings
from app.dependencies import get_faiss_store, get_embedding_service, get_clustering_service
from app.vector.faiss_store import FAISSStore
from app.vector.embedding_service import EmbeddingService
from app.vector.clustering_service import ClusteringService

router = APIRouter(prefix="/api", tags=["Health"])
settings = get_settings()


@router.get("/health")
def get_health(
    db: Session = Depends(get_db),
    faiss_store: FAISSStore = Depends(get_faiss_store),
    embedder: EmbeddingService = Depends(get_embedding_service),
    clustering_service: ClusteringService = Depends(get_clustering_service)
):
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    faiss_loaded = faiss_store.is_healthy()
    faiss_count = faiss_store.vector_count()
    cluster_count = clustering_service.metadata.get("n_clusters", 0)

    overall_status = "healthy" if (db_status == "connected" and faiss_loaded) else "degraded"

    return {
        "status": overall_status,
        "database": db_status,
        "embedding_model": embedder.model_name,
        "faiss_index_loaded": faiss_loaded,
        "faiss_vector_count": faiss_count,
        "cluster_count": cluster_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
