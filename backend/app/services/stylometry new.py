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
    """
    Podział tekstu na zdania po '.', '!' i '?'.

    Heurystyka wierszowa: jeśli tekst ma mniej niż jedno zdanie
    na 40 słów (np. poezja bez kropek na końcu wersu), przełącza się
    na segmentację po wierszach (liniach).
    """
    import re
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    word_count = len(text.split())
    if word_count > 0 and len(sentences) < word_count / 40:
        verse_lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > 5]
        if len(verse_lines) > len(sentences):
            return verse_lines

    return sentences


def calculate_ttr(tokens: List[str], window: int = 50) -> float:
    """
    MATTR – Moving Average Type-Token Ratio.
    Okno 50 tokenów, uśrednione po całym tekście.
    Niewrażliwe na długość tekstu (w przeciwieństwie do zwykłego TTR).
    """
    if not tokens:
        return 0.0
    if len(tokens) <= window:
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


def calculate_sentence_length_std(text: str) -> float:
    """
    Odchylenie standardowe długości zdań.

    Miara zróżnicowania struktury syntaktycznej tekstu.
    Teksty XIX-wieczne przeplatają zdania krótkie z rozbudowanymi
    periodami — daje wysokie STD (~12-18).
    Teksty XXI-wieczne i teksty generowane przez AI mają bardziej
    jednorodne zdania — daje niskie STD (~3-7).
    Wiarygodne dla tekstów zawierających co najmniej 5 zdań.
    """
    sentences = get_sentences(text)
    if len(sentences) < 2:
        return 0.0
    lengths = [len(s.split()) for s in sentences if s]
    if not lengths:
        return 0.0
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    return round(math.sqrt(variance), 4)


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
    Bogactwo słownikowe (hapax legomena ratio):
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
        if count >= 2
    ]


def analyze_stylometry(text: str) -> dict:
    tokens = tokenize(text)
    sentences = get_sentences(text)

    return {
        "ttr":                  calculate_ttr(tokens),
        "avg_sentence_length":  round(calculate_avg_sentence_length(text), 2),
        "sentence_length_std":  calculate_sentence_length_std(text),
        "lexical_density":      calculate_lexical_density(tokens, text),
        "entropy":              calculate_entropy(tokens),
        "vocab_richness":       calculate_vocab_richness(tokens),
        "word_count":           len(tokens),
        "sentence_count":       len(sentences),
        "unique_words":         len(set(tokens)),
        "top_ngrams":           get_top_ngrams(tokens, n=2, top_k=5),
    }