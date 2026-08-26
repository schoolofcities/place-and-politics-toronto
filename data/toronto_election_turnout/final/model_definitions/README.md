# PLS Model-Definition Dictionary

These long and model-level tables explain how to interpret the CT outputs in
`../modelled/` and `../meeting_pls/`. They avoid repeating model constants on
585 CT rows. `model_id` is the common join key across this folder.

## File Guide

| File | Grain and key | What it answers |
| --- | --- | --- |
| `toronto_turnout_model_summary.csv` | 7 rows; one per `model_id` | Which outcome, sample, predictors, components, fit, CV convention, and source define each model? |
| `toronto_turnout_model_predictors.csv` | 166 rows; `model_id + predictor_order` | Which variables entered each model and in what order? |
| `toronto_turnout_component_loadings.csv` | 1,207 rows; `model_id + component + variable` | Which variables define the high and low sides of every component? |
| `toronto_turnout_variable_importance.csv` | 166 rows; `model_id + variable` | Which predictors are most important and how do they correlate with turnout? |
| `toronto_turnout_model_coefficients.csv` | 166 rows; `model_id + variable` | What PLS coefficient is associated with each predictor? |
| `toronto_turnout_component_dictionary.csv` | 34 rows; `model_id + component` | What label, anchor variables, sign convention, and outcome correlation describe each component? |

## Important Fields

### Model summary

`num_predictors` and `selected_components` define model size. `train_r2` and
`train_rmse` describe in-sample fit; `cv_r2` and `cv_rmse` describe the saved
shuffled cross-validation evaluation. `source_summary` and `source_report`
point back to the model-development artifacts.

### Predictor membership and coefficients

`predictor_order` preserves input ordering. `meeting_selected_flag` identifies
the 14-variable meeting subset. `pls_coefficient` is the coefficient exported
for the fitted PLS model and should be interpreted together with predictor
scaling and the model outcome.

### Loadings, VIP, and component labels

`loading` gives signed component orientation; `absolute_loading` supports
ranking without discarding the sign in interpretation. `vip` summarizes
variable importance in projection. `turnout_correlation` and `direction`
describe bivariate direction, not causality. The component dictionary provides
human-readable high/low anchors and the exact sign convention.

Join these tables to one another on `model_id`, adding `component` or `variable`
where those fields form part of the stated key. Do not join them directly to CT
rows unless intentionally expanding model constants across observations.
