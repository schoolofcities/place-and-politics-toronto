"""Run supervised dimension-reduction and multicollinearity diagnostics.

This workflow treats mean CT turnout as the supervising outcome. It produces:
- a full, unfiltered PLS model with VIP scores;
- correlation/VIF/redundancy diagnostics over the full predictor universe;
- a theory-cleaned PLS model selected through variable-family comparisons.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
import math
import re

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[5]
INPUT = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "modelling"
    / "processed"
    / "spatial_models"
    / "toronto_ct_blocks_1_5_model_input_housing_augmented_median_imputed.csv"
)
OUTPUT_ROOT = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "modelling"
    / "processed"
    / "dimension_reduction"
)
REPORT_ROOT = OUTPUT_ROOT / "reports"
FULL_ROOT = OUTPUT_ROOT / "full_pls"
DIAG_ROOT = OUTPUT_ROOT / "diagnostics"
CLEAN_ROOT = OUTPUT_ROOT / "theory_cleaned_pls"
INTERACTION_ROOT = OUTPUT_ROOT / "interaction_discovery"
SPARSE_ROOT = OUTPUT_ROOT / "sparse_pls"
SUPERVISED_PCA_ROOT = OUTPUT_ROOT / "supervised_pca"
ELASTIC_NET_ROOT = OUTPUT_ROOT / "elastic_net_robustness"

TARGET = "outcome_mean_participation_citizen_18plus"
MAX_COMPONENTS = 12
CV_FOLDS = 10
RANDOM_SEED = 20260803


BLOCKS = {
    "block_1_demographic": [
        "block1_age_18_34_share",
        "block1_age_35_64_share",
        "block1_age_65_plus_share",
        "block1_median_age",
        "block1_average_household_size",
        "block1_bachelors_or_higher_25_64_share",
        "block1_low_income_lim_at_share",
        "block1_unemployment_rate_share",
    ],
    "block_2_housing_stability": [
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
    "block_3_immigration_eligibility": [
        "block3_immigrant_share",
        "block3_recent_immigrant_share",
        "block3_non_citizen_share",
        "block3_citizen_adult_share",
        "block3_visible_minority_share",
        "block3_english_french_knowledge_share",
        "block3_non_official_mother_tongue_share",
    ],
    "block_4_competitiveness": [
        "block4_mayoral_top_two_margin",
        "block4_effective_mayoral_candidates_5pct",
        "block4_mayoral_vote_fragmentation",
        "block4_federal_margin",
        "block4_provincial_margin",
        "block4_effective_federal_parties_5pct",
        "block4_effective_provincial_parties_5pct",
    ],
    "block_5_municipal_services": [
        "block5_transit_commute_share_preferred",
        "block5_no_car_household_share",
        "block5_social_housing_share",
        "block5_requests_311_per_1000",
        "block5_library_access_1200m",
        "block5_community_centre_access_1200m",
        "block5_park_access_1200m",
        "block5_school_age_5_17_share",
        "block5_ksi_collision_events_2021_2025_per_1000",
        "block5_development_applications_2021_2025_per_1000",
        "block5_shelter_access_1200m",
    ],
}

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

FAMILIES = {
    "age_structure": [
        "block1_age_18_34_share",
        "block1_age_35_64_share",
        "block1_age_65_plus_share",
        "block1_median_age",
    ],
    "household_class": [
        "block1_average_household_size",
        "block1_bachelors_or_higher_25_64_share",
        "block1_low_income_lim_at_share",
        "block1_unemployment_rate_share",
    ],
    "housing_tenure": ["block2_renter_share", "block2_owner_share"],
    "residential_stability": ["block2_same_address_1yr_share", "block2_same_address_5yr_share"],
    "housing_form_density": [
        "block2_condo_share",
        "block2_apartment_share",
        "block2_detached_share",
        "block2_semi_detached_share",
        "block2_population_density_per_km2",
        "block2_structural_type_total_dwellings",
        "block2_apartment_duplex_count",
        "block2_apartment_lt5_storeys_count",
        "block2_apartment_5plus_storeys_count",
        "block2_apartment_total_count",
        "block2_condo_status_total_dwellings",
        "block2_condominium_dwellings_count",
        "block2_apartments_per_km2",
        "block2_condos_per_km2",
    ],
    "immigration_citizenship": [
        "block3_immigrant_share",
        "block3_recent_immigrant_share",
        "block3_non_citizen_share",
        "block3_citizen_adult_share",
        "block3_visible_minority_share",
        "block3_english_french_knowledge_share",
        "block3_non_official_mother_tongue_share",
    ],
    "mayoral_competitiveness": [
        "block4_mayoral_top_two_margin",
        "block4_mayoral_winner_margin",
        "block4_effective_mayoral_candidates_5pct",
        "block4_mayoral_candidate_count_5pct",
        "block4_mayoral_vote_fragmentation",
    ],
    "federal_competitiveness": [
        "block4_federal_margin",
        "block4_effective_federal_parties_5pct",
        "block4_federal_party_count_5pct",
        "block4_federal_vote_fragmentation",
    ],
    "provincial_competitiveness": [
        "block4_provincial_margin",
        "block4_effective_provincial_parties_5pct",
        "block4_provincial_party_count_5pct",
        "block4_provincial_vote_fragmentation",
    ],
    "transportation_access": [
        "block5_transit_commute_share_preferred",
        "block5_no_car_household_share",
        "block5_tts_no_car_household_share",
        "block5_tts_transit_trip_share",
        "block5_tts_overlap_area_m2",
    ],
    "service_access": [
        "block5_library_access_1200m",
        "block5_library_nearest_m",
        "block5_library_count_1200m",
        "block5_community_centre_access_1200m",
        "block5_community_centre_nearest_m",
        "block5_community_centre_count_1200m",
        "block5_park_access_1200m",
        "block5_park_nearest_m",
        "block5_park_count_1200m",
        "block5_shelter_access_1200m",
        "block5_shelter_nearest_m",
        "block5_shelter_count_1200m",
    ],
    "service_contact": [
        "block5_social_housing_share",
        "block5_requests_311_per_1000",
        "block5_ksi_collision_events_2021_2025_per_1000",
        "block5_development_applications_2021_2025_per_1000",
        "block5_school_age_5_17_share",
        "block5_ksi_collision_events_2021_2025",
        "block5_development_applications_2021_2025",
        "block5_requests_311_2023_2025_estimated_count",
    ],
}

THEORY_ANCHORS = {
    "age_structure": ["block1_age_18_34_share", "block1_age_65_plus_share"],
    "household_class": [
        "block1_average_household_size",
        "block1_bachelors_or_higher_25_64_share",
        "block1_low_income_lim_at_share",
    ],
    "housing_tenure": ["block2_renter_share"],
    "residential_stability": ["block2_same_address_5yr_share"],
    "housing_form_density": [
        "block2_apartment_share",
        "block2_condo_share",
        "block2_population_density_per_km2",
    ],
    "immigration_citizenship": [
        "block3_non_citizen_share",
        "block3_visible_minority_share",
        "block3_recent_immigrant_share",
    ],
    "mayoral_competitiveness": [
        "block4_mayoral_top_two_margin",
        "block4_effective_mayoral_candidates_5pct",
    ],
    "federal_competitiveness": ["block4_federal_margin"],
    "provincial_competitiveness": ["block4_provincial_margin"],
    "transportation_access": ["block5_transit_commute_share_preferred", "block5_no_car_household_share"],
    "service_access": [
        "block5_library_access_1200m",
        "block5_community_centre_access_1200m",
        "block5_park_access_1200m",
        "block5_shelter_access_1200m",
    ],
    "service_contact": [
        "block5_social_housing_share",
        "block5_requests_311_per_1000",
        "block5_ksi_collision_events_2021_2025_per_1000",
        "block5_development_applications_2021_2025_per_1000",
        "block5_school_age_5_17_share",
    ],
}


@dataclass
class PlsModel:
    x_mean: np.ndarray
    x_std: np.ndarray
    y_mean: float
    y_std: float
    weights: np.ndarray
    loadings: np.ndarray
    q: np.ndarray
    scores: np.ndarray
    coef_scaled: np.ndarray
    vip: np.ndarray


def safe_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def fmt(value: float | int | str | None, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(float(value)):
        return "inf" if float(value) > 0 else "-inf"
    return f"{float(value):.{digits}f}"


def md_table(rows: list[dict], columns: list[str], limit: int | None = None) -> str:
    shown = rows if limit is None else rows[:limit]
    if not shown:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(str(row.get(col, "")) for col in columns) + " |" for row in shown]
    return "\n".join([header, sep, *body]) + "\n"


PLAIN_VARIABLE_NAMES = {
    "block1_age_18_34_share": "age 18 to 34 share",
    "block1_age_35_64_share": "age 35 to 64 share",
    "block1_age_65_plus_share": "age 65 plus share",
    "block1_median_age": "median age",
    "block1_average_household_size": "average household size",
    "block1_bachelors_or_higher_25_64_share": "bachelor or higher education share",
    "block1_low_income_lim_at_share": "low income share",
    "block1_unemployment_rate_share": "unemployment rate",
    "block2_renter_share": "renter share",
    "block2_owner_share": "owner share",
    "block2_same_address_1yr_share": "same address one year share",
    "block2_same_address_5yr_share": "same address five year share",
    "block2_condo_share": "condo share",
    "block2_apartment_share": "apartment share",
    "block2_detached_share": "detached house share",
    "block2_semi_detached_share": "semi detached house share",
    "block2_population_density_per_km2": "population density",
    "block2_apartment_lt5_storeys_count": "apartment under five storeys count",
    "block2_apartment_5plus_storeys_count": "apartment five plus storeys count",
    "block2_apartment_total_count": "apartment total count",
    "block2_apartments_per_km2": "apartments per square kilometre",
    "block2_condos_per_km2": "condos per square kilometre",
    "block2_structural_type_total_dwellings": "structural type total dwellings",
    "block2_condo_status_total_dwellings": "condo status total dwellings",
    "block2_condominium_dwellings_count": "condominium dwellings count",
    "block3_immigrant_share": "immigrant share",
    "block3_recent_immigrant_share": "recent immigrant share",
    "block3_non_citizen_share": "non citizen share",
    "block3_citizen_adult_share": "citizen adult share",
    "block3_visible_minority_share": "visible minority share",
    "block3_english_french_knowledge_share": "English or French knowledge share",
    "block3_non_official_mother_tongue_share": "non official mother tongue share",
    "block4_mayoral_top_two_margin": "mayoral top two margin",
    "block4_mayoral_winner_margin": "mayoral winner margin",
    "block4_effective_mayoral_candidates_5pct": "effective mayoral candidates above five percent",
    "block4_mayoral_candidate_count_5pct": "mayoral candidate count above five percent",
    "block4_mayoral_vote_fragmentation": "mayoral vote fragmentation",
    "block4_federal_margin": "federal margin",
    "block4_effective_federal_parties_5pct": "effective federal parties above five percent",
    "block4_federal_party_count_5pct": "federal party count above five percent",
    "block4_federal_vote_fragmentation": "federal vote fragmentation",
    "block4_provincial_margin": "provincial margin",
    "block4_effective_provincial_parties_5pct": "effective provincial parties above five percent",
    "block4_provincial_party_count_5pct": "provincial party count above five percent",
    "block4_provincial_vote_fragmentation": "provincial vote fragmentation",
    "block5_transit_commute_share_preferred": "transit commute share",
    "block5_no_car_household_share": "no car household share",
    "block5_tts_no_car_household_share": "TTS no car household share",
    "block5_tts_transit_trip_share": "TTS transit trip share",
    "block5_social_housing_share": "social housing share",
    "block5_requests_311_per_1000": "311 requests per 1000 residents",
    "block5_requests_311_2023_2025_estimated_count": "311 estimated request count",
    "block5_library_access_1200m": "library access within 1200 metres",
    "block5_library_count_1200m": "library count within 1200 metres",
    "block5_community_centre_access_1200m": "community centre access within 1200 metres",
    "block5_park_access_1200m": "park access within 1200 metres",
    "block5_shelter_access_1200m": "shelter access within 1200 metres",
    "block5_shelter_count_1200m": "shelter count within 1200 metres",
    "block5_school_age_5_17_share": "school age children share",
    "block5_ksi_collision_events_2021_2025_per_1000": "KSI collisions per 1000 residents",
    "block5_development_applications_2021_2025_per_1000": "development applications per 1000 residents",
}


def plain_variable(name: str) -> str:
    return PLAIN_VARIABLE_NAMES.get(name, name.replace("__x__", " with ").replace("_", " "))


def plain_term(name: str) -> str:
    if "__x__" not in name:
        return plain_variable(name)
    left, right = name.split("__x__", 1)
    return f"{plain_variable(left)} with {plain_variable(right)}"


def plain_list(names: list[str], limit: int | None = None) -> str:
    shown = names if limit is None else names[:limit]
    return ", ".join(plain_term(name) for name in shown)


def predictor_universe(df: pd.DataFrame) -> list[str]:
    cols: list[str] = []
    for block_cols in BLOCKS.values():
        cols.extend(block_cols)
    cols.extend(ADDITIONAL_FULL_VARIABLES)
    available: list[str] = []
    seen = set()
    for col in cols:
        if col in seen or col not in df.columns:
            continue
        values = pd.to_numeric(df[col], errors="coerce")
        if values.notna().any() and values.std(skipna=True) > 0:
            available.append(col)
            seen.add(col)
    return available


def standardize_train(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    x_mean = np.nanmean(x, axis=0)
    x_std = np.nanstd(x, axis=0, ddof=0)
    x_std[x_std == 0] = 1
    y_mean = float(np.nanmean(y))
    y_std = float(np.nanstd(y, ddof=0)) or 1.0
    return (x - x_mean) / x_std, (y - y_mean) / y_std, x_mean, x_std, y_mean, y_std


def fit_pls(x: np.ndarray, y: np.ndarray, n_components: int) -> PlsModel:
    xs, ys, x_mean, x_std, y_mean, y_std = standardize_train(x, y)
    x_def = xs.copy()
    y_def = ys.copy()
    n, p = xs.shape
    comps = min(n_components, p, n - 1)
    weights = np.zeros((p, comps))
    loadings = np.zeros((p, comps))
    q = np.zeros(comps)
    scores = np.zeros((n, comps))
    ssy = np.zeros(comps)
    for comp in range(comps):
        w = x_def.T @ y_def
        norm = np.linalg.norm(w)
        if norm < 1e-12:
            weights = weights[:, :comp]
            loadings = loadings[:, :comp]
            q = q[:comp]
            scores = scores[:, :comp]
            ssy = ssy[:comp]
            break
        w = w / norm
        t = x_def @ w
        tt = float(t.T @ t)
        if tt < 1e-12:
            break
        p_load = (x_def.T @ t) / tt
        q_load = float((y_def.T @ t) / tt)
        x_def = x_def - np.outer(t, p_load)
        y_def = y_def - q_load * t
        weights[:, comp] = w
        loadings[:, comp] = p_load
        q[comp] = q_load
        scores[:, comp] = t
        ssy[comp] = (q_load**2) * tt

    if weights.shape[1] == 0:
        coef_scaled = np.zeros(p)
        vip = np.zeros(p)
    else:
        w_star = weights @ np.linalg.pinv(loadings.T @ weights)
        coef_scaled = w_star @ q
        total_ssy = float(ssy.sum()) or 1.0
        vip = np.sqrt(p * ((weights**2) @ ssy) / total_ssy)
    return PlsModel(x_mean, x_std, y_mean, y_std, weights, loadings, q, scores, coef_scaled, vip)


def predict_pls(model: PlsModel, x: np.ndarray) -> np.ndarray:
    xs = (x - model.x_mean) / model.x_std
    return (xs @ model.coef_scaled) * model.y_std + model.y_mean


def metrics(y: np.ndarray, pred: np.ndarray, k: int) -> dict[str, float]:
    resid = y - pred
    sse = float(np.sum(resid**2))
    sst = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1 - sse / sst if sst else 0.0
    n = len(y)
    adj = 1 - (1 - r2) * (n - 1) / max(n - k - 1, 1)
    rmse = math.sqrt(sse / n)
    return {"r2": r2, "adjusted_r2": adj, "rmse": rmse}


def cv_predictions(x: np.ndarray, y: np.ndarray, n_components: int) -> np.ndarray:
    rng = np.random.default_rng(RANDOM_SEED)
    indices = np.arange(len(y))
    rng.shuffle(indices)
    folds = np.array_split(indices, CV_FOLDS)
    pred = np.zeros_like(y, dtype=float)
    for fold in folds:
        train = np.setdiff1d(indices, fold, assume_unique=False)
        model = fit_pls(x[train], y[train], n_components)
        pred[fold] = predict_pls(model, x[fold])
    return pred


def choose_components(x: np.ndarray, y: np.ndarray, max_components: int) -> pd.DataFrame:
    rows = []
    max_comps = min(max_components, x.shape[1], x.shape[0] - 2)
    for comp in range(1, max_comps + 1):
        model = fit_pls(x, y, comp)
        train_pred = predict_pls(model, x)
        cv_pred = cv_predictions(x, y, comp)
        train = metrics(y, train_pred, comp)
        cv = metrics(y, cv_pred, comp)
        rows.append(
            {
                "n_components": comp,
                "train_r2": train["r2"],
                "train_adjusted_r2": train["adjusted_r2"],
                "train_rmse": train["rmse"],
                "cv_r2": cv["r2"],
                "cv_rmse": cv["rmse"],
            }
        )
    return pd.DataFrame(rows)


def pls_outputs(df: pd.DataFrame, predictors: list[str], label: str, root: Path) -> tuple[PlsModel, pd.DataFrame]:
    x = df[predictors].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(df[TARGET], errors="coerce").to_numpy(dtype=float)
    keep = np.isfinite(y) & np.isfinite(x).all(axis=1)
    x = x[keep]
    y = y[keep]
    cv = choose_components(x, y, MAX_COMPONENTS)
    best_components = int(cv.sort_values(["cv_rmse", "n_components"]).iloc[0]["n_components"])
    model = fit_pls(x, y, best_components)
    pred = predict_pls(model, x)
    train = metrics(y, pred, best_components)
    cv_pred = cv_predictions(x, y, best_components)
    cv_best = metrics(y, cv_pred, best_components)
    root.mkdir(parents=True, exist_ok=True)
    cv.to_csv(root / f"{label}_component_cv.csv", index=False)

    coef = model.coef_scaled * model.y_std / model.x_std
    corr = [float(np.corrcoef(x[:, i], y)[0, 1]) for i in range(x.shape[1])]
    rows = []
    for idx, var in enumerate(predictors):
        rows.append(
            {
                "variable": var,
                "block": variable_block(var),
                "family": variable_family(var),
                "turnout_corr": corr[idx],
                "abs_turnout_corr": abs(corr[idx]),
                "vip": model.vip[idx],
                "pls_coefficient": coef[idx],
                "direction": "higher turnout" if coef[idx] > 0 else "lower turnout",
            }
        )
    importance = pd.DataFrame(rows).sort_values(["vip", "abs_turnout_corr"], ascending=False)
    importance.to_csv(root / f"{label}_variable_importance.csv", index=False)

    loadings = pd.DataFrame(
        model.loadings,
        index=predictors,
        columns=[f"component_{i + 1}" for i in range(model.loadings.shape[1])],
    ).reset_index(names="variable")
    loadings.to_csv(root / f"{label}_component_loadings.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "model": label,
                "n": len(y),
                "num_predictors": len(predictors),
                "selected_components": best_components,
                "train_r2": train["r2"],
                "train_adjusted_r2": train["adjusted_r2"],
                "train_rmse": train["rmse"],
                "cv_r2": cv_best["r2"],
                "cv_rmse": cv_best["rmse"],
            }
        ]
    )
    summary.to_csv(root / f"{label}_summary.csv", index=False)
    return model, importance


def variable_block(var: str) -> str:
    for block, variables in BLOCKS.items():
        if var in variables:
            return block
    if var.startswith("block"):
        return var.split("_", 1)[0]
    return "other"


def variable_family(var: str) -> str:
    for family, variables in FAMILIES.items():
        if var in variables:
            return family
    return "other"


def diagnostics(df: pd.DataFrame, predictors: list[str], full_importance: pd.DataFrame) -> pd.DataFrame:
    xdf = df[predictors].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="coerce")
    corr = xdf.corr()
    corr.to_csv(DIAG_ROOT / "predictor_correlation_matrix.csv")
    rows = []
    for i, a in enumerate(predictors):
        for b in predictors[i + 1 :]:
            r = corr.loc[a, b]
            if pd.isna(r):
                continue
            abs_r = abs(float(r))
            if abs_r >= 0.70:
                rows.append(
                    {
                        "variable_a": a,
                        "variable_b": b,
                        "correlation": float(r),
                        "abs_correlation": abs_r,
                        "family_a": variable_family(a),
                        "family_b": variable_family(b),
                        "flag": "near_duplicate_or_inverse"
                        if abs_r >= 0.95
                        else "strong"
                        if abs_r >= 0.85
                        else "moderate_high",
                    }
                )
    high_pairs = pd.DataFrame(rows).sort_values(["abs_correlation"], ascending=False)
    high_pairs.to_csv(DIAG_ROOT / "high_correlation_pairs.csv", index=False)

    z = (xdf - xdf.mean()) / xdf.std(ddof=0)
    z = z.fillna(z.median())
    vifs = []
    zmat = z.to_numpy(dtype=float)
    for idx, var in enumerate(predictors):
        yj = zmat[:, idx]
        xj = np.delete(zmat, idx, axis=1)
        xj = np.column_stack([np.ones(len(xj)), xj])
        beta = np.linalg.pinv(xj.T @ xj) @ xj.T @ yj
        pred = xj @ beta
        r2 = metrics(yj, pred, xj.shape[1] - 1)["r2"]
        vif = math.inf if r2 >= 0.999999 else 1 / max(1 - r2, 1e-12)
        vifs.append({"variable": var, "vif": vif, "vif_r2": r2, "family": variable_family(var)})
    vif_df = pd.DataFrame(vifs).sort_values(["vif"], ascending=False)
    vif_df.to_csv(DIAG_ROOT / "vif_full_predictor_set.csv", index=False)

    var_diag = []
    for var in predictors:
        series = xdf[var]
        var_diag.append(
            {
                "variable": var,
                "block": variable_block(var),
                "family": variable_family(var),
                "turnout_corr": float(series.corr(y)),
                "max_abs_predictor_corr": float(corr[var].drop(index=var).abs().max()),
                "mean_abs_predictor_corr": float(corr[var].drop(index=var).abs().mean()),
                "high_corr_partner_count_abs_0_70": int((corr[var].drop(index=var).abs() >= 0.70).sum()),
                "vif": float(vif_df.loc[vif_df["variable"] == var, "vif"].iloc[0]),
            }
        )
    var_diag_df = pd.DataFrame(var_diag).merge(
        full_importance[["variable", "vip", "pls_coefficient"]], on="variable", how="left"
    )
    var_diag_df.to_csv(DIAG_ROOT / "variable_diagnostic_summary.csv", index=False)

    family_rows = []
    for family, variables in FAMILIES.items():
        present = [v for v in variables if v in predictors]
        if not present:
            continue
        sub = corr.loc[present, present]
        max_abs = 0.0
        if len(present) > 1:
            mask = ~np.eye(len(present), dtype=bool)
            max_abs = float(sub.where(mask).abs().max().max())
        family_rows.append(
            {
                "family": family,
                "num_variables": len(present),
                "max_abs_within_family_corr": max_abs,
                "variables": "; ".join(present),
            }
        )
    pd.DataFrame(family_rows).to_csv(DIAG_ROOT / "correlated_variable_families.csv", index=False)
    return var_diag_df


def vif_dataframe(df: pd.DataFrame, predictors: list[str]) -> pd.DataFrame:
    xdf = df[predictors].apply(pd.to_numeric, errors="coerce")
    z = (xdf - xdf.mean()) / xdf.std(ddof=0)
    z = z.fillna(z.median())
    zmat = z.to_numpy(dtype=float)
    rows = []
    for idx, var in enumerate(predictors):
        yj = zmat[:, idx]
        xj = np.delete(zmat, idx, axis=1)
        xj = np.column_stack([np.ones(len(xj)), xj])
        beta = np.linalg.pinv(xj.T @ xj) @ xj.T @ yj
        pred = xj @ beta
        r2 = metrics(yj, pred, xj.shape[1] - 1)["r2"]
        vif = math.inf if r2 >= 0.999999 else 1 / max(1 - r2, 1e-12)
        rows.append({"variable": var, "family": variable_family(var), "vif": vif, "vif_r2": r2})
    return pd.DataFrame(rows).sort_values("vif", ascending=False)


def selection_score(row: pd.Series) -> float:
    vif_penalty = min(float(row["vif"]), 100.0) / 100.0
    redundancy_penalty = 0.25 * float(row["mean_abs_predictor_corr"])
    return 0.55 * float(row["vip"]) + 0.45 * float(row["abs_turnout_corr"]) - vif_penalty - redundancy_penalty


def select_clean_variables(var_diag: pd.DataFrame, full_importance: pd.DataFrame) -> pd.DataFrame:
    scoring = var_diag.merge(
        full_importance[["variable", "abs_turnout_corr", "direction"]], on="variable", how="left"
    )
    scoring["selection_score"] = scoring.apply(selection_score, axis=1)
    selected: set[str] = set()
    decisions = []

    for family, variables in FAMILIES.items():
        present = [v for v in variables if v in set(scoring["variable"])]
        if not present:
            continue
        fam = scoring[scoring["variable"].isin(present)].sort_values("selection_score", ascending=False)
        anchors = [v for v in THEORY_ANCHORS.get(family, []) if v in present]
        target_count = min(len(anchors), 3)
        if target_count == 0:
            target_count = min(2, len(present))
        chosen = []
        for anchor in anchors:
            if anchor in present:
                chosen.append(anchor)
        for var in fam["variable"]:
            if len(chosen) >= target_count:
                break
            if var not in chosen:
                chosen.append(var)

        fam_vars = set(fam["variable"])
        for var in chosen:
            selected.add(var)
        for _, row in fam.iterrows():
            var = row["variable"]
            was_selected = var in selected
            reason = ""
            if was_selected and var in anchors:
                reason = "Kept as a theory/common-sense representative and checked against diagnostics."
            elif was_selected:
                reason = "Kept because it scored well on supervised PLS VIP/turnout association within its family."
            elif row["max_abs_predictor_corr"] >= 0.95:
                reason = "Excluded because it is near-duplicate/inverse/compositional with selected family information."
            elif row["high_corr_partner_count_abs_0_70"] > 0:
                reason = "Excluded to keep the family from double-weighting a correlated concept."
            else:
                reason = "Excluded to keep the cleaned model interpretable and lower dimensional."
            decisions.append(
                {
                    "family": family,
                    "variable": var,
                    "selected": was_selected,
                    "selection_score": row["selection_score"],
                    "vip": row["vip"],
                    "turnout_corr": row["turnout_corr"],
                    "vif": row["vif"],
                    "max_abs_predictor_corr": row["max_abs_predictor_corr"],
                    "reason": reason,
                }
            )

    selected_df = pd.DataFrame(decisions)
    selected_df.to_csv(CLEAN_ROOT / "theory_cleaned_variable_decisions.csv", index=False)
    return selected_df


def tournament(df: pd.DataFrame, decisions: pd.DataFrame) -> pd.DataFrame:
    selected = decisions.loc[decisions["selected"], "variable"].tolist()
    rows = []
    for family in decisions["family"].unique():
        fam = decisions[decisions["family"] == family].sort_values("selection_score", ascending=False)
        candidates = fam["variable"].head(min(6, len(fam))).tolist()
        baseline_family_vars = [v for v in selected if variable_family(v) == family]
        for cand in candidates:
            trial = [v for v in selected if variable_family(v) != family]
            trial.append(cand)
            trial = [v for v in trial if v in df.columns]
            x = df[trial].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
            y = pd.to_numeric(df[TARGET], errors="coerce").to_numpy(dtype=float)
            keep = np.isfinite(y) & np.isfinite(x).all(axis=1)
            if len(trial) < 2 or keep.sum() < 20:
                continue
            cv = choose_components(x[keep], y[keep], min(6, len(trial)))
            best = cv.sort_values(["cv_rmse", "n_components"]).iloc[0]
            rows.append(
                {
                    "family": family,
                    "candidate_variable": cand,
                    "baseline_family_variables": "; ".join(baseline_family_vars),
                    "num_predictors": len(trial),
                    "best_components": int(best["n_components"]),
                    "cv_r2": float(best["cv_r2"]),
                    "cv_rmse": float(best["cv_rmse"]),
                    "note": "One-family substitution: all other selected families held fixed.",
                }
            )

    # Connected family combinations where pairwise correlation can make A+C differ from A+D.
    connected_groups = [
        ["housing_tenure", "housing_form_density"],
        ["age_structure", "immigration_citizenship"],
        ["mayoral_competitiveness", "federal_competitiveness", "provincial_competitiveness"],
        ["transportation_access", "service_access", "service_contact"],
    ]
    for group in connected_groups:
        option_lists = []
        for family in group:
            fam = decisions[decisions["family"] == family].sort_values("selection_score", ascending=False)
            option_lists.append(fam["variable"].head(min(3, len(fam))).tolist())
        if not all(option_lists):
            continue
        for combo in product(*option_lists):
            trial = [v for v in selected if variable_family(v) not in group]
            trial.extend(combo)
            trial = list(dict.fromkeys([v for v in trial if v in df.columns]))
            x = df[trial].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
            y = pd.to_numeric(df[TARGET], errors="coerce").to_numpy(dtype=float)
            keep = np.isfinite(y) & np.isfinite(x).all(axis=1)
            cv = choose_components(x[keep], y[keep], min(6, len(trial)))
            best = cv.sort_values(["cv_rmse", "n_components"]).iloc[0]
            rows.append(
                {
                    "family": "+".join(group),
                    "candidate_variable": "; ".join(combo),
                    "baseline_family_variables": "connected-family tournament",
                    "num_predictors": len(trial),
                    "best_components": int(best["n_components"]),
                    "cv_r2": float(best["cv_r2"]),
                    "cv_rmse": float(best["cv_rmse"]),
                    "note": "Connected-family combination test.",
                }
            )
    out = pd.DataFrame(rows).sort_values(["family", "cv_rmse", "candidate_variable"])
    out.to_csv(CLEAN_ROOT / "variable_family_tournament_results.csv", index=False)
    return out


def write_full_report(summary: pd.DataFrame, importance: pd.DataFrame, loadings: pd.DataFrame) -> None:
    top = importance.head(20).copy()
    rows = []
    for _, row in top.iterrows():
        rows.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "VIP": fmt(row["vip"]),
                "Turnout corr": fmt(row["turnout_corr"]),
                "PLS direction": row["direction"],
            }
        )
    s = summary.iloc[0]
    top_plain = plain_list(top["variable"].head(12).tolist())
    md = f"""# Step 1: Full Supervised PLS Model

This model intentionally uses the full predictor universe before filtering obvious inverse or redundant variables. Mean turnout (`{TARGET}`) supervises the latent components through PLS.

## Model Fit

- Observations: {int(s['n'])}
- Predictors: {int(s['num_predictors'])}
- Selected components by {CV_FOLDS}-fold CV: {int(s['selected_components'])}
- Training R2: {fmt(s['train_r2'])}
- Cross-validated R2: {fmt(s['cv_r2'])}
- Cross-validated RMSE: {fmt(s['cv_rmse'])}

## Main Read

The full model is useful as a stress test. It lets the supervised dimension reduction procedure see every available signal, but it also lets inverse and same-concept variables double-enter the component construction. VIP scores should therefore be read as supervised importance, not as final variable-selection decisions.

The selected components are latent variables, not original predictors. In this model, 12 components means PLS built 12 turnout-supervised dimensions from the 70 original predictors. The original variables are interpreted through VIP scores, coefficients, and component loadings.

## Highest VIP Variables

{md_table(rows, ['Variable', 'Family', 'VIP', 'Turnout corr', 'PLS direction'])}

## Reference Categories Suggested By The Full Model

The full model points toward these broad reference categories for story-building: immigration and racialized geography, education and class resources, household composition, local electoral fragmentation, citizenship and language context, age structure, and urban service/contact geography. The strongest plain-language variables behind these categories are {top_plain}.

## Short Interpretation

Variables with VIP above 1 are contributing more than average to the turnout-supervised PLS projection. The strongest variables should be carried into Step 2 and Step 3 as evidence, but not accepted mechanically. For example, if renter and owner variables both score highly, that is not two separate housing-tenure findings; it is the same tenure concept appearing twice with opposite coding.
"""
    (REPORT_ROOT / "task1_full_pls_summary.md").write_text(md, encoding="utf-8")


def write_diag_report(var_diag: pd.DataFrame, pairs: pd.DataFrame, families: pd.DataFrame, vif: pd.DataFrame) -> None:
    top_vif = []
    for _, row in vif.head(20).iterrows():
        top_vif.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "VIF": fmt(row["vif"]),
            }
        )
    top_pairs = []
    for _, row in pairs.head(25).iterrows():
        top_pairs.append(
            {
                "A": f"`{row['variable_a']}`",
                "B": f"`{row['variable_b']}`",
                "r": fmt(row["correlation"]),
                "Flag": row["flag"],
            }
        )
    family_rows = []
    for _, row in families.sort_values("max_abs_within_family_corr", ascending=False).iterrows():
        family_rows.append(
            {
                "Family": row["family"],
                "Vars": int(row["num_variables"]),
                "Max |r|": fmt(row["max_abs_within_family_corr"]),
            }
        )
    strongest_plain_pairs = []
    for _, row in pairs.head(10).iterrows():
        strongest_plain_pairs.append(
            f"{plain_variable(row['variable_a'])} and {plain_variable(row['variable_b'])} "
            f"with correlation {fmt(row['correlation'])}"
        )

    md = f"""# Step 2: Multicollinearity and Redundancy Diagnostics

This step diagnoses the full predictor universe used in Step 1. It does not decide the final variable set by itself. It flags where the same concept is probably being counted more than once.

## Headline Findings

- Predictor count checked: {len(var_diag)}
- High-correlation pairs with |r| >= 0.70: {len(pairs)}
- Near duplicate or inverse pairs with |r| >= 0.95: {int((pairs['abs_correlation'] >= 0.95).sum()) if not pairs.empty else 0}
- Variables with VIF >= 10: {int((vif['vif'] >= 10).sum())}
- Variables with VIF >= 5: {int((vif['vif'] >= 5).sum())}

## Highest VIF Variables

{md_table(top_vif, ['Variable', 'Family', 'VIF'])}

## Strongest Correlated Pairs

{md_table(top_pairs, ['A', 'B', 'r', 'Flag'])}

## Plain-Language Redundancy Summary

The most important high-correlation or inverse relationships are { '; '.join(strongest_plain_pairs) }. These are the relationships most likely to double-count the same social concept if they are fed into dimension reduction together.

## Family-Level Redundancy

{md_table(family_rows, ['Family', 'Vars', 'Max |r|'])}

## Interpretation

The diagnostics confirm Zack's warning: the modelling table contains variables that are not merely correlated but sometimes structurally tied. Tenure is the clearest example because renter and owner shares are inverse codings of the same concept. Housing form and density also form a dense cluster, especially because apartment counts, apartment shares, condo variables, density variables, and total dwelling counts partly track the same urban form.

VIF is stricter than pairwise correlation because it asks whether a variable can be reconstructed from all other predictors together. High VIF does not mean the variable is unimportant; it means the model cannot cleanly separate its unique contribution from nearby variables. That is why Step 3 should use family comparisons rather than deleting variables mechanically by VIF.

The practical conclusion is that the final cleaned model should choose representatives from correlated families, then test substitutions and connected-family combinations. That preserves the idea that A may work better with D than with C, which pairwise correlation alone cannot discover.
"""
    (REPORT_ROOT / "task2_multicollinearity_diagnostics.md").write_text(md, encoding="utf-8")


def write_clean_report(
    full_summary: pd.DataFrame,
    clean_summary: pd.DataFrame,
    decisions: pd.DataFrame,
    tournament_df: pd.DataFrame,
    clean_importance: pd.DataFrame,
    clean_vif: pd.DataFrame,
) -> None:
    selected = decisions[decisions["selected"]].copy()
    excluded = decisions[~decisions["selected"]].copy()
    selected_rows = []
    for _, row in selected.sort_values(["family", "selection_score"], ascending=[True, False]).iterrows():
        selected_rows.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "VIP": fmt(row["vip"]),
                "Turnout corr": fmt(row["turnout_corr"]),
                "VIF": fmt(row["vif"]),
                "Reason": row["reason"],
            }
        )
    top_tournament = []
    for _, row in tournament_df.groupby("family", as_index=False).first().head(20).iterrows():
        top_tournament.append(
            {
                "Family/test": row["family"],
                "Best candidate": f"`{row['candidate_variable']}`",
                "CV R2": fmt(row["cv_r2"]),
                "CV RMSE": fmt(row["cv_rmse"]),
            }
        )
    importance_rows = []
    for _, row in clean_importance.head(20).iterrows():
        importance_rows.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "VIP": fmt(row["vip"]),
                "Turnout corr": fmt(row["turnout_corr"]),
                "Direction": row["direction"],
            }
        )
    clean_vif_rows = []
    for _, row in clean_vif.head(15).iterrows():
        clean_vif_rows.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "Cleaned VIF": fmt(row["vif"]),
            }
        )

    f = full_summary.iloc[0]
    c = clean_summary.iloc[0]
    selected_plain = plain_list(selected["variable"].tolist())
    top_clean_plain = plain_list(clean_importance.head(12)["variable"].tolist())
    variable_notes = []
    for _, row in decisions.sort_values(["family", "selected"], ascending=[True, False]).iterrows():
        status = "Kept" if row["selected"] else "Not kept"
        variable_notes.append(
            f"- `{row['variable']}` ({row['family']}): {status}. VIP {fmt(row['vip'])}, "
            f"turnout correlation {fmt(row['turnout_corr'])}, VIF {fmt(row['vif'])}. {row['reason']}"
        )

    md = f"""# Step 3: Theory-Cleaned Supervised PLS and Variable Family Tournament

Step 3 uses the Step 1 VIP evidence and Step 2 redundancy diagnostics to build a more defensible supervised dimension-reduction model. The goal is not to pretend the predictors are independent. The goal is to keep a smaller set of representatives so no single social concept gets double-weighted in the PLS components.

## Full vs Cleaned Model

| Model | Predictors | Components | CV R2 | CV RMSE | Train R2 |
|---|---:|---:|---:|---:|---:|
| Full unfiltered PLS | {int(f['num_predictors'])} | {int(f['selected_components'])} | {fmt(f['cv_r2'])} | {fmt(f['cv_rmse'])} | {fmt(f['train_r2'])} |
| Theory-cleaned PLS | {int(c['num_predictors'])} | {int(c['selected_components'])} | {fmt(c['cv_r2'])} | {fmt(c['cv_rmse'])} | {fmt(c['train_r2'])} |

## Selection Logic

The cleaned model was built with a family approach. Within each family, variables were judged using four pieces of evidence: common-sense interpretability, bivariate turnout association, full-model PLS VIP, and redundancy/VIF. Where variables were close substitutes, the workflow also ran one-family substitution tests and connected-family combination tests.

This means a variable could be excluded even if it had a high VIP when another selected variable represented the same concept more cleanly. Conversely, a variable could stay with moderate VIP if it gives a clearer theoretical reading and does not create severe redundancy.

The 5 selected components are latent variables created from the 27 selected original predictors. They are not 5 named raw variables. The model is interpreted by looking back at which original predictors have high VIP scores and strong loadings within those latent components.

## Final Variables Kept

{md_table(selected_rows, ['Variable', 'Family', 'VIP', 'Turnout corr', 'VIF', 'Reason'])}

In plain language, the kept variables are {selected_plain}.

## Cleaned Model VIP Results

{md_table(importance_rows, ['Variable', 'Family', 'VIP', 'Turnout corr', 'Direction'])}

## Remaining VIF After Cleaning

{md_table(clean_vif_rows, ['Variable', 'Family', 'Cleaned VIF'])}

The cleaned model removes the exact duplicate/inverse variables from the full universe, so the impossible VIFs mostly disappear. Some VIF values remain above 10 because the social geography itself is bundled: household size, age, tenure, apartment form, citizenship, and school-age composition still move together across Toronto CTs. That remaining collinearity should be handled by reading the PLS components and VIP scores, not by treating each coefficient as a standalone causal estimate.

The age variables are a good example of remaining conceptual correlation. Age 18 to 34 share and age 65 plus share are partly compositional, but they are not exact inverses. I kept both because they represent different turnout stories: younger-adult concentration and older-adult concentration. Still, the VIF table shows that age structure remains bundled with household size, residential stability, and school-age composition, so these should be interpreted as a family rather than isolated causal coefficients.

## Reference Categories For The Cleaned Model

The cleaned model suggests five main reference categories for the final story: immigration and racialized geography, education and class resources, age and household composition, housing tenure and urban form, and electoral competitiveness. The most stable variables behind these categories are {top_clean_plain}. These categories are a way to bridge the model-first workflow back to the kind of reference categories Zack was emphasizing.

## Family Tournament Highlights

{md_table(top_tournament, ['Family/test', 'Best candidate', 'CV R2', 'CV RMSE'])}

## Variable-by-Variable Decisions

{chr(10).join(variable_notes)}

## Final Interpretation

The cleaned PLS model should be treated as the main supervised dimension-reduction candidate. It keeps turnout supervision through PLS, while reducing the most obvious double-counting problems that appear in the full model. If an inverse pair performs almost identically, the final choice should be explained as interpretive rather than purely predictive. For example, renter share and owner share can encode nearly the same tenure gradient with opposite signs; keeping renter share makes the urban turnout story easier to discuss without implying that owner share is empirically irrelevant.

The remaining ambiguous cases are valuable rather than embarrassing. They show where the data cannot clearly distinguish one representative from another, especially inside housing form, service access, and election-competitiveness families. Those should be reported as sensitivity areas, not hidden.
"""
    (REPORT_ROOT / "task3_theory_cleaned_pls_report.md").write_text(md, encoding="utf-8")


def standardized_frame(df: pd.DataFrame, predictors: list[str]) -> pd.DataFrame:
    x = df[predictors].apply(pd.to_numeric, errors="coerce")
    return (x - x.mean()) / x.std(ddof=0)


def eligible_interaction_variables(decisions: pd.DataFrame) -> list[str]:
    selected = decisions.loc[decisions["selected"], "variable"].tolist()
    alternatives = decisions[
        (~decisions["selected"])
        & (~decisions["reason"].str.contains("near-duplicate|inverse|compositional", case=False, na=False))
        & (decisions["max_abs_predictor_corr"] < 0.95)
    ].copy()
    alternatives = alternatives.sort_values(["family", "selection_score"], ascending=[True, False])
    extra = []
    for family, group in alternatives.groupby("family"):
        extra.extend(group.head(2)["variable"].tolist())
    return list(dict.fromkeys(selected + extra))


def interaction_candidates(eligible: list[str]) -> list[tuple[str, str, str]]:
    allowed_family_pairs = {
        ("age_structure", "household_class"),
        ("age_structure", "housing_tenure"),
        ("age_structure", "residential_stability"),
        ("age_structure", "immigration_citizenship"),
        ("age_structure", "mayoral_competitiveness"),
        ("household_class", "housing_tenure"),
        ("household_class", "housing_form_density"),
        ("household_class", "immigration_citizenship"),
        ("household_class", "service_access"),
        ("household_class", "service_contact"),
        ("housing_tenure", "housing_form_density"),
        ("housing_tenure", "residential_stability"),
        ("housing_tenure", "transportation_access"),
        ("housing_form_density", "transportation_access"),
        ("immigration_citizenship", "mayoral_competitiveness"),
        ("immigration_citizenship", "service_access"),
        ("immigration_citizenship", "service_contact"),
        ("mayoral_competitiveness", "household_class"),
        ("mayoral_competitiveness", "federal_competitiveness"),
        ("mayoral_competitiveness", "provincial_competitiveness"),
        ("transportation_access", "service_access"),
        ("transportation_access", "service_contact"),
        ("service_access", "service_contact"),
    }
    pairs = []
    for idx, a in enumerate(eligible):
        for b in eligible[idx + 1 :]:
            fa, fb = variable_family(a), variable_family(b)
            key = tuple(sorted([fa, fb]))
            allowed_keys = {tuple(sorted(k)) for k in allowed_family_pairs}
            if key not in allowed_keys:
                continue
            name = f"{a}__x__{b}"
            pairs.append((a, b, name))
    return pairs


def add_interactions(df: pd.DataFrame, pairs: list[tuple[str, str, str]]) -> pd.DataFrame:
    if not pairs:
        return df.copy()
    z = standardized_frame(df, sorted(set([v for pair in pairs for v in pair[:2]])))
    interaction_cols = {}
    for a, b, name in pairs:
        interaction_cols[name] = z[a] * z[b]
    return pd.concat([df.copy(), pd.DataFrame(interaction_cols, index=df.index)], axis=1)


def run_interaction_discovery(
    df: pd.DataFrame,
    decisions: pd.DataFrame,
    clean_summary: pd.DataFrame,
    clean_importance: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = decisions.loc[decisions["selected"], "variable"].tolist()
    eligible = eligible_interaction_variables(decisions)
    pairs = interaction_candidates(eligible)
    interaction_df = add_interactions(df, pairs)
    rows = []
    y = pd.to_numeric(df[TARGET], errors="coerce").to_numpy(dtype=float)

    for a, b, name in pairs:
        predictors = selected + [v for v in [a, b] if v not in selected] + [name]
        predictors = list(dict.fromkeys(predictors))
        x = interaction_df[predictors].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
        keep = np.isfinite(y) & np.isfinite(x).all(axis=1)
        cv = choose_components(x[keep], y[keep], min(8, len(predictors)))
        best = cv.sort_values(["cv_rmse", "n_components"]).iloc[0]
        model = fit_pls(x[keep], y[keep], int(best["n_components"]))
        vip = model.vip[predictors.index(name)]
        rows.append(
            {
                "interaction": name,
                "variable_a": a,
                "variable_b": b,
                "family_a": variable_family(a),
                "family_b": variable_family(b),
                "main_effect_added_a": a not in selected,
                "main_effect_added_b": b not in selected,
                "num_predictors": len(predictors),
                "best_components": int(best["n_components"]),
                "cv_r2": float(best["cv_r2"]),
                "cv_rmse": float(best["cv_rmse"]),
                "interaction_vip": float(vip),
                "story": interaction_story(a, b),
            }
        )

    screen = pd.DataFrame(rows).sort_values(["cv_rmse", "interaction_vip"], ascending=[True, False])
    screen.to_csv(INTERACTION_ROOT / "interaction_screen_results.csv", index=False)

    base_rmse = float(clean_summary.iloc[0]["cv_rmse"])
    strong = screen[(screen["cv_rmse"] <= base_rmse) & (screen["interaction_vip"] >= 0.8)].head(8)
    chosen_interactions = strong["interaction"].tolist()
    chosen_pairs = [(row["variable_a"], row["variable_b"], row["interaction"]) for _, row in strong.iterrows()]
    final_df = add_interactions(df, chosen_pairs)
    final_predictors = list(dict.fromkeys(selected + [v for pair in chosen_pairs for v in pair[:2]] + chosen_interactions))
    final_model, final_importance = pls_outputs(final_df, final_predictors, "interaction_augmented_pls", INTERACTION_ROOT)
    final_vif = vif_dataframe(final_df, final_predictors)
    final_vif.to_csv(INTERACTION_ROOT / "interaction_augmented_pls_vif.csv", index=False)
    pd.DataFrame({"variable": final_predictors}).to_csv(INTERACTION_ROOT / "interaction_augmented_predictors.csv", index=False)
    write_interaction_report(clean_summary, clean_importance, screen, pd.read_csv(INTERACTION_ROOT / "interaction_augmented_pls_summary.csv"), final_importance, final_vif)
    return screen, final_importance


def interaction_story(a: str, b: str) -> str:
    labels = {variable_family(a), variable_family(b)}
    if {"age_structure", "housing_tenure"} <= labels:
        return "Tests whether the youth/older-age turnout gradient changes in renter-heavy places."
    if {"housing_tenure", "housing_form_density"} <= labels:
        return "Tests whether tenure has a different turnout meaning in apartment/dense urban form."
    if {"immigration_citizenship", "mayoral_competitiveness"} <= labels:
        return "Tests whether fragmented local electoral geography compounds immigrant/racialized turnout gradients."
    if {"household_class", "immigration_citizenship"} <= labels:
        return "Tests whether class/education resources condition immigration or racialized-geography effects."
    if {"household_class", "service_contact"} <= labels:
        return "Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas."
    if {"age_structure", "household_class"} <= labels:
        return "Tests whether the class/household-size turnout pattern changes across age structure."
    if {"immigration_citizenship", "service_contact"} <= labels:
        return "Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography."
    if {"transportation_access", "service_access"} <= labels:
        return "Tests whether mobility and nearby civic/service infrastructure work together."
    if {"service_access", "service_contact"} <= labels:
        return "Tests whether service presence matters differently where service-contact need is higher."
    return "Theory-screened cross-family interaction with interpretable main effects retained."


def retained_interaction_interpretation(term: str) -> str:
    if "__x__" not in term:
        return ""
    left, right = term.split("__x__", 1)
    families = {variable_family(left), variable_family(right)}
    plain = plain_term(term)
    if {"household_class", "mayoral_competitiveness"} <= families:
        return (
            f"{plain}: this asks whether education or class resources change how local electoral "
            "fragmentation relates to turnout. It is useful for a story about whether complex local contests "
            "are easier to navigate in higher-resource places."
        )
    if {"service_contact", "immigration_citizenship"} <= families:
        return (
            f"{plain}: this asks whether service-contact geography has a different meaning in immigrant, "
            "language, or citizenship contexts. It may point to places where municipal service contact and "
            "civic participation are linked unevenly."
        )
    if {"household_class", "age_structure"} <= families:
        return (
            f"{plain}: this asks whether class or household structure has a different turnout relationship "
            "depending on the age profile of the tract. It helps separate youth, working-age, and older-adult "
            "versions of the turnout story."
        )
    if {"household_class", "service_contact"} <= families:
        return (
            f"{plain}: this asks whether service-contact intensity is associated with turnout differently "
            "in higher-need or higher-resource places. It is especially relevant for interpreting 311 requests, "
            "development applications, and collision exposure as civic-contact context rather than simple services."
        )
    return f"{plain}: this is a retained interaction and should be interpreted as a conditional relationship, not as two separate main effects."


def write_interaction_report(
    clean_summary: pd.DataFrame,
    clean_importance: pd.DataFrame,
    screen: pd.DataFrame,
    interaction_summary: pd.DataFrame,
    interaction_importance: pd.DataFrame,
    interaction_vif: pd.DataFrame,
) -> None:
    base = clean_summary.iloc[0]
    inter = interaction_summary.iloc[0]
    top_screen = []
    for _, row in screen.head(25).iterrows():
        top_screen.append(
            {
                "Interaction": f"`{row['interaction']}`",
                "Families": f"{row['family_a']} + {row['family_b']}",
                "CV R2": fmt(row["cv_r2"]),
                "CV RMSE": fmt(row["cv_rmse"]),
                "VIP": fmt(row["interaction_vip"]),
                "Story": row["story"],
            }
        )
    chosen = interaction_importance[interaction_importance["variable"].str.contains("__x__", regex=False)].head(15)
    chosen_rows = []
    retained_notes = []
    for _, row in chosen.iterrows():
        chosen_rows.append(
            {
                "Interaction": f"`{row['variable']}`",
                "VIP": fmt(row["vip"]),
                "Turnout corr": fmt(row["turnout_corr"]),
                "Direction": row["direction"],
            }
        )
        retained_notes.append(f"- {retained_interaction_interpretation(row['variable'])}")
    vif_rows = []
    for _, row in interaction_vif.head(15).iterrows():
        vif_rows.append({"Variable": f"`{row['variable']}`", "Family": row["family"], "VIF": fmt(row["vif"])})

    md = f"""# Step 4: Interaction Discovery After Cleaning

Step 4 tests interpretable interaction terms after the Step 3 family-cleaned model. The candidate pool is broader than the exact Step 3 model: it includes selected variables plus reasonable non-duplicate family alternatives. Variables removed as exact duplicates, inverse codings, or near-compositional redundancies are not reintroduced.

## Baseline vs Interaction-Augmented PLS

| Model | Predictors | Components | CV R2 | CV RMSE | Train R2 |
|---|---:|---:|---:|---:|---:|
| Step 3 cleaned PLS | {int(base['num_predictors'])} | {int(base['selected_components'])} | {fmt(base['cv_r2'])} | {fmt(base['cv_rmse'])} | {fmt(base['train_r2'])} |
| Step 4 interaction PLS | {int(inter['num_predictors'])} | {int(inter['selected_components'])} | {fmt(inter['cv_r2'])} | {fmt(inter['cv_rmse'])} | {fmt(inter['train_r2'])} |

## Screening Rule

Each candidate interaction was tested by adding the interaction plus its main effects if those main effects were not already in the cleaned model. The screen used cross-validated PLS performance and the interaction term's VIP. I treated an interaction as promising only when it did not worsen CV RMSE and had interaction VIP around 0.8 or higher.

## Best Interaction Trials

{md_table(top_screen, ['Interaction', 'Families', 'CV R2', 'CV RMSE', 'VIP', 'Story'])}

## Interactions Retained In The Augmented PLS

{md_table(chosen_rows, ['Interaction', 'VIP', 'Turnout corr', 'Direction'])}

## Interpretation Of Retained Interactions

{chr(10).join(retained_notes)}

## Reference Categories For Interactions

The interaction results mainly point to four conditional reference categories: class and service contact, education and local electoral fragmentation, language or immigrant geography and service contact, and age structure interacting with class or household size. These should not all become final hypotheses automatically. They are candidate story lines that can be checked against maps, plots, and substantive plausibility.

## Remaining VIF In Interaction Model

{md_table(vif_rows, ['Variable', 'Family', 'VIF'])}

## Interpretation

Interactions should be used as story devices only when they describe a plausible conditional relationship. The strongest candidates here are not arbitrary products; they mainly ask whether the turnout penalty associated with social composition becomes sharper in places with particular housing form, electoral fragmentation, or service/contact contexts. If an interaction improves prediction only trivially, it should still be kept out of the final narrative unless it clarifies a substantive mechanism.
"""
    (REPORT_ROOT / "task4_interaction_discovery_report.md").write_text(md, encoding="utf-8")


def fit_sparse_pls(x: np.ndarray, y: np.ndarray, n_components: int, keep_per_component: int) -> PlsModel:
    xs, ys, x_mean, x_std, y_mean, y_std = standardize_train(x, y)
    x_def = xs.copy()
    y_def = ys.copy()
    n, p = xs.shape
    comps = min(n_components, p, n - 1)
    weights = np.zeros((p, comps))
    loadings = np.zeros((p, comps))
    q = np.zeros(comps)
    scores = np.zeros((n, comps))
    ssy = np.zeros(comps)
    for comp in range(comps):
        w = x_def.T @ y_def
        if keep_per_component < p:
            keep_idx = np.argsort(np.abs(w))[-keep_per_component:]
            mask = np.zeros(p, dtype=bool)
            mask[keep_idx] = True
            w = np.where(mask, w, 0)
        norm = np.linalg.norm(w)
        if norm < 1e-12:
            break
        w = w / norm
        t = x_def @ w
        tt = float(t.T @ t)
        if tt < 1e-12:
            break
        p_load = (x_def.T @ t) / tt
        q_load = float((y_def.T @ t) / tt)
        x_def = x_def - np.outer(t, p_load)
        y_def = y_def - q_load * t
        weights[:, comp] = w
        loadings[:, comp] = p_load
        q[comp] = q_load
        scores[:, comp] = t
        ssy[comp] = (q_load**2) * tt
    w_star = weights @ np.linalg.pinv(loadings.T @ weights)
    coef_scaled = w_star @ q
    total_ssy = float(ssy.sum()) or 1.0
    vip = np.sqrt(p * ((weights**2) @ ssy) / total_ssy)
    return PlsModel(x_mean, x_std, y_mean, y_std, weights, loadings, q, scores, coef_scaled, vip)


def cv_sparse_pls(x: np.ndarray, y: np.ndarray, n_components: int, keep_per_component: int) -> np.ndarray:
    rng = np.random.default_rng(RANDOM_SEED)
    indices = np.arange(len(y))
    rng.shuffle(indices)
    pred = np.zeros_like(y, dtype=float)
    for fold in np.array_split(indices, CV_FOLDS):
        train = np.setdiff1d(indices, fold, assume_unique=False)
        model = fit_sparse_pls(x[train], y[train], n_components, keep_per_component)
        pred[fold] = predict_pls(model, x[fold])
    return pred


def run_sparse_pls(df: pd.DataFrame, predictors: list[str], full_summary: pd.DataFrame, clean_summary: pd.DataFrame) -> pd.DataFrame:
    x = df[predictors].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(df[TARGET], errors="coerce").to_numpy(dtype=float)
    keep = np.isfinite(y) & np.isfinite(x).all(axis=1)
    x, y = x[keep], y[keep]
    rows = []
    keep_grid = sorted(set([5, 8, 10, 12, 15, min(20, len(predictors)), len(predictors)]))
    for comps in range(1, min(8, len(predictors)) + 1):
        for keep_count in keep_grid:
            model = fit_sparse_pls(x, y, comps, keep_count)
            pred = predict_pls(model, x)
            cv_pred = cv_sparse_pls(x, y, comps, keep_count)
            train = metrics(y, pred, comps)
            cv = metrics(y, cv_pred, comps)
            rows.append(
                {
                    "n_components": comps,
                    "keep_per_component": keep_count,
                    "train_r2": train["r2"],
                    "train_rmse": train["rmse"],
                    "cv_r2": cv["r2"],
                    "cv_rmse": cv["rmse"],
                }
            )
    grid = pd.DataFrame(rows).sort_values(["cv_rmse", "keep_per_component"])
    grid.to_csv(SPARSE_ROOT / "sparse_pls_grid_search.csv", index=False)
    best = grid.iloc[0]
    model = fit_sparse_pls(x, y, int(best["n_components"]), int(best["keep_per_component"]))
    coef = model.coef_scaled * model.y_std / model.x_std
    importance = pd.DataFrame(
        [
            {
                "variable": var,
                "family": variable_family(var),
                "vip": model.vip[idx],
                "sparse_pls_coefficient": coef[idx],
                "selected_in_sparse_weights": bool(np.any(np.abs(model.weights[idx, :]) > 1e-10)),
                "nonzero_component_count": int(np.sum(np.abs(model.weights[idx, :]) > 1e-10)),
            }
            for idx, var in enumerate(predictors)
        ]
    ).sort_values(["selected_in_sparse_weights", "vip"], ascending=[False, False])
    importance.to_csv(SPARSE_ROOT / "sparse_pls_variable_importance.csv", index=False)
    summary = pd.DataFrame(
        [
            {
                "model": "sparse_pls_cleaned_predictors",
                "n": len(y),
                "num_predictors": len(predictors),
                "selected_components": int(best["n_components"]),
                "keep_per_component": int(best["keep_per_component"]),
                "train_r2": float(best["train_r2"]),
                "train_rmse": float(best["train_rmse"]),
                "cv_r2": float(best["cv_r2"]),
                "cv_rmse": float(best["cv_rmse"]),
            }
        ]
    )
    summary.to_csv(SPARSE_ROOT / "sparse_pls_summary.csv", index=False)
    write_sparse_report(full_summary, clean_summary, summary, importance)
    return importance


def pca_scores(x_train: np.ndarray, x_test: np.ndarray, n_components: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std == 0] = 1
    xs = (x_train - mean) / std
    xt = (x_test - mean) / std
    _, _, vt = np.linalg.svd(xs, full_matrices=False)
    components = vt[:n_components].T
    return xs @ components, xt @ components, components


def ols_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    x_train = np.column_stack([np.ones(len(train_x)), train_x])
    x_test = np.column_stack([np.ones(len(test_x)), test_x])
    beta = np.linalg.pinv(x_train.T @ x_train) @ x_train.T @ train_y
    return x_test @ beta


def run_supervised_pca(df: pd.DataFrame, predictors: list[str], full_summary: pd.DataFrame, clean_summary: pd.DataFrame) -> pd.DataFrame:
    xdf = df[predictors].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="coerce")
    keep = y.notna() & xdf.notna().all(axis=1)
    xdf, y = xdf.loc[keep], y.loc[keep]
    corrs = xdf.corrwith(y).abs().sort_values(ascending=False)
    rows = []
    thresholds = [0.10, 0.15, 0.20, 0.25, 0.30]
    top_ns = [8, 12, 16, 20, min(27, len(predictors))]
    configs = []
    for threshold in thresholds:
        selected = corrs[corrs >= threshold].index.tolist()
        if len(selected) >= 3:
            configs.append((f"corr_ge_{threshold}", selected))
    for n in top_ns:
        configs.append((f"top_{n}_corr", corrs.head(n).index.tolist()))
    y_arr = y.to_numpy(dtype=float)
    rng = np.random.default_rng(RANDOM_SEED)
    indices = np.arange(len(y_arr))
    rng.shuffle(indices)
    folds = np.array_split(indices, CV_FOLDS)
    for label, selected in configs:
        x = xdf[selected].to_numpy(dtype=float)
        for comps in range(1, min(8, len(selected)) + 1):
            pred = np.zeros_like(y_arr)
            for fold in folds:
                train = np.setdiff1d(indices, fold, assume_unique=False)
                train_scores, test_scores, _ = pca_scores(x[train], x[fold], comps)
                pred[fold] = ols_predict(train_scores, y_arr[train], test_scores)
            cv = metrics(y_arr, pred, comps)
            train_scores, _, components = pca_scores(x, x, comps)
            train_pred = ols_predict(train_scores, y_arr, train_scores)
            train = metrics(y_arr, train_pred, comps)
            rows.append(
                {
                    "screen": label,
                    "screened_predictor_count": len(selected),
                    "n_components": comps,
                    "cv_r2": cv["r2"],
                    "cv_rmse": cv["rmse"],
                    "train_r2": train["r2"],
                    "train_rmse": train["rmse"],
                    "variables": "; ".join(selected),
                }
            )
    result = pd.DataFrame(rows).sort_values(["cv_rmse", "screened_predictor_count"])
    result.to_csv(SUPERVISED_PCA_ROOT / "supervised_pca_grid_search.csv", index=False)
    best = result.iloc[0]
    best_vars = best["variables"].split("; ")
    x = xdf[best_vars].to_numpy(dtype=float)
    scores, _, components = pca_scores(x, x, int(best["n_components"]))
    loadings = pd.DataFrame(
        components,
        index=best_vars,
        columns=[f"component_{i + 1}" for i in range(int(best["n_components"]))],
    ).reset_index(names="variable")
    loadings["max_abs_loading"] = loadings.drop(columns=["variable"]).abs().max(axis=1)
    loadings.sort_values("max_abs_loading", ascending=False).to_csv(
        SUPERVISED_PCA_ROOT / "supervised_pca_loadings.csv", index=False
    )
    summary = pd.DataFrame([dict(best)])
    summary.insert(0, "model", "supervised_pca")
    summary.to_csv(SUPERVISED_PCA_ROOT / "supervised_pca_summary.csv", index=False)
    write_supervised_pca_report(full_summary, clean_summary, summary, loadings.sort_values("max_abs_loading", ascending=False))
    return result


def soft_threshold(value: float, penalty: float) -> float:
    if value > penalty:
        return value - penalty
    if value < -penalty:
        return value + penalty
    return 0.0


def elastic_net_fit(x: np.ndarray, y: np.ndarray, alpha: float, l1_ratio: float, max_iter: int = 5000) -> np.ndarray:
    n, p = x.shape
    beta = np.zeros(p)
    l1 = alpha * l1_ratio
    l2 = alpha * (1 - l1_ratio)
    for _ in range(max_iter):
        old = beta.copy()
        for j in range(p):
            residual = y - x @ beta + x[:, j] * beta[j]
            rho = float((x[:, j] @ residual) / n)
            denom = float((x[:, j] @ x[:, j]) / n) + l2
            beta[j] = soft_threshold(rho, l1) / max(denom, 1e-12)
        if np.max(np.abs(beta - old)) < 1e-7:
            break
    return beta


def run_elastic_net(
    df: pd.DataFrame,
    predictors: list[str],
    full_importance: pd.DataFrame,
    clean_importance: pd.DataFrame,
) -> pd.DataFrame:
    xdf = df[predictors].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[TARGET], errors="coerce")
    keep = y.notna() & xdf.notna().all(axis=1)
    x = xdf.loc[keep].to_numpy(dtype=float)
    y_arr = y.loc[keep].to_numpy(dtype=float)
    x_mean, x_std = x.mean(axis=0), x.std(axis=0)
    x_std[x_std == 0] = 1
    y_mean, y_std = y_arr.mean(), y_arr.std() or 1
    xs = (x - x_mean) / x_std
    ys = (y_arr - y_mean) / y_std
    alphas = [0.001, 0.003, 0.01, 0.03, 0.1, 0.2]
    ratios = [0.2, 0.5, 0.8]
    rng = np.random.default_rng(RANDOM_SEED)
    indices = np.arange(len(ys))
    rng.shuffle(indices)
    folds = np.array_split(indices, CV_FOLDS)
    rows = []
    for alpha in alphas:
        for ratio in ratios:
            pred = np.zeros_like(ys)
            selected_counts = []
            for fold in folds:
                train = np.setdiff1d(indices, fold, assume_unique=False)
                beta = elastic_net_fit(xs[train], ys[train], alpha, ratio)
                pred[fold] = xs[fold] @ beta
                selected_counts.append(int(np.sum(np.abs(beta) > 1e-6)))
            cv = metrics(ys, pred, int(np.mean(selected_counts)))
            rows.append(
                {
                    "alpha": alpha,
                    "l1_ratio": ratio,
                    "mean_selected_variables": float(np.mean(selected_counts)),
                    "cv_r2": cv["r2"],
                    "cv_rmse_scaled_y": cv["rmse"],
                }
            )
    grid = pd.DataFrame(rows).sort_values(["cv_rmse_scaled_y", "mean_selected_variables"])
    grid.to_csv(ELASTIC_NET_ROOT / "elastic_net_grid_search.csv", index=False)
    best = grid.iloc[0]
    beta = elastic_net_fit(xs, ys, float(best["alpha"]), float(best["l1_ratio"]))
    coef = beta * y_std / x_std
    selected = np.abs(beta) > 1e-6
    importance = pd.DataFrame(
        [
            {
                "variable": var,
                "family": variable_family(var),
                "elastic_net_coefficient": coef[idx],
                "abs_scaled_coefficient": abs(beta[idx]),
                "selected": bool(selected[idx]),
            }
            for idx, var in enumerate(predictors)
        ]
    ).sort_values(["selected", "abs_scaled_coefficient"], ascending=[False, False])
    importance.to_csv(ELASTIC_NET_ROOT / "elastic_net_variable_selection.csv", index=False)
    write_elastic_net_report(grid, importance, full_importance, clean_importance)
    return importance


def write_sparse_report(
    full_summary: pd.DataFrame,
    clean_summary: pd.DataFrame,
    sparse_summary: pd.DataFrame,
    importance: pd.DataFrame,
) -> None:
    f, c, s = full_summary.iloc[0], clean_summary.iloc[0], sparse_summary.iloc[0]
    sparse_plain = plain_list(importance.head(12)["variable"].tolist())
    top = []
    for _, row in importance.head(20).iterrows():
        top.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "VIP": fmt(row["vip"]),
                "In Sparse Weights": row["selected_in_sparse_weights"],
                "Components": int(row["nonzero_component_count"]),
            }
        )
    md = f"""# Step 5A: Sparse PLS Comparison

Sparse PLS keeps the PLS idea but forces each component to use only a limited number of variables. This implementation is a transparent sparse-PLS approximation: within each component, it keeps only the largest predictor weights before deflation. This is useful here because ordinary PLS can spread importance across correlated variables, while sparse PLS asks which variables still matter when each latent component must be simpler.

## Model Comparison

| Model | Predictors | Components | CV R2 | CV RMSE |
|---|---:|---:|---:|---:|
| Full unfiltered PLS | {int(f['num_predictors'])} | {int(f['selected_components'])} | {fmt(f['cv_r2'])} | {fmt(f['cv_rmse'])} |
| Step 3 cleaned PLS | {int(c['num_predictors'])} | {int(c['selected_components'])} | {fmt(c['cv_r2'])} | {fmt(c['cv_rmse'])} |
| Sparse PLS | {int(s['num_predictors'])} | {int(s['selected_components'])} | {fmt(s['cv_r2'])} | {fmt(s['cv_rmse'])} |

Best sparse setting: keep {int(s['keep_per_component'])} variables per component.

## Top Sparse PLS Variables

{md_table(top, ['Variable', 'Family', 'VIP', 'In Sparse Weights', 'Components'])}

## Interpretation

Sparse PLS is mainly a readability test. If the same variables remain important under sparsity, that strengthens the story. If performance collapses, it suggests turnout is being explained by a wider bundled social geography rather than a small handful of variables.

Sparse PLS did not introduce new raw variables beyond the cleaned predictor set. Instead, it reweighted the same cleaned variables under a sparsity constraint. The variables that remain strongest under this stricter setup are {sparse_plain}. This supports the same reference categories as the cleaned PLS model: immigration and racialized geography, education and class resources, household composition, electoral competitiveness, age structure, and selected service-contact context.
"""
    (REPORT_ROOT / "task5a_sparse_pls_report.md").write_text(md, encoding="utf-8")


def write_supervised_pca_report(
    full_summary: pd.DataFrame,
    clean_summary: pd.DataFrame,
    pca_summary: pd.DataFrame,
    loadings: pd.DataFrame,
) -> None:
    f, c, p = full_summary.iloc[0], clean_summary.iloc[0], pca_summary.iloc[0]
    screened_plain = plain_list(str(p["variables"]).split("; "))
    top = []
    for _, row in loadings.head(20).iterrows():
        top.append(
            {
                "Variable": f"`{row['variable']}`",
                "Max |loading|": fmt(row["max_abs_loading"]),
            }
        )
    md = f"""# Step 5B: Supervised PCA Comparison

Supervised PCA first screens variables by their relationship with turnout, then runs ordinary PCA on the screened variable set. It is less directly supervised than PLS, but easier to explain: turnout chooses the variable set; PCA summarizes the selected predictors.

## Model Comparison

| Model | Predictors/Screened Vars | Components | CV R2 | CV RMSE |
|---|---:|---:|---:|---:|
| Full unfiltered PLS | {int(f['num_predictors'])} | {int(f['selected_components'])} | {fmt(f['cv_r2'])} | {fmt(f['cv_rmse'])} |
| Step 3 cleaned PLS | {int(c['num_predictors'])} | {int(c['selected_components'])} | {fmt(c['cv_r2'])} | {fmt(c['cv_rmse'])} |
| Supervised PCA | {int(p['screened_predictor_count'])} | {int(p['n_components'])} | {fmt(p['cv_r2'])} | {fmt(p['cv_rmse'])} |

Best screen: `{p['screen']}`.

## Largest PCA Loadings In Best Screen

{md_table(top, ['Variable', 'Max |loading|'])}

## Interpretation

Supervised PCA is a useful comparison because it asks whether a simple turnout-screened latent structure can compete with PLS. If it performs similarly, the final story can lean more on interpretable screened dimensions. If it underperforms, PLS remains the stronger supervised reduction method.

The best supervised PCA screen retained these plain-language variables: {screened_plain}. This model is useful as a reference-category check because it independently returns a compact set around racialized and citizenship geography, education and class, household structure, electoral competitiveness, age structure, social housing, carlessness, and KSI collisions. Because its predictive performance is weaker than PLS, I would use it as supporting evidence rather than the main model.
"""
    (REPORT_ROOT / "task5b_supervised_pca_report.md").write_text(md, encoding="utf-8")


def write_elastic_net_report(
    grid: pd.DataFrame,
    importance: pd.DataFrame,
    full_importance: pd.DataFrame,
    clean_importance: pd.DataFrame,
) -> None:
    best = grid.iloc[0]
    selected = importance[importance["selected"]].copy()
    selected_plain = plain_list(selected.head(12)["variable"].tolist())
    top = []
    for _, row in selected.head(25).iterrows():
        top.append(
            {
                "Variable": f"`{row['variable']}`",
                "Family": row["family"],
                "Abs scaled coef": fmt(row["abs_scaled_coefficient"]),
                "Direction": "higher turnout" if row["elastic_net_coefficient"] > 0 else "lower turnout",
            }
        )
    clean_top = set(clean_importance.head(12)["variable"])
    elastic_selected = set(selected["variable"])
    overlap = sorted(clean_top & elastic_selected)
    md = f"""# Step 5C: Elastic Net Robustness Check

Elastic Net is not a latent-variable method. It is included here as a robustness check on the interaction-augmented candidate set: if a variable or interaction is important in PLS/VIP and also survives penalized regression, that is stronger evidence that it belongs in the final story.

## Best Elastic Net Setting

- Alpha: {best['alpha']}
- L1 ratio: {best['l1_ratio']}
- Mean selected variables across folds: {fmt(best['mean_selected_variables'])}
- CV R2 on scaled turnout: {fmt(best['cv_r2'])}
- CV RMSE on scaled turnout: {fmt(best['cv_rmse_scaled_y'])}

## Selected Variables

{md_table(top, ['Variable', 'Family', 'Abs scaled coef', 'Direction'])}

## Agreement With Interaction-Augmented PLS

Top interaction-augmented PLS variables also selected by Elastic Net:

{chr(10).join(f'- `{v}`' for v in overlap) if overlap else '_No overlap in the top cleaned-PLS set._'}

## Interpretation

Elastic Net should not replace PLS for this project because it does not create latent components. Its value is diagnostic. Variables and interactions that survive both methods are sturdy candidates for the final narrative. Terms that are high-VIP but not selected by Elastic Net may still matter as part of a latent geography, but they are less convincing as standalone predictors.

The strongest Elastic Net terms in plain language are {selected_plain}. As a robustness check, this supports reference categories around racialized geography, education, young adults, apartment and density context, local electoral fragmentation, household size, low income and 311 service contact, citizenship, and federal competitiveness.
"""
    (REPORT_ROOT / "task5c_elastic_net_robustness_report.md").write_text(md, encoding="utf-8")


def main() -> None:
    for root in [
        OUTPUT_ROOT,
        REPORT_ROOT,
        FULL_ROOT,
        DIAG_ROOT,
        CLEAN_ROOT,
        INTERACTION_ROOT,
        SPARSE_ROOT,
        SUPERVISED_PCA_ROOT,
        ELASTIC_NET_ROOT,
    ]:
        root.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT)
    predictors = predictor_universe(df)
    pd.DataFrame({"variable": predictors}).to_csv(OUTPUT_ROOT / "predictor_universe.csv", index=False)

    full_model, full_importance = pls_outputs(df, predictors, "full_unfiltered_pls", FULL_ROOT)
    full_summary = pd.read_csv(FULL_ROOT / "full_unfiltered_pls_summary.csv")
    full_loadings = pd.read_csv(FULL_ROOT / "full_unfiltered_pls_component_loadings.csv")
    write_full_report(full_summary, full_importance, full_loadings)

    var_diag = diagnostics(df, predictors, full_importance)
    pairs = pd.read_csv(DIAG_ROOT / "high_correlation_pairs.csv")
    families = pd.read_csv(DIAG_ROOT / "correlated_variable_families.csv")
    vif = pd.read_csv(DIAG_ROOT / "vif_full_predictor_set.csv")
    write_diag_report(var_diag, pairs, families, vif)

    decisions = select_clean_variables(var_diag, full_importance)
    tournament_df = tournament(df, decisions)
    selected_predictors = decisions.loc[decisions["selected"], "variable"].tolist()
    clean_model, clean_importance = pls_outputs(df, selected_predictors, "theory_cleaned_pls", CLEAN_ROOT)
    clean_vif = vif_dataframe(df, selected_predictors)
    clean_vif.to_csv(CLEAN_ROOT / "theory_cleaned_pls_vif.csv", index=False)
    clean_summary = pd.read_csv(CLEAN_ROOT / "theory_cleaned_pls_summary.csv")
    write_clean_report(full_summary, clean_summary, decisions, tournament_df, clean_importance, clean_vif)
    run_interaction_discovery(df, decisions, clean_summary, clean_importance)
    run_sparse_pls(df, selected_predictors, full_summary, clean_summary)
    run_supervised_pca(df, selected_predictors, full_summary, clean_summary)
    interaction_predictors = pd.read_csv(INTERACTION_ROOT / "interaction_augmented_predictors.csv")["variable"].tolist()
    interaction_importance = pd.read_csv(INTERACTION_ROOT / "interaction_augmented_pls_variable_importance.csv")
    interaction_pairs = [tuple(name.split("__x__") + [name]) for name in interaction_predictors if "__x__" in name]
    interaction_df = add_interactions(df, interaction_pairs)
    run_elastic_net(interaction_df, interaction_predictors, full_importance, interaction_importance)

    manifest = pd.DataFrame(
        [
            {"artifact": "predictor_universe", "path": str(OUTPUT_ROOT / "predictor_universe.csv")},
            {"artifact": "task1_report", "path": str(REPORT_ROOT / "task1_full_pls_summary.md")},
            {"artifact": "task2_report", "path": str(REPORT_ROOT / "task2_multicollinearity_diagnostics.md")},
            {"artifact": "task3_report", "path": str(REPORT_ROOT / "task3_theory_cleaned_pls_report.md")},
            {"artifact": "full_pls_importance", "path": str(FULL_ROOT / "full_unfiltered_pls_variable_importance.csv")},
            {"artifact": "vif", "path": str(DIAG_ROOT / "vif_full_predictor_set.csv")},
            {"artifact": "high_correlation_pairs", "path": str(DIAG_ROOT / "high_correlation_pairs.csv")},
            {"artifact": "cleaned_variable_decisions", "path": str(CLEAN_ROOT / "theory_cleaned_variable_decisions.csv")},
            {"artifact": "family_tournament", "path": str(CLEAN_ROOT / "variable_family_tournament_results.csv")},
            {"artifact": "cleaned_pls_importance", "path": str(CLEAN_ROOT / "theory_cleaned_pls_variable_importance.csv")},
            {"artifact": "cleaned_pls_vif", "path": str(CLEAN_ROOT / "theory_cleaned_pls_vif.csv")},
            {"artifact": "task4_report", "path": str(REPORT_ROOT / "task4_interaction_discovery_report.md")},
            {"artifact": "interaction_screen", "path": str(INTERACTION_ROOT / "interaction_screen_results.csv")},
            {"artifact": "interaction_pls_importance", "path": str(INTERACTION_ROOT / "interaction_augmented_pls_variable_importance.csv")},
            {"artifact": "task5a_report", "path": str(REPORT_ROOT / "task5a_sparse_pls_report.md")},
            {"artifact": "sparse_pls_importance", "path": str(SPARSE_ROOT / "sparse_pls_variable_importance.csv")},
            {"artifact": "task5b_report", "path": str(REPORT_ROOT / "task5b_supervised_pca_report.md")},
            {"artifact": "supervised_pca_loadings", "path": str(SUPERVISED_PCA_ROOT / "supervised_pca_loadings.csv")},
            {"artifact": "task5c_report", "path": str(REPORT_ROOT / "task5c_elastic_net_robustness_report.md")},
            {"artifact": "elastic_net_selection", "path": str(ELASTIC_NET_ROOT / "elastic_net_variable_selection.csv")},
        ]
    )
    manifest.to_csv(OUTPUT_ROOT / "artifact_manifest.csv", index=False)


if __name__ == "__main__":
    main()
