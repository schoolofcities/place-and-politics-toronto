"""Run a meeting-specified PLS model and write a short component report."""

from __future__ import annotations

from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_ROOT = REPO_ROOT / "analysis/toronto_election_turnout/modelling/dimension_reduction/scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

import run_dimension_reduction_workflow as wf  # noqa: E402


DR_ROOT = REPO_ROOT / "data/toronto_election_turnout/modelling/processed/dimension_reduction"
OUT = DR_ROOT / "meeting_PLS"
MODEL_ROOT = OUT / "meeting_pls_model"
TARGET = wf.TARGET

MEETING_VARIABLES = [
    "block1_age_18_34_share",
    "block1_age_65_plus_share",
    "block1_average_household_size",
    "block1_bachelors_or_higher_25_64_share",
    "block1_low_income_lim_at_share",
    "block2_renter_share",
    "block2_same_address_5yr_share",
    "block2_apartment_share",
    "block2_condo_share",
    "block2_population_density_per_km2",
    "block3_citizen_adult_share",
    "block3_immigrant_share",
    "block3_visible_minority_share",
    "block5_tts_no_car_household_share",
]

FAMILY_LABELS = {
    "age_structure": "Age structure",
    "household_class": "Education, income, and household",
    "housing_tenure": "Tenure",
    "residential_stability": "Residential stability",
    "housing_form_density": "Urban form",
    "immigration_citizenship": "Immigration and citizenship",
    "transportation_access": "Transportation",
}

COMPONENT_TITLES = {
    "component_1": "education/resource attachment versus racialized-immigrant household geography",
    "component_2": "older residential stability versus younger no-car renter/density geography",
    "component_3": "older stability versus younger educated condo geography",
    "component_4": "condo/educated density versus renter/low-income apartment profile",
    "component_5": "citizenship/visibility contrast within housing-form geography",
    "component_6": "transportation and residual housing-form contrast",
}


def plain_name(variable: str) -> str:
    if variable in wf.PLAIN_VARIABLE_NAMES:
        return wf.PLAIN_VARIABLE_NAMES[variable]
    cleaned = re.sub(r"^block\d+_", "", variable)
    cleaned = cleaned.replace("_lim_at", "")
    cleaned = cleaned.replace("_25_64", " 25 to 64")
    cleaned = cleaned.replace("_18_34", " 18 to 34")
    cleaned = cleaned.replace("_65_plus", " 65 plus")
    cleaned = cleaned.replace("_per_1000", " per 1000")
    return cleaned.replace("_", " ")


def fmt(value: float | int | str | None, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if not np.isfinite(float(value)):
        return ""
    return f"{float(value):.{digits}f}"


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    shown = df.fillna("").copy()
    columns = list(shown.columns)
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in shown.iterrows():
        values = [str(row[col]).replace("|", "/") for col in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep, *rows])


def component_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if re.fullmatch(r"component_\d+", c)]


def component_composition(loadings: pd.DataFrame, importance: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for comp in component_cols(loadings):
        tmp = loadings[["variable", comp]].rename(columns={comp: "loading"}).copy()
        tmp["component"] = comp
        tmp["abs_loading"] = tmp["loading"].abs()
        tmp["Variable"] = tmp["variable"].map(plain_name)
        tmp["Family"] = tmp["variable"].map(lambda v: FAMILY_LABELS.get(wf.variable_family(v), wf.variable_family(v)))
        tmp = tmp.merge(
            importance[["variable", "vip", "pls_coefficient", "turnout_corr", "direction"]],
            on="variable",
            how="left",
        )
        tmp["Component side"] = np.where(tmp["loading"] >= 0, "high side", "low side")
        tmp = tmp.sort_values("abs_loading", ascending=False)
        tmp["Rank"] = range(1, len(tmp) + 1)
        rows.append(tmp)
    return pd.concat(rows, ignore_index=True)


def reference_scores(df: pd.DataFrame, composition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for comp, group in composition.groupby("component"):
        variables = group["variable"].tolist()
        weights = group.set_index("variable")["loading"].astype(float)
        x = df[variables].apply(pd.to_numeric, errors="coerce")
        z = (x - x.mean()) / x.std(ddof=0)
        score = z.fillna(0).to_numpy() @ weights.loc[variables].to_numpy()
        turnout = pd.to_numeric(df[TARGET], errors="coerce")
        corr = float(np.corrcoef(score, turnout)[0, 1])
        temp = pd.DataFrame(
            {
                "Reference CT": df.get("geo_name", pd.Series(range(len(df)))),
                "component": comp,
                "Reference score": score,
                "Mean turnout": turnout,
                "Component-turnout correlation": corr,
            }
        )
        rows.append(temp.sort_values("Reference score", ascending=False).head(3).assign(Reference_side="high side"))
        rows.append(temp.sort_values("Reference score", ascending=True).head(3).assign(Reference_side="low side"))
    return pd.concat(rows, ignore_index=True)


def component_title(component: str, comp: pd.DataFrame) -> str:
    if component in COMPONENT_TITLES:
        return COMPONENT_TITLES[component]
    pos = comp[comp["loading"] > 0]["Variable"].head(3).tolist()
    neg = comp[comp["loading"] < 0]["Variable"].head(3).tolist()
    return f"{'; '.join(pos)} versus {'; '.join(neg)}"


def component_summary(component: str, composition: pd.DataFrame, refs: pd.DataFrame) -> str:
    comp = composition[composition["component"].eq(component)].sort_values("abs_loading", ascending=False)
    pos = comp[comp["loading"] > 0]["Variable"].head(5).tolist()
    neg = comp[comp["loading"] < 0]["Variable"].head(5).tolist()
    corr = refs[refs["component"].eq(component)]["Component-turnout correlation"].iloc[0]
    direction = "a direct higher-turnout axis" if corr > 0.20 else "a direct lower-turnout axis" if corr < -0.20 else "a secondary social-geographic contrast"
    return (
        f"The high side is anchored by {', '.join(pos)}. The low side is anchored by {', '.join(neg)}. "
        f"The projected component score correlates {fmt(corr)} with mean turnout, so this component is best read as {direction}."
    )


def variable_table(predictors: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Variable": plain_name(v),
                "Family": FAMILY_LABELS.get(wf.variable_family(v), wf.variable_family(v)),
                "Model column": v,
            }
            for v in predictors
        ]
    )


def report_sections(composition: pd.DataFrame, refs: pd.DataFrame) -> str:
    sections = []
    for component in sorted(composition["component"].unique(), key=lambda c: int(c.split("_")[1])):
        comp = composition[composition["component"].eq(component)].copy()
        top = comp.head(10)[["Variable", "Family", "Component side", "loading", "vip", "turnout_corr", "direction"]]
        top = top.rename(
            columns={
                "loading": "Component loading",
                "vip": "VIP",
                "turnout_corr": "Bivariate turnout correlation",
                "direction": "PLS turnout direction",
            }
        )
        for col in ["Component loading", "VIP", "Bivariate turnout correlation"]:
            top[col] = top[col].map(fmt)
        ref = refs[refs["component"].eq(component)].copy()
        ref = ref.rename(columns={"Reference_side": "Reference side"})
        ref = ref[["Reference side", "Reference CT", "Mean turnout", "Reference score", "Component-turnout correlation"]]
        for col in ["Mean turnout", "Reference score", "Component-turnout correlation"]:
            ref[col] = ref[col].map(fmt)
        sections.append(
            f"""### {component.replace('_', ' ').title()}: {component_title(component, comp)}

**Interpretive summary.** {component_summary(component, composition, refs)}

{md_table(top)}

Reference CTs:

{md_table(ref)}
"""
        )
    return "\n".join(sections)


def write_report(
    predictors: list[str],
    summary: pd.DataFrame,
    importance: pd.DataFrame,
    composition: pd.DataFrame,
    refs: pd.DataFrame,
) -> None:
    s = summary.iloc[0]
    top_importance = importance.head(14).copy()
    top_importance["Variable"] = top_importance["variable"].map(plain_name)
    top_importance["Family"] = top_importance["family"].map(lambda f: FAMILY_LABELS.get(f, f))
    top_importance = top_importance[["Variable", "Family", "vip", "turnout_corr", "direction"]].rename(
        columns={"vip": "VIP", "turnout_corr": "Bivariate turnout correlation", "direction": "PLS turnout direction"}
    )
    for col in ["VIP", "Bivariate turnout correlation"]:
        top_importance[col] = top_importance[col].map(fmt)

    appendix = composition[
        ["component", "Variable", "Family", "Component side", "loading", "vip", "turnout_corr", "direction"]
    ].rename(
        columns={
            "component": "Component",
            "loading": "Component loading",
            "vip": "VIP",
            "turnout_corr": "Bivariate turnout correlation",
            "direction": "PLS turnout direction",
        }
    )
    appendix["Component"] = appendix["Component"].str.replace("_", " ", regex=False).str.title()
    for col in ["Component loading", "VIP", "Bivariate turnout correlation"]:
        appendix[col] = appendix[col].map(fmt)

    report = f"""# Meeting PLS Report: Mean Turnout

This report fits a meeting-specified PLS model using 14 selected predictors across age, education/income/household, tenure, residential stability, urban form, immigration/citizenship, and transportation. The outcome is mean CT turnout (`{TARGET}`).

## Report Structure

**Section 1: Model Input.** Lists the exact meeting-specified variables used in the model.

**Section 2: Model Results.** Reports predictive fit, selected component count, and the most important variables by VIP.

**Section 3: Component Interpretation.** Interprets each retained PLS component as a latent social-geographic contrast.

**Section 4: Short Takeaway.** Summarizes what this compact meeting PLS adds to the earlier latent reports.

**Appendix A: Full Component Loading Table.** Provides all component loadings for audit.

## Section 1: Model Input

The model uses {len(predictors)} predictors:

{md_table(variable_table(predictors))}

## Section 2: Model Results

| Model | Observations | Predictors | Components | Train R2 | CV R2 | CV RMSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Meeting PLS | {int(s['n'])} | {int(s['num_predictors'])} | {int(s['selected_components'])} | {fmt(s['train_r2'])} | {fmt(s['cv_r2'])} | {fmt(s['cv_rmse'])} |

The meeting PLS selects {int(s['selected_components'])} components by cross-validation. Its cross-validated R2 is `{fmt(s['cv_r2'])}`, with cross-validated RMSE `{fmt(s['cv_rmse'])}`. This is a compact model, so the useful question is less whether it beats the larger models and more whether it preserves the main interpretable turnout axes.

Most important variables:

{md_table(top_importance)}

## Section 3: Component Interpretation

{report_sections(composition, refs)}

## Section 4: Short Takeaway

The meeting PLS keeps the main demographic story visible in a smaller, more directed variable set. The strongest component again separates education/resource variables from visible-minority, immigrant, larger-household, renter, and lower-income geography. This supports the earlier interpretation that the main turnout pattern is not dependent on service or election-context variables alone.

The second component mostly separates age, stability, tenure, density, and no-car/transportation context. It is useful as descriptive geography, but only the first component should be read as a strong direct turnout gradient. The compact variable list therefore gives a clean meeting-friendly version of the broader latent story: turnout is structured by overlapping education/class, settlement/citizenship, household, tenure, density, and transportation geographies.

## Appendix A: Full Component Loading Table

{md_table(appendix)}
"""
    (OUT / "meeting_pls_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(wf.INPUT)
    missing = [v for v in MEETING_VARIABLES if v not in df.columns]
    if missing:
        raise ValueError(f"Missing meeting variables: {missing}")
    pd.DataFrame({"variable": MEETING_VARIABLES}).to_csv(OUT / "meeting_pls_predictors.csv", index=False)
    _, importance = wf.pls_outputs(df, MEETING_VARIABLES, "meeting_pls", MODEL_ROOT)
    summary = pd.read_csv(MODEL_ROOT / "meeting_pls_summary.csv")
    loadings = pd.read_csv(MODEL_ROOT / "meeting_pls_component_loadings.csv")
    composition = component_composition(loadings, importance)
    composition.to_csv(OUT / "meeting_pls_component_composition.csv", index=False)
    refs = reference_scores(df, composition)
    refs.to_csv(OUT / "meeting_pls_component_reference_geographies.csv", index=False)
    write_report(MEETING_VARIABLES, summary, importance, composition, refs)


if __name__ == "__main__":
    main()
