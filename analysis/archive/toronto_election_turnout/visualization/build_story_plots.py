#!/usr/bin/env python3
"""Build the retained, non-spatial Toronto CT story plots.

This script only reads published outputs. It does not fit or rerun any model.
It writes the two publication SVGs to the final visual release folder and can
optionally write PNG previews outside the repository for visual QA.
"""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

# Keep Matplotlib's generated cache outside the repository and user home.
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "toronto_ct_matplotlib_cache"))

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
FINAL_ROOT = REPO_ROOT / "data/toronto_election_turnout/final"
OUTPUT_DIR = FINAL_ROOT / "visuals"
OBSERVED_FILE = FINAL_ROOT / "observed/toronto_ct_2021_observed_variables.csv"
ROBUSTNESS_FILE = FINAL_ROOT / "robustness_checks/robustness_validation_summary.csv"
PLS_SHUFFLED_FILE = FINAL_ROOT / "model_definitions/toronto_turnout_model_summary.csv"
MODEL_RESULTS_FILE = FINAL_ROOT / "modelled/toronto_ct_turnout_model_results.csv"
FONT_DIR = REPO_ROOT / "src/assets/fonts"

INK = "#191919"
MUTED = "#727272"
GRID = "#D0D1C9"
BACKGROUND = "#FFFEFD"
ELECTION_COLORS = {
    "Mean": "#1E3765",
    "Municipal": "#007FA3",
    "Provincial": "#6D247A",
    "Federal": "#DC4633",
}
METHOD_COLORS = {
    "PLS": "#1E3765",
    "Supervised PCA": "#00A189",
    "Elastic Net": "#AB1368",
}

VARIABLES = {
    "block3_visible_minority_share": "Visible minority share",
    "block1_bachelors_or_higher_25_64_share": "Bachelor's degree or higher, age 25–64",
    "block1_unemployment_rate_share": "Unemployment rate",
    "block1_average_household_size": "Average household size",
    "block3_recent_immigrant_share": "Recent immigrant share",
    "block2_condo_share": "Condominium share",
}
OUTCOMES = {
    "Mean": "outcome_mean_participation_citizen_18plus",
    "Municipal": "outcome_municipal_participation_citizen_18plus",
    "Provincial": "outcome_provincial_participation_citizen_18plus",
    "Federal": "outcome_federal_participation_citizen_18plus",
}


def register_fonts() -> tuple[str, str]:
    """Register repository fonts and return title and label family names."""
    title_font = FONT_DIR / "Trade Gothic LT Bold.ttf"
    label_font = FONT_DIR / "OpenSans-Regular.ttf"
    label_bold = FONT_DIR / "OpenSans-Bold.ttf"
    for path in (title_font, label_font, label_bold):
        if not path.exists():
            raise FileNotFoundError(f"Required repository font is missing: {path}")
        fm.fontManager.addfont(path)
    return fm.FontProperties(fname=title_font).get_name(), fm.FontProperties(fname=label_font).get_name()


TITLE_FONT, LABEL_FONT = register_fonts()
mpl.rcParams.update(
    {
        "font.family": LABEL_FONT,
        "font.size": 9.5,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": GRID,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "figure.facecolor": BACKGROUND,
        "axes.facecolor": BACKGROUND,
        "savefig.facecolor": BACKGROUND,
        "svg.fonttype": "none",
        "svg.hashsalt": "toronto-ct-story-plots-v1",
    }
)


def assert_columns(frame: pd.DataFrame, columns: list[str], source: Path) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns in {source}: {missing}")


def save_figure(fig: plt.Figure, filename: str, preview_dir: Path | None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    svg_path = OUTPUT_DIR / filename
    fig.savefig(svg_path, format="svg", bbox_inches="tight", metadata={"Date": None})
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(preview_dir / filename.replace(".svg", ".png"), dpi=170, bbox_inches="tight")
    plt.close(fig)


def build_correlation_plot(preview_dir: Path | None) -> None:
    observed = pd.read_csv(OBSERVED_FILE)
    required = list(VARIABLES) + list(OUTCOMES.values())
    assert_columns(observed, required, OBSERVED_FILE)

    rows: list[dict[str, object]] = []
    for variable, variable_label in VARIABLES.items():
        for election, outcome in OUTCOMES.items():
            pair = observed[[variable, outcome]].dropna()
            rows.append(
                {
                    "variable": variable,
                    "variable_label": variable_label,
                    "election": election,
                    "r": pair[variable].corr(pair[outcome]),
                    "n": len(pair),
                }
            )
    corr = pd.DataFrame(rows)
    if corr["n"].min() != 583 or corr["n"].max() != 583:
        raise ValueError(f"Unexpected pairwise sample sizes: {sorted(corr['n'].unique())}")
    if corr["r"].isna().any():
        raise ValueError("Correlation output contains missing values")

    fig, ax = plt.subplots(figsize=(11.2, 7.2))
    fig.subplots_adjust(left=0.30, right=0.95, top=0.76, bottom=0.19)
    base_y = np.arange(len(VARIABLES) - 1, -1, -1, dtype=float)
    offsets = {"Mean": 0.24, "Municipal": 0.08, "Provincial": -0.08, "Federal": -0.24}
    markers = {"Mean": "D", "Municipal": "o", "Provincial": "s", "Federal": "^"}

    for base, (variable, label) in zip(base_y, VARIABLES.items()):
        block = corr[corr["variable"] == variable]
        ax.hlines(base, block["r"].min(), block["r"].max(), color=GRID, linewidth=2.1, zorder=1)
        for election in OUTCOMES:
            value = float(block.loc[block["election"] == election, "r"].iloc[0])
            y = base + offsets[election]
            ax.scatter(
                value,
                y,
                s=55,
                marker=markers[election],
                color=ELECTION_COLORS[election],
                edgecolor=BACKGROUND,
                linewidth=0.7,
                zorder=3,
            )
            dx = 0.018 if value < 0.70 else -0.018
            ha = "left" if dx > 0 else "right"
            ax.text(value + dx, y, f"{value:+.2f}", va="center", ha=ha, fontsize=8.2, color=ELECTION_COLORS[election])
        ax.text(-0.825, base, label, ha="right", va="center", fontsize=9.5, color=INK, clip_on=False)

    ax.axvline(0, color=INK, linewidth=1.0, zorder=0)
    ax.set_xlim(-0.8, 0.8)
    ax.set_ylim(-0.55, len(VARIABLES) - 0.45)
    ax.set_yticks([])
    ax.set_xticks(np.arange(-0.8, 0.81, 0.2))
    ax.set_xticklabels([f"{x:.1f}" for x in np.arange(-0.8, 0.81, 0.2)])
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)
    ax.set_xlabel("Pearson correlation with citizen-age-18+ participation (r)", labelpad=11)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)

    fig.text(0.075, 0.935, "Participation correlates are strongest in the municipal election", fontsize=22, fontfamily=TITLE_FONT, color=INK)
    fig.text(
        0.075,
        0.888,
        "Across 583 census tracts, the same social gradients recur—but their strength depends on the election.",
        fontsize=11,
        color=MUTED,
    )
    legend_x = [0.075, 0.19, 0.335, 0.475]
    for x, election in zip(legend_x, OUTCOMES):
        fig.add_artist(
            Line2D(
                [x],
                [0.84],
                transform=fig.transFigure,
                marker=markers[election],
                markersize=7,
                markerfacecolor=ELECTION_COLORS[election],
                markeredgecolor=ELECTION_COLORS[election],
                linestyle="none",
            )
        )
        fig.text(x + 0.013, 0.835, election, color=ELECTION_COLORS[election], fontsize=10, fontweight="bold")

    fig.text(
        0.075,
        0.105,
        "Recent-immigrant share attenuates from municipal (−0.46) to federal (−0.08); condominium share changes sign (−0.08 to +0.21).",
        fontsize=9.2,
        color=INK,
    )
    fig.text(
        0.075,
        0.061,
        "Each estimate is a bivariate, ecological association—not an individual-level or causal effect. Pairwise n = 583 CTs.",
        fontsize=8.3,
        color=MUTED,
    )
    fig.text(
        0.075,
        0.031,
        "Source: final/observed/toronto_ct_2021_observed_variables.csv",
        fontsize=7.6,
        color=MUTED,
    )
    save_figure(fig, "figure_04_singular_variables_across_elections.svg", preview_dir)


def load_validation_results() -> pd.DataFrame:
    robustness = pd.read_csv(ROBUSTNESS_FILE)
    assert_columns(
        robustness,
        ["outcome", "method", "shuffled_cv_r2", "spatial_nested_cv_r2"],
        ROBUSTNESS_FILE,
    )
    robust_rows = robustness.assign(
        outcome_key=robustness["outcome"].str.extract(r"outcome_(mean|municipal|provincial|federal)_", expand=False),
        method_label=robustness["method"].map({"supervised_pca": "Supervised PCA", "elastic_net": "Elastic Net"}),
    )[["outcome_key", "method_label", "shuffled_cv_r2", "spatial_nested_cv_r2"]]

    pls_shuffled = pd.read_csv(PLS_SHUFFLED_FILE)
    assert_columns(pls_shuffled, ["model_id", "outcome", "cv_r2"], PLS_SHUFFLED_FILE)
    pls_shuffled = pls_shuffled[pls_shuffled["model_id"].isin(
        ["meeting_mean_pls", "meeting_municipal_pls", "meeting_provincial_pls", "meeting_federal_pls"]
    )].copy()
    pls_shuffled["outcome_key"] = pls_shuffled["outcome"].str.extract(
        r"outcome_(mean|municipal|provincial|federal)_", expand=False
    )

    model_results = pd.read_csv(MODEL_RESULTS_FILE)
    pls_spatial_rows = []
    for outcome_key in ("mean", "municipal", "provincial", "federal"):
        prediction_col = f"meeting_{outcome_key}_pls_spatial_nested_cv_prediction"
        residual_col = f"meeting_{outcome_key}_pls_spatial_nested_cv_residual"
        assert_columns(model_results, [prediction_col, residual_col], MODEL_RESULTS_FILE)
        prediction = model_results[prediction_col]
        actual = prediction + model_results[residual_col]
        r2 = 1 - ((actual - prediction) ** 2).sum() / ((actual - actual.mean()) ** 2).sum()
        pls_spatial_rows.append({"outcome_key": outcome_key, "spatial_nested_cv_r2": r2})
    pls_spatial = pd.DataFrame(pls_spatial_rows)
    pls_rows = pls_shuffled[["outcome_key", "cv_r2"]].rename(columns={"cv_r2": "shuffled_cv_r2"}).merge(
        pls_spatial, on="outcome_key", how="inner", validate="one_to_one"
    )
    pls_rows["method_label"] = "PLS"

    combined = pd.concat([pls_rows, robust_rows], ignore_index=True)
    if combined.shape != (12, 4):
        raise ValueError(f"Expected 12 validation comparisons, found {combined.shape}")
    if combined.isna().any().any():
        raise ValueError("Validation comparison contains missing values")
    expected = pd.MultiIndex.from_product(
        [["mean", "municipal", "provincial", "federal"], ["PLS", "Supervised PCA", "Elastic Net"]]
    )
    actual = pd.MultiIndex.from_frame(combined[["outcome_key", "method_label"]])
    if set(actual) != set(expected) or actual.has_duplicates:
        raise ValueError("Validation comparison does not contain one row per outcome-method pair")
    return combined


def build_validation_plot(preview_dir: Path | None) -> None:
    results = load_validation_results()
    outcomes = [("municipal", "Municipal"), ("mean", "Mean"), ("provincial", "Provincial"), ("federal", "Federal")]
    methods = ["PLS", "Supervised PCA", "Elastic Net"]

    fig, axes = plt.subplots(1, 4, figsize=(13.2, 5.9), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.70, bottom=0.22, wspace=0.16)
    y_positions = np.arange(len(methods) - 1, -1, -1)

    for ax, (outcome_key, outcome_label) in zip(axes, outcomes):
        subset = results[results["outcome_key"] == outcome_key].set_index("method_label")
        for y, method in zip(y_positions, methods):
            shuffled = float(subset.loc[method, "shuffled_cv_r2"])
            spatial = float(subset.loc[method, "spatial_nested_cv_r2"])
            color = METHOD_COLORS[method]
            ax.plot([spatial, shuffled], [y, y], color=color, linewidth=2.2, alpha=0.78, zorder=1)
            ax.scatter(shuffled, y, s=58, marker="s", color=color, edgecolor=BACKGROUND, linewidth=0.6, zorder=3)
            ax.scatter(spatial, y, s=62, marker="o", facecolor=BACKGROUND, edgecolor=color, linewidth=2.0, zorder=3)
            ax.text(shuffled + 0.018, y + 0.14, f"{shuffled:.2f}", ha="center", va="bottom", fontsize=7.7, color=color)
            ax.text(spatial - 0.018, y - 0.14, f"{spatial:.2f}", ha="center", va="top", fontsize=7.7, color=color)

        ax.set_title(outcome_label, fontsize=14, fontfamily=TITLE_FONT, pad=13, color=INK)
        ax.set_xlim(0, 0.70)
        ax.set_xticks(np.arange(0, 0.71, 0.1))
        ax.set_ylim(-0.55, 2.55)
        ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.75)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel("Cross-validated R²", labelpad=10)

    axes[0].set_yticks(y_positions)
    axes[0].set_yticklabels(methods)
    for tick, method in zip(axes[0].get_yticklabels(), methods):
        tick.set_color(METHOD_COLORS[method])
        tick.set_fontweight("bold")

    fig.text(0.075, 0.93, "Spatial validation narrows apparent model performance", fontsize=22, fontfamily=TITLE_FONT, color=INK)
    fig.text(
        0.075,
        0.875,
        "Municipal participation remains the most predictable outcome; mean, provincial, and federal participation follow in order.",
        fontsize=10.6,
        color=MUTED,
    )
    fig.add_artist(
        Line2D(
            [0.078],
            [0.804],
            transform=fig.transFigure,
            marker="s",
            markersize=7,
            markerfacecolor=INK,
            markeredgecolor=INK,
            linestyle="none",
        )
    )
    fig.text(0.089, 0.798, "Shuffled 10-fold CV", color=INK, fontsize=9.8, fontweight="bold")
    fig.add_artist(
        Line2D(
            [0.248],
            [0.804],
            transform=fig.transFigure,
            marker="o",
            markersize=7,
            markerfacecolor=BACKGROUND,
            markeredgecolor=INK,
            markeredgewidth=1.5,
            linestyle="none",
        )
    )
    fig.text(0.259, 0.798, "Spatial nested CV", color=INK, fontsize=9.8, fontweight="bold")
    fig.text(
        0.075,
        0.105,
        "Lines show the validation gap for the same saved model family; spatial folds are the more conservative test of geographic generalization.",
        fontsize=8.5,
        color=INK,
    )
    fig.text(
        0.075,
        0.058,
        "Sources: final model definitions, model results, and robustness summary. No models were refit.",
        fontsize=7.6,
        color=MUTED,
    )
    save_figure(fig, "figure_05_model_validation_comparison.svg", preview_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=None,
        help="Optional directory for PNG QA previews (keep outside the repository).",
    )
    args = parser.parse_args()
    build_correlation_plot(args.preview_dir)
    build_validation_plot(args.preview_dir)
    print(f"Wrote retained SVG figures to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
