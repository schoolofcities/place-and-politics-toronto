from __future__ import annotations

from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "modelling" / "processed" / "dimension_reduction" / "reports"
OUTPUT = REPO_ROOT / "output" / "pdf" / "dimension_reduction_steps_report.pdf"

REPORTS = [
    REPORT_ROOT / "task1_full_pls_summary.md",
    REPORT_ROOT / "task2_multicollinearity_diagnostics.md",
    REPORT_ROOT / "task3_theory_cleaned_pls_report.md",
    REPORT_ROOT / "task4_interaction_discovery_report.md",
    REPORT_ROOT / "task5a_sparse_pls_report.md",
    REPORT_ROOT / "task5b_supervised_pca_report.md",
    REPORT_ROOT / "task5c_elastic_net_robustness_report.md",
]


def clean_inline(text: str) -> str:
    text = text.strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_sep(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def make_table(lines: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    header = split_table_row(lines[0])
    data_lines = lines[2:] if len(lines) > 1 and is_table_sep(lines[1]) else lines[1:]
    rows = [header] + [split_table_row(line) for line in data_lines]
    max_cols = max(len(row) for row in rows)
    rows = [row + [""] * (max_cols - len(row)) for row in rows]

    processed = []
    for row_idx, row in enumerate(rows):
        style = styles["table_header"] if row_idx == 0 else styles["table_cell"]
        processed.append([Paragraph(clean_inline(cell), style) for cell in row])

    page_width = letter[0] - 1.0 * inch
    first_width = min(2.15 * inch, page_width * 0.35)
    other_width = (page_width - first_width) / max(max_cols - 1, 1)
    col_widths = [first_width] + [other_width] * (max_cols - 1)
    if max_cols <= 4:
        col_widths = [page_width / max_cols] * max_cols

    table = Table(processed, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24364b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.1),
                ("LEADING", (0, 0), (-1, -1), 8.6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f8")]),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c7ced8")),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5c6670"))
    canvas.drawString(0.5 * inch, 0.35 * inch, "Toronto turnout modelling - supervised dimension reduction")
    canvas.drawRightString(letter[0] - 0.5 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#17212f"),
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#17212f"),
            spaceBefore=8,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#2f4f6f"),
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=11.5,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            leftIndent=10,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.1,
            leading=8.6,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=8.8,
            textColor=colors.white,
        ),
    }


def parse_markdown(text: str, styles: dict[str, ParagraphStyle]) -> list:
    story = []
    lines = text.splitlines()
    i = 0
    pending_bullets: list[str] = []

    def flush_bullets():
        nonlocal pending_bullets
        if pending_bullets:
            items = [ListItem(Paragraph(clean_inline(item), styles["bullet"])) for item in pending_bullets]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=12, bulletFontSize=6))
            story.append(Spacer(1, 4))
            pending_bullets = []

    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            flush_bullets()
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
            flush_bullets()
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            story.append(make_table(table_lines, styles))
            story.append(Spacer(1, 8))
            continue
        if line.startswith("# "):
            flush_bullets()
            if story:
                story.append(PageBreak())
            story.append(Paragraph(clean_inline(line[2:]), styles["h1"]))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(clean_inline(line[3:]), styles["h2"]))
        elif line.startswith("- "):
            pending_bullets.append(line[2:])
        else:
            flush_bullets()
            story.append(Paragraph(clean_inline(line), styles["body"]))
        i += 1
    flush_bullets()
    return story


def main() -> None:
    styles = build_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="Supervised Dimension Reduction Report",
        author="Codex",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=page_footer)])

    story = [
        Paragraph("Supervised Dimension Reduction And Turnout Modelling", styles["title"]),
        Paragraph(
            "Combined PDF version of the updated Step 1 through Step 5C reports. Tables are reformatted for readability while preserving the report contents.",
            styles["body"],
        ),
        Spacer(1, 8),
    ]
    for report in REPORTS:
        story.extend(parse_markdown(report.read_text(encoding="utf-8"), styles))
    doc.build(story)


if __name__ == "__main__":
    main()
