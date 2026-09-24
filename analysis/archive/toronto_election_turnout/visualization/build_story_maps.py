#!/usr/bin/env python3
"""Build the retained Toronto census-tract story maps from saved outputs.

This script is collection/visualization only: it does not fit or tune models.
SVGs are written to the final visual release folder. Optional PNG previews are
for visual QA only and are not release artifacts.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path

# Keep Matplotlib's generated cache outside the repository and user home.
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "toronto_ct_matplotlib_cache"))

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Polygon
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
FINAL_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "final"
OUTPUT_DIR = FINAL_ROOT / "visuals"

CT_GEOJSON = FINAL_ROOT / "geography" / "toronto_ct_2021_geography.geojson"
WARD_GEOJSON = REPO_ROOT / "src" / "data" / "wards.geo.json"
OBSERVED_CSV = FINAL_ROOT / "observed" / "toronto_ct_2021_observed_variables.csv"
MEETING_CSV = FINAL_ROOT / "meeting_pls" / "toronto_ct_meeting_pls.csv"
LOADINGS_CSV = FINAL_ROOT / "model_definitions" / "toronto_turnout_component_loadings.csv"
VIP_CSV = FINAL_ROOT / "model_definitions" / "toronto_turnout_variable_importance.csv"
MODEL_RESULTS_CSV = FINAL_ROOT / "modelled" / "toronto_ct_turnout_model_results.csv"

BRAND_DARK_BLUE = "#1E3765"
BRAND_MED_BLUE = "#007FA3"
BRAND_LIGHT_BLUE = "#6FC7EA"
BRAND_RED = "#DC4633"
BRAND_ORANGE = "#EBA00F"
BRAND_GRAY = "#D0D1C9"
BRAND_GRAY_50 = "#858585"
BRAND_GRAY_70 = "#4D4D4D"
BRAND_GRAY_90 = "#191919"
WHITE = "#FFFFFF"

# ColorBrewer RdBu-inspired, color-blind legible diverging colors.
DIVERGING_5 = ["#B2182B", "#EF8A62", "#F7F7F7", "#67A9CF", "#2166AC"]
DIVERGING_6 = ["#B2182B", "#D6604D", "#F4A582", "#92C5DE", "#4393C3", "#2166AC"]
SEQUENTIAL_5 = ["#F7FCFD", "#CCECE6", "#66C2A4", "#238B8E", "#005824"]

OUTCOMES = ["municipal", "provincial", "federal"]
OUTCOME_LABELS = {
    "mean": "Three-election mean",
    "municipal": "Municipal",
    "provincial": "Provincial",
    "federal": "Federal",
}
IMPUTED_CT_IDS = {"5350006.00", "5350205.00"}


def configure_style() -> None:
    """Register repository fonts and configure deterministic SVG output."""
    font_dir = REPO_ROOT / "src" / "assets" / "fonts"
    for path in sorted(font_dir.iterdir()):
        try:
            mpl.font_manager.fontManager.addfont(path)
        except RuntimeError:
            pass
    mpl.rcParams.update(
        {
            "font.family": "Open Sans",
            "font.size": 9.5,
            "text.color": BRAND_GRAY_90,
            "axes.labelcolor": BRAND_GRAY_70,
            "axes.edgecolor": BRAND_GRAY,
            "axes.titleweight": "normal",
            "axes.titlesize": 12,
            "axes.titlepad": 8,
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "svg.fonttype": "none",
            "svg.hashsalt": "toronto-ct-story-maps-v1",
        }
    )


def load_geojson(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def exterior_rings(geometry: dict):
    """Yield polygon exterior rings from Polygon or MultiPolygon geometry."""
    if geometry["type"] == "Polygon":
        yield geometry["coordinates"][0]
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield polygon[0]
    else:
        raise ValueError(f"Unsupported geometry type: {geometry['type']}")


def geometry_bounds(features: list[dict]) -> tuple[float, float, float, float]:
    xs, ys = [], []
    for feature in features:
        for ring in exterior_rings(feature["geometry"]):
            for x, y in ring:
                xs.append(x)
                ys.append(y)
    return min(xs), max(xs), min(ys), max(ys)


def normalize_ct_id(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip()


def load_inputs():
    ct_geo = load_geojson(CT_GEOJSON)
    wards_geo = load_geojson(WARD_GEOJSON)
    observed = pd.read_csv(OBSERVED_CSV, dtype={"ct_id": str})
    meeting = pd.read_csv(MEETING_CSV, dtype={"ct_id": str})
    model_results = pd.read_csv(MODEL_RESULTS_CSV, dtype={"ct_id": str})
    loadings = pd.read_csv(LOADINGS_CSV)
    vip = pd.read_csv(VIP_CSV)
    for frame in (observed, meeting, model_results):
        frame["ct_id"] = normalize_ct_id(frame["ct_id"])
    ct_ids = {str(f["properties"]["ct_id"]) for f in ct_geo["features"]}
    for name, frame in (("observed", observed), ("meeting", meeting), ("model_results", model_results)):
        if len(frame) != 585 or frame["ct_id"].nunique() != 585:
            raise ValueError(f"{name} must contain 585 unique CT rows")
        if set(frame["ct_id"]) != ct_ids:
            raise ValueError(f"{name} CT universe differs from canonical geometry")
    return ct_geo, wards_geo, observed, meeting, model_results, loadings, vip


def classify(value: float, breaks: list[float], colors: list[str], missing=BRAND_GRAY) -> str:
    if value is None or not np.isfinite(value):
        return missing
    return colors[int(np.digitize(value, breaks, right=True))]


def draw_map(
    ax,
    ct_geo: dict,
    wards_geo: dict,
    values: dict[str, float],
    breaks: list[float],
    colors: list[str],
    *,
    diagnostic_ids: set[str] | None = None,
    hatched_ids: set[str] | None = None,
    missing_ids: set[str] | None = None,
) -> None:
    diagnostic_ids = diagnostic_ids or set()
    hatched_ids = hatched_ids or set()
    missing_ids = missing_ids or set()
    for feature in ct_geo["features"]:
        ct_id = str(feature["properties"]["ct_id"])
        color = classify(values.get(ct_id, np.nan), breaks, colors)
        if ct_id in missing_ids:
            color = BRAND_GRAY
        for ring in exterior_rings(feature["geometry"]):
            ax.add_patch(
                Polygon(
                    ring,
                    closed=True,
                    facecolor=color,
                    edgecolor=WHITE,
                    linewidth=0.18,
                    alpha=1.0,
                    joinstyle="round",
                    zorder=1,
                )
            )
    if hatched_ids:
        for feature in ct_geo["features"]:
            ct_id = str(feature["properties"]["ct_id"])
            if ct_id not in hatched_ids:
                continue
            for ring in exterior_rings(feature["geometry"]):
                ax.add_patch(
                    Polygon(
                        ring,
                        closed=True,
                        facecolor="none",
                        edgecolor=BRAND_GRAY_70,
                        linewidth=0.0,
                        hatch="///",
                        zorder=2,
                    )
                )
    for feature in wards_geo["features"]:
        for ring in exterior_rings(feature["geometry"]):
            ax.add_patch(
                Polygon(
                    ring,
                    closed=True,
                    facecolor="none",
                    edgecolor=BRAND_GRAY_50,
                    linewidth=0.45,
                    alpha=0.65,
                    joinstyle="round",
                    zorder=3,
                )
            )
    if diagnostic_ids:
        for feature in ct_geo["features"]:
            ct_id = str(feature["properties"]["ct_id"])
            if ct_id not in diagnostic_ids:
                continue
            for ring in exterior_rings(feature["geometry"]):
                ax.add_patch(
                    Polygon(
                        ring,
                        closed=True,
                        facecolor="none",
                        edgecolor=BRAND_GRAY_90,
                        linewidth=1.15,
                        zorder=5,
                    )
                )
    xmin, xmax, ymin, ymax = geometry_bounds(ct_geo["features"])
    xpad, ypad = (xmax - xmin) * 0.012, (ymax - ymin) * 0.02
    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)
    ax.set_aspect(1.0 / math.cos(math.radians((ymin + ymax) / 2)))
    ax.axis("off")


def add_panel_label(ax, label: str) -> None:
    ax.text(
        0,
        1.03,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontfamily="TradeGothic LT Bold",
        fontsize=12,
        color=BRAND_GRAY_90,
    )


def add_figure_header(fig, title: str, subtitle: str) -> None:
    fig.text(
        0.04,
        0.965,
        title,
        ha="left",
        va="top",
        fontfamily="TradeGothic LT Bold",
        fontsize=21,
        color=BRAND_GRAY_90,
    )
    fig.text(
        0.04,
        0.91,
        subtitle,
        ha="left",
        va="top",
        fontfamily="Source Serif Pro",
        fontsize=10.3,
        color=BRAND_GRAY_70,
    )


def add_footer(fig, text: str, *, y: float = 0.026) -> None:
    fig.text(
        0.04,
        y,
        text,
        ha="left",
        va="bottom",
        fontsize=7.2,
        color=BRAND_GRAY_70,
        linespacing=1.35,
    )


def add_swatch_legend(fig, colors, labels, *, x=0.04, y=0.105, ncol=None) -> None:
    handles = [Patch(facecolor=c, edgecolor=BRAND_GRAY, linewidth=0.35, label=l) for c, l in zip(colors, labels)]
    fig.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(x, y),
        frameon=False,
        ncol=ncol or len(handles),
        handlelength=1.5,
        handleheight=0.9,
        columnspacing=1.05,
        handletextpad=0.45,
        fontsize=8.2,
    )


def save_figure(fig, filename: str, preview_dir: Path | None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = OUTPUT_DIR / filename
    metadata = {"Date": None, "Creator": "build_story_maps.py"}
    fig.savefig(svg_path, format="svg", metadata=metadata)
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        png_path = preview_dir / filename.replace(".svg", ".png")
        fig.savefig(png_path, format="png", dpi=180, metadata={"Software": "build_story_maps.py"})
    plt.close(fig)


def build_figure_01(ct_geo, wards_geo, observed, preview_dir: Path | None) -> None:
    values_by_outcome = {}
    city_rates = {}
    weight = observed["citizen_canadian_18plus_count"]
    for outcome in OUTCOMES:
        col = f"outcome_{outcome}_participation_citizen_18plus"
        valid = observed[col].notna() & weight.notna() & (weight > 0)
        city_rates[outcome] = np.average(observed.loc[valid, col], weights=weight.loc[valid])
        values_by_outcome[outcome] = dict(
            zip(observed["ct_id"], (observed[col] - city_rates[outcome]) * 100)
        )
    federal_diagnostic = set(
        observed.loc[observed["outcome_federal_participation_citizen_18plus"] > 1, "ct_id"]
    )
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.75))
    fig.subplots_adjust(left=0.035, right=0.985, top=0.79, bottom=0.19, wspace=0.035)
    add_figure_header(
        fig,
        "Participation geography persists across election levels",
        "Each tract is measured against its election’s citizen-18+-weighted Toronto rate; the shared scale makes local gaps directly comparable.",
    )
    for ax, outcome in zip(axes, OUTCOMES):
        diagnostic = federal_diagnostic if outcome == "federal" else set()
        draw_map(
            ax,
            ct_geo,
            wards_geo,
            values_by_outcome[outcome],
            [-10, -5, 5, 10],
            DIVERGING_5,
            diagnostic_ids=diagnostic,
        )
        add_panel_label(ax, f"{OUTCOME_LABELS[outcome]}  ·  Toronto {city_rates[outcome] * 100:.1f}%")
    labels = ["≤ −10", "−10 to −5", "−5 to +5", "+5 to +10", "> +10 pp"]
    add_swatch_legend(fig, DIVERGING_5, labels, y=0.09)
    extra = [
        Patch(facecolor=BRAND_GRAY, edgecolor=BRAND_GRAY, label="No observed outcome"),
        Patch(facecolor="none", edgecolor=BRAND_GRAY_90, linewidth=1.15, label="Federal ratio > 1 (diagnostic)"),
    ]
    fig.legend(handles=extra, loc="lower right", bbox_to_anchor=(0.975, 0.095), frameon=False, ncol=2, fontsize=8.2)
    add_footer(
        fig,
        "Notes: Participation is estimated votes divided by the 2021 Census citizen population age 18+. Two tracts lack observed outcomes and appear gray.\n"
        "Federal ratios above 1 are retained but outlined because interpolated votes can exceed the census denominator. Ward lines provide orientation.\n"
        "Sources: final observed CT variables; canonical 2021 CT geometry; City of Toronto ward geometry.",
    )
    save_figure(fig, "figure_01_cross_election_participation.svg", preview_dir)


def build_figure_02(ct_geo, wards_geo, observed, preview_dir: Path | None) -> None:
    weights = observed["citizen_canadian_18plus_count"]
    deviations = {}
    zscores = {}
    for outcome in OUTCOMES:
        col = f"outcome_{outcome}_participation_citizen_18plus"
        valid = observed[col].notna() & weights.notna() & (weights > 0)
        center = np.average(observed.loc[valid, col], weights=weights.loc[valid])
        deviations[outcome] = (observed[col] - center) * 100
        zscores[outcome] = (observed[col] - observed.loc[valid, col].mean()) / observed.loc[valid, col].std(ddof=0)
    prov_minus_muni = deviations["provincial"] - deviations["municipal"]
    fed_minus_prov = deviations["federal"] - deviations["provincial"]
    z_matrix = np.column_stack([zscores[o] for o in OUTCOMES])
    instability = np.full(len(observed), np.nan)
    has_all_outcomes = np.all(np.isfinite(z_matrix), axis=1)
    instability[has_all_outcomes] = np.ptp(z_matrix[has_all_outcomes], axis=1)
    panels = [
        (dict(zip(observed["ct_id"], prov_minus_muni)), [-15, -7.5, 7.5, 15], DIVERGING_5),
        (dict(zip(observed["ct_id"], fed_minus_prov)), [-15, -7.5, 7.5, 15], DIVERGING_5),
        (dict(zip(observed["ct_id"], instability)), [0.5, 1.0, 1.5, 2.0], SEQUENTIAL_5),
    ]
    federal_diagnostic = set(
        observed.loc[observed["outcome_federal_participation_citizen_18plus"] > 1, "ct_id"]
    )
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.75))
    fig.subplots_adjust(left=0.035, right=0.985, top=0.79, bottom=0.19, wspace=0.035)
    add_figure_header(
        fig,
        "A minority of tracts changes position sharply between elections",
        "The first two maps remove each election’s Toronto baseline; the third measures how far a tract moves across the three election-specific distributions.",
    )
    titles = [
        "Provincial minus municipal gap",
        "Federal minus provincial gap",
        "Cross-election instability",
    ]
    for i, (ax, (values, breaks, colors), title) in enumerate(zip(axes, panels, titles)):
        draw_map(
            ax,
            ct_geo,
            wards_geo,
            values,
            breaks,
            colors,
            diagnostic_ids=federal_diagnostic if i in (1, 2) else set(),
        )
        add_panel_label(ax, title)
    diff_labels = ["≤ −15", "−15 to −7.5", "−7.5 to +7.5", "+7.5 to +15", "> +15 pp"]
    add_swatch_legend(fig, DIVERGING_5, diff_labels, x=0.035, y=0.105)
    instability_handles = [
        Patch(facecolor=c, edgecolor=BRAND_GRAY, linewidth=0.35, label=l)
        for c, l in zip(SEQUENTIAL_5, ["≤ 0.5", "0.5–1.0", "1.0–1.5", "1.5–2.0", "> 2.0 SD"])
    ]
    axes[2].legend(
        handles=instability_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        frameon=False,
        ncol=5,
        handlelength=1.1,
        handletextpad=0.3,
        columnspacing=0.55,
        fontsize=7.3,
    )
    add_footer(
        fig,
        "Notes: Difference maps compare deviations from the citizen-18+-weighted Toronto rate, so zero means the tract keeps the same relative position.\n"
        "Instability is the range of municipal, provincial, and federal within-election z-scores. Two missing outcomes are gray; federal ratios above 1 are outlined.\n"
        "Sources: final observed CT variables; canonical 2021 CT geometry; City of Toronto ward geometry.",
    )
    save_figure(fig, "figure_02_cross_election_instability.svg", preview_dir)


VARIABLE_LABELS = {
    "block1_age_18_34_share": "Age 18–34 share",
    "block1_age_65_plus_share": "Age 65+ share",
    "block1_average_household_size": "Average household size",
    "block1_bachelors_or_higher_25_64_share": "Bachelor’s+ (age 25–64)",
    "block1_low_income_lim_at_share": "Low-income share",
    "block2_renter_share": "Renter share",
    "block2_same_address_5yr_share": "Same address 5 years",
    "block2_apartment_share": "Apartment share",
    "block2_condo_share": "Condo share",
    "block2_population_density_per_km2": "Population density",
    "block3_citizen_adult_share": "Citizen share, age 18+",
    "block3_immigrant_share": "Immigrant share",
    "block3_visible_minority_share": "Visible-minority share",
    "block5_tts_no_car_household_share": "No-car household share",
}


def build_figure_03(ct_geo, wards_geo, meeting, loadings, vip, preview_dir: Path | None) -> None:
    score_col = "meeting_mean_pls_component_1_score"
    score = (meeting[score_col] - meeting[score_col].mean()) / meeting[score_col].std(ddof=0)
    score_values = dict(zip(meeting["ct_id"], score))
    comp = loadings.loc[
        (loadings["model_id"] == "meeting_mean_pls") & (loadings["component"] == "component_1"),
        ["variable", "loading"],
    ].copy()
    comp = comp.merge(
        vip.loc[vip["model_id"] == "meeting_mean_pls", ["variable", "vip"]],
        on="variable",
        how="left",
        validate="one_to_one",
    )
    comp["label"] = comp["variable"].map(VARIABLE_LABELS).fillna(comp["variable"])
    comp = comp.sort_values("loading")

    fig = plt.figure(figsize=(13.2, 6.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.28, 1], left=0.04, right=0.97, top=0.80, bottom=0.17, wspace=0.12)
    map_ax = fig.add_subplot(gs[0, 0])
    load_ax = fig.add_subplot(gs[0, 1])
    add_figure_header(
        fig,
        "The three-election-mean PLS component separates recurring tract profiles",
        "The map shows standardized component scores; the loading plot defines the two sides without treating either profile as intrinsically better.",
    )
    draw_map(
        map_ax,
        ct_geo,
        wards_geo,
        score_values,
        [-1.5, -0.5, 0.5, 1.5],
        DIVERGING_5,
    )
    add_panel_label(map_ax, "Component 1 score (standard deviations)")

    y = np.arange(len(comp))
    bar_colors = [DIVERGING_5[0] if x < 0 else DIVERGING_5[-1] for x in comp["loading"]]
    load_ax.barh(y, comp["loading"], height=0.62, color=bar_colors, alpha=0.88, zorder=2)
    sizes = 18 + 34 * np.clip(comp["vip"].to_numpy(), 0, 2.0)
    load_ax.scatter(comp["loading"], y, s=sizes, facecolor=WHITE, edgecolor=BRAND_GRAY_90, linewidth=0.7, zorder=3)
    load_ax.axvline(0, color=BRAND_GRAY_50, linewidth=0.8, zorder=1)
    load_ax.set_yticks(y, comp["label"])
    load_ax.set_xlim(-0.60, 0.52)
    load_ax.set_xlabel("Signed component loading")
    load_ax.set_ylim(-0.6, len(comp) + 0.35)
    load_ax.set_title("Variables defining the component", loc="left", fontfamily="TradeGothic LT Bold", pad=13)
    load_ax.grid(axis="x", color=BRAND_GRAY, linewidth=0.45, alpha=0.7)
    load_ax.spines[["top", "right", "left"]].set_visible(False)
    load_ax.tick_params(axis="y", length=0, labelsize=8.1)
    load_ax.tick_params(axis="x", labelsize=8)
    load_ax.text(0.01, 0.985, "LOW-SCORE SIDE", transform=load_ax.transAxes, ha="left", va="top", fontsize=7.3, color=DIVERGING_5[0])
    load_ax.text(0.99, 0.985, "HIGH-SCORE SIDE", transform=load_ax.transAxes, ha="right", va="top", fontsize=7.3, color=DIVERGING_5[-1])
    for threshold, label in [(1.0, "VIP 1.0"), (2.0, "VIP 2.0")]:
        load_ax.scatter([], [], s=18 + 34 * threshold, facecolor=WHITE, edgecolor=BRAND_GRAY_90, linewidth=0.7, label=label)
    load_ax.legend(loc="lower right", frameon=False, fontsize=8, title="Point size", title_fontsize=8)
    add_swatch_legend(fig, DIVERGING_5, ["≤ −1.5", "−1.5 to −0.5", "−0.5 to +0.5", "+0.5 to +1.5", "> +1.5 SD"], y=0.087)
    add_footer(
        fig,
        "Notes: Scores are standardized across 585 tracts for display. Bars are saved PLS component-1 loadings; point size is saved VIP.\n"
        "Loading signs describe relative component sides and are not causal effects.\n"
        "Sources: final meeting-PLS CT scores and model definitions; canonical 2021 CT geometry; City of Toronto ward geometry.",
    )
    save_figure(fig, "figure_03_mean_pls_component_1.svg", preview_dir)


def build_figure_06(ct_geo, wards_geo, observed, model_results, preview_dir: Path | None) -> None:
    values_by_outcome, muted_by_outcome, agreement_rates = {}, {}, {}
    for outcome in ["mean", "municipal", "provincial", "federal"]:
        residual_cols = [
            f"meeting_{outcome}_{method}_spatial_nested_cv_residual"
            for method in ("pls", "supervised_pca", "elastic_net")
        ]
        missing = sorted(set(residual_cols) - set(model_results.columns))
        if missing:
            raise ValueError(f"Missing saved spatial-CV residual columns: {missing}")
        residuals = model_results[residual_cols]
        consensus = residuals.mean(axis=1)
        sign_agreement = np.sign(residuals).nunique(axis=1).eq(1)
        values_by_outcome[outcome] = dict(zip(model_results["ct_id"], consensus * 100))
        muted_by_outcome[outcome] = set(model_results.loc[~sign_agreement, "ct_id"]) - IMPUTED_CT_IDS
        eligible = ~model_results["ct_id"].isin(IMPUTED_CT_IDS)
        agreement_rates[outcome] = sign_agreement.loc[eligible].mean() * 100
    federal_diagnostic = set(
        observed.loc[observed["outcome_federal_participation_citizen_18plus"] > 1, "ct_id"]
    )
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.3))
    fig.subplots_adjust(left=0.045, right=0.975, top=0.82, bottom=0.20, wspace=0.04, hspace=0.15)
    add_figure_header(
        fig,
        "Persistent prediction errors reveal where all three models struggle",
        f"Consensus is the mean saved spatial nested-CV residual. All methods agree on the error sign in {min(agreement_rates.values()):.0f}–{max(agreement_rates.values()):.0f}% of observed tracts, depending on outcome.",
    )
    for ax, outcome in zip(axes.ravel(), ["mean", "municipal", "provincial", "federal"]):
        draw_map(
            ax,
            ct_geo,
            wards_geo,
            values_by_outcome[outcome],
            [-10, -5, 0, 5, 10],
            DIVERGING_6,
            diagnostic_ids=federal_diagnostic if outcome == "federal" else set(),
            hatched_ids=muted_by_outcome[outcome],
            missing_ids=IMPUTED_CT_IDS,
        )
        add_panel_label(ax, f"{OUTCOME_LABELS[outcome]}  ·  sign agreement {agreement_rates[outcome]:.0f}%")
    add_swatch_legend(fig, DIVERGING_6, ["≤ −10", "−10 to −5", "−5 to 0", "0 to +5", "+5 to +10", "> +10 pp"], y=0.095)
    extra = [
        Patch(facecolor=WHITE, edgecolor=BRAND_GRAY_70, hatch="///", label="Hatched: methods disagree on sign"),
        Patch(facecolor=BRAND_GRAY, edgecolor=BRAND_GRAY, label="Imputed outcome (2 CTs)"),
        Patch(facecolor="none", edgecolor=BRAND_GRAY_90, linewidth=1.15, label="Federal ratio > 1"),
    ]
    fig.legend(handles=extra, loc="lower left", bbox_to_anchor=(0.04, 0.063), frameon=False, ncol=3, fontsize=7.8)
    add_footer(
        fig,
        "Notes: Residual = observed minus spatial nested-CV prediction; positive means participation exceeded prediction. Consensus averages saved PLS, supervised-PCA, and Elastic Net residuals—no refits.\n"
        "The two originally missing outcomes were imputed upstream for modelling and are deliberately grayed here.\n"
        "Sources: final saved CT model results and observed variables; canonical 2021 CT geometry; City of Toronto ward geometry.",
        y=0.008,
    )
    save_figure(fig, "figure_06_consensus_spatial_cv_residuals.svg", preview_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Optional directory for PNG QA previews (keep outside the repository).",
    )
    args = parser.parse_args()
    configure_style()
    ct_geo, wards_geo, observed, meeting, model_results, loadings, vip = load_inputs()
    build_figure_01(ct_geo, wards_geo, observed, args.preview_dir)
    build_figure_02(ct_geo, wards_geo, observed, args.preview_dir)
    build_figure_03(ct_geo, wards_geo, meeting, loadings, vip, args.preview_dir)
    build_figure_06(ct_geo, wards_geo, observed, model_results, args.preview_dir)


if __name__ == "__main__":
    main()
