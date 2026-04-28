# Backend — AI Career Gap Analyzer

FastAPI backend with deterministic skill extraction, embedding-based semantic matching, and optional LLM enrichment.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Running Tests

```bash
python -m pytest tests/ -v
```

No API key required. Tests use sample fixtures from `data/examples/`.

## Environment Variables

See `.env.example` in the project root. Key variable:

```
OPENAI_API_KEY=   # Leave blank for deterministic mode (default)
```

## Key Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service health + LLM availability |
| POST | `/cv/upload` | Upload PDF/TXT CV → parsed sections |
| POST | `/jobs/analyze` | Analyze job descriptions → extracted skills |
| POST | `/match` | CV + job descriptions → full analysis |
| GET | `/skills/taxonomy` | Full skills taxonomy |
| POST | `/analysis/export-markdown` | Export analysis as Markdown |

## Project Structure

```
app/
├── main.py          # FastAPI app, middleware, routing
├── schemas.py       # All Pydantic models
├── api/             # Thin route handlers
├── core/            # Config, logging, error handling
└── services/        # Business logic
    ├── cv_parser.py
    ├── job_parser.py
    ├── skill_extractor.py
    ├── embedding_matcher.py
    ├── scoring.py
    ├── llm_analyzer.py
    └── exporter.py
configs/
└── skills_taxonomy.yaml   # 15 categories, 70+ skills, 200+ synonyms
```
