"""Write a narrative report and simple figures for blockwise CT models."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "modelling"
MODEL_ROOT = DATA_ROOT / "processed" / "models"
FIGURE_ROOT = MODEL_ROOT / "figures"
REPORT_PATH = (
    REPO_ROOT
    / "analysis"
    / "toronto_election_turnout"
    / "modelling"
    / "docs"
    / "block_model_narrative_report.md"
)


DV_LABELS = {
    "outcome_municipal_participation_citizen_18plus": "Municipal turnout",
    "outcome_provincial_participation_citizen_18plus": "Provincial turnout",
    "outcome_federal_participation_citizen_18plus": "Federal turnout",
    "outcome_federal_minus_municipal_participation": "Federal - municipal gap",
    "outcome_mean_participation_citizen_18plus": "Mean turnout",
}

BLOCK_LABELS = {
    "block_1_demographic": "Block 1: Demographics",
    "block_2_housing_stability": "Block 2: Housing/stability",
    "block_3_immigration_eligibility": "Block 3: Immigration/eligibility",
    "block_4_competitiveness": "Block 4: Competitiveness",
}

BLOCK_COLORS = {
    "block_1_demographic": "#1f77b4",
    "block_2_housing_stability": "#8c6d31",
    "block_3_immigration_eligibility": "#2ca02c",
    "block_4_competitiveness": "#9467bd",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> float:
    return float(value) if value else 0.0


def fmt(value: str | float, digits: int = 3) -> str:
    if isinstance(value, str):
        value = number(value)
    return f"{value:.{digits}f}"


def svg_text(x: float, y: float, text: str, size: int = 12, anchor: str = "start", weight: str = "400") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#222">{text}</text>'
    )


def write_fit_heatmap(summary: list[dict[str, str]]) -> Path:
    width, height = 980, 420
    left, top = 250, 70
    cell_w, cell_h = 165, 52
    max_value = max(number(row["adjusted_r2"]) for row in summary)
    by_key = {
        (row["dependent_variable"], row["block"]): number(row["adjusted_r2"])
        for row in summary
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(24, 30, "Adjusted R2 by dependent variable and predictor block", 18, weight="700"),
    ]
    for col, block in enumerate(BLOCK_LABELS):
        lines.append(svg_text(left + col * cell_w + cell_w / 2, top - 18, BLOCK_LABELS[block].replace("Block ", "B"), 11, "middle", "700"))
    for row_i, dv in enumerate(DV_LABELS):
        y = top + row_i * cell_h
        lines.append(svg_text(24, y + 32, DV_LABELS[dv], 13, weight="700"))
        for col, block in enumerate(BLOCK_LABELS):
            value = by_key.get((dv, block), 0)
            intensity = value / max_value if max_value else 0
            blue = int(245 - 130 * intensity)
            green = int(248 - 95 * intensity)
            red = int(247 - 190 * intensity)
            x = left + col * cell_w
            lines.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 6}" height="{cell_h - 6}" '
                f'rx="4" fill="rgb({red},{green},{blue})" stroke="#d4d4d4"/>'
            )
            lines.append(svg_text(x + (cell_w - 6) / 2, y + 30, fmt(value), 15, "middle", "700"))
    lines.append(svg_text(24, height - 24, "Darker cells indicate stronger adjusted R2.", 12))
    lines.append("</svg>")
    path = FIGURE_ROOT / "adjusted_r2_heatmap.svg"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_best_block_bars(summary: list[dict[str, str]]) -> Path:
    best = []
    for dv in DV_LABELS:
        rows = [row for row in summary if row["dependent_variable"] == dv]
        best.append(max(rows, key=lambda row: number(row["adjusted_r2"])))
    width, height = 900, 420
    left, top, bar_h, gap = 245, 58, 38, 26
    max_value = max(number(row["adjusted_r2"]) for row in best)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(24, 30, "Best-fitting predictor block for each outcome", 18, weight="700"),
    ]
    for i, row in enumerate(best):
        y = top + i * (bar_h + gap)
        value = number(row["adjusted_r2"])
        bar_w = 540 * value / max_value if max_value else 0
        color = BLOCK_COLORS[row["block"]]
        lines.append(svg_text(24, y + 24, DV_LABELS[row["dependent_variable"]], 13, weight="700"))
        lines.append(f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="4" fill="{color}"/>')
        lines.append(svg_text(left + bar_w + 10, y + 24, f"{fmt(value)}  {BLOCK_LABELS[row['block']]}", 13))
    lines.append(svg_text(24, height - 24, "Bars show adjusted R2. Labels identify the strongest block.", 12))
    lines.append("</svg>")
    path = FIGURE_ROOT / "best_block_adjusted_r2.svg"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_mean_top_predictors(top_terms: list[dict[str, str]]) -> Path:
    rows = [
        row
        for row in top_terms
        if row["dependent_variable"] == "outcome_mean_participation_citizen_18plus"
        and int(row["rank"]) <= 3
    ]
    width, height = 980, 560
    left, mid, top = 360, 500, 64
    row_h = 34
    max_abs = max(abs(number(row["standardized_beta"])) for row in rows)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(24, 30, "Top predictors for mean turnout models", 18, weight="700"),
        f'<line x1="{mid}" y1="{top - 18}" x2="{mid}" y2="{height - 54}" stroke="#555"/>',
    ]
    for i, row in enumerate(rows):
        y = top + i * row_h
        beta = number(row["standardized_beta"])
        block = row["block"]
        bar_w = 255 * abs(beta) / max_abs if max_abs else 0
        x = mid - bar_w if beta < 0 else mid
        color = BLOCK_COLORS.get(block, "#666")
        label = row["term"].replace("_", " ")
        lines.append(svg_text(24, y + 20, label[:42], 12))
        lines.append(f'<rect x="{x:.1f}" y="{y}" width="{bar_w:.1f}" height="22" rx="3" fill="{color}"/>')
        value_x = x - 8 if beta < 0 else x + bar_w + 8
        anchor = "end" if beta < 0 else "start"
        lines.append(svg_text(value_x, y + 16, fmt(beta), 12, anchor, "700"))
    lines.append(svg_text(24, height - 24, "Standardized betas. Negative values predict lower mean turnout.", 12))
    lines.append("</svg>")
    path = FIGURE_ROOT / "mean_turnout_top_predictors.svg"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def model_fit_table(summary: list[dict[str, str]]) -> list[str]:
    lines = [
        "| Outcome | Block 1 demographics | Block 2 housing | Block 3 immigration | Block 4 competitiveness |",
        "|---|---:|---:|---:|---:|",
    ]
    by_key = {
        (row["dependent_variable"], row["block"]): row
        for row in summary
    }
    for dv in DV_LABELS:
        values = [fmt(by_key[(dv, block)]["adjusted_r2"]) for block in BLOCK_LABELS]
        lines.append(f"| {DV_LABELS[dv]} | " + " | ".join(values) + " |")
    return lines


def top_predictor_table(top_terms: list[dict[str, str]], dependent: str) -> list[str]:
    rows = [
        row
        for row in top_terms
        if row["dependent_variable"] == dependent and int(row["rank"]) <= 3
    ]
    lines = [
        "| Block | Predictor | Std. beta | Direction |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        beta = number(row["standardized_beta"])
        direction = "higher turnout" if beta > 0 else "lower turnout"
        lines.append(
            f"| {BLOCK_LABELS[row['block']]} | `{row['term']}` | {fmt(beta)} | {direction} |"
        )
    return lines


def write_report(summary: list[dict[str, str]], top_terms: list[dict[str, str]], figures: list[Path]) -> None:
    lines = [
        "# CT Turnout Models: Narrative Report",
        "",
        "This report summarizes the first blockwise modelling pass for Toronto CT-level turnout.",
        "The models use the clean curated CT dataset and include only Blocks 1-4 because Blocks",
        "5-6 still require additional official service/campaign data.",
        "",
        "The dependent variables are municipal, provincial, federal, federal-minus-municipal,",
        "and mean participation. All turnout outcomes use the Census citizen-adult denominator",
        "rather than registered-elector denominators.",
        "",
        "## Figure 1. Model Fit",
        "",
        f"![Adjusted R2 heatmap](../../../../data/toronto_election_turnout/modelling/processed/models/figures/{figures[0].name})",
        "",
        "Adjusted R2 by outcome and block:",
        "",
        *model_fit_table(summary),
        "",
        "The first result is hard to miss: demographic composition is the strongest block for",
        "municipal, provincial, federal, and mean turnout. This is especially pronounced for",
        "municipal turnout, where Block 1 reaches an adjusted R2 of 0.604. Mean turnout is",
        "similar, with Block 1 at 0.551. Housing is consistently the weakest of the four blocks",
        "for direct turnout levels.",
        "",
        "## Figure 2. Best Block By Outcome",
        "",
        f"![Best block bars](../../../../data/toronto_election_turnout/modelling/processed/models/figures/{figures[1].name})",
        "",
        "The federal-minus-municipal gap is the exception. Its best block is not demographics;",
        "it is Block 3, immigration/citizenship/eligibility, with adjusted R2 of 0.270. That",
        "suggests that the geography of municipal drop-off is not simply about high-turnout",
        "versus low-turnout places. It appears tied to places where federal participation",
        "remains comparatively high while municipal participation falls away.",
        "",
        "## Figure 3. Mean Turnout Predictors",
        "",
        f"![Mean turnout top predictors](../../../../data/toronto_election_turnout/modelling/processed/models/figures/{figures[2].name})",
        "",
        "Across the mean-turnout models, the most consistent negative predictors are larger",
        "household size, young-adult share, visible-minority share, non-citizen share, and",
        "mayoral electoral fragmentation. Bachelor-plus share is the clearest positive",
        "demographic predictor.",
        "",
        "Top predictors for mean turnout:",
        "",
        *top_predictor_table(top_terms, "outcome_mean_participation_citizen_18plus"),
        "",
        "## What Stands Out",
        "",
        "### 1. Municipal turnout is the most socially structured outcome",
        "",
        "Municipal turnout is explained unusually well by basic demographic and immigration",
        "variables. Block 1 adjusted R2 is 0.604 and Block 3 adjusted R2 is 0.549. In practical",
        "terms, this means the municipal electorate varies sharply across CT social geography.",
        "Places with higher young-adult share, larger household size, lower income, lower",
        "bachelor-plus share, and higher racialized/immigrant shares tend to have lower municipal",
        "participation.",
        "",
        "### 2. Federal turnout is higher, but less tightly explained",
        "",
        "Federal participation is much higher on average, but the block fits are weaker. Block 1",
        "still leads with adjusted R2 of 0.349, but that is far below the municipal model. This",
        "supports a narrative where federal elections activate more people across the city, but",
        "do not erase the underlying turnout gradient.",
        "",
        "### 3. The municipal drop-off story is about immigration/citizenship geography",
        "",
        "For federal-minus-municipal participation, Block 3 is strongest. The top terms include",
        "non-citizen share, recent immigrant share, citizen-adult share, immigrant share, and",
        "English/French knowledge. This is promising because it points toward a sharper research",
        "question: which communities participate federally but are not being mobilized municipally?",
        "",
        "### 4. Competitiveness is meaningful but should be handled carefully",
        "",
        "Block 4 performs well for municipal and mean turnout. The effective number of mayoral",
        "candidates above 5% is strongly negative across several outcomes. This probably means",
        "that fragmented mayoral vote geographies overlap with lower-turnout social geography.",
        "It is interesting, but not yet causal: competitiveness is computed from the same vote",
        "data we are trying to explain.",
        "",
        "### 5. Housing variables need a reduced specification",
        "",
        "The housing block has the weakest overall fit and shows signs of collinearity. Renter",
        "share and owner share are mechanically related, and apartment/condo/density are also",
        "tightly coupled. The next modelling pass should reduce this block to a smaller set,",
        "such as renter share, condo share, apartment share, same-address-five-years share, and",
        "density.",
        "",
        "## Suggested Next Story",
        "",
        "The strongest narrative is: **Toronto municipal turnout is not just lower than federal",
        "turnout; it is more socially selective.** The places most likely to disappear municipally",
        "are not random low-turnout places. They appear to be structured by age, household form,",
        "education, racialized/immigrant geography, and citizenship-related context.",
        "",
        "A strong next model would be a combined reduced model for mean turnout and municipal",
        "drop-off, using a small non-collinear set of predictors from Blocks 1-4, then adding",
        "Block 5 service-contact variables once we finish the Open Toronto data build.",
        "",
        "## Caveats",
        "",
        "- This is exploratory OLS, not a final causal model.",
        "- P-values are normal approximations from the local pure-Python implementation.",
        "- Spatial autocorrelation and robust standard errors are not yet included.",
        "- Several predictors are compositionally related, so multicollinearity needs to be checked.",
        "- Turnout uses Census citizen-adult denominators, not official registered-elector denominators.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    FIGURE_ROOT.mkdir(parents=True, exist_ok=True)
    summary = read_csv(MODEL_ROOT / "block_model_summary.csv")
    top_terms = read_csv(MODEL_ROOT / "block_model_top_predictors.csv")
    figures = [
        write_fit_heatmap(summary),
        write_best_block_bars(summary),
        write_mean_top_predictors(top_terms),
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_report(summary, top_terms, figures)
    print(f"Wrote narrative report to {REPORT_PATH}")
    for figure in figures:
        print(f"Wrote figure {figure}")


if __name__ == "__main__":
    main()
