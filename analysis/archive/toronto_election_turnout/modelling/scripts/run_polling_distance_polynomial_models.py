"""Run Order 5 polling-distance polynomial spatial-error models for A and B."""

from __future__ import annotations

from collections import defaultdict
from html import escape
from pathlib import Path

from run_combined_spatial_models import run_one
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
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
OUTPUT_ROOT = DATA_ROOT / "modelling" / "processed" / "spatial_models"
INPUT = OUTPUT_ROOT / "toronto_ct_blocks_1_5_model_input_housing_augmented_median_imputed.csv"
SUMMARY_OUTPUT = OUTPUT_ROOT / "polling_distance_polynomial_model_summary.csv"
COEFFICIENT_OUTPUT = OUTPUT_ROOT / "polling_distance_polynomial_model_coefficients.csv"
CT_DISTANCE_OUTPUT = OUTPUT_ROOT / "ct_polling_distance_variables.csv"


ACCESSIBILITY_ROOT = DATA_ROOT / "accessibility" / "processed"
MUNICIPAL_METRICS = ACCESSIBILITY_ROOT / "poll_accessibility_metrics" / "municipal_2023_mayor_poll_accessibility_metrics.csv"
PROVINCIAL_METRICS = ACCESSIBILITY_ROOT / "poll_accessibility_metrics" / "provincial_2025_poll_accessibility_metrics.csv"
MUNICIPAL_CROSSWALK = DATA_ROOT / "interpolation" / "processed" / "intermediate" / "02_spatial_crosswalks" / "municipal_2023_mayor_poll_to_ct_crosswalk.csv"
PROVINCIAL_CROSSWALK = DATA_ROOT / "interpolation" / "processed" / "intermediate" / "02_spatial_crosswalks" / "provincial_2025_poll_to_ct_crosswalk.csv"


ORDER2_TRIMMED = {
    "A_municipal_turnout": [
        "block1_age_18_34_share",
        "block1_average_household_size",
        "block1_bachelors_or_higher_25_64_share",
        "block1_unemployment_rate_share",
        "block2_renter_share",
        "block2_apartment_share",
        "block3_visible_minority_share",
        "block3_immigrant_share",
        "block4_mayoral_top_two_margin",
        "block4_effective_mayoral_candidates_5pct",
        "block5_park_access_1200m",
        "block5_ksi_collision_events_2021_2025_per_1000",
        "block2_apartments_per_km2",
        "block2_condos_per_km2",
    ],
    "B_provincial_turnout": [
        "block1_age_18_34_share",
        "block1_average_household_size",
        "block2_renter_share",
        "block2_apartment_share",
        "block3_visible_minority_share",
        "block4_effective_mayoral_candidates_5pct",
        "block5_park_access_1200m",
    ],
}


def distance_by_poll(metrics_path: Path) -> dict[str, float]:
    out = {}
    for row in read_csv(metrics_path):
        if str(row.get("vote_type", "")).strip() != "election_day":
            continue
        if str(row.get("exclude_from_distance_model_flag", "")).strip() in {"1", "true", "True"}:
            continue
        distance_m = as_number(row.get("poll_point_on_surface_distance_m"))
        if distance_m is None:
            distance_m = as_number(row.get("poll_centroid_distance_m"))
        if distance_m is None:
            continue
        out[row["poll_id"]] = distance_m / 1000.0
    return out


def aggregate_ct_distance(metrics_path: Path, crosswalk_path: Path, prefix: str) -> dict[str, dict[str, str]]:
    poll_distances = distance_by_poll(metrics_path)
    weighted_sum = defaultdict(float)
    weight_sum = defaultdict(float)
    contributing_polls = defaultdict(int)
    for row in read_csv(crosswalk_path):
        poll_id = row.get("poll_id") or row.get("source_id")
        if poll_id not in poll_distances:
            continue
        weight = as_number(row.get("population_weight"))
        if weight is None or weight <= 0:
            weight = as_number(row.get("intersection_area_m2"))
        if weight is None or weight <= 0:
            continue
        ct_id = row["ct_id"]
        weighted_sum[ct_id] += weight * poll_distances[poll_id]
        weight_sum[ct_id] += weight
        contributing_polls[ct_id] += 1

    out = {}
    for ct_id, total_weight in weight_sum.items():
        distance = weighted_sum[ct_id] / total_weight
        out[ct_id] = {
            f"{prefix}_poll_distance_km": fmt(distance, 10),
            f"{prefix}_poll_distance_km_sq": fmt(distance * distance, 10),
            f"{prefix}_poll_distance_contributing_polls": str(contributing_polls[ct_id]),
        }
    return out


def add_distance_variables(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    municipal = aggregate_ct_distance(MUNICIPAL_METRICS, MUNICIPAL_CROSSWALK, "municipal")
    provincial = aggregate_ct_distance(PROVINCIAL_METRICS, PROVINCIAL_CROSSWALK, "provincial")
    out = []
    medians = {}
    for prefix, source in [("municipal", municipal), ("provincial", provincial)]:
        values = [as_number(v.get(f"{prefix}_poll_distance_km")) for v in source.values()]
        values = sorted(v for v in values if v is not None)
        mid = len(values) // 2
        medians[prefix] = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2

    for row in rows:
        updated = dict(row)
        ct_id = row["ct_id"]
        for prefix, source in [("municipal", municipal), ("provincial", provincial)]:
            if ct_id in source:
                updated.update(source[ct_id])
                updated[f"{prefix}_poll_distance_median_imputed"] = "false"
            else:
                distance = medians[prefix]
                updated[f"{prefix}_poll_distance_km"] = fmt(distance, 10)
                updated[f"{prefix}_poll_distance_km_sq"] = fmt(distance * distance, 10)
                updated[f"{prefix}_poll_distance_contributing_polls"] = "0"
                updated[f"{prefix}_poll_distance_median_imputed"] = "true"
        out.append(updated)
    return out


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


def append_report(summary_rows: list[dict], coef_rows: list[dict]) -> None:
    html = REPORT_OUTPUT.read_text(encoding="utf-8")
    marker = "<h2>Order 5 Polling Distance Polynomial Models</h2>"
    if marker in html:
        html = html.split(marker)[0] + "</body>\n</html>\n"

    metrics = [
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
    ]
    sections = []
    for row in summary_rows:
        sections.append(
            f"<section><h3>{escape(row['model_id'])}</h3>"
            + coefficient_table(coef_rows, row["model_id"])
            + "</section>"
        )
    addition = (
        marker
        + "<p class='note'>Order 5 tests CT-level weighted mean polling-place distance with a quadratic term for Model A municipal and Model B provincial. "
        "Each outcome uses the matching election's polling-location distance measure.</p>"
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
    rows = add_distance_variables(read_csv(INPUT))
    distance_columns = [
        "ct_id",
        "municipal_poll_distance_km",
        "municipal_poll_distance_km_sq",
        "municipal_poll_distance_contributing_polls",
        "municipal_poll_distance_median_imputed",
        "provincial_poll_distance_km",
        "provincial_poll_distance_km_sq",
        "provincial_poll_distance_contributing_polls",
        "provincial_poll_distance_median_imputed",
    ]
    write_csv(CT_DISTANCE_OUTPUT, [{col: row.get(col, "") for col in distance_columns} for row in rows], distance_columns)

    ct_ids_all = [row["ct_id"] for row in rows]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}

    specs = {
        "A_municipal_turnout__distance_poly_only": (
            DEPENDENT_VARIABLES["A_municipal_turnout"],
            ["municipal_poll_distance_km", "municipal_poll_distance_km_sq"],
        ),
        "A_municipal_turnout__selected_plus_distance_poly": (
            DEPENDENT_VARIABLES["A_municipal_turnout"],
            ORDER2_TRIMMED["A_municipal_turnout"] + ["municipal_poll_distance_km", "municipal_poll_distance_km_sq"],
        ),
        "B_provincial_turnout__distance_poly_only": (
            DEPENDENT_VARIABLES["B_provincial_turnout"],
            ["provincial_poll_distance_km", "provincial_poll_distance_km_sq"],
        ),
        "B_provincial_turnout__selected_plus_distance_poly": (
            DEPENDENT_VARIABLES["B_provincial_turnout"],
            ORDER2_TRIMMED["B_provincial_turnout"] + ["provincial_poll_distance_km", "provincial_poll_distance_km_sq"],
        ),
    }
    summary_rows = []
    coef_rows = []
    for model_id, (dependent, predictors) in specs.items():
        summary, coefs, _ = run_one(rows, w_all, index_all, model_id, dependent, predictors)
        summary_rows.append(summary)
        coef_rows.extend(coefs)

    write_csv(SUMMARY_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in summary_rows])
    write_csv(COEFFICIENT_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in coef_rows])
    append_report(summary_rows, coef_rows)
    print(f"Wrote {CT_DISTANCE_OUTPUT}")
    print(f"Wrote {SUMMARY_OUTPUT}")
    print(f"Wrote {COEFFICIENT_OUTPUT}")
    print(f"Appended {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
