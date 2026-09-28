# Step 5A: Sparse PLS Comparison

Sparse PLS keeps the PLS idea but forces each component to use only a limited number of variables. This implementation is a transparent sparse-PLS approximation: within each component, it keeps only the largest predictor weights before deflation. This is useful here because ordinary PLS can spread importance across correlated variables, while sparse PLS asks which variables still matter when each latent component must be simpler.

## Model Comparison

| Model | Predictors | Components | CV R2 | CV RMSE |
|---|---:|---:|---:|---:|
| Full unfiltered PLS | 70 | 12 | 0.565 | 0.057 |
| Step 3 cleaned PLS | 27 | 5 | 0.558 | 0.058 |
| Sparse PLS | 27 | 5 | 0.560 | 0.058 |

Best sparse setting: keep 15 variables per component.

## Top Sparse PLS Variables

| Variable | Family | VIP | In Sparse Weights | Components |
| --- | --- | --- | --- | --- |
| `block3_visible_minority_share` | immigration_citizenship | 2.217 | True | 3 |
| `block1_bachelors_or_higher_25_64_share` | household_class | 1.921 | True | 2 |
| `block4_effective_mayoral_candidates_5pct` | mayoral_competitiveness | 1.861 | True | 3 |
| `block1_average_household_size` | household_class | 1.731 | True | 3 |
| `block3_non_citizen_share` | immigration_citizenship | 1.444 | True | 3 |
| `block4_mayoral_top_two_margin` | mayoral_competitiveness | 1.211 | True | 2 |
| `block3_recent_immigrant_share` | immigration_citizenship | 1.146 | True | 5 |
| `block4_federal_margin` | federal_competitiveness | 0.956 | True | 3 |
| `block1_age_65_plus_share` | age_structure | 0.877 | True | 3 |
| `block5_school_age_5_17_share` | service_contact | 0.823 | True | 4 |
| `block1_age_18_34_share` | age_structure | 0.753 | True | 2 |
| `block5_no_car_household_share` | transportation_access | 0.737 | True | 5 |
| `block1_low_income_lim_at_share` | household_class | 0.721 | True | 3 |
| `block4_provincial_margin` | provincial_competitiveness | 0.719 | True | 3 |
| `block5_ksi_collision_events_2021_2025_per_1000` | service_contact | 0.711 | True | 3 |
| `block5_social_housing_share` | service_contact | 0.689 | True | 2 |
| `block2_apartment_share` | housing_form_density | 0.583 | True | 3 |
| `block2_condo_share` | housing_form_density | 0.540 | True | 3 |
| `block5_shelter_access_1200m` | service_access | 0.529 | True | 2 |
| `block2_population_density_per_km2` | housing_form_density | 0.449 | True | 2 |


## Interpretation

Sparse PLS is mainly a readability test. If the same variables remain important under sparsity, that strengthens the story. If performance collapses, it suggests turnout is being explained by a wider bundled social geography rather than a small handful of variables.

Sparse PLS did not introduce new raw variables beyond the cleaned predictor set. Instead, it reweighted the same cleaned variables under a sparsity constraint. The variables that remain strongest under this stricter setup are visible minority share, bachelor or higher education share, effective mayoral candidates above five percent, average household size, non citizen share, mayoral top two margin, recent immigrant share, federal margin, age 65 plus share, school age children share, age 18 to 34 share, no car household share. This supports the same reference categories as the cleaned PLS model: immigration and racialized geography, education and class resources, household composition, electoral competitiveness, age structure, and selected service-contact context.
