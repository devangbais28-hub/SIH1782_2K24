import numpy as np
import faiss
from typing import List, Union
from sentence_transformers import SentenceTransformer
from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()


class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer model loaded successfully.")
        return self._model

    def encode_titles(self, titles: List[str], batch_size: int = 64) -> np.ndarray:
        if not titles:
            return np.empty((0, 384), dtype=np.float32)

        embeddings = self.model.encode(
            titles,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embeddings = embeddings.astype(np.float32)
        # Ensure L2 normalization for Inner Product cosine equivalence
        faiss.normalize_L2(embeddings)
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        if not query or not query.strip():
            return np.zeros((1, 384), dtype=np.float32)

        embedding = self.model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embedding = embedding.astype(np.float32)
        faiss.normalize_L2(embedding)
        return embedding
