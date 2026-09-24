"""Interpret existing dimension-reduction artifacts without fitting new models.

The script consumes previously generated loadings, VIP tables, summaries, and
the modelling input. It writes interpretation tables and a compact narrative
report for mean turnout.
"""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[5]
DR_ROOT = REPO_ROOT / "data/toronto_election_turnout/modelling/processed/dimension_reduction"
INPUT = (
    REPO_ROOT
    / "data/toronto_election_turnout/modelling/processed/spatial_models/"
    / "toronto_ct_blocks_1_5_model_input_housing_augmented_median_imputed.csv"
)
OUT = DR_ROOT / "latent_interpretation"
TARGET = "outcome_mean_participation_citizen_18plus"


MODEL_SPECS = {
    "full_unfiltered_pls": {
        "family": "PLS, full predictor universe",
        "summary": DR_ROOT / "full_pls/full_unfiltered_pls_summary.csv",
        "loadings": DR_ROOT / "full_pls/full_unfiltered_pls_component_loadings.csv",
        "importance": DR_ROOT / "full_pls/full_unfiltered_pls_variable_importance.csv",
    },
    "theory_cleaned_pls": {
        "family": "PLS, theory-cleaned predictor set",
        "summary": DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_summary.csv",
        "loadings": DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_component_loadings.csv",
        "importance": DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_variable_importance.csv",
    },
    "interaction_augmented_pls": {
        "family": "PLS, cleaned plus retained interaction",
        "summary": DR_ROOT / "interaction_discovery/interaction_augmented_pls_summary.csv",
        "loadings": DR_ROOT / "interaction_discovery/interaction_augmented_pls_component_loadings.csv",
        "importance": DR_ROOT / "interaction_discovery/interaction_augmented_pls_variable_importance.csv",
    },
    "supervised_pca": {
        "family": "Supervised-screen PCA",
        "summary": DR_ROOT / "supervised_pca/supervised_pca_summary.csv",
        "loadings": DR_ROOT / "supervised_pca/supervised_pca_loadings.csv",
        "importance": None,
    },
    "sparse_pls": {
        "family": "Sparse PLS robustness",
        "summary": DR_ROOT / "sparse_pls/sparse_pls_summary.csv",
        "loadings": None,
        "importance": DR_ROOT / "sparse_pls/sparse_pls_variable_importance.csv",
    },
}


FAMILY_LABELS = {
    "age_structure": "age structure",
    "household_class": "education, income, and household class",
    "housing_tenure": "renter/owner tenure",
    "residential_stability": "residential stability",
    "housing_form_density": "urban form and density",
    "immigration_citizenship": "immigration, citizenship, and racialized geography",
    "mayoral_competitiveness": "local mayoral competitiveness",
    "federal_competitiveness": "federal competitiveness",
    "provincial_competitiveness": "provincial competitiveness",
    "transportation_access": "transportation access",
    "service_access": "civic/service proximity",
    "service_contact": "service contact and local need",
}


def plain_name(variable: str) -> str:
    if "__x__" in variable:
        return " x ".join(plain_name(part) for part in variable.split("__x__"))
    cleaned = re.sub(r"^block\d+_", "", variable)
    cleaned = cleaned.replace("_lim_at", "")
    cleaned = cleaned.replace("_5pct", " above 5 percent")
    cleaned = cleaned.replace("_25_64", " 25-64")
    cleaned = cleaned.replace("_18_34", " 18-34")
    cleaned = cleaned.replace("_35_64", " 35-64")
    cleaned = cleaned.replace("_65_plus", " 65 plus")
    cleaned = cleaned.replace("_5_17", " 5-17")
    cleaned = cleaned.replace("_2021_2025", " 2021-2025")
    cleaned = cleaned.replace("_1200m", " within 1200m")
    cleaned = cleaned.replace("_per_1000", " per 1000")
    return cleaned.replace("_", " ")


def family_display(variable: str, family: str) -> str:
    if "__x__" in variable:
        return "interaction term"
    return FAMILY_LABELS.get(family, family)


def variable_family_map() -> dict[str, str]:
    frames = []
    for spec in MODEL_SPECS.values():
        path = spec.get("importance")
        if path and path.exists():
            df = pd.read_csv(path)
            if "family" in df.columns:
                frames.append(df[["variable", "family"]])
    diag = DR_ROOT / "diagnostics/variable_diagnostic_summary.csv"
    if diag.exists():
        df = pd.read_csv(diag)
        frames.append(df[["variable", "family"]])
    if not frames:
        return {}
    merged = pd.concat(frames, ignore_index=True).dropna().drop_duplicates("variable")
    return dict(zip(merged["variable"], merged["family"]))


def read_summary(model: str, spec: dict) -> dict:
    row = pd.read_csv(spec["summary"]).iloc[0].to_dict()
    row["model_key"] = model
    row["model_family"] = spec["family"]
    if "selected_components" in row:
        row["components"] = int(row["selected_components"])
    elif "n_components" in row:
        row["components"] = int(row["n_components"])
    else:
        row["components"] = np.nan
    return row


def summarize_models() -> pd.DataFrame:
    rows = [read_summary(model, spec) for model, spec in MODEL_SPECS.items()]
    out = pd.DataFrame(rows)
    wanted = [
        "model_key",
        "model_family",
        "n",
        "num_predictors",
        "screened_predictor_count",
        "components",
        "keep_per_component",
        "cv_r2",
        "cv_rmse",
        "train_r2",
        "train_rmse",
    ]
    return out[[c for c in wanted if c in out.columns]].sort_values("cv_r2", ascending=False)


def component_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if re.fullmatch(r"component_\d+", c)]


def component_composition(family_map: dict[str, str]) -> pd.DataFrame:
    rows = []
    for model, spec in MODEL_SPECS.items():
        if not spec.get("loadings") or not spec["loadings"].exists():
            continue
        loadings = pd.read_csv(spec["loadings"])
        importance = None
        if spec.get("importance") and spec["importance"].exists():
            importance = pd.read_csv(spec["importance"])
        for comp in component_cols(loadings):
            tmp = loadings[["variable", comp]].copy()
            tmp = tmp.rename(columns={comp: "loading"})
            tmp["abs_loading"] = tmp["loading"].abs()
            tmp["model_key"] = model
            tmp["model_family"] = spec["family"]
            tmp["component"] = comp
            tmp["family"] = tmp["variable"].map(family_map).fillna("unknown")
            tmp["plain_variable"] = tmp["variable"].map(plain_name)
            if importance is not None:
                cols = [
                    c
                    for c in [
                        "variable",
                        "vip",
                        "pls_coefficient",
                        "sparse_pls_coefficient",
                        "turnout_corr",
                        "direction",
                    ]
                    if c in importance.columns
                ]
                tmp = tmp.merge(importance[cols], on="variable", how="left")
            tmp = tmp.sort_values("abs_loading", ascending=False)
            tmp["rank_abs_loading"] = range(1, len(tmp) + 1)
            rows.append(tmp)
    return pd.concat(rows, ignore_index=True)


def family_theme_summary(composition: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        composition.groupby(["model_key", "model_family", "component", "family"], dropna=False)
        .agg(
            family_abs_loading_sum=("abs_loading", "sum"),
            max_abs_loading=("abs_loading", "max"),
            variables=("plain_variable", lambda s: "; ".join(s.head(6))),
        )
        .reset_index()
    )
    totals = grouped.groupby(["model_key", "component"])["family_abs_loading_sum"].transform("sum")
    grouped["family_loading_share"] = grouped["family_abs_loading_sum"] / totals
    grouped["family_label"] = grouped["family"].map(FAMILY_LABELS).fillna(grouped["family"])
    return grouped.sort_values(
        ["model_key", "component", "family_loading_share"], ascending=[True, True, False]
    )


def reference_geographies(composition: pd.DataFrame) -> pd.DataFrame:
    data = pd.read_csv(INPUT)
    geo_cols = ["ct_id", "ctuid", "geo_name", TARGET]
    rows = []
    for (model, comp), group in composition.groupby(["model_key", "component"]):
        vars_present = [v for v in group["variable"] if v in data.columns]
        if not vars_present:
            continue
        weights = group.set_index("variable").loc[vars_present, "loading"].astype(float)
        x = data[vars_present].astype(float)
        x = (x - x.mean()) / x.std(ddof=0).replace(0, np.nan)
        score = x.fillna(0).dot(weights / np.sqrt(np.square(weights).sum()))
        ref = data[geo_cols].copy()
        ref["geo_label"] = "CT " + ref["geo_name"].astype(str)
        ref["model_key"] = model
        ref["component"] = comp
        ref["component_reference_score"] = score
        ref["score_turnout_corr"] = ref["component_reference_score"].corr(ref[TARGET])
        low = ref.nsmallest(8, "component_reference_score").assign(reference_side="low")
        high = ref.nlargest(8, "component_reference_score").assign(reference_side="high")
        near_zero = (
            ref.assign(abs_score=lambda d: d["component_reference_score"].abs())
            .nsmallest(8, "abs_score")
            .drop(columns=["abs_score"])
            .assign(reference_side="near_zero")
        )
        rows.extend([low, high, near_zero])
    return pd.concat(rows, ignore_index=True)


def sparse_summary(family_map: dict[str, str]) -> pd.DataFrame:
    path = MODEL_SPECS["sparse_pls"]["importance"]
    df = pd.read_csv(path).copy()
    df["family"] = df["variable"].map(family_map).fillna(df.get("family", "unknown"))
    df["plain_variable"] = df["variable"].map(plain_name)
    return df.sort_values("vip", ascending=False)


def interaction_summary() -> pd.DataFrame:
    path = DR_ROOT / "interaction_discovery/interaction_screen_results.csv"
    df = pd.read_csv(path)
    cols = [
        "interaction",
        "variable_a",
        "variable_b",
        "family_a",
        "family_b",
        "best_components",
        "cv_r2",
        "cv_rmse",
        "interaction_vip",
        "story",
    ]
    return df[[c for c in cols if c in df.columns]].sort_values("cv_r2", ascending=False)


def top_component_story(theme: pd.DataFrame, comp: pd.DataFrame, model: str, component: str) -> str:
    t = theme[(theme["model_key"] == model) & (theme["component"] == component)].head(3)
    c = comp[(comp["model_key"] == model) & (comp["component"] == component)].head(8)
    fams = ", ".join(t["family_label"].tolist())
    pos = c[c["loading"] > 0]["plain_variable"].head(4).tolist()
    neg = c[c["loading"] < 0]["plain_variable"].head(4).tolist()
    parts = [f"{component_label(component)} concentrates {fams}."]
    if pos:
        parts.append("Positive side: " + ", ".join(pos) + ".")
    if neg:
        parts.append("Negative side: " + ", ".join(neg) + ".")
    return " ".join(parts)


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    tmp = df.copy()
    for col in tmp.columns:
        if pd.api.types.is_float_dtype(tmp[col]):
            if col in {"Predictors", "Latent components", "Best PLS components"}:
                tmp[col] = tmp[col].map(lambda v: "" if pd.isna(v) else f"{v:.0f}")
            else:
                tmp[col] = tmp[col].map(
                    lambda v: "" if pd.isna(v) else f"{0.0 if abs(v) < 0.0005 else v:.3f}"
                )
        else:
            tmp[col] = tmp[col].map(lambda v: "" if pd.isna(v) else str(v))
    headers = list(tmp.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in tmp.iterrows():
        vals = [str(row[col]).replace("|", "\\|") for col in headers]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def component_label(component: str) -> str:
    return component.replace("component_", "Component ")


def clean_component_terms(composition: pd.DataFrame, component: str, n: int = 10) -> pd.DataFrame:
    rows = composition[
        (composition["model_key"] == "theory_cleaned_pls")
        & (composition["component"] == component)
    ].head(n)
    out = rows[
        [
            "plain_variable",
            "family",
            "loading",
            "vip",
            "turnout_corr",
            "direction",
        ]
    ].copy()
    out["family"] = out["family"].map(FAMILY_LABELS).fillna(out["family"])
    out["loading_side"] = np.where(out["loading"] >= 0, "high side", "low side")
    out = out.rename(
        columns={
            "plain_variable": "Variable",
            "family": "Variable family",
            "loading": "Component loading",
            "vip": "VIP",
            "turnout_corr": "Bivariate turnout correlation",
            "direction": "PLS turnout direction",
            "loading_side": "Component side",
        }
    )
    return out[
        [
            "Variable",
            "Variable family",
            "Component side",
            "Component loading",
            "VIP",
            "Bivariate turnout correlation",
            "PLS turnout direction",
        ]
    ]


def clean_family_terms(theme: pd.DataFrame, component: str, n: int = 5) -> pd.DataFrame:
    rows = theme[
        (theme["model_key"] == "theory_cleaned_pls")
        & (theme["component"] == component)
    ].head(n)
    out = rows[["family_label", "family_loading_share", "variables"]].copy()
    out = out.rename(
        columns={
            "family_label": "Latent theme",
            "family_loading_share": "Share of absolute loading",
            "variables": "Representative variables",
        }
    )
    return out


def readable_reference_table(refs: pd.DataFrame, component: str) -> pd.DataFrame:
    rows = refs[
        (refs["model_key"] == "theory_cleaned_pls")
        & (refs["component"] == component)
        & (refs["reference_side"].isin(["high", "low"]))
    ].copy()
    rows["Reference side"] = rows["reference_side"].map(
        {
            "high": f"High {component_label(component)} profile",
            "low": f"Low {component_label(component)} profile",
        }
    )
    rows["Mean turnout"] = rows[TARGET]
    rows["Reference score"] = rows["component_reference_score"]
    rows["Component-turnout correlation"] = rows["score_turnout_corr"]
    rows = rows.sort_values(["reference_side", "component_reference_score"], ascending=[True, False])
    return rows[
        [
            "Reference side",
            "geo_label",
            "Mean turnout",
            "Reference score",
            "Component-turnout correlation",
        ]
    ].rename(columns={"geo_label": "Reference CT"})


def reference_paragraph(component: str) -> str:
    text = {
        "component_1": (
            "The high-score CTs on Component 1 are the clearest examples of the turnout-resource side of the model: they align with education, stronger electoral margins, and lower values on the newcomer/racialized-fragmentation bundle. The low-score CTs sit on the opposite side and have much lower mean turnout in the reference table. This is the component where the reference scores are most directly interpretable as a turnout gradient."
        ),
        "component_2": (
            "Component 2 is best read as a contrast between older residential stability and younger dense renter/carless urban geography. The reference CTs show that both sides can include moderate turnout, which is why this component should not be read as a simple high-turnout/low-turnout axis. Its value is in describing the type of place after the main Component 1 turnout gradient has already done much of the explanatory work."
        ),
        "component_3": (
            "Component 3 separates vertical rental/newcomer urban form from more stable and larger-household contexts. The high side combines apartments, condos, renters, density, recent immigration, and low income; the low side contains places that do not share that same vertical-rental profile. This helps distinguish dense urban form from the education/electoral-attachment pattern in Component 1."
        ),
        "component_4": (
            "Component 4 is a mixed family/service-need and electoral-margin dimension. Its high side includes school-age share, social housing, renter share, residential stability, and federal/provincial margins; its low side includes older and condo-heavy contexts. Because the loading pattern mixes social need with electoral context, it is useful for story-building but should be described cautiously."
        ),
        "component_5": (
            "Component 5 is the most tentative component. It places service-contact and road-exposure indicators alongside condo and education signals, while the opposite side includes community-centre/library access, social housing, renters, no-car households, and residential stability. This is less a standalone turnout mechanism than a reminder that service context changes meaning depending on the social geography around it."
        ),
    }
    return text[component]


def interaction_readable_table(interactions: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    rows = interactions.head(n).copy()
    rows["Interaction term"] = rows.apply(
        lambda r: f"{plain_name(r['variable_a'])} x {plain_name(r['variable_b'])}", axis=1
    )
    rows["Variable families"] = rows.apply(
        lambda r: (
            f"{FAMILY_LABELS.get(r['family_a'], r['family_a'])} x "
            f"{FAMILY_LABELS.get(r['family_b'], r['family_b'])}"
        ),
        axis=1,
    )
    rows["Interpretive result"] = rows.apply(
        lambda r: (
            f"Screened interaction was already tested in the prior workflow. "
            f"It reached CV R2 {r['cv_r2']:.3f}, CV RMSE {r['cv_rmse']:.3f}, "
            f"and interaction VIP {r['interaction_vip']:.3f}; substantively, it suggests {interaction_meaning(r)}"
        ),
        axis=1,
    )
    return rows[
        [
            "Interaction term",
            "Variable families",
            "best_components",
            "cv_r2",
            "cv_rmse",
            "interaction_vip",
            "Interpretive result",
        ]
    ].rename(
        columns={
            "best_components": "Best PLS components",
            "cv_r2": "Cross-validated R2",
            "cv_rmse": "Cross-validated RMSE",
            "interaction_vip": "Interaction VIP",
        }
    )


def interaction_meaning(row: pd.Series) -> str:
    a = plain_name(row["variable_a"])
    b = plain_name(row["variable_b"])
    fams = {row["family_a"], row["family_b"]}
    if fams == {"household_class", "service_contact"}:
        return (
            "that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts."
        )
    if "immigration_citizenship" in fams and "service_contact" in fams:
        return (
            "that service-contact indicators may work differently in immigrant, language, or citizenship geographies."
        )
    if fams == {"household_class", "age_structure"}:
        return (
            "that class and education patterns are conditioned by local age structure."
        )
    if "mayoral_competitiveness" in fams:
        return (
            "that local electoral fragmentation may compound social-geographic turnout differences."
        )
    return f"that the relationship between {a} and turnout changes depending on {b}, rather than operating as a purely additive effect."


def sparse_readable_table(sparse: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    rows = sparse.head(n).copy()
    rows["Variable"] = rows["variable"].map(plain_name)
    rows["Variable family"] = rows["family"].map(FAMILY_LABELS).fillna(rows["family"])
    return rows[
        [
            "Variable",
            "Variable family",
            "vip",
            "sparse_pls_coefficient",
            "selected_in_sparse_weights",
            "nonzero_component_count",
        ]
    ].rename(
        columns={
            "vip": "VIP",
            "sparse_pls_coefficient": "Sparse PLS coefficient",
            "selected_in_sparse_weights": "Selected in sparse weights",
            "nonzero_component_count": "Nonzero component count",
        }
    )


def model_results_table(model_summary: pd.DataFrame) -> pd.DataFrame:
    out = model_summary.copy()
    out["Model"] = out["model_key"].map(
        {
            "interaction_augmented_pls": "Interaction-augmented PLS",
            "full_unfiltered_pls": "Full unfiltered PLS",
            "sparse_pls": "Sparse PLS",
            "theory_cleaned_pls": "Theory-cleaned PLS",
            "supervised_pca": "Supervised PCA",
        }
    )
    out["Predictors"] = out["num_predictors"].fillna(out["screened_predictor_count"])
    out = out.rename(
        columns={
            "components": "Latent components",
            "cv_r2": "Cross-validated R2",
            "cv_rmse": "Cross-validated RMSE",
            "train_r2": "Training R2",
            "train_rmse": "Training RMSE",
        }
    )
    return out[
        [
            "Model",
            "Predictors",
            "Latent components",
            "Cross-validated R2",
            "Cross-validated RMSE",
            "Training R2",
            "Training RMSE",
        ]
    ]


def cleaned_model_results_table(top_vip: pd.DataFrame) -> pd.DataFrame:
    out = top_vip.head(15).copy()
    out["Variable"] = out["variable"].map(plain_name)
    out["Variable family"] = out["family"].map(FAMILY_LABELS).fillna(out["family"])
    return out[
        [
            "Variable",
            "Variable family",
            "vip",
            "pls_coefficient",
            "turnout_corr",
            "direction",
        ]
    ].rename(
        columns={
            "vip": "VIP",
            "pls_coefficient": "Cleaned PLS coefficient",
            "turnout_corr": "Bivariate turnout correlation",
            "direction": "PLS turnout direction",
        }
    )


def model_top_terms(composition: pd.DataFrame, model: str, component: str = "component_1", n: int = 12) -> pd.DataFrame:
    rows = composition[
        (composition["model_key"] == model)
        & (composition["component"] == component)
    ].head(n).copy()
    rows["Variable"] = rows["plain_variable"]
    rows["Variable family"] = rows.apply(
        lambda r: family_display(r["variable"], r["family"]), axis=1
    )
    rows["Component side"] = np.where(rows["loading"] >= 0, "high side", "low side")
    return rows[
        [
            "Variable",
            "Variable family",
            "Component side",
            "loading",
            "vip",
            "turnout_corr",
            "direction",
        ]
    ].rename(
        columns={
            "loading": "Component loading",
            "vip": "VIP",
            "turnout_corr": "Bivariate turnout correlation",
            "direction": "PLS turnout direction",
        }
    )


def pca_component_table(composition: pd.DataFrame, n_components: int = 8, n_terms: int = 6) -> pd.DataFrame:
    rows = []
    for i in range(1, n_components + 1):
        comp = f"component_{i}"
        tmp = composition[
            (composition["model_key"] == "supervised_pca")
            & (composition["component"] == comp)
        ].head(n_terms).copy()
        tmp["Component"] = component_label(comp)
        tmp["Variable"] = tmp["plain_variable"]
        tmp["Variable family"] = tmp["family"].map(FAMILY_LABELS).fillna(tmp["family"])
        tmp["Component side"] = np.where(tmp["loading"] >= 0, "high side", "low side")
        rows.append(
            tmp[
                [
                    "Component",
                    "Variable",
                    "Variable family",
                    "Component side",
                    "loading",
                    "abs_loading",
                ]
            ]
        )
    out = pd.concat(rows, ignore_index=True)
    return out.rename(
        columns={
            "loading": "PCA loading",
            "abs_loading": "Absolute loading",
        }
    )


def overlap_table(benchmark: pd.DataFrame, comparator: pd.DataFrame, label: str, n: int = 15) -> pd.DataFrame:
    b = benchmark.head(n).copy()
    c = comparator.head(n).copy()
    b_vars = set(b["variable"])
    c_vars = set(c["variable"])
    rows = []
    for var in sorted(b_vars | c_vars):
        rows.append(
            {
                "Variable": plain_name(var),
                "In augmented PLS top terms": var in b_vars,
                f"In {label} top terms": var in c_vars,
                "Variable family": family_display(
                    var,
                    (b[b["variable"].eq(var)]["family"].head(1).tolist()
                     or c[c["variable"].eq(var)]["family"].head(1).tolist()
                     or ["unknown"])[0],
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["In augmented PLS top terms", f"In {label} top terms", "Variable"],
        ascending=[False, False, True],
    )


def pairwise_overlap_table(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_label: str,
    right_label: str,
    n: int = 15,
) -> pd.DataFrame:
    l = left.head(n).copy()
    r = right.head(n).copy()
    l_vars = set(l["variable"])
    r_vars = set(r["variable"])
    rows = []
    for var in sorted(l_vars | r_vars):
        family = (
            l[l["variable"].eq(var)]["family"].head(1).tolist()
            or r[r["variable"].eq(var)]["family"].head(1).tolist()
            or ["unknown"]
        )[0]
        rows.append(
            {
                "Variable": plain_name(var),
                f"In {left_label} top terms": var in l_vars,
                f"In {right_label} top terms": var in r_vars,
                "Variable family": family_display(var, family),
            }
        )
    return pd.DataFrame(rows).sort_values(
        [f"In {left_label} top terms", f"In {right_label} top terms", "Variable"],
        ascending=[False, False, True],
    )


def pca_screened_importance(composition: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    pca = composition[composition["model_key"].eq("supervised_pca")].copy()
    agg = (
        pca.groupby(["variable", "plain_variable", "family"], as_index=False)
        .agg(max_abs_loading=("abs_loading", "max"))
        .sort_values("max_abs_loading", ascending=False)
        .head(n)
    )
    agg["Variable family"] = agg["family"].map(FAMILY_LABELS).fillna(agg["family"])
    return agg[["plain_variable", "Variable family", "max_abs_loading"]].rename(
        columns={
            "plain_variable": "Variable",
            "max_abs_loading": "Maximum absolute PCA loading",
        }
    )


def write_comparison_report(
    model_summary: pd.DataFrame,
    composition: pd.DataFrame,
    theme: pd.DataFrame,
    interactions: pd.DataFrame,
) -> None:
    augmented_importance = (
        pd.read_csv(DR_ROOT / "interaction_discovery/interaction_augmented_pls_variable_importance.csv")
        .sort_values("vip", ascending=False)
    )
    cleaned_importance = (
        pd.read_csv(DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_variable_importance.csv")
        .sort_values("vip", ascending=False)
    )
    pca_loadings = pd.read_csv(DR_ROOT / "supervised_pca/supervised_pca_loadings.csv")
    pca_rank = pca_loadings[["variable", "max_abs_loading"]].copy()
    pca_rank["family"] = pca_rank["variable"].map(variable_family_map()).fillna("unknown")

    perf = model_results_table(
        model_summary[model_summary["model_key"].isin(
            ["interaction_augmented_pls", "theory_cleaned_pls", "supervised_pca"]
        )]
    )
    augmented_terms = model_top_terms(composition, "interaction_augmented_pls", "component_1", 14)
    cleaned_c1_terms = model_top_terms(composition, "theory_cleaned_pls", "component_1", 12)
    cleaned_themes = theme[
        theme["model_key"].eq("theory_cleaned_pls")
    ].groupby("component").head(3)[
        ["component", "family_label", "family_loading_share", "variables"]
    ].copy()
    cleaned_themes["component"] = cleaned_themes["component"].map(component_label)
    cleaned_themes = cleaned_themes.rename(
        columns={
            "component": "Cleaned PLS component",
            "family_label": "Dominant theme",
            "family_loading_share": "Share of absolute loading",
            "variables": "Representative variables",
        }
    )

    pca_terms = pca_component_table(composition, 8, 5)
    pca_top = pca_screened_importance(composition, 15)
    interactions_table = interaction_readable_table(interactions, 8)
    cleaned_overlap = overlap_table(augmented_importance, cleaned_importance, "cleaned PLS", 15)
    pca_rank_for_overlap = pca_rank.sort_values("max_abs_loading", ascending=False).head(15)
    pca_overlap = overlap_table(augmented_importance, pca_rank_for_overlap, "supervised PCA", 15)

    report = f"""# Latent Model Comparison Report

This report compares the two more interpretable latent approaches back to the strongest predictive benchmark, the interaction-augmented PLS. No new models were fit. The comparison uses existing loadings, VIP tables, model summaries, supervised PCA loadings, and the prior interaction screen.

## Report Structure

**Section 1: Benchmark Model - Interaction-Augmented PLS.** This section introduces the strongest predictive model, explains why it is used as the benchmark, and summarizes its model performance, main component terms, and interaction-screen evidence.

**Section 2: Cleaned PLS Compared With The Benchmark.** This section compares the theory-cleaned PLS with the interaction-augmented PLS. It focuses on whether cleaned PLS recovers the benchmark's main turnout axis and what extra interpretive structure its five components add.

**Section 3: Supervised PCA Compared With The Benchmark.** This section compares supervised PCA with the interaction-augmented PLS. It treats PCA as a more familiar validation check and asks which benchmark themes reappear under PCA and which are separated differently.

**Section 4: Overall Interpretation.** This section synthesizes what the comparisons imply for the turnout story: which findings are stable across models, which are specific to the augmented interaction model, and how the strongest predictive model can be understood as a compressed version of the broader latent geography.

**Tables Included.** The report includes model performance, augmented PLS component terms, interaction-screen results, cleaned PLS Component 1 terms, shared/distinct variable comparisons, cleaned PLS component themes, supervised PCA high-loading variables, and supervised PCA component terms.

## Benchmark: Interaction-Augmented PLS

The interaction-augmented PLS is the strongest existing dimension-reduction model by cross-validation. It has the highest CV R2 and lowest CV RMSE among the focused latent candidates, but it keeps only one retained PLS component. That means it is best interpreted as a compact benchmark axis plus interaction evidence, not as a multi-component explanation of Toronto's turnout geography.

{md_table(perf)}

The benchmark component is substantively close to the main axis found in the cleaned PLS: education and electoral attachment on one side, and newcomer/racialized/language/class-fragmentation geography on the other. Its strongest negative-loading variables include visible minority share, effective mayoral candidates above 5 percent, unemployment, non-official mother tongue, average household size, non-citizenship, and recent immigration. Its strongest positive-loading variables include bachelor-or-higher education, mayoral top-two margin, federal margin, shelter/library/service-contact variables, and age 65 plus share.

Top augmented PLS component terms:

{md_table(augmented_terms)}

The interaction evidence is why this model predicts slightly better. The benchmark does not simply say that service-contact variables matter; it says they matter conditionally, especially when paired with low income, education, unemployment, household size, language/citizenship geography, and age.

{md_table(interactions_table)}

## Cleaned PLS Compared With Interaction-Augmented PLS

The cleaned PLS is slightly weaker predictively than the augmented PLS, but it is the best interpretive companion to it. The key finding is that cleaned PLS Component 1 reproduces the same broad benchmark axis: education/electoral attachment versus newcomer/racialized-fragmentation geography. This supports the view that the augmented model's strongest predictive component is not an artifact of the interaction screen.

The difference is that cleaned PLS decomposes the benchmark story into five dimensions. Component 1 carries the direct turnout gradient. Components 2-5 then separate older stability, young dense renter/carless geography, vertical rental/newcomer urban form, family/social-housing/service-need context, and service-contact/road-exposure context. In other words, cleaned PLS does not beat the benchmark; it explains what the benchmark compresses.

Cleaned PLS Component 1 terms:

{md_table(cleaned_c1_terms)}

Shared and distinct top variables:

{md_table(cleaned_overlap)}

Cleaned PLS component themes:

{md_table(cleaned_themes)}

Interpretively, the cleaned PLS adds three things that the augmented PLS does not show as clearly. First, it shows that the strongest turnout axis is only one part of the latent structure. Second, it separates density into different meanings: young/renter/carless density is not the same as condo/education density or family/social-housing density. Third, it shows why some variables have mixed signs or weak standalone interpretations: service access, 311 requests, KSI collisions, and development applications appear in secondary components and interactions rather than as simple one-direction predictors.

## Supervised PCA Compared With Interaction-Augmented PLS

Supervised PCA is weaker predictively than the augmented PLS, but it is valuable because it is more familiar and less directly supervised once the screening step is done. It independently recovers many of the same ingredients: visible minority share, bachelor-or-higher education, mayoral competitiveness, non-citizenship, recent immigration, federal/provincial margins, low income, age, no-car households, social housing, school-age share, and KSI collisions.

The main difference is conceptual. The augmented PLS builds the strongest turnout-predictive axis directly. Supervised PCA first screens variables by turnout association, then decomposes covariance among the screened variables. So PCA gives clearer mechanical contrasts, but those contrasts are not necessarily the best turnout-predictive axes. This is why supervised PCA is useful as a confirmation check rather than the central story model.

Highest-loading supervised PCA variables:

{md_table(pca_top)}

Supervised PCA component terms:

{md_table(pca_terms)}

Shared and distinct top variables:

{md_table(pca_overlap)}

The PCA comparison mainly confirms the benchmark story rather than replacing it. PCA Component 1 mirrors the same broad divide, though with signs reversed: racialized/newcomer/household/electoral-fragmentation variables sit opposite education and electoral margins. Later PCA components separate service need, age, social housing, KSI collisions, and electoral margins in ways that are substantively useful, but less directly tied to predictive performance.

## Overall Interpretation

The three-model comparison strengthens the story. The strongest model is interaction-augmented PLS, but the same social-geographic structure appears in cleaned PLS and supervised PCA. That means the main interpretation does not depend on one modeling choice.

The safest core story is this: mean turnout is highest where education, clearer electoral attachment, and institutional/civic resources cluster together. It is lower where newcomer/racialized/citizenship/language geography overlaps with larger households, unemployment or lower income, and fragmented local electoral competition. The interaction model adds that service-contact variables matter conditionally, not as simple standalone effects.

Cleaned PLS is the best model for explaining the benchmark because it decomposes the benchmark axis into readable secondary dimensions. Supervised PCA is the best model for validating the benchmark because it uses a familiar PCA structure and still recovers the same broad ingredients. Together, they make the augmented PLS less opaque: the strongest predictive model is not a black box, but a compressed version of a broader turnout geography.
"""
    (OUT / "latent_model_comparison_report.md").write_text(report, encoding="utf-8")


def write_report(
    model_summary: pd.DataFrame,
    composition: pd.DataFrame,
    theme: pd.DataFrame,
    refs: pd.DataFrame,
    sparse: pd.DataFrame,
    interactions: pd.DataFrame,
) -> None:
    clean = model_summary[model_summary["model_key"] == "theory_cleaned_pls"].iloc[0]
    inter = model_summary[model_summary["model_key"] == "interaction_augmented_pls"].iloc[0]
    pca = model_summary[model_summary["model_key"] == "supervised_pca"].iloc[0]
    sparse_row = model_summary[model_summary["model_key"] == "sparse_pls"].iloc[0]

    pca_stories = [
        top_component_story(theme, composition, "supervised_pca", f"component_{i}")
        for i in range(1, int(pca["components"]) + 1)
    ]

    top_vip = (
        pd.read_csv(DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_variable_importance.csv")
        .sort_values("vip", ascending=False)
    )
    top_sparse = sparse_readable_table(sparse)
    readable_interactions = interaction_readable_table(interactions)
    pca_loadings = pd.read_csv(DR_ROOT / "supervised_pca/supervised_pca_loadings.csv")
    pca_rank = pca_loadings[["variable", "max_abs_loading"]].copy()
    pca_rank["family"] = pca_rank["variable"].map(variable_family_map()).fillna("unknown")
    pca_rank = pca_rank.sort_values("max_abs_loading", ascending=False)
    pca_top = pca_screened_importance(composition, 15)
    pca_terms = pca_component_table(composition, 8, 5)
    cleaned_pca_overlap = pairwise_overlap_table(
        top_vip,
        pca_rank,
        "cleaned PLS",
        "supervised PCA",
        15,
    )
    latent_names = [
        (
            "Component 1: education and electoral attachment versus newcomer/racialized-fragmentation geography",
            "This is the main direct turnout axis. Its high side combines university education and larger election margins; its low side combines visible minority share, non-citizenship, recent immigration, larger household size, and mayoral fragmentation.",
        ),
        (
            "Component 2: established older stability versus young dense carless-renter geography",
            "This axis separates older, longer-residence CTs from younger, denser, more carless, renter/newcomer CTs. It is more compositional than directly predictive after Component 1.",
        ),
        (
            "Component 3: vertical rental/newcomer urban form versus larger-household stability",
            "The high side is apartment/condo/renter/density with recent immigration and low income; the opposite side is more stable and larger-household. This helps distinguish different kinds of urban density.",
        ),
        (
            "Component 4: family/social-housing/service need with electoral margins versus older condo geography",
            "This is a mixed axis linking school-age share, social housing, and federal/provincial margins against older and condo-heavy contexts.",
        ),
        (
            "Component 5: service-contact/road-exposure and condo-education versus rental/service-access vulnerability",
            "This is the most ambiguous cleaned component. It mainly says that service-contact variables matter as part of urban context rather than as simple standalone turnout predictors.",
        ),
    ]
    component_sections = []
    for i, (name, body) in enumerate(latent_names, start=1):
        comp = f"component_{i}"
        component_sections.append(
            f"""### {component_label(comp)}: {name.split(': ', 1)[1]}

**{name}.** {body}

{reference_paragraph(comp)}

Most influential variables in this component:

{md_table(clean_component_terms(composition, comp, 10))}

Main variable-family composition:

{md_table(clean_family_terms(theme, comp, 5))}
"""
        )
    reference_sections = []
    for i in range(1, 6):
        comp = f"component_{i}"
        reference_sections.append(
            f"""### {component_label(comp)} Reference CTs

{reference_paragraph(comp)}

{md_table(readable_reference_table(refs, comp))}
"""
        )

    report = f"""# Latent Variable Interpretation Report: Mean Turnout

This report interprets the existing dimension-reduction outputs for mean CT turnout (`{TARGET}`). No new models were fit. The analysis reads prior model summaries, loadings, VIP tables, interaction screens, and the existing CT model input.

## Report Structure

**Section 1: Main Findings.** Summarizes the overall latent-variable story for mean turnout and explains why the theory-cleaned PLS is the main interpretive model.

**Section 2: Cleaned PLS Latent Meanings.** Interprets the five cleaned PLS components, including their high/low sides, dominant variable families, and substantive meanings.

**Section 3: Cleaned PLS Model Results.** Reports model performance and the most important cleaned PLS variables by VIP, coefficient direction, and bivariate turnout correlation.

**Section 4: Direction Toward Turnout And Reference Categories.** Explains how the components relate to turnout and gives high/low reference CTs for each cleaned PLS component.

**Section 5: Interactions And Bundles.** Interprets the interaction-augmented PLS evidence, especially why service-contact variables matter conditionally rather than as simple standalone predictors.

**Section 6: Cleaned PLS Compared With Supervised PCA.** Compares the cleaned PLS latent interpretation with supervised PCA, highlighting shared reference categories, sign reversals, and PCA-specific additions.

**Section 7: Suggested Story.** Synthesizes the model interpretation into a coherent turnout narrative.

**Section 8: Robustness Across Model Types.** Places sparse PLS and PCA robustness evidence after the main story as supporting evidence.

**Section 9: Appendices.** Provides selected model, component, reference geography, PCA, and caution tables.

## Section 1: Main Findings

The strongest practical finding is that mean turnout is not organized by one isolated predictor. Across the existing PLS, sparse PLS, supervised PCA, and interaction checks, turnout is structured by bundled social geographies: immigration/citizenship/racialized composition, education and class resources, local electoral competitiveness, age and household composition, housing form, and a weaker but recurring urban-service/transportation layer. The latent variables matter because these dimensions overlap in Toronto CTs; they are not cleanly separable in ordinary single-variable rankings.

The best cross-validated latent candidate is the interaction-augmented PLS (`CV R2 {inter['cv_r2']:.3f}`, `CV RMSE {inter['cv_rmse']:.3f}`). However, the theory-cleaned PLS is nearly as strong (`CV R2 {clean['cv_r2']:.3f}`, `CV RMSE {clean['cv_rmse']:.3f}`) and is the better main interpretive model because it avoids the worst duplicate and inverse-variable double counting. Sparse PLS (`CV R2 {sparse_row['cv_r2']:.3f}`) and supervised PCA (`CV R2 {pca['cv_r2']:.3f}`) are best used as robustness checks: they show that the same broad ingredients reappear even when the model is simplified or PCA-screened.

The main substantive axis is Component 1 of the cleaned PLS: education and electoral attachment on one side, and newcomer/racialized-fragmentation geography on the other. The high side of this component aligns with higher mean turnout; the low side aligns with lower mean turnout. That does not mean immigrant or racialized residents are inherently less politically engaged. At the CT level, the component is more plausibly capturing eligibility, settlement timing, campaign contact, institutional inclusion, household structure, and local political context together.

The other cleaned PLS components are still important, but they should be read differently. Components 2-5 describe the structure of Toronto's social geography after the strongest turnout gradient has already been extracted. They separate older stability from younger dense renter geography, vertical rental/newcomer urban form from larger-household stability, family/service need from older condo contexts, and service-contact variables from simple one-direction turnout claims. In short: Component 1 is the clearest turnout gradient; Components 2-5 help explain what kinds of places sit behind that gradient.

## Section 2: Cleaned PLS Latent Meanings

The theory-cleaned PLS should be the main interpretive model because it keeps most of the full model's predictive power while using 27 selected predictors instead of 70. It retains enough predictive power to be credible, while its components are much easier to interpret than the full 70-variable PLS.

{chr(10).join(component_sections)}

## Section 3: Cleaned PLS Model Results

The table below gives the main model-level results. The interaction-augmented PLS has the best cross-validated fit, but the cleaned PLS is the main interpretive model because it is almost as predictive and produces five readable latent dimensions.

{md_table(model_results_table(model_summary))}

The next table reports the most important variables in the cleaned PLS model. VIP values above 1 indicate above-average contribution to the supervised latent projection. The cleaned PLS coefficient gives the direction inside the cleaned PLS prediction; the bivariate correlation is included as a simpler reference point.

{md_table(cleaned_model_results_table(top_vip))}

## Section 4: Direction Toward Turnout And Reference Categories

The strongest cleaned PLS VIP evidence points to lower mean turnout in CTs with higher visible minority share, larger household size, higher non-citizen share, higher recent immigrant share, and more fragmented mayoral competition. Higher bachelor-or-higher education is the strongest positive counterweight. Federal and provincial margin variables are weaker but generally point toward higher turnout in places with clearer/stronger party geography.

Only Component 1 behaves like a strong direct turnout gradient in the projection-based reference scores (`r about 0.67` with mean turnout). Components 2-5 should be read as secondary dimensions: they organize the remaining social geography after the primary turnout-resource/newcomer-fragmentation axis is accounted for.

### Reference Categories

The high/low ends of the cleaned PLS components should be read as reference categories, not individual-level claims. High component scores identify CTs whose standardized variable profile aligns with the existing component loadings; low scores identify the opposite side of the same latent axis.

These reference geographies help keep interpretation grounded. A component name should be checked against both its variable composition and the places sitting at the high and low ends. The reference scores are interpretive projections from existing loadings and standardized existing predictors, not newly fitted model scores.

{chr(10).join(reference_sections)}

## Section 5: Interactions And Bundles

The interaction screen was already conducted in the prior workflow. The rows below are therefore not proposed future tests; they are screened interaction results, ranked by cross-validated performance. The strongest interaction candidate is low-income share with 311 requests per 1,000 residents, which reached `CV R2 {readable_interactions.iloc[0]['Cross-validated R2']:.3f}` and `CV RMSE {readable_interactions.iloc[0]['Cross-validated RMSE']:.3f}`. Substantively, this means service-contact intensity should not be read as a simple standalone variable. It appears to matter differently depending on whether a CT is lower-income, higher-education, larger-household, higher-unemployment, immigrant/language, or otherwise socially distinct.

{md_table(readable_interactions)}

The important pattern is not just the top individual interaction. Several of the strongest interactions pair household/class variables with service-contact variables, especially 311 requests, KSI collision rates, and development applications. A second cluster links service-contact variables with immigrant, language, or citizenship geography. These results support a bundled interpretation: local service demand, neighbourhood change, and civic infrastructure may have different turnout meanings in different social geographies.

For the story, this means service contact should not be described only as "more 311 equals more turnout" or "less 311 equals lower turnout." Its meaning changes with class, need, and settlement context. The more defensible phrasing is that service-contact intensity appears as part of a broader civic-demand or neighbourhood-condition bundle, and the interaction-augmented PLS performs best because it lets that conditional structure enter the model.

## Section 6: Cleaned PLS Compared With Supervised PCA

Supervised PCA is useful here because it offers a familiar comparison point. It first screens variables by turnout association and then applies PCA to the screened set. That makes it less directly supervised than PLS after the screen, but easier to interpret as a covariance structure among turnout-relevant variables. The main question is whether PCA uncovers the same latent geography as cleaned PLS, or whether it separates the story in a different way.

The strongest similarity is that both models recover the same main reference category: education and electoral attachment versus newcomer/racialized/citizenship and household-fragmentation geography. Cleaned PLS Component 1 puts bachelor-or-higher education, mayoral margin, and federal margin on one side, while visible minority share, non-citizenship, recent immigration, larger household size, and effective mayoral candidates above 5 percent sit on the other. Supervised PCA Component 1 captures a very similar contrast, but with the signs reversed: visible minority share, effective mayoral candidates above 5 percent, and average household size load positively, while bachelor-or-higher education, mayoral top-two margin, and federal margin load negatively. This is still a similarity, not a contradiction, because component signs are arbitrary; the two models are describing the same opposing reference categories.

The second similarity is that both models repeatedly return the same broad variable families: immigration/citizenship/racialized geography, education and household class, local electoral competitiveness, service contact, age, and transportation access. The exact component numbers differ, but the reference categories are stable. For example, age 65 plus share, low income share, no-car households, school-age share, social housing, KSI collisions, and provincial/federal margins all appear as important in PCA even when they are secondary or lower-VIP terms in cleaned PLS.

The main difference is how the models distribute these ideas across components. Cleaned PLS is turnout-supervised and therefore concentrates the main turnout story into Component 1, then uses Components 2-5 to organize secondary social geography. Supervised PCA spreads the same variables across more components: service need, KSI collisions, social housing, age, and provincial/federal margins become more visible as separate PCA contrasts. This does not mean PCA has found a stronger turnout model; its predictive performance is weaker. But it does mean PCA is useful for checking what cleaned PLS may compress into secondary components or lower-ranked variables.

The most important additions from supervised PCA are service-contact and age contrasts. KSI collisions per 1,000, social housing share, age 65 plus share, provincial margin, and school-age share are among the highest-loading PCA variables. Cleaned PLS includes these variables, but its main interpretation is dominated by the Component 1 education/newcomer-fragmentation axis. PCA therefore adds a helpful caution: the turnout story should not ignore service need, road-exposure context, age structure, and social housing simply because they are not the strongest cleaned-PLS VIP terms.

Shared and distinct high-ranking variables:

{md_table(cleaned_pca_overlap)}

Highest-loading supervised PCA variables:

{md_table(pca_top)}

## Section 7: Suggested Story

Mean turnout in Toronto CTs appears highest where the latent geography combines education, clearer electoral attachment, and forms of civic embeddedness. In the cleaned PLS, this appears most clearly in Component 1, where bachelor-or-higher education and stronger election margins sit opposite visible minority share, non-citizenship, recent immigration, larger household size, and mayoral fragmentation. This is the strongest and most direct turnout-facing result of the latent-variable analysis.

Lower mean turnout is most consistently associated with CTs where newcomer/racialized/citizenship geography overlaps with larger households and fragmented local electoral competition. This should be interpreted carefully. The model is not identifying individual political interest or individual willingness to vote. It is describing places where eligibility, settlement timing, language/citizenship context, campaign contact, institutional familiarity, and household/community structure may combine to produce lower observed turnout.

Education is the strongest positive counterweight in the results. It appears with high VIP in cleaned PLS, sparse PLS, supervised PCA, and robustness checks. This suggests that educational resources may proxy civic skills, political information access, institutional familiarity, or class position. But education does not operate alone: in the latent structure, it sits alongside election margins and against several citizenship/settlement variables. That is why the story should be about a resource-and-attachment geography rather than "education alone raises turnout."

The secondary components deepen the geographic story. Older stability is not identical to high turnout, dense apartment/condo geography is not a single political type, and service-contact variables are not simple signs of participation or disengagement. Components 2-5 show that Toronto's turnout geography contains multiple kinds of density, multiple kinds of stability, and multiple kinds of service context. This helps explain why ordinary one-variable rankings can feel thin: the politically meaningful object is often the combination of variables, not one variable by itself.

The interaction results add one more layer to the story. The best-performing model overall is the interaction-augmented PLS, and its strongest screened interactions involve class/household variables with service-contact measures. This implies that neighbourhood condition and service demand matter conditionally: 311 requests, KSI collisions, or development pressure may not have one stable meaning across all CTs. Their turnout meaning changes depending on income, education, household structure, age, and immigrant/citizenship geography.

The supervised PCA comparison adds a final robustness note. PCA confirms the main cleaned-PLS divide even when the signs are reversed: education and electoral margins sit opposite visible minority share, household size, non-citizenship, recent immigration, and local electoral fragmentation. At the same time, PCA makes service-contact and age variables more visible, especially KSI collisions, social housing, age 65 plus share, school-age share, and provincial/federal margins. So the final story should keep both layers: the primary turnout-resource/newcomer-fragmentation axis, and a secondary layer about service need, age, and urban condition.

The substantive contribution of the latent-variable analysis is therefore to turn the project away from a simple predictor ranking. It shows that turnout is structured by combinations: newcomer/racialized/citizenship geographies overlap with household composition and class; education and electoral attachment offset part of that pattern; local electoral competitiveness has a surprisingly strong place in the same latent space; and service-contact variables become most meaningful when read through interactions with class, need, and settlement context.

## Section 8: Robustness Across Model Types

Supervised PCA independently screens to a compact set and still recovers the same broad ingredients:

{chr(10).join(f'- {story}' for story in pca_stories[:5])}

Sparse PLS also keeps the same strongest signals under a simpler component constraint. Its highest VIP variables are:

{md_table(top_sparse)}

The recurring variables across PLS, sparse PLS, PCA, and Elastic Net robustness are therefore the safest story material: visible minority share, bachelor-or-higher education, mayoral competitiveness/fragmentation, household size, non-citizenship, recent immigration, low income, age structure, and selected service-contact measures.

## Section 9: Appendices

### Appendix A: Model Selection

{md_table(model_results_table(model_summary))}

### Appendix B: Component Family Themes

The appendix table below keeps the top three variable families for each cleaned PLS component. It shows which broad concept groups dominate each latent variable.

{md_table(theme[theme['model_key'].eq('theory_cleaned_pls')].groupby('component').head(3)[['component', 'family_label', 'family_loading_share', 'variables']].assign(component=lambda d: d['component'].map(component_label)).rename(columns={'component': 'Component', 'family_label': 'Variable family theme', 'family_loading_share': 'Share of absolute loading', 'variables': 'Representative variables'}))}

### Appendix C: Component Compositions

The appendix table below lists the top terms by absolute loading for each cleaned PLS component. These are the core empirical evidence behind the component names.

{md_table(composition[composition['model_key'].eq('theory_cleaned_pls') & composition['rank_abs_loading'].le(8)][['component', 'plain_variable', 'family', 'loading', 'vip', 'turnout_corr', 'direction']].assign(component=lambda d: d['component'].map(component_label), family=lambda d: d['family'].map(FAMILY_LABELS).fillna(d['family'])).rename(columns={'component': 'Component', 'plain_variable': 'Variable', 'family': 'Variable family', 'loading': 'Component loading', 'vip': 'VIP', 'turnout_corr': 'Bivariate turnout correlation', 'direction': 'PLS turnout direction'}))}

### Appendix D: Reference Geographies

The appendix table below gives near-zero reference CTs for the cleaned PLS components. These are useful as middle/reference cases when interpreting the high and low sides of each latent dimension.

{md_table(refs[refs['model_key'].eq('theory_cleaned_pls') & refs['reference_side'].eq('near_zero')][['component', 'geo_label', TARGET, 'component_reference_score', 'score_turnout_corr']].assign(component=lambda d: d['component'].map(component_label)).rename(columns={'component': 'Component', 'geo_label': 'Reference CT', TARGET: 'Mean turnout', 'component_reference_score': 'Reference score', 'score_turnout_corr': 'Component-turnout correlation'}))}

The complete CSV outputs remain available in the same folder for reproducibility, but the key report-facing selections are included directly above.

### Appendix E: Supervised PCA Comparison Tables

The table below lists the top supervised PCA component terms. These are included because the PCA comparison introduces or elevates several variables that are less central in the cleaned PLS narrative, especially KSI collisions, social housing, age, and provincial margin.

{md_table(pca_terms)}

### Appendix F: Important Cautions

- The component reference scores are interpretive projections from existing loadings. They are not new fitted latent models.
- PLS components are supervised by mean turnout, so they should be interpreted as turnout-oriented social-geographic dimensions.
- Some component signs are arbitrary. Interpret the high and low sides together rather than treating a positive loading as inherently good or bad.
- The analysis is ecological at the CT level. It should not be converted into claims about individual voters.
- Citizenship and turnout eligibility are central to interpretation; lower turnout associations in newcomer-heavy areas may reflect eligibility, settlement, mobilization, and institutional barriers.
"""
    (OUT / "latent_variable_interpretation_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    family_map = variable_family_map()
    model_summary = summarize_models()
    composition = component_composition(family_map)
    theme = family_theme_summary(composition)
    refs = reference_geographies(composition)
    sparse = sparse_summary(family_map)
    interactions = interaction_summary()

    model_summary.to_csv(OUT / "model_selection_summary.csv", index=False)
    composition.to_csv(OUT / "component_composition_all_terms.csv", index=False)
    composition[composition["rank_abs_loading"] <= 12].to_csv(
        OUT / "component_composition_top_terms.csv", index=False
    )
    theme.to_csv(OUT / "component_family_theme_summary.csv", index=False)
    refs.to_csv(OUT / "component_reference_geographies.csv", index=False)
    sparse.to_csv(OUT / "sparse_pls_variable_interpretation.csv", index=False)
    interactions.to_csv(OUT / "interaction_interpretation_summary.csv", index=False)
    write_report(model_summary, composition, theme, refs, sparse, interactions)
    write_comparison_report(model_summary, composition, theme, interactions)
    step_summary = f"""# Latent Interpretation Step Summary

1. Located existing outputs: found prior summaries, loadings, VIP tables, interaction screens, and PCA/sparse PLS comparison artifacts under `data/toronto_election_turnout/modelling/processed/dimension_reduction`.
2. Created structure: wrote this analysis to `data/toronto_election_turnout/modelling/processed/dimension_reduction/latent_interpretation` and the script to `analysis/toronto_election_turnout/modelling/dimension_reduction/latent_interpretation`.
3. Selected representatives: interaction-augmented PLS has the highest CV R2 ({model_summary.iloc[0]['cv_r2']:.3f}); theory-cleaned PLS is the main interpretation model because it is nearly as predictive and clearer; sparse PLS and supervised PCA are robustness/reference checks.
4. Interpreted latent compositions: Component 1 of cleaned PLS is the main turnout-resource/newcomer-fragmentation axis; Components 2-5 capture age/stability, urban form, service need, and secondary housing/service bundles.
5. Checked reference categories: high/low CT reference scores were generated from existing loadings and standardized existing predictors, not from newly trained models.
6. Compared model families: the same broad variables recur across PLS, sparse PLS, and PCA: visible minority share, bachelor-or-higher education, mayoral competitiveness, household size, non-citizenship, recent immigration, age, low income, and selected service-contact measures.
7. Interpreted interactions: the strongest interaction evidence concerns household/class variables with service-contact measures, especially low-income share times 311 requests per 1,000 residents.
8. Drafted main report: see `latent_variable_interpretation_report.md`.
9. Drafted benchmark comparison report: see `latent_model_comparison_report.md`.
"""
    (OUT / "analysis_step_summary.md").write_text(step_summary, encoding="utf-8")


if __name__ == "__main__":
    main()
