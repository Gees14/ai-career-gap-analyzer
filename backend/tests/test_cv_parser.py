"""Tests for CV parser."""
import pytest
from app.services.cv_parser import parse_cv_text
from tests.conftest import SAMPLE_CV, MINIMAL_CV


def test_parse_returns_raw_text():
    result = parse_cv_text(SAMPLE_CV)
    assert len(result.raw_text) > 100


def test_parse_extracts_skills_section():
    result = parse_cv_text(SAMPLE_CV)
    assert "python" in result.skills.lower() or "pytorch" in result.skills.lower()


def test_parse_extracts_experience_section():
    result = parse_cv_text(SAMPLE_CV)
    assert len(result.experience) > 50


def test_parse_extracts_education():
    result = parse_cv_text(SAMPLE_CV)
    assert "university" in result.education.lower() or result.education != ""


def test_parse_minimal_cv():
    result = parse_cv_text(MINIMAL_CV)
    assert result.raw_text == MINIMAL_CV
    assert result.skills != "" or result.experience != ""


def test_parse_empty_text_returns_empty():
    result = parse_cv_text("")
    assert result.raw_text == ""
    assert result.skills == ""


def test_parse_text_without_headers_uses_fallback():
    text = "I know Python and TensorFlow and have 3 years of experience in ML."
    result = parse_cv_text(text)
    assert result.raw_text == text
