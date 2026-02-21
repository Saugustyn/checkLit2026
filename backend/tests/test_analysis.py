"""
Testy jednostkowe modułów analizy.
Uruchomienie: pytest tests/ -v
"""
import pytest
from app.services.stylometry import (
    tokenize, calculate_ttr, calculate_entropy,
    analyze_stylometry
)
from app.services.nlp_service import (
    calculate_flesch, calculate_avg_word_length,
    analyze_quality
)


# ===== TESTY STYLOMETRII =====

class TestTokenize:
    def test_basic_tokenization(self):
        tokens = tokenize("Hello world! This is a test.")
        assert "hello" in tokens
        assert "world" in tokens

    def test_removes_punctuation(self):
        tokens = tokenize("Hello, world!")
        assert "hello" in tokens
        assert "," not in tokens

    def test_empty_text(self):
        assert tokenize("") == []


class TestTTR:
    def test_all_unique(self):
        tokens = ["cat", "dog", "bird"]
        assert calculate_ttr(tokens) == 1.0

    def test_all_same(self):
        tokens = ["cat", "cat", "cat"]
        assert calculate_ttr(tokens) == pytest.approx(1/3, abs=0.001)

    def test_empty(self):
        assert calculate_ttr([]) == 0.0


class TestEntropy:
    def test_uniform_distribution_high_entropy(self):
        tokens = ["a", "b", "c", "d", "e"]
        entropy = calculate_entropy(tokens)
        assert entropy > 2.0

    def test_single_word_zero_entropy(self):
        tokens = ["word"] * 10
        assert calculate_entropy(tokens) == 0.0

    def test_empty(self):
        assert calculate_entropy([]) == 0.0


class TestAnalyzeStylometry:
    def test_returns_all_keys(self):
        text = "This is a sample text. It has multiple sentences. We test it now."
        result = analyze_stylometry(text)
        expected_keys = ["ttr", "avg_sentence_length", "lexical_density",
                         "entropy", "vocab_richness", "word_count",
                         "sentence_count", "unique_words", "top_ngrams"]
        for key in expected_keys:
            assert key in result, f"Brak klucza: {key}"

    def test_word_count(self):
        text = "one two three four five"
        result = analyze_stylometry(text)
        assert result["word_count"] == 5


# ===== TESTY JAKOŚCI JĘZYKOWEJ =====

class TestFlesch:
    def test_simple_text_high_score(self):
        text = "The cat sat. It is big. A dog ran."
        score = calculate_flesch(text)
        assert score > 50  # Prosty tekst = wysoki wynik

    def test_score_in_range(self):
        text = "This is a moderately complex sentence with several clauses."
        score = calculate_flesch(text)
        assert 0 <= score <= 100

    def test_empty_text(self):
        assert calculate_flesch("") == 0.0


class TestAnalyzeQuality:
    def test_returns_all_keys(self):
        text = "Sample text for quality analysis. It should work fine."
        result = analyze_quality(text)
        assert "flesch_score" in result
        assert "flesch_label" in result
        assert "avg_word_length" in result
        assert "punctuation_density" in result

    def test_flesch_label_type(self):
        text = "The quick brown fox jumps over the lazy dog."
        result = analyze_quality(text)
        assert isinstance(result["flesch_label"], str)


# ===== TESTY INTEGRACYJNE API =====

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIEndpoints:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_analyze_valid_text(self):
        text = "This is a sufficiently long text for analysis. " * 5
        response = client.post("/api/analyze", json={"text": text})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "ai_detection" in data
        assert "stylometry" in data
        assert "quality" in data

    def test_analyze_too_short_text(self):
        response = client.post("/api/analyze", json={"text": "Too short"})
        assert response.status_code == 400

    def test_get_history(self):
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_compare_texts(self):
        text_a = "The quick brown fox jumps over the lazy dog. " * 3
        text_b = "A completely different text with other vocabulary. " * 3
        response = client.post("/api/compare", json={
            "text_a": text_a,
            "text_b": text_b
        })
        assert response.status_code == 200
        data = response.json()
        assert "similarity_score" in data
        assert 0.0 <= data["similarity_score"] <= 1.0
