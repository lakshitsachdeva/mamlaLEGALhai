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

Requirements: a recent Python installation for the static server and Node.js
20+ for tests.

```bash
npm test
npm run serve
```

Then open <http://localhost:4173>.

No document is sent to an external API. The current engine runs entirely in
the browser.

## Repository structure

```text
dist/
  index.html             application shell
  styles.css             responsive visual system
  js/engine.js           transparent NLP and comparison engine
  js/app.js              interaction and visualization layer
  docs/                   research proposal
tests/engine.test.js     executable baseline tests
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

B.Tech Computer Engineering, C Division, NMIMS MPSTME Mumbai, 2026–27.

## License

MIT. See [LICENSE](LICENSE).

