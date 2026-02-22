from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Analysis(Base):
    """Model bazy danych dla wyników analizy tekstu"""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    text_preview = Column(String(500))
    full_text = Column(Text, nullable=True)
    text_length = Column(Integer)


    ai_probability = Column(Float)

    ttr = Column(Float)                  # Type-Token Ratio (MATTR)
    avg_sentence_length = Column(Float)  # Średnia długość zdania
    lexical_density = Column(Float)      # Gęstość leksykalna
    entropy = Column(Float)              # Entropia Shannona

    flesch_score = Column(Float)         # LIX (zachowane dla kompatybilności)
    vocab_richness = Column(Float)       # Bogactwo słownikowe

    full_results = Column(Text)