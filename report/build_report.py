"""Build the current mamlaLEGALhai project report PDF.

Run with the Codex bundled Python or any Python with reportlab installed:
    python report/build_report.py --output dist/docs/mamlaLEGALhai_Project_Report.pdf
"""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
INK = colors.HexColor("#152925")
GREEN = colors.HexColor("#3d6858")
MUTED = colors.HexColor("#52635d")
PALE = colors.HexColor("#edf3ee")
LINE = colors.HexColor("#d5dfd7")
RED = colors.HexColor("#9a524a")
PAGE_W, PAGE_H = A4


ST = {
    "kicker": ParagraphStyle("kicker", fontName="Helvetica-Bold", fontSize=8, leading=12, textColor=GREEN, spaceAfter=8),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=34, leading=39, textColor=INK, spaceAfter=14),
    "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=14, leading=20, textColor=MUTED, spaceAfter=16),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=19, leading=24, textColor=INK, spaceAfter=12),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.2, leading=15, textColor=GREEN, spaceBefore=12, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.1, leading=13.4, textColor=INK, spaceAfter=8),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.1, leading=11.2, textColor=MUTED, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.2, leading=11.2, textColor=INK),
    "cell_head": ParagraphStyle("cell_head", fontName="Helvetica-Bold", fontSize=8.2, leading=11.2, textColor=INK),
    "callout": ParagraphStyle("callout", fontName="Helvetica-Bold", fontSize=9.5, leading=14, textColor=INK),
}


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, ST[style])


def heading(number: str, title: str):
    return [p("mamlaLEGALhai / CURRENT BUILD", "kicker"), p(f"{number}  {title}", "h1"), HRFlowable(width="100%", thickness=1, color=LINE, spaceAfter=15)]


def box(text: str, width: float = 505):
    t = Table([[p(text, "callout")]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    return t


def table(headers: list[str], rows: list[list[str]], widths: list[float]):
    data = [[p(x, "cell_head") for x in headers]] + [[p(x, "cell") for x in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, GREEN),
        ("LINEBELOW", (0, 1), (-1, -1), 0.35, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def figure(path: Path, width: float, caption: str):
    iw, ih = ImageReader(str(path)).getSize()
    return [Image(str(path), width=width, height=width * ih / iw), Spacer(1, 5), p(caption, "small")]


def flow(items: list[tuple[str, str]], width: float):
    cells = [p(f"<b>{title}</b><br/>{detail}", "cell") for title, detail in items]
    t = Table([cells], colWidths=[width / len(items)] * len(items))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 13),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 13),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(44, 48, PAGE_W - 44, 48)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(MUTED)
    canvas.drawString(44, 36, "mamlaLEGALhai  /  IMPLEMENTATION AND RESEARCH REPORT  /  27 OCT 2026")
    canvas.drawRightString(PAGE_W - 44, 36, str(doc.page))
    canvas.restoreState()


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, leftMargin=44, rightMargin=44,
        topMargin=54, bottomMargin=66, title="mamlaLEGALhai: Implementation and Research Report",
        author="Lakshit Sachdeva; Anannya Samudra; Trayee Nayampalli; Riddhi Ranjan",
        subject="Verified prototype, exploratory NLP evaluation, and reviewer-guided neural-symbolic workflow",
    )
    W = PAGE_W - 88
    story = []

    # 1. Cover and executive claim.
    story += [Spacer(1, 50), p("NMIMS MPSTME  /  LEGAL NLP RESEARCH", "kicker"),
              p("mamlaLEGALhai", "title"),
              p("Implementation and research report<br/>Evidence-linked obligation records, external classification probes, and a reviewer-guided InLegalBERT + Z3 check", "subtitle"),
              HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=22),
              p("Lakshit Sachdeva  /  Anannya Samudra  /  Trayee Nayampalli  /  Riddhi Ranjan", "body"),
              p("Current code and manuscript state: 27 October 2026. Named research draft; not submitted to arXiv.", "small"),
              Spacer(1, 29),
              box("mamlaLEGALhai proposes source-linked duty records for human review. It does not decide whether an organization complies with law.", W),
              Spacer(1, 22),
              p("What is actually implemented", "h2"),
              p("A local FastAPI and browser application ingests text-based documents, segments clauses, proposes rule fields with source offsets, keeps reviewer corrections and audit history, compares policy wording and versions, and checks two manually normalized rules with Z3. An optional pinned InLegalBERT encoder scores relatedness between their evidence quotes."),
              p("What is measured", "h2"),
              p("Two exploratory EU sentence-label experiments compare the deterministic rule baseline with simple linear models. They do not measure complete obligation records, contradiction detection, or reviewer benefit."),
              PageBreak()]

    # 2. Concrete current-state scope.
    story += heading("01", "System status")
    story += [p("The product combines an inspectable baseline with explicit review gates. The table separates deployed behavior from the claims that still require independent evaluation."),
              table(["Surface", "Implemented behavior", "Boundary"], [
                  ["Obligation Lab", "Text-based PDF, DOCX, TXT, or Markdown input; clause segmentation; heuristic actor/action/modality/timing fields; source quote and offset.", "A located quote is not a correct field interpretation. OCR and document hierarchy are limited."],
                  ["Review and Evidence Graph", "SQLite cases, field corrections, before/after audit entries, and a visual source-to-record-to-review path.", "The graph is a UI view, not a Neo4j knowledge graph or proof of source authority."],
                  ["Policy Comparator", "Separate heuristic signals for actor, action, polarity, timing, exception, and evidence.", "No evaluated legal entailment or calibrated compliance verdict."],
                  ["Version compare", "Old/new clause alignment and wording-based change flags.", "Suggested reasons are inferences; legal effect and intent need source review."],
                  ["Contradiction Lab", "Optional InLegalBERT quote cosine plus independent Z3 feasibility over reviewed formal fields.", "No automatic text-to-logic model or real-law contradiction accuracy."],
              ], [105, 205, 195]),
              Spacer(1, 18),
              box("The website's 16/16 challenge suite contains authored software checks. It is not an unseen-document accuracy result.", W),
              Spacer(1, 18),
              p("Verification on the current branch", "h2"),
              flow([("30 Python checks", "API, research harness, and neural contract"),
                    ("8 JavaScript checks", "Deterministic browser engine"),
                    ("Live smoke test", "InLegalBERT signal + Z3 proof in the browser")], W),
              PageBreak()]

    # 3. Evidence contract.
    story += heading("02", "From text to a reviewable record")
    story += [p("The baseline treats a supplied document as a Unicode string. It segments candidate clauses and proposes a record containing modality, actor, action, timing, condition, exception, quote, source identifier, version, and a half-open character interval [start, end)."),
              table(["Stage", "Output", "Check performed"], [
                  ["1. Supply text", "Document text and user-supplied source metadata", "File type, size, and basic extraction validation"],
                  ["2. Propose a clause", "One record per segmented clause", "Ordered modal-cue rules and heuristic fields"],
                  ["3. Locate evidence", "Exact quote and Unicode source interval", "The interval reconstructs the quote in supplied/extracted text"],
                  ["4. Human review", "Confirmed, corrected, or rejected record", "Before/after audit event retained locally"],
              ], [108, 180, 217]),
              Spacer(1, 17),
              p("Why the source interval matters", "h2"),
              p("A reviewer can reopen the original wording rather than trusting a paraphrase. Offset validity is machine-checkable, but actor, action, exceptions, and legal meaning still need independent annotation or human judgment. PDF offsets refer to extracted text, not official page coordinates."),
              p("Known representation failure", "h2"),
              p("A clause such as <i>The provider must retain logs and notify the authority within 24 hours</i> contains two acts. The current one-record-per-clause design can store only one action field. A valid quote therefore does not imply a complete obligation representation."),
              box("Evidence-linked means recoverable from the input. It does not mean the input is an authoritative legal source.", W),
              Spacer(1, 20),
              p("The audit path shown in the application", "h2"),
              flow([("Source", "Supplied text and metadata"),
                    ("Proposal", "Rule fields and located quote"),
                    ("Review", "Confirm, correct, or reject"),
                    ("History", "Before/after audit entry")], W),
              PageBreak()]

    # 4. Neural-symbolic method.
    story += heading("03", "Reviewer-guided InLegalBERT + Z3")
    story += [p("The optional path is deliberately narrow. InLegalBERT is a pretrained Indian legal text encoder, used here to signal that two quotes are related. It is not fine-tuned in this project for clause similarity, structured rule extraction, or contradiction labels."),
              table(["Step", "What runs", "What can be concluded"], [
                  ["Neural quote signal", "Pinned law-ai/InLegalBERT revision b5ecfed8ed6c; 256-token maximum; mean pool final non-padding hidden states; cosine.", "A raw, uncalibrated relatedness value. High similarity can coexist with opposite duties."],
                  ["Reviewer gate", "A person checks both exact quotes and actor/action/object/scope/jurisdiction/condition/exception/date fields. Editing a field clears confirmation.", "The formalization was acknowledged by a reviewer, not independently certified correct."],
                  ["Symbolic check", "Z3 runs only for matching formal fields and overlapping dates; obligation adds p, prohibition adds not-p.", "UNSAT means the supplied formal constraints cannot both hold; the proof core identifies the rules."],
              ], [101, 214, 190]),
              Spacer(1, 17),
              p("Worked fictional case", "h2"),
              p("Rule A says a records team must delete a test record. Rule B says the same team must not delete that record in the same scope and period. The live implementation returned both a neural quote signal and a two-rule Z3 unsatisfiable core. This is a functional smoke test, not a contradiction-detection score or a ruling about real Indian statutes."),
              box("The neural cosine does not change the solver constraints. The solver verdict does not validate the neural score or the original legal interpretation.", W),
              Spacer(1, 20),
              p("Two outputs from one reviewed pair", "h2"),
              flow([("Quotes", "Exact spans in supplied passages"),
                    ("InLegalBERT", "Raw relatedness cosine"),
                    ("Z3", "Conditional SAT / UNSAT verdict")], W),
              PageBreak()]

    # 5. First external experiment.
    story += heading("04", "Measured proxy A: deontic modality")
    story += [p("Question: can the rules label explicit obligation, permission, prohibition, power, and right language in an independently released EU sample? After cleaning, 566 distinct texts remain. The release has one annotator's labels and no source-act IDs; three folds group highly similar texts but cannot guarantee source-disjoint evaluation."),
              *figure(ROOT / "paper/regulatrace-preprint/figures/deontic_proxy_scores.png", W, "Figure 1. Three-fold mean scores; whiskers show one fold standard deviation. These are provision-level labels, not complete duty records."),
              table(["Model", "Accuracy", "Macro F1"], [
                  ["mamlaLEGALhai cue rules", "0.922 +/- 0.007", "0.543 +/- 0.036"],
                  ["Word TF-IDF logistic regression", "0.866 +/- 0.038", "0.499 +/- 0.060"],
                  ["Majority class", "0.784", "0.176"],
              ], [230, 130, 145]),
              Spacer(1, 10),
              p("Interpretation", "h2"),
              p("The sample contains 444 obligations among 566 texts. High overall accuracy is therefore insufficient. The rule engine has no output classes for power and right, which depresses its class-balanced score. This experiment does not validate actor/action fields or source authority."),
              PageBreak()]

    # 6. Second external experiment.
    story += heading("05", "Measured proxy B: legal function")
    story += [p("Question: does a sentence impose a regulatory duty on an agent, or is it constitutive text about how a legal system operates? The cleaned set contains 5,831 distinct sentences from 379 CELEX acts. All sentences from an act stay in one of three folds."),
              *figure(ROOT / "paper/regulatrace-preprint/figures/regulatory_binary_scores.png", W, "Figure 2. The same cue rules fail when modal words occur in both regulatory and constitutive sentences."),
              table(["Model", "Mean accuracy", "Regulatory F1"], [
                  ["mamlaLEGALhai cue rules", "0.419 +/- 0.070", "0.588 +/- 0.072"],
                  ["Word TF-IDF linear SVM", "0.852 +/- 0.026", "0.810 +/- 0.046"],
              ], [230, 130, 145]),
              Spacer(1, 10),
              p("Failure mode", "h2"),
              p("The rule baseline flags 3,336 of 3,337 constitutive sentences as regulatory in pooled out-of-fold predictions. A modal cue such as <i>shall</i> is therefore a poor proxy for actionable legal function. The SVM reduces false positives but also misses some regulatory sentences. The two experiments ask different questions; their scores must not be ranked against each other."),
              PageBreak()]

    # 7. How to use the current website.
    story += heading("06", "Presentation and website route")
    story += [p("The local app starts at <b>http://127.0.0.1:8000/#executive</b>. Run <b>sh ./start-mamlalegalhai.sh</b>, then use the numbered route on the Presentation page. The left sidebar remains available when presentation mode is off."),
              table(["Order", "Where to click", "What to tell the audience"], [
                  ["1", "Presentation -> Load demo data", "The example analysis, comparison, version changes, and authored checks are prepared."],
                  ["2", "Obligation Lab -> open a record", "Point to the proposed actor/action/timing and the exact source quote. A reviewer can correct fields."],
                  ["3", "Version compare", "In the fictional example, account reviews change from 90 to 60 days and retention from 12 to 24 months."],
                  ["4", "Contradiction Lab -> Load example -> review -> Run InLegalBERT + Z3", "Read the raw quote score and solver result as separate outputs. Run Z3 only if the optional model is unavailable."],
                  ["5", "Research notes -> Read current paper -> Results", "The external charts measure sentence labels; Evaluation on the site runs only authored checks."],
              ], [45, 213, 247]),
              Spacer(1, 17),
              p("Explain the boundaries in one sentence", "h2"),
              p("<i>mamlaLEGALhai makes proposed rules and their evidence inspectable; the current models and solver do not certify legal compliance.</i>"),
              p("Presentation materials", "h2"),
              p("The repository includes a five-minute script and a ten-minute Click / Say / Understand script in <b>presentation/</b>. The manuscript source is in the repository's <b>paper/</b> directory. The website offers a page-by-page browser view and a PDF download."),
              PageBreak()]

    # 8. Limitations and reproducibility.
    story += heading("07", "Limits, next study, and sources")
    story += [table(["Observed limit", "Required next evidence"], [
                  ["One record per clause; inherited actors, multi-action clauses, complex exceptions", "Expert-marked duty spans and field labels on held-out source documents"],
                  ["Uncalibrated InLegalBERT cosine; no neural field extraction", "Labeled candidate-pair study and a common frozen comparison with legal-domain encoders"],
                  ["Manual rule normalization; strict equality; no legal priority model", "Adjudicated formal rules, exceptions, and real-law conflict/compatibility labels"],
                  ["Local single-user SQLite; no production source authentication", "Identity, permissions, provenance of official sources, and operational review controls"],
                  ["No measured human benefit", "Blinded reviewer study with time, errors, and trust calibration"],
              ], [215, 290]),
              Spacer(1, 15),
              p("Reproduce the measured results", "h2"),
              p("The experiment scripts, input hashes, cleaning rules, grouped folds, and result JSON are in <b>research/experiments/</b>. The five-class and binary results are sentence-classification proxies. The span-level protocol is in <b>research/PROTOCOL.md</b>. The optional model dependencies are in <b>requirements-neural.txt</b>; its weights are not committed."),
              p("References and links", "h2"),
              p("[1] Paul et al. <i>Pre-trained Language Models for the Legal Domain: A Case Study on Indian Law</i>. ICAIL 2023. <link href='https://arxiv.org/abs/2209.06049'>arXiv:2209.06049</link>.", "small"),
              p("[2] Minkova et al. EU deontic-modality data. <link href='https://doi.org/10.34894/HQ8LIH'>doi:10.34894/HQ8LIH</link>.", "small"),
              p("[3] Moodley et al. Regulatory-statement reproducibility data. <link href='https://doi.org/10.5281/zenodo.8200001'>doi:10.5281/zenodo.8200001</link>.", "small"),
              p("[4] mamlaLEGALhai research branch and <link href='https://github.com/trayee05/regulatrace-compliance-intelligence/pull/1'>draft pull request 1</link>.", "small"),
              Spacer(1, 10),
              box("Research status: a working prototype with exploratory external proxies and a conditional neural + symbolic demo. No end-to-end obligation or contradiction accuracy is claimed.", W)]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist/docs/mamlaLEGALhai_Project_Report.pdf")
    args = parser.parse_args()
    build(args.output)
    print(args.output)
