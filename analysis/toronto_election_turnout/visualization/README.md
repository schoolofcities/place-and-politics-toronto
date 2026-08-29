# Retained Visual Analysis

This folder contains the two scripts that reproduce the six selected figures
in `data/toronto_election_turnout/final/visuals/`. They read the published CT
release and repository geometry/style assets; they do not fit, tune, or predict
any model.

## Rebuild

Install the Python dependencies from the analysis root, then run the combined
build:

```bash
python3 -m pip install -r requirements.txt
npm run build:visuals
```

The SVG files are overwritten deterministically. Either script can optionally
make PNG previews in any temporary directory for visual QA:

```bash
python3 visualization/build_story_maps.py --preview-dir /tmp/toronto_ct_story_map_previews
python3 visualization/build_story_plots.py --preview-dir /tmp/toronto_ct_story_plot_previews
```

## Script Responsibilities

| Script | Figures | Main published inputs |
| --- | --- | --- |
| `build_story_maps.py` | 01, 02, 03, 06 | CT geometry, observed variables, meeting-PLS scores and definitions, final saved spatial nested-CV model results |
| `build_story_plots.py` | 04, 05 | Observed variables, final PLS definitions and model results, robustness validation summary |

Both scripts assert required columns or CT coverage before drawing. `ct_id` is
read as text. Fixed cross-panel scales are used where values are meant to be
compared directly.

## Deliberate Data Treatments

- Figures 01 and 02 preserve missing participation outcomes as gray.
- Federal participation ratios above 1 remain in the data and are outlined as
  denominator/interpolation diagnostics rather than clipped.
- Figure 03 maps all 585 available latent scores; missing turnout outcomes do
  not make a predictor-derived score missing.
- Figure 06 grays the two outcomes imputed upstream for validation and hatches
  tracts where PLS, supervised PCA, and Elastic Net disagree on residual sign.
- Figure 05 compares saved validation results only. Spatial nested CV is the
  geographic-generalization test; no uncertainty interval was persisted.

The figures are descriptive and ecological. Correlations, loadings, variable
importance, predictions, and residuals should not be read as causal effects.
