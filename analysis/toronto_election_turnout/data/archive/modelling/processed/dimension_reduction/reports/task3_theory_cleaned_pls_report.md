# Step 3: Theory-Cleaned Supervised PLS and Variable Family Tournament

Step 3 uses the Step 1 VIP evidence and Step 2 redundancy diagnostics to build a more defensible supervised dimension-reduction model. The goal is not to pretend the predictors are independent. The goal is to keep a smaller set of representatives so no single social concept gets double-weighted in the PLS components.

## Full vs Cleaned Model

| Model | Predictors | Components | CV R2 | CV RMSE | Train R2 |
|---|---:|---:|---:|---:|---:|
| Full unfiltered PLS | 70 | 12 | 0.565 | 0.057 | 0.693 |
| Theory-cleaned PLS | 27 | 5 | 0.558 | 0.058 | 0.625 |

## Selection Logic

The cleaned model was built with a family approach. Within each family, variables were judged using four pieces of evidence: common-sense interpretability, bivariate turnout association, full-model PLS VIP, and redundancy/VIF. Where variables were close substitutes, the workflow also ran one-family substitution tests and connected-family combination tests.

This means a variable could be excluded even if it had a high VIP when another selected variable represented the same concept more cleanly. Conversely, a variable could stay with moderate VIP if it gives a clearer theoretical reading and does not create severe redundancy.

The 5 selected components are latent variables created from the 27 selected original predictors. They are not 5 named raw variables. The model is interpreted by looking back at which original predictors have high VIP scores and strong loadings within those latent components.

## Final Variables Kept

| Variable | Family | VIP | Turnout corr | VIF | Reason |
| --- | --- | --- | --- | --- | --- |
| `block1_age_65_plus_share` | age_structure | 1.219 | 0.182 | 146.305 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block1_age_18_34_share` | age_structure | 0.932 | -0.136 | 129.804 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block4_federal_margin` | federal_competitiveness | 1.065 | 0.272 | 8.264 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block1_bachelors_or_higher_25_64_share` | household_class | 1.985 | 0.554 | 7.119 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block1_average_household_size` | household_class | 1.834 | -0.485 | 26.655 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block1_low_income_lim_at_share` | household_class | 0.919 | -0.199 | 10.691 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block2_apartment_share` | housing_form_density | 0.863 | 0.089 | 30.687 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block2_condo_share` | housing_form_density | 0.664 | 0.084 | 28.586 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block2_population_density_per_km2` | housing_form_density | 0.744 | 0.102 | 47.932 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block2_renter_share` | housing_tenure | 0.671 | -0.081 | 8100.055 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block3_visible_minority_share` | immigration_citizenship | 2.286 | -0.642 | 16.311 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block3_non_citizen_share` | immigration_citizenship | 1.534 | -0.417 | 23.912 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block3_recent_immigrant_share` | immigration_citizenship | 1.227 | -0.317 | 13.072 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block4_effective_mayoral_candidates_5pct` | mayoral_competitiveness | 1.907 | -0.535 | 39.781 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block4_mayoral_top_two_margin` | mayoral_competitiveness | 1.151 | 0.288 | inf | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block4_provincial_margin` | provincial_competitiveness | 0.802 | 0.184 | 4.606 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block2_same_address_5yr_share` | residential_stability | 0.644 | -0.120 | 14.819 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_shelter_access_1200m` | service_access | 0.728 | 0.139 | 2.882 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_library_access_1200m` | service_access | 0.630 | 0.137 | 4.646 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_community_centre_access_1200m` | service_access | 0.495 | -0.037 | 2.138 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_ksi_collision_events_2021_2025_per_1000` | service_contact | 0.933 | 0.157 | 3.371 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_social_housing_share` | service_contact | 0.747 | -0.191 | 2.642 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_requests_311_per_1000` | service_contact | 0.765 | 0.140 | 10.169 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_development_applications_2021_2025_per_1000` | service_contact | 0.690 | 0.095 | 5.890 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_school_age_5_17_share` | service_contact | 0.882 | -0.194 | 46.384 | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_no_car_household_share` | transportation_access | 0.832 | 0.174 | inf | Kept as a theory/common-sense representative and checked against diagnostics. |
| `block5_transit_commute_share_preferred` | transportation_access | 0.538 | -0.002 | inf | Kept as a theory/common-sense representative and checked against diagnostics. |


In plain language, the kept variables are age 65 plus share, age 18 to 34 share, bachelor or higher education share, average household size, low income share, renter share, same address five year share, apartment share, condo share, population density, visible minority share, non citizen share, recent immigrant share, effective mayoral candidates above five percent, mayoral top two margin, federal margin, provincial margin, no car household share, transit commute share, shelter access within 1200 metres, library access within 1200 metres, community centre access within 1200 metres, KSI collisions per 1000 residents, social housing share, 311 requests per 1000 residents, development applications per 1000 residents, school age children share.

## Cleaned Model VIP Results

| Variable | Family | VIP | Turnout corr | Direction |
| --- | --- | --- | --- | --- |
| `block3_visible_minority_share` | immigration_citizenship | 2.145 | -0.642 | lower turnout |
| `block1_bachelors_or_higher_25_64_share` | household_class | 1.847 | 0.554 | higher turnout |
| `block4_effective_mayoral_candidates_5pct` | mayoral_competitiveness | 1.787 | -0.535 | lower turnout |
| `block1_average_household_size` | household_class | 1.672 | -0.485 | lower turnout |
| `block3_non_citizen_share` | immigration_citizenship | 1.433 | -0.417 | lower turnout |
| `block3_recent_immigrant_share` | immigration_citizenship | 1.137 | -0.317 | lower turnout |
| `block4_mayoral_top_two_margin` | mayoral_competitiveness | 1.084 | 0.288 | lower turnout |
| `block4_federal_margin` | federal_competitiveness | 0.967 | 0.272 | higher turnout |
| `block1_age_18_34_share` | age_structure | 0.833 | -0.136 | lower turnout |
| `block5_school_age_5_17_share` | service_contact | 0.820 | -0.194 | higher turnout |
| `block1_age_65_plus_share` | age_structure | 0.805 | 0.182 | higher turnout |
| `block1_low_income_lim_at_share` | household_class | 0.770 | -0.199 | lower turnout |
| `block5_no_car_household_share` | transportation_access | 0.741 | 0.174 | lower turnout |
| `block5_shelter_access_1200m` | service_access | 0.716 | 0.139 | lower turnout |
| `block4_provincial_margin` | provincial_competitiveness | 0.675 | 0.184 | higher turnout |
| `block5_social_housing_share` | service_contact | 0.674 | -0.191 | lower turnout |
| `block2_apartment_share` | housing_form_density | 0.669 | 0.089 | higher turnout |
| `block2_population_density_per_km2` | housing_form_density | 0.609 | 0.102 | higher turnout |
| `block5_ksi_collision_events_2021_2025_per_1000` | service_contact | 0.592 | 0.157 | higher turnout |
| `block2_same_address_5yr_share` | residential_stability | 0.575 | -0.120 | lower turnout |


## Remaining VIF After Cleaning

| Variable | Family | Cleaned VIF |
| --- | --- | --- |
| `block1_average_household_size` | household_class | 17.521 |
| `block2_apartment_share` | housing_form_density | 14.575 |
| `block2_renter_share` | housing_tenure | 14.327 |
| `block1_age_18_34_share` | age_structure | 12.753 |
| `block3_non_citizen_share` | immigration_citizenship | 12.265 |
| `block5_school_age_5_17_share` | service_contact | 10.666 |
| `block2_condo_share` | housing_form_density | 10.022 |
| `block3_recent_immigrant_share` | immigration_citizenship | 9.402 |
| `block2_same_address_5yr_share` | residential_stability | 9.301 |
| `block3_visible_minority_share` | immigration_citizenship | 7.847 |
| `block1_low_income_lim_at_share` | household_class | 6.224 |
| `block1_age_65_plus_share` | age_structure | 5.412 |
| `block5_no_car_household_share` | transportation_access | 5.102 |
| `block4_effective_mayoral_candidates_5pct` | mayoral_competitiveness | 4.677 |
| `block1_bachelors_or_higher_25_64_share` | household_class | 3.890 |


The cleaned model removes the exact duplicate/inverse variables from the full universe, so the impossible VIFs mostly disappear. Some VIF values remain above 10 because the social geography itself is bundled: household size, age, tenure, apartment form, citizenship, and school-age composition still move together across Toronto CTs. That remaining collinearity should be handled by reading the PLS components and VIP scores, not by treating each coefficient as a standalone causal estimate.

The age variables are a good example of remaining conceptual correlation. Age 18 to 34 share and age 65 plus share are partly compositional, but they are not exact inverses. I kept both because they represent different turnout stories: younger-adult concentration and older-adult concentration. Still, the VIF table shows that age structure remains bundled with household size, residential stability, and school-age composition, so these should be interpreted as a family rather than isolated causal coefficients.

## Reference Categories For The Cleaned Model

The cleaned model suggests five main reference categories for the final story: immigration and racialized geography, education and class resources, age and household composition, housing tenure and urban form, and electoral competitiveness. The most stable variables behind these categories are visible minority share, bachelor or higher education share, effective mayoral candidates above five percent, average household size, non citizen share, recent immigrant share, mayoral top two margin, federal margin, age 18 to 34 share, school age children share, age 65 plus share, low income share. These categories are a way to bridge the model-first workflow back to the kind of reference categories Zack was emphasizing.

## Family Tournament Highlights

| Family/test | Best candidate | CV R2 | CV RMSE |
| --- | --- | --- | --- |
| age_structure | `block1_age_18_34_share` | 0.559 | 0.058 |
| age_structure+immigration_citizenship | `block1_age_65_plus_share; block3_visible_minority_share` | 0.564 | 0.057 |
| federal_competitiveness | `block4_federal_margin` | 0.558 | 0.058 |
| household_class | `block1_bachelors_or_higher_25_64_share` | 0.558 | 0.058 |
| housing_form_density | `block2_apartment_share` | 0.559 | 0.058 |
| housing_tenure | `block2_renter_share` | 0.558 | 0.058 |
| housing_tenure+housing_form_density | `block2_renter_share; block2_apartment_share` | 0.559 | 0.058 |
| immigration_citizenship | `block3_visible_minority_share` | 0.566 | 0.057 |
| mayoral_competitiveness | `block4_effective_mayoral_candidates_5pct` | 0.560 | 0.058 |
| mayoral_competitiveness+federal_competitiveness+provincial_competitiveness | `block4_effective_mayoral_candidates_5pct; block4_federal_margin; block4_provincial_margin` | 0.560 | 0.058 |
| provincial_competitiveness | `block4_effective_provincial_parties_5pct` | 0.562 | 0.058 |
| residential_stability | `block2_same_address_1yr_share` | 0.558 | 0.058 |
| service_access | `block5_shelter_count_1200m` | 0.557 | 0.058 |
| service_contact | `block5_ksi_collision_events_2021_2025_per_1000` | 0.569 | 0.057 |
| transportation_access | `block5_transit_commute_share_preferred` | 0.561 | 0.058 |
| transportation_access+service_access+service_contact | `block5_no_car_household_share; block5_shelter_count_1200m; block5_ksi_collision_events_2021_2025_per_1000` | 0.578 | 0.056 |


## Variable-by-Variable Decisions

- `block1_age_65_plus_share` (age_structure): Kept. VIP 1.219, turnout correlation 0.182, VIF 146.305. Kept as a theory/common-sense representative and checked against diagnostics.
- `block1_age_18_34_share` (age_structure): Kept. VIP 0.932, turnout correlation -0.136, VIF 129.804. Kept as a theory/common-sense representative and checked against diagnostics.
- `block1_median_age` (age_structure): Not kept. VIP 1.268, turnout correlation 0.232, VIF 28.099. Excluded to keep the family from double-weighting a correlated concept.
- `block1_age_35_64_share` (age_structure): Not kept. VIP 0.708, turnout correlation 0.142, VIF 44.191. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block4_federal_margin` (federal_competitiveness): Kept. VIP 1.065, turnout correlation 0.272, VIF 8.264. Kept as a theory/common-sense representative and checked against diagnostics.
- `block4_federal_party_count_5pct` (federal_competitiveness): Not kept. VIP 0.912, turnout correlation 0.206, VIF 5.005. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block4_federal_vote_fragmentation` (federal_competitiveness): Not kept. VIP 0.436, turnout correlation -0.057, VIF 163.980. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block4_effective_federal_parties_5pct` (federal_competitiveness): Not kept. VIP 0.416, turnout correlation -0.029, VIF 154.937. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block1_bachelors_or_higher_25_64_share` (household_class): Kept. VIP 1.985, turnout correlation 0.554, VIF 7.119. Kept as a theory/common-sense representative and checked against diagnostics.
- `block1_average_household_size` (household_class): Kept. VIP 1.834, turnout correlation -0.485, VIF 26.655. Kept as a theory/common-sense representative and checked against diagnostics.
- `block1_low_income_lim_at_share` (household_class): Kept. VIP 0.919, turnout correlation -0.199, VIF 10.691. Kept as a theory/common-sense representative and checked against diagnostics.
- `block1_unemployment_rate_share` (household_class): Not kept. VIP 1.934, turnout correlation -0.532, VIF 3.556. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block2_apartment_share` (housing_form_density): Kept. VIP 0.863, turnout correlation 0.089, VIF 30.687. Kept as a theory/common-sense representative and checked against diagnostics.
- `block2_condo_share` (housing_form_density): Kept. VIP 0.664, turnout correlation 0.084, VIF 28.586. Kept as a theory/common-sense representative and checked against diagnostics.
- `block2_population_density_per_km2` (housing_form_density): Kept. VIP 0.744, turnout correlation 0.102, VIF 47.932. Kept as a theory/common-sense representative and checked against diagnostics.
- `block2_semi_detached_share` (housing_form_density): Not kept. VIP 0.570, turnout correlation 0.095, VIF 6.727. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block2_condos_per_km2` (housing_form_density): Not kept. VIP 0.579, turnout correlation 0.071, VIF 13.166. Excluded to keep the family from double-weighting a correlated concept.
- `block2_detached_share` (housing_form_density): Not kept. VIP 0.742, turnout correlation -0.047, VIF 25.246. Excluded to keep the family from double-weighting a correlated concept.
- `block2_condominium_dwellings_count` (housing_form_density): Not kept. VIP 0.571, turnout correlation 0.071, VIF 31.740. Excluded to keep the family from double-weighting a correlated concept.
- `block2_apartments_per_km2` (housing_form_density): Not kept. VIP 0.673, turnout correlation 0.115, VIF 69.113. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block2_apartment_lt5_storeys_count` (housing_form_density): Not kept. VIP 1.034, turnout correlation 0.275, VIF inf. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block2_apartment_duplex_count` (housing_form_density): Not kept. VIP 0.866, turnout correlation -0.169, VIF inf. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block2_apartment_total_count` (housing_form_density): Not kept. VIP 0.634, turnout correlation 0.096, VIF inf. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block2_structural_type_total_dwellings` (housing_form_density): Not kept. VIP 0.543, turnout correlation 0.083, VIF 284.495. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block2_condo_status_total_dwellings` (housing_form_density): Not kept. VIP 0.542, turnout correlation 0.083, VIF 259.010. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block2_apartment_5plus_storeys_count` (housing_form_density): Not kept. VIP 0.566, turnout correlation 0.035, VIF inf. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block2_renter_share` (housing_tenure): Kept. VIP 0.671, turnout correlation -0.081, VIF 8100.055. Kept as a theory/common-sense representative and checked against diagnostics.
- `block2_owner_share` (housing_tenure): Not kept. VIP 0.666, turnout correlation 0.079, VIF 8033.196. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block3_visible_minority_share` (immigration_citizenship): Kept. VIP 2.286, turnout correlation -0.642, VIF 16.311. Kept as a theory/common-sense representative and checked against diagnostics.
- `block3_non_citizen_share` (immigration_citizenship): Kept. VIP 1.534, turnout correlation -0.417, VIF 23.912. Kept as a theory/common-sense representative and checked against diagnostics.
- `block3_recent_immigrant_share` (immigration_citizenship): Kept. VIP 1.227, turnout correlation -0.317, VIF 13.072. Kept as a theory/common-sense representative and checked against diagnostics.
- `block3_immigrant_share` (immigration_citizenship): Not kept. VIP 2.031, turnout correlation -0.573, VIF 34.659. Excluded to keep the family from double-weighting a correlated concept.
- `block3_non_official_mother_tongue_share` (immigration_citizenship): Not kept. VIP 1.751, turnout correlation -0.491, VIF 21.937. Excluded to keep the family from double-weighting a correlated concept.
- `block3_citizen_adult_share` (immigration_citizenship): Not kept. VIP 1.401, turnout correlation 0.353, VIF 9.215. Excluded to keep the family from double-weighting a correlated concept.
- `block3_english_french_knowledge_share` (immigration_citizenship): Not kept. VIP 0.969, turnout correlation 0.265, VIF 5.821. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block4_effective_mayoral_candidates_5pct` (mayoral_competitiveness): Kept. VIP 1.907, turnout correlation -0.535, VIF 39.781. Kept as a theory/common-sense representative and checked against diagnostics.
- `block4_mayoral_top_two_margin` (mayoral_competitiveness): Kept. VIP 1.151, turnout correlation 0.288, VIF inf. Kept as a theory/common-sense representative and checked against diagnostics.
- `block4_mayoral_vote_fragmentation` (mayoral_competitiveness): Not kept. VIP 1.775, turnout correlation -0.495, VIF 55.498. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block4_mayoral_candidate_count_5pct` (mayoral_competitiveness): Not kept. VIP 0.584, turnout correlation -0.107, VIF 1.952. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block4_mayoral_winner_margin` (mayoral_competitiveness): Not kept. VIP 1.151, turnout correlation 0.288, VIF inf. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block4_provincial_margin` (provincial_competitiveness): Kept. VIP 0.802, turnout correlation 0.184, VIF 4.606. Kept as a theory/common-sense representative and checked against diagnostics.
- `block4_provincial_party_count_5pct` (provincial_competitiveness): Not kept. VIP 0.688, turnout correlation -0.150, VIF 2.354. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block4_effective_provincial_parties_5pct` (provincial_competitiveness): Not kept. VIP 0.529, turnout correlation -0.052, VIF 89.222. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block4_provincial_vote_fragmentation` (provincial_competitiveness): Not kept. VIP 0.530, turnout correlation -0.061, VIF 99.928. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block2_same_address_5yr_share` (residential_stability): Kept. VIP 0.644, turnout correlation -0.120, VIF 14.819. Kept as a theory/common-sense representative and checked against diagnostics.
- `block2_same_address_1yr_share` (residential_stability): Not kept. VIP 0.748, turnout correlation -0.156, VIF 13.103. Excluded to keep the family from double-weighting a correlated concept.
- `block5_shelter_access_1200m` (service_access): Kept. VIP 0.728, turnout correlation 0.139, VIF 2.882. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_library_access_1200m` (service_access): Kept. VIP 0.630, turnout correlation 0.137, VIF 4.646. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_community_centre_access_1200m` (service_access): Kept. VIP 0.495, turnout correlation -0.037, VIF 2.138. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_library_count_1200m` (service_access): Not kept. VIP 0.990, turnout correlation 0.246, VIF 4.853. Excluded to keep the family from double-weighting a correlated concept.
- `block5_shelter_count_1200m` (service_access): Not kept. VIP 0.818, turnout correlation 0.082, VIF 3.889. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_shelter_nearest_m` (service_access): Not kept. VIP 0.718, turnout correlation -0.146, VIF 3.357. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_library_nearest_m` (service_access): Not kept. VIP 0.680, turnout correlation -0.137, VIF 3.964. Excluded to keep the family from double-weighting a correlated concept.
- `block5_park_count_1200m` (service_access): Not kept. VIP 0.581, turnout correlation 0.108, VIF 1.800. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_community_centre_nearest_m` (service_access): Not kept. VIP 0.558, turnout correlation 0.063, VIF 2.461. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_community_centre_count_1200m` (service_access): Not kept. VIP 0.424, turnout correlation -0.040, VIF 1.644. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_park_nearest_m` (service_access): Not kept. VIP 0.366, turnout correlation 0.066, VIF 1.264. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_ksi_collision_events_2021_2025_per_1000` (service_contact): Kept. VIP 0.933, turnout correlation 0.157, VIF 3.371. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_social_housing_share` (service_contact): Kept. VIP 0.747, turnout correlation -0.191, VIF 2.642. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_requests_311_per_1000` (service_contact): Kept. VIP 0.765, turnout correlation 0.140, VIF 10.169. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_development_applications_2021_2025_per_1000` (service_contact): Kept. VIP 0.690, turnout correlation 0.095, VIF 5.890. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_school_age_5_17_share` (service_contact): Kept. VIP 0.882, turnout correlation -0.194, VIF 46.384. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_requests_311_2023_2025_estimated_count` (service_contact): Not kept. VIP 0.844, turnout correlation 0.168, VIF 11.940. Excluded to keep the family from double-weighting a correlated concept.
- `block5_development_applications_2021_2025` (service_contact): Not kept. VIP 0.666, turnout correlation 0.120, VIF 3.590. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_ksi_collision_events_2021_2025` (service_contact): Not kept. VIP 0.618, turnout correlation -0.050, VIF 3.028. Excluded to keep the cleaned model interpretable and lower dimensional.
- `block5_no_car_household_share` (transportation_access): Kept. VIP 0.832, turnout correlation 0.174, VIF inf. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_transit_commute_share_preferred` (transportation_access): Kept. VIP 0.538, turnout correlation -0.002, VIF inf. Kept as a theory/common-sense representative and checked against diagnostics.
- `block5_tts_overlap_area_m2` (transportation_access): Not kept. VIP 0.649, turnout correlation -0.102, VIF 6.638. Excluded to keep the family from double-weighting a correlated concept.
- `block5_tts_no_car_household_share` (transportation_access): Not kept. VIP 0.832, turnout correlation 0.174, VIF inf. Excluded because it is near-duplicate/inverse/compositional with selected family information.
- `block5_tts_transit_trip_share` (transportation_access): Not kept. VIP 0.538, turnout correlation -0.002, VIF inf. Excluded because it is near-duplicate/inverse/compositional with selected family information.

## Final Interpretation

The cleaned PLS model should be treated as the main supervised dimension-reduction candidate. It keeps turnout supervision through PLS, while reducing the most obvious double-counting problems that appear in the full model. If an inverse pair performs almost identically, the final choice should be explained as interpretive rather than purely predictive. For example, renter share and owner share can encode nearly the same tenure gradient with opposite signs; keeping renter share makes the urban turnout story easier to discuss without implying that owner share is empirically irrelevant.

The remaining ambiguous cases are valuable rather than embarrassing. They show where the data cannot clearly distinguish one representative from another, especially inside housing form, service access, and election-competitiveness families. Those should be reported as sensitivity areas, not hidden.
