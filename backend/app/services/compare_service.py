import math
import sys

# Zakresy wyznaczone empirycznie na zbiorze 12 tekstów testowych
# (evaluate_checklit.py, luty 2026). Zakres = [5. percentyl, 95. percentyl]
# obserwowanych wartości — im węższy zakres, tym bardziej wrażliwa metryka.
FEATURE_RANGES = {
    "ttr":                  (0.82, 0.96),  # obs: 0.842–0.943
    "avg_sentence_length":  (6.0,  32.0),  # obs: ~8–28 słów/zdanie
    "sentence_length_std":  (1.5,  18.0),  # obs: AI~4-6, human~8-14
    "lexical_density":      (0.54, 0.80),  # obs: 0.562–0.788
    "entropy":              (6.50,  7.50), # obs: 6.68–7.29 (BYŁO 5.5–9.0 = za szerokie!)
    "vocab_richness":       (0.78, 0.95),  # obs: 0.820–0.943
}

# Wagi oparte na d-prime z ewaluacji (wyższy d' = lepsza separacja stylów)
# d-prime: sentence_length_std=1.83, avg_sentence_length=0.93
# Poprzednia wersja miała to odwrócone (avg_sl=0.30, std=0.22)
FEATURE_WEIGHTS = {
    "sentence_length_std":  0.30,  # d'=1.83 — najlepszy separator (BYŁO 0.22)
    "avg_sentence_length":  0.20,  # d'=0.93 — umiarkowany    (BYŁO 0.30)
    "ttr":                  0.18,  # d'=2.10 — dobry
    "lexical_density":      0.16,  # d'=2.28 — dobry
    "entropy":              0.10,  # d'=0.20 — słaby, ale szeroki zakres już naprawiony
    "vocab_richness":       0.06,  # d'=2.48 — dobry, ale zbyt zbliżony dla obu klas
}

print(
    f"[compare_service v4] loaded | "
    f"entropy range: {FEATURE_RANGES['entropy']} | "
    f"std weight: {FEATURE_WEIGHTS['sentence_length_std']}",
    file=sys.stderr, flush=True,
)


def compute_stylometric_similarity(stylo_a: dict, stylo_b: dict) -> dict:
    diffs = []
    breakdown = {}

    for feature, (lo, hi) in FEATURE_RANGES.items():
        val_a = stylo_a.get(feature, 0.0)
        val_b = stylo_b.get(feature, 0.0)

        norm_a = max(0.0, min(1.0, (val_a - lo) / (hi - lo)))
        norm_b = max(0.0, min(1.0, (val_b - lo) / (hi - lo)))

        diff = FEATURE_WEIGHTS[feature] * abs(norm_a - norm_b)
        diffs.append(diff)
        breakdown[feature] = round(abs(norm_a - norm_b), 4)

    distance = math.sqrt(sum(d ** 2 for d in diffs))
    max_distance = math.sqrt(sum(w ** 2 for w in FEATURE_WEIGHTS.values()))
    similarity = round(max(0.0, min(1.0, 1.0 - (distance / max_distance))), 4)

    return {
        "similarity": similarity,
        "distance":   round(distance, 4),
        "breakdown":  breakdown,
    }