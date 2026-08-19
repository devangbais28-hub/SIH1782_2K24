import pytest
from app.database import SessionLocal
from app.models.title_record import TitleRecord
from app.vector.faiss_store import FAISSStore
from app.vector.embedding_service import EmbeddingService
from app.vector.clustering_service import ClusteringService

def test_faiss_index_loads():
    store = FAISSStore()
    loaded = store.load_index()
    assert loaded is True
    assert store.vector_count() >= 6000

def test_known_title_retrieves_itself():
    db = SessionLocal()
    try:
        rec = db.query(TitleRecord).filter(
            TitleRecord.record_status == "active"
        ).first()
        assert rec is not None

        embedder = EmbeddingService()
        query_emb = embedder.encode_query(rec.title)

        store = FAISSStore()
        store.load_index()
        results = store.search(query_emb, top_k=5)
        result_ids = [rid for rid, _ in results]
        assert rec.id in result_ids, f"Record {rec.id} not in FAISS top-5"
    finally:
        db.close()

def test_cluster_metadata_loads():
    cs = ClusteringService()
    loaded = cs.load_metadata()
    assert loaded is True
    assert cs.metadata.get("n_clusters", 0) >= 10

def test_cluster_assignment_returns_ids():
    cs = ClusteringService()
    cs.load_metadata()
    embedder = EmbeddingService()
    query_emb = embedder.encode_query("Climate Change Daily News")
    cluster_ids = cs.assign_cluster(query_emb, top_n=3)
    assert len(cluster_ids) > 0
    assert all(isinstance(c, int) for c in cluster_ids)
