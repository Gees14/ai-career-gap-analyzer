from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SkillMatch(BaseModel):
    skill: str
    category: str
    evidence: str = ""
    similarity_score: float = 1.0


class CategoryScore(BaseModel):
    category: str
    score: float = Field(ge=0, le=100)
    matched: int
    total_required: int


class LearningPlan(BaseModel):
    days_30: list[str] = Field(default_factory=list)
    days_60: list[str] = Field(default_factory=list)
    days_90: list[str] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    fit_score: float = Field(ge=0, le=100)
    category_scores: dict[str, float] = Field(default_factory=dict)
    strong_matches: list[SkillMatch] = Field(default_factory=list)
    partial_matches: list[SkillMatch] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    profile_summary: str = ""
    fit_assessment: str = ""
    recommendations: list[str] = Field(default_factory=list)
    resume_suggestions: list[str] = Field(default_factory=list)
    learning_plan: LearningPlan = Field(default_factory=LearningPlan)
    explanation: str = ""


class CVParseResult(BaseModel):
    raw_text: str
    summary: str = ""
    experience: str = ""
    projects: str = ""
    skills: str = ""
    education: str = ""
    certifications: str = ""


class JobParseResult(BaseModel):
    raw_text: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    tools_frameworks: list[str] = Field(default_factory=list)
    cloud_requirements: list[str] = Field(default_factory=list)
    mlops_requirements: list[str] = Field(default_factory=list)
    genai_requirements: list[str] = Field(default_factory=list)
    software_engineering: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    years_experience: Optional[int] = None


class MatchRequest(BaseModel):
    cv_text: str = Field(min_length=50)
    job_descriptions: list[str] = Field(min_length=1)
    use_llm: bool = False


class JobAnalyzeRequest(BaseModel):
    job_descriptions: list[str] = Field(min_length=1)


class ExportRequest(BaseModel):
    analysis: AnalysisResult
    cv_name: str = "candidate"
    job_title: str = "AI/ML Engineer"
