from typing import Dict, Optional, Tuple
from rapidfuzz import fuzz
from app.config import get_settings
from app.utils.normalization import normalize_title, is_latin_script
from app.utils.phonetic import compute_phonetic_code

settings = get_settings()


class ScoringEngine:
    def __init__(
        self,
        semantic_weight: float = settings.SEMANTIC_WEIGHT,
        lexical_weight: float = settings.LEXICAL_WEIGHT,
        phonetic_weight: float = settings.PHONETIC_WEIGHT
    ):
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight
        self.phonetic_weight = phonetic_weight

    def calculate_lexical_score(self, query_title: str, candidate_title: str) -> float:
        norm_query = normalize_title(query_title)
        norm_cand = normalize_title(candidate_title)

        if not norm_query or not norm_cand:
            return 0.0

        if norm_query == norm_cand:
            return 1.0

        set_ratio = fuzz.token_set_ratio(norm_query, norm_cand) / 100.0
        sort_ratio = fuzz.token_sort_ratio(norm_query, norm_cand) / 100.0
        ratio = max(set_ratio, sort_ratio)
        return float(min(max(ratio, 0.0), 1.0))

    def calculate_phonetic_score(self, query_title: str, candidate_title: str) -> Optional[float]:
        if not is_latin_script(query_title) or not is_latin_script(candidate_title):
            return None

        query_code = compute_phonetic_code(query_title)
        cand_code = compute_phonetic_code(candidate_title)

        if not query_code or not cand_code:
            return None

        if query_code == cand_code:
            return 1.0

        # Fuzzy comparison of phonetic codes
        phonetic_ratio = fuzz.token_set_ratio(query_code, cand_code) / 100.0
        return float(min(max(phonetic_ratio, 0.0), 1.0))

    def score_candidate(
        self,
        query_title: str,
        candidate_title: str,
        raw_semantic_score: float = 0.0
    ) -> Dict:
        semantic_score = float(min(max(raw_semantic_score, 0.0), 1.0))
        lexical_score = self.calculate_lexical_score(query_title, candidate_title)
        phonetic_score = self.calculate_phonetic_score(query_title, candidate_title)

        # Check exact normalized match
        norm_query = normalize_title(query_title)
        norm_cand = normalize_title(candidate_title)
        is_exact_match = (norm_query == norm_cand and len(norm_query) > 0)

        if is_exact_match:
            semantic_score = 1.0
            lexical_score = 1.0

        # Weights adjustment
        if phonetic_score is not None:
            w_sem = self.semantic_weight
            w_lex = self.lexical_weight
            w_phon = self.phonetic_weight
        else:
            total_weight = self.semantic_weight + self.lexical_weight
            w_sem = self.semantic_weight / total_weight if total_weight > 0 else 0.625
            w_lex = self.lexical_weight / total_weight if total_weight > 0 else 0.375
            w_phon = 0.0

        p_score_val = phonetic_score if phonetic_score is not None else 0.0
        final_score = (w_sem * semantic_score) + (w_lex * lexical_score) + (w_phon * p_score_val)
        final_score = float(min(max(final_score, 0.0), 1.0))

        if is_exact_match:
            final_score = 1.0

        return {
            "final_score": round(final_score, 4),
            "semantic_score": round(semantic_score, 4),
            "lexical_score": round(lexical_score, 4),
            "phonetic_score": round(phonetic_score, 4) if phonetic_score is not None else None,
            "is_exact_match": is_exact_match,
            "weights_used": {
                "semantic": round(w_sem, 3),
                "lexical": round(w_lex, 3),
                "phonetic": round(w_phon, 3)
            }
        }
