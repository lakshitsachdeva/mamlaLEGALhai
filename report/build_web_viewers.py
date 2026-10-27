"""Render the current PDFs as browser-readable page images.

Requires pdftoppm on PATH and Pillow. Run after building the paper and report PDFs:
    python report/build_web_viewers.py
"""

from __future__ import annotations

import html
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "dist/docs"
DOCUMENTS = [
    ("mamlaLEGALhai_Preprint", "Research preprint", "Measured results begin on page 8.", 8),
    ("mamlaLEGALhai_Project_Report", "Project report", "Measured results begin on page 5.", 5),
]


def build(stem: str, title: str, detail: str, results_page: int) -> None:
    pdf = DOCS / f"{stem}.pdf"
    page_count = len(PdfReader(pdf).pages)
    images = DOCS / f"{stem}_pages"
    images.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mamlalegalhai-pdf-") as temp:
        prefix = Path(temp) / "page"
        subprocess.run(["pdftoppm", "-r", "145", "-png", str(pdf), str(prefix)], check=True)
        rendered = sorted(Path(temp).glob("page-*.png"))
        if len(rendered) != page_count:
            raise RuntimeError(f"Expected {page_count} pages, rendered {len(rendered)}")
        for number, path in enumerate(rendered, 1):
            with Image.open(path) as source:
                source.convert("RGB").save(images / f"page-{number:02}.webp", "WEBP", quality=88, method=6)

    page_nav = "".join(f'<a href="#page-{n}">{n}</a>' for n in range(1, page_count + 1))
    pages = "\n".join(
        f'<figure id="page-{n}"><img src="./{stem}_pages/page-{n:02}.webp" '
        f'alt="{html.escape(title)} page {n} of {page_count}" loading="{"eager" if n == 1 else "lazy"}">'
        f'<figcaption>Page {n} of {page_count}</figcaption></figure>'
        for n in range(1, page_count + 1)
    )
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · mamlaLEGALhai</title>
<style>
:root{{font-family:Inter,Arial,sans-serif;color:#1c2824;background:#f0f2ed}}
*{{box-sizing:border-box}}body{{margin:0}}a{{color:inherit}}header{{position:sticky;top:0;z-index:2;background:#f9faf7;border-bottom:1px solid #d3dbd3;padding:12px clamp(16px,3vw,40px);display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}}
.brand{{font-weight:700;text-decoration:none}}.actions{{display:flex;gap:8px;flex-wrap:wrap}}.actions a{{border:1px solid #bfcfc5;padding:9px 12px;border-radius:5px;text-decoration:none;font-size:14px}}.actions a:last-child{{background:#20362e;color:white;border-color:#20362e}}
main{{max-width:1040px;margin:auto;padding:24px 18px 70px}}h1{{font-size:clamp(28px,4vw,46px);margin:0 0 6px}}.intro{{color:#52655a;margin:0 0 18px}}nav{{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:22px}}nav span{{font-size:13px;margin-right:5px}}nav a{{padding:6px 9px;border:1px solid #ccd8ce;background:#fff;text-decoration:none;border-radius:4px;font-size:13px}}nav .results{{background:#dce8de;font-weight:700}}
figure{{margin:0 0 26px;scroll-margin-top:95px}}figure img{{display:block;width:100%;height:auto;background:white;box-shadow:0 8px 30px #1b312425;border:1px solid #d7ded7}}figcaption{{text-align:center;color:#52655a;font-size:13px;margin-top:8px}}.note{{font-size:13px;color:#52655a}}
@media(max-width:650px){{header{{position:static}}figure{{scroll-margin-top:8px}}}}
</style></head><body>
<header><a class="brand" href="../index.html#research">← mamlaLEGALhai research notes</a><div class="actions"><a href="./{stem}.pdf" download>Download PDF</a><a href="#page-{results_page}">Jump to measured results ↓</a></div></header>
<main><h1>{html.escape(title)}</h1><p class="intro">{html.escape(detail)} This is a page-for-page browser view of the current PDF.</p>
<nav aria-label="Paper pages"><span>Page</span>{page_nav}<a class="results" href="#page-{results_page}">Results</a></nav>
{pages}
<p class="note">For selectable text, citations, and offline use, download the PDF above.</p></main></body></html>
"""
    (DOCS / f"{stem}_view.html").write_text(doc, encoding="utf-8")
    print(f"{stem}: {page_count} pages")


if __name__ == "__main__":
    for spec in DOCUMENTS:
        build(*spec)
