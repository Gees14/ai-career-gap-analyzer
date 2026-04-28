# PROJECT_SPEC.md — AI Career Gap Analyzer

## Product Goal
Help software engineers and data professionals understand how their CV compares to AI/ML Engineer job descriptions,
identify skill gaps, and receive a structured improvement plan — all locally, without sharing data with third parties.

## Target Users
- Software engineers transitioning into AI/ML roles
- Data scientists targeting ML Engineering positions
- ML Engineers preparing for senior AI Engineer interviews
- Career coaches reviewing client profiles

## User Stories

1. As a candidate, I can upload my CV as a PDF so the system extracts my skills automatically.
2. As a candidate, I can paste a job description so the system identifies what is required.
3. As a candidate, I can see an overall fit score (0–100) with a plain-English explanation.
4. As a candidate, I can see which skills I have that match the job (strong and partial matches).
5. As a candidate, I can see which required skills are missing from my CV.
6. As a candidate, I can see a per-category score breakdown (GenAI, MLOps, Cloud, etc.).
7. As a candidate, I can see recommended projects and learning actions.
8. As a candidate, I can see resume improvement suggestions.
9. As a candidate, I can download a Markdown report of the full analysis.
10. As a developer, I can run the system without any paid API keys.

## Core Features
- PDF and text CV upload with section extraction
- Job description parsing with skill identification
- Skills taxonomy (15 categories, 70+ canonical skills, 200+ synonyms)
- Exact skill matching with evidence snippets
- Embedding-based semantic partial matching (sentence-transformers)
- Explainable fit scoring (0–100) with category breakdown
- Optional LLM enrichment (profile summary, recommendations, learning plan)
- Deterministic fallback for all LLM features
- Markdown export
- React dashboard with interactive charts

## Non-Functional Requirements
- All analysis must be reproducible: same input → same output, always
- Backend must start without any API keys
- PDF parsing must not crash on malformed files (fallback to raw text)
- API response time: under 5 seconds for deterministic mode
- No user data stored to disk by default
- All secrets via environment variables

## Matching Requirements
- Exact match: skill or synonym found in CV text
- Partial match: cosine similarity ≥ 0.60 between CV phrase and job skill embedding
- Strong match threshold: cosine similarity ≥ 0.85 or exact keyword match
- Synonyms normalised to canonical skill name before scoring
- Score is weighted by category importance (Generative AI: 18%, Machine Learning: 15%, etc.)

## API Requirements
- `POST /cv/upload` — PDF/TXT upload → CVParseResult
- `POST /jobs/analyze` — job text → JobParseResult[]
- `POST /match` — cv_text + job_descriptions → AnalysisResult
- `GET /skills/taxonomy` — full taxonomy JSON
- `POST /analysis/export-markdown` — AnalysisResult → Markdown string
- `GET /health` — service health check

## Success Criteria
- `make test` passes with zero failures (no API key required)
- Sample CV vs. AI Engineer job produces fit_score > 0
- Missing skills are detected for a CV without GenAI experience
- Score is identical on repeated runs with the same input
- Markdown export contains all sections
- Frontend renders without errors on a clean install

## Out of Scope
- Storing user CVs in a database
- Multi-user accounts or authentication
- Automatic job description scraping
- LinkedIn or GitHub profile integration
- Guaranteeing hiring outcomes
- Replacing human recruiters

## Limitations
- PDF parsing quality depends on PDF structure (scanned PDFs not supported)
- Skill extraction is keyword-based; domain jargon not in the taxonomy may be missed
- LLM analysis quality depends on the model and API availability
- Fit score is a heuristic — not a substitute for human judgment
