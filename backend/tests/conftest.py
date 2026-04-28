"""Shared fixtures for backend tests."""
import pytest
from pathlib import Path

SAMPLE_CV = (Path(__file__).parent.parent / "data" / "examples" / "sample_cv.txt").read_text()
AI_JOB = (Path(__file__).parent.parent / "data" / "examples" / "ai_engineer_job.txt").read_text()
ML_JOB = (Path(__file__).parent.parent / "data" / "examples" / "ml_engineer_job.txt").read_text()

MINIMAL_CV = """
Professional Summary
Software engineer with 3 years experience in Python and machine learning.

Technical Skills
Python, scikit-learn, PyTorch, FastAPI, Docker, Git, SQL, pandas

Experience
ML Engineer at TechCorp (2022-2024)
- Trained and deployed classification models using scikit-learn and PyTorch
- Built FastAPI services and deployed with Docker

Projects
RAG Pipeline: built retrieval augmented generation system with ChromaDB and sentence-transformers.
"""
