import type { SkillMatch } from '../types'

interface Props {
  strongMatches: SkillMatch[]
  partialMatches: SkillMatch[]
  missingRequired: string[]
  missingPreferred: string[]
}

function Badge({ label, variant }: { label: string; variant: 'green' | 'amber' | 'red' | 'slate' }) {
  const styles = {
    green: 'bg-emerald-100 text-emerald-700',
    amber: 'bg-amber-100 text-amber-700',
    red: 'bg-red-100 text-red-700',
    slate: 'bg-slate-100 text-slate-500',
  }
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${styles[variant]}`}>
      {label}
    </span>
  )
}

export default function SkillGapTable({
  strongMatches,
  partialMatches,
  missingRequired,
  missingPreferred,
}: Props) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <h2 className="text-base font-semibold text-slate-800 mb-4">Skill Gap Analysis</h2>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <StatCard label="Strong Matches" value={strongMatches.length} color="emerald" />
        <StatCard label="Partial Matches" value={partialMatches.length} color="amber" />
        <StatCard label="Missing Required" value={missingRequired.length} color="red" />
        <StatCard label="Missing Preferred" value={missingPreferred.length} color="slate" />
      </div>

      {/* Strong matches */}
      {strongMatches.length > 0 && (
        <Section title="Strong Matches">
          <div className="flex flex-wrap gap-2">
            {strongMatches.map((m) => (
              <SkillChip key={m.skill} match={m} variant="green" />
            ))}
          </div>
        </Section>
      )}

      {/* Partial matches */}
      {partialMatches.length > 0 && (
        <Section title="Partial Matches">
          <div className="flex flex-wrap gap-2">
            {partialMatches.map((m) => (
              <SkillChip key={m.skill} match={m} variant="amber" />
            ))}
          </div>
        </Section>
      )}

      {/* Missing required */}
      {missingRequired.length > 0 && (
        <Section title="Missing Required Skills">
          <div className="flex flex-wrap gap-2">
            {missingRequired.map((s) => (
              <Badge key={s} label={s} variant="red" />
            ))}
          </div>
        </Section>
      )}

      {/* Missing preferred */}
      {missingPreferred.length > 0 && (
        <Section title="Missing Preferred Skills">
          <div className="flex flex-wrap gap-2">
            {missingPreferred.map((s) => (
              <Badge key={s} label={s} variant="slate" />
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colors: Record<string, string> = {
    emerald: 'text-emerald-600',
    amber: 'text-amber-500',
    red: 'text-red-500',
    slate: 'text-slate-400',
  }
  return (
    <div className="bg-slate-50 rounded-lg p-3 text-center">
      <p className={`text-2xl font-bold ${colors[color]}`}>{value}</p>
      <p className="text-xs text-slate-500 mt-0.5">{label}</p>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{title}</h3>
      {children}
    </div>
  )
}

function SkillChip({ match, variant }: { match: SkillMatch; variant: 'green' | 'amber' }) {
  const styles = {
    green: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    amber: 'bg-amber-50 border-amber-200 text-amber-700',
  }
  return (
    <div
      className={`group relative inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border text-xs font-medium cursor-default ${styles[variant]}`}
      title={match.evidence || match.category}
    >
      {match.skill}
      <span className="text-[10px] opacity-60">({match.category})</span>
    </div>
  )
}
