"""Explainable fit scoring engine."""
from __future__ import annotations

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas import AnalysisResult, SkillMatch
from app.services.embedding_matcher import EmbeddingMatcher
from app.services.skill_extractor import SkillExtractor

logger = get_logger(__name__)

# Category importance weights (must sum to 1.0)
_CATEGORY_WEIGHTS: dict[str, float] = {
    "Generative AI": 0.18,
    "Machine Learning": 0.15,
    "LLMOps": 0.12,
    "MLOps": 0.10,
    "Deep Learning": 0.10,
    "NLP": 0.08,
    "Software Engineering": 0.08,
    "Backend APIs": 0.06,
    "Cloud": 0.06,
    "Data Engineering": 0.04,
    "DevOps": 0.02,
    "Testing": 0.01,
}


class ScoringEngine:
    def __init__(
        self,
        extractor: SkillExtractor,
        matcher: EmbeddingMatcher,
    ) -> None:
        self._extractor = extractor
        self._matcher = matcher
        self._settings = get_settings()

    def score(
        self,
        cv_text: str,
        job_descriptions: list[str],
    ) -> AnalysisResult:
        combined_job_text = "\n\n".join(job_descriptions)

        cv_skills = self._extractor.extract(cv_text)
        job_skills = self._extractor.extract(combined_job_text)

        cv_skill_names = {s.skill for s in cv_skills}
        job_skill_names = {s.skill for s in job_skills}

        # --- Exact matches ---
        exact_match_names = cv_skill_names & job_skill_names
        exact_matches = [s for s in job_skills if s.skill in exact_match_names]

        # --- Semantic partial matches for unmatched job skills ---
        unmatched_job = [(s.skill, s.category) for s in job_skills if s.skill not in exact_match_names]
        cv_phrases = self._build_cv_phrases(cv_text)
        partial_matches = self._matcher.find_semantic_matches(cv_phrases, unmatched_job)
        partial_match_names = {m.skill for m in partial_matches}

        # --- Missing skills ---
        all_matched = exact_match_names | partial_match_names
        missing_skills = [s.skill for s in job_skills if s.skill not in all_matched]

        # --- Category scores ---
        category_scores = self._compute_category_scores(
            job_skills, exact_matches, partial_matches
        )

        # --- Total fit score ---
        fit_score = self._compute_total_score(
            exact_matches, partial_matches, job_skills, category_scores
        )

        explanation = self._build_explanation(
            fit_score, exact_matches, partial_matches, missing_skills
        )

        return AnalysisResult(
            fit_score=round(fit_score, 1),
            category_scores={k: round(v, 1) for k, v in category_scores.items()},
            strong_matches=exact_matches,
            partial_matches=partial_matches,
            missing_required_skills=missing_skills[:15],
            missing_preferred_skills=[],
            explanation=explanation,
        )

    # ------------------------------------------------------------------
    def _build_cv_phrases(self, cv_text: str) -> list[str]:
        """Split CV into overlapping chunks to preserve context for semantic matching."""
        import re
        # Split into sentences/lines first
        raw = re.split(r"(?<=[.!?])\s+|\n+", cv_text)
        sentences = [s.strip() for s in raw if len(s.strip()) > 15]

        # Build 2-sentence chunks with 1-sentence overlap for context
        chunks: list[str] = []
        for i in range(len(sentences)):
            chunk = " ".join(sentences[i : i + 2])
            if len(chunk) > 20:
                chunks.append(chunk)

        # Also include individual sentences so short bullet points aren't lost
        chunks.extend(s for s in sentences if len(s) > 20)

        # Deduplicate while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for c in chunks:
            if c not in seen:
                seen.add(c)
                result.append(c)
        return result[:120]

    def _compute_category_scores(
        self,
        job_skills: list[SkillMatch],
        exact_matches: list[SkillMatch],
        partial_matches: list[SkillMatch],
    ) -> dict[str, float]:
        by_category: dict[str, dict] = {}
        for s in job_skills:
            by_category.setdefault(s.category, {"required": 0, "exact": 0, "partial": 0})
            by_category[s.category]["required"] += 1

        exact_names = {m.skill for m in exact_matches}
        partial_names = {m.skill for m in partial_matches}

        for s in job_skills:
            cat = s.category
            if s.skill in exact_names:
                by_category[cat]["exact"] += 1
            elif s.skill in partial_names:
                by_category[cat]["partial"] += 1

        scores: dict[str, float] = {}
        for cat, counts in by_category.items():
            if counts["required"] == 0:
                scores[cat] = 0.0
                continue
            w_exact = self._settings.score_weight_exact
            w_sem = self._settings.score_weight_semantic
            raw = (
                (counts["exact"] * w_exact + counts["partial"] * w_sem)
                / counts["required"]
            ) * 100
            scores[cat] = min(100.0, raw)

        return scores

    def _compute_total_score(
        self,
        exact_matches: list[SkillMatch],
        partial_matches: list[SkillMatch],
        job_skills: list[SkillMatch],
        category_scores: dict[str, float],
    ) -> float:
        if not job_skills:
            return 0.0

        # Weighted average of category scores
        total_weight = 0.0
        weighted_sum = 0.0
        for cat, score in category_scores.items():
            w = _CATEGORY_WEIGHTS.get(cat, 0.02)
            weighted_sum += score * w
            total_weight += w

        if total_weight == 0:
            return 0.0

        # Normalise to known weights; remaining categories share leftover weight evenly
        base_score = weighted_sum / total_weight

        # Blend with simple coverage ratio to avoid over-weighting category weights
        total_required = len(job_skills)
        coverage = (
            len(exact_matches) * self._settings.score_weight_exact
            + len(partial_matches) * self._settings.score_weight_semantic
        ) / total_required * 100

        return min(100.0, base_score * 0.6 + coverage * 0.4)

    def _build_explanation(
        self,
        fit_score: float,
        exact_matches: list[SkillMatch],
        partial_matches: list[SkillMatch],
        missing_skills: list[str],
    ) -> str:
        lines = [
            f"Overall fit score: {fit_score:.1f}/100.",
            f"Exact skill matches: {len(exact_matches)}.",
            f"Semantic partial matches: {len(partial_matches)}.",
        ]
        if missing_skills:
            top_missing = ", ".join(missing_skills[:5])
            lines.append(f"Key missing skills: {top_missing}.")
        if fit_score >= 75:
            lines.append("Strong candidate — most critical skills are present.")
        elif fit_score >= 50:
            lines.append("Moderate fit — targeted upskilling would significantly improve candidacy.")
        else:
            lines.append("Significant skill gaps identified — a structured learning plan is recommended.")
        return " ".join(lines)
