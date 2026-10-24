# RegulaTrace Project Status

Status date: 2026-10-24  
Current milestone: Phase 1 — Python backend integration

## Verification

- Backend API: 7 tests passed on 2026-10-24.
- Existing JavaScript engine: 5 tests passed on 2026-10-24.
- Browser integration: health, analysis, policy comparison and version comparison all returned HTTP 200; the UI rendered 3 obligations, a `POTENTIAL_MISMATCH`, 4 version changes and a 7-node Evidence Graph with no console errors.

## Implemented

- FastAPI service with interactive OpenAPI documentation.
- Typed Pydantic request and response models.
- `GET /api/health`.
- `POST /api/analyze` with source metadata and evidence-linked obligation output.
- `POST /api/compare` with constraint-level policy comparison.
- `POST /api/versions/compare` with deterministic change classification.
- Python port of the existing JavaScript rule engine, preserving its response structure and intended semantics.
- Explicit structured validation and server error responses.
- Configurable CORS for the local frontend.
- Frontend API integration for all three analysis operations.
- Clearly labeled browser fallback when the API is unavailable; fallback output is never presented as a backend result.
- Existing Obligation Lab, Policy Comparator, Change Radar, Evidence Graph, Evaluation Console, guided demo, navigation and visual design.
- Backend API tests and the original five JavaScript engine tests.

## Partial

- The Python and JavaScript deterministic engines are intentionally duplicated for offline fallback. Phase 1 validates representative parity cases, but a larger generated parity corpus would strengthen drift detection.
- The backend accepts plain text and source metadata only. Source authenticity and document retrieval remain manual.
- Review state changes remain browser-session state and are not persisted.
- Evaluation Console values remain clearly labeled research fixtures rather than results from an annotated legal corpus.

## Not implemented in Phase 1

- PDF or document ingestion.
- Database persistence, authentication or multi-user review workflows.
- Semantic embeddings, vector search or retrieval-augmented generation.
- Legal-BERT, transformer models or other learned extraction models.
- Production deployment, rate limiting, audit-log persistence or background jobs.
- Legal advice, compliance certification or autonomous release decisions.

## Known limitations

- Rule-based clause segmentation and actor/action extraction can fail on deeply nested provisions, inherited headings, tables, quotations and unusual drafting styles.
- Deadline normalization supports the deterministic units and patterns present in the original engine; it does not resolve calendars, business days or jurisdiction-specific computation rules.
- Policy comparison uses lexical overlap and explicit constraint checks, not semantic equivalence.
- Version alignment is greedy and lexical; extensive reordering or paraphrase can appear as removals and additions.
- The static hosted demo cannot host the Python process. Run the FastAPI service locally, or deploy it separately and set `window.REGULATRACE_API_BASE_URL` before loading `app.js`.

