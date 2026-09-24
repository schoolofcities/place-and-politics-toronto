# Step 1: Full Supervised PLS Model

This model intentionally uses the full predictor universe before filtering obvious inverse or redundant variables. Mean turnout (`outcome_mean_participation_citizen_18plus`) supervises the latent components through PLS.

## Model Fit

- Observations: 583
- Predictors: 70
- Selected components by 10-fold CV: 12
- Training R2: 0.693
- Cross-validated R2: 0.565
- Cross-validated RMSE: 0.057

## Main Read

The full model is useful as a stress test. It lets the supervised dimension reduction procedure see every available signal, but it also lets inverse and same-concept variables double-enter the component construction. VIP scores should therefore be read as supervised importance, not as final variable-selection decisions.

The selected components are latent variables, not original predictors. In this model, 12 components means PLS built 12 turnout-supervised dimensions from the 70 original predictors. The original variables are interpreted through VIP scores, coefficients, and component loadings.

## Highest VIP Variables

| Variable | Family | VIP | Turnout corr | PLS direction |
| --- | --- | --- | --- | --- |
| `block3_visible_minority_share` | immigration_citizenship | 2.286 | -0.642 | lower turnout |
| `block3_immigrant_share` | immigration_citizenship | 2.031 | -0.573 | lower turnout |
| `block1_bachelors_or_higher_25_64_share` | household_class | 1.985 | 0.554 | higher turnout |
| `block1_unemployment_rate_share` | household_class | 1.934 | -0.532 | lower turnout |
| `block4_effective_mayoral_candidates_5pct` | mayoral_competitiveness | 1.907 | -0.535 | lower turnout |
| `block1_average_household_size` | household_class | 1.834 | -0.485 | lower turnout |
| `block4_mayoral_vote_fragmentation` | mayoral_competitiveness | 1.775 | -0.495 | higher turnout |
| `block3_non_official_mother_tongue_share` | immigration_citizenship | 1.751 | -0.491 | higher turnout |
| `block3_non_citizen_share` | immigration_citizenship | 1.534 | -0.417 | lower turnout |
| `block3_citizen_adult_share` | immigration_citizenship | 1.401 | 0.353 | lower turnout |
| `block1_median_age` | age_structure | 1.268 | 0.253 | lower turnout |
| `block3_recent_immigrant_share` | immigration_citizenship | 1.227 | -0.317 | lower turnout |
| `block1_age_65_plus_share` | age_structure | 1.219 | 0.213 | higher turnout |
| `block4_mayoral_top_two_margin` | mayoral_competitiveness | 1.151 | 0.288 | lower turnout |
| `block4_mayoral_winner_margin` | mayoral_competitiveness | 1.151 | 0.288 | lower turnout |
| `block4_federal_margin` | federal_competitiveness | 1.065 | 0.272 | higher turnout |
| `block2_apartment_lt5_storeys_count` | housing_form_density | 1.034 | 0.275 | higher turnout |
| `block5_library_count_1200m` | service_access | 0.990 | 0.246 | lower turnout |
| `block3_english_french_knowledge_share` | immigration_citizenship | 0.969 | 0.266 | higher turnout |
| `block5_ksi_collision_events_2021_2025_per_1000` | service_contact | 0.933 | 0.160 | higher turnout |


## Reference Categories Suggested By The Full Model

The full model points toward these broad reference categories for story-building: immigration and racialized geography, education and class resources, household composition, local electoral fragmentation, citizenship and language context, age structure, and urban service/contact geography. The strongest plain-language variables behind these categories are visible minority share, immigrant share, bachelor or higher education share, unemployment rate, effective mayoral candidates above five percent, average household size, mayoral vote fragmentation, non official mother tongue share, non citizen share, citizen adult share, median age, recent immigrant share.

## Short Interpretation

Variables with VIP above 1 are contributing more than average to the turnout-supervised PLS projection. The strongest variables should be carried into Step 2 and Step 3 as evidence, but not accepted mechanically. For example, if renter and owner variables both score highly, that is not two separate housing-tenure findings; it is the same tenure concept appearing twice with opposite coding.
