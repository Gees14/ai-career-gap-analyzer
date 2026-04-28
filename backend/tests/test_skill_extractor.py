"""Tests for the deterministic skill extractor."""
import pytest
from app.services.skill_extractor import SkillExtractor
from tests.conftest import SAMPLE_CV, AI_JOB, MINIMAL_CV


@pytest.fixture(scope="module")
def extractor() -> SkillExtractor:
    return SkillExtractor()


def test_extracts_python(extractor):
    matches = extractor.extract("I have 5 years of Python experience.")
    skill_names = [m.skill for m in matches]
    assert "python" in skill_names


def test_extracts_rag_synonym(extractor):
    matches = extractor.extract("Built a retrieval augmented generation system.")
    skill_names = [m.skill for m in matches]
    assert "retrieval augmented generation" in skill_names


def test_extracts_transformer_synonym(extractor):
    matches = extractor.extract("Used Hugging Face transformers for fine-tuning BERT.")
    skill_names = [m.skill for m in matches]
    assert "transformers" in skill_names


def test_synonym_normalisation(extractor):
    # "distilbert" is a synonym for "transformers"
    matches = extractor.extract("Fine-tuned DistilBERT for classification.")
    skill_names = [m.skill for m in matches]
    assert "transformers" in skill_names


def test_chromadb_maps_to_vector_database(extractor):
    matches = extractor.extract("Using ChromaDB as a vector database for semantic search.")
    skill_names = [m.skill for m in matches]
    assert "vector database" in skill_names


def test_no_duplicates(extractor):
    matches = extractor.extract("Python and more Python and python again.")
    python_hits = [m for m in matches if m.skill == "python"]
    assert len(python_hits) == 1


def test_evidence_returned(extractor):
    matches = extractor.extract("I built a FastAPI backend for the ML model.")
    fastapi_matches = [m for m in matches if m.skill == "fastapi"]
    assert fastapi_matches
    assert fastapi_matches[0].evidence != ""


def test_sample_cv_extracts_known_skills(extractor):
    matches = extractor.extract(SAMPLE_CV)
    skill_names = {m.skill for m in matches}
    expected = {"python", "fastapi", "retrieval augmented generation", "mlflow", "docker"}
    assert expected.issubset(skill_names), f"Missing: {expected - skill_names}"


def test_ai_job_extracts_skills(extractor):
    matches = extractor.extract(AI_JOB)
    skill_names = {m.skill for m in matches}
    assert "retrieval augmented generation" in skill_names
    assert "vector database" in skill_names
    assert "large language models" in skill_names


def test_empty_text_returns_empty(extractor):
    assert extractor.extract("") == []


def test_taxonomy_returns_dict(extractor):
    taxonomy = extractor.get_taxonomy()
    assert isinstance(taxonomy, dict)
    assert "Machine Learning" in taxonomy
    assert "Generative AI" in taxonomy
