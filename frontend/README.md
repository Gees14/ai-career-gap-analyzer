# Frontend — AI Career Gap Analyzer

React 18 + TypeScript + Vite + Tailwind CSS dashboard.

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:5173

Requires the backend running on http://localhost:8000 (proxied via Vite).

## Build

```bash
npm run build
```

## Environment

Set `VITE_API_URL` to override the backend URL (default: proxied `/api`).

## Key Components

| Component | Purpose |
|---|---|
| `CvUploadPanel` | PDF upload + text paste |
| `JobDescriptionInput` | Job description text area + LLM toggle |
| `FitScoreCard` | Circular score gauge with label |
| `SkillGapTable` | Strong/partial matches + missing skills |
| `CategoryChart` | Radar chart + bar list by category |
| `RecommendationPanel` | Projects, resume suggestions, 30/60/90 plan |
| `ExportPanel` | Download Markdown report |
