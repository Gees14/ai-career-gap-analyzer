# CLAUDE.md — AI Career Gap Analyzer

## Project Purpose
An AI-powered full-stack application that compares a candidate CV against AI/ML Engineer job descriptions,
extracts required skills, identifies gaps, scores fit, and generates a structured improvement plan.
Demonstrates LLM application engineering, semantic matching, explainable scoring, FastAPI, React, and MLOps tooling.

## Tech Stack
- **Backend**: Python 3.11, FastAPI, Pydantic v2, sentence-transformers, scikit-learn, pdfplumber
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts
- **Optional LLM**: OpenAI-compatible API (gpt-4o-mini default) — entirely optional
- **DevOps**: Docker, docker-compose, GitHub Actions, Makefile

## Architecture Overview
```
CV PDF/Text → cv_parser → raw text + sections
Job Text    → job_parser + skill_extractor → required skills
CV Text     → skill_extractor → candidate skills
                    ↓
             embedding_matcher (sentence-transformers)
                    ↓
             scoring.py → fit_score + category_scores + gaps
                    ↓
             llm_analyzer (optional) → enrichment
                    ↓
             FastAPI → JSON response → React Dashboard
```

## Important Commands

```bash
# Backend (from project root)
make install-backend       # Install Python deps
make run-backend           # Start FastAPI on :8000
make test                  # Run all pytest tests
make test-fast             # Run tests excluding slow embedding tests

# Frontend
make install-frontend      # npm install
make run-frontend          # Vite dev server on :5173

# Docker
make docker-up             # Build and start all services
make docker-down           # Stop all services
```

## Coding Conventions
- Backend: type hints on all functions, Pydantic schemas for all I/O
- Services contain business logic; API routes are thin wrappers
- No hardcoded secrets or API keys — use environment variables only
- All skills normalised through `skills_taxonomy.yaml`
- Scoring must be deterministic and reproducible
- Frontend: TypeScript strict mode, API calls only in `services/api.ts`

## Testing
```bash
cd backend && python -m pytest tests/ -v
```
Tests must pass without any paid API key. Use sample fixtures from `data/examples/`.

## Rules for Modifying This Project

1. **Never invent candidate experience** — only surface what is present in the CV text.
2. **Never make LLM API mandatory** — all features must work without `OPENAI_API_KEY`.
3. **Never remove deterministic matching** — `skill_extractor.py` is the foundation.
4. **Keep scoring explainable** — every score must have a computable reason.
5. **Keep services modular** — one responsibility per service file.
6. **Update README.md and ARCHITECTURE.md** when architecture changes.
7. **Update skills_taxonomy.yaml** when adding skill coverage, not hardcoded lists.
8. **Run tests before committing** — `make test` must pass.

## Security Rules
- Validate file uploads: type check + size limit before parsing.
- Never expose stack traces in API error responses.
- Never store uploaded CVs to disk in production without explicit user consent.
- Never commit `.env` or any file containing real API keys.
- Sanitise file paths — never allow path traversal.

## What Claude Must Never Do
- Invent skills or experience not present in the CV text.
- Claim the tool replaces recruiters or guarantees employment.
- Hardcode API keys anywhere in the codebase.
- Make the LLM API required for any feature.
- Return random or non-deterministic scores for the same input.
- Remove or bypass file upload validation.

## Definition of Done
A feature is done when:
- [ ] Service logic is implemented and unit tested
- [ ] API endpoint returns correct Pydantic-validated response
- [ ] Frontend renders the result correctly with loading/error states
- [ ] `make test` passes
- [ ] No secrets in code
- [ ] README and ARCHITECTURE updated if structure changed
