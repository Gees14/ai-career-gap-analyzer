"""Optional LLM-powered analysis layer.

Falls back to deterministic template-based output when no API key is configured.
Never invents experience that is not present in the CV text.
"""
from __future__ import annotations

import json
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas import AnalysisResult, LearningPlan

logger = get_logger(__name__)


class LLMAnalyzer:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Optional[object] = None
        self._llm_available = False
        self._init_client()

    def _init_client(self) -> None:
        if not self._settings.openai_api_key:
            logger.info("No LLM API key configured — using deterministic analysis")
            return
        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                base_url=self._settings.openai_base_url,
            )
            self._llm_available = True
            logger.info("LLM client initialised (model: %s)", self._settings.openai_model)
        except Exception as exc:
            logger.warning("Failed to init LLM client: %s", exc)

    # ------------------------------------------------------------------
    def enrich(
        self,
        base_result: AnalysisResult,
        cv_text: str,
        job_descriptions: list[str],
    ) -> AnalysisResult:
        """Add profile summary, recommendations, resume suggestions, learning plan."""
        if self._llm_available and self._client:
            return self._llm_enrich(base_result, cv_text, job_descriptions)
        return self._deterministic_enrich(base_result, cv_text)

    # ------------------------------------------------------------------
    def _llm_enrich(
        self,
        result: AnalysisResult,
        cv_text: str,
        job_descriptions: list[str],
    ) -> AnalysisResult:
        system_prompt = (
            "You are a senior AI/ML career coach. "
            "Your task is to analyse a candidate's CV against job requirements. "
            "IMPORTANT: You must NEVER invent skills or experience not present in the CV. "
            "Only rephrase or highlight what is already there. "
            "Respond with valid JSON only — no markdown fences."
        )

        strong = ", ".join(m.skill for m in result.strong_matches[:10])
        missing = ", ".join(result.missing_required_skills[:10])
        score = result.fit_score

        user_prompt = f"""
CV TEXT (first 2000 chars):
{cv_text[:2000]}

JOB REQUIREMENTS SUMMARY:
Strong matches already found: {strong}
Missing required skills: {missing}
Fit score: {score}/100

Return JSON with exactly these keys:
{{
  "profile_summary": "2-3 sentence summary based only on CV content",
  "fit_assessment": "2-3 sentences on fit for this role",
  "recommendations": ["project idea 1", "project idea 2", "project idea 3"],
  "resume_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "learning_plan": {{
    "days_30": ["action 1", "action 2"],
    "days_60": ["action 1", "action 2"],
    "days_90": ["action 1", "action 2"]
  }}
}}
"""
        try:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1200,
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
            return self._apply_llm_data(result, data)
        except Exception as exc:
            logger.warning("LLM call failed (%s) — falling back to deterministic", exc)
            return self._deterministic_enrich(result, cv_text)

    def _apply_llm_data(self, result: AnalysisResult, data: dict) -> AnalysisResult:
        result.profile_summary = str(data.get("profile_summary", ""))
        result.fit_assessment = str(data.get("fit_assessment", ""))
        result.recommendations = [str(r) for r in data.get("recommendations", [])]
        result.resume_suggestions = [str(s) for s in data.get("resume_suggestions", [])]
        plan_data = data.get("learning_plan", {})
        result.learning_plan = LearningPlan(
            days_30=[str(x) for x in plan_data.get("days_30", [])],
            days_60=[str(x) for x in plan_data.get("days_60", [])],
            days_90=[str(x) for x in plan_data.get("days_90", [])],
        )
        return result

    # ------------------------------------------------------------------
    def _deterministic_enrich(
        self, result: AnalysisResult, cv_text: str
    ) -> AnalysisResult:
        strong = [m.skill for m in result.strong_matches[:5]]
        missing = result.missing_required_skills[:5]
        score = result.fit_score

        result.profile_summary = (
            f"Candidate demonstrates experience in {', '.join(strong[:3]) if strong else 'multiple technical areas'}. "
            "Profile extracted directly from CV content."
        )
        result.fit_assessment = (
            f"With a fit score of {score:.0f}/100, the candidate "
            + ("is a strong match for this role." if score >= 75 else
               "shows moderate alignment with some gaps to address." if score >= 50 else
               "has significant gaps relative to the role requirements.")
        )

        if missing:
            result.recommendations = [
                f"Build a hands-on project demonstrating {missing[0]}",
                f"Complete an online course or tutorial on {missing[1] if len(missing) > 1 else missing[0]}",
                "Contribute to an open-source AI/ML project to demonstrate collaboration",
                "Build an end-to-end ML pipeline project with monitoring and CI/CD",
                "Create a RAG-based application using open-source tools",
            ]
        else:
            result.recommendations = [
                "Publish a technical blog post about your most complex project",
                "Contribute to an open-source AI/ML framework",
                "Build a portfolio project demonstrating end-to-end MLOps",
            ]

        result.resume_suggestions = [
            "Quantify achievements with metrics (e.g., 'reduced inference latency by 40%')",
            "Add a dedicated Technical Skills section with grouped categories",
            "Use active verbs: designed, implemented, deployed, optimised, evaluated",
            f"Highlight any {missing[0] if missing else 'recent AI'} experience even if indirect",
            "Add GitHub links to projects directly in the CV",
        ]

        result.learning_plan = LearningPlan(
            days_30=self._plan_30(missing),
            days_60=self._plan_60(missing),
            days_90=self._plan_90(missing),
        )

        return result

    def _plan_30(self, missing: list[str]) -> list[str]:
        base = [
            "Audit current CV and update with quantified achievements",
            "Complete one hands-on tutorial for each top missing skill",
        ]
        if missing:
            base.append(f"Start a focused study plan for: {missing[0]}")
        return base

    def _plan_60(self, missing: list[str]) -> list[str]:
        base = [
            "Build a small end-to-end project incorporating top missing skills",
            "Push project to GitHub with a clear README",
        ]
        if len(missing) > 1:
            base.append(f"Deepen understanding of {missing[1]} through a structured course")
        return base

    def _plan_90(self, missing: list[str]) -> list[str]:
        return [
            "Complete a capstone portfolio project demonstrating all key skills",
            "Apply to target roles with updated CV and projects",
            "Prepare technical interview topics: ML system design, coding, ML concepts",
        ]
