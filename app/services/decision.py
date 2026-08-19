from typing import List, Dict, Tuple
from app.config import get_settings
from app.utils.normalization import normalize_domain

settings = get_settings()


class DecisionEngine:
    def __init__(
        self,
        threshold_conflict: float = settings.SCORE_THRESHOLD_CONFLICT,
        threshold_review: float = settings.SCORE_THRESHOLD_REVIEW
    ):
        self.threshold_conflict = threshold_conflict
        self.threshold_review = threshold_review

    def evaluate_results(
        self,
        query_title: str,
        query_domain: str,
        scored_candidates: List[Dict],
        cluster_ids: List[int] = None
    ) -> Tuple[str, str, float, List[str], str]:
        """
        Returns (decision, risk, final_score, reasons, explanation)
        """
        if not scored_candidates:
            return (
                "NO_STRONG_CONFLICT",
                "LOW",
                0.0,
                ["No candidate matches found in dataset"],
                "No matching or similar titles were found in the dataset."
            )

        # Sort candidate matches by final_score descending
        scored_candidates.sort(key=lambda x: x["scores"]["final_score"], reverse=True)
        top_match = scored_candidates[0]
        top_score = top_match["scores"]["final_score"]
        top_scores_breakdown = top_match["scores"]

        reasons = []

        # Check exact match override
        has_exact_match = any(c["scores"].get("is_exact_match", False) for c in scored_candidates)

        if has_exact_match:
            decision = "POTENTIAL_CONFLICT"
            risk = "HIGH"
            top_score = 1.0
            reasons.append("Exact normalized title match found")
        elif top_score >= self.threshold_conflict:
            decision = "POTENTIAL_CONFLICT"
            risk = "HIGH"
        elif top_score >= self.threshold_review:
            decision = "REVIEW_REQUIRED"
            risk = "MEDIUM"
        else:
            decision = "NO_STRONG_CONFLICT"
            risk = "LOW"

        # Add granular reasons
        if not has_exact_match:
            if top_scores_breakdown["lexical_score"] >= 0.85:
                reasons.append("Very high lexical similarity detected")
            if top_scores_breakdown["semantic_score"] >= 0.80:
                reasons.append("High semantic similarity detected")
            if top_scores_breakdown.get("phonetic_score") is not None and top_scores_breakdown["phonetic_score"] >= 0.80:
                reasons.append("Phonetic similarity detected")

        # Check domain matching
        norm_q_domain = normalize_domain(query_domain)
        if norm_q_domain and norm_q_domain != "unknown":
            if any(normalize_domain(c["record"].domain) == norm_q_domain for c in scored_candidates[:3]):
                reasons.append("Same domain as closest matching title")

        # Check cluster matching
        if cluster_ids and scored_candidates:
            top_cluster = getattr(scored_candidates[0]["record"], "cluster_id", None)
            if top_cluster is not None and top_cluster in cluster_ids:
                reasons.append("High semantic similarity within same cluster")

        if not reasons:
            if decision == "NO_STRONG_CONFLICT":
                reasons.append("No high-confidence conflict found")
            else:
                reasons.append("Manual review recommended because signals conflict")

        # Generate explanation text
        if decision == "POTENTIAL_CONFLICT":
            explanation = (
                f"A potential conflict was detected (Risk: HIGH). The proposed title '{query_title}' "
                f"closely matches existing title '{top_match['record'].title}' with a score of {top_score:.2f}."
            )
        elif decision == "REVIEW_REQUIRED":
            explanation = (
                f"Manual review is recommended (Risk: MEDIUM). The proposed title '{query_title}' "
                f"shares moderate similarity with existing title '{top_match['record'].title}' (score: {top_score:.2f})."
            )
        else:
            explanation = (
                f"No strong conflict was detected (Risk: LOW). The highest similarity score found is {top_score:.2f}."
            )

        return (decision, risk, round(top_score, 4), reasons, explanation)
