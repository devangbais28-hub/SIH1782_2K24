import numpy as np
from typing import List, Dict
from sqlalchemy.orm import Session
from rapidfuzz import fuzz, process

from app.models.title_record import TitleRecord
from app.repositories.titles import TitleRepository
from app.vector.faiss_store import FAISSStore
from app.vector.clustering_service import ClusteringService
from app.utils.normalization import normalize_title
from app.config import get_settings

settings = get_settings()


class RetrievalPipeline:
    def __init__(self, db: Session, faiss_store: FAISSStore, clustering_service: ClusteringService):
        self.db = db
        self.repo = TitleRepository(db)
        self.faiss_store = faiss_store
        self.clustering_service = clustering_service

    def retrieve_candidates(
        self,
        query_title: str,
        query_embedding: np.ndarray,
        top_k: int = settings.FAISS_TOP_K
    ) -> List[Dict]:
        norm_query = normalize_title(query_title)
        candidate_map: Dict[int, Dict] = {}

        # 1. Exact Match Search (database)
        exact_records = self.repo.get_by_exact_normalized_title(norm_query)
        for rec in exact_records:
            candidate_map[rec.id] = {
                "record": rec,
                "sources": {"exact"},
                "semantic_score": 0.0,  # Computed by scoring engine
            }

        # 2. Assign query to nearest cluster(s)
        cluster_ids = self.clustering_service.assign_cluster(query_embedding, top_n=settings.CLUSTER_TOP_N)

        # 3. Semantic Search (FAISS)
        if self.faiss_store.is_healthy():
            faiss_results = self.faiss_store.search(query_embedding, top_k=top_k * 3, cluster_filter=cluster_ids)
            
            # Get record objects for FAISS results
            faiss_record_ids = [rid for rid, _ in faiss_results]
            faiss_records_map = {r.id: r for r in self.repo.get_by_ids(faiss_record_ids) if r}
            
            count = 0
            for record_id, sim_score in faiss_results:
                rec = faiss_records_map.get(record_id)
                if rec is None or rec.record_status not in ("active", "approved"):
                    continue
                
                is_in_cluster = (rec.cluster_id in cluster_ids) if cluster_ids else True
                
                if record_id in candidate_map:
                    candidate_map[record_id]["sources"].add("semantic")
                    candidate_map[record_id]["semantic_score"] = sim_score
                else:
                    if is_in_cluster or count < top_k:
                        candidate_map[record_id] = {
                            "record": rec,
                            "sources": {"semantic"},
                            "semantic_score": sim_score,
                        }
                        count += 1

        # 4. Lexical Search — ONLY within cluster records (NOT loading all 6000)
        if cluster_ids:
            cluster_records = self.repo.get_by_cluster_ids(cluster_ids)
        else:
            cluster_records = self.repo.get_all_active_titles()[:500]

        if cluster_records:
            title_to_record = {rec.title: rec for rec in cluster_records}
            choices = list(title_to_record.keys())
            fuzzy_matches = process.extract(
                query_title, choices,
                scorer=fuzz.token_set_ratio,
                limit=top_k
            )
            for match_title, match_score, _ in fuzzy_matches:
                if match_score >= 60.0:
                    rec = title_to_record[match_title]
                    if rec.id in candidate_map:
                        candidate_map[rec.id]["sources"].add("lexical")
                    else:
                        candidate_map[rec.id] = {
                            "record": rec,
                            "sources": {"lexical"},
                            "semantic_score": 0.0,
                        }

        return list(candidate_map.values())
