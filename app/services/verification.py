import time
import uuid
from typing import Dict, Optional, List
from sqlalchemy.orm import Session

from app.vector.embedding_service import EmbeddingService
from app.vector.faiss_store import FAISSStore
from app.vector.clustering_service import ClusteringService
from app.services.retrieval import RetrievalPipeline
from app.services.scoring import ScoringEngine
from app.services.decision import DecisionEngine
from app.utils.logging import logger


class FAISSNotReadyError(Exception):
    """Raised when FAISS index is uninitialized, missing, or corrupt."""
    pass


class VerificationService:
    def __init__(
        self,
        db: Session,
        faiss_store: FAISSStore,
        embedding_service: EmbeddingService,
        clustering_service: Optional[ClusteringService] = None
    ):
        self.db = db
        self.faiss_store = faiss_store
        self.embedding_service = embedding_service
        self.clustering_service = clustering_service or ClusteringService()
        if self.clustering_service.centroids is None:
            self.clustering_service.load_metadata()
        self.retrieval_pipeline = RetrievalPipeline(db, faiss_store, self.clustering_service)
        self.scoring_engine = ScoringEngine()
        self.decision_engine = DecisionEngine()

    def verify_title(
        self,
        title: str,
        domain: str = "general",
        language: str = "English",
        description: Optional[str] = None
    ) -> Dict:
        start_time = time.perf_counter()

        if not self.faiss_store.is_healthy():
            logger.error("Verification requested but FAISS index is not ready or unhealthy.")
            raise FAISSNotReadyError("FAISS vector search index is missing, uninitialized, or corrupt.")

        verification_id = f"VR-{uuid.uuid4().hex[:8].upper()}"

        # 1. Embed query
        query_text = title
        if description and description.strip():
            query_text = f"{title}. {description.strip()}"

        query_embedding = self.embedding_service.encode_query(query_text)

        # Assign cluster
        cluster_ids = self.clustering_service.assign_cluster(query_embedding)

        # 2. Retrieve candidates
        candidates = self.retrieval_pipeline.retrieve_candidates(title, query_embedding)

        # 3. Score candidates
        scored_candidates = []
        for cand in candidates:
            rec = cand["record"]
            raw_semantic = cand.get("semantic_score", 0.0)

            score_details = self.scoring_engine.score_candidate(
                query_title=title,
                candidate_title=rec.title,
                raw_semantic_score=raw_semantic
            )

            scored_candidates.append({
                "record": rec,
                "scores": score_details
            })

        # Sort candidates by final score descending
        scored_candidates.sort(key=lambda x: x["scores"]["final_score"], reverse=True)

        # 4. Evaluate decision
        decision, risk, final_score, reasons, explanation = self.decision_engine.evaluate_results(
            query_title=title,
            query_domain=domain,
            scored_candidates=scored_candidates,
            cluster_ids=cluster_ids
        )

        # Take top 5 candidates for response
        top_matches = []
        for cand in scored_candidates[:5]:
            rec = cand["record"]
            scores = cand["scores"]
            top_matches.append({
                "id": rec.id,
                "title": rec.title,
                "domain": rec.domain,
                "language": rec.language,
                "description": rec.description,
                "semantic_score": scores["semantic_score"],
                "lexical_score": scores["lexical_score"],
                "phonetic_score": scores["phonetic_score"],
                "final_score": scores["final_score"]
            })

        # Calculate score breakdown for the top match (if present)
        if scored_candidates:
            top_scores = scored_candidates[0]["scores"]
            score_breakdown = {
                "semantic_score": top_scores["semantic_score"],
                "lexical_score": top_scores["lexical_score"],
                "phonetic_score": top_scores["phonetic_score"],
                "weights_used": top_scores["weights_used"]
            }
        else:
            score_breakdown = {
                "semantic_score": 0.0,
                "lexical_score": 0.0,
                "phonetic_score": None,
                "weights_used": {"semantic": 0.625, "lexical": 0.375, "phonetic": 0.0}
            }

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "verification_id": verification_id,
            "decision": decision,
            "risk": risk,
            "final_score": final_score,
            "score_breakdown": score_breakdown,
            "top_matches": top_matches,
            "reasons": reasons,
            "explanation": explanation,
            "candidate_count": len(candidates),
            "processing_time_ms": elapsed_ms
        }
