from typing import Generator
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import get_settings
from app.vector.embedding_service import EmbeddingService
from app.vector.faiss_store import FAISSStore
from app.vector.clustering_service import ClusteringService

settings = get_settings()

_faiss_store_instance: FAISSStore = None
_embedding_service_instance: EmbeddingService = None
_clustering_service_instance: ClusteringService = None


def get_faiss_store() -> FAISSStore:
    global _faiss_store_instance
    if _faiss_store_instance is None:
        _faiss_store_instance = FAISSStore()
        _faiss_store_instance.load_index()
    return _faiss_store_instance


def get_embedding_service() -> EmbeddingService:
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance


def get_clustering_service() -> ClusteringService:
    global _clustering_service_instance
    if _clustering_service_instance is None:
        _clustering_service_instance = ClusteringService()
        _clustering_service_instance.load_metadata()
    return _clustering_service_instance


def verify_admin_key(x_admin_api_key: str = Header(None, alias="X-Admin-Api-Key")):
    if not x_admin_api_key or x_admin_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Admin-Api-Key header"
        )
    return True
