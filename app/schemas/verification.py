from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Proposed publication title", json_schema_extra={"example": "Climate Change News Today"})
    domain: str = Field(default="general", max_length=200, description="Publication domain/category", json_schema_extra={"example": "news-environment"})
    language: str = Field(default="English", max_length=50, description="Language of publication", json_schema_extra={"example": "English"})
    description: Optional[str] = Field(default=None, max_length=2000, description="Optional brief description")


class ScoreWeights(BaseModel):
    semantic: float
    lexical: float
    phonetic: float


class ScoreBreakdown(BaseModel):
    semantic_score: float
    lexical_score: float
    phonetic_score: Optional[float] = None
    weights_used: ScoreWeights


class MatchedCandidate(BaseModel):
    id: int
    title: str
    domain: str
    language: str
    description: Optional[str] = None
    semantic_score: float
    lexical_score: float
    phonetic_score: Optional[float] = None
    final_score: float


class VerificationResponse(BaseModel):
    verification_id: str
    decision: str = Field(..., description="POTENTIAL_CONFLICT, REVIEW_REQUIRED, or NO_STRONG_CONFLICT")
    risk: str = Field(..., description="HIGH, MEDIUM, or LOW")
    final_score: float
    score_breakdown: ScoreBreakdown
    top_matches: List[MatchedCandidate]
    reasons: List[str]
    explanation: str
    candidate_count: int
    processing_time_ms: float


class SubmissionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    domain: str = Field(default="general", max_length=200)
    language: str = Field(default="English", max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    contact_info: Optional[str] = Field(default=None, max_length=500)


class SubmissionResponse(BaseModel):
    submission_id: int
    record_status: str = Field(..., description="approved, pending, or rejected")
    verification_result: VerificationResponse
