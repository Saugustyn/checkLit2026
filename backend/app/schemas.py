from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AnalysisRequest(BaseModel):
    text: str
    class Config:
        json_schema_extra = {"example": {"text": "To jest przykładowy tekst literacki do analizy..."}}


class StylometryResult(BaseModel):
    ttr: float
    avg_sentence_length: float
    sentence_length_std: float = 0.0
    lexical_density: float
    entropy: float
    vocab_richness: float
    word_count: int
    sentence_count: int
    unique_words: int
    top_ngrams: list[dict]


class QualityResult(BaseModel):
    flesch_score: float
    flesch_label: str
    lix_score: float
    lix_label: str
    lix_description: str
    avg_word_length: float
    punctuation_density: float
    long_word_ratio: float


class AIDetectionResult(BaseModel):
    ai_probability: float
    human_probability: float
    label: str
    confidence: str
    perplexity: Optional[float] = None


class AnalysisResponse(BaseModel):
    id: int
    created_at: datetime
    text_preview: str
    text_length: int
    ai_detection: AIDetectionResult
    stylometry: StylometryResult
    quality: QualityResult
    full_text: str


class AnalysisListItem(BaseModel):
    id: int
    created_at: datetime
    text_preview: str
    text_length: int
    ai_probability: float
    ttr: float
    flesch_score: float
    class Config:
        from_attributes = True


class CompareRequest(BaseModel):
    text_a: str
    text_b: str


class CompareResponse(BaseModel):
    text_a: StylometryResult
    text_b: StylometryResult
    similarity_score: float
    similarity_breakdown: dict = {}