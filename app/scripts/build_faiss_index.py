import sys
from app.database import SessionLocal
from app.repositories.titles import TitleRepository
from app.vector.embedding_service import EmbeddingService
from app.vector.faiss_store import FAISSStore
from app.utils.logging import logger


def build_faiss_index():
    logger.info("Starting FAISS index build pipeline...")
    db = SessionLocal()

    try:
        repo = TitleRepository(db)
        active_records = repo.get_all_active_titles()
        logger.info(f"Retrieved {len(active_records)} active title records from database.")

        if not active_records:
            logger.warning("No active title records found. Skipping FAISS index build.")
            return

        texts_to_embed = []
        record_ids = []
        for rec in active_records:
            # Title text + description if available
            text = rec.title
            if rec.description and rec.description.strip():
                text = f"{rec.title}. {rec.description.strip()}"
            texts_to_embed.append(text)
            record_ids.append(rec.id)

        # Batch encode
        embedder = EmbeddingService()
        logger.info("Generating batch embeddings with SentenceTransformer...")
        vectors = embedder.encode_titles(texts_to_embed, batch_size=128)
        logger.info(f"Generated embeddings shape: {vectors.shape}")

        # Build FAISS store
        store = FAISSStore()
        store.build_index(vectors, record_ids, extra_metadata={"model": embedder.model_name})
        store.save_index()

        # Update database faiss_position for records
        id_to_pos = {rec_id: pos for pos, rec_id in enumerate(record_ids)}
        updated_count = repo.update_faiss_positions(id_to_pos)
        logger.info(f"Updated faiss_position for {updated_count} records in database.")
        logger.info("FAISS index build complete!")

    except Exception as e:
        logger.error(f"Failed to build FAISS index: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    build_faiss_index()
