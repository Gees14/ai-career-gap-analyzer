interface Props {
  score: number
  explanation: string
  fitAssessment: string
}

function scoreColor(score: number): string {
  if (score >= 75) return 'text-emerald-600'
  if (score >= 50) return 'text-amber-500'
  return 'text-red-500'
}

function scoreLabel(score: number): string {
  if (score >= 75) return 'Strong Match'
  if (score >= 50) return 'Moderate Fit'
  return 'Significant Gaps'
}

function scoreBgColor(score: number): string {
  if (score >= 75) return 'bg-emerald-50 border-emerald-200'
  if (score >= 50) return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
}

export default function FitScoreCard({ score, explanation, fitAssessment }: Props) {
  const pct = Math.min(100, Math.max(0, score))
  const circumference = 2 * Math.PI * 54
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className={`bg-white rounded-xl border shadow-sm p-6 ${scoreBgColor(score)}`}>
      <h2 className="text-base font-semibold text-slate-800 mb-4">Overall Fit Score</h2>

      <div className="flex items-center gap-6">
        {/* Circular gauge */}
        <div className="relative w-32 h-32 shrink-0">
          <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#e2e8f0" strokeWidth="10" />
            <circle
              cx="60" cy="60" r="54"
              fill="none"
              stroke={score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-700"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${scoreColor(score)}`}>{Math.round(pct)}</span>
            <span className="text-xs text-slate-400">/100</span>
          </div>
        </div>

        <div className="flex-1">
          <p className={`text-lg font-bold ${scoreColor(score)}`}>{scoreLabel(score)}</p>
          {fitAssessment && (
            <p className="text-sm text-slate-600 mt-1">{fitAssessment}</p>
          )}
          {explanation && (
            <p className="text-xs text-slate-500 mt-2 italic">{explanation}</p>
          )}
        </div>
      </div>
    </div>
  )
}
