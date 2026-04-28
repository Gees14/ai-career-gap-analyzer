# TASKS.md — Implementation Checklist

## Backend

### Core Services
- [x] `app/services/cv_parser.py` — PDF + text parsing with section extraction
- [x] `app/services/job_parser.py` — Job description parsing with required/preferred split
- [x] `app/services/skill_extractor.py` — Keyword + synonym taxonomy matching
- [x] `app/services/embedding_matcher.py` — sentence-transformers semantic matching
- [x] `app/services/scoring.py` — Explainable fit scoring with category weights
- [x] `app/services/llm_analyzer.py` — Optional LLM enrichment with deterministic fallback
- [x] `app/services/exporter.py` — Markdown export

### API Routes
- [x] `GET /health`
- [x] `POST /cv/upload`
- [x] `POST /jobs/analyze`
- [x] `POST /match`
- [x] `GET /skills/taxonomy`
- [x] `POST /analysis/export-markdown`

### Config & Infrastructure
- [x] `app/core/config.py` — Pydantic settings with env vars
- [x] `app/core/logging.py` — Structured logging
- [x] `app/core/errors.py` — Error handlers
- [x] `app/schemas.py` — All Pydantic models
- [x] `configs/skills_taxonomy.yaml` — 15 categories, 70+ skills, 200+ synonyms

## Frontend

- [x] `src/types/index.ts` — TypeScript interfaces
- [x] `src/services/api.ts` — All API calls
- [x] `src/components/Layout.tsx` — App shell
- [x] `src/components/CvUploadPanel.tsx` — File upload + text paste
- [x] `src/components/JobDescriptionInput.tsx` — Job text + LLM toggle
- [x] `src/components/FitScoreCard.tsx` — Circular score gauge
- [x] `src/components/SkillGapTable.tsx` — Matches + gaps
- [x] `src/components/CategoryChart.tsx` — Radar chart + bar list
- [x] `src/components/RecommendationPanel.tsx` — Projects + resume + plan
- [x] `src/components/ExportPanel.tsx` — Markdown download
- [x] `src/pages/Dashboard.tsx` — Main page orchestrator

## Testing

- [x] `tests/test_skill_extractor.py` — Extraction, synonyms, normalisation
- [x] `tests/test_cv_parser.py` — Section detection, empty text
- [x] `tests/test_job_parser.py` — Required/preferred split, years, cloud
- [x] `tests/test_scoring.py` — Score range, reproducibility, gap detection
- [x] `tests/test_embedding_matcher.py` — Embeddings, similarity
- [x] `tests/test_api_health.py` — API integration tests

## DevOps

- [x] `backend/Dockerfile`
- [x] `frontend/Dockerfile`
- [x] `docker-compose.yml`
- [x] `Makefile`
- [x] `.github/workflows/ci.yml`
- [x] `.env.example`
- [x] `.gitignore`

## Documentation

- [x] `README.md`
- [x] `CLAUDE.md`
- [x] `PROJECT_SPEC.md`
- [x] `ARCHITECTURE.md`
- [x] `TASKS.md`
- [x] `DECISIONS.md`
- [x] `backend/README.md`
- [x] `frontend/README.md`

## Example Data

- [x] `data/examples/sample_cv.txt`
- [x] `data/examples/ai_engineer_job.txt`
- [x] `data/examples/ml_engineer_job.txt`

## Future Improvements

- [ ] Support for multiple job description comparison view
- [ ] LinkedIn profile URL as CV input
- [ ] Salary range estimation by skill fit
- [ ] Skill trend analysis (what's gaining/losing demand)
- [ ] ATS keyword density analysis
- [ ] Interview preparation question generator
- [ ] Support for scanned PDF OCR
- [ ] ChromaDB-backed job description library
- [ ] User accounts and saved analyses
- [ ] Batch CV analysis for recruiting teams
