# Selected Visual Findings

This folder contains the six publication-ready figures retained after the
exploratory analysis. The set is intentionally small: each figure contributes a
distinct result, and near-duplicate model or variable maps were not kept.

| Figure | What it shows | Main use |
| --- | --- | --- |
| `figure_01_cross_election_participation.svg` | CT participation relative to each election's weighted Toronto rate | Compare the shared geography of municipal, provincial, and federal participation |
| `figure_02_cross_election_instability.svg` | Centered election-to-election gaps and the range of within-election z-scores | Find tracts whose relative position changes across election levels |
| `figure_03_mean_pls_component_1.svg` | Mean meeting-PLS component-1 scores, loadings, and VIP | Interpret the main recurring tract profile and its geography |
| `figure_04_singular_variables_across_elections.svg` | Six bivariate CT correlations across four participation outcomes | Compare how selected observed associations strengthen, attenuate, or change sign |
| `figure_05_model_validation_comparison.svg` | Saved shuffled and spatial CV R-squared for PLS, supervised PCA, and Elastic Net | Assess geographic generalization and method robustness |
| `figure_06_consensus_spatial_cv_residuals.svg` | Mean saved residual across the three methods, with disagreement and QA flags | Locate persistent under- and over-prediction without repeating twelve method maps |

Figures 01–03 and 06 are reproduced by
`analysis/toronto_election_turnout/visualization/build_story_maps.py`; figures 04
and 05 by `build_story_plots.py` in the same folder. The analysis README records
the source files, commands, and data treatments so this release folder can stay
focused on interpretation.

These are tract-level ecological results. Election returns are spatially
allocated estimates, federal ratios above 1 are flagged rather than hidden, and
model-validation results describe prediction—not causal importance.
