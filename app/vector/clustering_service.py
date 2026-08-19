import os
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans
from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()


class ClusteringService:
    def __init__(self, metadata_path: str = settings.CLUSTER_METADATA_PATH):
        self.metadata_path = metadata_path
        self.centroids: Optional[np.ndarray] = None
        self.metadata: Dict = {}

    def fit_clusters(
        self,
        embeddings: np.ndarray,
        record_ids: List[int],
        n_clusters: Optional[int] = None
    ) -> Dict[int, int]:
        """
        Cluster embeddings using K-Means.
        Returns dict mapping record_id -> cluster_id.
        """
        n = embeddings.shape[0]
        if n_clusters is None:
            # Heuristic: sqrt(n / 2), clamped to [10, 200]
            n_clusters = max(10, min(200, int(np.sqrt(n / 2))))

        logger.info(f"Running K-Means clustering with k={n_clusters} on {n} vectors...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10, max_iter=300)
        labels = kmeans.fit_predict(embeddings)
        self.centroids = kmeans.cluster_centers_.astype(np.float32)

        id_to_cluster = {}
        cluster_sizes = {}
        for i, rid in enumerate(record_ids):
            cid = int(labels[i])
            id_to_cluster[rid] = cid
            cluster_sizes[cid] = cluster_sizes.get(cid, 0) + 1

        self.metadata = {
            "n_clusters": n_clusters,
            "algorithm": "KMeans",
            "record_count": n,
            "cluster_sizes": cluster_sizes
        }

        logger.info(f"Clustering complete. {n_clusters} clusters formed.")
        return id_to_cluster

    def save_metadata(self) -> None:
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)
        data_to_save = {
            **self.metadata,
            "centroids": self.centroids.tolist() if self.centroids is not None else []
        }
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2)
        logger.info(f"Cluster metadata saved to {self.metadata_path}")

    def load_metadata(self) -> bool:
        if not os.path.exists(self.metadata_path):
            logger.warning(f"Cluster metadata not found at {self.metadata_path}")
            return False
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.centroids = np.array(data.get("centroids", []), dtype=np.float32)
        self.metadata = {k: v for k, v in data.items() if k != "centroids"}
        logger.info(f"Cluster metadata loaded: {self.metadata.get('n_clusters', 0)} clusters.")
        return True

    def assign_cluster(self, query_embedding: np.ndarray, top_n: int = settings.CLUSTER_TOP_N) -> List[int]:
        """
        Given a query embedding, return the top_n nearest cluster IDs
        by cosine distance to centroids.
        """
        if self.centroids is None or len(self.centroids) == 0:
            return []
        # Normalize for cosine
        query_norm = query_embedding.flatten()
        query_norm = query_norm / (np.linalg.norm(query_norm) + 1e-9)
        centroid_norms = self.centroids / (np.linalg.norm(self.centroids, axis=1, keepdims=True) + 1e-9)
        similarities = centroid_norms @ query_norm
        top_indices = np.argsort(-similarities)[:top_n]
        return [int(i) for i in top_indices]
