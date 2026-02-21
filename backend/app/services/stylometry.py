"""
Moduł analizy stylometrycznej tekstu literackiego.
Implementuje metryki: TTR, gęstość leksykalna, entropia, n-gramy.
"""
import math
import string
from collections import Counter
from typing import List


def tokenize(text: str) -> List[str]:
    """Tokenizacja – zamiana tekstu na listę słów (lowercase, bez interpunkcji)."""
    text = text.lower()
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    return [w for w in text.split() if w]


def get_sentences(text: str) -> List[str]:
    """Podział tekstu na zdania po '.', '!' i '?'."""
    import re
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_ttr(tokens: List[str], window: int = 50) -> float:
    """
    MATTR – Moving Average Type-Token Ratio.
    Okno 50 tokenów, uśrednione po całym tekście.
    Niewrażliwe na długość tekstu (w przeciwieństwie do zwykłego TTR).
    """
    if not tokens:
        return 0.0
    if len(tokens) <= window:
        # za krótki tekst — fallback do zwykłego TTR
        return round(len(set(tokens)) / len(tokens), 4)
    
    scores = [
        len(set(tokens[i:i + window])) / window
        for i in range(len(tokens) - window + 1)
    ]
    return round(sum(scores) / len(scores), 4)


def calculate_avg_sentence_length(text: str) -> float:
    """Średnia liczba słów w zdaniu."""
    sentences = get_sentences(text)
    if not sentences:
        return 0.0
    word_counts = [len(s.split()) for s in sentences if s]
    return sum(word_counts) / len(word_counts)


def calculate_lexical_density(tokens: List[str], text: str) -> float:
    """
    Gęstość leksykalna: stosunek słów treściowych do wszystkich tokenów.
    Słowa treściowe = nie-stopwords (lista 50 najczęstszych polskich).
    """
    POLISH_STOPWORDS = {
        "i", "w", "z", "na", "do", "się", "nie", "to", "że", "a",
        "jak", "ale", "po", "co", "go", "jej", "jego", "za", "ten",
        "ta", "te", "tego", "tej", "o", "już", "by", "tak", "ze",
        "czy", "ich", "im", "przez", "pan", "była", "było", "były",
        "jest", "są", "będzie", "był", "być", "ma", "mam", "mają",
        "gdy", "bo", "mu", "mu", "mi", "nas", "nam", "on", "ona",
        "oni", "je", "też", "tylko", "więc", "tu", "tam", "tego"
    }
    if not tokens:
        return 0.0
    content = [t for t in tokens if t not in POLISH_STOPWORDS]
    return round(len(content) / len(tokens), 4)


def calculate_entropy(tokens: List[str]) -> float:
    """
    Entropia Shannona: mierzy losowość/nieprzewidywalność tekstu.
    Wyższy = bardziej różnorodny/unikalny tekst.
    """
    if not tokens:
        return 0.0
    freq = Counter(tokens)
    total = len(tokens)
    entropy = -sum((count / total) * math.log2(count / total)
                   for count in freq.values())
    return round(entropy, 4)


def calculate_vocab_richness(tokens: List[str]) -> float:
    """
    Bogactwo słownikowe (Yule's K uproszczony):
    stosunek słów używanych raz do wszystkich unikalnych.
    """
    if not tokens:
        return 0.0
    freq = Counter(tokens)
    hapax = sum(1 for count in freq.values() if count == 1)
    return round(hapax / len(set(tokens)), 4) if len(set(tokens)) > 0 else 0.0


def get_top_ngrams(tokens: List[str], n: int = 2, top_k: int = 5) -> list:
    if len(tokens) < n:
        return []
    ngrams = [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
    freq = Counter(ngrams)
    return [
        {"ngram": " ".join(gram), "count": count}
        for gram, count in freq.most_common(top_k)
        if count >= 2  # jedyna zmiana
    ]


def analyze_stylometry(text: str) -> dict:
    tokens = tokenize(text)
    sentences = get_sentences(text)

    return {
        "ttr": calculate_ttr(tokens),              # ← teraz MATTR
        "avg_sentence_length": round(calculate_avg_sentence_length(text), 2),
        "lexical_density": calculate_lexical_density(tokens, text),  # ← teraz stopwords
        "entropy": calculate_entropy(tokens),
        "vocab_richness": calculate_vocab_richness(tokens),
        "word_count": len(tokens),
        "sentence_count": len(sentences),
        "unique_words": len(set(tokens)),
        "top_ngrams": get_top_ngrams(tokens, n=2, top_k=5),
    }