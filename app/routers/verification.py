from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_faiss_store, get_embedding_service, get_clustering_service
from app.vector.faiss_store import FAISSStore
from app.vector.embedding_service import EmbeddingService
from app.vector.clustering_service import ClusteringService
from app.services.verification import VerificationService, FAISSNotReadyError
from app.repositories.titles import TitleRepository
from app.schemas.verification import (
    VerificationRequest, VerificationResponse,
    SubmissionRequest, SubmissionResponse
)
from app.utils.normalization import normalize_title, normalize_domain
from app.utils.phonetic import compute_phonetic_code

router = APIRouter(prefix="/api", tags=["Verification & Submission"])


@router.post("/verify", response_model=VerificationResponse)
def verify_title_endpoint(
    payload: VerificationRequest,
    db: Session = Depends(get_db),
    faiss_store: FAISSStore = Depends(get_faiss_store),
    embedder: EmbeddingService = Depends(get_embedding_service),
    clustering_service: ClusteringService = Depends(get_clustering_service)
):
    try:
        service = VerificationService(db, faiss_store, embedder, clustering_service)
        result = service.verify_title(
            title=payload.title,
            domain=payload.domain,
            language=payload.language,
            description=payload.description
        )
        return result
    except FAISSNotReadyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.post("/submit", response_model=SubmissionResponse)
def submit_title_endpoint(
    payload: SubmissionRequest,
    db: Session = Depends(get_db),
    faiss_store: FAISSStore = Depends(get_faiss_store),
    embedder: EmbeddingService = Depends(get_embedding_service),
    clustering_service: ClusteringService = Depends(get_clustering_service)
):
    try:
        service = VerificationService(db, faiss_store, embedder, clustering_service)
        verification_res = service.verify_title(
            title=payload.title,
            domain=payload.domain,
            language=payload.language,
            description=payload.description
        )

        decision = verification_res["decision"]

        if decision == "POTENTIAL_CONFLICT":
            record_status = "rejected"
        elif decision == "REVIEW_REQUIRED":
            record_status = "pending"
        else:
            record_status = "approved"

        # Create record in DB
        repo = TitleRepository(db)
        norm_title = normalize_title(payload.title)
        norm_domain = normalize_domain(payload.domain)
        phonetic_code = compute_phonetic_code(payload.title)

        record_data = {
            "title": payload.title,
            "normalized_title": norm_title,
            "description": payload.description,
            "domain": norm_domain,
            "raw_domain": payload.domain,
            "language": payload.language,
            "language_source": "user_submitted",
            "contact_info": payload.contact_info,
            "phonetic_code": phonetic_code,
            "record_status": record_status,
            "source_file": "user_submission"
        }

        saved_record = repo.create_title_record(record_data)

        return {
            "submission_id": saved_record.id,
            "record_status": record_status,
            "verification_result": verification_res
        }
    except FAISSNotReadyError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Submission failed: {str(e)}"
        )
