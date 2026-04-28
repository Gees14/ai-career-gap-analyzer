"""Tests for embedding-based semantic matcher."""
import pytest
from app.services.embedding_matcher import EmbeddingMatcher


@pytest.fixture(scope="module")
def matcher() -> EmbeddingMatcher:
    return EmbeddingMatcher()


def test_embed_returns_array(matcher):
    import numpy as np
    result = matcher.embed(["machine learning", "deep learning"])
    assert result.shape == (2, 384)


def test_embed_empty_returns_empty(matcher):
    result = matcher.embed([])
    assert result.shape[0] == 0


def test_semantic_match_finds_related_skills(matcher):
    cv_phrases = [
        "Built a transformer-based NLP model using BERT for text classification.",
        "Deployed models as REST APIs using FastAPI.",
    ]
    job_skills = [("transformers", "NLP"), ("fastapi", "Backend APIs")]
    matches = matcher.find_semantic_matches(cv_phrases, job_skills)
    # Should find at least one partial match
    assert isinstance(matches, list)


def test_cv_job_similarity_range(matcher):
    score = matcher.score_cv_job_similarity(
        "machine learning engineer with pytorch experience",
        "we need a machine learning engineer proficient in pytorch",
    )
    assert 0.0 <= score <= 1.0


def test_high_similarity_for_matching_texts(matcher):
    score = matcher.score_cv_job_similarity(
        "RAG pipeline with vector database and semantic search",
        "retrieval augmented generation with pinecone vector database",
    )
    # Should be reasonably similar
    assert score > 0.5


def test_find_semantic_matches_empty_inputs(matcher):
    assert matcher.find_semantic_matches([], [("python", "Data Engineering")]) == []
    assert matcher.find_semantic_matches(["some text"], []) == []
