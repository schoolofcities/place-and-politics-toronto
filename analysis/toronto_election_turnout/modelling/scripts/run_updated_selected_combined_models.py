"""Run Order 2 updated selected combined spatial-error models."""

from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np

from run_combined_spatial_models import design_matrix, run_one
from run_spatial_block_models import (
    DEPENDENT_VARIABLES,
    REPORT_OUTPUT,
    as_number,
    fmt,
    html_table,
    load_queen_weights,
    read_csv,
    write_csv,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "modelling" / "processed" / "spatial_models"
INPUT = OUTPUT_ROOT / "toronto_ct_blocks_1_5_model_input_housing_augmented_median_imputed.csv"
BASELINE_SUMMARY = OUTPUT_ROOT / "combined_spatial_model_summary.csv"
BASELINE_COEFFICIENTS = OUTPUT_ROOT / "combined_spatial_model_coefficients.csv"
UPDATED_SUMMARY_OUTPUT = OUTPUT_ROOT / "updated_selected_combined_model_summary.csv"
UPDATED_COEFFICIENT_OUTPUT = OUTPUT_ROOT / "updated_selected_combined_model_coefficients.csv"
UPDATED_RESIDUAL_OUTPUT = OUTPUT_ROOT / "updated_selected_combined_model_e_trimmed_residuals.csv"


BASE_SELECTED_VARIABLES = [
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

UPDATED_HOUSING_CANDIDATES = [
    "block2_condo_share",
    "block2_apartments_per_km2",
    "block2_condos_per_km2",
]

UPDATED_FULL_VARIABLES = BASE_SELECTED_VARIABLES + UPDATED_HOUSING_CANDIDATES


def coefficient_table(coef_rows: list[dict], model_id: str) -> str:
    rows = [
        [
            row["term"],
            "positive" if float(row["coefficient"]) > 0 else "negative",
            row["coefficient"],
            row["std_error"],
            row["z_value"],
            row["p_value"],
            row["significance"],
        ]
        for row in coef_rows
        if row["model_id"] == model_id and row["term"] != "intercept"
    ]
    return html_table(["Variable", "Direction", "SEM coef", "SE", "z", "p", ""], rows, "coef")


def summary_table(summary_rows: list[dict]) -> str:
    return html_table(
        ["Model", "Outcome", "N", "K", "OLS adj R2", "Lambda", "Lambda p", "Delta AIC", "Filtered Moran I", "Filtered Moran p"],
        [
            [
                row["model_id"],
                row["dependent_variable"],
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
        ],
    )


def compare_trimmed_sets(updated_trimmed: dict[str, list[str]]) -> str:
    baseline_rows = read_csv(BASELINE_COEFFICIENTS)
    baseline_trimmed = {}
    for label in DEPENDENT_VARIABLES:
        model_id = f"{label}__trimmed"
        baseline_trimmed[label] = [row["term"] for row in baseline_rows if row["model_id"] == model_id and row["term"] != "intercept"]

    rows = []
    for label in DEPENDENT_VARIABLES:
        old = baseline_trimmed.get(label, [])
        new = updated_trimmed[label]
        rows.append(
            [
                label,
                ", ".join(sorted(set(new) - set(old))) or "None",
                ", ".join(sorted(set(old) - set(new))) or "None",
                ", ".join(new),
            ]
        )
    return html_table(["Outcome", "Newly included", "Dropped from prior trimmed", "Updated trimmed predictors"], rows)


def compare_baseline_metrics(summary_rows: list[dict]) -> str:
    baseline_rows = {row["model_id"]: row for row in read_csv(BASELINE_SUMMARY)}
    updated_rows = {row["model_id"]: row for row in summary_rows}
    rows = []
    for label in DEPENDENT_VARIABLES:
        old_id = f"{label}__trimmed"
        new_id = f"{label}__updated_trimmed"
        old = baseline_rows[old_id]
        new = updated_rows[new_id]
        rows.append(
            [
                label,
                old["num_predictors"],
                new["num_predictors"],
                float(new["ols_adjusted_r2"]) - float(old["ols_adjusted_r2"]),
                float(new["spatial_lambda"]) - float(old["spatial_lambda"]),
                float(new["delta_aic_spatial_minus_ols"]) - float(old["delta_aic_spatial_minus_ols"]),
            ]
        )
    return html_table(["Outcome", "Old K", "New K", "Delta OLS adj R2", "Delta lambda", "Delta delta-AIC"], rows)


def append_report(summary_rows: list[dict], coef_rows: list[dict], trimmed_predictors: dict[str, list[str]]) -> None:
    html = REPORT_OUTPUT.read_text(encoding="utf-8")
    marker = "<h2>Order 2 Updated Selected Combined Models</h2>"
    if marker in html:
        html = html.split(marker)[0] + "</body>\n</html>\n"

    full_sections = []
    trimmed_sections = []
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
        if row["model_id"].endswith("__updated_full"):
            full_sections.append(section)
        else:
            trimmed_sections.append(section)

    addition = (
        marker
        + "<p class='note'>Order 2 updates the selected combined models using the housing-augmented dataset. "
        "The full candidate set keeps the earlier selected variables and adds condo share, apartment density, and condo density. "
        "The updated trimmed model keeps variables with p &lt; 0.10 in the corresponding updated full spatial-error model.</p>"
        + "<h3>Updated Combined Model Summary</h3>"
        + summary_table(summary_rows)
        + "<h3>Baseline vs Updated Trimmed Models</h3>"
        + compare_baseline_metrics(summary_rows)
        + "<h3>Updated Trimmed Predictor Sets</h3>"
        + compare_trimmed_sets(trimmed_predictors)
        + "<h3>Updated Full Combined Models</h3>"
        + "".join(full_sections)
        + "<h3>Updated Trimmed Combined Models</h3>"
        + "".join(trimmed_sections)
    )
    html = html.replace("</body>\n</html>", addition + "\n</body>\n</html>")
    REPORT_OUTPUT.write_text(html, encoding="utf-8")


def main() -> None:
    rows = read_csv(INPUT)
    missing = [col for col in UPDATED_FULL_VARIABLES if col not in rows[0]]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    ct_ids_all = [row["ct_id"] for row in rows]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}

    summary_rows = []
    coef_rows = []
    residual_rows = []
    keep_by_outcome = {}

    for label, dependent in DEPENDENT_VARIABLES.items():
        model_id = f"{label}__updated_full"
        summary, coefs, residuals = run_one(rows, w_all, index_all, model_id, dependent, UPDATED_FULL_VARIABLES)
        summary_rows.append(summary)
        coef_rows.extend(coefs)
        residual_rows.extend(residuals)
        keep = [
            row["term"]
            for row in coefs
            if row["term"] != "intercept" and as_number(row["p_value"]) is not None and float(row["p_value"]) < 0.10
        ]
        keep_by_outcome[label] = keep if len(keep) >= 2 else UPDATED_FULL_VARIABLES

    for label, dependent in DEPENDENT_VARIABLES.items():
        keep = keep_by_outcome[label]
        model_id = f"{label}__updated_trimmed"
        summary, coefs, residuals = run_one(rows, w_all, index_all, model_id, dependent, keep)
        summary_rows.append(summary)
        coef_rows.extend(coefs)
        residual_rows.extend(residuals)

    write_csv(UPDATED_SUMMARY_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in summary_rows])
    write_csv(UPDATED_COEFFICIENT_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in coef_rows])
    write_csv(
        UPDATED_RESIDUAL_OUTPUT,
        [{k: fmt(v) for k, v in row.items()} for row in residual_rows if row["model_id"] == "E_mean_turnout__updated_trimmed"],
    )
    append_report(summary_rows, coef_rows, keep_by_outcome)
    print(f"Wrote {UPDATED_SUMMARY_OUTPUT}")
    print(f"Wrote {UPDATED_COEFFICIENT_OUTPUT}")
    print(f"Wrote {UPDATED_RESIDUAL_OUTPUT}")
    print(f"Appended {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
