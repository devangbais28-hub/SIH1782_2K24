import os
import json
import numpy as np
import faiss
from datetime import datetime, timezone
from typing import List, Tuple, Optional, Dict
from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()


class FAISSStore:
    def __init__(
        self,
        index_path: str = settings.FAISS_INDEX_PATH,
        id_map_path: str = settings.FAISS_ID_MAP_PATH,
        metadata_path: str = settings.FAISS_METADATA_PATH,
        dimension: int = 384
    ):
        self.index_path = index_path
        self.id_map_path = id_map_path
        self.metadata_path = metadata_path
        self.dimension = dimension

        self.index: Optional[faiss.IndexFlatIP] = None
        self.id_map: Dict[int, int] = {}  # pos -> record_id
        self.metadata: Dict = {}

    def is_healthy(self) -> bool:
        if self.index is None or self.index.ntotal == 0:
            return False
        if len(self.id_map) != self.index.ntotal:
            return False
        return True

    def vector_count(self) -> int:
        if self.index is None:
            return 0
        return self.index.ntotal

    def build_index(self, vectors: np.ndarray, record_ids: List[int], extra_metadata: Dict = None) -> bool:
        if vectors.shape[0] != len(record_ids):
            raise ValueError(f"Vector count ({vectors.shape[0]}) does not match record_ids count ({len(record_ids)}).")

        logger.info(f"Building FAISS IndexFlatIP with {vectors.shape[0]} vectors of dim {self.dimension}...")
        self.index = faiss.IndexFlatIP(self.dimension)
        
        if vectors.shape[0] > 0:
            faiss.normalize_L2(vectors)
            self.index.add(vectors)

        self.id_map = {idx: record_id for idx, record_id in enumerate(record_ids)}
        self.metadata = {
            "model_name": settings.EMBEDDING_MODEL,
            "dimension": self.dimension,
            "record_count": self.index.ntotal,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            **(extra_metadata or {})
        }

        return True

    def save_index(self) -> bool:
        if self.index is None:
            raise ValueError("Cannot save unitialized FAISS index.")

        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save index file
        faiss.write_index(self.index, self.index_path)

        # Save ID map
        str_id_map = {str(k): v for k, v in self.id_map.items()}
        with open(self.id_map_path, "w", encoding="utf-8") as f:
            json.dump(str_id_map, f, indent=2)

        # Save metadata
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"FAISS index successfully saved to {self.index_path} ({self.index.ntotal} vectors)")
        return True

    def load_index(self) -> bool:
        if not os.path.exists(self.index_path) or not os.path.exists(self.id_map_path):
            logger.warning(f"FAISS index files missing at {self.index_path} or {self.id_map_path}")
            return False

        try:
            self.index = faiss.read_index(self.index_path)

            with open(self.id_map_path, "r", encoding="utf-8") as f:
                raw_map = json.load(f)
                self.id_map = {int(k): int(v) for k, v in raw_map.items()}

            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)

            if not self.is_healthy():
                logger.error("Loaded FAISS index failed health check (ntotal mismatch with id_map).")
                return False

            logger.info(f"FAISS store loaded successfully with {self.index.ntotal} vectors.")
            return True
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}", exc_info=True)
            return False

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = settings.FAISS_TOP_K,
        cluster_filter: Optional[List[int]] = None
    ) -> List[Tuple[int, float]]:
        if not self.is_healthy():
            raise RuntimeError("FAISS index is not loaded or unhealthy.")

        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        fetch_k = min(top_k * 5 if cluster_filter else top_k, self.index.ntotal)
        if fetch_k == 0:
            return []

        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, fetch_k)

        results = []
        for pos, sim in zip(indices[0], distances[0]):
            if pos < 0:
                continue
            if pos in self.id_map:
                record_id = self.id_map[pos]
                # Clamp cosine similarity to [0.0, 1.0]
                clamped_sim = float(np.clip(sim, 0.0, 1.0))
                results.append((record_id, clamped_sim))

        return results[:top_k]
