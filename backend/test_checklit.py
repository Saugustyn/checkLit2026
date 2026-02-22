"""
checkLit – Testy jednostkowe i integracyjne (pytest) - POPRAWIONE
==================================================================
Uruchomienie:
    cd C:\\Users\\sebas\\Documents\\checkLit\\backend
    venv\\Scripts\\activate
    pytest test_checklit.py -v
"""

import io
import math
import pytest
from unittest.mock import patch


# ══════════════════════════════════════════════════════════════════
# 1. STYLOMETRIA – testy jednostkowe
# ══════════════════════════════════════════════════════════════════

from app.services.stylometry import (
    tokenize,
    get_sentences,
    calculate_ttr,
    calculate_lexical_density,
    calculate_entropy,
    calculate_vocab_richness,
    get_top_ngrams,
    analyze_stylometry,
)

# ── tokenize ──────────────────────────────────────────────────────

class TestTokenize:
    def test_basic(self):
        assert tokenize("Ala ma kota.") == ["ala", "ma", "kota"]

    def test_lowercase(self):
        tokens = tokenize("Warszawa Kraków Gdańsk")
        assert all(t == t.lower() for t in tokens)

    def test_strips_punctuation(self):
        tokens = tokenize("Witaj, świecie! Jak się masz?")
        assert "," not in tokens
        assert "!" not in tokens
        assert "?" not in tokens

    def test_empty_string(self):
        assert tokenize("") == []

    def test_only_punctuation(self):
        assert tokenize("... !!! ???") == []

    def test_numbers_kept(self):
        tokens = tokenize("rok 1978 był ważny")
        assert "1978" in tokens

    def test_polish_chars(self):
        tokens = tokenize("Żółta żaba źle się czuła")
        assert "żółta" in tokens
        assert "źle" in tokens


# ── get_sentences ─────────────────────────────────────────────────

class TestGetSentences:
    def test_period(self):
        s = get_sentences("Pierwsze zdanie. Drugie zdanie.")
        assert len(s) == 2

    def test_exclamation(self):
        s = get_sentences("Brawo! Tak trzymaj!")
        assert len(s) == 2

    def test_question(self):
        s = get_sentences("Jak masz na imię? Odpowiedz.")
        assert len(s) == 2

    def test_empty(self):
        assert get_sentences("") == []

    def test_no_punctuation(self):
        s = get_sentences("To jest zdanie bez kropki")
        assert len(s) == 1

    def test_multiple_terminators(self):
        s = get_sentences("Czekał... i czekał.")
        assert len(s) <= 2


# ── calculate_ttr (MATTR) ─────────────────────────────────────────

class TestCalculateTTR:
    def test_empty(self):
        assert calculate_ttr([]) == 0.0

    def test_all_unique(self):
        tokens = ["a", "b", "c", "d", "e"]
        assert calculate_ttr(tokens) == 1.0

    def test_all_same(self):
        tokens = ["słowo"] * 20
        assert calculate_ttr(tokens) == pytest.approx(1 / 20, abs=0.01)

    def test_range(self):
        tokens = "ala ma kota i psa i rybki i chomika i konia".split()
        ttr = calculate_ttr(tokens)
        assert 0.0 <= ttr <= 1.0

    def test_short_text_fallback(self):
        tokens = ["a", "b", "c"]
        result = calculate_ttr(tokens, window=50)
        assert result == pytest.approx(1.0)

    def test_mattr_more_stable_than_raw(self):
        base = "Tomasz szedł przez las i widział drzewa i słyszał ptaki".split()
        long_tokens = base * 10
        
        raw_ttr_short = len(set(base)) / len(base)
        raw_ttr_long  = len(set(long_tokens)) / len(long_tokens)
        raw_diff = abs(raw_ttr_short - raw_ttr_long)
        
        mattr_short = calculate_ttr(base)
        mattr_long  = calculate_ttr(long_tokens)
        mattr_diff = abs(mattr_short - mattr_long)
        
        assert mattr_diff < raw_diff 


# ── calculate_lexical_density ─────────────────────────────────────

class TestLexicalDensity:
    def test_empty(self):
        assert calculate_lexical_density([], "") == 0.0

    def test_all_stopwords(self):
        tokens = ["i", "w", "z", "na", "do"]
        result = calculate_lexical_density(tokens, " ".join(tokens))
        assert result == 0.0

    def test_no_stopwords(self):
        tokens = ["Wisła", "płynie", "spokojnie", "przez", "kraj"]
        result = calculate_lexical_density(tokens, " ".join(tokens))
        assert result > 0.5

    def test_range(self):
        tokens = tokenize("Piotr i Paweł szli przez las i rozmawiali o życiu")
        result = calculate_lexical_density(tokens, "")
        assert 0.0 <= result <= 1.0

    def test_different_from_ttr(self):
        tokens = tokenize("ala ma kota i psa i rybkę i chomika")
        ttr = calculate_ttr(tokens)
        ld  = calculate_lexical_density(tokens, "")
        assert ttr != ld


# ── calculate_entropy ─────────────────────────────────────────────

class TestEntropy:
    def test_empty(self):
        assert calculate_entropy([]) == 0.0

    def test_all_same_zero(self):
        assert calculate_entropy(["słowo"] * 10) == 0.0

    def test_all_unique_max(self):
        tokens = ["a", "b", "c", "d"]
        expected = math.log2(4)
        assert calculate_entropy(tokens) == pytest.approx(expected, abs=0.001)

    def test_real_text(self):
        text = "Petroniusz obudził się późno i jak zwykle był zmęczony"
        tokens = tokenize(text)
        entropy = calculate_entropy(tokens)
        assert entropy > 2.0

    def test_ai_text_lower_entropy(self):
        ai = tokenize("system jest dobry system działa dobrze system " * 5)
        hu = tokenize("Petroniusz szedł przez Rzym szukając cienia "
                      "i chwili spokoju wśród rozgrzanych murów " * 5)
        assert calculate_entropy(hu) >= calculate_entropy(ai)


# ── calculate_vocab_richness ──────────────────────────────────────

class TestVocabRichness:
    def test_empty(self):
        assert calculate_vocab_richness([]) == 0.0

    def test_all_hapax(self):
        tokens = ["alpha", "beta", "gamma", "delta"]
        assert calculate_vocab_richness(tokens) == 1.0

    def test_no_hapax(self):
        tokens = ["ala", "ala", "ma", "ma"]
        assert calculate_vocab_richness(tokens) == 0.0

    def test_range(self):
        tokens = tokenize("ala ma kota i kota i psa i psa i rybkę")
        r = calculate_vocab_richness(tokens)
        assert 0.0 <= r <= 1.0


# ── get_top_ngrams ────────────────────────────────────────────────

class TestGetTopNgrams:
    def test_empty(self):
        assert get_top_ngrams([]) == []

    def test_too_short(self):
        assert get_top_ngrams(["jedno"], n=2) == []

    def test_no_repeats_returns_empty(self):
        tokens = ["a", "b", "c", "d", "e"]
        result = get_top_ngrams(tokens)
        assert result == []

    def test_repeated_bigram(self):
        tokens = ["ala", "ma", "kota", "ala", "ma", "psa"]
        result = get_top_ngrams(tokens)
        ngram_strings = [r["ngram"] for r in result]
        assert "ala ma" in ngram_strings

    def test_count_correct(self):
        tokens = ["a", "b", "a", "b", "a", "b"]
        result = get_top_ngrams(tokens, n=2, top_k=1)
        assert result[0]["count"] == 3

    def test_top_k_respected(self):
        tokens = "a b a b c d c d e f e f".split()
        result = get_top_ngrams(tokens, n=2, top_k=2)
        assert len(result) <= 2

    def test_trigrams(self):
        tokens = "a b c a b c a b c".split()
        result = get_top_ngrams(tokens, n=3, top_k=3)
        assert result[0]["ngram"] == "a b c"
        assert result[0]["count"] == 3


# ── analyze_stylometry (integracyjny) ────────────────────────────

class TestAnalyzeStylometry:
    TEXT = (
        "Petroniusz obudził się zaledwie koło południa i jak zwykle "
        "był zmęczony. Poprzedniego dnia był na uczcie u Nerona, która "
        "przeciągnęła się do późna w noc. Sam mówił, że rankami budzi "
        "się jakby zdrętwiały i bez możności zebrania myśli."
    )

    def test_returns_all_keys(self):
        result = analyze_stylometry(self.TEXT)
        expected_keys = {
            "ttr", "avg_sentence_length", "lexical_density",
            "entropy", "vocab_richness", "word_count",
            "sentence_count", "unique_words", "top_ngrams"
        }
        assert expected_keys.issubset(result.keys())

    def test_word_count_positive(self):
        assert analyze_stylometry(self.TEXT)["word_count"] > 0

    def test_sentence_count_positive(self):
        assert analyze_stylometry(self.TEXT)["sentence_count"] > 0

    def test_ttr_differs_from_lexical_density(self):
        r = analyze_stylometry(self.TEXT)
        assert r["ttr"] != r["lexical_density"]

    def test_unique_words_le_word_count(self):
        r = analyze_stylometry(self.TEXT)
        assert r["unique_words"] <= r["word_count"]

    def test_entropy_positive(self):
        assert analyze_stylometry(self.TEXT)["entropy"] > 0

    def test_short_text(self):
        result = analyze_stylometry("Krótki tekst.")
        assert result["word_count"] >= 0

    def test_empty_text(self):
        result = analyze_stylometry("")
        assert result["word_count"] == 0
        assert result["ttr"] == 0.0


# ══════════════════════════════════════════════════════════════════
# 2. FILE PARSER – testy jednostkowe
# ══════════════════════════════════════════════════════════════════

from app.services.file_parser import extract_text, clean_text

class TestCleanText:
    def test_removes_hyphen_linebreak(self):
        assert clean_text("przy-\nkład") == "przykład"

    def test_normalizes_whitespace(self):
        result = clean_text("słowo   drugie\t\ttrzecie")
        assert "   " not in result.replace("\t", " ")

    def test_removes_control_chars(self):
        text = "normalny\x00tekst\x1f"
        result = clean_text(text)
        assert "\x00" not in result
        assert "\x1f" not in result

    def test_empty(self):
        assert clean_text("") == ""


class TestExtractText:
    def test_unsupported_extension(self):
        with pytest.raises(ValueError, match="Nieobsługiwany"):
            extract_text("plik.xyz", b"data")

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="krótki"):
            extract_text("plik.txt", "za".encode("utf-8"))


# ══════════════════════════════════════════════════════════════════
# 3. AI DETECTOR – testy jednostkowe (model mockowany)
# ══════════════════════════════════════════════════════════════════

from app.services.ai_detector import (
    perplexity_to_ai_probability,
    detect_ai,
    PERPLEXITY_AI_THRESHOLD,
    PERPLEXITY_HUMAN_THRESHOLD,
)

class TestPerplexityToAiProbability:
    def test_very_low_perplexity_is_ai(self):
        prob = perplexity_to_ai_probability(10.0)
        assert prob > 0.85

    def test_very_high_perplexity_is_human(self):
        prob = perplexity_to_ai_probability(80.0)
        assert prob < 0.15

    def test_at_ai_threshold(self):
        prob = perplexity_to_ai_probability(PERPLEXITY_AI_THRESHOLD)
        assert prob > 0.5

    def test_at_human_threshold(self):
        prob = perplexity_to_ai_probability(PERPLEXITY_HUMAN_THRESHOLD)
        assert prob < 0.5 

    def test_gray_zone(self):
        mid = (PERPLEXITY_AI_THRESHOLD + PERPLEXITY_HUMAN_THRESHOLD) / 2
        prob = perplexity_to_ai_probability(mid)
        assert 0.15 < prob < 0.85

    def test_probability_range(self):
        for ppx in [5, 15, 25, 33, 40, 60, 100]:
            p = perplexity_to_ai_probability(ppx)
            assert 0.0 <= p <= 1.0


class TestDetectAi:
    def test_low_perplexity_returns_ai(self):
        with patch("app.services.ai_detector.compute_perplexity", return_value=15.0):
            result = detect_ai("jakiś tekst")
        assert result["label"] == "AI-generated"
        assert result["ai_probability"] > 0.5

    def test_high_perplexity_returns_human(self):
        with patch("app.services.ai_detector.compute_perplexity", return_value=75.0):
            result = detect_ai("jakiś tekst")
        assert result["label"] == "Human-written"
        assert result["human_probability"] > 0.5

    def test_gray_zone_low_confidence(self):
        mid = (PERPLEXITY_AI_THRESHOLD + PERPLEXITY_HUMAN_THRESHOLD) / 2
        with patch("app.services.ai_detector.compute_perplexity", return_value=mid):
            result = detect_ai("jakiś tekst")
        assert "strefa szara" in result["confidence"].lower()

    def test_model_unavailable_fallback(self):
        with patch("app.services.ai_detector.compute_perplexity", return_value=None):
            result = detect_ai("tekst do analizy")
        assert "ai_probability" in result
        assert "heurystyczny" in result["confidence"].lower()

    def test_result_keys(self):
        with patch("app.services.ai_detector.compute_perplexity", return_value=25.0):
            result = detect_ai("tekst")
        assert {"ai_probability", "human_probability", "label",
                "confidence", "perplexity"}.issubset(result.keys())

    def test_probabilities_sum_to_one(self):
        with patch("app.services.ai_detector.compute_perplexity", return_value=30.0):
            result = detect_ai("tekst")
        total = result["ai_probability"] + result["human_probability"]
        assert total == pytest.approx(1.0, abs=0.01)


# ══════════════════════════════════════════════════════════════════
# 4. API – testy integracyjne (FastAPI TestClient)
# ══════════════════════════════════════════════════════════════════

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(autouse=True)
def mock_perplexity():
    with patch("app.services.ai_detector.compute_perplexity", return_value=25.0):
        yield

client = TestClient(app)

SAMPLE_TEXT = (
    "Petroniusz obudził się zaledwie koło południa i jak zwykle był bardzo zmęczony. "
    "Poprzedniego dnia był na uczcie u Nerona, która przeciągnęła się do późna w noc. "
    "Sam mówił, że rankami budzi się jakby zdrętwiały i bez możności zebrania myśli. "
    "Ale poranna kąpiel i staranne wygniatanie ciała przez wprawionych do tego niewolników "
    "przyśpieszało stopniowo obieg jego leniwej krwi i cuciło go."
)

class TestAnalyzeEndpoint:
    def test_status_200(self):
        r = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        assert r.status_code == 200

    def test_response_has_required_fields(self):
        r = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        body = r.json()
        assert "id" in body
        assert "ai_detection" in body
        assert "stylometry" in body

    def test_ai_detection_fields(self):
        r = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        ai = r.json()["ai_detection"]
        assert "ai_probability" in ai
        assert "human_probability" in ai
        assert "label" in ai
        assert "confidence" in ai

    def test_stylometry_fields(self):
        r = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        sty = r.json()["stylometry"]
        for key in ["ttr", "word_count", "sentence_count", "unique_words",
                    "lexical_density", "entropy", "vocab_richness"]:
            assert key in sty, f"Brak klucza: {key}"

    def test_text_too_short_returns_error(self):
        r = client.post("/api/analyze", json={"text": "za krótko"})
        assert r.status_code in (400, 422)

    def test_empty_text_returns_error(self):
        r = client.post("/api/analyze", json={"text": ""})
        assert r.status_code in (400, 422)

    def test_missing_text_field_returns_422(self):
        r = client.post("/api/analyze", json={})
        assert r.status_code == 422


class TestAnalyzeFileEndpoint:
    def test_txt_upload(self):
        content = (SAMPLE_TEXT * 3).encode("utf-8")
        r = client.post(
            "/api/analyze-file",
            files={"file": ("test.txt", content, "text/plain")}
        )
        assert r.status_code == 200

    def test_unsupported_format_returns_400(self):
        r = client.post(
            "/api/analyze-file",
            files={"file": ("test.doc", b"tresc", "application/msword")}
        )
        assert r.status_code in (400, 422)

    def test_response_same_structure_as_analyze(self):
        content = (SAMPLE_TEXT * 3).encode("utf-8")
        r = client.post(
            "/api/analyze-file",
            files={"file": ("test.txt", content, "text/plain")}
        )
        body = r.json()
        assert "ai_detection" in body
        assert "stylometry" in body


class TestHistoryEndpoint:
    def test_history_returns_list(self):
        client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        r = client.get("/api/history")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_history_item_has_id(self):
        client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        items = client.get("/api/history").json()
        assert len(items) > 0
        assert "id" in items[0]


class TestResultsEndpoint:
    def test_get_existing_result(self):
        create = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        analysis_id = create.json()["id"]
        r = client.get(f"/api/results/{analysis_id}")
        assert r.status_code == 200
        assert r.json()["id"] == analysis_id

    def test_get_nonexistent_returns_404(self):
        r = client.get("/api/results/999999")
        assert r.status_code == 404


class TestDeleteEndpoint:
    def test_delete_existing(self):
        create = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        analysis_id = create.json()["id"]
        r = client.delete(f"/api/history/{analysis_id}")
        assert r.status_code in (200, 204)

    def test_deleted_not_in_history(self):
        create = client.post("/api/analyze", json={"text": SAMPLE_TEXT})
        analysis_id = create.json()["id"]
        client.delete(f"/api/history/{analysis_id}")
        r = client.get(f"/api/results/{analysis_id}")
        assert r.status_code == 404

    def test_delete_nonexistent_returns_404(self):
        r = client.delete("/api/history/999999")
        assert r.status_code == 404


class TestCompareEndpoint:
    def test_compare_two_texts(self):
        r = client.post("/api/compare", json={
            "text_a": SAMPLE_TEXT,
            "text_b": SAMPLE_TEXT + " Dodatkowe zdanie na końcu tekstu."
        })
        assert r.status_code == 200

    def test_compare_response_has_both_results(self):
        r = client.post("/api/compare", json={
            "text_a": SAMPLE_TEXT,
            "text_b": SAMPLE_TEXT + " Inne zakończenie."
        })
        body = r.json()
        assert len(body) >= 2 or "analysis_a" in body or "result_a" in body

    def test_compare_missing_field_returns_422(self):
        r = client.post("/api/compare", json={"text_a": SAMPLE_TEXT})
        assert r.status_code == 422