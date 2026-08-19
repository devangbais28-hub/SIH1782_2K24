import os
import time
import json
import numpy as np
import pandas as pd
from typing import List, Dict
from app.database import SessionLocal
from app.vector.embedding_service import EmbeddingService
from app.vector.faiss_store import FAISSStore
from app.services.verification import VerificationService
from app.utils.logging import logger

OUTPUT_DIR = "output"


def run_benchmark(num_queries: int = 100):
    logger.info(f"Starting TitleGuard Benchmark pipeline with {num_queries} queries...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        faiss_store = FAISSStore()
        if not faiss_store.load_index():
            logger.error("Cannot run benchmark because FAISS index is not built/ready.")
            return

        embedder = EmbeddingService()
        service = VerificationService(db, faiss_store, embedder)

        # 1. Warm model & index
        logger.info("Warming model and FAISS index with dummy queries...")
        for _ in range(5):
            service.verify_title("Warmup Title Test", domain="technology")

        # Sample query templates
        sample_queries = [
            ("Climate Change News", "news-environment"),
            ("Tech Innovations Daily", "news-technology"),
            ("Global Financial Review", "business"),
            ("Sports Weekly Digest", "news-sports"),
            ("Health & Wellness Magazine", "health"),
            ("Artificial Intelligence Frontier", "technology"),
            ("National Geographic Science", "science"),
            ("International Policy Journal", "politics"),
            ("Entertainment Tonight Buzz", "entertainment"),
            ("Education Horizons Today", "education")
        ]

        latencies_ms: List[float] = []

        logger.info(f"Executing {num_queries} benchmark requests...")
        for i in range(num_queries):
            query_title, domain = sample_queries[i % len(sample_queries)]
            full_title = f"{query_title} Variation {i + 1}"

            start_t = time.perf_counter()
            res = service.verify_title(full_title, domain=domain)
            elapsed_ms = (time.perf_counter() - start_t) * 1000
            latencies_ms.append(elapsed_ms)

        # Compute summary metrics
        arr = np.array(latencies_ms)
        metrics = {
            "query_count": num_queries,
            "mean_ms": round(float(np.mean(arr)), 2),
            "median_ms": round(float(np.median(arr)), 2),
            "p95_ms": round(float(np.percentile(arr, 95)), 2),
            "p99_ms": round(float(np.percentile(arr, 99)), 2),
            "min_ms": round(float(np.min(arr)), 2),
            "max_ms": round(float(np.max(arr)), 2),
            "meets_target_under_500ms": bool(np.percentile(arr, 95) < 500.0)
        }

        logger.info("==========================================")
        logger.info("BENCHMARK RESULTS")
        logger.info("==========================================")
        logger.info(f"Mean Latency:    {metrics['mean_ms']} ms")
        logger.info(f"Median Latency:  {metrics['median_ms']} ms")
        logger.info(f"p95 Latency:     {metrics['p95_ms']} ms")
        logger.info(f"p99 Latency:     {metrics['p99_ms']} ms")
        logger.info(f"Min Latency:     {metrics['min_ms']} ms")
        logger.info(f"Max Latency:     {metrics['max_ms']} ms")
        logger.info("==========================================")

        # Write output JSON
        json_path = os.path.join(OUTPUT_DIR, "benchmark_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # Write output CSV
        csv_path = os.path.join(OUTPUT_DIR, "benchmark_results.csv")
        pd.DataFrame([metrics]).to_csv(csv_path, index=False)

        logger.info(f"Benchmark results written to {json_path} and {csv_path}")

    finally:
        db.close()


if __name__ == "__main__":
    run_benchmark()
