interface Props {
  jobText: string
  onJobText: (text: string) => void
  useLlm: boolean
  onUseLlm: (v: boolean) => void
}

export default function JobDescriptionInput({ jobText, onJobText, useLlm, onUseLlm }: Props) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <h2 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <span className="text-blue-600">02</span> Job Description
      </h2>

      <textarea
        className="w-full h-52 text-xs border border-slate-200 rounded-lg p-3 resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
        placeholder="Paste one or more job descriptions here…"
        value={jobText}
        onChange={(e) => onJobText(e.target.value)}
      />
      <p className="text-xs text-slate-400 mt-1">{jobText.length} characters</p>

      <div className="mt-4 flex items-center gap-3">
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <div
            className={`relative w-10 h-5 rounded-full transition-colors ${
              useLlm ? 'bg-blue-600' : 'bg-slate-300'
            }`}
            onClick={() => onUseLlm(!useLlm)}
          >
            <div
              className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                useLlm ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </div>
          <span className="text-xs text-slate-600">
            Use LLM enrichment
            <span className="ml-1 text-slate-400">(requires API key)</span>
          </span>
        </label>
      </div>
    </div>
  )
}
