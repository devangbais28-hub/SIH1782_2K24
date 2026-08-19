import pytest
from app.services.scoring import ScoringEngine


def test_scoring_engine_exact_match():
    engine = ScoringEngine()
    result = engine.score_candidate("Climate News Today", "Climate News Today", raw_semantic_score=0.9)
    assert result["is_exact_match"] is True
    assert result["final_score"] == 1.0
    assert result["semantic_score"] == 1.0
    assert result["lexical_score"] == 1.0


def test_scoring_engine_weight_renormalization():
    engine = ScoringEngine(semantic_weight=0.50, lexical_weight=0.30, phonetic_weight=0.20)
    # Non-latin script query title -> phonetic score is None
    result = engine.score_candidate("समाचार पत्रिका", "समाचार पत्रिका 2", raw_semantic_score=0.8)
    assert result["phonetic_score"] is None
    assert result["weights_used"]["phonetic"] == 0.0
    assert result["weights_used"]["semantic"] == 0.625
    assert result["weights_used"]["lexical"] == 0.375


def test_scoring_engine_high_similarity():
    engine = ScoringEngine()
    result = engine.score_candidate("Global Warming Update", "Global Warming News Update", raw_semantic_score=0.85)
    assert result["final_score"] > 0.70
    assert result["lexical_score"] > 0.70
