from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Analysis(Base):
    """Model bazy danych dla wyników analizy tekstu"""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Oryginalny tekst — podgląd (500 znaków) i pełna wersja
    text_preview = Column(String(500))
    full_text = Column(Text, nullable=True)   # ← NOWE: pełny tekst do pobrania
    text_length = Column(Integer)

    # Wynik detekcji AI
    ai_probability = Column(Float)  # 0.0 - 1.0

    # Metryki stylometryczne
    ttr = Column(Float)                  # Type-Token Ratio (MATTR)
    avg_sentence_length = Column(Float)  # Średnia długość zdania
    lexical_density = Column(Float)      # Gęstość leksykalna
    entropy = Column(Float)              # Entropia Shannona

    # Metryki jakości
    flesch_score = Column(Float)         # LIX (zachowane dla kompatybilności)
    vocab_richness = Column(Float)       # Bogactwo słownikowe

    # Pełne wyniki jako JSON string
    full_results = Column(Text)