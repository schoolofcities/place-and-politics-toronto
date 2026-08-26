"""Advanced spatial validation, PLS stability, and domain attribution."""

from __future__ import annotations

from itertools import combinations
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


REPO_ROOT = Path(__file__).resolve().parents[5]
MEETING_SCRIPT_ROOT = Path(__file__).resolve().parent
SHARED_ROOT = REPO_ROOT / "analysis/toronto_election_turnout/modelling/dimension_reduction/scripts"
sys.path.insert(0, str(MEETING_SCRIPT_ROOT))
sys.path.insert(0, str(SHARED_ROOT))

import run_dimension_reduction_workflow as wf  # noqa: E402
import run_meeting_pls as meeting  # noqa: E402


INPUT = wf.INPUT
GEOMETRY = REPO_ROOT / "data/toronto_election_turnout/variables/processed/toronto_ct_blocks_1_5_modelling_master.geojson"
BASE = REPO_ROOT / "data/toronto_election_turnout/modelling/processed/dimension_reduction/meeting_PLS/turnout_level_comparisons"
OUT = BASE / "advanced_validation"
SPATIAL_ROOT = OUT / "01_spatial_nested_cv"
BOOT_ROOT = OUT / "02_spatial_block_bootstrap"
DOMAIN_ROOT = OUT / "03_domain_importance"
REPORT_ROOT = OUT / "reports"

OUTCOMES = {
    "mean": ("Mean turnout", "outcome_mean_participation_citizen_18plus"),
    "municipal": ("Municipal turnout", "outcome_municipal_participation_citizen_18plus"),
    "provincial": ("Provincial turnout", "outcome_provincial_participation_citizen_18plus"),
    "federal": ("Federal turnout", "outcome_federal_participation_citizen_18plus"),
}

DOMAINS = {
    "age_structure": ["block1_age_18_34_share", "block1_age_65_plus_share"],
    "education_income_household": [
        "block1_average_household_size",
        "block1_bachelors_or_higher_25_64_share",
        "block1_low_income_lim_at_share",
    ],
    "tenure": ["block2_renter_share"],
    "residential_stability": ["block2_same_address_5yr_share"],
    "urban_form": [
        "block2_apartment_share",
        "block2_condo_share",
        "block2_population_density_per_km2",
    ],
    "immigration_citizenship": [
        "block3_citizen_adult_share",
        "block3_immigrant_share",
        "block3_visible_minority_share",
    ],
    "transportation": ["block5_tts_no_car_household_share"],
}

DOMAIN_LABELS = {
    "age_structure": "Age structure",
    "education_income_household": "Education, income, and household",
    "tenure": "Tenure",
    "residential_stability": "Residential stability",
    "urban_form": "Urban form",
    "immigration_citizenship": "Immigration and citizenship",
    "transportation": "Transportation",
}

PLS_COMPONENTS = {"mean": 2, "municipal": 3, "provincial": 3, "federal": 3}
OUTER_FOLDS = 5
INNER_FOLDS = 4
BOOTSTRAPS = 500
SEED = 20260818


def fmt(value: float | int, digits: int = 3) -> str:
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return "" if not np.isfinite(float(value)) else f"{float(value):.{digits}f}"


def md_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    shown = frame.fillna("")
    header = "| " + " | ".join(shown.columns) + " |"
    sep = "| " + " | ".join("---" for _ in shown.columns) + " |"
    rows = ["| " + " | ".join(str(row[c]).replace("|", "/") for c in shown.columns) + " |" for _, row in shown.iterrows()]
    return "\n".join([header, sep, *rows])


def ring_area_centroid(ring) -> tuple[float, float, float]:
    points = np.asarray(ring, dtype=float)
    if len(points) < 3:
        return 0.0, float(points[:, 0].mean()), float(points[:, 1].mean())
    x, y = points[:, 0], points[:, 1]
    cross = x[:-1] * y[1:] - x[1:] * y[:-1]
    signed_area = cross.sum() / 2
    if abs(signed_area) < 1e-15:
        return 0.0, float(x.mean()), float(y.mean())
    cx = ((x[:-1] + x[1:]) * cross).sum() / (6 * signed_area)
    cy = ((y[:-1] + y[1:]) * cross).sum() / (6 * signed_area)
    return abs(float(signed_area)), float(cx), float(cy)


def geometry_centroid(geometry) -> tuple[float, float]:
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    weighted = []
    for polygon in polygons:
        exterior_area, exterior_x, exterior_y = ring_area_centroid(polygon[0])
        area, x_sum, y_sum = exterior_area, exterior_area * exterior_x, exterior_area * exterior_y
        for hole in polygon[1:]:
            hole_area, hole_x, hole_y = ring_area_centroid(hole)
            area -= hole_area
            x_sum -= hole_area * hole_x
            y_sum -= hole_area * hole_y
        if area > 0:
            weighted.append((area, x_sum / area, y_sum / area))
    total = sum(item[0] for item in weighted)
    if total <= 0:
        raise ValueError("Could not calculate polygon centroid")
    return sum(a * x for a, x, _ in weighted) / total, sum(a * y for a, _, y in weighted) / total


def load_centroids() -> pd.DataFrame:
    data = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    rows = []
    for feature in data["features"]:
        lon, lat = geometry_centroid(feature["geometry"])
        rows.append({"ct_id": str(feature["properties"]["ct_id"]), "lon": lon, "lat": lat})
    return pd.DataFrame(rows)


def prepare_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT, dtype={"ct_id": str})
    centroids = load_centroids()
    df = df.merge(centroids, on="ct_id", how="inner", validate="one_to_one")
    if len(df) != 585:
        raise ValueError(f"Expected 585 CTs after geometry join, found {len(df)}")
    x = np.column_stack([df["lon"].to_numpy() * np.cos(np.deg2rad(df["lat"].mean())), df["lat"].to_numpy()])
    df["spatial_block"] = KMeans(n_clusters=OUTER_FOLDS, random_state=SEED, n_init=100).fit_predict(x) + 1
    centers = df.groupby("spatial_block")[["lon", "lat"]].mean().sort_values(["lon", "lat"])
    relabel = {old: new for new, old in enumerate(centers.index, 1)}
    df["spatial_block"] = df["spatial_block"].map(relabel)
    df[["ct_id", "geo_name", "lon", "lat", "spatial_block"]].to_csv(SPATIAL_ROOT / "ct_spatial_blocks.csv", index=False)
    return df


def metric(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    resid = y - pred
    sst = float(np.sum((y - y.mean()) ** 2))
    return {
        "r2": 1 - float(resid @ resid) / sst,
        "rmse": float(np.sqrt(np.mean(resid**2))),
        "mae": float(np.mean(np.abs(resid))),
    }


def pls_predict(train_x, train_y, test_x, components):
    model = wf.fit_pls(train_x, train_y, components)
    return wf.predict_pls(model, test_x)


def pca_predict(train_x, train_y, test_x, threshold, components):
    correlations = np.array([np.corrcoef(train_x[:, i], train_y)[0, 1] for i in range(train_x.shape[1])])
    selected = np.where(np.abs(correlations) >= threshold)[0] if threshold > 0 else np.arange(train_x.shape[1])
    if len(selected) < components:
        return None, len(selected)
    train_scores, test_scores, _ = wf.pca_scores(train_x[:, selected], test_x[:, selected], components)
    return wf.ols_predict(train_scores, train_y, test_scores), len(selected)


def elastic_predict(train_x, train_y, test_x, alpha, ratio):
    xm, xs = train_x.mean(axis=0), train_x.std(axis=0)
    xs[xs == 0] = 1
    ym, ys = train_y.mean(), train_y.std()
    if ys == 0:
        ys = 1
    beta = wf.elastic_net_fit((train_x - xm) / xs, (train_y - ym) / ys, alpha, ratio)
    return (((test_x - xm) / xs) @ beta) * ys + ym, int(np.sum(np.abs(beta) > 1e-6))


def inner_groups(blocks: np.ndarray, outer_block: int) -> list[np.ndarray]:
    remaining = sorted(set(blocks) - {outer_block})
    return [np.where(blocks == block)[0] for block in remaining]


def choose_pls(x, y, blocks, outer_block):
    candidates = []
    for components in range(1, 6):
        pred, actual = [], []
        for valid in inner_groups(blocks, outer_block):
            train = np.where((blocks != outer_block) & (blocks != blocks[valid[0]]))[0]
            pred.extend(pls_predict(x[train], y[train], x[valid], components))
            actual.extend(y[valid])
        candidates.append((metric(np.asarray(actual), np.asarray(pred))["rmse"], components))
    return min(candidates)[1]


def choose_pca(x, y, blocks, outer_block):
    candidates = []
    for threshold in [0.0, 0.1, 0.2, 0.3]:
        for components in range(1, 6):
            pred, actual, valid_config = [], [], True
            for valid in inner_groups(blocks, outer_block):
                train = np.where((blocks != outer_block) & (blocks != blocks[valid[0]]))[0]
                fold_pred, _ = pca_predict(x[train], y[train], x[valid], threshold, components)
                if fold_pred is None:
                    valid_config = False
                    break
                pred.extend(fold_pred)
                actual.extend(y[valid])
            if valid_config:
                candidates.append((metric(np.asarray(actual), np.asarray(pred))["rmse"], threshold, components))
    _, threshold, components = min(candidates)
    return threshold, components


def choose_elastic(x, y, blocks, outer_block):
    candidates = []
    for alpha in [0.001, 0.003, 0.01, 0.03, 0.1, 0.2]:
        for ratio in [0.0, 0.2, 0.5, 0.8, 1.0]:
            pred, actual = [], []
            for valid in inner_groups(blocks, outer_block):
                train = np.where((blocks != outer_block) & (blocks != blocks[valid[0]]))[0]
                fold_pred, _ = elastic_predict(x[train], y[train], x[valid], alpha, ratio)
                pred.extend(fold_pred)
                actual.extend(y[valid])
            candidates.append((metric(np.asarray(actual), np.asarray(pred))["rmse"], alpha, ratio))
    _, alpha, ratio = min(candidates)
    return alpha, ratio


def residual_neighbor_correlation(residuals: np.ndarray, coords: np.ndarray, k: int = 8) -> float:
    distances = ((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(distances, np.inf)
    neighbors = np.argpartition(distances, k, axis=1)[:, :k]
    neighbor_mean = residuals[neighbors].mean(axis=1)
    return float(np.corrcoef(residuals, neighbor_mean)[0, 1])


def run_spatial_nested_cv(df: pd.DataFrame) -> pd.DataFrame:
    x = df[meeting.MEETING_VARIABLES].to_numpy(float)
    blocks = df["spatial_block"].to_numpy(int)
    coords = df[["lon", "lat"]].to_numpy(float)
    summaries, predictions, tuning = [], [], []
    for key, (label, target) in OUTCOMES.items():
        y = df[target].to_numpy(float)
        for method in ["pls", "supervised_pca", "elastic_net"]:
            pred = np.zeros(len(y))
            for outer in sorted(set(blocks)):
                train, test = np.where(blocks != outer)[0], np.where(blocks == outer)[0]
                if method == "pls":
                    components = choose_pls(x, y, blocks, outer)
                    pred[test] = pls_predict(x[train], y[train], x[test], components)
                    setting = f"components={components}"
                elif method == "supervised_pca":
                    threshold, components = choose_pca(x, y, blocks, outer)
                    fold_pred, count = pca_predict(x[train], y[train], x[test], threshold, components)
                    if fold_pred is None:
                        raise RuntimeError("Selected PCA configuration was not fit-able on outer training data")
                    pred[test] = fold_pred
                    setting = f"threshold={threshold}; components={components}; predictors={count}"
                else:
                    alpha, ratio = choose_elastic(x, y, blocks, outer)
                    pred[test], count = elastic_predict(x[train], y[train], x[test], alpha, ratio)
                    setting = f"alpha={alpha}; l1_ratio={ratio}; selected={count}"
                tuning.append({"outcome": key, "method": method, "outer_block": outer, "setting": setting})
            result = metric(y, pred)
            result.update({
                "outcome": key,
                "outcome_label": label,
                "method": method,
                "residual_neighbor_correlation": residual_neighbor_correlation(y - pred, coords),
            })
            summaries.append(result)
            predictions.extend({
                "ct_id": df.iloc[i]["ct_id"], "outcome": key, "method": method,
                "spatial_block": blocks[i], "actual": y[i], "prediction": pred[i], "residual": y[i] - pred[i],
            } for i in range(len(y)))
    summary = pd.DataFrame(summaries)
    summary.to_csv(SPATIAL_ROOT / "spatial_nested_cv_summary.csv", index=False)
    pd.DataFrame(predictions).to_csv(SPATIAL_ROOT / "spatial_nested_cv_predictions.csv", index=False)
    pd.DataFrame(tuning).to_csv(SPATIAL_ROOT / "spatial_nested_cv_selected_settings.csv", index=False)
    write_spatial_report(df, summary)
    return summary


def fit_full_pls(df, key):
    x = df[meeting.MEETING_VARIABLES].to_numpy(float)
    y = df[OUTCOMES[key][1]].to_numpy(float)
    return wf.fit_pls(x, y, PLS_COMPONENTS[key])


def run_block_bootstrap(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    blocks = sorted(df["spatial_block"].unique())
    loading_rows, vip_rows = [], []
    for key in OUTCOMES:
        full = fit_full_pls(df, key)
        ycol = OUTCOMES[key][1]
        full_loadings = full.loadings
        full_vip = full.vip
        for iteration in range(BOOTSTRAPS):
            sampled_blocks = rng.choice(blocks, size=len(blocks), replace=True)
            sampled_indices = np.concatenate([np.where(df["spatial_block"].to_numpy() == block)[0] for block in sampled_blocks])
            model = wf.fit_pls(
                df.iloc[sampled_indices][meeting.MEETING_VARIABLES].to_numpy(float),
                df.iloc[sampled_indices][ycol].to_numpy(float),
                PLS_COMPONENTS[key],
            )
            aligned = model.loadings.copy()
            for comp in range(aligned.shape[1]):
                if np.dot(aligned[:, comp], full_loadings[:, comp]) < 0:
                    aligned[:, comp] *= -1
            for j, variable in enumerate(meeting.MEETING_VARIABLES):
                vip_rows.append({"outcome": key, "bootstrap": iteration + 1, "variable": variable, "vip": model.vip[j]})
                for comp in range(aligned.shape[1]):
                    loading_rows.append({
                        "outcome": key, "bootstrap": iteration + 1, "component": comp + 1,
                        "variable": variable, "loading": aligned[j, comp], "full_loading": full_loadings[j, comp],
                    })
    loadings = pd.DataFrame(loading_rows)
    vips = pd.DataFrame(vip_rows)
    loadings.to_csv(BOOT_ROOT / "bootstrap_loading_draws.csv", index=False)
    vips.to_csv(BOOT_ROOT / "bootstrap_vip_draws.csv", index=False)
    loading_summary = loadings.groupby(["outcome", "component", "variable"]).agg(
        full_loading=("full_loading", "first"), median_loading=("loading", "median"),
        lower_95=("loading", lambda x: x.quantile(.025)), upper_95=("loading", lambda x: x.quantile(.975)),
    ).reset_index()
    loading_summary["sign_stability"] = loadings.groupby(["outcome", "component", "variable"]).apply(
        lambda g: np.mean(np.sign(g["loading"]) == np.sign(g["full_loading"])), include_groups=False
    ).to_numpy()
    vip_summary = vips.groupby(["outcome", "variable"])["vip"].agg(
        median_vip="median", lower_95=lambda x: x.quantile(.025), upper_95=lambda x: x.quantile(.975)
    ).reset_index()
    loading_summary.to_csv(BOOT_ROOT / "bootstrap_loading_stability_summary.csv", index=False)
    vip_summary.to_csv(BOOT_ROOT / "bootstrap_vip_stability_summary.csv", index=False)
    write_bootstrap_report(loading_summary, vip_summary)
    return loading_summary, vip_summary


def ols_r2(x: np.ndarray, y: np.ndarray) -> float:
    design = np.column_stack([np.ones(len(x)), x]) if x.shape[1] else np.ones((len(y), 1))
    pred = design @ (np.linalg.pinv(design) @ y)
    return metric(y, pred)["r2"]


def all_domain_subsets(domains: list[str]):
    for size in range(len(domains) + 1):
        for subset in combinations(domains, size):
            yield frozenset(subset)


def run_domain_importance(df: pd.DataFrame) -> pd.DataFrame:
    domains = list(DOMAINS)
    rows, summaries = [], []
    for key, (label, target) in OUTCOMES.items():
        y = df[target].to_numpy(float)
        subset_r2 = {}
        for subset in all_domain_subsets(domains):
            variables = [v for domain in domains if domain in subset for v in DOMAINS[domain]]
            r2 = ols_r2(df[variables].to_numpy(float), y) if variables else 0.0
            subset_r2[subset] = r2
            rows.append({"outcome": key, "domains": ";".join(sorted(subset)), "domain_count": len(subset), "r2": r2})
        full = frozenset(domains)
        full_r2 = subset_r2[full]
        factorial = np.math.factorial if hasattr(np, "math") else __import__("math").factorial
        for domain in domains:
            unique = full_r2 - subset_r2[full - {domain}]
            shapley = 0.0
            others = [d for d in domains if d != domain]
            for subset in all_domain_subsets(others):
                weight = factorial(len(subset)) * factorial(len(domains) - len(subset) - 1) / factorial(len(domains))
                shapley += weight * (subset_r2[subset | {domain}] - subset_r2[subset])
            summaries.append({
                "outcome": key, "outcome_label": label, "domain": domain, "domain_label": DOMAIN_LABELS[domain],
                "full_model_r2": full_r2, "unique_r2": unique, "shapley_r2": shapley,
                "allocated_shared_r2": shapley - unique, "shapley_share_of_explained": shapley / full_r2,
            })
    pd.DataFrame(rows).to_csv(DOMAIN_ROOT / "all_domain_subset_r2.csv", index=False)
    summary = pd.DataFrame(summaries)
    summary.to_csv(DOMAIN_ROOT / "domain_commonality_shapley_summary.csv", index=False)
    bootstrap_domain_importance(df, summary)
    write_domain_report(summary)
    return summary


def bootstrap_domain_importance(df: pd.DataFrame, point_summary: pd.DataFrame) -> None:
    rng = np.random.default_rng(SEED + 1)
    blocks = sorted(df["spatial_block"].unique())
    domains = list(DOMAINS)
    rows = []
    for iteration in range(BOOTSTRAPS):
        sampled = rng.choice(blocks, len(blocks), replace=True)
        indices = np.concatenate([np.where(df["spatial_block"].to_numpy() == b)[0] for b in sampled])
        sample = df.iloc[indices]
        for key, (_, target) in OUTCOMES.items():
            y = sample[target].to_numpy(float)
            subset_r2 = {}
            for subset in all_domain_subsets(domains):
                variables = [v for domain in domains if domain in subset for v in DOMAINS[domain]]
                subset_r2[subset] = ols_r2(sample[variables].to_numpy(float), y) if variables else 0.0
            full = frozenset(domains)
            full_r2 = subset_r2[full]
            import math
            for domain in domains:
                unique = full_r2 - subset_r2[full - {domain}]
                shapley = 0.0
                others = [d for d in domains if d != domain]
                for subset in all_domain_subsets(others):
                    weight = math.factorial(len(subset)) * math.factorial(len(domains) - len(subset) - 1) / math.factorial(len(domains))
                    shapley += weight * (subset_r2[subset | {domain}] - subset_r2[subset])
                rows.append({"bootstrap": iteration + 1, "outcome": key, "domain": domain, "unique_r2": unique, "shapley_r2": shapley})
    draws = pd.DataFrame(rows)
    draws.to_csv(DOMAIN_ROOT / "domain_spatial_bootstrap_draws.csv", index=False)
    stable = draws.groupby(["outcome", "domain"]).agg(
        unique_median=("unique_r2", "median"), unique_lower_95=("unique_r2", lambda x: x.quantile(.025)), unique_upper_95=("unique_r2", lambda x: x.quantile(.975)),
        shapley_median=("shapley_r2", "median"), shapley_lower_95=("shapley_r2", lambda x: x.quantile(.025)), shapley_upper_95=("shapley_r2", lambda x: x.quantile(.975)),
    ).reset_index()
    stable.to_csv(DOMAIN_ROOT / "domain_spatial_bootstrap_summary.csv", index=False)


def write_spatial_report(df, summary):
    shown = summary[["outcome_label", "method", "r2", "rmse", "mae", "residual_neighbor_correlation"]].copy()
    shown.columns = ["Outcome", "Method", "Spatial CV R2", "RMSE", "MAE", "Residual neighbour correlation"]
    for col in shown.columns[2:]: shown[col] = shown[col].map(fmt)
    counts = df.groupby("spatial_block").size().reset_index(name="CTs")
    shuffled = {"mean": .533657, "municipal": .629326, "provincial": .370600, "federal": .316719}
    pls_rows = summary[summary["method"] == "pls"].set_index("outcome")
    comparison = ", ".join(
        f"{OUTCOMES[key][0]} {shuffled[key]:.3f} to {pls_rows.loc[key, 'r2']:.3f}"
        for key in ["mean", "municipal", "provincial", "federal"]
    )
    strongest = summary.loc[summary.groupby("outcome")["r2"].idxmax()]
    strongest_text = ", ".join(f"{row.outcome_label}: {row.method}" for row in strongest.itertuples())
    report = f"""# Step 1 Report: Spatially Blocked Nested Cross-Validation

## What has been done

The 585 CTs were joined to the project modelling geometry and divided into five deterministic compact geographic blocks. Each outer fold held out one complete block. Four inner geographic folds selected PLS component count, supervised-PCA screening/components, or elastic-net penalties using training geography only. Scaling and screening were refit inside the folds.

Block sizes were {', '.join(str(v) for v in counts['CTs'])} CTs.

## Results

{md_table(shown)}

## Interpretation and analysis

These scores estimate transfer to an unseen part of Toronto, a harder task than predicting randomly withheld nearby CTs. Compared with the earlier shuffled PLS CV, R2 changed as follows: {comparison}. The decline is real but moderate, so spatial resemblance explains part—not all—of the earlier performance. Municipal turnout remains the most predictable and federal turnout the least predictable.

PLS had the strongest spatial R2 for every outcome ({strongest_text}). The residual-neighbour correlations remain between `{fmt(summary['residual_neighbor_correlation'].min())}` and `{fmt(summary['residual_neighbor_correlation'].max())}`, showing that omitted spatial structure still clusters geographically. The 14 variables do not exhaust Toronto's spatial organization.

## Further analysis

The selected setting for every outer block is stored separately. Large setting changes across blocks indicate tuning instability. Residual maps should be inspected before treating any citywide model as geographically generalizable.

## Conclusion

Spatial nested validation directly addresses geographic leakage and tuning optimism. It does not remove spatial structure or establish causality; it reveals how much of the apparent predictive signal survives when entire areas are unseen.
"""
    (REPORT_ROOT / "01_spatial_nested_cv_report.md").write_text(report, encoding="utf-8")


def write_bootstrap_report(loadings, vips):
    primary = loadings[loadings["component"] == 1].copy()
    primary["abs_full"] = primary["full_loading"].abs()
    top = primary.sort_values(["outcome", "abs_full"], ascending=[True, False]).groupby("outcome").head(5)
    top["Variable"] = top["variable"].map(meeting.plain_name)
    shown = top[["outcome", "Variable", "full_loading", "lower_95", "upper_95", "sign_stability"]].copy()
    shown.columns = ["Outcome", "Primary-component variable", "Full loading", "Lower 95%", "Upper 95%", "Sign stability"]
    for col in shown.columns[2:]: shown[col] = shown[col].map(fmt)
    stable_share = loadings.assign(stable=loadings["sign_stability"] >= .90).groupby("outcome")["stable"].mean().reset_index()
    stable_text = ", ".join(f"{r.outcome}: {r.stable:.0%}" for r in stable_share.itertuples())
    report = f"""# Step 2 Report: Spatial-Block Bootstrap Stability

## What has been done

The five geographic blocks were resampled with replacement 500 times. For each outcome, the meeting-variable PLS was refit using its selected compact component count. Component signs were aligned to the full-data solution before summarizing loadings. The outputs report median loadings, 95% spatial-bootstrap intervals, sign stability, and VIP intervals.

## Key results

{md_table(shown)}

Across all variables and retained components, the share with at least 90% sign stability was {stable_text}.

## Interpretation and analysis

A high sign-stability value means a variable remains on the same side of a component when entire Toronto regions are emphasized or omitted by resampling. The strongest primary anchors are highly stable: visible-minority and immigrant shares remain on the lower-turnout side, while bachelor-level education remains on the higher-turnout side across the outcome models. Municipal citizenship and low-income loadings are also especially stable; federal household size and residential stability are stable anchors of its more housing-oriented construction.

Narrow intervals indicate magnitude stability. Some smaller primary loadings and many later-component loadings cross zero, explaining why the overall 90%-stable share is lower for mean and provincial models. Those terms should not anchor the narrative even if their full-data loading appears non-zero.

## Further analysis

The primary component deserves the most narrative weight because later deflated components are usually less stable and have weaker direct outcome relationships. VIP stability should support variable ranking, while loading stability should support component naming; neither is a causal effect.

## Conclusion

The bootstrap distinguishes a reproducible citywide latent story from component details that depend on particular geographic blocks. Final prose should emphasize variables with stable direction and avoid over-interpreting unstable secondary loadings.
"""
    (REPORT_ROOT / "02_spatial_block_bootstrap_stability_report.md").write_text(report, encoding="utf-8")


def write_domain_report(summary):
    top = summary.sort_values(["outcome", "shapley_r2"], ascending=[True, False]).groupby("outcome").head(4).copy()
    shown = top[["outcome_label", "domain_label", "unique_r2", "shapley_r2", "allocated_shared_r2", "shapley_share_of_explained"]].copy()
    shown.columns = ["Outcome", "Domain", "Unique R2", "Shapley R2", "Allocated shared R2", "Share of explained R2"]
    for col in shown.columns[2:]: shown[col] = shown[col].map(fmt)
    leaders = summary.loc[summary.groupby("outcome")["shapley_r2"].idxmax()]
    leader_text = "; ".join(f"{r.outcome_label}: {r.domain_label}" for r in leaders.itertuples())
    paired = summary[summary["domain"].isin(["education_income_household", "immigration_citizenship"])]
    paired_share = paired.groupby("outcome")["shapley_share_of_explained"].sum()
    paired_text = ", ".join(f"{OUTCOMES[key][0]} {paired_share[key]:.1%}" for key in OUTCOMES)
    report = f"""# Step 3 Report: Domain Commonality and Shapley Relative Importance

## What has been done

The seven manually specified research domains were held fixed exactly as proposed. All 128 possible domain-subset OLS models were fit for each outcome. Unique R2 is the loss from removing a domain from the full model. Shapley R2 averages its incremental contribution over every possible domain entry order. The difference is the domain's allocated share of variance jointly explained with other domains. A 500-draw spatial-block bootstrap supplies uncertainty files.

## Results

{md_table(shown)}

The largest Shapley domain for each outcome was: {leader_text}.

## Interpretation and analysis

Unique R2 answers whether a domain adds information after every other domain is present. Shapley R2 answers how much of the total explained variation should be attributed to that domain after shared explanatory power is distributed fairly. Education/resources and immigration/citizenship jointly receive {paired_text} of explained R2. They dominate every outcome, but their unique contributions are much smaller than their Shapley allocations. This directly confirms the bundled interpretation: both domains are important largely because they describe overlapping Toronto social geography.

Municipal turnout is the only outcome led by immigration/citizenship; mean, provincial, and federal turnout are led by education/income/household. Federal turnout gives a noticeably larger relative role to age and urban form, consistent with the earlier level-versus-mean interpretation. Residential stability and transportation have very small unique R2 even when they receive some shared allocation.

## Further analysis

The spatial-bootstrap intervals should govern claims about rank. Domains with overlapping intervals should be described as jointly important rather than strictly ordered. Single-variable domains—tenure, stability, and transportation—are observed blocks, not latent constructs.

## Conclusion

This stage does not eliminate correlated bundles. It makes the bundling explicit by separating unique contribution from shared allocated contribution, allowing the final story to say which domains add distinct information and which describe the same Toronto geography.
"""
    (REPORT_ROOT / "03_domain_commonality_shapley_report.md").write_text(report, encoding="utf-8")


def write_integrated_report(spatial, loading_stability, domain):
    pls = spatial[spatial["method"] == "pls"].set_index("outcome")
    domain_leaders = domain.loc[domain.groupby("outcome")["shapley_r2"].idxmax()].set_index("outcome")
    rows = []
    for key, (label, _) in OUTCOMES.items():
        comp1 = loading_stability[(loading_stability["outcome"] == key) & (loading_stability["component"] == 1)]
        rows.append({
            "Outcome": label, "Spatial PLS R2": fmt(pls.loc[key, "r2"]),
            "Primary loading sign stability": fmt((comp1["sign_stability"] >= .90).mean()),
            "Leading Shapley domain": domain_leaders.loc[key, "domain_label"],
            "Leading domain share": fmt(domain_leaders.loc[key, "shapley_share_of_explained"]),
        })
    report = f"""# Step 4 Report: Integrated Advanced Validation Conclusions

## What has been done

This synthesis combines three distinct questions: spatial nested CV tests geographic generalization; spatial-block bootstrap tests stability of the PLS latent construction; and domain commonality/Shapley analysis separates unique from shared domain importance.

## Integrated results

{md_table(pd.DataFrame(rows))}

## Interpretation

Municipal turnout remains the clearest result: it has the strongest spatial prediction, a stable primary construction, and is the only outcome whose leading Shapley domain is immigration/citizenship. Provincial turnout retains the same central construction but generalizes less strongly. Federal turnout has the weakest spatial prediction and shifts relatively toward age and urban form. Mean turnout falls between these cases.

Across outcomes, education/resources and immigration/citizenship explain most of the modelled variation, but much of that contribution is shared. The correct story is therefore not that one domain independently determines turnout. It is that overlapping class, education, household, citizenship, and racialized geographies form the main turnout structure, with election-level differences in how strongly that structure predicts participation.

Predictive performance, latent stability, and domain attribution should not be collapsed into one statistic. A model can have modest spatial prediction but a stable descriptive component. A domain can be highly important by Shapley allocation while contributing little uniquely because it overlaps with other domains.

## Further analysis

Map the stored outer-fold residuals and inspect the bootstrap interval tables before publication. If strict inference is required, add repeated alternative spatial partitions and report sensitivity to block definition. Causal language remains inappropriate for these cross-sectional ecological CT associations.

## Conclusion

The advanced workflow replaces a single bundled PLS reading with three layers of evidence: where prediction travels, which latent features survive geography, and how the seven prespecified domains divide unique and shared explanatory power.
"""
    (REPORT_ROOT / "04_integrated_conclusions_report.md").write_text(report, encoding="utf-8")


def write_readme():
    text = """# Advanced Meeting-Variable Validation

This folder contains four sequential analyses and reports:

1. Spatially blocked nested cross-validation.
2. Spatial-block bootstrap stability for PLS.
3. Domain commonality and Shapley relative importance.
4. Integrated conclusions.

The seven domains are prespecified from the research framework; no clustering or factor algorithm defines them. Rebuild from the repository root with:

```bash
/opt/anaconda3/bin/python3 analysis/toronto_election_turnout/modelling/dimension_reduction/meeting_PLS/run_advanced_validation.py
```
"""
    (OUT / "README.md").write_text(text, encoding="utf-8")


def main():
    for directory in [OUT, SPATIAL_ROOT, BOOT_ROOT, DOMAIN_ROOT, REPORT_ROOT]:
        directory.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {"domain": d, "domain_label": DOMAIN_LABELS[d], "variable": v, "variable_label": meeting.plain_name(v)}
        for d, variables in DOMAINS.items() for v in variables
    ]).to_csv(OUT / "prespecified_domain_registry.csv", index=False)
    df = prepare_data()
    spatial = run_spatial_nested_cv(df)
    loading_stability, _ = run_block_bootstrap(df)
    domain = run_domain_importance(df)
    write_integrated_report(spatial, loading_stability, domain)
    write_readme()
    artifacts = [{"relative_path": str(p.relative_to(OUT))} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "artifact_manifest.csv"]
    pd.DataFrame(artifacts).to_csv(OUT / "artifact_manifest.csv", index=False)


if __name__ == "__main__":
    main()
