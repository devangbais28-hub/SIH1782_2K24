import sys
from app.database import SessionLocal
from app.repositories.titles import TitleRepository
from app.vector.embedding_service import EmbeddingService
from app.vector.clustering_service import ClusteringService
from app.utils.logging import logger


def build_clusters():
    logger.info("Starting clustering pipeline...")
    db = SessionLocal()
    try:
        repo = TitleRepository(db)
        records = repo.get_all_active_titles()
        logger.info(f"Retrieved {len(records)} active/approved records.")
        if not records:
            logger.warning("No records to cluster.")
            return

        # Generate embeddings
        embedder = EmbeddingService()
        texts = []
        record_ids = []
        for rec in records:
            text = rec.title
            if rec.description and rec.description.strip():
                text = f"{rec.title}. {rec.description.strip()}"
            texts.append(text)
            record_ids.append(rec.id)

        vectors = embedder.encode_titles(texts, batch_size=128)
        logger.info(f"Generated embeddings shape: {vectors.shape}")

        # Run clustering
        clustering = ClusteringService()
        id_to_cluster = clustering.fit_clusters(vectors, record_ids)
        clustering.save_metadata()

        # Update DB
        updated = repo.update_cluster_ids(id_to_cluster)
        logger.info(f"Updated cluster_id for {updated} records in database.")
        logger.info("Clustering pipeline complete!")

    except Exception as e:
        logger.error(f"Clustering failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    build_clusters()
