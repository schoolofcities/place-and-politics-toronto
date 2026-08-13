from __future__ import annotations

from pathlib import Path

from build_dimension_reduction_pdf import (
    REPORT_ROOT,
    clean_inline,
    page_footer,
    parse_markdown,
    build_styles,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_ROOT = REPO_ROOT / "output" / "pdf" / "dimension_reduction_steps"

REPORTS = [
    ("step1_full_supervised_pls.pdf", REPORT_ROOT / "task1_full_pls_summary.md"),
    ("step2_multicollinearity_diagnostics.pdf", REPORT_ROOT / "task2_multicollinearity_diagnostics.md"),
    ("step3_theory_cleaned_pls.pdf", REPORT_ROOT / "task3_theory_cleaned_pls_report.md"),
    ("step4_interaction_discovery.pdf", REPORT_ROOT / "task4_interaction_discovery_report.md"),
    ("step5a_sparse_pls.pdf", REPORT_ROOT / "task5a_sparse_pls_report.md"),
    ("step5b_supervised_pca.pdf", REPORT_ROOT / "task5b_supervised_pca_report.md"),
    ("step5c_elastic_net_robustness.pdf", REPORT_ROOT / "task5c_elastic_net_robustness_report.md"),
]


def build_one(output_name: str, source: Path) -> Path:
    styles = build_styles()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_ROOT / output_name
    doc = BaseDocTemplate(
        str(output),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=clean_inline(source.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")),
        author="Codex",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_footer)])
    story = [
        Paragraph(clean_inline(source.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")), styles["title"]),
        Spacer(1, 6),
    ]
    markdown_without_title = "\n".join(source.read_text(encoding="utf-8").splitlines()[1:])
    story.extend(parse_markdown(markdown_without_title, styles))
    doc.build(story)
    return output


def main() -> None:
    for output_name, source in REPORTS:
        build_one(output_name, source)


if __name__ == "__main__":
    main()
