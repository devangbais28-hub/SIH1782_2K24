from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_admin_key, get_faiss_store, get_embedding_service
from app.repositories.titles import TitleRepository
from app.vector.faiss_store import FAISSStore
from app.vector.embedding_service import EmbeddingService
from app.utils.logging import logger

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(verify_admin_key)])


@router.post("/rebuild-index")
def rebuild_index_endpoint(
    db: Session = Depends(get_db),
    faiss_store: FAISSStore = Depends(get_faiss_store),
    embedder: EmbeddingService = Depends(get_embedding_service)
):
    try:
        logger.info("Admin triggered FAISS index rebuild...")
        repo = TitleRepository(db)

        # Query all active or approved records
        records = repo.get_all_active_titles()

        if not records:
            return {"status": "success", "message": "No active/approved records found to index.", "vector_count": 0}

        texts = []
        record_ids = []
        for rec in records:
            text = rec.title
            if rec.description and rec.description.strip():
                text = f"{rec.title}. {rec.description.strip()}"
            texts.append(text)
            record_ids.append(rec.id)

        vectors = embedder.encode_titles(texts)
        faiss_store.build_index(vectors, record_ids, extra_metadata={"model": embedder.model_name})
        faiss_store.save_index()

        # Reload index
        faiss_store.load_index()

        logger.info(f"FAISS index rebuild complete. Indexed {faiss_store.vector_count()} vectors.")
        return {
            "status": "success",
            "message": "FAISS index rebuilt successfully.",
            "vector_count": faiss_store.vector_count()
        }

    except Exception as e:
        logger.error(f"Failed to rebuild FAISS index: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rebuild FAISS index: {str(e)}"
        )
