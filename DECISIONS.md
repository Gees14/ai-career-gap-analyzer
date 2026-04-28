# DECISIONS.md — Architecture Decision Records

## ADR-001: FastAPI as Backend Framework

**Decision**: Use FastAPI (Python) as the backend web framework.

**Rationale**:
- Native Pydantic v2 integration for strict schema validation
- Automatic OpenAPI documentation at `/docs`
- Async-first, suitable for future LLM streaming
- Standard in the AI/ML Python ecosystem
- Excellent type hint support

**Alternatives considered**:
- Flask: simpler but no native typing/schema support
- Django: too heavyweight for this API-focused service
- Express/Node: Python is standard for ML workloads

---

## ADR-002: Local Embeddings with sentence-transformers

**Decision**: Use `sentence-transformers` with `all-MiniLM-L6-v2` for semantic matching.

**Rationale**:
- No API key required — fully local, zero cost at inference time
- 384-dimension embeddings with strong semantic quality for technical text
- Fast on CPU; 80ms per batch of 32 phrases
- Enables semantic matching of synonymous skills not in the taxonomy

**Alternatives considered**:
- OpenAI `text-embedding-ada-002`: excellent quality but requires paid API
- TF-IDF only: no semantic understanding, misses paraphrases
- Larger models (all-mpnet-base-v2): better quality but 3× slower

**Future migration**: Can swap in OpenAI embeddings or a fine-tuned model by replacing `_load_model()` in `embedding_matcher.py`.

---

## ADR-003: Optional LLM Integration

**Decision**: LLM analysis (profile summary, recommendations, learning plan) is entirely optional.

**Rationale**:
- System must be usable in air-gapped or cost-sensitive environments
- Deterministic fallback ensures consistent, testable output
- Avoids vendor lock-in for core functionality
- LLM output requires validation — Pydantic ensures structured output is correct

**Implementation**:
- `OPENAI_API_KEY` not set → `llm_analyzer._deterministic_enrich()` runs
- `OPENAI_API_KEY` set → OpenAI API called, JSON response validated with Pydantic
- LLM API errors fall back to deterministic analysis automatically

---

## ADR-004: Deterministic Scoring

**Decision**: Fit score is computed by a deterministic formula, not by an LLM.

**Rationale**:
- Reproducibility: same input → same score, always
- Explainability: every component of the score has a traceable reason
- Testability: scoring logic is fully unit-testable without API calls
- Trust: candidates can understand why they received a score

**Formula**:
```
category_score = (exact_matches × 0.6 + partial_matches × 0.4) / required_in_category × 100
total_score = weighted_avg(category_scores, weights) × 0.6 + coverage_ratio × 100 × 0.4
```

---

## ADR-005: YAML Skills Taxonomy

**Decision**: Maintain skills, synonyms, and categories in `configs/skills_taxonomy.yaml`.

**Rationale**:
- Human-readable and human-editable without code changes
- Version-controlled: taxonomy changes are tracked in git
- Single source of truth for both extraction and API taxonomy endpoint
- Synonyms handle the real-world variability in how skills are expressed

**Alternatives considered**:
- Hardcoded Python dicts: brittle, harder to maintain
- Database: over-engineering for this scale
- NLP-based NER: less reliable, harder to audit

---

## ADR-006: React + TypeScript + Vite Frontend

**Decision**: Use React 18 with TypeScript and Vite as the frontend stack.

**Rationale**:
- TypeScript catches interface mismatches between frontend and API at compile time
- Vite provides near-instant HMR for development
- React is the standard for AI product dashboards
- Tailwind CSS enables rapid, consistent UI without custom CSS

**Alternatives considered**:
- Next.js: SSR not needed for this SPA; adds complexity
- Vue: smaller ecosystem for AI tooling integrations
- Svelte: smaller community, fewer charting libraries

---

## ADR-007: Docker Compose for Local Development

**Decision**: Provide `docker-compose.yml` as the primary multi-service runner.

**Rationale**:
- Single command (`make docker-up`) starts both services
- Reproducible environment across developer machines
- Backend pre-downloads embedding model in Dockerfile for faster startup
- Easy to add services (database, vector store) in future

**Note**: Embedding model download in Dockerfile adds ~200 MB to image size but eliminates cold-start delay.

---

## ADR-008: No Persistent Storage by Default

**Decision**: Uploaded CVs are not stored to disk; analysis is stateless.

**Rationale**:
- Privacy: user CV data is sensitive — not persisting it is the safest default
- Simplicity: no database or file storage to manage
- Stateless API is easier to scale

**Future migration**: Add optional Redis or PostgreSQL backend for saving analyses with user consent.
