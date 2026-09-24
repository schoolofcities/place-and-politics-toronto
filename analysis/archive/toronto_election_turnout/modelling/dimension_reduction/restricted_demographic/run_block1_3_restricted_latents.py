"""Run and interpret Block 1-3 restricted latent models.

This is a separate follow-up workflow for the question: what do the turnout
latents look like when non-demographic/contextual predictors are omitted?
It leaves the original dimension-reduction artifacts untouched.
"""

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
OUT = DR_ROOT / "block1_3_restricted_latents"
FULL_ROOT = OUT / "full_block1_3_pls"
CLEAN_ROOT = OUT / "cleaned_block1_3_pls"
TARGET = wf.TARGET

BLOCK_LABELS = {
    "block_1_demographic": "Block 1: Demographic and Socioeconomic Composition",
    "block_2_housing_stability": "Block 2: Housing, Tenure, Built Form, and Stability",
    "block_3_immigration_eligibility": "Block 3: Immigration, Citizenship, Language, and Racialized Geography",
    "block1": "Block 1: Demographic and Socioeconomic Composition",
    "block2": "Block 2: Housing, Tenure, Built Form, and Stability",
    "block3": "Block 3: Immigration, Citizenship, Language, and Racialized Geography",
    "block_4_competitiveness": "Block 4: Electoral Competitiveness",
    "block_5_municipal_services": "Block 5: Transportation, Services, Access, and Local Need",
    "block4": "Block 4: Electoral Competitiveness",
    "block5": "Block 5: Transportation, Services, Access, and Local Need",
}

FAMILY_LABELS = {
    "age_structure": "Age structure",
    "household_class": "Education, income, and household class",
    "housing_tenure": "Renter/owner tenure",
    "residential_stability": "Residential stability",
    "housing_form_density": "Urban form and density",
    "immigration_citizenship": "Immigration, citizenship, language, and racialized geography",
    "mayoral_competitiveness": "Local mayoral competitiveness",
    "federal_competitiveness": "Federal competitiveness",
    "provincial_competitiveness": "Provincial competitiveness",
    "transportation_access": "Transportation access",
    "service_access": "Civic/service proximity",
    "service_contact": "Service contact and local need",
}

RESTRICTED_FAMILIES = {
    "age_structure",
    "household_class",
    "housing_tenure",
    "residential_stability",
    "housing_form_density",
    "immigration_citizenship",
}

COMPONENT_TITLES = {
    "component_1": "education and older-resource profile versus newcomer/citizenship/racialized household geography",
    "component_2": "dense renter/apartment urban form versus larger-household residential stability",
    "component_3": "older residential stability versus younger educated dense geography",
    "component_4": "dense educated mixed-newcomer geography versus older renter/lower-income contrast",
    "component_5": "renter/apartment lower-income profile versus older educated condo and citizenship contrast",
    "component_6": "condo/older profile versus renter dense-stability profile",
}

COMPONENT_NOTES = {
    "component_1": (
        "This is the main restricted-input turnout axis. The high side is anchored by bachelor-or-higher "
        "education and, more weakly, older age/condo context. The low side is anchored by visible minority "
        "share, non-citizenship, recent immigration, larger household size, low income, renter share, and "
        "younger age. Its reference scores line up strongly with mean turnout, so this component reproduces "
        "the earlier report's primary education/resource versus newcomer/citizenship-racialized geography "
        "without needing election or service variables."
    ),
    "component_2": (
        "This component is mainly an urban-form and tenure contrast. The high side combines apartments, "
        "density, renter share, low income, recent immigration, younger age, and non-citizenship. The low "
        "side is more strongly tied to five-year residential stability and larger household size. Because "
        "its direct component-turnout correlation is near zero, it is best read as a secondary geography "
        "that separates kinds of urban places rather than as a simple turnout gradient."
    ),
    "component_3": (
        "This component is the cleanest age/stability contrast in the restricted model. The high side is "
        "older and more residentially stable, with some low-income and renter/apartment signal; the low side "
        "is younger, more educated, more condo/dense, and somewhat more non-citizen/recent-immigrant. Its "
        "direct turnout relationship is weak, but it helps show that age and stability are not identical to "
        "the main education/newcomer axis."
    ),
    "component_4": (
        "This component mixes density and education with recent immigration and household size on one side, "
        "against older age, renter share, low income, and younger age on the other. It is not a clean "
        "high-turnout/low-turnout component. Its usefulness is interpretive: after the main demographic "
        "turnout axis, the model still separates different combinations of density, education, settlement, "
        "and household form."
    ),
    "component_5": (
        "This component contrasts a renter/apartment/lower-income profile with an opposite side containing "
        "older age, higher education, non-citizenship, visible minority share, condo share, and larger "
        "household size. The mixed signs show why later components need caution: they are not one-variable "
        "stories, but residual bundles left after Component 1 has already captured the strongest turnout "
        "gradient."
    ),
    "component_6": (
        "This component is mostly a housing-form contrast. The high side is dominated by condo share, older "
        "age, and some visible-minority/non-citizen signal; the low side is dominated by renter share, "
        "population density, five-year stability, recent immigration, and larger household size. It is "
        "useful mainly as a reminder that condo, renter, and density variables do not all describe the same "
        "kind of urban place."
    ),
}


def plain_name(variable: str) -> str:
    if variable in wf.PLAIN_VARIABLE_NAMES:
        return wf.PLAIN_VARIABLE_NAMES[variable]
    cleaned = re.sub(r"^block\d+_", "", variable)
    cleaned = cleaned.replace("_lim_at", "")
    cleaned = cleaned.replace("_5pct", " above five percent")
    cleaned = cleaned.replace("_25_64", " 25 to 64")
    cleaned = cleaned.replace("_18_34", " 18 to 34")
    cleaned = cleaned.replace("_35_64", " 35 to 64")
    cleaned = cleaned.replace("_65_plus", " 65 plus")
    cleaned = cleaned.replace("_5_17", " 5 to 17")
    cleaned = cleaned.replace("_per_1000", " per 1000")
    return cleaned.replace("_", " ")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    shown = df.copy()
    shown = shown.fillna("")
    columns = list(shown.columns)
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for _, row in shown.iterrows():
        values = [str(row[col]).replace("|", "/") for col in columns]
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, sep, *body])


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


def restricted_predictors(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    original = wf.predictor_universe(df)
    keep = [v for v in original if wf.variable_family(v) in RESTRICTED_FAMILIES]
    omit = [v for v in original if v not in set(keep)]
    return keep, omit


def readable_variable_table(variables: list[str]) -> pd.DataFrame:
    rows = []
    for var in variables:
        rows.append(
            {
                "Variable": plain_name(var),
                "Family": FAMILY_LABELS.get(wf.variable_family(var), wf.variable_family(var)),
                "Block": BLOCK_LABELS.get(wf.variable_block(var), wf.variable_block(var)),
            }
        )
    return pd.DataFrame(rows)


def component_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if re.fullmatch(r"component_\d+", c)]


def component_composition(loadings: pd.DataFrame, importance: pd.DataFrame) -> pd.DataFrame:
    rows = []
    importance_cols = ["variable", "vip", "pls_coefficient", "turnout_corr", "direction"]
    for comp in component_cols(loadings):
        tmp = loadings[["variable", comp]].rename(columns={comp: "loading"}).copy()
        tmp["component"] = comp
        tmp["abs_loading"] = tmp["loading"].abs()
        tmp["Variable"] = tmp["variable"].map(plain_name)
        tmp["Family"] = tmp["variable"].map(lambda v: FAMILY_LABELS.get(wf.variable_family(v), wf.variable_family(v)))
        tmp = tmp.merge(importance[importance_cols], on="variable", how="left")
        tmp["Component side"] = np.where(tmp["loading"] >= 0, "high side", "low side")
        tmp = tmp.sort_values("abs_loading", ascending=False)
        tmp["Rank"] = range(1, len(tmp) + 1)
        rows.append(tmp)
    return pd.concat(rows, ignore_index=True)


def family_theme_summary(composition: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        composition.groupby(["component", "Family"], as_index=False)
        .agg(
            abs_loading_sum=("abs_loading", "sum"),
            max_abs_loading=("abs_loading", "max"),
            variables=("Variable", lambda s: "; ".join(s.head(6))),
        )
        .sort_values(["component", "abs_loading_sum"], ascending=[True, False])
    )
    grouped["Share of absolute loading"] = grouped["abs_loading_sum"] / grouped.groupby("component")[
        "abs_loading_sum"
    ].transform("sum")
    return grouped


def component_reference_scores(df: pd.DataFrame, composition: pd.DataFrame) -> pd.DataFrame:
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
                "ct_id": df.get("ct_id", pd.Series(range(len(df)))),
                "ctuid": df.get("ctuid", pd.Series([""] * len(df))),
                "geo_name": df.get("geo_name", pd.Series([""] * len(df))),
                "component": comp,
                "Reference score": score,
                "Mean turnout": turnout,
                "Component-turnout correlation": corr,
            }
        )
        for side, sub in [
            ("high side", temp.sort_values("Reference score", ascending=False).head(5)),
            ("low side", temp.sort_values("Reference score", ascending=True).head(5)),
        ]:
            out = sub.copy()
            out["Reference side"] = side
            rows.append(out)
    return pd.concat(rows, ignore_index=True)


def clean_component_name(component: str, composition: pd.DataFrame) -> str:
    if component in COMPONENT_TITLES:
        return COMPONENT_TITLES[component]
    comp = composition[composition["component"].eq(component)].sort_values("abs_loading", ascending=False)
    pos = comp[comp["loading"] > 0]["Variable"].head(4).tolist()
    neg = comp[comp["loading"] < 0]["Variable"].head(4).tolist()
    return f"{'; '.join(pos)} versus {'; '.join(neg)}"


def component_interpretation(component: str, composition: pd.DataFrame, refs: pd.DataFrame) -> str:
    corr = refs[refs["component"].eq(component)]["Component-turnout correlation"].iloc[0]
    if component in COMPONENT_NOTES:
        return f"{COMPONENT_NOTES[component]} The projected component score has correlation {fmt(corr)} with mean turnout."
    comp = composition[composition["component"].eq(component)].sort_values("abs_loading", ascending=False)
    themes = family_theme_summary(composition)
    fam = themes[themes["component"].eq(component)].head(3)
    pos = comp[comp["loading"] > 0]["Variable"].head(5).tolist()
    neg = comp[comp["loading"] < 0]["Variable"].head(5).tolist()
    direction = "higher turnout" if corr > 0.20 else "lower turnout" if corr < -0.20 else "a weaker direct turnout pattern"
    family_text = "; ".join(f"{r['Family']} ({fmt(r['Share of absolute loading'])})" for _, r in fam.iterrows())
    return (
        f"The high side of this component is anchored by {', '.join(pos)}. "
        f"The low side is anchored by {', '.join(neg)}. The dominant variable families are {family_text}. "
        f"Its projected component score has correlation {fmt(corr)} with mean turnout, so it should be read as "
        f"{direction} rather than only as an abstract demographic contrast."
    )


def report_component_sections(composition: pd.DataFrame, refs: pd.DataFrame) -> str:
    sections = []
    for component in sorted(composition["component"].unique(), key=lambda c: int(c.split("_")[1])):
        title = clean_component_name(component, composition)
        top_terms = composition[composition["component"].eq(component)].head(10).copy()
        top_terms = top_terms[
            ["Variable", "Family", "Component side", "loading", "vip", "turnout_corr", "direction"]
        ].rename(
            columns={
                "loading": "Component loading",
                "vip": "VIP",
                "turnout_corr": "Bivariate turnout correlation",
                "direction": "PLS turnout direction",
            }
        )
        top_terms["Component loading"] = top_terms["Component loading"].map(fmt)
        top_terms["VIP"] = top_terms["VIP"].map(fmt)
        top_terms["Bivariate turnout correlation"] = top_terms["Bivariate turnout correlation"].map(fmt)
        ref = refs[refs["component"].eq(component)].copy()
        ref["Reference CT"] = ref["geo_name"].where(ref["geo_name"].astype(str).ne(""), ref["ctuid"])
        ref = ref[["Reference side", "Reference CT", "Mean turnout", "Reference score", "Component-turnout correlation"]]
        for col in ["Mean turnout", "Reference score", "Component-turnout correlation"]:
            ref[col] = ref[col].map(fmt)
        sections.append(
            f"""### {component.replace('_', ' ').title()}: {title}

**Interpretive summary.** {component_interpretation(component, composition, refs)}

Most influential variables:

{md_table(top_terms)}

Reference CTs:

{md_table(ref)}
"""
        )
    return "\n".join(sections)


def write_report(
    keep: list[str],
    omit: list[str],
    clean_predictors: list[str],
    full_summary: pd.DataFrame,
    clean_summary: pd.DataFrame,
    full_importance: pd.DataFrame,
    clean_importance: pd.DataFrame,
    composition: pd.DataFrame,
    refs: pd.DataFrame,
) -> None:
    old_summaries = {
        "Full original PLS": DR_ROOT / "full_pls/full_unfiltered_pls_summary.csv",
        "Theory-cleaned PLS": DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_summary.csv",
        "Interaction-augmented PLS": DR_ROOT / "interaction_discovery/interaction_augmented_pls_summary.csv",
        "Supervised PCA": DR_ROOT / "supervised_pca/supervised_pca_summary.csv",
    }
    rows = []
    for label, path in old_summaries.items():
        row = pd.read_csv(path).iloc[0]
        rows.append(
            {
                "Model": label,
                "Predictors": int(row.get("num_predictors", row.get("screened_predictor_count", 0))),
                "Components": int(row.get("selected_components", row.get("n_components", 0))),
                "CV R2": fmt(row["cv_r2"]),
                "CV RMSE": fmt(row["cv_rmse"]),
            }
        )
    for label, row in [
        ("Block 1-3 full PLS", full_summary.iloc[0]),
        ("Block 1-3 cleaned PLS", clean_summary.iloc[0]),
    ]:
        rows.append(
            {
                "Model": label,
                "Predictors": int(row["num_predictors"]),
                "Components": int(row["selected_components"]),
                "CV R2": fmt(row["cv_r2"]),
                "CV RMSE": fmt(row["cv_rmse"]),
            }
        )
    comparison = pd.DataFrame(rows)

    variable_keep = readable_variable_table(keep)
    variable_omit = readable_variable_table(omit)
    variable_clean = readable_variable_table(clean_predictors)
    for frame in [variable_keep, variable_omit, variable_clean]:
        frame.sort_values(["Block", "Family", "Variable"], inplace=True)

    top_clean = clean_importance.head(15).copy()
    top_clean["Variable"] = top_clean["variable"].map(plain_name)
    top_clean["Family"] = top_clean["family"].map(FAMILY_LABELS)
    top_clean = top_clean[["Variable", "Family", "vip", "turnout_corr", "direction"]].rename(
        columns={"vip": "VIP", "turnout_corr": "Bivariate turnout correlation", "direction": "PLS turnout direction"}
    )
    top_clean["VIP"] = top_clean["VIP"].map(fmt)
    top_clean["Bivariate turnout correlation"] = top_clean["Bivariate turnout correlation"].map(fmt)

    clean = clean_summary.iloc[0]
    full = full_summary.iloc[0]
    old_clean = pd.read_csv(DR_ROOT / "theory_cleaned_pls/theory_cleaned_pls_summary.csv").iloc[0]
    inter = pd.read_csv(DR_ROOT / "interaction_discovery/interaction_augmented_pls_summary.csv").iloc[0]

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
    for col in ["Component loading", "VIP", "Bivariate turnout correlation"]:
        appendix[col] = appendix[col].map(fmt)
    appendix["Component"] = appendix["Component"].str.replace("_", " ", regex=False).str.title()

    report = f"""# Block 1-3 Restricted Latent Variable Report: Mean Turnout

This report answers a follow-up question: what do the latent turnout components look like when the input set omits non-demographic/contextual variables and keeps only the approximate Block 1-3 predictors? The earlier latent report remains unchanged. This is a separate restricted-input analysis.

## Report Structure

**Section 1: Purpose and Input Restriction.** Defines the Block 1-3 restricted-input question and explains which kinds of non-demographic variables are omitted.

**Section 2: Variables Included and Omitted.** Lists the included Block 1-3 variables and the cleaned restricted PLS variables used for interpretation.

**Section 3: Restricted Model Summary.** Reports the restricted model fit and compares it with the earlier full, cleaned, interaction-augmented, and supervised PCA model summaries.

**Section 4: Restricted Latent Component Interpretation.** Interprets each cleaned Block 1-3 PLS component, including component sides, dominant variables, reference CTs, and turnout direction.

**Section 5: Comparison With the Previous Latent Report.** Explains what remains stable and what disappears when election, service, transportation, and civic-context variables are removed.

**Section 6: Suggested Takeaway.** Summarizes the restricted-input contribution to the broader turnout story.

**Appendix A: Full Component Loading Table.** Provides the complete cleaned restricted component loading table.

## Section 1: Purpose and Input Restriction

The restricted model keeps only the model-ready predictors from Blocks 1-3: demographic and socioeconomic composition; housing, tenure, built form, and residential stability; and immigration, citizenship, language, and racialized geography. It omits election competitiveness, service-contact, civic facility access, transportation/service access, road-safety, development, and other local-context variables.

This restriction is useful because it asks whether the main turnout story is already visible from demographic and housing composition alone. It also shows which parts of the previous latent report depended on non-demographic variables such as mayoral competition, federal/provincial margins, 311 requests, KSI collisions, development applications, and civic/service proximity.

## Section 2: Variables Included and Omitted

The original model-ready predictor universe contains 70 variables. The Block 1-3 restriction keeps {len(keep)} variables and omits {len(omit)} variables. From the kept variables, the cleaned restricted PLS uses {len(clean_predictors)} hand-picked representatives, following the same cleaned-model logic used in the earlier report.

### Included Block 1-3 Variables

{md_table(variable_keep)}

### Cleaned Restricted PLS Variables

{md_table(variable_clean)}

The omitted variables are not listed in this report to keep the focus on the restricted demographic/housing/immigration model. They are saved separately in `non_block1_3_omitted_predictors.csv` for audit purposes.

## Section 3: Restricted Model Summary

{md_table(comparison)}

The full Block 1-3 PLS uses all {len(keep)} restricted predictors and reaches `CV R2 {fmt(full['cv_r2'])}` with `CV RMSE {fmt(full['cv_rmse'])}`. The cleaned Block 1-3 PLS uses {len(clean_predictors)} interpretable representatives and reaches `CV R2 {fmt(clean['cv_r2'])}` with `CV RMSE {fmt(clean['cv_rmse'])}`. The performance is lower than the previous interaction-augmented benchmark (`CV R2 {fmt(inter['cv_r2'])}`), but it remains close enough to show that demographic, housing, and immigration/citizenship structure carries a large share of the turnout signal.

Most important cleaned restricted variables:

{md_table(top_clean)}

## Section 4: Restricted Latent Component Interpretation

The component interpretations below focus on the cleaned Block 1-3 PLS, because it is the most readable restricted-input model. As before, component signs are arbitrary; the interpretation should compare the two sides of each component rather than treating positive loadings as inherently good or negative loadings as inherently bad.

{report_component_sections(composition, refs)}

## Section 5: Comparison With the Previous Latent Report

The restricted analysis confirms the previous report's central demographic story. Even after removing election competitiveness, service-contact, civic access, transportation access, collisions, and development variables, the strongest remaining structure still separates education and older/stable or higher-resource CT profiles from newcomer/citizenship/racialized geography, larger households, renter/apartment urban form, and lower-income composition. This means the main education-versus-settlement/citizenship geography was not created by the non-demographic variables; it is already present inside Blocks 1-3.

The main difference is that the restricted model cannot express the earlier report's institutional and contextual layer. In the previous report, mayoral fragmentation and election margins helped connect social geography to electoral attachment. The interaction-augmented model also showed that service-contact variables, especially 311 requests, KSI collisions, and development applications, had conditional turnout meanings across different social geographies. Those mechanisms disappear by design here. The restricted model therefore gives a cleaner demographic map, but it gives a thinner civic-context story.

The restricted model also shifts more interpretive weight onto housing form, tenure, density, and residential stability. In the earlier cleaned PLS, these appeared as secondary dimensions after the main turnout-resource/newcomer-fragmentation axis. In the Block 1-3 version, they become more central because the model has no election or service variables available. This is helpful for showing that density and tenure are not just background controls: they are part of the compositional structure through which turnout differences appear.

The performance comparison is important but should not be overread. The restricted cleaned PLS (`CV R2 {fmt(clean['cv_r2'])}`) underperforms the earlier theory-cleaned PLS (`CV R2 {fmt(old_clean['cv_r2'])}`) and the interaction-augmented PLS (`CV R2 {fmt(inter['cv_r2'])}`). That drop is expected because the restricted model excludes predictive non-demographic information. Substantively, the finding is that demographics/housing/citizenship explain much of the turnout geography, while election context and service/contact variables add extra explanatory structure.

## Section 6: Suggested Takeaway

The Block 1-3 restricted model supports a cautious version of the original story: mean turnout is strongly structured by demographic and residential composition even before election competitiveness and service-contact variables are allowed into the model. The most stable latent contrast is a resource/education/stability side versus a newcomer/citizenship/racialized/larger-household side. This should be interpreted ecologically, not as an individual-level statement about voters.

The earlier full latent report remains the richer story because it adds the political and municipal-context layers. The restricted report shows the demographic foundation underneath that story. Together, they suggest that turnout differences are not simply about one variable such as education, immigration, age, or renter status. They are about overlapping social geographies, with non-demographic variables adding evidence about electoral attachment and local civic/service context.

## Appendix A: Full Component Loading Table

{md_table(appendix)}
"""
    (OUT / "block1_3_restricted_latent_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(wf.INPUT)
    keep, omit = restricted_predictors(df)
    pd.DataFrame({"variable": keep}).to_csv(OUT / "block1_3_predictor_universe.csv", index=False)
    pd.DataFrame({"variable": omit}).to_csv(OUT / "non_block1_3_omitted_predictors.csv", index=False)

    _, full_importance = wf.pls_outputs(df, keep, "block1_3_full_pls", FULL_ROOT)
    full_summary = pd.read_csv(FULL_ROOT / "block1_3_full_pls_summary.csv")

    existing_decisions = pd.read_csv(DR_ROOT / "theory_cleaned_pls/theory_cleaned_variable_decisions.csv")
    clean_predictors = [
        v
        for v in existing_decisions.loc[existing_decisions["selected"], "variable"].tolist()
        if v in set(keep)
    ]
    pd.DataFrame({"variable": clean_predictors}).to_csv(OUT / "block1_3_cleaned_predictors.csv", index=False)

    _, clean_importance = wf.pls_outputs(df, clean_predictors, "block1_3_cleaned_pls", CLEAN_ROOT)
    clean_summary = pd.read_csv(CLEAN_ROOT / "block1_3_cleaned_pls_summary.csv")
    clean_loadings = pd.read_csv(CLEAN_ROOT / "block1_3_cleaned_pls_component_loadings.csv")
    composition = component_composition(clean_loadings, clean_importance)
    composition.to_csv(OUT / "block1_3_cleaned_component_composition.csv", index=False)
    refs = component_reference_scores(df, composition)
    refs.to_csv(OUT / "block1_3_cleaned_component_reference_geographies.csv", index=False)

    write_report(
        keep,
        omit,
        clean_predictors,
        full_summary,
        clean_summary,
        full_importance,
        clean_importance,
        composition,
        refs,
    )


if __name__ == "__main__":
    main()
