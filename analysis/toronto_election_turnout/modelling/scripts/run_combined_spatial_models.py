"""Run combined and trimmed spatial-error models using selected predictors."""

from __future__ import annotations

import csv
from html import escape
from pathlib import Path

import numpy as np

from run_spatial_block_models import (
    COEFFICIENT_OUTPUT,
    DEPENDENT_VARIABLES,
    IMPUTED_OUTPUT,
    REPORT_OUTPUT,
    SUMMARY_OUTPUT,
    as_number,
    fit_spatial_error,
    fmt,
    html_table,
    load_queen_weights,
    morans_i,
    ols,
    read_csv,
    significance,
    write_csv,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "modelling" / "processed" / "spatial_models"
COMBINED_SUMMARY_OUTPUT = OUTPUT_ROOT / "combined_spatial_model_summary.csv"
COMBINED_COEFFICIENT_OUTPUT = OUTPUT_ROOT / "combined_spatial_model_coefficients.csv"
RESIDUAL_OUTPUT = OUTPUT_ROOT / "combined_model_e_trimmed_residuals.csv"


FULL_VARIABLES = [
    "block1_age_18_34_share",
    "block1_average_household_size",
    "block1_bachelors_or_higher_25_64_share",
    "block1_low_income_lim_at_share",
    "block1_unemployment_rate_share",
    "block2_renter_share",
    "block2_apartment_share",
    "block3_visible_minority_share",
    "block3_non_citizen_share",
    "block3_immigrant_share",
    "block4_mayoral_top_two_margin",
    "block4_effective_mayoral_candidates_5pct",
    "block5_school_age_5_17_share",
    "block5_park_access_1200m",
    "block5_transit_commute_share_preferred",
    "block5_social_housing_share",
    "block5_development_applications_2021_2025_per_1000",
    "block5_ksi_collision_events_2021_2025_per_1000",
]


def design_matrix(rows: list[dict[str, str]], dependent: str, predictors: list[str]):
    ct_ids = []
    y_vals = []
    x_vals = []
    for row in rows:
        y = as_number(row.get(dependent))
        xs = [as_number(row.get(col)) for col in predictors]
        if y is None or any(value is None for value in xs):
            continue
        ct_ids.append(row["ct_id"])
        y_vals.append(y)
        x_vals.append(xs)
    x_raw = np.array(x_vals, dtype=float)
    x = np.column_stack([np.ones(len(y_vals)), x_raw])
    return ct_ids, np.array(y_vals, dtype=float), x, x_raw


def run_one(rows, w_all, index_all, model_id: str, dependent: str, predictors: list[str]):
    ct_ids, y, x, _ = design_matrix(rows, dependent, predictors)
    idx = [index_all[ct_id] for ct_id in ct_ids]
    w = w_all[np.ix_(idx, idx)]
    w = w / w.sum(axis=1, keepdims=True)
    ols_fit = ols(y, x)
    sem_fit = fit_spatial_error(y, x, w)
    moran_ols, moran_ols_p = morans_i(ols_fit.residuals, w)
    moran_sem, moran_sem_p = morans_i(sem_fit.filtered_residuals, w)
    summary = {
        "model_id": model_id,
        "dependent_variable": dependent,
        "n": len(y),
        "num_predictors": len(predictors),
        "ols_adjusted_r2": ols_fit.adjusted_r2,
        "ols_aic": ols_fit.aic,
        "ols_residual_morans_i": moran_ols,
        "ols_residual_morans_p_perm": moran_ols_p,
        "spatial_lambda": sem_fit.lam,
        "spatial_lambda_p": sem_fit.lambda_p,
        "spatial_aic": sem_fit.aic,
        "spatial_filtered_residual_morans_i": moran_sem,
        "spatial_filtered_residual_morans_p_perm": moran_sem_p,
        "delta_aic_spatial_minus_ols": sem_fit.aic - ols_fit.aic,
    }
    coef_rows = []
    names = ["intercept"] + predictors
    for i, name in enumerate(names):
        coef_rows.append(
            {
                "model_id": model_id,
                "term": name,
                "coefficient": sem_fit.beta[i],
                "std_error": sem_fit.se[i],
                "z_value": sem_fit.t[i],
                "p_value": sem_fit.p[i],
                "significance": significance(float(sem_fit.p[i])) if np.isfinite(float(sem_fit.p[i])) else "",
            }
        )
    residual_rows = [
        {
            "model_id": model_id,
            "ct_id": ct_id,
            "observed": y_val,
            "spatial_residual": residual,
            "spatial_filtered_residual": filtered,
        }
        for ct_id, y_val, residual, filtered in zip(ct_ids, y, sem_fit.residuals, sem_fit.filtered_residuals)
    ]
    return summary, coef_rows, residual_rows


def model_table(summary_rows: list[dict]) -> str:
    rows = [
        [
            row["model_id"],
            row["n"],
            row["num_predictors"],
            row["ols_adjusted_r2"],
            row["spatial_lambda"],
            row["spatial_lambda_p"],
            row["delta_aic_spatial_minus_ols"],
            row["spatial_filtered_residual_morans_i"],
            row["spatial_filtered_residual_morans_p_perm"],
        ]
        for row in summary_rows
    ]
    return html_table(
        ["Model", "N", "K", "OLS adj R2", "Lambda", "Lambda p", "Delta AIC", "Filtered Moran I", "Filtered Moran p"],
        rows,
    )


def coefficient_table(coef_rows: list[dict], model_id: str) -> str:
    rows = [
        [row["term"], row["coefficient"], row["std_error"], row["z_value"], row["p_value"], row["significance"]]
        for row in coef_rows
        if row["model_id"] == model_id
    ]
    return html_table(["Term", "SEM coef", "SE", "z", "p", ""], rows, "coef")


def append_report(summary_rows: list[dict], coef_rows: list[dict], trimmed_predictors: dict[str, list[str]], residual_rows: list[dict]) -> None:
    html = REPORT_OUTPUT.read_text(encoding="utf-8")
    if "<h2>Combined Spatial Models</h2>" in html:
        html = html.split("<h2>Combined Spatial Models</h2>")[0] + "</body>\n</html>\n"

    full_sections = []
    trim_sections = []
    for row in summary_rows:
        section = (
            f"<section><h3>{escape(row['model_id'])}</h3>"
            f"<p><strong>Spatial lambda:</strong> {fmt(row['spatial_lambda'])} "
            f"(p={fmt(row['spatial_lambda_p'])}); "
            f"<strong>Delta AIC spatial-OLS:</strong> {fmt(row['delta_aic_spatial_minus_ols'])}; "
            f"<strong>Filtered Moran I:</strong> {fmt(row['spatial_filtered_residual_morans_i'])} "
            f"(p={fmt(row['spatial_filtered_residual_morans_p_perm'])}).</p>"
            + coefficient_table(coef_rows, row["model_id"])
            + "</section>"
        )
        if "__full" in row["model_id"]:
            full_sections.append(section)
        else:
            trim_sections.append(section)

    model_e_residuals = [r for r in residual_rows if r["model_id"] == "E_mean_turnout__trimmed"]
    high = sorted(model_e_residuals, key=lambda r: float(r["spatial_filtered_residual"]), reverse=True)[:10]
    low = sorted(model_e_residuals, key=lambda r: float(r["spatial_filtered_residual"]))[:10]
    residual_table = html_table(
        ["CT", "Observed", "Spatial residual", "Filtered residual"],
        [[r["ct_id"], r["observed"], r["spatial_residual"], r["spatial_filtered_residual"]] for r in high + low],
    )
    trimmed_table = html_table(
        ["Outcome", "Trimmed predictors"],
        [[outcome, ", ".join(cols)] for outcome, cols in trimmed_predictors.items()],
    )

    addition = (
        "<h2>Combined Spatial Models</h2>"
        "<p class='note'>This section was appended after the original 25 blockwise models. "
        "The full model combines the selected existing good variables and the Model E emphasis variables. "
        "The trimmed model keeps variables with p &lt; 0.10 in the corresponding full spatial-error model.</p>"
        "<h3>Combined Model Summary</h3>"
        + model_table(summary_rows)
        + "<h3>Trimmed Predictor Sets</h3>"
        + trimmed_table
        + "<h3>Full Combined Models</h3>"
        + "".join(full_sections)
        + "<h3>Trimmed Combined Models</h3>"
        + "".join(trim_sections)
        + "<h3>Step 3 Residual Check: Model E Trimmed</h3>"
        + "<p>Rows show the ten largest positive and ten largest negative filtered residuals after the trimmed spatial-error model for mean turnout.</p>"
        + residual_table
    )
    html = html.replace("</body>\n</html>", addition + "\n</body>\n</html>")
    REPORT_OUTPUT.write_text(html, encoding="utf-8")


def main() -> None:
    rows = read_csv(IMPUTED_OUTPUT)
    ct_ids_all = [row["ct_id"] for row in rows]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}

    summary_rows = []
    coef_rows = []
    residual_rows = []
    full_by_outcome = {}
    for label, dependent in DEPENDENT_VARIABLES.items():
        model_id = f"{label}__full"
        summary, coefs, residuals = run_one(rows, w_all, index_all, model_id, dependent, FULL_VARIABLES)
        summary_rows.append(summary)
        coef_rows.extend(coefs)
        residual_rows.extend(residuals)
        keep = [
            row["term"]
            for row in coefs
            if row["term"] != "intercept" and as_number(row["p_value"]) is not None and float(row["p_value"]) < 0.10
        ]
        full_by_outcome[label] = keep

    trimmed_predictors = {}
    for label, dependent in DEPENDENT_VARIABLES.items():
        keep = full_by_outcome[label]
        if len(keep) < 2:
            keep = FULL_VARIABLES
        trimmed_predictors[label] = keep
        model_id = f"{label}__trimmed"
        summary, coefs, residuals = run_one(rows, w_all, index_all, model_id, dependent, keep)
        summary_rows.append(summary)
        coef_rows.extend(coefs)
        residual_rows.extend(residuals)

    write_csv(COMBINED_SUMMARY_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in summary_rows])
    write_csv(COMBINED_COEFFICIENT_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in coef_rows])
    write_csv(RESIDUAL_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in residual_rows if row["model_id"] == "E_mean_turnout__trimmed"])
    append_report(summary_rows, coef_rows, trimmed_predictors, residual_rows)
    print(f"Wrote {COMBINED_SUMMARY_OUTPUT}")
    print(f"Wrote {COMBINED_COEFFICIENT_OUTPUT}")
    print(f"Wrote {RESIDUAL_OUTPUT}")
    print(f"Appended {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
