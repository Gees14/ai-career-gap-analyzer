import { useState } from 'react'
import type { AnalysisResult } from '../types'
import { analyzeMatch } from '../services/api'
import CvUploadPanel from '../components/CvUploadPanel'
import JobDescriptionInput from '../components/JobDescriptionInput'
import FitScoreCard from '../components/FitScoreCard'
import SkillGapTable from '../components/SkillGapTable'
import CategoryChart from '../components/CategoryChart'
import RecommendationPanel from '../components/RecommendationPanel'
import ExportPanel from '../components/ExportPanel'

export default function Dashboard() {
  const [cvText, setCvText] = useState('')
  const [jobText, setJobText] = useState('')
  const [useLlm, setUseLlm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const canAnalyze = cvText.trim().length >= 50 && jobText.trim().length >= 50

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await analyzeMatch({
        cv_text: cvText,
        job_descriptions: [jobText],
        use_llm: useLlm,
      })
      setResult(res)
      setTimeout(() => {
        document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analysis failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input section */}
      <div className="grid lg:grid-cols-2 gap-6">
        <CvUploadPanel cvText={cvText} onCvText={setCvText} />
        <JobDescriptionInput
          jobText={jobText}
          onJobText={setJobText}
          useLlm={useLlm}
          onUseLlm={setUseLlm}
        />
      </div>

      {/* Analyze button */}
      <div className="flex flex-col items-center gap-3">
        <button
          onClick={handleAnalyze}
          disabled={!canAnalyze || loading}
          className="inline-flex items-center gap-2 px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-xl text-base transition-colors shadow-sm"
        >
          {loading ? (
            <>
              <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Analyzing…
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Analyze Fit
            </>
          )}
        </button>
        {!canAnalyze && !loading && (
          <p className="text-xs text-slate-400">
            Add CV text (min 50 chars) and a job description to enable analysis.
          </p>
        )}
        {error && (
          <div className="w-full max-w-lg bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Results section */}
      {result && (
        <div id="results" className="space-y-6 pt-2">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-slate-900">Analysis Results</h2>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
              {useLlm ? 'LLM Enhanced' : 'Deterministic'}
            </span>
          </div>

          <FitScoreCard
            score={result.fit_score}
            explanation={result.explanation}
            fitAssessment={result.fit_assessment}
          />

          <div className="grid lg:grid-cols-2 gap-6">
            <SkillGapTable
              strongMatches={result.strong_matches}
              partialMatches={result.partial_matches}
              missingRequired={result.missing_required_skills}
              missingPreferred={result.missing_preferred_skills}
            />
            <CategoryChart categoryScores={result.category_scores} />
          </div>

          <RecommendationPanel
            recommendations={result.recommendations}
            resumeSuggestions={result.resume_suggestions}
            learningPlan={result.learning_plan}
            profileSummary={result.profile_summary}
          />

          <ExportPanel
            analysis={result}
            cvName="candidate"
            jobTitle="AI/ML Engineer"
          />
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && (
        <div className="text-center py-16 text-slate-400">
          <svg className="mx-auto w-12 h-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">Your analysis will appear here after you click Analyze Fit.</p>
        </div>
      )}
    </div>
  )
}
