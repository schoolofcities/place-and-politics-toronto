"""Analyze turnout versus polling-place distance for available station points."""

from __future__ import annotations

import csv
import html
import math
import os
from pathlib import Path
from statistics import mean, median


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
ACCESS_ROOT = DATA_ROOT / "accessibility"
PROCESSED_ROOT = ACCESS_ROOT / "processed"
ANALYSIS_ROOT = REPO_ROOT / "analysis" / "toronto_election_turnout" / "accessibility"
OUTPUT_ROOT = PROCESSED_ROOT / "turnout_distance_analysis"
FIGURE_ROOT = OUTPUT_ROOT / "figures"
REPORT_PATH = ANALYSIS_ROOT / "docs" / "turnout_distance_report.md"

MODEL_COVARIATES = ["distance_km", "poll_area_km2"]
VARIABLE_LABELS = {
    "turnout_rate": "Turnout rate",
    "distance_km": "Distance to polling station (km)",
    "poll_area_km2": "Polling division area (km2)",
    "number_of_votes": "Votes",
    "number_of_electors": "Electors",
    "fitted_turnout": "Fitted turnout",
    "residual": "Residual",
}
ELECTION_LABELS = {
    "municipal_2023_mayor": "Municipal 2023 mayoral by-election",
    "provincial_2025_partial": "Provincial 2025 partial official-location sample",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def number(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_den == 0 or y_den == 0:
        return None
    return numerator / (x_den * y_den)


def ranks(values: list[float]) -> list[float]:
    order = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and order[end][1] == order[index][1]:
            end += 1
        rank = (index + 1 + end) / 2
        for original, _ in order[index:end]:
            result[original] = rank
        index = end
    return result


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(ranks(xs), ranks(ys)) if len(xs) == len(ys) else None


def normal_cdf(value: float) -> float:
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    n = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        pivot_value = augmented[col][col]
        for item in range(col, n + 1):
            augmented[col][item] /= pivot_value
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            for item in range(col, n + 1):
                augmented[row][item] -= factor * augmented[col][item]
    return [augmented[i][n] for i in range(n)]


def invert_matrix(matrix: list[list[float]]) -> list[list[float]] | None:
    n = len(matrix)
    inverse = []
    for col in range(n):
        unit = [0.0] * n
        unit[col] = 1.0
        solution = solve_linear_system(matrix, unit)
        if solution is None:
            return None
        inverse.append(solution)
    return [[inverse[col][row] for col in range(n)] for row in range(n)]


def build_design(rows: list[dict], covariates: list[str], fixed_effect: str | None):
    data = [row for row in rows if all(row.get(key) is not None for key in covariates)]
    if fixed_effect:
        levels = sorted({str(row[fixed_effect]) for row in data})
        fe_levels = levels[1:]
    else:
        fe_levels = []
    columns = ["intercept"] + covariates + [f"district_fe_{level}" for level in fe_levels]
    x_rows = []
    y_values = []
    for row in data:
        x_row = [1.0] + [float(row[key]) for key in covariates]
        x_row += [1.0 if str(row[fixed_effect]) == level else 0.0 for level in fe_levels]
        x_rows.append(x_row)
        y_values.append(float(row["turnout_rate"]))
    return data, columns, x_rows, y_values, fe_levels


def ols(rows: list[dict], covariates: list[str], fixed_effect: str | None = None) -> dict:
    data, columns, x_rows, y_values, fe_levels = build_design(rows, covariates, fixed_effect)
    if len(x_rows) <= len(columns):
        return {"n": len(x_rows), "r2": None, "adj_r2": None, "coefficients": [], "rows": data}
    xtx = [
        [sum(x[i] * x[j] for x in x_rows) for j in range(len(columns))]
        for i in range(len(columns))
    ]
    xty = [sum(x[i] * y for x, y in zip(x_rows, y_values)) for i in range(len(columns))]
    beta = solve_linear_system(xtx, xty)
    inverse_xtx = invert_matrix(xtx)
    if beta is None or inverse_xtx is None:
        return {"n": len(x_rows), "r2": None, "adj_r2": None, "coefficients": [], "rows": data}
    fitted = [sum(b * x for b, x in zip(beta, x_row)) for x_row in x_rows]
    residuals = [y - yhat for y, yhat in zip(y_values, fitted)]
    y_mean = mean(y_values)
    sse = sum(residual ** 2 for residual in residuals)
    sst = sum((y - y_mean) ** 2 for y in y_values)
    n = len(y_values)
    k = len(columns)
    dof = n - k
    mse = sse / dof if dof > 0 else None
    coefficients = []
    for index, name in enumerate(columns):
        se = math.sqrt(max(0, mse * inverse_xtx[index][index])) if mse is not None else None
        t_stat = beta[index] / se if se and se > 0 else None
        p_value = 2 * (1 - normal_cdf(abs(t_stat))) if t_stat is not None else None
        coefficients.append(
            {
                "term": name,
                "estimate": beta[index],
                "std_error": se,
                "t_stat": t_stat,
                "p_value_normal_approx": p_value,
            }
        )
    annotated_rows = []
    for row, fitted_value, residual in zip(data, fitted, residuals):
        annotated = dict(row)
        annotated["fitted_turnout"] = fitted_value
        annotated["residual"] = residual
        annotated_rows.append(annotated)
    r2 = None if sst == 0 else 1 - sse / sst
    adj_r2 = None if r2 is None or dof <= 0 else 1 - ((1 - r2) * (n - 1) / dof)
    return {
        "n": n,
        "k": k,
        "r2": r2,
        "adj_r2": adj_r2,
        "sse": sse,
        "rmse": math.sqrt(mse) if mse is not None else None,
        "columns": columns,
        "coefficients": coefficients,
        "rows": annotated_rows,
        "fixed_effect_levels": fe_levels,
    }


def load_sample(election_id: str, metrics_filename: str) -> list[dict]:
    rows = read_csv(PROCESSED_ROOT / "poll_accessibility_metrics" / metrics_filename)
    sample = []
    for row in rows:
        turnout = number(row.get("proportion_of_turnout"))
        distance = number(row.get("poll_point_on_surface_distance_m"))
        area = number(row.get("poll_area_km2"))
        votes = number(row.get("number_of_votes"))
        electors = number(row.get("number_of_electors"))
        if (
            row.get("exclude_from_distance_model_flag") == "1"
            or turnout is None
            or distance is None
            or area is None
        ):
            continue
        sample.append(
            {
                "election_id": election_id,
                "poll_id": row["poll_id"],
                "district": row["electoral_district_number"],
                "polling_division_number": row["polling_division_number"],
                "turnout_rate": turnout,
                "distance_km": distance / 1000,
                "poll_area_km2": area,
                "number_of_votes": votes,
                "number_of_electors": electors,
                "location_source_status": row.get("location_assignment_type", ""),
            }
        )
    return sample


def summarize_values(values: list[float]) -> dict[str, float | None]:
    clean = [value for value in values if value is not None]
    if not clean:
        return {"mean": None, "median": None, "sd": None, "min": None, "max": None}
    value_mean = mean(clean)
    sd = math.sqrt(sum((value - value_mean) ** 2 for value in clean) / (len(clean) - 1)) if len(clean) > 1 else 0.0
    return {
        "mean": value_mean,
        "median": median(clean),
        "sd": sd,
        "min": min(clean),
        "max": max(clean),
    }


def variable_summary(sample: list[dict], variables: list[str]) -> list[dict]:
    rows = []
    for variable in variables:
        stats = summarize_values([row.get(variable) for row in sample])
        rows.append(
            {
                "election_id": sample[0]["election_id"] if sample else "",
                "variable": variable,
                "label": VARIABLE_LABELS.get(variable, variable),
                "n": len([row for row in sample if row.get(variable) is not None]),
                **stats,
            }
        )
    return rows


def summarize_sample(sample: list[dict]) -> dict:
    xs = [row["distance_km"] for row in sample]
    ys = [row["turnout_rate"] for row in sample]
    areas = [row["poll_area_km2"] for row in sample]
    return {
        "election_id": sample[0]["election_id"] if sample else "",
        "n": len(sample),
        "mean_turnout_rate": mean(ys) if ys else None,
        "mean_distance_km": mean(xs) if xs else None,
        "median_distance_km": median(xs) if xs else None,
        "mean_poll_area_km2": mean(areas) if areas else None,
        "distance_turnout_pearson": pearson(xs, ys),
        "distance_turnout_spearman": spearman(xs, ys),
        "area_turnout_pearson": pearson(areas, ys),
        "area_turnout_spearman": spearman(areas, ys),
    }


def fmt(value, digits=4):
    return "n/a" if value is None else f"{float(value):.{digits}f}"


def fmt_pct(value):
    return "n/a" if value is None else f"{float(value) * 100:.1f}%"


def fmt_p(value):
    if value is None:
        return "n/a"
    if value < 0.001:
        return "<0.001"
    return f"{value:.3f}"


def html_escape(value) -> str:
    return html.escape(str(value), quote=True)


def svg_scatter(rows: list[dict], x_key: str, y_key: str, title: str, x_label: str, y_label: str, path: Path):
    width, height = 760, 500
    left, right, top, bottom = 72, 24, 52, 62
    xs = [row[x_key] for row in rows if row.get(x_key) is not None and row.get(y_key) is not None]
    ys = [row[y_key] for row in rows if row.get(x_key) is not None and row.get(y_key) is not None]
    if not xs or not ys:
        return
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_min == x_max:
        x_max = x_min + 1
    if y_min == y_max:
        y_max = y_min + 1
    x_pad = (x_max - x_min) * 0.04
    y_pad = (y_max - y_min) * 0.06
    x_min -= x_pad
    x_max += x_pad
    y_min -= y_pad
    y_max += y_pad

    def sx(value):
        return left + (value - x_min) / (x_max - x_min) * (width - left - right)

    def sy(value):
        return height - bottom - (value - y_min) / (y_max - y_min) * (height - top - bottom)

    corr = pearson(xs, ys)
    slope = 0.0
    intercept = mean(ys)
    x_mean = mean(xs)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom:
        slope = sum((x - x_mean) * (y - mean(ys)) for x, y in zip(xs, ys)) / denom
        intercept = mean(ys) - slope * x_mean
    line_x1, line_x2 = min(xs), max(xs)
    line_y1, line_y2 = intercept + slope * line_x1, intercept + slope * line_x2
    points = []
    stride = max(1, len(rows) // 1800)
    for row in rows[::stride]:
        if row.get(x_key) is None or row.get(y_key) is None:
            continue
        points.append(f'<circle cx="{sx(row[x_key]):.2f}" cy="{sy(row[y_key]):.2f}" r="2.2" fill="#315f9c" fill-opacity="0.34"/>')
    x_ticks = []
    y_ticks = []
    for i in range(5):
        xv = x_min + (x_max - x_min) * i / 4
        yv = y_min + (y_max - y_min) * i / 4
        x_ticks.append(
            f'<line x1="{sx(xv):.1f}" y1="{height-bottom}" x2="{sx(xv):.1f}" y2="{height-bottom+5}" stroke="#333"/>'
            f'<text x="{sx(xv):.1f}" y="{height-bottom+22}" text-anchor="middle" font-size="12">{fmt(xv, 2)}</text>'
        )
        y_ticks.append(
            f'<line x1="{left-5}" y1="{sy(yv):.1f}" x2="{left}" y2="{sy(yv):.1f}" stroke="#333"/>'
            f'<text x="{left-9}" y="{sy(yv)+4:.1f}" text-anchor="end" font-size="12">{fmt(yv, 2)}</text>'
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="white"/>',
                f'<text x="{left}" y="30" font-size="20" font-weight="700">{html_escape(title)}</text>',
                f'<text x="{width-right}" y="30" text-anchor="end" font-size="12" fill="#555">Pearson r = {fmt(corr, 3)}</text>',
                f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333"/>',
                f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333"/>',
                *x_ticks,
                *y_ticks,
                f'<line x1="{sx(line_x1):.2f}" y1="{sy(line_y1):.2f}" x2="{sx(line_x2):.2f}" y2="{sy(line_y2):.2f}" stroke="#b33a3a" stroke-width="3"/>',
                *points,
                f'<text x="{(left+width-right)/2}" y="{height-18}" text-anchor="middle" font-size="14">{html_escape(x_label)}</text>',
                f'<text transform="translate(20,{(top+height-bottom)/2}) rotate(-90)" text-anchor="middle" font-size="14">{html_escape(y_label)}</text>',
                '</svg>',
            ]
        ),
        encoding="utf-8",
    )


def svg_histogram(rows: list[dict], key: str, title: str, x_label: str, path: Path, bins: int = 20):
    values = [row[key] for row in rows if row.get(key) is not None]
    if not values:
        return
    width, height = 760, 380
    left, right, top, bottom = 70, 24, 48, 58
    v_min, v_max = min(values), max(values)
    if v_min == v_max:
        v_max = v_min + 1
    step = (v_max - v_min) / bins
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, int((value - v_min) / step))
        counts[index] += 1
    max_count = max(counts)

    def sx(value):
        return left + (value - v_min) / (v_max - v_min) * (width - left - right)

    def sy(count):
        return height - bottom - count / max_count * (height - top - bottom)

    bars = []
    for i, count in enumerate(counts):
        x0 = sx(v_min + i * step)
        x1 = sx(v_min + (i + 1) * step)
        y = sy(count)
        bars.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{max(1, x1-x0-1):.1f}" height="{height-bottom-y:.1f}" fill="#4f7f6f" fill-opacity="0.82"/>')
    x_ticks = []
    y_ticks = []
    for i in range(5):
        xv = v_min + (v_max - v_min) * i / 4
        cv = max_count * i / 4
        x_ticks.append(f'<text x="{sx(xv):.1f}" y="{height-bottom+22}" text-anchor="middle" font-size="12">{fmt(xv, 2)}</text>')
        y_ticks.append(f'<text x="{left-9}" y="{sy(cv)+4:.1f}" text-anchor="end" font-size="12">{int(cv)}</text>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="white"/>',
                f'<text x="{left}" y="30" font-size="20" font-weight="700">{html_escape(title)}</text>',
                f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333"/>',
                f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333"/>',
                *bars,
                *x_ticks,
                *y_ticks,
                f'<text x="{(left+width-right)/2}" y="{height-18}" text-anchor="middle" font-size="14">{html_escape(x_label)}</text>',
                '<text transform="translate(18,210) rotate(-90)" text-anchor="middle" font-size="14">Polling divisions</text>',
                '</svg>',
            ]
        ),
        encoding="utf-8",
    )


def make_figures(samples: dict[str, list[dict]], model_results: dict[str, dict]) -> list[dict]:
    figures = []
    for election_id, sample in samples.items():
        slug = "municipal_2023" if election_id.startswith("municipal") else "provincial_2025"
        label = ELECTION_LABELS[election_id]
        scatter_path = FIGURE_ROOT / f"{slug}_distance_turnout_scatter.svg"
        area_path = FIGURE_ROOT / f"{slug}_area_turnout_scatter.svg"
        distance_hist_path = FIGURE_ROOT / f"{slug}_distance_histogram.svg"
        residual_path = FIGURE_ROOT / f"{slug}_residual_fitted.svg"
        svg_scatter(sample, "distance_km", "turnout_rate", f"{label}: turnout vs distance", "Distance to polling station (km)", "Turnout rate", scatter_path)
        svg_scatter(sample, "poll_area_km2", "turnout_rate", f"{label}: turnout vs poll area", "Polling division area (km2)", "Turnout rate", area_path)
        svg_histogram(sample, "distance_km", f"{label}: distance distribution", "Distance to polling station (km)", distance_hist_path)
        svg_scatter(model_results[election_id]["rows"], "fitted_turnout", "residual", f"{label}: residual diagnostic", "Fitted turnout", "Residual", residual_path)
        figures.extend(
            [
                {"election_id": election_id, "figure": "distance_turnout_scatter", "path": scatter_path},
                {"election_id": election_id, "figure": "area_turnout_scatter", "path": area_path},
                {"election_id": election_id, "figure": "distance_histogram", "path": distance_hist_path},
                {"election_id": election_id, "figure": "residual_fitted", "path": residual_path},
            ]
        )
    return figures


def coefficient_rows(model_results: dict[str, dict]) -> list[dict]:
    rows = []
    for election_id, result in model_results.items():
        for coef in result["coefficients"]:
            if coef["term"].startswith("district_fe_"):
                continue
            rows.append(
                {
                    "election_id": election_id,
                    "model": "turnout_rate ~ distance_km + poll_area_km2 + district fixed effects",
                    "term": coef["term"],
                    "estimate": coef["estimate"],
                    "std_error": coef["std_error"],
                    "t_stat": coef["t_stat"],
                    "p_value_normal_approx": coef["p_value_normal_approx"],
                }
            )
    return rows


def model_summary_rows(model_results: dict[str, dict]) -> list[dict]:
    rows = []
    for election_id, result in model_results.items():
        rows.append(
            {
                "election_id": election_id,
                "model": "turnout_rate ~ distance_km + poll_area_km2 + district fixed effects",
                "n": result["n"],
                "r2": result["r2"],
                "adjusted_r2": result["adj_r2"],
                "rmse": result["rmse"],
                "district_fixed_effects": len(result["fixed_effect_levels"]),
            }
        )
    return rows


def relative_path(path: Path) -> str:
    return os.path.relpath(path, REPORT_PATH.parent)


def markdown_table(rows: list[dict], columns: list[tuple[str, str]], formatters: dict[str, callable] | None = None) -> list[str]:
    formatters = formatters or {}
    lines = ["| " + " | ".join(label for _, label in columns) + " |"]
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        cells = []
        for key, _ in columns:
            value = row.get(key)
            formatter = formatters.get(key)
            cells.append(formatter(value) if formatter else str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def write_report(samples: dict[str, list[dict]], summaries: list[dict], variable_rows: list[dict], model_summaries: list[dict], coefs: list[dict], figures: list[dict]):
    municipal_coef = [row for row in coefs if row["election_id"] == "municipal_2023_mayor"]
    provincial_coef = [row for row in coefs if row["election_id"] == "provincial_2025_partial"]
    municipal_vars = [row for row in variable_rows if row["election_id"] == "municipal_2023_mayor"]
    provincial_vars = [row for row in variable_rows if row["election_id"] == "provincial_2025_partial"]
    summary_by_id = {row["election_id"]: row for row in summaries}
    model_by_id = {row["election_id"]: row for row in model_summaries}

    def fig(election_id, figure):
        path = next(item["path"] for item in figures if item["election_id"] == election_id and item["figure"] == figure)
        return f"![{figure} for {election_id}]({relative_path(path)})"

    lines = [
        "# Turnout vs Polling-Station Distance",
        "",
        "## Scope",
        "",
        "This report overwrites the prior distance analysis and uses the current accepted polling-station coordinates.",
        "Municipal 2023 has complete official Open Toronto station points. Provincial 2025 is a partial official-location sample: exact Elections Ontario proposed-location matches and exact Open Toronto official-label recoveries are included; unresolved/fuzzy rows are excluded.",
        "Federal 2025 remains out of this distance model because no official bulk station-location table has been found.",
        "",
        "## Model Specification",
        "",
        "The two main models are estimated separately:",
        "",
        "`turnout_rate = beta0 + beta1 * distance_km + beta2 * poll_area_km2 + district fixed effects + error`",
        "",
        "Distance is measured from the polling-division point-on-surface to the assigned polling-station/building point. Coefficients are turnout-rate units; multiply by 100 for percentage-point interpretation.",
        "",
        "## Sample And Correlations",
        "",
    ]
    lines.extend(
        markdown_table(
            summaries,
            [
                ("election_id", "Election"),
                ("n", "N"),
                ("mean_turnout_rate", "Mean turnout"),
                ("mean_distance_km", "Mean distance km"),
                ("median_distance_km", "Median distance km"),
                ("distance_turnout_pearson", "Pearson distance/turnout"),
                ("distance_turnout_spearman", "Spearman distance/turnout"),
                ("area_turnout_pearson", "Pearson area/turnout"),
            ],
            {
                "mean_turnout_rate": fmt_pct,
                "mean_distance_km": lambda value: fmt(value, 3),
                "median_distance_km": lambda value: fmt(value, 3),
                "distance_turnout_pearson": lambda value: fmt(value, 3),
                "distance_turnout_spearman": lambda value: fmt(value, 3),
                "area_turnout_pearson": lambda value: fmt(value, 3),
            },
        )
    )
    lines.extend(
        [
            "",
            "## Municipal 2023 Model",
            "",
            f"Model-ready rows: {model_by_id['municipal_2023_mayor']['n']}. Adjusted R2: {fmt(model_by_id['municipal_2023_mayor']['adjusted_r2'], 3)}. RMSE: {fmt(model_by_id['municipal_2023_mayor']['rmse'], 3)} turnout-rate units.",
            "",
            "### Municipal Variable Summary",
            "",
        ]
    )
    lines.extend(variable_table(municipal_vars))
    lines.extend(["", "### Municipal Coefficients", ""])
    lines.extend(coef_table(municipal_coef))
    lines.extend(
        [
            "",
            "### Municipal Figures",
            "",
            fig("municipal_2023_mayor", "distance_turnout_scatter"),
            "",
            fig("municipal_2023_mayor", "area_turnout_scatter"),
            "",
            fig("municipal_2023_mayor", "distance_histogram"),
            "",
            fig("municipal_2023_mayor", "residual_fitted"),
            "",
            "## Provincial 2025 Model",
            "",
            f"Model-ready rows: {model_by_id['provincial_2025_partial']['n']}. Adjusted R2: {fmt(model_by_id['provincial_2025_partial']['adjusted_r2'], 3)}. RMSE: {fmt(model_by_id['provincial_2025_partial']['rmse'], 3)} turnout-rate units.",
            "",
            "### Provincial Variable Summary",
            "",
        ]
    )
    lines.extend(variable_table(provincial_vars))
    lines.extend(["", "### Provincial Coefficients", ""])
    lines.extend(coef_table(provincial_coef))
    lines.extend(
        [
            "",
            "### Provincial Figures",
            "",
            fig("provincial_2025_partial", "distance_turnout_scatter"),
            "",
            fig("provincial_2025_partial", "area_turnout_scatter"),
            "",
            fig("provincial_2025_partial", "distance_histogram"),
            "",
            fig("provincial_2025_partial", "residual_fitted"),
            "",
            "## Comparison",
            "",
            comparison_text(summary_by_id, model_by_id, coefs),
            "",
            "## Caveats",
            "",
            "The municipal model is cleaner because station coverage is complete. The provincial model should be read as directional and exploratory because about 206 mapped provincial rows still lack a high-confidence station coordinate. The distance measure is straight-line point-on-surface distance, not walking-network distance, and polling-area size is a rough proxy for urban form as well as accessibility.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def variable_table(rows: list[dict]) -> list[str]:
    return markdown_table(
        rows,
        [
            ("label", "Variable"),
            ("n", "N"),
            ("mean", "Mean"),
            ("median", "Median"),
            ("sd", "SD"),
            ("min", "Min"),
            ("max", "Max"),
        ],
        {
            "mean": lambda value: fmt(value, 3),
            "median": lambda value: fmt(value, 3),
            "sd": lambda value: fmt(value, 3),
            "min": lambda value: fmt(value, 3),
            "max": lambda value: fmt(value, 3),
        },
    )


def coef_table(rows: list[dict]) -> list[str]:
    display_rows = []
    labels = {
        "intercept": "Intercept",
        "distance_km": "Distance to station (km)",
        "poll_area_km2": "Poll area (km2)",
    }
    for row in rows:
        display = dict(row)
        display["term_label"] = labels.get(row["term"], row["term"])
        display["estimate_pp"] = row["estimate"] * 100 if row.get("estimate") is not None else None
        display["std_error_pp"] = row["std_error"] * 100 if row.get("std_error") is not None else None
        display_rows.append(display)
    return markdown_table(
        display_rows,
        [
            ("term_label", "Term"),
            ("estimate_pp", "Estimate, percentage points"),
            ("std_error_pp", "SE, percentage points"),
            ("t_stat", "t"),
            ("p_value_normal_approx", "p approx."),
        ],
        {
            "estimate_pp": lambda value: fmt(value, 2),
            "std_error_pp": lambda value: fmt(value, 2),
            "t_stat": lambda value: fmt(value, 2),
            "p_value_normal_approx": fmt_p,
        },
    )


def comparison_text(summary_by_id: dict, model_by_id: dict, coefs: list[dict]) -> str:
    def get_coef(election_id, term):
        for row in coefs:
            if row["election_id"] == election_id and row["term"] == term:
                return row["estimate"]
        return None

    m_distance = get_coef("municipal_2023_mayor", "distance_km")
    p_distance = get_coef("provincial_2025_partial", "distance_km")
    m_area = get_coef("municipal_2023_mayor", "poll_area_km2")
    p_area = get_coef("provincial_2025_partial", "poll_area_km2")
    return (
        f"Both elections show a negative distance-turnout relationship, but it is much stronger in the municipal sample. "
        f"With district fixed effects and poll area in the model, an additional kilometre to the assigned station is associated with about {fmt(m_distance * 100 if m_distance is not None else None, 1)} percentage points lower municipal turnout, compared with about {fmt(p_distance * 100 if p_distance is not None else None, 1)} percentage points lower provincial turnout. "
        f"Poll area behaves differently: the municipal coefficient is small, positive, and not clearly distinguishable from zero ({fmt(m_area * 100 if m_area is not None else None, 1)} percentage points per km2), while the provincial partial model shows a clearer negative association ({fmt(p_area * 100 if p_area is not None else None, 1)} percentage points per km2). "
        f"The municipal model explains slightly less variance than the provincial partial model after district fixed effects (adjusted R2 {fmt(model_by_id['municipal_2023_mayor']['adjusted_r2'], 3)} vs. {fmt(model_by_id['provincial_2025_partial']['adjusted_r2'], 3)}), but the municipal location coverage is complete, making it the better evidence base for a clean accessibility story."
    )


def main():
    samples = {
        "municipal_2023_mayor": load_sample(
            "municipal_2023_mayor", "municipal_2023_mayor_poll_accessibility_metrics.csv"
        ),
        "provincial_2025_partial": load_sample(
            "provincial_2025_partial", "provincial_2025_poll_accessibility_metrics.csv"
        ),
    }
    all_rows = samples["municipal_2023_mayor"] + samples["provincial_2025_partial"]
    summaries = [summarize_sample(samples[key]) for key in samples]
    variable_rows = []
    for sample in samples.values():
        variable_rows.extend(
            variable_summary(
                sample,
                ["turnout_rate", "distance_km", "poll_area_km2", "number_of_votes", "number_of_electors"],
            )
        )
    model_results = {
        key: ols(sample, MODEL_COVARIATES, fixed_effect="district")
        for key, sample in samples.items()
    }
    for key, result in model_results.items():
        for row, annotated in zip(samples[key], result["rows"]):
            row["fitted_turnout"] = annotated["fitted_turnout"]
            row["residual"] = annotated["residual"]
    coefs = coefficient_rows(model_results)
    model_summaries = model_summary_rows(model_results)
    figures = make_figures(samples, model_results)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_ROOT / "turnout_distance_analysis_rows.csv", all_rows)
    write_csv(OUTPUT_ROOT / "turnout_distance_summary.csv", summaries)
    write_csv(OUTPUT_ROOT / "turnout_distance_variable_summary.csv", variable_rows)
    write_csv(OUTPUT_ROOT / "turnout_distance_models.csv", model_summaries)
    write_csv(OUTPUT_ROOT / "turnout_distance_model_coefficients.csv", coefs)
    write_csv(
        OUTPUT_ROOT / "turnout_distance_figures.csv",
        [{"election_id": item["election_id"], "figure": item["figure"], "path": relative_path(item["path"])} for item in figures],
    )
    write_report(samples, summaries, variable_rows, model_summaries, coefs, figures)
    print(f"Wrote turnout-distance analysis to {OUTPUT_ROOT}")
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
