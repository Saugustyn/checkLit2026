import math
import sys

FEATURE_RANGES = {
    "ttr":                  (0.50, 0.95),
    "avg_sentence_length":  (4.0,  55.0),
    "sentence_length_std":  (1.0,  22.0),
    "lexical_density":      (0.45, 0.85),
    "entropy":              (5.5,   9.0),
    "vocab_richness":       (0.30, 0.92),
}

FEATURE_WEIGHTS = {
    "ttr":                  0.16,
    "avg_sentence_length":  0.30,
    "sentence_length_std":  0.22,
    "lexical_density":      0.14,
    "entropy":              0.10,
    "vocab_richness":       0.08,
}

print(
    f"[compare_service v3] loaded | avg_sl range: {FEATURE_RANGES['avg_sentence_length']}",
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