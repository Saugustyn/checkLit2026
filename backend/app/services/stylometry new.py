# stylometry_pl.py
from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass
from collections import Counter
from typing import Dict, List, Tuple, Optional


# --- konfiguracja / zasoby ---

POLISH_LETTERS = "A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż"

# Prosty, ale praktyczny zestaw skrótów – możesz rozszerzyć pod swój korpus
DEFAULT_ABBREVIATIONS_PL = {
    "dr", "prof", "mgr", "inż", "inż.", "hab", "itd", "itp", "np", "m.in", "tj", "tzn",
    "św", "al", "ul", "pl", "nr", "str", "s", "rozdz", "red", "wyd", "dz", "p",
    "godz", "rys", "tab", "pkt", "ust", "art", "zob",
}

# Uwaga: to nie jest "idealna" stoplista lingwistyczna – to pragmatyczny filtr słów funkcyjnych.
# Dla lepszej jakości: podmień na listę zewnętrzną (np. z zasobu projektu) albo POS-taguj.
DEFAULT_STOPWORDS_PL = {
    "i","a","ale","lub","albo","lecz","że","z","za","do","od","u","o","w","we","na","nad","pod","przed","przez",
    "po","bez","dla","jak","gdy","kiedy","bo","więc","czy","żeby","aby","choć","chociaż","ponieważ","dlatego",
    "to","tego","temu","tę","ta","ten","te","ci","tam","tu","tutaj","stąd","stamtąd","tak","nie","już","jeszcze",
    "bardzo","trochę","wiele","mało","więcej","mniej","aż","tylko","również","też","nawet",
    "ja","ty","on","ona","ono","my","wy","oni","one","mnie","mi","mną","ciebie","ci","tobie","tobą",
    "go","jego","jemu","nim","nią","jej","jejże","im","nimi","ich","nas","nam","nami","was","wam","wami",
    "się","sobie","siebie","swoje","swój","swoja","swoją","swoim","swojej",
    "jest","są","był","była","było","byli","były","będzie","będą","być","bywa","został","została","zostało","zostać",
    "mam","masz","ma","mamy","macie","mają","miał","miała","miało","mieć",
    "niech","niechże","oto","właśnie",
}

# Token słowa: polskie litery, dopuszcza łączniki i apostrof w środku wyrazu
WORD_RE = re.compile(
    rf"[{POLISH_LETTERS}]+(?:[--–—'’][{POLISH_LETTERS}]+)*",
    re.UNICODE
)

# Dla "detekcji dialogu" – linie zaczynające się od myślnika/pauzy
DIALOGUE_LINE_RE = re.compile(r"^\s*[—–-]\s+\S", re.UNICODE)

# Koniec zdania: . ! ? … (wielokrotnie)
SENT_END_RE = re.compile(r"[.!?…]+", re.UNICODE)

# Interpunkcja, którą warto liczyć jako cechy stylu (literatura!)
PUNCT_CHARS = {
    ",": "comma",
    ";": "semicolon",
    ":": "colon",
    "—": "emdash",
    "–": "endash",
    "-": "hyphen",
    "…": "ellipsis",
    ".": "dot",
    "!": "excl",
    "?": "qmark",
    "\"": "quote",
    "„": "quote_pl_open",
    "”": "quote_pl_close",
    "’": "apostrophe",
    "'": "apostrophe_ascii",
    "(": "lparen",
    ")": "rparen",
}


@dataclass
class StylometryConfig:
    mattr_window: int = 50
    verse_word_sentence_ratio: float = 40.0  # jeśli < 1 zdanie na 40 słów -> poezja/wersy
    min_line_len_for_verse: int = 5
    abbreviations: Optional[set] = None
    stopwords: Optional[set] = None
    mtld_threshold: float = 0.72  # typowy próg MTLD


# --- narzędzia tekstowe ---

def normalize_text(text: str) -> str:
    """
    Normalizacja minimalna:
    - unifikuje znaki Unicode (NFKC),
    - normalizuje nowe linie.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def tokenize_words(text: str) -> List[str]:
    """
    Tokenizacja słów:
    - Unicode,
    - zachowuje polskie znaki,
    - dopuszcza łączniki i apostrofy wewnątrz wyrazu.
    """
    text = normalize_text(text).lower()
    return WORD_RE.findall(text)


def punctuation_stats(text: str) -> Dict[str, float]:
    """
    Liczy interpunkcję jako cechy stylu.
    Zwraca częstości na 1000 znaków (stabilniejsze od "na zdanie").
    """
    text = normalize_text(text)
    if not text:
        return {}

    total_chars = max(len(text), 1)
    counts = Counter(ch for ch in text if ch in PUNCT_CHARS)

    out: Dict[str, float] = {}
    for ch, name in PUNCT_CHARS.items():
        if ch in counts:
            out[f"punct_{name}_per_1kchar"] = round((counts[ch] / total_chars) * 1000.0, 4)

    # Przydatna agregacja dla dialogów: pauzy ogółem
    dash_total = counts.get("—", 0) + counts.get("–", 0) + counts.get("-", 0)
    out["punct_dash_per_1kchar"] = round((dash_total / total_chars) * 1000.0, 4)
    return out


def looks_like_abbrev(token: str, abbreviations: set) -> bool:
    """
    Heurystyka: token przed kropką jest skrótem / inicjałem.
    """
    t = token.lower().strip(".")
    if not t:
        return False
    if t in abbreviations:
        return True
    # Inicjał: "A." / "J."
    if len(t) == 1 and t.isalpha():
        return True
    # "m.in." -> ostatni człon
    if t.endswith("in") and "m.in" in abbreviations:
        return True
    return False


def split_sentences_pl(text: str, cfg: StylometryConfig) -> List[str]:
    """
    Segmentacja zdań:
    - rozbija po . ! ? …,
    - nie rozbija po skrótach i inicjałach,
    - obsługuje poezję: jeśli bardzo mało zdań względem słów -> segmentacja po wierszach.
    """
    text = normalize_text(text)
    if not text.strip():
        return []

    abbreviations = cfg.abbreviations or DEFAULT_ABBREVIATIONS_PL

    # 1) wstępna segmentacja "koniec zdania"
    sentences: List[str] = []
    start = 0
    for m in SENT_END_RE.finditer(text):
        end = m.end()
        chunk = text[start:end].strip()
        if not chunk:
            start = end
            continue

        # sprawdzamy, czy to kropka po skrócie / inicjale / liczbie typu "3.14"
        end_punct = text[m.start():m.end()]
        if "." in end_punct:
            before = text[start:m.start()].rstrip()
            # liczby dziesiętne / listy "1." – tu nie ma idealnej reguły, ale chronimy "3.14"
            if re.search(r"\d\.\d$", before):
                continue
            # token przed kropką
            last_token_match = re.search(rf"([{POLISH_LETTERS}]+)\s*$", before)
            if last_token_match:
                last_token = last_token_match.group(1)
                if looks_like_abbrev(last_token, abbreviations):
                    continue

        sentences.append(chunk)
        start = end

    tail = text[start:].strip()
    if tail:
        sentences.append(tail)

    # 2) heurystyka poezji / wersów
    word_count = len(tokenize_words(text))
    if word_count > 0 and len(sentences) < word_count / cfg.verse_word_sentence_ratio:
        verse_lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > cfg.min_line_len_for_verse]
        if len(verse_lines) > len(sentences):
            return verse_lines

    # 3) doczyszczanie (np. cudzysłowy przy końcu)
    cleaned = [s.strip(" \t\n\"“”„”) for s in sentences if s.strip()]
    return cleaned


# --- miary leksykalne / stylometryczne ---

def mattr(tokens: List[str], window: int) -> float:
    if not tokens:
        return 0.0
    if len(tokens) <= window:
        return len(set(tokens)) / max(len(tokens), 1)

    total = 0.0
    n = 0
    for i in range(len(tokens) - window + 1):
        total += len(set(tokens[i:i + window])) / window
        n += 1
    return total / max(n, 1)


def mtld(tokens: List[str], threshold: float = 0.72) -> float:
    """
    MTLD (Measure of Textual Lexical Diversity) – stabilniejsze od TTR w różnych długościach tekstu.
    Implementacja heurystyczna (wystarcza do porównań w aplikacji).
    """
    if not tokens:
        return 0.0

    def mtld_pass(seq: List[str]) -> float:
        types: set = set()
        token_count = 0
        factors = 0.0

        for t in seq:
            token_count += 1
            types.add(t)
            ttr_val = len(types) / token_count
            if ttr_val <= threshold:
                factors += 1.0
                types.clear()
                token_count = 0

        # niedomknięty "faktor" – proporcjonalnie
        if token_count > 0:
            ttr_val = len(types) / token_count
            # im bliżej progu, tym większy ułamek faktora
            if ttr_val != 1.0:
                factors += (1.0 - ttr_val) / max(1e-9, (1.0 - threshold))
            else:
                factors += 0.0

        return len(seq) / max(factors, 1e-9)

    forward = mtld_pass(tokens)
    backward = mtld_pass(list(reversed(tokens)))
    return (forward + backward) / 2.0


def lexical_density(tokens: List[str], stopwords: set) -> float:
    if not tokens:
        return 0.0
    content = [t for t in tokens if t not in stopwords]
    return len(content) / max(len(tokens), 1)


def shannon_entropy(tokens: List[str]) -> Tuple[float, float]:
    """
    Zwraca (entropy, entropy_normalized):
    - entropy: standardowa entropia Shannona na słowach
    - normalized: entropy / log2(V) (0..1), gdzie V = liczba typów
    """
    if not tokens:
        return 0.0, 0.0
    freq = Counter(tokens)
    total = len(tokens)
    ent = 0.0
    for c in freq.values():
        p = c / total
        ent -= p * math.log2(p)

    V = len(freq)
    denom = math.log2(V) if V > 1 else 1.0
    ent_norm = ent / denom if denom > 0 else 0.0
    return ent, ent_norm


def hapax_ratio(tokens: List[str]) -> float:
    if not tokens:
        return 0.0
    freq = Counter(tokens)
    hapax = sum(1 for c in freq.values() if c == 1)
    V = len(freq)
    return hapax / max(V, 1)


def yules_k(tokens: List[str]) -> float:
    """
    Yule's K – klasyczna miara "koncentracji słownictwa".
    Wyższe K => bardziej powtarzalne słownictwo.
    """
    if not tokens:
        return 0.0
    freq = Counter(tokens)
    N = len(tokens)
    if N <= 1:
        return 0.0
    # sum f_i * (f_i - 1)
    s = sum(c * (c - 1) for c in freq.values())
    return 1e4 * s / (N * (N - 1))


def sentence_length_stats(sentences: List[str]) -> Tuple[float, float]:
    if not sentences:
        return 0.0, 0.0
    lengths = [len(tokenize_words(s)) for s in sentences if s.strip()]
    if not lengths:
        return 0.0, 0.0
    avg = sum(lengths) / len(lengths)
    if len(lengths) < 2:
        return avg, 0.0
    var = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    return avg, math.sqrt(var)


def top_ngrams(tokens: List[str], n: int = 2, top_k: int = 5, min_count: int = 2) -> List[Dict[str, int | str]]:
    if len(tokens) < n:
        return []
    grams = [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
    freq = Counter(grams)
    out = []
    for gram, count in freq.most_common(top_k):
        if count >= min_count:
            out.append({"ngram": " ".join(gram), "count": int(count)})
    return out


def dialogue_ratio(text: str) -> float:
    """
    Ile linii wygląda na dialog (pauza na początku linii).
    Daje fajny sygnał dla prozy dialogowej.
    """
    text = normalize_text(text)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    dlg = sum(1 for ln in lines if DIALOGUE_LINE_RE.match(ln))
    return dlg / len(lines)


# --- główna funkcja analizy ---

def analyze_stylometry(text: str, cfg: Optional[StylometryConfig] = None) -> Dict:
    cfg = cfg or StylometryConfig()
    abbreviations = cfg.abbreviations or DEFAULT_ABBREVIATIONS_PL
    stopwords = cfg.stopwords or DEFAULT_STOPWORDS_PL

    text_n = normalize_text(text)
    tokens = tokenize_words(text_n)
    sentences = split_sentences_pl(text_n, cfg)

    avg_len, std_len = sentence_length_stats(sentences)
    ent, ent_norm = shannon_entropy(tokens)

    # Kompatybilność z Twoim obecnym API/compare:
    ttr_val = mattr(tokens, cfg.mattr_window)
    lex_den = lexical_density(tokens, stopwords)
    vocab_rich = hapax_ratio(tokens)

    result = {
        # zgodne klucze:
        "ttr": round(ttr_val, 4),
        "avg_sentence_length": round(avg_len, 2),
        "sentence_length_std": round(std_len, 4),
        "lexical_density": round(lex_den, 4),
        "entropy": round(ent, 4),
        "vocab_richness": round(vocab_rich, 4),

        # meta:
        "word_count": int(len(tokens)),
        "sentence_count": int(len(sentences)),
        "unique_words": int(len(set(tokens))),

        # bardziej „literackie” dodatki:
        "entropy_norm": round(ent_norm, 4),
        "mtld": round(mtld(tokens, cfg.mtld_threshold), 3) if len(tokens) >= 50 else 0.0,
        "yules_k": round(yules_k(tokens), 3),
        "dialogue_ratio": round(dialogue_ratio(text_n), 4),

        # UI:
        "top_ngrams": top_ngrams(tokens, n=2, top_k=5, min_count=2),
    }

    # interpunkcja jako dodatkowe cechy:
    result.update(punctuation_stats(text_n))

    return result