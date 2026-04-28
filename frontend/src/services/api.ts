import type { AnalysisResult, MatchRequest } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(body.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function analyzeMatch(req: MatchRequest): Promise<AnalysisResult> {
  return request<AnalysisResult>('/match', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export async function uploadCv(file: File): Promise<{ raw_text: string; skills: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/cv/upload`, { method: 'POST', body: form })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(body.error ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function exportMarkdown(
  analysis: AnalysisResult,
  cvName: string,
  jobTitle: string,
): Promise<string> {
  const res = await fetch(`${BASE_URL}/analysis/export-markdown`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis, cv_name: cvName, job_title: jobTitle }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.text()
}

export async function checkHealth(): Promise<{ status: string; llm_available: boolean }> {
  return request('/health')
}
