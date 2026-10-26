# RegulaTrace Compliance Intelligence Lab

RegulaTrace turns regulatory language into traceable, reviewable compliance work. The Presentation Edition combines an evidence-first FastAPI backend, persistent case history, document ingestion, a deterministic obligation engine, policy-gap analysis, change impact analysis, human review decisions, and an executable evaluation suite in one polished interface.

It is designed as both a strong classroom demonstration and a transparent research baseline. Every extracted record keeps its source span and metadata; uncertain findings stay visible; review decisions are written to an audit trail. RegulaTrace is not legal advice and does not certify compliance.

## Presentation Edition capabilities

- **Executive Brief** — a high-impact presentation surface with live system KPIs, a three-act product story, research-readiness indicators, and a single button that runs the complete workflow.
- **Document ingestion** — extracts text and metadata from text-based PDF, DOCX, TXT, and Markdown files.
- **Obligation Lab** — compiles clauses into actor, action, modality, timing, conditions, exceptions, references, confidence, and exact provenance.
- **Evidence Graph** — visualizes the chain from authoritative source through normalized obligation to policy evidence and reviewer decision.
- **Policy Comparator** — evaluates actor, action, polarity, timing, exception scope, and evidence sufficiency independently.
- **Change Radar** — aligns old and new provisions, identifies additions, removals, and material modifications, and explains observable changes with clearly labeled possible reasons and actions to review.
- **Persistent case workspace** — stores analyses, restores prior cases, records reviewer decisions, and exposes an audit trail in SQLite.
- **Evaluation Console** — executes a 16-case transparent challenge suite covering extraction, comparison, provenance, deadlines, and versioning.
- **Browser fallback** — retains the original JavaScript engine for demonstration continuity, labels it explicitly, and never presents fallback output as a backend result.
- **Presentation mode** — removes workspace chrome for a clean projector-ready story.

## Run the presentation

### One-click on Windows

Double-click `RUN_PRESENTATION.cmd`.

The launcher creates or reuses `.venv`, installs the required packages when needed, starts the complete application, checks backend health, and opens:

<http://127.0.0.1:8000/#executive>

Only one server is required—the FastAPI app serves both the API and the frontend. Interactive API documentation is available at <http://127.0.0.1:8000/api/docs>.

To stop it, double-click `stop-regulatrace.ps1` or run:

```powershell
powershell -ExecutionPolicy Bypass -File .\stop-regulatrace.ps1
```

### Manual start

```powershell
powershell -ExecutionPolicy Bypass -File .\start-regulatrace.ps1
```

For development with reload enabled:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

## Suggested live demo

1. Open **Executive Brief** and select **Run the live story**.
2. Show the three extracted obligations and their exact evidence spans in **Obligation Lab**.
3. Confirm one record and point out the persisted human decision.
4. Open **Evidence Graph** to explain traceability.
5. Show the multi-dimensional gap in **Policy Comparator**.
6. Show added, removed, and modified duties in **Change Radar**.
7. Finish with the executable benchmark in **Evaluation Console** and export the Executive Brief to PDF from the browser print dialog.

The sample upload document is in `examples/RegulaTrace_Demo_Regulation.docx`. Its issuing authority and jurisdiction are fictional; use it to demonstrate extraction, not as a real legal source. Change Radar's possible rationale is an inference from old and new wording. Verify actual legislative intent with official notes or recitals.

## API surface

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Runtime readiness |
| `POST` | `/api/analyze` | Evidence-linked obligation extraction |
| `POST` | `/api/compare` | Regulatory-to-policy comparison |
| `POST` | `/api/versions/compare` | Regulatory change analysis |
| `POST` | `/api/documents/ingest` | PDF, DOCX, TXT, or Markdown text extraction |
| `GET` | `/api/analyses` | Persistent case history |
| `GET` | `/api/analyses/{analysis_id}` | Restore an analysis |
| `POST` | `/api/reviews` | Persist a reviewer decision |
| `GET` | `/api/analyses/{analysis_id}/audit` | Retrieve the case audit trail |
| `GET` | `/api/dashboard` | Live operational KPIs |
| `GET` | `/api/evaluate` | Execute the challenge suite |

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q --basetemp .pytest-temp
npm test
```

The Presentation Edition includes backend integration tests and the original JavaScript engine tests. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the exact implementation state and research boundaries.

## Repository structure

```text
backend/
  main.py                FastAPI application and routes
  engine.py              deterministic Python analysis engine
  ingestion.py           document text extraction
  storage.py             SQLite cases, reviews, and audit trail
  evaluation.py          executable transparent challenge suite
  schemas.py             typed API contracts
  tests/                 backend integration tests
dist/
  index.html             application and presentation shell
  styles.css             responsive visual system
  js/engine.js           transparent browser fallback
  js/app.js              API integration and interaction layer
tests/engine.test.js     original JavaScript engine tests
examples/RegulaTrace_Demo_Regulation.docx  presentation upload document
RUN_PRESENTATION.cmd     one-click Windows launcher
start-regulatrace.ps1    environment-aware startup and health check
stop-regulatrace.ps1     clean local shutdown
PROJECT_STATUS.md        verified scope and known research boundaries
```

## Research path

The deterministic engine is a reproducible and inspectable lower bound. A paper-oriented evaluation can compare it against character n-gram, legal-domain encoder, and constrained language-model variants using document-level splits. The recommended primary safety metric is critical-miss rate, supported by field-level span F1, provenance integrity, comparison macro F1, change-impact recall, calibration, and reviewer time.

The UI, typed API contracts, stored provenance, audit model, and executable benchmark already provide the scaffolding for that study without hiding the baseline behind unverifiable claims.

## Team

- Lakshit Sachdeva — B102
- Anannya Samudra — B103
- Trayee Nayampalli — B084
- Riddhi Ranjan — B097

## License

MIT. See [LICENSE](LICENSE).
