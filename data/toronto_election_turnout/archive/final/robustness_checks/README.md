# Meeting-Variable Robustness Checks

This folder contains secondary supervised-PCA and Elastic Net checks for the
same 14 meeting variables and four participation outcomes used by the meeting
PLS analysis. These models test whether the primary predictive pattern depends
on the modelling method; they do not replace the PLS interpretation.

## CT-Level Results

`toronto_ct_meeting_robustness_spatial_cv.csv` has 585 rows × 27 columns: one
row per 2021 Toronto analytical Census Tract, keyed by `ct_id`. The GeoJSON has
the same properties plus EPSG:4326 geometry; the XLSX is a formatted convenience
copy with the definition tables on separate sheets.

The companion files are `toronto_ct_meeting_robustness_spatial_cv.geojson` and
`toronto_ct_meeting_robustness_spatial_cv.xlsx`.

For supervised PCA and Elastic Net, separately for mean, municipal, provincial,
and federal participation, the CT table collects the saved:

- observed outcome;
- spatially blocked nested-CV prediction and residual;
- spatial block, longitude, and latitude used by the validation.

Columns follow `{method}_{outcome}_spatial_nested_cv_{prediction|residual}`.
For each method and outcome, residual equals observed participation minus the
saved spatial-CV prediction.

## What Is Deliberately Not Included

The upstream analysis saved shuffled-CV metrics, but not its per-CT shuffled-CV
predictions. It also did not save supervised-PCA CT scores or in-sample fitted
predictions. Those fields are not reconstructed here. This folder packages only
persisted model outputs.

## Model-Definition Files

| File | Grain/key | Contents |
| --- | --- | --- |
| `supervised_pca_model_summary.csv` | 4 rows; one per `model_id` | Outcome, screening rule, selected predictors/components, train R², shuffled-CV R²/RMSE, and source file |
| `supervised_pca_loadings.csv` | 248 rows; `model_id + component + variable` | Signed and absolute saved component loadings, sign convention, and source file |
| `elastic_net_model_summary.csv` | 4 rows; one per `model_id` | Outcome, alpha, L1 ratio, mean selected predictors, shuffled-CV R²/RMSE, and source file |
| `elastic_net_coefficients.csv` | 56 rows; `model_id + term` | Saved scaled/unscaled coefficients, selection flag, and source file |
| `robustness_validation_summary.csv` | 8 rows; one per `model_id` | Side-by-side shuffled-CV and spatial nested-CV R²/RMSE, spatial MAE, residual spatial correlation, and lineage |

Supervised-PCA loading signs follow the saved SVD orientation. Elastic Net
`selected` indicates a nonzero coefficient in the saved fit. Validation metrics
are model-level constants and are therefore not repeated on every CT row.

Full tuning grids, fold-level settings, bootstrap draws, and experimental
artifacts remain in the upstream modelling folder. The final release records
the source artifacts and their checksums without duplicating development files.

From `analysis/toronto_election_turnout/`, refresh this folder without fitting
any model by running `npm run build:final:collect-robustness`.

## Interpretation

These are ecological prediction checks over 585 CTs. They do not establish
individual-level relationships or causal effects. Spatial nested-CV estimates
are preferred when discussing geographic generalization; shuffled CV remains
as the aggregate metric recorded by the original model-development outputs.
