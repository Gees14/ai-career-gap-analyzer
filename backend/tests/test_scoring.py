"""Tests for scoring engine — reproducibility and correctness."""
import pytest

sentence_transformers = pytest.importorskip(
    "sentence_transformers", reason="sentence-transformers not installed"
)

from app.services.skill_extractor import SkillExtractor
from app.services.embedding_matcher import EmbeddingMatcher
from app.services.scoring import ScoringEngine
from tests.conftest import SAMPLE_CV, AI_JOB, ML_JOB, MINIMAL_CV


@pytest.fixture(scope="module")
def engine() -> ScoringEngine:
    return ScoringEngine(SkillExtractor(), EmbeddingMatcher())


def test_score_returns_valid_range(engine):
    result = engine.score(SAMPLE_CV, [AI_JOB])
    assert 0 <= result.fit_score <= 100


def test_score_is_reproducible(engine):
    r1 = engine.score(SAMPLE_CV, [AI_JOB])
    r2 = engine.score(SAMPLE_CV, [AI_JOB])
    assert r1.fit_score == r2.fit_score


def test_strong_match_present_for_known_overlap(engine):
    result = engine.score(SAMPLE_CV, [AI_JOB])
    strong_names = {m.skill for m in result.strong_matches}
    # CV and AI job both mention fastapi and rag
    assert len(strong_names) > 0


def test_missing_skills_detected(engine):
    # MINIMAL_CV intentionally lacks kubernetes, llm fine-tuning, etc.
    result = engine.score(MINIMAL_CV, [AI_JOB])
    assert len(result.missing_required_skills) > 0


def test_category_scores_populated(engine):
    result = engine.score(SAMPLE_CV, [AI_JOB])
    assert isinstance(result.category_scores, dict)
    assert len(result.category_scores) > 0


def test_explanation_is_string(engine):
    result = engine.score(SAMPLE_CV, [AI_JOB])
    assert isinstance(result.explanation, str)
    assert len(result.explanation) > 20


def test_better_cv_scores_higher(engine):
    """A CV that matches the job well should score higher than a minimal one."""
    score_good = engine.score(SAMPLE_CV, [AI_JOB]).fit_score
    score_weak = engine.score(
        "I am a junior developer with no ML experience.", [AI_JOB]
    ).fit_score
    assert score_good > score_weak


def test_two_job_descriptions(engine):
    result = engine.score(SAMPLE_CV, [AI_JOB, ML_JOB])
    assert 0 <= result.fit_score <= 100


def test_missing_skills_for_ai_engineer_job(engine):
    """Verify specific missing skills for a candidate without GenAI experience."""
    cv_no_genai = """
    Technical Skills
    Python, scikit-learn, PyTorch, SQL, pandas, Docker, Git

    Experience
    Data Scientist — built ML models for regression and classification.
    Used scikit-learn and PyTorch for model training and evaluation.
    """
    result = engine.score(cv_no_genai, [AI_JOB])
    missing = set(result.missing_required_skills)
    # Should detect missing GenAI/LLM skills
    genai_skills = {"large language models", "retrieval augmented generation", "langchain",
                    "vector database", "prompt engineering"}
    assert len(missing & genai_skills) > 0, f"Expected some GenAI gaps, got: {missing}"
