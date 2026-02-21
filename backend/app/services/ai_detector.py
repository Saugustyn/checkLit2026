"""
Moduł detekcji tekstu generowanego przez AI.

Model: sdadas/polish-gpt2-small (Polski GPT-2, ~500MB)
Metoda: Perplexity-based detection na modelu autoregresywnym (causal LM)

KALIBRACJA v2 (luty 2026):
  Korpus: 25 tekstów ludzkich (wyłącznie Wolne Lektury, 7 autorów)
          + 25 tekstów AI (wygenerowanych przez Claude)
          n = 50
  Metoda wyznaczenia progu: ROC curve + kryterium Youdena
  Wyniki:
    AUC-ROC:   0.9376
    Accuracy:  0.90   (90%)
    Precision: 0.8846
    Recall:    0.9200
    F1:        0.9020
    Optymalny próg perplexity: 37.043

  POPRAWA vs v1 (AUC 0.79 → 0.94):
    Przyczyną poprawy było usunięcie z klasy 'human' tekstów
    wygenerowanych przez model AI (błąd konstrukcji korpusu v1).
    Klasa 'human' składa się teraz wyłącznie z tekstów z domeny
    publicznej pobranych z wolnelektury.pl.

ANALIZA BŁĘDÓW (5 z 50):
  Fałszywe alarmy (human → AI, 3 przypadki):
    - Prus, Lalka t.2: Wokulski w pociągu          ppx=28.26
    - Sienkiewicz, Potop t.2: Soroka i Kmicic       ppx=36.46
    - Reymont, Chłopi, Jesień: Boryna na miedzy     ppx=29.19
    Wzorzec: krótkie, narracyjne zdania, proste słownictwo,
    narracja 3. osoby bez archaizmów → niska perplexity.

  Przeoczenia (AI → human, 2 przypadki):
    ppx=47.35 i ppx=37.04 — teksty AI z nieregularną składnią,
    emocjonalnymi wtraceniami i złożonymi zdaniami.
    Wzorzec: jeśli AI naśladuje "ludzki" styl nieregularnych
    zdań, perplexity rośnie ponad próg.

WNIOSKI METODOLOGICZNE (do sekcji 4.3 pracy):
  1. Próg 37.04 skutecznie separuje większość tekstów.
  2. Metoda zawodzi na tekstach narracyjnych z prostą składnią
     (Potop, Chłopi) — styl historyczno-epickich narracji
     przypomina modelowi styl AI.
  3. Recall 0.92 > Precision 0.88 — zgodne z priorytetem:
     lepiej fałszywy alarm niż przeoczenie tekstu AI.
  4. AUC 0.94 mieści się w przedziale "doskonała dyskryminacja"
     (>0.90 wg klasyfikacji Hosmer & Lemeshow, 2000).
"""

_model = None
_tokenizer = None

# Progi wyznaczone metodą ROC/Youden na korpusie n=50
# Kalibracja v2, luty 2026, sdadas/polish-gpt2-small
PERPLEXITY_AI_THRESHOLD    = 32.03
PERPLEXITY_HUMAN_THRESHOLD = 41.0623


def get_model_and_tokenizer():
    """Lazy loading polskiego GPT-2. Ładowany raz, cache w pamięci procesu."""
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

    Strefy (skalibrowane metodą ROC/Youden na korpusie n=50):
      < 28.89  → AI z wysoką pewnością      (ai_prob 0.85–0.97)
      28.89–37.04 → strefa szara            (interpolacja liniowa)
      > 37.04  → human z wysoką pewnością   (ai_prob 0.03–0.15)
    """
    if perplexity <= PERPLEXITY_AI_THRESHOLD:
        ai_prob = 0.85 + (PERPLEXITY_AI_THRESHOLD - perplexity) / (PERPLEXITY_AI_THRESHOLD * 5)
        return round(min(0.97, ai_prob), 4)

    elif perplexity >= PERPLEXITY_HUMAN_THRESHOLD:
        ai_prob = 0.15 - (perplexity - PERPLEXITY_HUMAN_THRESHOLD) / (PERPLEXITY_HUMAN_THRESHOLD * 5)
        return round(max(0.03, ai_prob), 4)

    else:
        # Strefa szara: interpolacja liniowa między 0.85 a 0.15
        ratio = (perplexity - PERPLEXITY_AI_THRESHOLD) / (PERPLEXITY_HUMAN_THRESHOLD - PERPLEXITY_AI_THRESHOLD)
        return round(0.85 - ratio * 0.70, 4)


def detect_ai(text: str) -> dict:
    """Główna funkcja detekcji AI w tekście literackim."""
    perplexity = compute_perplexity(text)

    if perplexity is None:
        return _fallback_detection(text)

    ai_prob    = perplexity_to_ai_probability(perplexity)
    human_prob = round(1.0 - ai_prob, 4)
    in_gray    = PERPLEXITY_AI_THRESHOLD < perplexity < PERPLEXITY_HUMAN_THRESHOLD

    return {
        "ai_probability":    ai_prob,
        "human_probability": human_prob,
        "label":             "AI-generated" if ai_prob > 0.5 else "Human-written",
        "confidence":        _confidence_label(max(ai_prob, human_prob), in_gray),
        "perplexity":        perplexity,
    }


def _confidence_label(score: float, in_gray: bool) -> str:
    """Etykieta pewności klasyfikacji."""
    if in_gray:
        return "Niska (strefa szara – wynik niepewny)"
    if score >= 0.80:
        return "Wysoka"
    elif score >= 0.65:
        return "Średnia"
    else:
        return "Niska"


def _fallback_detection(text: str) -> dict:
    """Prosta heurystyka gdy model niedostępny (fallback)."""
    indicators = [
        "ponadto", "należy zauważyć", "warto podkreślić",
        "w podsumowaniu", "reasumując", "additionally",
        "furthermore", "in conclusion"
    ]
    matches  = sum(1 for i in indicators if i in text.lower())
    ai_prob  = min(0.5 + matches * 0.1, 0.90)

    return {
        "ai_probability":    round(ai_prob, 4),
        "human_probability": round(1.0 - ai_prob, 4),
        "label":             "AI-generated" if ai_prob > 0.5 else "Human-written",
        "confidence":        "Niska (tryb heurystyczny – model niedostępny)",
        "perplexity":        None,
    }