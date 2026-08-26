"""Build the compact, documented census-tract data release.

The final layer is intentionally derived from existing processed products. It
does not modify raw, intermediate, or model-development artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "data/toronto_election_turnout"
ANALYSIS_ROOT = REPO_ROOT / "analysis/toronto_election_turnout"
FINAL_ROOT = DATA_ROOT / "final"

GEOGRAPHY_DIR = FINAL_ROOT / "geography"
OBSERVED_DIR = FINAL_ROOT / "observed"
MODELLED_DIR = FINAL_ROOT / "modelled"
MEETING_DIR = FINAL_ROOT / "meeting_pls"
ROBUSTNESS_DIR = FINAL_ROOT / "robustness_checks"
DEFINITIONS_DIR = FINAL_ROOT / "model_definitions"
METADATA_DIR = FINAL_ROOT / "metadata"

VARIABLE_MASTER = DATA_ROOT / "variables/processed/toronto_ct_blocks_1_5_modelling_master.csv"
MODEL_INPUT = (
    DATA_ROOT
    / "modelling/processed/spatial_models/toronto_ct_blocks_1_5_model_input_housing_augmented_median_imputed.csv"
)
BASE_MAP = DATA_ROOT / "interpolation/map/municipal_2023_mayor_ct_map.geojson"

WF_DIR = ANALYSIS_ROOT / "modelling/dimension_reduction/scripts"
MEETING_SCRIPT_DIR = ANALYSIS_ROOT / "modelling/dimension_reduction/meeting_PLS"
sys.path.insert(0, str(WF_DIR))
sys.path.insert(0, str(MEETING_SCRIPT_DIR))
import run_dimension_reduction_workflow as wf  # noqa: E402
import run_meeting_pls as meeting  # noqa: E402


ID_COLUMNS = ["ct_id", "ctuid", "dguid", "geo_name"]
OUTCOMES = {
    "mean": "outcome_mean_participation_citizen_18plus",
    "municipal": "outcome_municipal_participation_citizen_18plus",
    "provincial": "outcome_provincial_participation_citizen_18plus",
    "federal": "outcome_federal_participation_citizen_18plus",
}

MEETING_COMPONENT_LABELS = {
    1: "education/resource attachment versus racialized-immigrant household geography",
    2: "older residential stability versus younger no-car renter/density geography",
}

BLOCK_COMPONENT_LABELS = {
    1: "education and older-resource profile versus newcomer/citizenship/racialized household geography",
    2: "dense renter/apartment urban form versus larger-household residential stability",
    3: "older residential stability versus younger educated dense geography",
    4: "dense educated mixed-newcomer geography versus older renter/lower-income contrast",
    5: "renter/apartment lower-income profile versus older educated condo and citizenship contrast",
    6: "condo/older profile versus renter dense-stability profile",
}


@dataclass(frozen=True)
class PlsSpec:
    model_id: str
    outcome: str
    predictors: tuple[str, ...]
    summary_path: Path
    loadings_path: Path
    importance_path: Path
    source_report: str


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"ct_id": "string", "ctuid": "string", "dguid": "string"})


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, na_rep="", float_format="%.10g")


def json_value(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def base_geometry() -> tuple[dict, dict[str, dict]]:
    collection = json.loads(BASE_MAP.read_text(encoding="utf-8"))
    geometry = {}
    for feature in collection["features"]:
        ct_id = str(feature["properties"]["ct_id"])
        geometry[ct_id] = feature["geometry"]
    return collection, geometry


def write_geojson(frame: pd.DataFrame, path: Path, geometry: dict[str, dict]) -> None:
    features = []
    for row in frame.to_dict(orient="records"):
        ct_id = str(row["ct_id"])
        if ct_id not in geometry:
            raise ValueError(f"Missing geometry for CT {ct_id}")
        properties = {key: json_value(value) for key, value in row.items()}
        features.append({"type": "Feature", "properties": properties, "geometry": geometry[ct_id]})
    payload = {"type": "FeatureCollection", "name": path.stem, "features": features}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def selected_theory_predictors() -> list[str]:
    decisions = read_csv(
        DATA_ROOT / "modelling/processed/dimension_reduction/theory_cleaned_pls/theory_cleaned_variable_decisions.csv"
    )
    selected = decisions["selected"].astype(str).str.lower().eq("true")
    return decisions.loc[selected, "variable"].tolist()


def one_column_list(path: Path) -> list[str]:
    frame = read_csv(path)
    return frame.iloc[:, 0].dropna().astype(str).tolist()


def specs(model_input: pd.DataFrame) -> list[PlsSpec]:
    dr = DATA_ROOT / "modelling/processed/dimension_reduction"
    full_predictors = wf.predictor_universe(model_input)
    theory_predictors = selected_theory_predictors()
    block_predictors = one_column_list(dr / "block1_3_restricted_latents/block1_3_cleaned_predictors.csv")
    rows = [
        PlsSpec(
            "full_unfiltered_mean_pls",
            OUTCOMES["mean"],
            tuple(full_predictors),
            dr / "full_pls/full_unfiltered_pls_summary.csv",
            dr / "full_pls/full_unfiltered_pls_component_loadings.csv",
            dr / "full_pls/full_unfiltered_pls_variable_importance.csv",
            "dimension_reduction/reports/task1_full_pls_summary.md",
        ),
        PlsSpec(
            "theory_cleaned_mean_pls",
            OUTCOMES["mean"],
            tuple(theory_predictors),
            dr / "theory_cleaned_pls/theory_cleaned_pls_summary.csv",
            dr / "theory_cleaned_pls/theory_cleaned_pls_component_loadings.csv",
            dr / "theory_cleaned_pls/theory_cleaned_pls_variable_importance.csv",
            "dimension_reduction/reports/task3_theory_cleaned_pls_report.md",
        ),
        PlsSpec(
            "blocks_1_3_cleaned_mean_pls",
            OUTCOMES["mean"],
            tuple(block_predictors),
            dr / "block1_3_restricted_latents/cleaned_block1_3_pls/block1_3_cleaned_pls_summary.csv",
            dr / "block1_3_restricted_latents/cleaned_block1_3_pls/block1_3_cleaned_pls_component_loadings.csv",
            dr / "block1_3_restricted_latents/cleaned_block1_3_pls/block1_3_cleaned_pls_variable_importance.csv",
            "dimension_reduction/block1_3_restricted_latents/block1_3_restricted_latent_report.md",
        ),
    ]
    comparison_root = dr / "meeting_PLS/turnout_level_comparisons/models"
    for level, outcome in OUTCOMES.items():
        rows.append(
            PlsSpec(
                f"meeting_{level}_pls",
                outcome,
                tuple(meeting.MEETING_VARIABLES),
                comparison_root / level / "pls" / f"{level}_meeting_pls_summary.csv",
                comparison_root / level / "pls" / f"{level}_meeting_pls_component_loadings.csv",
                comparison_root / level / "pls" / f"{level}_meeting_pls_variable_importance.csv",
                (
                    "dimension_reduction/meeting_PLS/meeting_pls_report.md"
                    if level == "mean"
                    else f"dimension_reduction/meeting_PLS/turnout_level_comparisons/reports/{level}_vs_mean_meeting_latent_report.md"
                ),
            )
        )
    return rows


def fit_spec(frame: pd.DataFrame, spec: PlsSpec) -> dict:
    summary = read_csv(spec.summary_path).iloc[0]
    n_components = int(summary["selected_components"])
    xdf = frame[list(spec.predictors)].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(frame[spec.outcome], errors="coerce")
    keep = y.notna() & xdf.notna().all(axis=1)
    x = xdf.loc[keep].to_numpy(float)
    y_values = y.loc[keep].to_numpy(float)
    model = wf.fit_pls(x, y_values, n_components)
    train_prediction = wf.predict_pls(model, x)
    cv_prediction = wf.cv_predictions(x, y_values, n_components)
    return {
        "summary": summary,
        "keep": keep,
        "model": model,
        "y": y_values,
        "train_prediction": train_prediction,
        "cv_prediction": cv_prediction,
    }


def build_observed(geometry: dict[str, dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed = read_csv(VARIABLE_MASTER)
    observed = observed.sort_values("ct_id").reset_index(drop=True)
    if len(observed) != 585 or observed["ct_id"].duplicated().any():
        raise ValueError("Observed-variable master is not a unique 585-CT table")
    write_csv(observed, OBSERVED_DIR / "toronto_ct_2021_observed_variables.csv")
    write_geojson(observed, OBSERVED_DIR / "toronto_ct_2021_observed_variables.geojson", geometry)

    geography_cols = [
        "ct_id",
        "ctuid",
        "dguid",
        "geo_name",
        "census_year",
        "land_area_km2",
        "population_total",
        "population_18plus",
        "citizen_canadian_18plus_count",
    ]
    geography = observed[geography_cols].copy()
    write_csv(geography, GEOGRAPHY_DIR / "toronto_ct_2021_geography.csv")
    write_geojson(geography, GEOGRAPHY_DIR / "toronto_ct_2021_geography.geojson", geometry)
    return observed, geography


def build_election_results(observed: pd.DataFrame, geometry: dict[str, dict]) -> pd.DataFrame:
    election_files = {
        "municipal_2023_mayor": DATA_ROOT / "interpolation/processed/municipal_2023_mayor_ct_estimated_results.csv",
        "provincial_2025": DATA_ROOT / "interpolation/processed/provincial_2025_ct_estimated_results.csv",
        "federal_2025": DATA_ROOT / "interpolation/processed/federal_2025_ct_estimated_results.csv",
    }
    result = observed[ID_COLUMNS + ["census_year"]].copy()
    repeated = {"election_id", "citizen_canadian_18over", "citizen_canadian_18over_status"}
    for prefix, path in election_files.items():
        election = read_csv(path)
        if len(election) != 585 or election["ct_id"].duplicated().any():
            raise ValueError(f"{path.name} is not a unique 585-CT table")
        keep = [column for column in election.columns if column not in repeated and column != "ct_id"]
        election = election[["ct_id", *keep]].rename(columns={column: f"{prefix}_{column}" for column in keep})
        result = result.merge(election, on="ct_id", how="left", validate="one_to_one")
    write_csv(result, OBSERVED_DIR / "toronto_ct_election_results.csv")
    write_geojson(result, OBSERVED_DIR / "toronto_ct_election_results.geojson", geometry)
    return result


def build_candidate_results() -> pd.DataFrame:
    candidate_paths = [
        DATA_ROOT / "interpolation/processed/municipal_2023_mayor_ct_candidate_estimated_votes.csv",
        DATA_ROOT / "interpolation/processed/provincial_2025_ct_candidate_estimated_votes.csv",
        DATA_ROOT / "interpolation/processed/federal_2025_ct_candidate_estimated_votes.csv",
    ]
    denominator_paths = [
        DATA_ROOT / "interpolation/processed/municipal_2023_mayor_ct_estimated_results.csv",
        DATA_ROOT / "interpolation/processed/provincial_2025_ct_estimated_results.csv",
        DATA_ROOT / "interpolation/processed/federal_2025_ct_estimated_results.csv",
    ]
    candidates = pd.concat([read_csv(path) for path in candidate_paths], ignore_index=True)
    denominators = pd.concat(
        [read_csv(path)[["election_id", "ct_id", "estimated_valid_candidate_votes"]] for path in denominator_paths],
        ignore_index=True,
    )
    candidates = candidates.merge(denominators, on=["election_id", "ct_id"], how="left", validate="many_to_one")
    candidates["estimated_candidate_vote_share"] = (
        pd.to_numeric(candidates["estimated_candidate_votes"], errors="coerce")
        / pd.to_numeric(candidates["estimated_valid_candidate_votes"], errors="coerce").replace(0, np.nan)
    )
    candidates["candidate_results_available_flag"] = pd.to_numeric(
        candidates["estimated_valid_candidate_votes"], errors="coerce"
    ).gt(0)
    candidate_rank = (
        candidates.groupby(["election_id", "ct_id"])["estimated_candidate_votes"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )
    candidates["candidate_rank_in_ct"] = candidate_rank.where(candidates["candidate_results_available_flag"])
    candidates["candidate_winner_in_ct_flag"] = (
        candidates["candidate_results_available_flag"] & candidates["candidate_rank_in_ct"].eq(1)
    )
    candidates = candidates.drop(columns=["estimated_valid_candidate_votes"])
    candidates = candidates.sort_values(
        ["election_id", "ct_id", "candidate_rank_in_ct", "candidate_id"], na_position="last"
    ).reset_index(drop=True)
    key = ["election_id", "ct_id", "candidate_id"]
    if candidates.duplicated(key).any():
        raise ValueError("Candidate result key is not unique")
    write_csv(candidates, OBSERVED_DIR / "toronto_ct_candidate_results.csv")
    return candidates


def build_modelled(
    observed: pd.DataFrame, geometry: dict[str, dict]
) -> tuple[pd.DataFrame, pd.DataFrame, list[PlsSpec], dict[str, dict]]:
    model_input = read_csv(MODEL_INPUT).sort_values("ct_id").reset_index(drop=True)
    if model_input["ct_id"].tolist() != observed["ct_id"].tolist():
        raise ValueError("Model input CT order/universe differs from observed variables")
    model_specs = specs(model_input)
    latent = observed[ID_COLUMNS].copy()
    results = observed[ID_COLUMNS].copy()
    fitted: dict[str, dict] = {}

    for spec in model_specs:
        fit = fit_spec(model_input, spec)
        fitted[spec.model_id] = fit
        keep = fit["keep"]
        model = fit["model"]
        for component in range(model.scores.shape[1]):
            name = f"{spec.model_id}_component_{component + 1}"
            values = pd.Series(np.nan, index=model_input.index, dtype=float)
            values.loc[keep] = model.scores[:, component]
            latent[f"{name}_score"] = values
            latent[f"{name}_percentile"] = values.rank(method="average", pct=True)

        observed_y = pd.to_numeric(model_input[spec.outcome], errors="coerce")
        train = pd.Series(np.nan, index=model_input.index, dtype=float)
        cv = pd.Series(np.nan, index=model_input.index, dtype=float)
        train.loc[keep] = fit["train_prediction"]
        cv.loc[keep] = fit["cv_prediction"]
        results[f"{spec.model_id}_fitted_participation"] = train
        results[f"{spec.model_id}_residual"] = observed_y - train
        results[f"{spec.model_id}_cv_prediction"] = cv
        results[f"{spec.model_id}_cv_residual"] = observed_y - cv
        results[f"{spec.model_id}_included_flag"] = keep

    spatial_paths = [
        DATA_ROOT / "modelling/processed/spatial_models/combined_model_e_trimmed_residuals.csv",
        DATA_ROOT / "modelling/processed/spatial_models/full_all_variables_model_e_residuals.csv",
        DATA_ROOT / "modelling/processed/spatial_models/updated_selected_combined_model_e_trimmed_residuals.csv",
    ]
    for path in spatial_paths:
        if not path.exists():
            continue
        spatial = read_csv(path)
        for model_id, group in spatial.groupby("model_id"):
            prefix = re.sub(r"[^a-z0-9]+", "_", str(model_id).lower()).strip("_")
            group = group[["ct_id", "observed", "spatial_residual", "spatial_filtered_residual"]].copy()
            group[f"{prefix}_fitted"] = group["observed"] - group["spatial_residual"]
            group[f"{prefix}_spatial_residual"] = group["spatial_residual"]
            group[f"{prefix}_spatial_filtered_fitted"] = group["observed"] - group["spatial_filtered_residual"]
            group[f"{prefix}_spatial_filtered_residual"] = group["spatial_filtered_residual"]
            group = group.drop(columns=["observed", "spatial_residual", "spatial_filtered_residual"])
            results = results.merge(group, on="ct_id", how="left", validate="one_to_one")

    spatial_cv_path = (
        DATA_ROOT
        / "modelling/processed/dimension_reduction/meeting_PLS/turnout_level_comparisons/advanced_validation"
        / "01_spatial_nested_cv/spatial_nested_cv_predictions.csv"
    )
    if spatial_cv_path.exists():
        spatial_cv = read_csv(spatial_cv_path)
        for (outcome, method), group in spatial_cv.groupby(["outcome", "method"]):
            prefix = f"meeting_{outcome}_{method}_spatial_nested_cv"
            group = group[["ct_id", "spatial_block", "prediction", "residual"]].rename(
                columns={
                    "spatial_block": f"{prefix}_block",
                    "prediction": f"{prefix}_prediction",
                    "residual": f"{prefix}_residual",
                }
            )
            results = results.merge(group, on="ct_id", how="left", validate="one_to_one")

    write_csv(latent, MODELLED_DIR / "toronto_ct_latent_scores.csv")
    write_geojson(latent, MODELLED_DIR / "toronto_ct_latent_scores.geojson", geometry)
    write_csv(results, MODELLED_DIR / "toronto_ct_turnout_model_results.csv")
    write_geojson(results, MODELLED_DIR / "toronto_ct_turnout_model_results.geojson", geometry)
    return latent, results, model_specs, fitted


def build_meeting_dataset(
    observed: pd.DataFrame, latent: pd.DataFrame, results: pd.DataFrame, geometry: dict[str, dict]
) -> pd.DataFrame:
    columns = ID_COLUMNS + ["census_year", *meeting.MEETING_VARIABLES, *OUTCOMES.values()]
    meeting_data = observed[columns].copy()
    latent_cols = [column for column in latent.columns if column.startswith("meeting_")]
    result_cols = [
        column
        for column in results.columns
        if column.startswith("meeting_") and "_spatial_nested_cv_" not in column
    ]
    meeting_data = meeting_data.merge(latent[["ct_id", *latent_cols]], on="ct_id", how="left", validate="one_to_one")
    meeting_data = meeting_data.merge(results[["ct_id", *result_cols]], on="ct_id", how="left", validate="one_to_one")
    write_csv(meeting_data, MEETING_DIR / "toronto_ct_meeting_pls.csv")
    write_geojson(meeting_data, MEETING_DIR / "toronto_ct_meeting_pls.geojson", geometry)
    return meeting_data


def build_robustness_checks(geometry: dict[str, dict]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Collect existing robustness artifacts without fitting or predicting models."""
    source_root = DATA_ROOT / "modelling/processed/dimension_reduction/meeting_PLS/turnout_level_comparisons"
    geography = read_csv(GEOGRAPHY_DIR / "toronto_ct_2021_geography.csv")[ID_COLUMNS]
    pca_summary_rows = []
    pca_loading_rows = []
    elastic_summary_rows = []
    elastic_coefficient_rows = []
    validation_rows = []

    validation_root = source_root / "advanced_validation/01_spatial_nested_cv"
    spatial_predictions = read_csv(validation_root / "spatial_nested_cv_predictions.csv")
    spatial_summary = read_csv(validation_root / "spatial_nested_cv_summary.csv")
    spatial_blocks = read_csv(validation_root / "ct_spatial_blocks.csv")
    methods = ["supervised_pca", "elastic_net"]
    spatial_predictions = spatial_predictions[spatial_predictions["method"].isin(methods)].copy()
    spatial_summary = spatial_summary[spatial_summary["method"].isin(methods)].copy()
    expected_rows = len(geography) * len(OUTCOMES) * len(methods)
    key = ["ct_id", "outcome", "method"]
    if len(spatial_predictions) != expected_rows or spatial_predictions.duplicated(key).any():
        raise ValueError("Saved robustness spatial-CV predictions do not form a complete CT/outcome/method table")
    if len(spatial_blocks) != len(geography) or spatial_blocks["ct_id"].duplicated().any():
        raise ValueError("Saved spatial blocks are not unique for the canonical CT universe")

    results = geography.merge(
        spatial_blocks[["ct_id", "lon", "lat", "spatial_block"]],
        on="ct_id",
        how="left",
        validate="one_to_one",
    )

    for level, target in OUTCOMES.items():
        pca_root = source_root / "models" / level / "supervised_pca"
        pca_summary_path = pca_root / f"{level}_supervised_pca_summary.csv"
        pca_loading_path = pca_root / f"{level}_supervised_pca_loadings.csv"
        pca_summary_source = read_csv(pca_summary_path).iloc[0]
        pca_loading_source = read_csv(pca_loading_path)
        component_columns = [column for column in pca_loading_source if re.fullmatch(r"component_\d+", column)]
        pca_prefix = f"supervised_pca_{level}"
        for _, row in pca_loading_source.iterrows():
            for component in component_columns:
                pca_loading_rows.append(
                    {
                        "model_id": pca_prefix,
                        "outcome": target,
                        "component": component,
                        "variable": row["variable"],
                        "loading": row[component],
                        "absolute_loading": abs(float(row[component])),
                        "sign_convention": "Source SVD orientation; interpret relative high and low sides",
                        "source_file": str(pca_loading_path.relative_to(REPO_ROOT)),
                    }
                )
        pca_summary_rows.append(
            {
                "model_id": pca_prefix,
                "outcome": target,
                "n": int(pca_summary_source["n"]),
                "screening_rule": pca_summary_source["screen"],
                "selected_predictors": int(pca_summary_source["screened_predictor_count"]),
                "selected_components": int(pca_summary_source["n_components"]),
                "train_r2": float(pca_summary_source["train_r2"]),
                "shuffled_cv_r2": float(pca_summary_source["cv_r2"]),
                "shuffled_cv_rmse": float(pca_summary_source["cv_rmse"]),
                "source_file": str(pca_summary_path.relative_to(REPO_ROOT)),
            }
        )

        elastic_root = source_root / "models" / level / "elastic_net"
        elastic_summary_path = elastic_root / f"{level}_elastic_net_summary.csv"
        elastic_coefficient_path = elastic_root / f"{level}_elastic_net_coefficients.csv"
        elastic_summary_source = read_csv(elastic_summary_path).iloc[0]
        coefficient_source = read_csv(elastic_coefficient_path)
        elastic_prefix = f"elastic_net_{level}"
        for _, row in coefficient_source.iterrows():
            elastic_coefficient_rows.append(
                {
                    "model_id": elastic_prefix,
                    "outcome": target,
                    "term": row["variable"],
                    "scaled_coefficient": row["scaled_coefficient"],
                    "coefficient": row["coefficient"],
                    "selected": row["selected"],
                    "source_file": str(elastic_coefficient_path.relative_to(REPO_ROOT)),
                }
            )
        elastic_summary_rows.append(
            {
                "model_id": elastic_prefix,
                "outcome": target,
                "n": int(elastic_summary_source["n"]),
                "alpha": float(elastic_summary_source["alpha"]),
                "l1_ratio": float(elastic_summary_source["l1_ratio"]),
                "mean_selected_predictors_cv": float(elastic_summary_source["mean_selected_variables"]),
                "shuffled_cv_r2": float(elastic_summary_source["cv_r2"]),
                "shuffled_cv_rmse": float(elastic_summary_source["cv_rmse"]),
                "source_file": str(elastic_summary_path.relative_to(REPO_ROOT)),
            }
        )

        actual = spatial_predictions[spatial_predictions["outcome"].eq(level)].groupby("ct_id")["actual"].nunique()
        if actual.max() != 1:
            raise ValueError(f"Saved actual values disagree across robustness methods for {level}")
        outcome_values = (
            spatial_predictions[spatial_predictions["outcome"].eq(level)][["ct_id", "actual"]]
            .drop_duplicates("ct_id")
            .rename(columns={"actual": target})
        )
        results = results.merge(outcome_values, on="ct_id", how="left", validate="one_to_one")

        for method, prefix, source_summary in [
            ("supervised_pca", pca_prefix, pca_summary_source),
            ("elastic_net", elastic_prefix, elastic_summary_source),
        ]:
            spatial_metrics = spatial_summary[
                spatial_summary["outcome"].eq(level) & spatial_summary["method"].eq(method)
            ]
            if len(spatial_metrics) != 1:
                raise ValueError(f"Expected one saved spatial validation summary for {prefix}")
            spatial_row = spatial_metrics.iloc[0]
            validation_rows.append(
                {
                    "model_id": prefix,
                    "outcome": target,
                    "method": method,
                    "n": int(source_summary["n"]),
                    "shuffled_cv_r2": float(source_summary["cv_r2"]),
                    "shuffled_cv_rmse": float(source_summary["cv_rmse"]),
                    "spatial_nested_cv_r2": spatial_row["r2"],
                    "spatial_nested_cv_rmse": spatial_row["rmse"],
                    "spatial_nested_cv_mae": spatial_row["mae"],
                    "spatial_residual_neighbor_correlation": spatial_row["residual_neighbor_correlation"],
                    "shuffled_cv_source_file": str(
                        (pca_summary_path if method == "supervised_pca" else elastic_summary_path).relative_to(REPO_ROOT)
                    ),
                    "spatial_cv_source_file": str(
                        (validation_root / "spatial_nested_cv_summary.csv").relative_to(REPO_ROOT)
                    ),
                }
            )
            spatial = spatial_predictions[
                spatial_predictions["outcome"].eq(level) & spatial_predictions["method"].eq(method)
            ][["ct_id", "prediction", "residual"]].rename(
                columns={
                    "prediction": f"{prefix}_spatial_nested_cv_prediction",
                    "residual": f"{prefix}_spatial_nested_cv_residual",
                }
            )
            results = results.merge(spatial, on="ct_id", how="left", validate="one_to_one")

    outputs = {
        "supervised_pca_model_summary.csv": pd.DataFrame(pca_summary_rows),
        "supervised_pca_loadings.csv": pd.DataFrame(pca_loading_rows),
        "elastic_net_model_summary.csv": pd.DataFrame(elastic_summary_rows),
        "elastic_net_coefficients.csv": pd.DataFrame(elastic_coefficient_rows),
        "robustness_validation_summary.csv": pd.DataFrame(validation_rows),
    }
    results = results.sort_values("ct_id").reset_index(drop=True)
    write_csv(results, ROBUSTNESS_DIR / "toronto_ct_meeting_robustness_spatial_cv.csv")
    write_geojson(results, ROBUSTNESS_DIR / "toronto_ct_meeting_robustness_spatial_cv.geojson", geometry)
    for name, frame in outputs.items():
        write_csv(frame, ROBUSTNESS_DIR / name)
    return results, outputs


def build_model_definitions(
    model_specs: list[PlsSpec], fitted: dict[str, dict], model_input: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    summary_rows = []
    predictor_rows = []
    loading_rows = []
    importance_rows = []
    coefficient_rows = []
    component_rows = []

    for spec in model_specs:
        fit = fitted[spec.model_id]
        summary = fit["summary"]
        summary_rows.append(
            {
                "model_id": spec.model_id,
                "method": "PLS1",
                "outcome": spec.outcome,
                "n": int(summary["n"]),
                "num_predictors": int(summary["num_predictors"]),
                "selected_components": int(summary["selected_components"]),
                "train_r2": float(summary["train_r2"]),
                "train_rmse": float(summary["train_rmse"]),
                "cv_r2": float(summary["cv_r2"]),
                "cv_rmse": float(summary["cv_rmse"]),
                "component_score_definition": "PLS X-score from the fitted, standardized predictor matrix with sequential deflation",
                "cv_definition": "Repository fixed shuffled 10-fold cross-validation",
                "source_summary": str(spec.summary_path.relative_to(DATA_ROOT)),
                "source_report": spec.source_report,
            }
        )
        for order, variable in enumerate(spec.predictors, start=1):
            predictor_rows.append(
                {
                    "model_id": spec.model_id,
                    "predictor_order": order,
                    "variable": variable,
                    "meeting_selected_flag": variable in meeting.MEETING_VARIABLES,
                }
            )

        loadings = read_csv(spec.loadings_path)
        importance = read_csv(spec.importance_path)
        for _, row in loadings.iterrows():
            for component in [column for column in loadings.columns if re.fullmatch(r"component_\d+", column)]:
                loading_rows.append(
                    {
                        "model_id": spec.model_id,
                        "component": component,
                        "variable": row["variable"],
                        "loading": row[component],
                        "absolute_loading": abs(float(row[component])),
                    }
                )
        for _, row in importance.iterrows():
            importance_rows.append(
                {
                    "model_id": spec.model_id,
                    "variable": row["variable"],
                    "block": row.get("block", ""),
                    "family": row.get("family", ""),
                    "vip": row.get("vip"),
                    "turnout_correlation": row.get("turnout_corr"),
                    "direction": row.get("direction", ""),
                }
            )
            coefficient_rows.append(
                {
                    "model_id": spec.model_id,
                    "outcome": spec.outcome,
                    "variable": row["variable"],
                    "pls_coefficient": row.get("pls_coefficient"),
                }
            )

        score_frame = model_input.loc[fit["keep"]]
        for component_index in range(fit["model"].scores.shape[1]):
            component_number = component_index + 1
            score = pd.Series(fit["model"].scores[:, component_index], index=score_frame.index)
            outcome = pd.to_numeric(score_frame[spec.outcome], errors="coerce")
            comp_loadings = loadings.set_index("variable")[f"component_{component_number}"].sort_values()
            high = "; ".join(comp_loadings.tail(3).sort_values(ascending=False).index)
            low = "; ".join(comp_loadings.head(3).index)
            if spec.model_id == "meeting_mean_pls":
                label = MEETING_COMPONENT_LABELS.get(component_number, f"Component {component_number}")
            elif spec.model_id == "blocks_1_3_cleaned_mean_pls":
                label = BLOCK_COMPONENT_LABELS.get(component_number, f"Component {component_number}")
            else:
                label = f"High: {high}; low: {low}"
            component_rows.append(
                {
                    "model_id": spec.model_id,
                    "component": f"component_{component_number}",
                    "component_label": label,
                    "high_loading_variables": high,
                    "low_loading_variables": low,
                    "score_outcome_correlation": float(score.corr(outcome)),
                    "sign_convention": "Algorithmic PLS1 orientation from positive X'Y weight at fitting; interpret relative high versus low sides",
                }
            )

    frames = {
        "toronto_turnout_model_summary.csv": pd.DataFrame(summary_rows),
        "toronto_turnout_model_predictors.csv": pd.DataFrame(predictor_rows),
        "toronto_turnout_component_loadings.csv": pd.DataFrame(loading_rows),
        "toronto_turnout_variable_importance.csv": pd.DataFrame(importance_rows),
        "toronto_turnout_model_coefficients.csv": pd.DataFrame(coefficient_rows),
        "toronto_turnout_component_dictionary.csv": pd.DataFrame(component_rows),
    }
    for name, frame in frames.items():
        write_csv(frame, DEFINITIONS_DIR / name)
    return frames


def infer_variable_group(variable: str) -> str:
    if variable in ID_COLUMNS or variable in {"census_year"}:
        return "identifier"
    if variable.startswith("block1_"):
        return "block_1_demographic_socioeconomic"
    if variable.startswith("block2_"):
        return "block_2_housing_stability"
    if variable.startswith("block3_"):
        return "block_3_immigration_eligibility"
    if variable.startswith("block4_"):
        return "block_4_electoral_competitiveness"
    if variable.startswith("block5_"):
        return "block_5_transport_services_access"
    if variable.startswith("outcome_"):
        return "election_outcome"
    if "score" in variable or "percentile" in variable:
        return "latent_score"
    if "residual" in variable or "prediction" in variable or "fitted" in variable:
        return "model_result"
    return "supporting_measure"


def default_description(variable: str) -> str:
    readable = variable.replace("_", " ")
    if variable == "ct_id":
        return "Canonical 2021 Toronto census-tract join identifier; read as text."
    if "supervised_pca" in variable and variable.endswith("_score"):
        return f"Fitted supervised-PCA component score for {readable.removesuffix(' score')}."
    if variable.endswith("_score"):
        return f"Fitted PLS X-score for {readable.removesuffix(' score')}."
    if variable.endswith("_percentile"):
        return f"Within-model CT percentile rank for {readable.removesuffix(' percentile')}."
    if variable.endswith("_cv_prediction"):
        return f"Fixed shuffled 10-fold cross-validation prediction for {readable.removesuffix(' cv prediction')}."
    if variable.endswith("_cv_residual"):
        return f"Observed participation minus shuffled-CV prediction for {readable.removesuffix(' cv residual')}."
    if variable.endswith("_residual"):
        return f"Observed value minus fitted or predicted value for {readable.removesuffix(' residual')}."
    if variable.endswith("_fitted_participation") or variable.endswith("_fitted"):
        return f"In-sample fitted value for {readable}."
    if variable.endswith("_flag"):
        return f"Boolean quality, availability, or inclusion indicator: {readable}."
    return readable.capitalize() + "."


def first_text(*values) -> str:
    for value in values:
        if value is None or pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def existing_dictionary_lookup() -> dict[str, dict]:
    path = DATA_ROOT / "variables/metadata/toronto_ct_blocks_1_5_variable_dictionary.csv"
    dictionary = read_csv(path)
    return {str(row["variable_name"]): row.to_dict() for _, row in dictionary.iterrows()}


def build_metadata(
    datasets: dict[str, pd.DataFrame], geometry_files: list[Path], definition_frames: dict[str, pd.DataFrame]
) -> None:
    existing = existing_dictionary_lookup()
    variable_rows = []
    for dataset_name, frame in datasets.items():
        for column in frame.columns:
            source = existing.get(column, {})
            variable_rows.append(
                {
                    "dataset": dataset_name,
                    "variable_name": column,
                    "variable_group": infer_variable_group(column),
                    "description": first_text(source.get("formula"), source.get("assumptions"), default_description(column)),
                    "units": source.get("units", ""),
                    "numerator": source.get("numerator", ""),
                    "denominator": source.get("denominator", ""),
                    "source": first_text(
                        source.get("official_data_source"), "Derived from existing processed project artifacts"
                    ),
                    "missing_count": int(frame[column].isna().sum()),
                    "data_type": str(frame[column].dtype),
                }
            )
    variable_detail = pd.DataFrame(variable_rows)
    compact_rows = []
    for variable, group in variable_detail.groupby("variable_name", sort=True):
        first = group.iloc[0]
        compact_rows.append(
            {
                "variable_name": variable,
                "datasets": "; ".join(sorted(group["dataset"].unique())),
                "variable_group": first["variable_group"],
                "description": first["description"],
                "units": first["units"],
                "numerator": first["numerator"],
                "denominator": first["denominator"],
                "source": first["source"],
                "maximum_missing_count": int(group["missing_count"].max()),
                "data_types": "; ".join(sorted(group["data_type"].unique())),
            }
        )
    write_csv(pd.DataFrame(compact_rows), METADATA_DIR / "variable_dictionary.csv")

    catalog_rows = [
        {
            "dataset": "toronto_ct_2021_geography",
            "grain": "one row/feature per 2021 Toronto analytical census tract",
            "primary_key": "ct_id",
            "purpose": "Canonical 585-CT identifiers and geometry",
            "csv": "geography/toronto_ct_2021_geography.csv",
            "geojson": "geography/toronto_ct_2021_geography.geojson",
        },
        {
            "dataset": "toronto_ct_2021_observed_variables",
            "grain": "one row per CT",
            "primary_key": "ct_id",
            "purpose": "Cleaned source-derived and engineered Blocks 1-5 variables and outcomes",
            "csv": "observed/toronto_ct_2021_observed_variables.csv",
            "geojson": "observed/toronto_ct_2021_observed_variables.geojson",
        },
        {
            "dataset": "toronto_ct_election_results",
            "grain": "one row per CT with election-prefixed columns",
            "primary_key": "ct_id",
            "purpose": "Full CT-estimated municipal, provincial, and federal election results",
            "csv": "observed/toronto_ct_election_results.csv",
            "geojson": "observed/toronto_ct_election_results.geojson",
        },
        {
            "dataset": "toronto_ct_candidate_results",
            "grain": "one row per CT, election, and candidate",
            "primary_key": "election_id + ct_id + candidate_id",
            "purpose": "Candidate-level CT-estimated votes, shares, ranks, and winner flags",
            "csv": "observed/toronto_ct_candidate_results.csv",
            "geojson": "",
        },
        {
            "dataset": "toronto_ct_latent_scores",
            "grain": "one row per CT",
            "primary_key": "ct_id",
            "purpose": "Fitted PLS X-scores and percentiles for retained latent models",
            "csv": "modelled/toronto_ct_latent_scores.csv",
            "geojson": "modelled/toronto_ct_latent_scores.geojson",
        },
        {
            "dataset": "toronto_ct_turnout_model_results",
            "grain": "one row per CT",
            "primary_key": "ct_id",
            "purpose": "Model fitted values, CV predictions, residuals, and inclusion flags",
            "csv": "modelled/toronto_ct_turnout_model_results.csv",
            "geojson": "modelled/toronto_ct_turnout_model_results.geojson",
        },
        {
            "dataset": "toronto_ct_meeting_pls",
            "grain": "one row per CT",
            "primary_key": "ct_id",
            "purpose": "Self-contained Aniket handoff: meeting variables, outcomes, latent scores, predictions, and residuals",
            "csv": "meeting_pls/toronto_ct_meeting_pls.csv",
            "geojson": "meeting_pls/toronto_ct_meeting_pls.geojson",
        },
        {
            "dataset": "toronto_ct_meeting_robustness_spatial_cv",
            "grain": "one row per CT",
            "primary_key": "ct_id",
            "purpose": "Saved supervised-PCA and elastic-net spatial nested-CV predictions and residuals",
            "csv": "robustness_checks/toronto_ct_meeting_robustness_spatial_cv.csv",
            "geojson": "robustness_checks/toronto_ct_meeting_robustness_spatial_cv.geojson",
        },
    ]
    write_csv(pd.DataFrame(catalog_rows), METADATA_DIR / "dataset_catalog.csv")

    qa_rows = []
    for name, frame in datasets.items():
        key = ["election_id", "ct_id", "candidate_id"] if name == "toronto_ct_candidate_results" else ["ct_id"]
        qa_rows.append(
            {
                "dataset": name,
                "rows": len(frame),
                "columns": len(frame.columns),
                "duplicate_primary_keys": int(frame.duplicated(key).sum()),
                "missing_ct_id": int(frame["ct_id"].isna().sum()),
                "unique_ct_count": int(frame["ct_id"].nunique()),
                "status": "pass" if frame.duplicated(key).sum() == 0 and frame["ct_id"].isna().sum() == 0 else "fail",
            }
        )
    write_csv(pd.DataFrame(qa_rows), METADATA_DIR / "qa_summary.csv")

    source_paths = sorted(
        {
            VARIABLE_MASTER,
            MODEL_INPUT,
            BASE_MAP,
            DATA_ROOT / "variables/metadata/toronto_ct_blocks_1_5_variable_dictionary.csv",
            DATA_ROOT / "modelling/processed/dimension_reduction/theory_cleaned_pls/theory_cleaned_variable_decisions.csv",
            DATA_ROOT / "modelling/processed/dimension_reduction/block1_3_restricted_latents/block1_3_cleaned_predictors.csv",
            DATA_ROOT / "interpolation/processed/municipal_2023_mayor_ct_estimated_results.csv",
            DATA_ROOT / "interpolation/processed/provincial_2025_ct_estimated_results.csv",
            DATA_ROOT / "interpolation/processed/federal_2025_ct_estimated_results.csv",
            DATA_ROOT / "interpolation/processed/municipal_2023_mayor_ct_candidate_estimated_votes.csv",
            DATA_ROOT / "interpolation/processed/provincial_2025_ct_candidate_estimated_votes.csv",
            DATA_ROOT / "interpolation/processed/federal_2025_ct_candidate_estimated_votes.csv",
            DATA_ROOT / "modelling/processed/spatial_models/combined_model_e_trimmed_residuals.csv",
            DATA_ROOT / "modelling/processed/spatial_models/full_all_variables_model_e_residuals.csv",
            DATA_ROOT / "modelling/processed/spatial_models/updated_selected_combined_model_e_trimmed_residuals.csv",
            *(spec.summary_path for spec in specs(read_csv(MODEL_INPUT))),
            *(spec.loadings_path for spec in specs(read_csv(MODEL_INPUT))),
            *(spec.importance_path for spec in specs(read_csv(MODEL_INPUT))),
        }
    )
    spatial_cv_source = (
        DATA_ROOT
        / "modelling/processed/dimension_reduction/meeting_PLS/turnout_level_comparisons/advanced_validation"
        / "01_spatial_nested_cv/spatial_nested_cv_predictions.csv"
    )
    if spatial_cv_source.exists():
        source_paths.append(spatial_cv_source)
        source_paths = sorted(set(source_paths))
    robustness_source_root = (
        DATA_ROOT / "modelling/processed/dimension_reduction/meeting_PLS/turnout_level_comparisons/models"
    )
    for level in OUTCOMES:
        source_paths.extend(
            [
                robustness_source_root / level / "supervised_pca" / f"{level}_supervised_pca_summary.csv",
                robustness_source_root / level / "supervised_pca" / f"{level}_supervised_pca_loadings.csv",
                robustness_source_root / level / "elastic_net" / f"{level}_elastic_net_summary.csv",
                robustness_source_root / level / "elastic_net" / f"{level}_elastic_net_coefficients.csv",
            ]
        )
    robustness_validation_root = (
        DATA_ROOT
        / "modelling/processed/dimension_reduction/meeting_PLS/turnout_level_comparisons/advanced_validation"
        / "01_spatial_nested_cv"
    )
    for name in ["ct_spatial_blocks.csv", "spatial_nested_cv_summary.csv"]:
        path = robustness_validation_root / name
        if path.exists():
            source_paths.append(path)
    source_paths = sorted(set(source_paths))
    source_rows = []
    for path in source_paths:
        source_rows.append(
            {
                "source_file": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
        )
    write_csv(pd.DataFrame(source_rows), METADATA_DIR / "source_manifest.csv")

    output_paths = sorted(path for path in FINAL_ROOT.rglob("*") if path.is_file() and path.name != "release_manifest.json")
    release = {
        "release_name": "toronto_ct_turnout_final",
        "canonical_ct_count": 585,
        "ct_key": "ct_id",
        "geometry_crs": "EPSG:4326",
        "build_script": str(Path(__file__).relative_to(REPO_ROOT)),
        "files": [
            {
                "path": str(path.relative_to(FINAL_ROOT)),
                "sha256": sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for path in output_paths
        ],
    }
    (METADATA_DIR / "release_manifest.json").write_text(json.dumps(release, indent=2), encoding="utf-8")


def main() -> None:
    for directory in [
        GEOGRAPHY_DIR,
        OBSERVED_DIR,
        MODELLED_DIR,
        MEETING_DIR,
        ROBUSTNESS_DIR,
        DEFINITIONS_DIR,
        METADATA_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
    _, geometry = base_geometry()
    observed, geography = build_observed(geometry)
    election_results = build_election_results(observed, geometry)
    candidates = build_candidate_results()
    latent, model_results, model_specs, fitted = build_modelled(observed, geometry)
    meeting_data = build_meeting_dataset(observed, latent, model_results, geometry)
    robustness_results, robustness_definitions = build_robustness_checks(geometry)
    definitions = build_model_definitions(model_specs, fitted, read_csv(MODEL_INPUT).sort_values("ct_id").reset_index(drop=True))
    datasets = {
        "toronto_ct_2021_geography": geography,
        "toronto_ct_2021_observed_variables": observed,
        "toronto_ct_election_results": election_results,
        "toronto_ct_candidate_results": candidates,
        "toronto_ct_latent_scores": latent,
        "toronto_ct_turnout_model_results": model_results,
        "toronto_ct_meeting_pls": meeting_data,
        "toronto_ct_meeting_robustness_spatial_cv": robustness_results,
    }
    build_metadata(datasets, list(FINAL_ROOT.rglob("*.geojson")), definitions)
    print(f"Built final CT release at {FINAL_ROOT}")


def collect_robustness_only() -> None:
    """Refresh robustness deliverables and release metadata from saved artifacts only."""
    ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)
    _, geometry = base_geometry()
    robustness_results, _ = build_robustness_checks(geometry)
    dataset_paths = {
        "toronto_ct_2021_geography": GEOGRAPHY_DIR / "toronto_ct_2021_geography.csv",
        "toronto_ct_2021_observed_variables": OBSERVED_DIR / "toronto_ct_2021_observed_variables.csv",
        "toronto_ct_election_results": OBSERVED_DIR / "toronto_ct_election_results.csv",
        "toronto_ct_candidate_results": OBSERVED_DIR / "toronto_ct_candidate_results.csv",
        "toronto_ct_latent_scores": MODELLED_DIR / "toronto_ct_latent_scores.csv",
        "toronto_ct_turnout_model_results": MODELLED_DIR / "toronto_ct_turnout_model_results.csv",
        "toronto_ct_meeting_pls": MEETING_DIR / "toronto_ct_meeting_pls.csv",
    }
    datasets = {name: read_csv(path) for name, path in dataset_paths.items()}
    datasets["toronto_ct_meeting_robustness_spatial_cv"] = robustness_results
    build_metadata(datasets, list(FINAL_ROOT.rglob("*.geojson")), {})
    print(f"Collected saved robustness artifacts at {ROBUSTNESS_DIR}")


if __name__ == "__main__":
    if "--collect-robustness-only" in sys.argv:
        collect_robustness_only()
    else:
        main()
