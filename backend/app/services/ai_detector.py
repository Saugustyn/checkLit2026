"""
Moduł detekcji tekstu generowanego przez AI.

Model: sdadas/polish-gpt2-small (Polski GPT-2, ~500MB)
Metoda: Perplexity-based detection na modelu autoregresywnym (causal LM)
        uzupełniona hybrydowym sygnałem stylometrycznym.

KALIBRACJA v3:
  Korpus: 42 teksty ludzkie (Wolne Lektury, 7 autorów)
          + 38 tekstów AI (wygenerowanych przez Claude)
          n = 80
  Metoda wyznaczenia progu: ROC curve + kryterium Youdena
  Wyniki:
    AUC-ROC:   0.90
    Optymalny próg perplexity (Youden): midpoint 32.03–41.06 → 36.5

  Konwersja perplexity → prawdopodobieństwo AI:
    Sigmoida wycentrowana na progu Youdena (midpoint = 36.5).
    k=0.07 dobrane empirycznie — spłaszczone względem v2 (k=0.15),
    by unikać skrajnych wartości 97%/3% dla przypadków granicznych.

    Przykładowe wartości (k=0.07):
      ppx=20  → ~0.72  (wyraźnie AI)
      ppx=30  → ~0.60  (prawdopodobnie AI)
      ppx=37  → ~0.50  (granica decyzji)
      ppx=45  → ~0.40  (prawdopodobnie human)
      ppx=62  → ~0.26  (human)
      ppx=100 → ~0.14  (wyraźnie human)

  Wynik hybrydowy:
    Końcowe prawdopodobieństwo AI to ważona suma sygnału perplexity (70%)
    i sygnału stylometrycznego (30%). Cechy stylometryczne uwzględniane:
    MATTR, entropia Shannona, hapax legomena ratio.

ANALIZA BŁĘDÓW (korpus v3, n=80):
  Fałszywe alarmy (human → AI, 11 przypadków):
    Prosta narracja epicka, krótkie zdania, narracja 3. osoby
    bez archaizmów (Reymont, Orzeszkowa, Sienkiewicz).
  Przeoczenia (AI → human, 3 przypadki):
    Teksty AI z nieregularną, poetycką składnią.

WNIOSKI METODOLOGICZNE:
  1. Próg 36.5 skutecznie separuje większość tekstów.
  2. Sigmoida ze spłaszczonym k=0.07 daje bardziej ciągły rozkład
     prawdopodobieństwa — redukuje polaryzację 97%/3%.
  3. Sygnał hybrydowy (ppx + stylometria) poprawia precyzję
     dla tekstów granicznych.
"""

import math

_model = None
_tokenizer = None

# Progi wyznaczone metodą ROC/Youden na korpusie n=80
# Kalibracja v3, luty 2026, sdadas/polish-gpt2-small
PERPLEXITY_AI_THRESHOLD    = 32.03
PERPLEXITY_HUMAN_THRESHOLD = 41.0623

# Parametry sigmoidy (kalibracja v3)
# Midpoint = środek progu Youdena (32.03 + 41.06) / 2 ≈ 36.5
# k=0.07 — spłaszczone względem poprzedniej wersji (k=0.15),
# eliminuje polaryzację wyników do wartości granicznych 0.97/0.03
_SIGMOID_MIDPOINT = 36.5
_SIGMOID_K        = 0.07


def get_model_and_tokenizer():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM

            print("Ładowanie modelu Polish GPT-2 (sdadas/polish-gpt2-small)...")
            print("Pierwsze uruchomienie pobierze ~500MB — chwilę poczekaj.")

            _tokenizer = AutoTokenizer.from_pretrained("sdadas/polish-gpt2-small")
            _model = AutoModelForCausalLM.from_pretrained("sdadas/polish-gpt2-small")
            _model.eval()
            print("Model Polish GPT-2 załadowany!")

        except Exception as e:
            print(f"Błąd ładowania modelu Polish GPT-2: {e}")
            _model = None
            _tokenizer = None

    return _model, _tokenizer


def compute_perplexity(text: str) -> float | None:
    """
    Oblicza perplexity tekstu używając polskiego GPT-2 (causal LM).

    Niższa perplexity = model nie jest zaskoczony = styl AI.
    Wyższa perplexity = model zaskoczony = styl ludzki/literacki.
    """
    import torch

    model, tokenizer = get_model_and_tokenizer()
    if model is None or tokenizer is None:
        return None

    try:
        inputs = tokenizer(
            text[:4000],
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )
        if inputs["input_ids"].shape[1] < 10:
            return None

        with torch.no_grad():
            outputs = model(inputs["input_ids"], labels=inputs["input_ids"])

        return round(min(torch.exp(outputs.loss).item(), 1000.0), 2)

    except Exception as e:
        print(f"Błąd obliczania perplexity: {e}")
        return None


def perplexity_to_ai_probability(perplexity: float) -> float:
    """
    Konwertuje perplexity → prawdopodobieństwo AI (0.0–1.0).

    Sigmoida wycentrowana na optymalnym progu Youdena (midpoint = 36.5).
    k=0.07 dobrane empirycznie — spłaszczone względem v2 (k=0.15),
    redukuje polaryzację wyników do wartości skrajnych.

    Przy niskim perplexity (styl AI) sigmoida zbliża się do 1.0,
    przy wysokim (styl ludzki) — do 0.0. Odwrócony znak k realizuje
    ten kierunek: wyższe ppx = niższe P(AI).
    """
    ai_prob = 1.0 / (1.0 + math.exp(_SIGMOID_K * (perplexity - _SIGMOID_MIDPOINT)))
    return round(ai_prob, 4)


def compute_hybrid_probability(ppx_prob: float, stylometry: dict) -> float:
    """
    Łączy sygnał perplexity (70%) z cechami stylometrycznymi (30%).

    Cechy stylometryczne charakterystyczne dla tekstów AI:
    - niższe MATTR (bardziej powtarzalne słownictwo)
    - niższa entropia Shannona (mniejsza nieprzewidywalność rozkładu słów)
    - niższy hapax legomena ratio (mniej słów unikalnych)

    Każda cecha normalizowana jest do przedziału [0, 1],
    gdzie 1 oznacza wartość typową dla AI, 0 — dla tekstu ludzkiego.
    Sygnał stylometryczny to średnia arytmetyczna trzech znormalizowanych cech.

    Blend: 70% perplexity + 30% stylometria.
    Wagi dobrane empirycznie: perplexity jest sygnałem dominującym
    (AUC=0.90), stylometria pełni rolę korektora dla przypadków granicznych.
    """
    ttr     = stylometry.get("ttr", 0.6)
    entropy = stylometry.get("entropy", 6.0)
    hapax   = stylometry.get("vocab_richness", 0.5)

    ttr_signal     = max(0.0, min(1.0, (0.75 - ttr)     / 0.35))
    entropy_signal = max(0.0, min(1.0, (7.0  - entropy) / 4.0))
    hapax_signal   = max(0.0, min(1.0, (0.6  - hapax)   / 0.4))

    stylo_score = (ttr_signal + entropy_signal + hapax_signal) / 3.0

    hybrid = 0.70 * ppx_prob + 0.30 * stylo_score
    return round(hybrid, 4)


def detect_ai(text: str) -> dict:
    """
    Główna funkcja detekcji. Zwraca słownik z wynikami:
    - ai_probability:    końcowe prawdopodobieństwo AI (hybrydowe)
    - human_probability: 1 - ai_probability
    - ppx_probability:   surowy sygnał perplexity (do celów diagnostycznych)
    - label:             'AI-generated' lub 'Human-written'
    - confidence:        opis pewności klasyfikacji
    - perplexity:        wartość perplexity GPT-2
    """
    from app.services.stylometry import analyze_stylometry

    perplexity = compute_perplexity(text)

    if perplexity is None:
        return _fallback_detection(text)

    stylometry = analyze_stylometry(text)

    ppx_prob    = perplexity_to_ai_probability(perplexity)
    hybrid_prob = compute_hybrid_probability(ppx_prob, stylometry)
    human_prob  = round(1.0 - hybrid_prob, 4)
    in_gray     = PERPLEXITY_AI_THRESHOLD < perplexity < PERPLEXITY_HUMAN_THRESHOLD

    return {
        "ai_probability":    hybrid_prob,
        "human_probability": human_prob,
        "ppx_probability":   ppx_prob,
        "label":             "AI-generated" if hybrid_prob > 0.5 else "Human-written",
        "confidence":        _confidence_label(max(hybrid_prob, human_prob), in_gray),
        "perplexity":        perplexity,
    }


def _confidence_label(score: float, in_gray: bool) -> str:
    if in_gray:
        return "Niska (strefa szara – wynik niepewny)"
    if score >= 0.75:
        return "Wysoka"
    elif score >= 0.60:
        return "Średnia"
    else:
        return "Niska"


def _fallback_detection(text: str) -> dict:
    indicators = [
        "ponadto", "należy zauważyć", "warto podkreślić",
        "w podsumowaniu", "reasumując", "additionally",
        "furthermore", "in conclusion"
    ]
    matches = sum(1 for i in indicators if i in text.lower())
    ai_prob = min(0.5 + matches * 0.1, 0.90)

    return {
        "ai_probability":    round(ai_prob, 4),
        "human_probability": round(1.0 - ai_prob, 4),
        "ppx_probability":   None,
        "label":             "AI-generated" if ai_prob > 0.5 else "Human-written",
        "confidence":        "Niska (tryb heurystyczny – model niedostępny)",
        "perplexity":        None,
    }