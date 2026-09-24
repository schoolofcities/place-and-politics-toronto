"""Run updated Block 2 housing spatial-error model specifications."""

from __future__ import annotations

import csv
from html import escape
from pathlib import Path

import numpy as np

from run_spatial_block_models import (
    DEPENDENT_VARIABLES,
    REPORT_OUTPUT,
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
INPUT = OUTPUT_ROOT / "toronto_ct_blocks_1_5_model_input_housing_augmented_median_imputed.csv"
SUMMARY_OUTPUT = OUTPUT_ROOT / "updated_block2_housing_model_summary.csv"
COEFFICIENT_OUTPUT = OUTPUT_ROOT / "updated_block2_housing_model_coefficients.csv"


SPECS = {
    "housing_original": [
        "block2_renter_share",
        "block2_owner_share",
        "block2_same_address_1yr_share",
        "block2_same_address_5yr_share",
        "block2_condo_share",
        "block2_apartment_share",
        "block2_detached_share",
        "block2_semi_detached_share",
        "block2_population_density_per_km2",
    ],
    "housing_zack_condo_share": [
        "block2_renter_share",
        "block2_apartment_share",
        "block2_condo_share",
    ],
    "housing_density_scale": [
        "block2_renter_share",
        "block2_apartment_share",
        "block2_apartments_per_km2",
        "block2_condos_per_km2",
    ],
    "housing_condo_interpretation": [
        "block2_renter_share",
        "block2_apartment_share",
        "block2_condo_share",
        "block2_condos_per_km2",
    ],
    "housing_augmented_check": [
        "block2_renter_share",
        "block2_apartment_share",
        "block2_condo_share",
        "block2_apartments_per_km2",
        "block2_condos_per_km2",
        "block2_population_density_per_km2",
    ],
}


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
    return ct_ids, np.array(y_vals, dtype=float), x


def run_one(rows, w_all, index_all, model_id: str, dependent: str, predictors: list[str]):
    ct_ids, y, x = design_matrix(rows, dependent, predictors)
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
        "specification": model_id.split("__", 1)[1],
        "n": len(y),
        "num_predictors": len(predictors),
        "ols_adjusted_r2": ols_fit.adjusted_r2,
        "ols_aic": ols_fit.aic,
        "spatial_lambda": sem_fit.lam,
        "spatial_lambda_p": sem_fit.lambda_p,
        "spatial_aic": sem_fit.aic,
        "delta_aic_spatial_minus_ols": sem_fit.aic - ols_fit.aic,
        "ols_residual_morans_i": moran_ols,
        "ols_residual_morans_p_perm": moran_ols_p,
        "spatial_filtered_residual_morans_i": moran_sem,
        "spatial_filtered_residual_morans_p_perm": moran_sem_p,
    }
    coef_rows = []
    for i, name in enumerate(["intercept"] + predictors):
        coef_rows.append(
            {
                "model_id": model_id,
                "dependent_variable": dependent,
                "specification": summary["specification"],
                "term": name,
                "coefficient": sem_fit.beta[i],
                "std_error": sem_fit.se[i],
                "z_value": sem_fit.t[i],
                "p_value": sem_fit.p[i],
                "significance": significance(float(sem_fit.p[i])) if np.isfinite(float(sem_fit.p[i])) else "",
            }
        )
    return summary, coef_rows


def append_report(summary_rows: list[dict], coef_rows: list[dict]) -> None:
    html = REPORT_OUTPUT.read_text(encoding="utf-8")
    marker = "<h2>Order 1 Updated Block 2 Housing Models</h2>"
    if marker in html:
        html = html.split(marker)[0] + "</body>\n</html>\n"

    metrics = [
        [
            r["model_id"],
            r["dependent_variable"],
            r["n"],
            r["num_predictors"],
            r["ols_adjusted_r2"],
            r["spatial_lambda"],
            r["spatial_lambda_p"],
            r["delta_aic_spatial_minus_ols"],
            r["spatial_filtered_residual_morans_i"],
            r["spatial_filtered_residual_morans_p_perm"],
        ]
        for r in summary_rows
    ]
    sections = []
    for r in summary_rows:
        rows = []
        for c in coef_rows:
            if c["model_id"] == r["model_id"] and c["term"] != "intercept":
                rows.append(
                    [
                        c["term"],
                        "positive" if float(c["coefficient"]) > 0 else "negative",
                        c["coefficient"],
                        c["std_error"],
                        c["z_value"],
                        c["p_value"],
                        c["significance"],
                    ]
                )
        sections.append(
            f"<section><h3>{escape(r['model_id'])}</h3>"
            + html_table(["Variable", "Direction", "SEM coef", "SE", "z", "p", ""], rows, "coef")
            + "</section>"
        )
    addition = (
        marker
        + "<p class='note'>Order 1 re-tests Block 2 housing using the housing-augmented dataset. "
        "The original Block 2 model is included for comparison, followed by condo-share and density/scale specifications.</p>"
        + html_table(
            ["Model", "Outcome", "N", "K", "OLS adj R2", "Lambda", "Lambda p", "Delta AIC", "Filtered Moran I", "Filtered Moran p"],
            metrics,
        )
        + "<h3>Coefficient Tables</h3>"
        + "".join(sections)
    )
    html = html.replace("</body>\n</html>", addition + "\n</body>\n</html>")
    REPORT_OUTPUT.write_text(html, encoding="utf-8")


def main() -> None:
    rows = read_csv(INPUT)
    ct_ids_all = [row["ct_id"] for row in rows]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}

    summary_rows = []
    coef_rows = []
    for outcome_label, dependent in DEPENDENT_VARIABLES.items():
        for spec_name, predictors in SPECS.items():
            model_id = f"{outcome_label}__{spec_name}"
            summary, coefs = run_one(rows, w_all, index_all, model_id, dependent, predictors)
            summary_rows.append(summary)
            coef_rows.extend(coefs)

    write_csv(SUMMARY_OUTPUT, [{k: fmt(v) for k, v in r.items()} for r in summary_rows])
    write_csv(COEFFICIENT_OUTPUT, [{k: fmt(v) for k, v in r.items()} for r in coef_rows])
    append_report(summary_rows, coef_rows)
    print(f"Wrote {SUMMARY_OUTPUT}")
    print(f"Wrote {COEFFICIENT_OUTPUT}")
    print(f"Appended {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
