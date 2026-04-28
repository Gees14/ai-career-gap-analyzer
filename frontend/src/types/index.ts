export interface SkillMatch {
  skill: string
  category: string
  evidence: string
  similarity_score: number
}

export interface LearningPlan {
  days_30: string[]
  days_60: string[]
  days_90: string[]
}

export interface AnalysisResult {
  fit_score: number
  category_scores: Record<string, number>
  strong_matches: SkillMatch[]
  partial_matches: SkillMatch[]
  missing_required_skills: string[]
  missing_preferred_skills: string[]
  profile_summary: string
  fit_assessment: string
  recommendations: string[]
  resume_suggestions: string[]
  learning_plan: LearningPlan
  explanation: string
}

export interface MatchRequest {
  cv_text: string
  job_descriptions: string[]
  use_llm: boolean
}

export interface ApiError {
  error: string
}

export type AppState = 'idle' | 'loading' | 'success' | 'error'
