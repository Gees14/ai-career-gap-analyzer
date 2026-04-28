"""API integration tests — runs without paid API keys."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_skills_taxonomy_returns_categories():
    response = client.get("/skills/taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert "Machine Learning" in data
    assert "Generative AI" in data
    assert isinstance(data["Machine Learning"], list)


def test_match_endpoint_basic():
    from tests.conftest import SAMPLE_CV, AI_JOB

    response = client.post(
        "/match",
        json={
            "cv_text": SAMPLE_CV,
            "job_descriptions": [AI_JOB],
            "use_llm": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "fit_score" in data
    assert 0 <= data["fit_score"] <= 100
    assert "strong_matches" in data
    assert "missing_required_skills" in data


def test_match_validation_rejects_short_cv():
    response = client.post(
        "/match",
        json={
            "cv_text": "short",
            "job_descriptions": ["job desc"],
            "use_llm": False,
        },
    )
    assert response.status_code == 422


def test_jobs_analyze_endpoint():
    from tests.conftest import AI_JOB

    response = client.post(
        "/jobs/analyze",
        json={"job_descriptions": [AI_JOB]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "required_skills" in data[0]


def test_export_markdown_endpoint():
    analysis = {
        "fit_score": 75.0,
        "category_scores": {"Machine Learning": 80.0},
        "strong_matches": [{"skill": "python", "category": "Data Engineering", "evidence": "...", "similarity_score": 1.0}],
        "partial_matches": [],
        "missing_required_skills": ["kubernetes"],
        "missing_preferred_skills": [],
        "profile_summary": "Strong candidate.",
        "fit_assessment": "Good fit.",
        "recommendations": ["Build a RAG project"],
        "resume_suggestions": ["Add metrics"],
        "learning_plan": {"days_30": ["Study LangChain"], "days_60": [], "days_90": []},
        "explanation": "Good match overall.",
    }
    response = client.post(
        "/analysis/export-markdown",
        json={"analysis": analysis, "cv_name": "Test Candidate", "job_title": "AI Engineer"},
    )
    assert response.status_code == 200
    text = response.text
    assert "75" in text
    assert "Career Gap Analysis" in text
    assert "kubernetes" in text.lower()
