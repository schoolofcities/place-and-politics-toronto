"""Run blockwise CT turnout models.

The modelling design is 5 dependent variables x 4 predictor blocks = 20 OLS
models. This script intentionally uses the curated modelling table, not the
verbose provenance table.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from math import erf, isfinite, sqrt
from pathlib import Path
from statistics import mean


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "modelling"
PROCESSED_ROOT = DATA_ROOT / "processed"
OUTPUT_ROOT = PROCESSED_ROOT / "models"
ANALYSIS_ROOT = REPO_ROOT / "analysis" / "toronto_election_turnout" / "modelling"
REPORT_PATH = ANALYSIS_ROOT / "docs" / "block_model_results.md"
INPUT = PROCESSED_ROOT / "toronto_ct_modelling_curated.csv"


DEPENDENT_VARIABLES = {
    "A_municipal_turnout": "outcome_municipal_participation_citizen_18plus",
    "B_provincial_turnout": "outcome_provincial_participation_citizen_18plus",
    "C_federal_turnout": "outcome_federal_participation_citizen_18plus",
    "D_federal_minus_municipal": "outcome_federal_minus_municipal_participation",
    "E_mean_turnout": "outcome_mean_participation_citizen_18plus",
}


BLOCKS = {
    "block_1_demographic": [
        "dem_share_18_34",
        "dem_share_35_64",
        "dem_share_65_plus",
        "dem_median_age",
        "dem_average_household_size",
        "dem_bachelors_plus_share",
        "dem_low_income_share",
        "dem_unemployment_rate",
    ],
    "block_2_housing_stability": [
        "housing_renter_share",
        "housing_owner_share",
        "housing_recent_mover_share",
        "housing_same_address_1yr_share",
        "housing_same_address_5yr_share",
        "housing_condo_share",
        "housing_apartment_share",
        "housing_detached_semi_share",
        "housing_population_density_per_km2",
    ],
    "block_3_immigration_eligibility": [
        "immigration_immigrant_share",
        "immigration_recent_immigrant_share",
        "immigration_non_citizen_share",
        "eligibility_citizen_adult_share",
        "racialized_visible_minority_share",
        "language_english_french_knowledge_share",
        "language_non_official_mother_tongue_share",
    ],
    "block_4_competitiveness": [
        "election_mayoral_top_two_margin",
        "election_effective_mayoral_candidates_5pct",
        "election_mayoral_vote_fragmentation",
        "election_federal_margin",
        "election_provincial_margin",
        "election_effective_federal_parties_5pct",
        "election_effective_provincial_parties_5pct",
    ],
}


@dataclass
class FitResult:
    model_id: str
    dependent_variable: str
    block: str
    n: int
    k: int
    r2: float | None
    adjusted_r2: float | None
    rmse: float | None
    coefficients: list[dict]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def number(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if isfinite(parsed) else None


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*matrix)]


def matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    right_t = transpose(right)
    return [[sum(a * b for a, b in zip(row, col)) for col in right_t] for row in left]


def matvec(left: list[list[float]], right: list[float]) -> list[float]:
    return [sum(a * b for a, b in zip(row, right)) for row in left]


def inverse(matrix: list[list[float]]) -> list[list[float]] | None:
    n = len(matrix)
    augmented = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        scale = augmented[col][col]
        for j in range(2 * n):
            augmented[col][j] /= scale
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            for j in range(2 * n):
                augmented[row][j] -= factor * augmented[col][j]
    return [row[n:] for row in augmented]


def normal_approx_p_value(t_value: float | None) -> float | None:
    if t_value is None:
        return None
    # With n around 580, the standard normal is a close enough screening
    # approximation for p-values in this exploratory pass.
    cdf = 0.5 * (1 + erf(abs(t_value) / sqrt(2)))
    return 2 * (1 - cdf)


def standardize(values: list[float]) -> list[float] | None:
    avg = mean(values)
    variance = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
    sd = sqrt(variance) if variance > 0 else 0
    if sd == 0:
        return None
    return [(value - avg) / sd for value in values]


def fit_ols(model_id: str, dependent: str, block: str, predictors: list[str], rows: list[dict]) -> FitResult:
    usable = []
    for row in rows:
        y = number(row.get(dependent))
        xs = [number(row.get(predictor)) for predictor in predictors]
        if y is None or any(value is None for value in xs):
            continue
        usable.append((y, xs))

    n = len(usable)
    k = len(predictors)
    if n <= k + 1:
        return FitResult(model_id, dependent, block, n, k, None, None, None, [])

    y_values = [item[0] for item in usable]
    x_values = [[1.0] + item[1] for item in usable]
    xt = transpose(x_values)
    xtx = matmul(xt, x_values)
    xtx_inv = inverse(xtx)
    if xtx_inv is None:
        return FitResult(model_id, dependent, block, n, k, None, None, None, [])
    xty = matvec(xt, y_values)
    beta = matvec(xtx_inv, xty)
    fitted = [sum(coef * value for coef, value in zip(beta, row)) for row in x_values]
    residuals = [y - yhat for y, yhat in zip(y_values, fitted)]
    y_mean = mean(y_values)
    sse = sum(value * value for value in residuals)
    sst = sum((value - y_mean) ** 2 for value in y_values)
    dof = n - k - 1
    mse = sse / dof if dof > 0 else None
    rmse = sqrt(mse) if mse is not None else None
    r2 = 1 - sse / sst if sst > 0 else None
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / dof if r2 is not None and dof > 0 else None

    se = [sqrt(max(mse * xtx_inv[i][i], 0)) if mse is not None else None for i in range(k + 1)]
    raw_coefficients = []
    names = ["intercept"] + predictors
    for name, coef, coef_se in zip(names, beta, se):
        t_value = coef / coef_se if coef_se not in {None, 0} else None
        raw_coefficients.append(
            {
                "model_id": model_id,
                "dependent_variable": dependent,
                "block": block,
                "term": name,
                "coefficient": coef,
                "std_error": coef_se,
                "t_value": t_value,
                "p_value_normal_approx": normal_approx_p_value(t_value),
                "standardized_beta": "",
            }
        )

    y_z = standardize(y_values)
    standardized_betas: dict[str, float | None] = {name: None for name in predictors}
    if y_z is not None:
        standardized_columns = []
        for index in range(k):
            column = [item[1][index] for item in usable]
            standardized_columns.append(standardize(column))
        if all(column is not None for column in standardized_columns):
            z_x = [[1.0] + [column[i] for column in standardized_columns if column is not None] for i in range(n)]
            z_xt = transpose(z_x)
            z_inv = inverse(matmul(z_xt, z_x))
            if z_inv is not None:
                z_beta = matvec(z_inv, matvec(z_xt, y_z))
                standardized_betas = dict(zip(predictors, z_beta[1:]))

    for row in raw_coefficients:
        if row["term"] in standardized_betas:
            row["standardized_beta"] = standardized_betas[row["term"]]

    return FitResult(model_id, dependent, block, n, k, r2, adjusted_r2, rmse, raw_coefficients)


def fmt(value: float | str | None) -> str:
    if value == "":
        return ""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return f"{value:.10g}" if isfinite(value) else ""


def run_models() -> list[FitResult]:
    rows = read_rows(INPUT)
    results = []
    for model_label, dependent in DEPENDENT_VARIABLES.items():
        for block, predictors in BLOCKS.items():
            model_id = f"{model_label}__{block}"
            results.append(fit_ols(model_id, dependent, block, predictors, rows))
    return results


def write_outputs(results: list[FitResult]) -> None:
    summary = []
    coefficients = []
    top_terms = []
    for result in results:
        summary.append(
            {
                "model_id": result.model_id,
                "dependent_variable": result.dependent_variable,
                "block": result.block,
                "n": result.n,
                "num_predictors": result.k,
                "r2": fmt(result.r2),
                "adjusted_r2": fmt(result.adjusted_r2),
                "rmse": fmt(result.rmse),
            }
        )
        for row in result.coefficients:
            coefficients.append({key: fmt(value) for key, value in row.items()})
        ranked = [
            row
            for row in result.coefficients
            if row["term"] != "intercept" and isinstance(row["standardized_beta"], float)
        ]
        ranked.sort(key=lambda row: abs(row["standardized_beta"]), reverse=True)
        for rank, row in enumerate(ranked[:5], start=1):
            top_terms.append(
                {
                    "model_id": result.model_id,
                    "dependent_variable": result.dependent_variable,
                    "block": result.block,
                    "rank": rank,
                    "term": row["term"],
                    "standardized_beta": fmt(row["standardized_beta"]),
                    "coefficient": fmt(row["coefficient"]),
                    "p_value_normal_approx": fmt(row["p_value_normal_approx"]),
                }
            )
    write_csv(OUTPUT_ROOT / "block_model_summary.csv", summary)
    write_csv(OUTPUT_ROOT / "block_model_coefficients.csv", coefficients)
    write_csv(OUTPUT_ROOT / "block_model_top_predictors.csv", top_terms)
    write_report(summary, top_terms)


def write_report(summary: list[dict], top_terms: list[dict]) -> None:
    best_by_dv: dict[str, dict] = {}
    for row in summary:
        current = best_by_dv.get(row["dependent_variable"])
        if current is None or float(row["adjusted_r2"] or -999) > float(current["adjusted_r2"] or -999):
            best_by_dv[row["dependent_variable"]] = row

    lines = [
        "# Blockwise CT Turnout Models",
        "",
        "This exploratory pass runs 20 OLS models: five dependent variables by",
        "four predictor blocks. Predictors come from Blocks 1-4 only; Blocks 5-6",
        "are excluded because key variables remain missing or partially sourced.",
        "",
        "Dependent variables use the curated CT participation fields with",
        "`citizen_canadian_18over` as denominator.",
        "",
        "P-values are normal approximations from a pure-Python OLS implementation",
        "and should be treated as screening diagnostics, not publication-ready",
        "inference.",
        "",
        "## Model Fit",
        "",
        "| Dependent variable | Block | N | Adjusted R2 | R2 | RMSE |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['dependent_variable']} | {row['block']} | {row['n']} | "
            f"{row['adjusted_r2']} | {row['r2']} | {row['rmse']} |"
        )

    lines.extend(["", "## Best Block By Dependent Variable", ""])
    for dependent, row in best_by_dv.items():
        lines.append(
            f"- `{dependent}`: `{row['block']}` has the strongest adjusted R2 "
            f"({row['adjusted_r2']})."
        )

    lines.extend(["", "## Top Predictors", ""])
    grouped: dict[str, list[dict]] = {}
    for row in top_terms:
        if int(row["rank"]) <= 3:
            grouped.setdefault(row["model_id"], []).append(row)
    for model_id in sorted(grouped):
        lines.append(f"### {model_id}")
        for row in grouped[model_id]:
            lines.append(
                f"- {row['term']}: standardized beta {row['standardized_beta']}, "
                f"p~{row['p_value_normal_approx']}"
            )
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    results = run_models()
    write_outputs(results)
    print(f"Wrote {len(results)} models to {OUTPUT_ROOT}")
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
