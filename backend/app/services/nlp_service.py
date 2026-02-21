"""
Moduł analizy jakości językowej tekstu.

Implementuje:
- LIX (Läsbarhetsindex) – wskaźnik czytelności neutralny językowo,
  odpowiedni dla tekstów polskich i innych słowiańskich.
  Zastępuje Flesch Reading Ease, który był kalibrowany pod angielski
  i dawał zaniżone wyniki dla polszczyzny.
- Gęstość interpunkcji
- Średnia długość słowa
"""
import re
import string
from typing import List


def get_words(text: str) -> List[str]:
    """Zwraca listę słów bez interpunkcji."""
    translator = str.maketrans("", "", string.punctuation)
    return [w for w in text.translate(translator).split() if w]


def get_sentences(text: str) -> List[str]:
    """Podział na zdania po '.', '!' i '?'."""
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_lix(text: str) -> float:
    """
    LIX (Läsbarhetsindex) – wskaźnik czytelności.

    Formuła: LIX = (słowa / zdania) + (długie_słowa * 100 / słowa)
    gdzie długie_słowa = słowa dłuższe niż 6 znaków.

    Skala:
      < 25  → Bardzo łatwy
      25-35 → Łatwy
      35-45 → Średni
      45-55 → Trudny
      > 55  → Bardzo trudny

    Zalety nad Flesch: neutralny językowo, działa dla polskiego,
    nie opiera się na liczeniu sylab (problematyczne dla języków
    fleksyjnych jak polski).
    """
    words = get_words(text)
    sentences = get_sentences(text)

    if not words or not sentences:
        return 0.0

    long_words = [w for w in words if len(w) > 6]

    lix = (len(words) / len(sentences)) + (len(long_words) * 100 / len(words))
    return round(lix, 2)


def lix_label(score: float) -> str:
    """Etykieta słowna dla wyniku LIX."""
    if score < 25:
        return "Bardzo łatwy"
    elif score < 35:
        return "Łatwy"
    elif score < 45:
        return "Średni"
    elif score < 55:
        return "Trudny"
    else:
        return "Bardzo trudny"


def lix_description(score: float) -> str:
    """Opis kontekstowy dla tekstów literackich."""
    if score < 25:
        return "Literatura dziecięca, bajki"
    elif score < 35:
        return "Proza popularna, literatura młodzieżowa"
    elif score < 45:
        return "Beletrystyka, proza współczesna"
    elif score < 55:
        return "Literatura poważna, proza złożona"
    else:
        return "Proza awangardowa, teksty naukowe"


def calculate_avg_word_length(text: str) -> float:
    """Średnia długość słowa w znakach."""
    words = get_words(text)
    if not words:
        return 0.0
    return round(sum(len(w) for w in words) / len(words), 2)


def calculate_punctuation_density(text: str) -> float:
    """Stosunek znaków interpunkcyjnych do wszystkich znaków (bez spacji)."""
    chars = [c for c in text if c != " "]
    if not chars:
        return 0.0
    punct = sum(1 for c in chars if c in string.punctuation)
    return round(punct / len(chars), 4)


def calculate_long_word_ratio(text: str) -> float:
    """Stosunek słów dłuższych niż 6 znaków do wszystkich słów."""
    words = get_words(text)
    if not words:
        return 0.0
    long_words = [w for w in words if len(w) > 6]
    return round(len(long_words) / len(words), 4)


def analyze_quality(text: str) -> dict:
    """
    Główna funkcja analizy jakości językowej.
    Zwraca słownik z metrykami.
    """
    lix = calculate_lix(text)
    return {
        "flesch_score": lix,            # pole zachowane dla kompatybilności API
        "flesch_label": lix_label(lix), # pole zachowane dla kompatybilności API
        "lix_score": lix,
        "lix_label": lix_label(lix),
        "lix_description": lix_description(lix),
        "avg_word_length": calculate_avg_word_length(text),
        "punctuation_density": calculate_punctuation_density(text),
        "long_word_ratio": calculate_long_word_ratio(text),
    }