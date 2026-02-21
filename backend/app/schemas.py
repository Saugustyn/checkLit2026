from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AnalysisRequest(BaseModel):
    """Schemat żądania analizy tekstu"""
    text: str

    class Config:
        json_schema_extra = {
            "example": {
                "text": "To jest przykładowy tekst literacki do analizy..."
            }
        }


class StylometryResult(BaseModel):
    """Wyniki analizy stylometrycznej"""
    ttr: float
    avg_sentence_length: float
    lexical_density: float
    entropy: float
    vocab_richness: float
    word_count: int
    sentence_count: int
    unique_words: int
    top_ngrams: list[dict]


class QualityResult(BaseModel):
    """Wyniki analizy jakości językowej"""
    # Pola flesch_ zachowane dla kompatybilności (zawierają wartości LIX)
    flesch_score: float
    flesch_label: str
    # Pola LIX – właściwy wskaźnik dla języka polskiego
    lix_score: float
    lix_label: str
    lix_description: str
    avg_word_length: float
    punctuation_density: float
    long_word_ratio: float


class AIDetectionResult(BaseModel):
    """Wyniki detekcji AI metodą perplexity (Herbert)"""
    ai_probability: float
    human_probability: float
    label: str
    confidence: str
    perplexity: Optional[float] = None  # None gdy model niedostępny (fallback)


class AnalysisResponse(BaseModel):
    """Pełna odpowiedź z wynikami analizy"""
    id: int
    created_at: datetime
    text_preview: str
    text_length: int
    ai_detection: AIDetectionResult
    stylometry: StylometryResult
    quality: QualityResult


class AnalysisListItem(BaseModel):
    """Element listy historii analiz"""
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
    """Schemat żądania porównania dwóch tekstów"""
    text_a: str
    text_b: str


class CompareResponse(BaseModel):
    """Wyniki porównania dwóch tekstów"""
    text_a: StylometryResult
    text_b: StylometryResult
    similarity_score: float