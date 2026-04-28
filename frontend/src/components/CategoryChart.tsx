import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

interface Props {
  categoryScores: Record<string, number>
}

export default function CategoryChart({ categoryScores }: Props) {
  const data = Object.entries(categoryScores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)
    .map(([category, score]) => ({
      category: category.length > 18 ? category.slice(0, 16) + '…' : category,
      score: Math.round(score),
    }))

  if (data.length === 0) return null

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <h2 className="text-base font-semibold text-slate-800 mb-4">Category Scores</h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis
              dataKey="category"
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.25}
              strokeWidth={2}
            />
            <Tooltip
              formatter={(v: number) => [`${v}%`, 'Score']}
              contentStyle={{ fontSize: 12 }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Bar list below chart */}
      <div className="mt-4 space-y-1.5">
        {Object.entries(categoryScores)
          .sort(([, a], [, b]) => b - a)
          .map(([cat, score]) => (
            <div key={cat} className="flex items-center gap-2 text-xs">
              <span className="w-36 shrink-0 text-slate-600 truncate">{cat}</span>
              <div className="flex-1 bg-slate-100 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${score >= 75 ? 'bg-emerald-500' : score >= 50 ? 'bg-amber-400' : 'bg-red-400'}`}
                  style={{ width: `${score}%` }}
                />
              </div>
              <span className="w-8 text-right text-slate-500">{Math.round(score)}%</span>
            </div>
          ))}
      </div>
    </div>
  )
}
