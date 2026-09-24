"""Compare meeting-variable latent models for each election level with mean turnout."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[5]
SHARED_ROOT = REPO_ROOT / "analysis/toronto_election_turnout/modelling/dimension_reduction/scripts"
MEETING_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SHARED_ROOT))
sys.path.insert(0, str(MEETING_ROOT))

import run_dimension_reduction_workflow as wf  # noqa: E402
import run_meeting_pls as meeting  # noqa: E402


OUT = (
    REPO_ROOT
    / "data/toronto_election_turnout/modelling/processed/dimension_reduction/meeting_PLS"
    / "turnout_level_comparisons"
)
MODEL_ROOT = OUT / "models"
REPORT_ROOT = OUT / "reports"

OUTCOMES = {
    "mean": ("Mean turnout", "outcome_mean_participation_citizen_18plus"),
    "municipal": ("Municipal turnout", "outcome_municipal_participation_citizen_18plus"),
    "provincial": ("Provincial turnout", "outcome_provincial_participation_citizen_18plus"),
    "federal": ("Federal turnout", "outcome_federal_participation_citizen_18plus"),
}


def fmt(value: float | int | str, digits: int = 3) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return "" if not np.isfinite(float(value)) else f"{float(value):.{digits}f}"


def md_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    shown = frame.fillna("").copy()
    header = "| " + " | ".join(shown.columns) + " |"
    sep = "| " + " | ".join("---" for _ in shown.columns) + " |"
    rows = [
        "| " + " | ".join(str(row[col]).replace("|", "/") for col in shown.columns) + " |"
        for _, row in shown.iterrows()
    ]
    return "\n".join([header, sep, *rows])


def folds(n: int) -> list[np.ndarray]:
    rng = np.random.default_rng(wf.RANDOM_SEED)
    idx = np.arange(n)
    rng.shuffle(idx)
    return list(np.array_split(idx, wf.CV_FOLDS))


def model_frame(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    cols = meeting.MEETING_VARIABLES
    xdf = df[cols].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[target], errors="coerce")
    keep = y.notna() & xdf.notna().all(axis=1)
    return df.loc[keep].copy(), xdf.loc[keep].to_numpy(float), y.loc[keep].to_numpy(float)


def run_pls(df: pd.DataFrame, key: str, target: str) -> None:
    root = MODEL_ROOT / key / "pls"
    old_target = wf.TARGET
    old_max_components = wf.MAX_COMPONENTS
    try:
        wf.TARGET = target
        # The meeting models prioritize a compact interpretable construction.
        # Searching beyond five components produced high-order municipal and
        # provincial solutions that added little narrative value.
        wf.MAX_COMPONENTS = 5
        wf.pls_outputs(df, meeting.MEETING_VARIABLES, f"{key}_meeting_pls", root)
    finally:
        wf.TARGET = old_target
        wf.MAX_COMPONENTS = old_max_components


def run_supervised_pca(df: pd.DataFrame, key: str, target: str) -> None:
    """Run the repository's correlation-screened PCA regression on 14 variables."""
    root = MODEL_ROOT / key / "supervised_pca"
    root.mkdir(parents=True, exist_ok=True)
    _, x, y = model_frame(df, target)
    variables = meeting.MEETING_VARIABLES
    corrs = pd.Series([np.corrcoef(x[:, i], y)[0, 1] for i in range(x.shape[1])], index=variables)
    ranked = corrs.abs().sort_values(ascending=False)
    configs: list[tuple[str, list[str]]] = [("all_14", variables)]
    for threshold in [0.10, 0.20, 0.30]:
        selected = ranked[ranked >= threshold].index.tolist()
        if len(selected) >= 3:
            configs.append((f"corr_ge_{threshold:.2f}", selected))
    for n_vars in [6, 8, 10, 12]:
        configs.append((f"top_{n_vars}_corr", ranked.head(n_vars).index.tolist()))

    idx_map = {v: i for i, v in enumerate(variables)}
    rows: list[dict] = []
    split = folds(len(y))
    all_idx = np.arange(len(y))
    for screen, selected in configs:
        xs = x[:, [idx_map[v] for v in selected]]
        for n_components in range(1, min(8, len(selected)) + 1):
            pred = np.zeros(len(y))
            for test in split:
                train = np.setdiff1d(all_idx, test)
                train_scores, test_scores, _ = wf.pca_scores(xs[train], xs[test], n_components)
                pred[test] = wf.ols_predict(train_scores, y[train], test_scores)
            cv = wf.metrics(y, pred, n_components)
            train_scores, _, _ = wf.pca_scores(xs, xs, n_components)
            train_pred = wf.ols_predict(train_scores, y, train_scores)
            train_metric = wf.metrics(y, train_pred, n_components)
            rows.append({
                "screen": screen,
                "screened_predictor_count": len(selected),
                "n_components": n_components,
                "train_r2": train_metric["r2"],
                "cv_r2": cv["r2"],
                "cv_rmse": cv["rmse"],
                "variables": "; ".join(selected),
            })
    grid = pd.DataFrame(rows).sort_values(["cv_rmse", "screened_predictor_count", "n_components"])
    grid.to_csv(root / f"{key}_supervised_pca_grid.csv", index=False)
    best = grid.iloc[0]
    selected = best["variables"].split("; ")
    xs = x[:, [idx_map[v] for v in selected]]
    _, _, components = wf.pca_scores(xs, xs, int(best["n_components"]))
    loadings = pd.DataFrame(components, index=selected, columns=[f"component_{i+1}" for i in range(components.shape[1])])
    loadings.reset_index(names="variable").to_csv(root / f"{key}_supervised_pca_loadings.csv", index=False)
    pd.DataFrame([{"model": "supervised_pca", "n": len(y), **best.to_dict()}]).to_csv(
        root / f"{key}_supervised_pca_summary.csv", index=False
    )


def elastic_net_fold_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, alpha: float, ratio: float) -> tuple[np.ndarray, int]:
    x_mean, x_std = x_train.mean(axis=0), x_train.std(axis=0)
    x_std[x_std == 0] = 1
    y_mean, y_std = y_train.mean(), y_train.std()
    if y_std == 0:
        y_std = 1
    beta = wf.elastic_net_fit((x_train - x_mean) / x_std, (y_train - y_mean) / y_std, alpha, ratio)
    prediction = (((x_test - x_mean) / x_std) @ beta) * y_std + y_mean
    return prediction, int(np.sum(np.abs(beta) > 1e-6))


def run_elastic_net(df: pd.DataFrame, key: str, target: str) -> None:
    root = MODEL_ROOT / key / "elastic_net"
    root.mkdir(parents=True, exist_ok=True)
    _, x, y = model_frame(df, target)
    split = folds(len(y))
    all_idx = np.arange(len(y))
    rows = []
    for alpha in [0.001, 0.003, 0.01, 0.03, 0.1, 0.2]:
        for ratio in [0.0, 0.2, 0.5, 0.8, 1.0]:
            pred = np.zeros(len(y))
            selected = []
            for test in split:
                train = np.setdiff1d(all_idx, test)
                pred[test], count = elastic_net_fold_predict(x[train], y[train], x[test], alpha, ratio)
                selected.append(count)
            metric = wf.metrics(y, pred, int(round(np.mean(selected))))
            rows.append({
                "alpha": alpha,
                "l1_ratio": ratio,
                "mean_selected_variables": float(np.mean(selected)),
                "cv_r2": metric["r2"],
                "cv_rmse": metric["rmse"],
            })
    grid = pd.DataFrame(rows).sort_values(["cv_rmse", "mean_selected_variables"])
    grid.to_csv(root / f"{key}_elastic_net_grid.csv", index=False)
    best = grid.iloc[0]
    x_mean, x_std = x.mean(axis=0), x.std(axis=0)
    x_std[x_std == 0] = 1
    y_mean, y_std = y.mean(), y.std()
    beta = wf.elastic_net_fit((x - x_mean) / x_std, (y - y_mean) / y_std, float(best["alpha"]), float(best["l1_ratio"]))
    coefficients = beta * y_std / x_std
    importance = pd.DataFrame({
        "variable": meeting.MEETING_VARIABLES,
        "scaled_coefficient": beta,
        "coefficient": coefficients,
        "selected": np.abs(beta) > 1e-6,
    }).sort_values("scaled_coefficient", key=lambda s: s.abs(), ascending=False)
    importance.to_csv(root / f"{key}_elastic_net_coefficients.csv", index=False)
    pd.DataFrame([{"model": "elastic_net", "n": len(y), **best.to_dict()}]).to_csv(
        root / f"{key}_elastic_net_summary.csv", index=False
    )


def read_pls(key: str, suffix: str) -> pd.DataFrame:
    return pd.read_csv(MODEL_ROOT / key / "pls" / f"{key}_meeting_pls_{suffix}.csv")


def align_components(level: str) -> pd.DataFrame:
    mean = read_pls("mean", "component_loadings").set_index("variable")
    other = read_pls(level, "component_loadings").set_index("variable")
    rows = []
    for level_component in other.columns:
        best = None
        for mean_component in mean.columns:
            a = other[level_component].to_numpy(float)
            b = mean[mean_component].to_numpy(float)
            cosine = float((a @ b) / (np.linalg.norm(a) * np.linalg.norm(b)))
            candidate = (abs(cosine), cosine, mean_component)
            if best is None or candidate > best:
                best = candidate
        assert best is not None
        rows.append({
            "level_component": level_component,
            "matched_mean_component": best[2],
            "loading_cosine": best[1],
            "absolute_loading_cosine": best[0],
            "sign_flipped_for_comparison": best[1] < 0,
        })
    result = pd.DataFrame(rows)
    result.to_csv(OUT / f"{level}_component_alignment.csv", index=False)
    return result


def model_summary_table(level: str) -> pd.DataFrame:
    rows = []
    for key in ["mean", level]:
        label = OUTCOMES[key][0]
        pls = read_pls(key, "summary").iloc[0]
        pca = pd.read_csv(MODEL_ROOT / key / "supervised_pca" / f"{key}_supervised_pca_summary.csv").iloc[0]
        enet = pd.read_csv(MODEL_ROOT / key / "elastic_net" / f"{key}_elastic_net_summary.csv").iloc[0]
        rows.extend([
            {"Outcome": label, "Method": "PLS", "Components/selected": int(pls["selected_components"]), "CV R2": fmt(pls["cv_r2"]), "CV RMSE": fmt(pls["cv_rmse"])},
            {"Outcome": label, "Method": "Supervised PCA", "Components/selected": int(pca["n_components"]), "CV R2": fmt(pca["cv_r2"]), "CV RMSE": fmt(pca["cv_rmse"])},
            {"Outcome": label, "Method": "Elastic net", "Components/selected": fmt(enet["mean_selected_variables"], 1), "CV R2": fmt(enet["cv_r2"]), "CV RMSE": fmt(enet["cv_rmse"])},
        ])
    return pd.DataFrame(rows)


def importance_comparison(level: str) -> pd.DataFrame:
    mean = read_pls("mean", "variable_importance")[["variable", "vip", "pls_coefficient", "turnout_corr"]]
    other = read_pls(level, "variable_importance")[["variable", "vip", "pls_coefficient", "turnout_corr"]]
    merged = mean.merge(other, on="variable", suffixes=("_mean", f"_{level}"))
    merged["plain"] = merged["variable"].map(meeting.plain_name)
    merged["vip_change"] = merged[f"vip_{level}"] - merged["vip_mean"]
    merged["coefficient_direction_same"] = np.sign(merged["pls_coefficient_mean"]) == np.sign(merged[f"pls_coefficient_{level}"])
    merged = merged.sort_values(f"vip_{level}", ascending=False)
    shown = merged[["plain", "vip_mean", f"vip_{level}", "vip_change", "coefficient_direction_same"]].copy()
    shown.columns = ["Variable", "Mean VIP", f"{OUTCOMES[level][0]} VIP", "VIP change", "Same coefficient direction"]
    for col in ["Mean VIP", f"{OUTCOMES[level][0]} VIP", "VIP change"]:
        shown[col] = shown[col].map(fmt)
    return shown


def component_comparison(level: str, alignment: pd.DataFrame) -> str:
    mean = read_pls("mean", "component_loadings").set_index("variable")
    other = read_pls(level, "component_loadings").set_index("variable")
    sections = []
    for _, match in alignment.iterrows():
        lc, mc = match["level_component"], match["matched_mean_component"]
        sign = -1 if bool(match["sign_flipped_for_comparison"]) else 1
        table = pd.DataFrame({
            "Variable": [meeting.plain_name(v) for v in other.index],
            "Mean loading": mean[mc].to_numpy(float),
            "Level loading (aligned)": sign * other[lc].to_numpy(float),
        })
        table["Absolute loading difference"] = (table["Level loading (aligned)"] - table["Mean loading"]).abs()
        table = table.sort_values("Absolute loading difference", ascending=False).head(8)
        for col in ["Mean loading", "Level loading (aligned)", "Absolute loading difference"]:
            table[col] = table[col].map(fmt)
        aligned_level = sign * other[lc]
        level_high = [meeting.plain_name(v) for v in aligned_level.sort_values(ascending=False).head(4).index]
        level_low = [meeting.plain_name(v) for v in aligned_level.sort_values().head(4).index]
        mean_high = [meeting.plain_name(v) for v in mean[mc].sort_values(ascending=False).head(4).index]
        mean_low = [meeting.plain_name(v) for v in mean[mc].sort_values().head(4).index]
        level_corr = projected_component_correlation(level, lc, sign)
        mean_corr = projected_component_correlation("mean", mc, 1)
        sections.append(
            f"### {lc.replace('_', ' ').title()} versus {mc.replace('_', ' ').title()}\n\n"
            f"Loading cosine after accounting for arbitrary component sign: `{fmt(match['absolute_loading_cosine'])}`. "
            "Higher values indicate that the component constructs nearly the same predictor bundle. "
            f"The aligned level component has projected outcome correlation `{fmt(level_corr)}`; the matched mean component has projected outcome correlation `{fmt(mean_corr)}`.\n\n"
            f"For the level-specific component, the high side is anchored by {', '.join(level_high)}, while the low side is anchored by {', '.join(level_low)}. "
            f"For mean turnout, the matched high side is anchored by {', '.join(mean_high)}, while its low side is anchored by {', '.join(mean_low)}. "
            "The table emphasizes the variables whose loadings changed most.\n\n"
            f"{md_table(table)}"
        )
    return "\n\n".join(sections)


def projected_component_correlation(key: str, component: str, sign: int) -> float:
    """Correlation of a loading-projected standardized X score with its outcome."""
    df = pd.read_csv(wf.INPUT)
    target = OUTCOMES[key][1]
    _, x, y = model_frame(df, target)
    z = (x - x.mean(axis=0)) / x.std(axis=0)
    loadings = read_pls(key, "component_loadings").set_index("variable")
    weights = sign * loadings.loc[meeting.MEETING_VARIABLES, component].to_numpy(float)
    return float(np.corrcoef(z @ weights, y)[0, 1])


def write_level_report(level: str) -> None:
    label = OUTCOMES[level][0]
    alignment = align_components(level)
    fit = model_summary_table(level)
    importance = importance_comparison(level)
    level_summary = read_pls(level, "summary").iloc[0]
    mean_summary = read_pls("mean", "summary").iloc[0]
    top_level = importance.iloc[0:5]["Variable"].tolist()
    changed = importance.sort_values("VIP change", key=lambda s: pd.to_numeric(s, errors="coerce").abs(), ascending=False).head(5)["Variable"].tolist()
    report = f"""# {label} Meeting-Variable PLS Compared With Mean Turnout

This report fits the same 14 meeting-specified predictors to `{OUTCOMES[level][1]}` and compares that model with the previously specified mean-turnout construction. It does not model an election-level difference outcome; the comparison is between two separately supervised latent models.

## Model fit and robustness

{md_table(fit)}

The {label.lower()} PLS selected {int(level_summary['selected_components'])} component(s), with CV R2 `{fmt(level_summary['cv_r2'])}` and CV RMSE `{fmt(level_summary['cv_rmse'])}`. The mean-turnout model selected {int(mean_summary['selected_components'])} component(s), with CV R2 `{fmt(mean_summary['cv_r2'])}`. Supervised PCA tests whether a screened predictor-correlation structure predicts the outcome without PLS supervision; elastic net tests whether coefficient directions and predictive signal survive shrinkage and variable selection.

## Variable interpretation

The five highest-VIP predictors for {label.lower()} are {', '.join(top_level)}. The largest VIP shifts relative to mean turnout involve {', '.join(changed)}.

{md_table(importance)}

VIP values describe importance within each fitted model; they are not causal effects. “Same coefficient direction” checks whether the overall PLS regression direction agrees between the level-specific and mean models.

## Component construction compared with mean turnout

PLS component signs are arbitrary, so level components are sign-aligned to the closest mean-turnout loading vector before comparison.

{component_comparison(level, alignment)}

## Interpretation

Shared high VIP values and high loading cosine indicate a common citywide turnout geography. Differences in VIP and aligned loadings show which parts of that bundle are more characteristic of {label.lower()} than of the three-election mean. The PCA and elastic-net rows should be treated as robustness evidence, not as replacements for the PLS component narrative.

## Cautions

- These are ecological CT models using Census citizen-adult denominators, not individual voting models or official registered-elector turnout.
- Mean turnout contains the level-specific outcome being compared, so the two outcomes are mechanically related; this report describes construction differences and does not test an independent contrast.
- The repository's fixed shuffled 10-fold validation is retained for comparability and is not spatially blocked.
- Correlation screening for supervised PCA is performed on the analysis sample, so its CV score is exploratory rather than a fully nested estimate.
"""
    (REPORT_ROOT / f"{level}_vs_mean_meeting_latent_report.md").write_text(report, encoding="utf-8")


def write_combined_report() -> None:
    summaries = {
        key: read_pls(key, "summary").iloc[0]
        for key in ["mean", "municipal", "provincial", "federal"]
    }
    alignments = {
        key: pd.read_csv(OUT / f"{key}_component_alignment.csv")
        for key in ["municipal", "provincial", "federal"]
    }
    report = f"""# Meeting-Variable Turnout-Level Comparison: Executive Summary

This report gives a quick narrative comparison of separately supervised municipal, provincial, and federal meeting-variable PLS models with mean turnout. Detailed loadings, VIP tables, component matching, and robustness grids remain in the three level-specific reports. Mean turnout includes all three election outcomes, so similarities are partly expected and the comparisons are descriptive rather than independent difference tests.

## Municipal turnout

### Interpretation

Municipal turnout is the most strongly structured of the three levels by the meeting variables. Its three-component PLS reaches CV R2 `{fmt(summaries['municipal']['cv_r2'])}`, compared with `{fmt(summaries['mean']['cv_r2'])}` for mean turnout. The primary municipal construction contrasts higher education and citizen attachment with visible-minority, immigrant, larger-household, and lower-income geography. Visible-minority share, immigrant share, bachelor-level education, citizen-adult share, and household size carry the highest VIP values.

### Similarity with mean turnout

The first municipal and mean components are strongly aligned: their loading cosine is `{fmt(alignments['municipal'].iloc[0]['absolute_loading_cosine'])}`. Both express essentially the same central social-geographic turnout gradient, and both are reproduced closely by supervised PCA and elastic net. This indicates that the main municipal story is not an artifact of one estimator or of averaging election levels.

### Difference from mean turnout

Municipal turnout gives more importance than the mean model to low-income share, citizen-adult share, renter share, and the young-adult share. Average household size, the age-65-plus share, no-car households, and five-year residential stability contribute less relative importance. The municipal model is also markedly more predictive, with robustness CV R2 values around `0.626–0.639`, suggesting a sharper social gradient than the average outcome.

### Discussion

The municipal pattern is therefore best read as a more socially selective version of the shared turnout geography. Citizenship eligibility, income, tenure, and younger-adult context sharpen the separation between high- and low-participation CTs. This supports a story about unequal municipal incorporation, while remaining an ecological association rather than evidence about individual voters.

## Provincial turnout

### Interpretation

Provincial turnout retains the same main demographic axis but is less predictable: its three-component PLS has CV R2 `{fmt(summaries['provincial']['cv_r2'])}`. Visible-minority share, immigrant share, household size, bachelor-level education, and citizen-adult share remain the leading variables. Its secondary construction gives more space to urban form, stability, density, and transportation context.

### Similarity with mean turnout

The provincial primary component is the closest match to the mean model of any election level, with loading cosine `{fmt(alignments['provincial'].iloc[0]['absolute_loading_cosine'])}`. The high- and low-side variable bundles are nearly the same, showing that provincial turnout closely represents the central construction captured by the three-election average.

### Difference from mean turnout

Apartment share, population density, no-car household share, and five-year residential stability become more important provincially. Bachelor-level education, both age shares, and low-income share become somewhat less important. PLS, supervised PCA, and elastic net all produce CV R2 near `0.36–0.38`, so the weaker fit is consistent across estimators.

### Discussion

Provincial turnout looks like the clearest middle case: it shares the mean model's central social divide almost exactly, but supplements it with an urban-form and mobility layer. The similarity of the component construction combined with lower predictive power suggests the same geography is present, but it organizes provincial participation less tightly than municipal participation.

## Federal turnout

### Interpretation

Federal turnout is the least predictable from the meeting variables. Its three-component PLS has CV R2 `{fmt(summaries['federal']['cv_r2'])}`. Household size and bachelor-level education lead the VIP ranking, followed by visible-minority and immigrant shares; condo, apartment, residential-stability, and density variables are much more prominent than in the mean model.

### Similarity with mean turnout

The federal primary component still has a strong loading cosine of `{fmt(alignments['federal'].iloc[0]['absolute_loading_cosine'])}` with the mean primary component. Education/resources versus immigrant/racialized household geography therefore remains recognizable. PCA and elastic net again return almost the same predictive performance as PLS, supporting the existence of a stable but weaker common signal.

### Difference from mean turnout

Federal turnout shifts strongly toward housing form: condo share, apartment share, five-year residential stability, and density show the largest positive VIP changes. Immigrant share, citizen-adult share, visible-minority share, and low-income share become less important than in mean turnout. Its robustness CV R2 values remain only about `0.317–0.327`.

### Discussion

The federal result suggests broader mobilization across social groups, leaving less of the sharply selective pattern seen municipally. Where federal turnout still varies, stable residential and built-form differences become relatively more informative. This does not mean immigration or racialized geography disappears; rather, those variables dominate less once federal participation is considered by itself.

## Overall similarities and differences

All three election levels share one central construction: education and resource attachment on one side, and immigrant/racialized, larger-household geography on the other. This common axis is strongest for municipal turnout, almost identical in construction for provincial turnout, and still visible but weaker for federal turnout. Agreement among PLS, supervised PCA, and elastic net supports treating it as a recurring feature of the data rather than a PLS-specific artifact.

The main difference is emphasis. Municipal turnout accentuates citizenship, income, tenure, and young-adult inequality; provincial turnout most closely follows the mean while adding urban form and transportation; federal turnout places greater relative weight on housing form, density, and residential stability. In short, the same underlying Toronto social geography is present at every level, but it is most consequential municipally and least determinative federally.

These comparisons summarize associations among CT characteristics. They do not identify individual behavior, causal mechanisms, or statistically independent differences from the mean outcome.
"""
    (REPORT_ROOT / "all_levels_vs_mean_meeting_latent_report.md").write_text(report, encoding="utf-8")


def write_methodology_note() -> None:
    note = """# Next-Step Methodology: Spatial Nested Validation and Domain Importance

This note explains two complementary extensions for the 585 Toronto Census Tracts and the 14 meeting variables. Spatially blocked nested cross-validation asks whether the models generalize to held-out parts of Toronto. Domain-level commonality and relative-importance analysis asks how much of the explained turnout variation is unique to each conceptual domain and how much is shared among correlated domains.

## 1. Spatially blocked, nested cross-validation

### What problem it solves

The current fixed shuffled folds treat CTs as exchangeable observations. Nearby CTs often share housing markets, built form, settlement histories, services, and turnout patterns. Randomly putting neighbouring CTs in both training and validation folds can therefore leak local spatial information and make predictive performance look better than it would be in a genuinely unseen area. The same data are also used to choose component counts and assess the chosen model, which adds tuning optimism.

Spatial blocking separates geographically proximate CTs into the same fold. Nesting then separates two decisions: inner spatial folds tune the model, while outer spatial folds estimate performance on unseen geographic regions. This addresses spatial leakage and tuning bias. It does not make the model causal or eliminate ecological inference.

### Proposed implementation for this project

1. Join the 585 modelling rows to the existing CT geometry by `ct_id` and project centroids to EPSG:3347.
2. Construct five outer spatial folds. A practical first version is spatially contiguous clustering of CT centroids, balanced so each fold has roughly similar CT counts and outcome coverage. A sensitivity version should repeat the analysis with several block widths or clustering seeds.
3. For each outer fold, hold out the entire geographic block. Use only the remaining four blocks for model development.
4. Inside that training set, create four spatial inner folds. Perform imputation, scaling, supervised-PCA screening, PLS component selection, and elastic-net tuning only within the inner-training data.
5. Select PLS components from 1–5; supervised-PCA threshold and components jointly; and elastic-net `alpha` plus `l1_ratio`, including ridge (`l1_ratio = 0`).
6. Refit the selected pipeline on the full outer-training set and predict the untouched outer block.
7. Combine the five outer-fold predictions and report spatial CV R2, RMSE, and MAE for mean, municipal, provincial, and federal turnout.
8. Map outer-fold residuals and calculate residual Moran's I. Remaining spatial autocorrelation would indicate geographic structure not captured by the 14 variables.
9. Repeat the outer blocking several times and report the distribution of performance, rather than relying on one convenient partition.

### What to compare

- Current shuffled-CV performance versus outer spatial-CV performance.
- Whether the selected PLS component count changes across outer folds.
- Loading, VIP, and coefficient stability after aligning component signs and order.
- Whether PLS, supervised PCA, ridge, and elastic net rank outcomes similarly under spatial validation.
- Which neighbourhood blocks are systematically over- or under-predicted.

A material drop from shuffled to spatial CV would not invalidate the substantive story. It would show that some apparent predictive strength depends on local spatial resemblance. Stable loadings but weaker spatial prediction would support a descriptive citywide latent interpretation while cautioning against geographic extrapolation.

## 2. Domain-level commonality and relative importance

### What problem it solves

PLS provides a useful bundled latent story but does not tell us how much turnout variation belongs uniquely to education, immigration, housing, or another correlated domain. Loadings and VIP scores can be shared across correlated variables and should not be read as unique effects.

Commonality analysis decomposes model R2 into unique and shared pieces. Relative-importance methods, such as dominance analysis or Shapley/LMG allocation, distribute shared explained variance across predictors or domains. These methods clarify attribution of association; they do not establish causality.

### Recommended seven domains

1. Age structure: age 18–34 and age 65+.
2. Education/income/household: household size, bachelor-level education, and low income.
3. Tenure: renter share.
4. Residential stability: same-address-five-years share.
5. Urban form: apartment share, condo share, and population density.
6. Immigration/citizenship: citizen-adult, immigrant, and visible-minority shares.
7. Transportation: TTS no-car household share.

Because tenure, stability, and transportation each contain one observed variable, these should be called domains or blocks rather than latent factors.

### Proposed implementation

1. Standardize the 14 variables and keep the seven domain definitions fixed before looking at outcome-specific results.
2. Fit all `2^7 = 128` possible domain-subset models separately for mean, municipal, provincial, and federal turnout. Domain-level subsets are more interpretable than presenting all `2^14 = 16,384` variable subsets.
3. For each domain, calculate its unique contribution: full-model R2 minus the R2 of the model omitting that domain.
4. Calculate shared commonality components for combinations of domains. Collapse the full decomposition into readable quantities: unique contribution, total shared contribution, and total involvement for each domain.
5. Calculate Shapley/LMG or general-dominance importance by averaging each domain's incremental R2 over all possible entry orders.
6. Bootstrap by spatial blocks, not individual CTs. Report median contribution, 95% interval, and the frequency with which each domain ranks first, second, or third.
7. Repeat using ridge predictions as a sensitivity analysis when subset OLS is unstable.

### How it would enrich the story

The analysis could distinguish statements such as:

- Immigration/citizenship has a substantial unique association with municipal turnout.
- Education/resources and immigration/citizenship explain mostly the same geographic variation.
- Urban form adds relatively little uniquely for municipal turnout but more for federal turnout.
- Transportation contributes primarily through shared variance with density and tenure rather than independently.

That is more precise than saying variables form one bundle. It reveals whether a domain contributes new information or mainly tags the same Toronto geography as another domain.

## Recommended sequence

First implement spatially blocked nested CV, because it changes how confidently every model's performance can be interpreted. Next add spatial-block bootstrap stability for PLS loadings and VIPs. Then run domain-level commonality and Shapley/LMG importance using the same outer spatial partitions. The final narrative can combine: PLS for the shape of the latent geography, bootstrap stability for confidence in that shape, and domain attribution for unique-versus-shared explanatory contributions.

## References

- [Roberts et al., cross-validation strategies for spatially structured data](https://www.wsl.ch/lud/biodiversity_events/papers/Roberts_et_al-2017-Ecography.pdf)
- [Spatial cross-validation and predictive error](https://www.nature.com/articles/s41467-020-18321-y)
- [Bair et al., supervised principal components](https://web.stanford.edu/~hastie/Papers/spca_JASA.pdf)
- [Commonality analysis for correlated predictors](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.12166)
"""
    (REPORT_ROOT / "methodology_spatial_cv_and_domain_importance.md").write_text(note, encoding="utf-8")


def write_readme_and_manifest() -> None:
    readme = """# Meeting-Variable Turnout-Level Comparisons

This folder contains separately supervised meeting-variable models for mean,
municipal, provincial, and federal CT turnout. Each outcome has PLS,
correlation-screened supervised PCA, and elastic-net robustness artifacts.

The four interpretation reports are under `reports/`. The three level-specific
reports compare one election level with mean turnout; the consolidated report
is a short audience-facing synthesis rather than a stack of the detailed
reports. A separate methodology note specifies spatially blocked nested CV and
domain-importance next steps. No cross-level difference outcome is fitted.

Rebuild from the repository root with:

```bash
/opt/anaconda3/bin/python3 analysis/toronto_election_turnout/modelling/dimension_reduction/meeting_PLS/run_turnout_level_comparisons.py
```

PLS component selection searches one through five components using the
repository's fixed shuffled 10-fold CV convention. Component signs are aligned
before level-versus-mean loading comparisons. Supervised PCA and elastic net
are exploratory robustness checks; see the reports for validation caveats.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    artifacts = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "artifact_manifest.csv":
            artifacts.append({"artifact": path.stem, "relative_path": str(path.relative_to(OUT))})
    pd.DataFrame(artifacts).to_csv(OUT / "artifact_manifest.csv", index=False)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(wf.INPUT)
    missing = [v for v in meeting.MEETING_VARIABLES if v not in df.columns]
    missing += [target for _, target in OUTCOMES.values() if target not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    pd.DataFrame({"variable": meeting.MEETING_VARIABLES}).to_csv(OUT / "meeting_predictors.csv", index=False)
    for key, (_, target) in OUTCOMES.items():
        run_pls(df, key, target)
        run_supervised_pca(df, key, target)
        run_elastic_net(df, key, target)
    for level in ["municipal", "provincial", "federal"]:
        write_level_report(level)
    write_combined_report()
    write_methodology_note()
    write_readme_and_manifest()


if __name__ == "__main__":
    main()
