"""Run Order 3 saturated full spatial-error models with all collected predictors."""

from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np

from run_combined_spatial_models import run_one
from run_spatial_block_models import (
    BLOCKS,
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
SUMMARY_OUTPUT = OUTPUT_ROOT / "full_all_variables_spatial_model_summary.csv"
COEFFICIENT_OUTPUT = OUTPUT_ROOT / "full_all_variables_spatial_model_coefficients.csv"
MODEL_E_RESIDUAL_OUTPUT = OUTPUT_ROOT / "full_all_variables_model_e_residuals.csv"


ADDITIONAL_FULL_VARIABLES = [
    "block4_mayoral_winner_margin",
    "block4_mayoral_candidate_count_5pct",
    "block4_provincial_party_count_5pct",
    "block4_provincial_vote_fragmentation",
    "block4_federal_party_count_5pct",
    "block4_federal_vote_fragmentation",
    "block5_tts_no_car_household_share",
    "block5_tts_transit_trip_share",
    "block5_tts_overlap_area_m2",
    "block5_library_nearest_m",
    "block5_library_count_1200m",
    "block5_community_centre_nearest_m",
    "block5_community_centre_count_1200m",
    "block5_park_nearest_m",
    "block5_park_count_1200m",
    "block5_shelter_nearest_m",
    "block5_shelter_count_1200m",
    "block5_ksi_collision_events_2021_2025",
    "block5_development_applications_2021_2025",
    "block5_requests_311_2023_2025_estimated_count",
    "block5_requests_311_per_1000",
    "block2_structural_type_total_dwellings",
    "block2_apartment_duplex_count",
    "block2_apartment_lt5_storeys_count",
    "block2_apartment_5plus_storeys_count",
    "block2_apartment_total_count",
    "block2_condo_status_total_dwellings",
    "block2_condominium_dwellings_count",
    "block2_apartments_per_km2",
    "block2_condos_per_km2",
]


def full_predictors(rows: list[dict[str, str]]) -> list[str]:
    cols = []
    for block_cols in BLOCKS.values():
        cols.extend(block_cols)
    cols.extend(ADDITIONAL_FULL_VARIABLES)

    seen = set()
    available = []
    for col in cols:
        if col in seen or col not in rows[0]:
            continue
        values = [as_number(row.get(col)) for row in rows]
        if not any(value is not None for value in values):
            continue
        available.append(col)
        seen.add(col)
    return available


def design_rank_diagnostics(rows: list[dict[str, str]], dependent: str, predictors: list[str]) -> dict[str, object]:
    x_vals = []
    for row in rows:
        y = as_number(row.get(dependent))
        xs = [as_number(row.get(col)) for col in predictors]
        if y is None or any(value is None for value in xs):
            continue
        x_vals.append(xs)
    x = np.column_stack([np.ones(len(x_vals)), np.array(x_vals, dtype=float)])
    rank = int(np.linalg.matrix_rank(x))
    cols = int(x.shape[1])
    try:
        condition = float(np.linalg.cond(x))
    except np.linalg.LinAlgError:
        condition = np.inf
    return {
        "design_rank": rank,
        "design_columns_with_intercept": cols,
        "rank_deficiency": cols - rank,
        "condition_number": condition,
    }


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


def significant_terms_table(coef_rows: list[dict]) -> str:
    rows = []
    for row in coef_rows:
        if row["term"] == "intercept":
            continue
        p = as_number(row.get("p_value"))
        if p is not None and p < 0.10:
            rows.append(
                [
                    row["model_id"],
                    row["term"],
                    "positive" if float(row["coefficient"]) > 0 else "negative",
                    row["coefficient"],
                    row["p_value"],
                    row["significance"],
                ]
            )
    return html_table(["Model", "Variable", "Direction", "SEM coef", "p", ""], rows, "coef")


def append_report(summary_rows: list[dict], coef_rows: list[dict], predictors: list[str]) -> None:
    html = REPORT_OUTPUT.read_text(encoding="utf-8")
    marker = "<h2>Order 3 Full All-Variables Spatial Models</h2>"
    if marker in html:
        html = html.split(marker)[0] + "</body>\n</html>\n"

    metrics = [
        [
            row["model_id"],
            row["dependent_variable"],
            row["n"],
            row["num_predictors"],
            row["design_rank"],
            row["rank_deficiency"],
            row["ols_adjusted_r2"],
            row["spatial_lambda"],
            row["spatial_lambda_p"],
            row["delta_aic_spatial_minus_ols"],
            row["spatial_filtered_residual_morans_i"],
            row["spatial_filtered_residual_morans_p_perm"],
        ]
        for row in summary_rows
    ]
    predictor_table = html_table(["Predictors included"], [[col] for col in predictors])
    sections = []
    for row in summary_rows:
        sections.append(
            f"<section><h3>{escape(row['model_id'])}</h3>"
            f"<p><strong>Rank deficiency:</strong> {fmt(row['rank_deficiency'])}; "
            f"<strong>Condition number:</strong> {fmt(row['condition_number'])}; "
            f"<strong>Spatial lambda:</strong> {fmt(row['spatial_lambda'])} "
            f"(p={fmt(row['spatial_lambda_p'])}); "
            f"<strong>Delta AIC spatial-OLS:</strong> {fmt(row['delta_aic_spatial_minus_ols'])}.</p>"
            + coefficient_table(coef_rows, row["model_id"])
            + "</section>"
        )
    addition = (
        marker
        + "<p class='note'>Order 3 fits saturated full models using all collected substantive Block 1-5 predictors in the housing-augmented dataset. "
        "These models intentionally include highly related variables, so coefficient-level interpretation should be cautious where rank deficiency or high condition numbers appear.</p>"
        + "<h3>Full Model Summary</h3>"
        + html_table(
            [
                "Model",
                "Outcome",
                "N",
                "K",
                "Rank",
                "Rank deficiency",
                "OLS adj R2",
                "Lambda",
                "Lambda p",
                "Delta AIC",
                "Filtered Moran I",
                "Filtered Moran p",
            ],
            metrics,
        )
        + "<h3>Predictor Universe</h3>"
        + predictor_table
        + "<h3>Terms With p &lt; 0.10</h3>"
        + significant_terms_table(coef_rows)
        + "<h3>Coefficient Tables</h3>"
        + "".join(sections)
    )
    html = html.replace("</body>\n</html>", addition + "\n</body>\n</html>")
    REPORT_OUTPUT.write_text(html, encoding="utf-8")


def main() -> None:
    rows = read_csv(INPUT)
    predictors = full_predictors(rows)
    ct_ids_all = [row["ct_id"] for row in rows]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}

    summary_rows = []
    coef_rows = []
    residual_rows = []
    for label, dependent in DEPENDENT_VARIABLES.items():
        model_id = f"{label}__full_all_variables"
        summary, coefs, residuals = run_one(rows, w_all, index_all, model_id, dependent, predictors)
        summary.update(design_rank_diagnostics(rows, dependent, predictors))
        summary_rows.append(summary)
        coef_rows.extend(coefs)
        residual_rows.extend(residuals)

    write_csv(SUMMARY_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in summary_rows])
    write_csv(COEFFICIENT_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in coef_rows])
    write_csv(
        MODEL_E_RESIDUAL_OUTPUT,
        [{k: fmt(v) for k, v in row.items()} for row in residual_rows if row["model_id"] == "E_mean_turnout__full_all_variables"],
    )
    append_report(summary_rows, coef_rows, predictors)
    print(f"Predictors: {len(predictors)}")
    print(f"Wrote {SUMMARY_OUTPUT}")
    print(f"Wrote {COEFFICIENT_OUTPUT}")
    print(f"Wrote {MODEL_E_RESIDUAL_OUTPUT}")
    print(f"Appended {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
