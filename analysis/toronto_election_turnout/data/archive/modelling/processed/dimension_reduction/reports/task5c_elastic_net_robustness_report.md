# Step 5C: Elastic Net Robustness Check

Elastic Net is not a latent-variable method. It is included here as a robustness check on the interaction-augmented candidate set: if a variable or interaction is important in PLS/VIP and also survives penalized regression, that is stronger evidence that it belongs in the final story.

## Best Elastic Net Setting

- Alpha: 0.03
- L1 ratio: 0.5
- Mean selected variables across folds: 27.000
- CV R2 on scaled turnout: 0.617
- CV RMSE on scaled turnout: 0.619

## Selected Variables

| Variable | Family | Abs scaled coef | Direction |
| --- | --- | --- | --- |
| `block3_visible_minority_share` | immigration_citizenship | 0.291 | lower turnout |
| `block1_bachelors_or_higher_25_64_share` | household_class | 0.202 | higher turnout |
| `block1_age_18_34_share` | age_structure | 0.180 | lower turnout |
| `block2_apartment_share` | housing_form_density | 0.125 | higher turnout |
| `block1_bachelors_or_higher_25_64_share__x__block4_effective_mayoral_candidates_5pct` | other | 0.123 | higher turnout |
| `block1_average_household_size` | household_class | 0.114 | lower turnout |
| `block2_population_density_per_km2` | housing_form_density | 0.104 | higher turnout |
| `block1_low_income_lim_at_share__x__block5_requests_311_per_1000` | other | 0.088 | higher turnout |
| `block3_non_citizen_share` | immigration_citizenship | 0.086 | lower turnout |
| `block4_federal_margin` | federal_competitiveness | 0.077 | higher turnout |
| `block4_effective_mayoral_candidates_5pct` | mayoral_competitiveness | 0.069 | lower turnout |
| `block3_non_official_mother_tongue_share` | immigration_citizenship | 0.068 | lower turnout |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block1_unemployment_rate_share` | other | 0.066 | lower turnout |
| `block1_low_income_lim_at_share` | household_class | 0.059 | lower turnout |
| `block5_community_centre_access_1200m` | service_access | 0.052 | lower turnout |
| `block1_average_household_size__x__block5_ksi_collision_events_2021_2025_per_1000` | other | 0.049 | lower turnout |
| `block2_condo_share` | housing_form_density | 0.043 | higher turnout |
| `block1_age_65_plus_share__x__block1_average_household_size` | other | 0.040 | lower turnout |
| `block1_low_income_lim_at_share__x__block1_age_35_64_share` | other | 0.036 | lower turnout |
| `block1_average_household_size__x__block1_age_35_64_share` | other | 0.032 | higher turnout |
| `block2_renter_share` | housing_tenure | 0.032 | lower turnout |
| `block5_shelter_access_1200m` | service_access | 0.026 | lower turnout |
| `block5_library_access_1200m` | service_access | 0.010 | lower turnout |
| `block5_requests_311_per_1000` | service_contact | 0.008 | higher turnout |
| `block5_social_housing_share` | service_contact | 0.004 | higher turnout |


## Agreement With Interaction-Augmented PLS

Top interaction-augmented PLS variables also selected by Elastic Net:

- `block1_average_household_size`
- `block1_bachelors_or_higher_25_64_share`
- `block1_bachelors_or_higher_25_64_share__x__block4_effective_mayoral_candidates_5pct`
- `block3_non_citizen_share`
- `block3_non_official_mother_tongue_share`
- `block3_visible_minority_share`
- `block4_effective_mayoral_candidates_5pct`
- `block4_federal_margin`
- `block4_mayoral_top_two_margin`

## Interpretation

Elastic Net should not replace PLS for this project because it does not create latent components. Its value is diagnostic. Variables and interactions that survive both methods are sturdy candidates for the final narrative. Terms that are high-VIP but not selected by Elastic Net may still matter as part of a latent geography, but they are less convincing as standalone predictors.

The strongest Elastic Net terms in plain language are visible minority share, bachelor or higher education share, age 18 to 34 share, apartment share, bachelor or higher education share with effective mayoral candidates above five percent, average household size, population density, low income share with 311 requests per 1000 residents, non citizen share, federal margin, effective mayoral candidates above five percent, non official mother tongue share. As a robustness check, this supports reference categories around racialized geography, education, young adults, apartment and density context, local electoral fragmentation, household size, low income and 311 service contact, citizenship, and federal competitiveness.
