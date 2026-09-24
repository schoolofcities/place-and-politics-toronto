"""Run Order 4 variable-by-variable spatial-error robustness screen."""

from __future__ import annotations

from collections import defaultdict
from html import escape
from math import isfinite, sqrt
from pathlib import Path

import numpy as np

from run_full_all_variables_spatial_models import INPUT, full_predictors
from run_spatial_block_models import (
    DEPENDENT_VARIABLES,
    REPORT_OUTPUT,
    SpatialErrorFit,
    as_number,
    fmt,
    html_table,
    load_queen_weights,
    normal_p,
    ols,
    read_csv,
    significance,
    write_csv,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "modelling" / "processed" / "spatial_models"
SUMMARY_OUTPUT = OUTPUT_ROOT / "variable_robustness_spatial_screen_summary.csv"
TOP_OUTPUT = OUTPUT_ROOT / "variable_robustness_spatial_screen_top_terms.csv"


def variable_block(variable: str) -> str:
    if variable.startswith("block1_"):
        return "Block 1"
    if variable.startswith("block2_"):
        return "Block 2"
    if variable.startswith("block3_"):
        return "Block 3"
    if variable.startswith("block4_"):
        return "Block 4"
    if variable.startswith("block5_"):
        return "Block 5"
    return "Other"


def build_design(rows: list[dict[str, str]], dependent: str, variable: str):
    ct_ids = []
    y_vals = []
    x_vals = []
    for row in rows:
        y = as_number(row.get(dependent))
        x = as_number(row.get(variable))
        if y is None or x is None:
            continue
        ct_ids.append(row["ct_id"])
        y_vals.append(y)
        x_vals.append(x)
    y_arr = np.array(y_vals, dtype=float)
    x_raw = np.array(x_vals, dtype=float)
    x_arr = np.column_stack([np.ones(len(y_arr)), x_raw])
    return ct_ids, y_arr, x_raw, x_arr


def subset_weights(w_all: np.ndarray, index_all: dict[str, int], ct_ids: list[str]) -> np.ndarray:
    idx = [index_all[ct_id] for ct_id in ct_ids]
    w = w_all[np.ix_(idx, idx)].copy()
    row_sums = w.sum(axis=1)
    if np.any(row_sums == 0):
        # Very rare after dropping rows; keep the model runnable by using the nearest retained index in original order.
        zero_rows = np.where(row_sums == 0)[0]
        for i in zero_rows:
            j = i - 1 if i > 0 else min(i + 1, len(ct_ids) - 1)
            w[i, j] = 1.0
            w[j, i] = 1.0
        row_sums = w.sum(axis=1)
    return w / row_sums[:, None]


def spatial_error_loglik_fast(lam: float, y: np.ndarray, x: np.ndarray, w: np.ndarray, eigvals: np.ndarray):
    n = len(y)
    log_terms = np.log(1 - lam * eigvals)
    logdet = float(np.real(log_terms.sum()))
    if not isfinite(logdet):
        return -np.inf, np.array([]), np.array([]), np.inf
    a = np.eye(n) - lam * w
    ys = a @ y
    xs = a @ x
    fit = ols(ys, xs)
    sse = fit.sse
    if sse <= 0:
        return -np.inf, fit.beta, fit.residuals, np.inf
    ll = float(logdet - 0.5 * n * (np.log(2 * np.pi) + np.log(sse / n) + 1))
    return ll, fit.beta, fit.residuals, sse / n


def fit_spatial_error_fast(y: np.ndarray, x: np.ndarray, w: np.ndarray, eigvals: np.ndarray) -> SpatialErrorFit:
    n, cols = x.shape
    grid = np.linspace(-0.95, 0.95, 191)
    vals = [(spatial_error_loglik_fast(float(lam), y, x, w, eigvals)[0], float(lam)) for lam in grid]
    _, best = max(vals, key=lambda item: item[0])
    lo = max(-0.98, best - 0.03)
    hi = min(0.98, best + 0.03)
    gr = (sqrt(5) - 1) / 2
    c = hi - gr * (hi - lo)
    d = lo + gr * (hi - lo)
    for _ in range(60):
        fc = spatial_error_loglik_fast(c, y, x, w, eigvals)[0]
        fd = spatial_error_loglik_fast(d, y, x, w, eigvals)[0]
        if fc < fd:
            lo = c
            c = d
            d = lo + gr * (hi - lo)
        else:
            hi = d
            d = c
            c = hi - gr * (hi - lo)
    lam = (lo + hi) / 2
    loglik, beta, filtered_residuals, sigma2 = spatial_error_loglik_fast(lam, y, x, w, eigvals)
    residuals = y - x @ beta

    a = np.eye(n) - lam * w
    xs = a @ x
    xtx_inv = np.linalg.pinv(xs.T @ xs)
    se = np.sqrt(np.maximum(np.diag(xtx_inv) * sigma2, 0))
    t = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se != 0)
    p = np.array([normal_p(float(v)) if isfinite(float(v)) else np.nan for v in t])

    h = 1e-4
    ll0 = loglik
    llp = spatial_error_loglik_fast(min(0.98, lam + h), y, x, w, eigvals)[0]
    llm = spatial_error_loglik_fast(max(-0.98, lam - h), y, x, w, eigvals)[0]
    second = (llp - 2 * ll0 + llm) / (h * h)
    lambda_se = sqrt(-1 / second) if second < 0 else None
    lambda_z = lam / lambda_se if lambda_se not in {None, 0} else None
    lambda_p = normal_p(lambda_z)
    aic = float(2 * (cols + 1) - 2 * loglik)
    return SpatialErrorFit(lam, lambda_se, lambda_z, lambda_p, beta, se, t, p, residuals, filtered_residuals, sigma2, aic, loglik, True)


def run_screen(rows: list[dict[str, str]], predictors: list[str]) -> list[dict[str, object]]:
    ct_ids_all = [row["ct_id"] for row in rows]
    w_all = load_queen_weights(ct_ids_all)
    index_all = {ct_id: idx for idx, ct_id in enumerate(ct_ids_all)}
    results = []
    weights_cache: dict[tuple[str, ...], tuple[np.ndarray, np.ndarray]] = {}

    for outcome_label, dependent in DEPENDENT_VARIABLES.items():
        for variable in predictors:
            ct_ids, y, x_raw, x = build_design(rows, dependent, variable)
            if len(y) < 50 or float(np.std(x_raw)) == 0:
                continue
            cache_key = tuple(ct_ids)
            if cache_key not in weights_cache:
                w = subset_weights(w_all, index_all, ct_ids)
                weights_cache[cache_key] = (w, np.linalg.eigvals(w))
            w, eigvals = weights_cache[cache_key]
            ols_fit = ols(y, x)
            sem_fit = fit_spatial_error_fast(y, x, w, eigvals)
            coef = float(sem_fit.beta[1])
            p = float(sem_fit.p[1])
            standardized = coef * float(np.std(x_raw, ddof=1)) / float(np.std(y, ddof=1))
            results.append(
                {
                    "outcome": outcome_label,
                    "dependent_variable": dependent,
                    "block": variable_block(variable),
                    "variable": variable,
                    "n": len(y),
                    "ols_adjusted_r2": ols_fit.adjusted_r2,
                    "ols_aic": ols_fit.aic,
                    "spatial_lambda": sem_fit.lam,
                    "spatial_lambda_p": sem_fit.lambda_p,
                    "spatial_aic": sem_fit.aic,
                    "delta_aic_spatial_minus_ols": sem_fit.aic - ols_fit.aic,
                    "coefficient": coef,
                    "std_error": float(sem_fit.se[1]),
                    "z_value": float(sem_fit.t[1]),
                    "p_value": p,
                    "significance": significance(p),
                    "standardized_coefficient": standardized,
                    "direction": "positive" if coef > 0 else "negative",
                    "abs_standardized_coefficient": abs(standardized),
                }
            )
    return results


def top_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    by_outcome: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in results:
        if float(row["p_value"]) < 0.10:
            by_outcome[str(row["outcome"])].append(row)
    for outcome, outcome_rows in by_outcome.items():
        ranked = sorted(outcome_rows, key=lambda r: float(r["abs_standardized_coefficient"]), reverse=True)
        rows.extend(ranked[:20])
    stable_counts = defaultdict(lambda: {"count": 0, "positive": 0, "negative": 0, "max_abs_standardized": 0.0})
    for row in results:
        if float(row["p_value"]) < 0.05:
            item = stable_counts[str(row["variable"])]
            item["count"] += 1
            item[str(row["direction"])] += 1
            item["max_abs_standardized"] = max(item["max_abs_standardized"], float(row["abs_standardized_coefficient"]))
    for variable, stats in stable_counts.items():
        rows.append(
            {
                "outcome": "cross_outcome_count",
                "dependent_variable": "",
                "block": variable_block(variable),
                "variable": variable,
                "n": "",
                "ols_adjusted_r2": "",
                "ols_aic": "",
                "spatial_lambda": "",
                "spatial_lambda_p": "",
                "spatial_aic": "",
                "delta_aic_spatial_minus_ols": "",
                "coefficient": "",
                "std_error": "",
                "z_value": "",
                "p_value": "",
                "significance": "",
                "standardized_coefficient": "",
                "direction": f"{stats['positive']} positive / {stats['negative']} negative",
                "abs_standardized_coefficient": stats["max_abs_standardized"],
                "significant_outcome_count_p05": stats["count"],
            }
        )
    return rows


def strongest_by_outcome_table(results: list[dict[str, object]]) -> str:
    rows = []
    for outcome in DEPENDENT_VARIABLES:
        sig = [row for row in results if row["outcome"] == outcome and float(row["p_value"]) < 0.05]
        ranked = sorted(sig, key=lambda r: float(r["abs_standardized_coefficient"]), reverse=True)[:12]
        for row in ranked:
            rows.append(
                [
                    row["outcome"],
                    row["block"],
                    row["variable"],
                    row["direction"],
                    row["standardized_coefficient"],
                    row["coefficient"],
                    row["p_value"],
                    row["spatial_lambda"],
                ]
            )
    return html_table(["Outcome", "Block", "Variable", "Direction", "Std coef", "SEM coef", "p", "Lambda"], rows, "coef")


def stable_variables_table(results: list[dict[str, object]]) -> str:
    counts = defaultdict(lambda: {"positive": 0, "negative": 0, "max_abs": 0.0, "block": ""})
    for row in results:
        if float(row["p_value"]) < 0.05:
            item = counts[str(row["variable"])]
            item["block"] = row["block"]
            item[str(row["direction"])] += 1
            item["max_abs"] = max(item["max_abs"], float(row["abs_standardized_coefficient"]))
    ranked = sorted(counts.items(), key=lambda item: (item[1]["positive"] + item[1]["negative"], item[1]["max_abs"]), reverse=True)
    rows = [
        [variable, stats["block"], stats["positive"] + stats["negative"], stats["positive"], stats["negative"], stats["max_abs"]]
        for variable, stats in ranked[:30]
    ]
    return html_table(["Variable", "Block", "Significant outcomes p<0.05", "Positive", "Negative", "Max abs std coef"], rows)


def append_report(results: list[dict[str, object]], predictors: list[str]) -> None:
    html = REPORT_OUTPUT.read_text(encoding="utf-8")
    marker = "<h2>Order 4 Variable Robustness Spatial Screen</h2>"
    if marker in html:
        html = html.split(marker)[0] + "</body>\n</html>\n"

    total = len(results)
    sig05 = sum(1 for row in results if float(row["p_value"]) < 0.05)
    sig10 = sum(1 for row in results if float(row["p_value"]) < 0.10)
    spatial_sig = sum(1 for row in results if as_number(row["spatial_lambda_p"]) is not None and float(row["spatial_lambda_p"]) < 0.05)
    addition = (
        marker
        + "<p class='note'>Order 4 screens each collected predictor separately against each outcome using a one-variable spatial-error model. "
        "This is a robustness/exploration screen, not a replacement for the selected combined models.</p>"
        + html_table(
            ["Predictors", "Models screened", "p<0.05 coefficient", "p<0.10 coefficient", "p<0.05 lambda"],
            [[len(predictors), total, sig05, sig10, spatial_sig]],
        )
        + "<h3>Most Robust Variables Across Outcomes</h3>"
        + stable_variables_table(results)
        + "<h3>Strongest Variables By Outcome</h3>"
        + strongest_by_outcome_table(results)
    )
    html = html.replace("</body>\n</html>", addition + "\n</body>\n</html>")
    REPORT_OUTPUT.write_text(html, encoding="utf-8")


def main() -> None:
    rows = read_csv(INPUT)
    predictors = full_predictors(rows)
    results = run_screen(rows, predictors)
    top = top_rows(results)
    write_csv(SUMMARY_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in results])
    write_csv(TOP_OUTPUT, [{k: fmt(v) for k, v in row.items()} for row in top])
    append_report(results, predictors)
    print(f"Predictors screened: {len(predictors)}")
    print(f"Models screened: {len(results)}")
    print(f"Wrote {SUMMARY_OUTPUT}")
    print(f"Wrote {TOP_OUTPUT}")
    print(f"Appended {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
