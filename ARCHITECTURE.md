# ARCHITECTURE.md — AI Career Gap Analyzer

## System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (React + Vite :5173)"]
        UI[Dashboard]
        Upload[CV Upload Panel]
        JD[Job Description Input]
        Results[Results: Score · Chart · Gaps · Plan]
        Export[Markdown Export]
    end

    subgraph Backend["Backend (FastAPI :8000)"]
        API_CV[POST /cv/upload]
        API_JOBS[POST /jobs/analyze]
        API_MATCH[POST /match]
        API_SKILLS[GET /skills/taxonomy]
        API_EXPORT[POST /analysis/export-markdown]

        subgraph Services
            CVParser[cv_parser]
            JobParser[job_parser]
            SkillExtractor[skill_extractor]
            EmbeddingMatcher[embedding_matcher]
            Scoring[scoring]
            LLMAnalyzer[llm_analyzer]
            Exporter[exporter]
        end

        TaxonomyYAML[(skills_taxonomy.yaml)]
        EmbeddingModel[(all-MiniLM-L6-v2\nlocal model)]
    end

    subgraph Optional
        OpenAI[OpenAI-compatible API\nOptional]
    end

    UI --> API_MATCH
    Upload --> API_CV
    JD --> API_MATCH
    Export --> API_EXPORT

    API_CV --> CVParser
    API_JOBS --> JobParser
    API_MATCH --> SkillExtractor
    API_MATCH --> EmbeddingMatcher
    API_MATCH --> Scoring
    API_MATCH --> LLMAnalyzer
    API_EXPORT --> Exporter

    SkillExtractor --> TaxonomyYAML
    EmbeddingMatcher --> EmbeddingModel
    LLMAnalyzer -.->|if key set| OpenAI
```

## CV Parsing Flow

```mermaid
sequenceDiagram
    participant User
    participant API as POST /cv/upload
    participant Parser as cv_parser
    participant PDF as pdfplumber / pypdf

    User->>API: Upload PDF
    API->>API: Validate type + size
    API->>PDF: Extract raw text
    PDF-->>Parser: raw text
    Parser->>Parser: Regex section splitting
    Parser-->>API: CVParseResult {raw_text, summary, experience, projects, skills, ...}
    API-->>User: JSON response
```

## Job Parsing Flow

```mermaid
sequenceDiagram
    participant API as POST /jobs/analyze
    participant JobParser
    participant SkillExtractor

    API->>JobParser: raw job description text
    JobParser->>JobParser: Split required / preferred blocks
    JobParser->>SkillExtractor: extract(required_block)
    SkillExtractor->>SkillExtractor: Regex match against taxonomy index
    SkillExtractor-->>JobParser: list[SkillMatch]
    JobParser->>SkillExtractor: extract(preferred_block)
    SkillExtractor-->>JobParser: list[SkillMatch]
    JobParser->>JobParser: Extract years, soft skills, cloud, MLOps
    JobParser-->>API: JobParseResult
```

## Skill Extraction Flow

```
skills_taxonomy.yaml
        │
        ▼
SkillExtractor._build_index()
        │   term_index: {synonym → (canonical_skill, category)}
        ▼
SkillExtractor.extract(text)
        │   Regex word-boundary search for each term
        │   Deduplication by canonical name
        ▼
list[SkillMatch] {skill, category, evidence, similarity_score=1.0}
```

## Embedding Matching Flow

```mermaid
flowchart LR
    CV[CV text] -->|split into phrases| CVPhrases[CV Phrases]
    JobSkills[Unmatched Job Skills] --> JobEmb[Job Embeddings\nall-MiniLM-L6-v2]
    CVPhrases --> CVEmb[CV Phrase Embeddings\nall-MiniLM-L6-v2]
    JobEmb --> CosSim[Cosine Similarity Matrix\nn_job × n_phrases]
    CVEmb --> CosSim
    CosSim -->|score ≥ 0.60| PartialMatch[Partial Match]
    CosSim -->|score ≥ 0.85| StrongMatch[Strong Semantic Match]
```

## Scoring Flow

```
cv_skills (exact) ∩ job_skills → exact_matches
job_skills \ exact_matches → unmatched_job_skills
  → EmbeddingMatcher → partial_matches (0.60–0.85 threshold)

For each category:
  category_score = (exact × 0.6 + partial × 0.4) / required_in_category × 100

total_fit_score = weighted_avg(category_scores, CATEGORY_WEIGHTS) × 0.6
                + (exact × 0.6 + partial × 0.4) / total_required × 100 × 0.4
```

## Optional LLM Analysis Flow

```mermaid
flowchart TD
    Check{OPENAI_API_KEY set?}
    Check -->|Yes| LLMCall[OpenAI API call\nwith CV + gap summary]
    Check -->|No| Deterministic[Template-based analysis]
    LLMCall -->|JSON response| Validate[Pydantic validation]
    LLMCall -->|API error| Deterministic
    Validate --> Enrich[Enrich AnalysisResult]
    Deterministic --> Enrich
    Enrich --> Response[Final AnalysisResult]
```

## Frontend Flow

```
User lands on Dashboard
    ↓
CvUploadPanel: PDF upload → POST /cv/upload → raw_text
    OR paste CV text directly
JobDescriptionInput: paste job description text
    ↓
Click "Analyze Fit" → POST /match
    ↓
Loading state → results rendered:
    FitScoreCard (circular gauge)
    SkillGapTable (matches + gaps)
    CategoryChart (radar + bar chart)
    RecommendationPanel (projects + resume + 30/60/90 plan)
    ExportPanel → POST /analysis/export-markdown → .md download
```

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Embedding model | all-MiniLM-L6-v2 | Fast, no API, good semantic quality |
| Scoring | Deterministic weighted formula | Reproducible, explainable |
| LLM | Optional OpenAI-compatible | Works without paid key |
| Taxonomy | YAML file | Human-editable, version-controlled |
| Backend | FastAPI | Async, auto-docs, Pydantic native |
| Frontend | React + Vite + Tailwind | Modern DX, fast build |
