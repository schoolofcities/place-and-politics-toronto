# Step 5B: Supervised PCA Comparison

Supervised PCA first screens variables by their relationship with turnout, then runs ordinary PCA on the screened variable set. It is less directly supervised than PLS, but easier to explain: turnout chooses the variable set; PCA summarizes the selected predictors.

## Model Comparison

| Model | Predictors/Screened Vars | Components | CV R2 | CV RMSE |
|---|---:|---:|---:|---:|
| Full unfiltered PLS | 70 | 12 | 0.565 | 0.057 |
| Step 3 cleaned PLS | 27 | 5 | 0.558 | 0.058 |
| Supervised PCA | 15 | 8 | 0.540 | 0.059 |

Best screen: `corr_ge_0.15`.

## Largest PCA Loadings In Best Screen

| Variable | Max |loading| |
| --- | --- |
| `block5_ksi_collision_events_2021_2025_per_1000` | 0.633 |
| `block1_age_65_plus_share` | 0.630 |
| `block4_mayoral_top_two_margin` | 0.554 |
| `block1_bachelors_or_higher_25_64_share` | 0.513 |
| `block5_social_housing_share` | 0.498 |
| `block4_provincial_margin` | 0.488 |
| `block1_low_income_lim_at_share` | 0.434 |
| `block4_effective_mayoral_candidates_5pct` | 0.430 |
| `block5_no_car_household_share` | 0.403 |
| `block3_visible_minority_share` | 0.402 |
| `block4_federal_margin` | 0.401 |
| `block3_non_citizen_share` | 0.396 |
| `block3_recent_immigrant_share` | 0.389 |
| `block5_school_age_5_17_share` | 0.358 |
| `block1_average_household_size` | 0.355 |


## Interpretation

Supervised PCA is a useful comparison because it asks whether a simple turnout-screened latent structure can compete with PLS. If it performs similarly, the final story can lean more on interpretable screened dimensions. If it underperforms, PLS remains the stronger supervised reduction method.

The best supervised PCA screen retained these plain-language variables: visible minority share, bachelor or higher education share, effective mayoral candidates above five percent, average household size, non citizen share, recent immigrant share, mayoral top two margin, federal margin, low income share, school age children share, social housing share, provincial margin, age 65 plus share, no car household share, KSI collisions per 1000 residents. This model is useful as a reference-category check because it independently returns a compact set around racialized and citizenship geography, education and class, household structure, electoral competitiveness, age structure, social housing, carlessness, and KSI collisions. Because its predictive performance is weaker than PLS, I would use it as supporting evidence rather than the main model.
