import type { LearningPlan } from '../types'

interface Props {
  recommendations: string[]
  resumeSuggestions: string[]
  learningPlan: LearningPlan
  profileSummary: string
}

export default function RecommendationPanel({
  recommendations,
  resumeSuggestions,
  learningPlan,
  profileSummary,
}: Props) {
  return (
    <div className="space-y-4">
      {profileSummary && (
        <Card title="Profile Summary" icon="👤">
          <p className="text-sm text-slate-600">{profileSummary}</p>
        </Card>
      )}

      {recommendations.length > 0 && (
        <Card title="Recommended Actions & Projects" icon="🚀">
          <ol className="space-y-2">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex gap-3 text-sm text-slate-700">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </span>
                {rec}
              </li>
            ))}
          </ol>
        </Card>
      )}

      {resumeSuggestions.length > 0 && (
        <Card title="Resume Improvement Suggestions" icon="📝">
          <ul className="space-y-1.5">
            {resumeSuggestions.map((s, i) => (
              <li key={i} className="flex gap-2 text-sm text-slate-700">
                <span className="text-amber-500 mt-0.5">→</span>
                {s}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {(learningPlan.days_30.length > 0 || learningPlan.days_60.length > 0 || learningPlan.days_90.length > 0) && (
        <Card title="30 / 60 / 90 Day Learning Plan" icon="📅">
          <div className="grid md:grid-cols-3 gap-4">
            <PlanPhase title="First 30 Days" items={learningPlan.days_30} color="bg-blue-50 border-blue-200" />
            <PlanPhase title="Days 31–60" items={learningPlan.days_60} color="bg-purple-50 border-purple-200" />
            <PlanPhase title="Days 61–90" items={learningPlan.days_90} color="bg-indigo-50 border-indigo-200" />
          </div>
        </Card>
      )}
    </div>
  )
}

function Card({ title, icon, children }: { title: string; icon: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <h2 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <span>{icon}</span> {title}
      </h2>
      {children}
    </div>
  )
}

function PlanPhase({ title, items, color }: { title: string; items: string[]; color: string }) {
  if (items.length === 0) return null
  return (
    <div className={`rounded-lg border p-3 ${color}`}>
      <h3 className="text-xs font-semibold text-slate-600 mb-2">{title}</h3>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-xs text-slate-700 flex gap-1.5">
            <span className="text-slate-400 mt-0.5">•</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
