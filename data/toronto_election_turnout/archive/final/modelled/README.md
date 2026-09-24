# CT-Level Model Output Dictionary

This folder stores outputs indexed by CT. Model-wide definitions—predictors,
loadings, coefficients, fit statistics, and component labels—are kept in
`../model_definitions/` to avoid repeating them on every CT row.

## Retained Model IDs

| Model ID prefix | Outcome | Retained components |
| --- | --- | ---: |
| `full_unfiltered_mean_pls` | Mean participation | 12 |
| `theory_cleaned_mean_pls` | Mean participation | 5 |
| `blocks_1_3_cleaned_mean_pls` | Mean participation | 6 |
| `meeting_mean_pls` | Mean participation | 2 |
| `meeting_municipal_pls` | Municipal participation | 3 |
| `meeting_provincial_pls` | Provincial participation | 3 |
| `meeting_federal_pls` | Federal participation | 3 |

## `toronto_ct_latent_scores`

Files: `toronto_ct_latent_scores.csv` and `toronto_ct_latent_scores.geojson`.
Grain: one row per CT. Primary key: `ct_id`.
Dimensions: 585 rows × 72 columns.

For every retained model/component, two columns are provided:

| Suffix | Meaning |
| --- | --- |
| `_component_N_score` | Fitted PLS X-score for component N |
| `_component_N_percentile` | Within-model percentile rank of that score across eligible CTs |

The full-unfiltered model has two CTs without complete inputs, so its score and
percentile fields are blank there. Other retained models cover all 585 CTs.
Component signs are orientation conventions; interpret them using the component
dictionary and loading table rather than as inherently positive or negative.

## `toronto_ct_turnout_model_results`

Files: `toronto_ct_turnout_model_results.csv` and
`toronto_ct_turnout_model_results.geojson`. Grain: one row per CT. Primary key: `ct_id`.
Dimensions: 585 rows × 87 columns.

PLS result suffixes:

| Suffix | Meaning |
| --- | --- |
| `_fitted_participation` | In-sample fitted outcome |
| `_residual` | Observed outcome minus fitted value |
| `_cv_prediction` | Fixed shuffled 10-fold cross-validation prediction |
| `_cv_residual` | Observed outcome minus shuffled-CV prediction |
| `_included_flag` | Whether the CT was included in that model fit |

The table also retains selected spatial-model fitted/residual outputs and saved
meeting-model spatial nested-CV blocks, predictions, and residuals. Those names
contain `_spatial_` or `_spatial_nested_cv_` and identify the method and outcome
before the suffix.

Use out-of-sample CV predictions for predictive evaluation. In-sample fitted
values describe fit to the observed data and should not be reported as a
generalization estimate.
