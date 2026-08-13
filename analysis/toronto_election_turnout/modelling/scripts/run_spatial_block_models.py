"""Run 25 block models with median imputation and spatial-error diagnostics.

This script intentionally avoids optional PySAL/statsmodels dependencies so it
can run in the project environment. It uses numpy for OLS and a maximum
likelihood spatial-error fit over a row-standardized Queen contiguity matrix.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from html import escape
import json
from math import erf, isfinite, sqrt
from pathlib import Path
import random

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
VARIABLE_MASTER = DATA_ROOT / "variables" / "processed" / "toronto_ct_blocks_1_5_modelling_master.csv"
VARIABLE_MASTER_GEOJSON = DATA_ROOT / "variables" / "processed" / "toronto_ct_blocks_1_5_modelling_master.geojson"
OUTPUT_ROOT = DATA_ROOT / "modelling" / "processed" / "spatial_models"
IMPUTED_OUTPUT = OUTPUT_ROOT / "toronto_ct_blocks_1_5_model_input_median_imputed.csv"
SUMMARY_OUTPUT = OUTPUT_ROOT / "spatial_block_model_summary.csv"
COEFFICIENT_OUTPUT = OUTPUT_ROOT / "spatial_block_model_coefficients.csv"
IMPUTATION_OUTPUT = OUTPUT_ROOT / "median_imputation_report.csv"
REPORT_OUTPUT = OUTPUT_ROOT / "spatial_block_model_report.html"


DEPENDENT_VARIABLES = {
    "A_municipal_turnout": "outcome_municipal_participation_citizen_18plus",
    "B_provincial_turnout": "outcome_provincial_participation_citizen_18plus",
    "C_federal_turnout": "outcome_federal_participation_citizen_18plus",
    "D_federal_minus_municipal": "outcome_federal_minus_municipal_participation",
    "E_mean_turnout": "outcome_mean_participation_citizen_18plus",
}


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


@dataclass
class Fit:
    beta: np.ndarray
    se: np.ndarray
    t: np.ndarray
    p: np.ndarray
    yhat: np.ndarray
    residuals: np.ndarray
    sse: float
    sigma2: float
    r2: float
    adjusted_r2: float
    rmse: float
    aic: float
    loglik: float


@dataclass
class SpatialErrorFit:
    lam: float
    lambda_se: float | None
    lambda_z: float | None
    lambda_p: float | None
    beta: np.ndarray
    se: np.ndarray
    t: np.ndarray
    p: np.ndarray
    residuals: np.ndarray
    filtered_residuals: np.ndarray
    sigma2: float
    aic: float
    loglik: float
    success: bool


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
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


def as_number(value: object) -> float | None:
    text = "" if value is None else str(value).strip().replace(",", "")
    if not text or text.lower() in {"none", "nan", "null", "n/a", "na", "..", "...", "x"}:
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    return parsed if isfinite(parsed) else None


def fmt(value: object, digits: int = 6) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float) or hasattr(value, "item"):
        value = float(value)
        if not isfinite(value):
            return ""
        return f"{value:.{digits}g}"
    return str(value)


def normal_p(z: float | None) -> float | None:
    if z is None or not isfinite(z):
        return None
    cdf = 0.5 * (1 + erf(abs(z) / sqrt(2)))
    return 2 * (1 - cdf)


def significance(p: float | None) -> str:
    if p is None:
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.1:
        return "."
    return ""


def add_derived_outcomes(rows: list[dict[str, str]]) -> None:
    for row in rows:
        federal = as_number(row.get("outcome_federal_participation_citizen_18plus"))
        municipal = as_number(row.get("outcome_municipal_participation_citizen_18plus"))
        row["outcome_federal_minus_municipal_participation"] = (
            fmt(federal - municipal, 10) if federal is not None and municipal is not None else ""
        )


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def impute_rows(rows: list[dict[str, str]], columns: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    out = [dict(row) for row in rows]
    report = []
    for col in columns:
        values = [as_number(row.get(col)) for row in out]
        present = [value for value in values if value is not None]
        missing_count = len(values) - len(present)
        if not present:
            report.append(
                {
                    "variable": col,
                    "missing_count": missing_count,
                    "imputed_count": 0,
                    "median": "",
                    "note": "No observed values; left missing.",
                }
            )
            continue
        med = median(present)
        imputed = 0
        flag_col = f"{col}_median_imputed"
        for row in out:
            if as_number(row.get(col)) is None:
                row[col] = fmt(med, 10)
                row[flag_col] = "true"
                imputed += 1
            else:
                row[flag_col] = "false"
        report.append(
            {
                "variable": col,
                "missing_count": missing_count,
                "imputed_count": imputed,
                "median": fmt(med, 10),
                "note": "Median filled from non-missing CT rows.",
            }
        )
    return out, report


def ols(y: np.ndarray, x: np.ndarray) -> Fit:
    n, cols = x.shape
    xtx_inv = np.linalg.pinv(x.T @ x)
    beta = xtx_inv @ x.T @ y
    yhat = x @ beta
    residuals = y - yhat
    sse = float(residuals.T @ residuals)
    y_centered = y - y.mean()
    sst = float(y_centered.T @ y_centered)
    dof = max(n - cols, 1)
    sigma2 = sse / dof
    se = np.sqrt(np.maximum(np.diag(xtx_inv) * sigma2, 0))
    t = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se != 0)
    p = np.array([normal_p(float(v)) if isfinite(float(v)) else np.nan for v in t])
    r2 = 1 - sse / sst if sst > 0 else np.nan
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / dof if sst > 0 else np.nan
    rmse = sqrt(sigma2)
    loglik = float(-0.5 * n * (np.log(2 * np.pi) + np.log(sse / n) + 1))
    aic = float(2 * cols - 2 * loglik)
    return Fit(beta, se, t, p, yhat, residuals, sse, sigma2, r2, adjusted_r2, rmse, aic, loglik)


def standardized_betas(y: np.ndarray, x_raw: np.ndarray) -> np.ndarray:
    y_sd = y.std(ddof=1)
    if y_sd == 0:
        return np.full(x_raw.shape[1], np.nan)
    y_z = (y - y.mean()) / y_sd
    cols = []
    for idx in range(x_raw.shape[1]):
        col = x_raw[:, idx]
        sd = col.std(ddof=1)
        if sd == 0:
            return np.full(x_raw.shape[1], np.nan)
        cols.append((col - col.mean()) / sd)
    x_z = np.column_stack([np.ones(len(y)), *cols])
    return ols(y_z, x_z).beta[1:]


def morans_i(values: np.ndarray, w: np.ndarray, permutations: int = 199) -> tuple[float, float]:
    z = values - values.mean()
    denom = float(z.T @ z)
    s0 = float(w.sum())
    if denom == 0 or s0 == 0:
        return np.nan, np.nan
    observed = float((len(z) / s0) * (z.T @ w @ z) / denom)
    rng = random.Random(20260715)
    extreme = 0
    arr = list(z)
    for _ in range(permutations):
        rng.shuffle(arr)
        zp = np.array(arr, dtype=float)
        perm_i = float((len(zp) / s0) * (zp.T @ w @ zp) / denom)
        if abs(perm_i) >= abs(observed):
            extreme += 1
    return observed, (extreme + 1) / (permutations + 1)


def spatial_error_loglik(lam: float, y: np.ndarray, x: np.ndarray, w: np.ndarray) -> tuple[float, np.ndarray, np.ndarray, float]:
    n = len(y)
    a = np.eye(n) - lam * w
    sign, logdet = np.linalg.slogdet(a)
    if sign <= 0:
        return -np.inf, np.array([]), np.array([]), np.inf
    ys = a @ y
    xs = a @ x
    fit = ols(ys, xs)
    sse = fit.sse
    if sse <= 0:
        return -np.inf, fit.beta, fit.residuals, np.inf
    ll = float(logdet - 0.5 * n * (np.log(2 * np.pi) + np.log(sse / n) + 1))
    return ll, fit.beta, fit.residuals, sse / n


def fit_spatial_error(y: np.ndarray, x: np.ndarray, w: np.ndarray) -> SpatialErrorFit:
    n, cols = x.shape
    grid = np.linspace(-0.95, 0.95, 191)
    vals = [(spatial_error_loglik(float(lam), y, x, w)[0], float(lam)) for lam in grid]
    _, best = max(vals, key=lambda item: item[0])
    lo = max(-0.98, best - 0.03)
    hi = min(0.98, best + 0.03)
    gr = (sqrt(5) - 1) / 2
    c = hi - gr * (hi - lo)
    d = lo + gr * (hi - lo)
    for _ in range(60):
        fc = spatial_error_loglik(c, y, x, w)[0]
        fd = spatial_error_loglik(d, y, x, w)[0]
        if fc < fd:
            lo = c
            c = d
            d = lo + gr * (hi - lo)
        else:
            hi = d
            d = c
            c = hi - gr * (hi - lo)
    lam = (lo + hi) / 2
    loglik, beta, filtered_residuals, sigma2 = spatial_error_loglik(lam, y, x, w)
    residuals = y - x @ beta

    a = np.eye(n) - lam * w
    xs = a @ x
    xtx_inv = np.linalg.pinv(xs.T @ xs)
    se = np.sqrt(np.maximum(np.diag(xtx_inv) * sigma2, 0))
    t = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se != 0)
    p = np.array([normal_p(float(v)) if isfinite(float(v)) else np.nan for v in t])

    h = 1e-4
    ll0 = loglik
    llp = spatial_error_loglik(min(0.98, lam + h), y, x, w)[0]
    llm = spatial_error_loglik(max(-0.98, lam - h), y, x, w)[0]
    second = (llp - 2 * ll0 + llm) / (h * h)
    lambda_se = sqrt(-1 / second) if second < 0 else None
    lambda_z = lam / lambda_se if lambda_se not in {None, 0} else None
    lambda_p = normal_p(lambda_z)
    aic = float(2 * (cols + 1) - 2 * loglik)
    return SpatialErrorFit(lam, lambda_se, lambda_z, lambda_p, beta, se, t, p, residuals, filtered_residuals, sigma2, aic, loglik, True)


def load_queen_weights(ct_ids: list[str]) -> np.ndarray:
    geojson = json.loads(VARIABLE_MASTER_GEOJSON.read_text(encoding="utf-8"))
    wanted = set(ct_ids)
    vertices: dict[str, set[tuple[float, float]]] = {}
    centroids: dict[str, tuple[float, float]] = {}

    def rings(geometry: dict) -> list[list[list[float]]]:
        if geometry["type"] == "Polygon":
            return geometry["coordinates"]
        if geometry["type"] == "MultiPolygon":
            return [ring for polygon in geometry["coordinates"] for ring in polygon]
        return []

    for feature in geojson["features"]:
        ct_id = str(feature["properties"]["ct_id"])
        if ct_id not in wanted:
            continue
        pts = []
        for ring in rings(feature["geometry"]):
            for coord in ring:
                x, y = float(coord[0]), float(coord[1])
                pts.append((x, y))
        vertices[ct_id] = {(round(x, 7), round(y, 7)) for x, y in pts}
        centroids[ct_id] = (
            sum(x for x, _ in pts) / len(pts),
            sum(y for _, y in pts) / len(pts),
        ) if pts else (0.0, 0.0)
    n = len(ct_ids)
    w = np.zeros((n, n), dtype=float)
    for i, left_id in enumerate(ct_ids):
        left_vertices = vertices[left_id]
        for j in range(i + 1, n):
            if left_vertices.intersection(vertices[ct_ids[j]]):
                w[i, j] = 1.0
                w[j, i] = 1.0
    row_sums = w.sum(axis=1)
    # Rare islands get connected to their nearest centroid so W has no empty rows.
    if np.any(row_sums == 0):
        centroid_list = [centroids[ct_id] for ct_id in ct_ids]
        for i in np.where(row_sums == 0)[0]:
            x0, y0 = centroid_list[i]
            distances = [((x0 - centroid_list[j][0]) ** 2 + (y0 - centroid_list[j][1]) ** 2, j) for j in range(n) if j != i]
            _, j = min(distances)
            w[i, j] = 1.0
            w[j, i] = 1.0
        row_sums = w.sum(axis=1)
    return w / row_sums[:, None]


def design_matrix(rows: list[dict[str, str]], dependent: str, predictors: list[str]) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
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


def html_table(headers: list[str], rows: list[list[object]], cls: str = "") -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{escape(fmt(cell))}</td>" for cell in row) + "</tr>")
    return f"<table class='{cls}'><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def run() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = read_csv(VARIABLE_MASTER)
    add_derived_outcomes(rows)
    model_columns = sorted({col for cols in BLOCKS.values() for col in cols} | set(DEPENDENT_VARIABLES.values()))
    imputed, imputation_report = impute_rows(rows, model_columns)
    write_csv(IMPUTED_OUTPUT, imputed)
    write_csv(IMPUTATION_OUTPUT, imputation_report)

    ct_ids_all = [row["ct_id"] for row in imputed]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}

    summary_rows: list[dict[str, object]] = []
    coef_rows: list[dict[str, object]] = []
    report_sections = []

    model_index = 0
    for dv_label, dependent in DEPENDENT_VARIABLES.items():
        for block, predictors in BLOCKS.items():
            model_index += 1
            model_id = f"{model_index:02d}_{dv_label}__{block}"
            ct_ids, y, x, x_raw = design_matrix(imputed, dependent, predictors)
            idx = [index_all[ct_id] for ct_id in ct_ids]
            w = w_all[np.ix_(idx, idx)]
            w = w / w.sum(axis=1, keepdims=True)

            ols_fit = ols(y, x)
            sem_fit = fit_spatial_error(y, x, w)
            moran_ols, moran_ols_p = morans_i(ols_fit.residuals, w)
            moran_sem, moran_sem_p = morans_i(sem_fit.filtered_residuals, w)
            std = standardized_betas(y, x_raw)
            delta_aic = sem_fit.aic - ols_fit.aic
            spatial_effect = bool(
                sem_fit.lambda_p is not None
                and sem_fit.lambda_p < 0.05
                and abs(sem_fit.lam) >= 0.1
            )
            summary = {
                "model_id": model_id,
                "dependent_variable": dependent,
                "block": block,
                "n": len(y),
                "ols_adjusted_r2": ols_fit.adjusted_r2,
                "ols_aic": ols_fit.aic,
                "ols_rmse": ols_fit.rmse,
                "ols_residual_morans_i": moran_ols,
                "ols_residual_morans_p_perm": moran_ols_p,
                "spatial_lambda": sem_fit.lam,
                "spatial_lambda_se": sem_fit.lambda_se,
                "spatial_lambda_p": sem_fit.lambda_p,
                "spatial_aic": sem_fit.aic,
                "spatial_filtered_residual_morans_i": moran_sem,
                "spatial_filtered_residual_morans_p_perm": moran_sem_p,
                "delta_aic_spatial_minus_ols": delta_aic,
                "spatial_effect_flag": "yes" if spatial_effect else "no",
            }
            summary_rows.append(summary)

            names = ["intercept"] + predictors
            for i, name in enumerate(names):
                coef_rows.append(
                    {
                        "model_id": model_id,
                        "model_type": "OLS",
                        "term": name,
                        "coefficient": ols_fit.beta[i],
                        "std_error": ols_fit.se[i],
                        "z_or_t": ols_fit.t[i],
                        "p_value": ols_fit.p[i],
                        "significance": significance(float(ols_fit.p[i])) if isfinite(float(ols_fit.p[i])) else "",
                        "standardized_beta": std[i - 1] if i > 0 else "",
                    }
                )
                coef_rows.append(
                    {
                        "model_id": model_id,
                        "model_type": "Spatial error",
                        "term": name,
                        "coefficient": sem_fit.beta[i],
                        "std_error": sem_fit.se[i],
                        "z_or_t": sem_fit.t[i],
                        "p_value": sem_fit.p[i],
                        "significance": significance(float(sem_fit.p[i])) if isfinite(float(sem_fit.p[i])) else "",
                        "standardized_beta": "",
                    }
                )

            metric_rows = [
                ["OLS", ols_fit.adjusted_r2, ols_fit.aic, ols_fit.rmse, moran_ols, moran_ols_p],
                ["Spatial error", "", sem_fit.aic, sqrt(sem_fit.sigma2), moran_sem, moran_sem_p],
            ]
            coef_display = []
            for i, name in enumerate(names):
                coef_display.append(
                    [
                        name,
                        ols_fit.beta[i],
                        ols_fit.p[i],
                        significance(float(ols_fit.p[i])) if isfinite(float(ols_fit.p[i])) else "",
                        sem_fit.beta[i],
                        sem_fit.p[i],
                        significance(float(sem_fit.p[i])) if isfinite(float(sem_fit.p[i])) else "",
                    ]
                )
            report_sections.append(
                f"<section><h2>{escape(model_id)}</h2>"
                f"<p><strong>Spatial lambda:</strong> {fmt(sem_fit.lam)} "
                f"(p={fmt(sem_fit.lambda_p)}); <strong>Delta AIC spatial-OLS:</strong> {fmt(delta_aic)}; "
                f"<strong>Spatial effect:</strong> {'yes' if spatial_effect else 'no'}.</p>"
                + html_table(["Model", "Adj R2", "AIC", "RMSE", "Residual Moran I", "Moran p"], metric_rows)
                + html_table(["Term", "OLS coef", "OLS p", "", "SEM coef", "SEM p", ""], coef_display, "coef")
                + "</section>"
            )

    write_csv(SUMMARY_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in summary_rows])
    write_csv(COEFFICIENT_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in coef_rows])

    significant = [row for row in summary_rows if row["spatial_effect_flag"] == "yes"]
    improved = [row for row in summary_rows if as_number(row["delta_aic_spatial_minus_ols"]) is not None and float(row["delta_aic_spatial_minus_ols"]) < -2]
    impute_display = [
        [row["variable"], row["missing_count"], row["imputed_count"], row["median"]]
        for row in imputation_report
        if int(row["missing_count"]) > 0
    ]
    summary_display = [
        [
            row["model_id"],
            row["n"],
            row["ols_adjusted_r2"],
            row["ols_residual_morans_i"],
            row["ols_residual_morans_p_perm"],
            row["spatial_lambda"],
            row["spatial_lambda_p"],
            row["delta_aic_spatial_minus_ols"],
            row["spatial_effect_flag"],
        ]
        for row in summary_rows
    ]
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Toronto CT Turnout Spatial Block Models</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1f2933; }}
h1 {{ font-size: 28px; margin-bottom: 4px; }}
h2 {{ font-size: 20px; margin-top: 32px; border-top: 1px solid #d8dee4; padding-top: 18px; }}
p, li {{ line-height: 1.45; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; font-size: 12px; }}
th, td {{ border: 1px solid #d8dee4; padding: 6px 8px; text-align: right; vertical-align: top; }}
th:first-child, td:first-child {{ text-align: left; }}
th {{ background: #f6f8fa; position: sticky; top: 0; }}
.coef td:first-child {{ max-width: 260px; word-break: break-word; }}
.note {{ background: #fff8dc; border: 1px solid #ead98b; padding: 12px 14px; }}
</style>
</head>
<body>
<h1>Toronto CT Turnout Spatial Block Models</h1>
<p class="note">Rows use the 585 Census Tracts in the Toronto interpolation universe. Missing predictor/outcome entries were filled with the column median only when at least one observed value existed.</p>
<h2>Executive Summary</h2>
<ul>
<li>Models run: {len(summary_rows)} OLS models and {len(summary_rows)} spatial-error counterparts.</li>
<li>Spatial-effect flags: {len(significant)} of {len(summary_rows)} models have |lambda| >= 0.1 and lambda p &lt; 0.05.</li>
<li>AIC materially improves for the spatial-error version in {len(improved)} models using Delta AIC &lt; -2.</li>
</ul>
<h2>Median Imputation</h2>
{html_table(["Variable", "Missing", "Imputed", "Median"], impute_display)}
<h2>All Model Summary</h2>
{html_table(["Model", "N", "OLS adj R2", "OLS Moran I", "OLS Moran p", "Lambda", "Lambda p", "Delta AIC", "Spatial effect"], summary_display)}
{''.join(report_sections)}
</body>
</html>
"""
    REPORT_OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote imputed input: {IMPUTED_OUTPUT}")
    print(f"Wrote summary: {SUMMARY_OUTPUT}")
    print(f"Wrote coefficients: {COEFFICIENT_OUTPUT}")
    print(f"Wrote report: {REPORT_OUTPUT}")


if __name__ == "__main__":
    run()
