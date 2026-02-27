"""
Moduł stylometryczny systemu checkLit.

Oblicza zestaw miar językoznawczych dla tekstu literackiego w języku polskim:
  - MATTR (Moving Average Type-Token Ratio)
  - Gęstość leksykalna (z rozbudowaną listą stopwords)
  - Entropia Shannona
  - Bogactwo słownikowe (hapax legomena ratio)
  - Odchylenie standardowe długości zdań
  - Top-5 bigramów

Iteracja v2: poprawiona tokenizacja Unicode, ochrona skrótów w segmentacji zdań,
rozbudowana lista polskich stopwords (~110 wyrazów).
"""

import math
import re
import unicodedata
from collections import Counter
from typing import List


# ---------------------------------------------------------------------------
# Zasoby językowe
# ---------------------------------------------------------------------------

# Tokenizacja: polskie litery + apostrof / łącznik wewnątrz wyrazu
_WORD_RE = re.compile(
    r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+"
    r"(?:[-\u2010\u2011'][A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+)*",
    re.UNICODE,
)

# Koniec zdania: . ! ? … (wielokrotnie)
_SENT_END_RE = re.compile(r"[.!?…]+")

# Typowe skróty, po których kropka nie kończy zdania
_ABBREVIATIONS = {
    "dr", "prof", "mgr", "inż", "hab", "itd", "itp", "np", "m.in",
    "tj", "tzn", "św", "al", "ul", "pl", "nr", "str", "s", "rozdz",
    "red", "wyd", "dz", "p", "godz", "rys", "tab", "pkt", "ust",
    "art", "zob", "por", "ok", "ok.", "proc", "wg", "tzn", "m",
    "km", "cm", "mm", "kg", "zł",
}

# Rozbudowana polska lista stopwords (~110 słów funkcyjnych).
# Obejmuje spójniki, przyimki, zaimki, partykuły i najczęstsze formy
# czasowników posiłkowych — czyli wyrazy, które nie niosą treści.
_STOPWORDS = {
    # Spójniki i partykuły
    "i", "a", "ale", "lecz", "lub", "albo", "ani", "czy", "że", "bo",
    "więc", "zatem", "jednak", "jednakże", "choć", "chociaż", "mimo",
    "dlatego", "ponieważ", "gdy", "kiedy", "gdy", "skoro", "żeby",
    "aby", "by", "też", "również", "nawet", "tylko", "już", "jeszcze",
    "właśnie", "jednak", "aż", "zaś", "bądź", "tudzież", "zarówno",
    # Przyimki
    "w", "we", "z", "ze", "za", "do", "od", "po", "nad", "pod",
    "przed", "przez", "przy", "między", "wśród", "dla", "na", "o",
    "u", "ku", "około", "spod", "spoza", "sprzed", "wokół", "wobec",
    # Zaimki osobowe i dzierżawcze
    "ja", "ty", "on", "ona", "ono", "my", "wy", "oni", "one",
    "mnie", "mi", "mną", "ciebie", "tobie", "tobą", "go", "jego",
    "jemu", "jej", "nim", "nią", "nam", "nami", "wam", "wami",
    "ich", "im", "nimi", "się", "sobie", "siebie",
    "mój", "moja", "moje", "twój", "twoja", "twoje",
    "jego", "jej", "nasz", "nasza", "nasze", "wasz", "wasza", "wasze",
    "ich", "swój", "swoja", "swoje",
    # Zaimki wskazujące i pytające
    "ten", "ta", "to", "tego", "tej", "temu", "tę", "ci", "te",
    "tam", "tu", "tutaj", "stąd", "stamtąd", "taki", "taka", "takie",
    "który", "która", "które", "kto", "co",
    # Przysłówki o niskiej treści
    "tak", "nie", "już", "jeszcze", "bardzo", "trochę", "więcej",
    "mniej", "wiele", "mało", "tu", "tam", "tu",
    # Czasowniki posiłkowe — najczęstsze formy
    "jest", "są", "był", "była", "było", "byli", "były",
    "będzie", "będą", "być", "bywa", "bywać",
    "został", "została", "zostało", "zostali", "zostały", "zostać",
    "mam", "masz", "ma", "mamy", "macie", "mają",
    "miał", "miała", "miało", "mieli", "miały", "mieć",
    "niech", "oto",
}


# ---------------------------------------------------------------------------
# Normalizacja i tokenizacja
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalizacja Unicode (NFKC) i ujednolicenie znaków nowej linii."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def tokenize(text: str) -> List[str]:
    """
    Tokenizacja z obsługą polskich liter Unicode.
    Zwraca listę słów w małych literach; zachowuje łączniki i apostrofy
    wewnątrz wyrazu (np. 'przy-jazd', 'd'Artagnan').
    """
    return _WORD_RE.findall(_normalize(text).lower())


# ---------------------------------------------------------------------------
# Segmentacja zdań
# ---------------------------------------------------------------------------

def _is_abbreviation(token: str) -> bool:
    """Heurystyczne wykrywanie skrótów przed kropką."""
    t = token.lower().rstrip(".")
    if not t:
        return False
    if t in _ABBREVIATIONS:
        return True
    # Inicjał: "A.", "J."
    if len(t) == 1 and t.isalpha():
        return True
    return False


def get_sentences(text: str) -> List[str]:
    """
    Segmentacja zdań z ochroną skrótów i inicjałów.

    Dla tekstów poetyckich (< 1 zdanie na 40 słów) automatycznie
    przełącza się na segmentację wierszową.
    """
    text = _normalize(text)
    if not text.strip():
        return []

    sentences: List[str] = []
    start = 0

    for m in _SENT_END_RE.finditer(text):
        chunk = text[start:m.end()].strip()
        if not chunk:
            start = m.end()
            continue

        # Ochrona skrótów: sprawdź token przed kropką
        if "." in text[m.start():m.end()]:
            before = text[start:m.start()].rstrip()
            # Liczby dziesiętne: "3.14" — nie dziel
            if re.search(r"\d\.\d$", before):
                continue
            # Token tuż przed kropką
            last = re.search(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+\s*$", before)
            if last and _is_abbreviation(last.group(0)):
                continue

        sentences.append(chunk)
        start = m.end()

    tail = text[start:].strip()
    if tail:
        sentences.append(tail)

    # Heurystyka poetycka
    word_count = len(text.split())
    if word_count > 0 and len(sentences) < word_count / 40:
        verse_lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > 5]
        if len(verse_lines) > len(sentences):
            return verse_lines

    return [s.strip(' \t\n"„"') for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# Miary stylometryczne
# ---------------------------------------------------------------------------

def calculate_ttr(tokens: List[str], window: int = 50) -> float:
    """
    MATTR – Moving Average Type-Token Ratio.
    Okno 50 tokenów; dla krótkich tekstów stosuje klasyczny TTR.
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


def calculate_avg_sentence_length(sentences: List[str]) -> float:
    """Średnia liczba słów na zdanie."""
    if not sentences:
        return 0.0
    lengths = [len(s.split()) for s in sentences if s]
    return sum(lengths) / len(lengths) if lengths else 0.0


def calculate_sentence_length_std(sentences: List[str]) -> float:
    """
    Odchylenie standardowe długości zdań.

    Miara zróżnicowania struktury syntaktycznej. Teksty XIX-wieczne
    przeplatają zdania krótkie z rozbudowanymi periodami (STD ~ 12–18);
    teksty współczesne i generowane przez AI mają bardziej jednorodną
    składnię (STD ~ 3–7). Wiarygodne dla tekstów z co najmniej 5 zdaniami.
    """
    if len(sentences) < 2:
        return 0.0
    lengths = [len(s.split()) for s in sentences if s]
    if not lengths:
        return 0.0
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    return round(math.sqrt(variance), 4)


def calculate_lexical_density(tokens: List[str]) -> float:
    """
    Gęstość leksykalna: stosunek słów treściowych do wszystkich tokenów.
    Słowa treściowe = tokeny spoza listy ~110 polskich stopwords.
    """
    if not tokens:
        return 0.0
    content = [t for t in tokens if t not in _STOPWORDS]
    return round(len(content) / len(tokens), 4)


def calculate_entropy(tokens: List[str]) -> float:
    """Entropia Shannona: mierzy różnorodność/nieprzewidywalność tekstu."""
    if not tokens:
        return 0.0
    freq = Counter(tokens)
    total = len(tokens)
    return round(-sum(
        (c / total) * math.log2(c / total)
        for c in freq.values()
    ), 4)


def calculate_vocab_richness(tokens: List[str]) -> float:
    """Hapax legomena ratio: stosunek słów jednorazowych do wszystkich unikalnych."""
    if not tokens:
        return 0.0
    freq = Counter(tokens)
    hapax = sum(1 for c in freq.values() if c == 1)
    V = len(freq)
    return round(hapax / V, 4) if V > 0 else 0.0


def get_top_ngrams(tokens: List[str], n: int = 2, top_k: int = 5) -> list:
    """Top-k najczęstszych n-gramów (min. 2 wystąpienia)."""
    if len(tokens) < n:
        return []
    ngrams = [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
    freq = Counter(ngrams)
    return [
        {"ngram": " ".join(gram), "count": count}
        for gram, count in freq.most_common(top_k)
        if count >= 2
    ]


# ---------------------------------------------------------------------------
# Interfejs publiczny modułu
# ---------------------------------------------------------------------------

def analyze_stylometry(text: str) -> dict:
    """
    Główna funkcja modułu — oblicza kompletny profil stylometryczny.

    Zwraca słownik kompatybilny ze schematem Pydantic StylometryResult:
      ttr, avg_sentence_length, sentence_length_std,
      lexical_density, entropy, vocab_richness,
      word_count, sentence_count, unique_words, top_ngrams.
    """
    tokens = tokenize(text)
    sentences = get_sentences(text)

    return {
        "ttr":                   calculate_ttr(tokens),
        "avg_sentence_length":   round(calculate_avg_sentence_length(sentences), 2),
        "sentence_length_std":   calculate_sentence_length_std(sentences),
        "lexical_density":       calculate_lexical_density(tokens),
        "entropy":               calculate_entropy(tokens),
        "vocab_richness":        calculate_vocab_richness(tokens),
        "word_count":            len(tokens),
        "sentence_count":        len(sentences),
        "unique_words":          len(set(tokens)),
        "top_ngrams":            get_top_ngrams(tokens, n=2, top_k=5),
    }