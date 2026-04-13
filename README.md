# Golden Set Coverage Advisor

A decision-support tool that helps analysts and Product Owners evaluate whether accuracy and consistency golden sets still represent real production language.

## Overview

The Golden Set Coverage Advisor (Quality Evaluation) provides a structured workflow for importing evaluation datasets, running coverage and statistical analysis, generating actionable recommendations, and tracking approvals. It is designed for teams that maintain golden sets used in product quality gates.

## Features

### Dashboard (`/quality-evaluation`)
KPI cards, actionability summary, and recent run overview.

### Data Intake (`/quality-evaluation/intake`)
Upload real-input, accuracy, consistency, and status-mapping datasets in CSV, JSON, or Markdown format. Configure observation windows, thresholds, and protected-case rules before running analysis.

### Analysis Workbench (`/quality-evaluation/analysis`)
- Intent coverage table with 7-group classification
- Wording gap table for paraphrase coverage
- Mapping coverage chart

### Recommendations Review (`/quality-evaluation/recommendations`)
Filterable queue of 8 recommendation types with a detail drawer, evidence tracing, and an analyst → PO approval workflow.

### Reports and Export (`/quality-evaluation/reports`)
Run history, approval register, and export to Markdown, CSV, or JSON with PII filtering.

## Key Capabilities

- Canonical Intent Determination Engine — deterministic 8-stage pipeline for intent classification, normalization, and comparison anchor generation
- Wilson score confidence intervals for statistical stability evaluation
- Deterministic rule-table-first normalization with audit trail
- Protected-case handling (policy-blocked, PII, non-English, unsupported-intent, rule-behavior-sensitive)
- 4-level priority scoring (Critical / High / Medium / Low)
- State machine governed approval workflow (Draft → Analyst Reviewed → PO Review → Approved → Implemented → Archived)
- Property-based tests validating correctness invariants (23 intent engine properties + existing suite)

## Tech Stack

- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Icons**: Lucide React
- **Font**: Inter (Google Fonts)
- **Testing**: Jest + fast-check (frontend), pytest + Hypothesis (backend)

## Getting Started

### 1. Python Backend

```bash
cd python-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (Next.js)

```bash
npm install
npm run dev
```

The frontend reads `NEXT_PUBLIC_API_BASE_URL` from `.env.local` to route all API calls to the Python backend:

```
# .env.local (project root)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Running Tests

```bash
# Frontend (Jest)
npm test

# Backend (pytest + Hypothesis)
cd python-backend
pytest
```

## Canonical Intent Determination Engine

The engine classifies input records through an 8-stage pipeline:

1. **Text Normalization** — lowercase, punctuation stripping, separator normalization, spelling variant substitution
2. **Protected-Case Routing** — policy-blocked, PII, non-English detection with terminate/continue modes
3. **Supported Intent Matching** — exact phrase, synonym, and regex pattern matching against the intent catalog
4. **Disambiguation** — priority-score resolution, rule-based tie-breaking, ambiguity flagging
5. **Unsupported Intent Detection** — catalog-matched or generic unsupported labeling
6. **Unknown Handling** — fallback classification for unresolvable inputs
7. **Outcome Normalization** — status and option value canonicalization
8. **Comparison Anchor Generation** — pipe-delimited anchor strings per intent class

### Usage

```python
from engine import IntentDeterminationService, IntentEngineConfig, InputRecord

config = IntentEngineConfig(...)  # Load from external config
service = IntentDeterminationService(config)

# Single record
result = service.determine(record)

# Batch processing
results = service.determine_batch(records)

# Hot-reload config
service.reload_config(new_config)
```

Each `IntentDeterminationResult` includes the resolved intent, normalized outcome, comparison anchor, decision method, applied rules, and catalog version for full traceability.

## Project Structure

```
app/
├── page.tsx                        # Root page
├── layout.tsx                      # App shell layout
├── globals.css                     # Global styles
└── quality-evaluation/             # Quality Evaluation pages
    ├── page.tsx                    #   Dashboard
    ├── intake/                     #   Data Intake / Run Setup
    ├── analysis/                   #   Analysis Workbench
    ├── recommendations/            #   Recommendations Review
    └── reports/                    #   Reports / Export

components/
├── layout/                         # App shell (header, containers)
├── quality-evaluation/             # Quality Evaluation components
└── ui/                             # Shared UI primitives

lib/
├── quality-evaluation/
│   ├── api-client.ts               # Fetch wrapper (routes calls to Python backend)
│   └── types.ts                    # Domain types and enums
├── constants/                      # App configuration
└── types/                          # Shared TypeScript types

python-backend/
├── main.py                         # App entry point + CORS + route wiring
├── api/                            # REST route handlers
├── engine/                         # Analysis engine modules
│   ├── intent_engine.py            #   Canonical Intent Determination Service
│   ├── intent_pipeline.py          #   8-stage pipeline (pure functions)
│   ├── intent_config.py            #   Configuration models & loader
│   ├── intent_matching.py          #   Exact/synonym/pattern matching
│   └── ...                         #   Normalization, comparison, recommendations
├── models/                         # Pydantic data models
│   ├── intent_models.py            #   InputRecord, IntentDeterminationResult
│   └── ...                         #   Domain models, enums, requests
├── storage/                        # Pluggable persistence (in-memory / JSON file)
└── tests/                          # pytest + Hypothesis
    ├── property/                   #   Property-based tests (23 intent engine properties)
    └── unit/                       #   Unit tests

docs/                               # Business and software requirements
```

## Architecture

The Next.js frontend is a pure UI layer. All analysis, storage, and business logic runs in the Python FastAPI backend.

```
┌─────────────────────────────┐
│   Next.js Frontend (React)   │
│   api-client.ts fetch wrapper│
└──────────┬──────────────────┘
           │  NEXT_PUBLIC_API_BASE_URL
           ▼
┌─────────────────────────────┐
│   Python FastAPI Backend     │
│   ├── API routes             │
│   ├── Analysis engine        │
│   │   └── Intent Engine      │
│   └── Storage layer          │
└─────────────────────────────┘
```
