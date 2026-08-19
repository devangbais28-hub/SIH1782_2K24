import pytest
from unittest.mock import MagicMock
from app.services.decision import DecisionEngine


def test_decision_engine_exact_override():
    engine = DecisionEngine()
    mock_rec = MagicMock()
    mock_rec.title = "Exact Test Title"
    mock_rec.domain = "news-sports"

    candidates = [{
        "record": mock_rec,
        "scores": {
            "final_score": 1.0,
            "semantic_score": 1.0,
            "lexical_score": 1.0,
            "phonetic_score": 1.0,
            "is_exact_match": True,
            "weights_used": {"semantic": 0.5, "lexical": 0.3, "phonetic": 0.2}
        }
    }]

    decision, risk, final_score, reasons, explanation = engine.evaluate_results(
        "Exact Test Title", "news-sports", candidates
    )

    assert decision == "POTENTIAL_CONFLICT"
    assert risk == "HIGH"
    assert final_score == 1.0
    assert "Exact normalized title match found" in reasons


def test_decision_engine_threshold_boundaries():
    engine = DecisionEngine(threshold_conflict=0.75, threshold_review=0.50)
    mock_rec = MagicMock()
    mock_rec.title = "Sample Title"
    mock_rec.domain = "general"

    # High risk >= 0.75
    cand_high = [{
        "record": mock_rec,
        "scores": {
            "final_score": 0.80, "semantic_score": 0.82, "lexical_score": 0.78, "phonetic_score": None,
            "is_exact_match": False, "weights_used": {"semantic": 0.625, "lexical": 0.375, "phonetic": 0.0}
        }
    }]
    decision, risk, score, _, _ = engine.evaluate_results("Sample Title 2", "general", cand_high)
    assert decision == "POTENTIAL_CONFLICT"
    assert risk == "HIGH"

    # Medium risk 0.50 <= score < 0.75
    cand_med = [{
        "record": mock_rec,
        "scores": {
            "final_score": 0.60, "semantic_score": 0.65, "lexical_score": 0.55, "phonetic_score": None,
            "is_exact_match": False, "weights_used": {"semantic": 0.625, "lexical": 0.375, "phonetic": 0.0}
        }
    }]
    decision, risk, score, _, _ = engine.evaluate_results("Sample Title 2", "general", cand_med)
    assert decision == "REVIEW_REQUIRED"
    assert risk == "MEDIUM"

    # Low risk score < 0.50
    cand_low = [{
        "record": mock_rec,
        "scores": {
            "final_score": 0.30, "semantic_score": 0.30, "lexical_score": 0.30, "phonetic_score": None,
            "is_exact_match": False, "weights_used": {"semantic": 0.625, "lexical": 0.375, "phonetic": 0.0}
        }
    }]
    decision, risk, score, _, _ = engine.evaluate_results("Unrelated Title", "general", cand_low)
    assert decision == "NO_STRONG_CONFLICT"
    assert risk == "LOW"
