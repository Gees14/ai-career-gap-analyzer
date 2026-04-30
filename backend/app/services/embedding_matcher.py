"""Embedding-based semantic matching using sentence-transformers."""
from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas import SkillMatch

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)

_PARTIAL_MATCH_THRESHOLD = 0.60
_STRONG_MATCH_THRESHOLD = 0.75


@lru_cache(maxsize=1)
def _load_model() -> "SentenceTransformer":
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    logger.info("Loading embedding model: %s", settings.embedding_model)
    return SentenceTransformer(settings.embedding_model)


class EmbeddingMatcher:
    """Computes semantic similarity between CV skill phrases and job requirements."""

    def __init__(self) -> None:
        self._model = _load_model()

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 768))
        return self._model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

    def find_semantic_matches(
        self,
        cv_phrases: list[str],
        job_skills: list[tuple[str, str]],  # (skill_name, category)
    ) -> list[SkillMatch]:
        """
        For each job skill not already exactly matched, find the best-matching
        CV phrase via cosine similarity.  Returns SkillMatch objects for
        partial matches above threshold.
        """
        if not cv_phrases or not job_skills:
            return []

        job_names = [s for s, _ in job_skills]
        job_cats = [c for _, c in job_skills]

        cv_embs = self.embed(cv_phrases)
        job_embs = self.embed(job_names)

        # shape: (n_job_skills, n_cv_phrases)
        sims = cosine_similarity(job_embs, cv_embs)
        best_idx = sims.argmax(axis=1)
        best_scores = sims[np.arange(len(job_skills)), best_idx]

        matches: list[SkillMatch] = []
        for i, (skill, cat) in enumerate(job_skills):
            score = float(best_scores[i])
            if _PARTIAL_MATCH_THRESHOLD <= score < _STRONG_MATCH_THRESHOLD:
                evidence = cv_phrases[best_idx[i]][:120]
                matches.append(
                    SkillMatch(
                        skill=skill,
                        category=cat,
                        evidence=evidence,
                        similarity_score=round(score, 3),
                    )
                )
        return matches

    def score_cv_job_similarity(self, cv_text: str, job_text: str) -> float:
        """Return overall semantic similarity between two text blocks (0-1)."""
        embs = self.embed([cv_text[:512], job_text[:512]])
        if embs.shape[0] < 2:
            return 0.0
        return float(cosine_similarity(embs[:1], embs[1:])[0][0])


@lru_cache(maxsize=1)
def get_embedding_matcher() -> EmbeddingMatcher:
    return EmbeddingMatcher()
