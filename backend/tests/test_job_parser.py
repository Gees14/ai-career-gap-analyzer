"""Tests for job description parser."""
import pytest
from app.services.skill_extractor import SkillExtractor
from app.services.job_parser import JobParser
from tests.conftest import AI_JOB, ML_JOB


@pytest.fixture(scope="module")
def parser() -> JobParser:
    return JobParser(SkillExtractor())


def test_parse_ai_job_required_skills(parser):
    result = parser.parse(AI_JOB)
    assert len(result.required_skills) > 0


def test_parse_ai_job_detects_rag(parser):
    result = parser.parse(AI_JOB)
    all_skills = set(result.required_skills + result.preferred_skills)
    assert "retrieval augmented generation" in all_skills


def test_parse_ai_job_detects_years(parser):
    result = parser.parse(AI_JOB)
    assert result.years_experience is not None
    assert result.years_experience >= 3


def test_parse_ml_job_detects_mlflow(parser):
    result = parser.parse(ML_JOB)
    all_skills = set(result.required_skills + result.preferred_skills)
    assert "mlflow" in all_skills


def test_parse_ml_job_detects_cloud(parser):
    result = parser.parse(ML_JOB)
    assert len(result.cloud_requirements) > 0


def test_parse_returns_raw_text(parser):
    result = parser.parse(AI_JOB)
    assert result.raw_text == AI_JOB
