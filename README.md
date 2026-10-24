# RegulaTrace Compliance Intelligence Lab

RegulaTrace is an evidence-first research prototype for compiling regulatory
language into atomic obligations, comparing those obligations with internal
policy evidence, and tracing the impact of regulatory revisions.

The prototype is intentionally transparent: it exposes source spans,
intermediate fields, confidence, unresolved states, version identity and human
review status. It is not legal advice and does not certify compliance.

## Live capabilities

- **Obligation Lab** — parses source text into actor, action, modality, timing,
  conditions, exceptions and cross-references.
- **Policy Comparator** — evaluates actor, action, polarity, timing, exception
  scope and evidence sufficiency separately.
- **Change Radar** — aligns old and new provisions and identifies added,
  removed and materially modified clauses.
- **Evidence Graph** — visualizes the path from authoritative source through
  normalized obligation to reviewer decision.
- **Evaluation Console** — presents baselines, challenge cases, safety metrics
  and a reproducible study design.

## Run locally

Requirements: Python 3.11+ and Node.js 20+.

Create an isolated Python environment and install the Phase 1 API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

In a second terminal, activate the same environment and start the static
frontend:

```powershell
.\.venv\Scripts\Activate.ps1
python -m http.server 4173 --directory dist
```

Open <http://127.0.0.1:4173>. The top navigation reports **FastAPI connected**
when requests are served by the backend. If the API is unavailable, the
interface explicitly reports **Browser fallback** and uses the original
deterministic JavaScript engine; fallback output is never labeled as a backend
result.

API documentation is available at <http://127.0.0.1:8000/api/docs> and ReDoc
at <http://127.0.0.1:8000/api/redoc>.

To use a separately deployed API, set `window.REGULATRACE_API_BASE_URL` before
`dist/js/app.js` loads, or change the `regulatrace-api-base` meta tag in
`dist/index.html`.

### Run tests

```powershell
python -m pytest backend/tests -q
npm test
```

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for implemented, partial and
intentionally deferred capabilities.

## Repository structure

```text
dist/
  index.html             application shell
  styles.css             responsive visual system
  js/engine.js           transparent NLP and comparison engine
  js/app.js              interaction and visualization layer
  docs/                   research proposal
tests/engine.test.js     executable baseline tests
backend/                 FastAPI service, typed schemas and deterministic Python engine
backend/tests/           API and CORS tests
requirements.txt         Python dependencies
PROJECT_STATUS.md        milestone scope and known limitations
.openai/hosting.json     Sites deployment manifest
```

## Research path

The lexical engine is a reproducible lower bound. A paper-oriented study can
compare it with character n-gram, legal-domain encoder and constrained language
model variants on document-level splits. The primary safety metric should be
critical-miss rate; supporting metrics include field-level span F1, provenance
integrity, policy-comparison macro F1, change-impact recall and reviewer time.

The interface already reflects that experimental design so learned models can
replace or augment the baseline without changing the evidence contract.

## Team

- Lakshit Sachdeva — B102
- Anannya Samudra — B103
- Trayee Nayampalli — B084
- Riddhi Ranjan — B097


## License

MIT. See [LICENSE](LICENSE).

