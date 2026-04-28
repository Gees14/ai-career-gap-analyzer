import { useState, useRef, type ChangeEvent, type DragEvent } from 'react'
import { uploadCv } from '../services/api'

interface Props {
  cvText: string
  onCvText: (text: string) => void
}

export default function CvUploadPanel({ cvText, onCvText }: Props) {
  const [fileName, setFileName] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    setError(null)
    if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      setUploading(true)
      try {
        const result = await uploadCv(file)
        onCvText(result.raw_text)
        setFileName(file.name)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Upload failed')
      } finally {
        setUploading(false)
      }
    } else if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      const text = await file.text()
      onCvText(text)
      setFileName(file.name)
    } else {
      setError('Only PDF or TXT files are supported.')
    }
  }

  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <h2 className="text-base font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <span className="text-blue-600">01</span> Upload CV
      </h2>

      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          dragging ? 'border-blue-400 bg-blue-50' : 'border-slate-300 hover:border-blue-400'
        }`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          className="hidden"
          onChange={onInputChange}
        />
        {uploading ? (
          <p className="text-sm text-blue-600 animate-pulse">Parsing PDF…</p>
        ) : fileName ? (
          <p className="text-sm text-green-600 font-medium">✓ {fileName}</p>
        ) : (
          <>
            <p className="text-sm text-slate-500">Drop PDF or TXT here, or click to browse</p>
            <p className="text-xs text-slate-400 mt-1">Max 10 MB</p>
          </>
        )}
      </div>

      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}

      <div className="mt-4">
        <label className="block text-xs font-medium text-slate-600 mb-1">
          Or paste CV text directly
        </label>
        <textarea
          className="w-full h-40 text-xs border border-slate-200 rounded-lg p-3 resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
          placeholder="Paste your CV text here…"
          value={cvText}
          onChange={(e) => onCvText(e.target.value)}
        />
        <p className="text-xs text-slate-400 mt-1">{cvText.length} characters</p>
      </div>
    </div>
  )
}
