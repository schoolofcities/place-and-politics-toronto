# Step 4: Interaction Discovery After Cleaning

Step 4 tests interpretable interaction terms after the Step 3 family-cleaned model. The candidate pool is broader than the exact Step 3 model: it includes selected variables plus reasonable non-duplicate family alternatives. Variables removed as exact duplicates, inverse codings, or near-compositional redundancies are not reintroduced.

## Baseline vs Interaction-Augmented PLS

| Model | Predictors | Components | CV R2 | CV RMSE | Train R2 |
|---|---:|---:|---:|---:|---:|
| Step 3 cleaned PLS | 27 | 5 | 0.558 | 0.058 | 0.625 |
| Step 4 interaction PLS | 38 | 1 | 0.566 | 0.057 | 0.587 |

## Screening Rule

Each candidate interaction was tested by adding the interaction plus its main effects if those main effects were not already in the cleaned model. The screen used cross-validated PLS performance and the interaction term's VIP. I treated an interaction as promising only when it did not worsen CV RMSE and had interaction VIP around 0.8 or higher.

## Best Interaction Trials

| Interaction | Families | CV R2 | CV RMSE | VIP | Story |
| --- | --- | --- | --- | --- | --- |
| `block1_low_income_lim_at_share__x__block5_requests_311_per_1000` | household_class + service_contact | 0.618 | 0.054 | 0.954 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_bachelors_or_higher_25_64_share__x__block5_requests_311_per_1000` | household_class + service_contact | 0.607 | 0.055 | 0.775 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block1_unemployment_rate_share` | service_contact + household_class | 0.596 | 0.055 | 0.808 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_low_income_lim_at_share__x__block5_development_applications_2021_2025_per_1000` | household_class + service_contact | 0.595 | 0.055 | 0.645 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_average_household_size__x__block5_requests_311_per_1000` | household_class + service_contact | 0.593 | 0.055 | 0.711 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block3_non_official_mother_tongue_share` | service_contact + immigration_citizenship | 0.591 | 0.056 | 1.086 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |
| `block1_bachelors_or_higher_25_64_share__x__block1_median_age` | household_class + age_structure | 0.584 | 0.056 | 0.774 | Tests whether the class/household-size turnout pattern changes across age structure. |
| `block5_requests_311_per_1000__x__block3_immigrant_share` | service_contact + immigration_citizenship | 0.582 | 0.056 | 0.651 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |
| `block1_low_income_lim_at_share__x__block1_age_35_64_share` | household_class + age_structure | 0.582 | 0.056 | 0.933 | Tests whether the class/household-size turnout pattern changes across age structure. |
| `block1_average_household_size__x__block5_ksi_collision_events_2021_2025_per_1000` | household_class + service_contact | 0.581 | 0.056 | 0.827 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block5_transit_commute_share_preferred__x__block5_requests_311_2023_2025_estimated_count` | transportation_access + service_contact | 0.580 | 0.056 | 0.593 | Theory-screened cross-family interaction with interpretable main effects retained. |
| `block5_development_applications_2021_2025_per_1000__x__block3_immigrant_share` | service_contact + immigration_citizenship | 0.580 | 0.056 | 0.613 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |
| `block5_requests_311_per_1000__x__block3_non_official_mother_tongue_share` | service_contact + immigration_citizenship | 0.578 | 0.057 | 0.623 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |
| `block1_bachelors_or_higher_25_64_share__x__block5_requests_311_2023_2025_estimated_count` | household_class + service_contact | 0.577 | 0.057 | 0.618 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_bachelors_or_higher_25_64_share__x__block2_renter_share` | household_class + housing_tenure | 0.577 | 0.057 | 0.541 | Theory-screened cross-family interaction with interpretable main effects retained. |
| `block3_non_citizen_share__x__block5_development_applications_2021_2025_per_1000` | immigration_citizenship + service_contact | 0.577 | 0.057 | 0.403 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |
| `block1_age_65_plus_share__x__block1_average_household_size` | age_structure + household_class | 0.576 | 0.057 | 0.950 | Tests whether the class/household-size turnout pattern changes across age structure. |
| `block1_unemployment_rate_share__x__block5_requests_311_2023_2025_estimated_count` | household_class + service_contact | 0.576 | 0.057 | 0.629 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block3_visible_minority_share__x__block5_development_applications_2021_2025_per_1000` | immigration_citizenship + service_contact | 0.576 | 0.057 | 0.566 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |
| `block1_low_income_lim_at_share__x__block5_requests_311_2023_2025_estimated_count` | household_class + service_contact | 0.574 | 0.057 | 0.395 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_average_household_size__x__block5_development_applications_2021_2025_per_1000` | household_class + service_contact | 0.573 | 0.057 | 0.282 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_bachelors_or_higher_25_64_share__x__block5_development_applications_2021_2025_per_1000` | household_class + service_contact | 0.572 | 0.057 | 0.605 | Tests whether service-contact intensity has a different turnout meaning in higher-need or higher-resource areas. |
| `block1_age_65_plus_share__x__block1_bachelors_or_higher_25_64_share` | age_structure + household_class | 0.572 | 0.057 | 0.690 | Tests whether the class/household-size turnout pattern changes across age structure. |
| `block1_low_income_lim_at_share__x__block2_condo_share` | household_class + housing_form_density | 0.571 | 0.057 | 0.773 | Theory-screened cross-family interaction with interpretable main effects retained. |
| `block3_recent_immigrant_share__x__block5_development_applications_2021_2025_per_1000` | immigration_citizenship + service_contact | 0.571 | 0.057 | 0.352 | Tests whether service-contact intensity interacts with immigrant, language, or citizenship geography. |


## Interactions Retained In The Augmented PLS

| Interaction | VIP | Turnout corr | Direction |
| --- | --- | --- | --- |
| `block1_bachelors_or_higher_25_64_share__x__block4_effective_mayoral_candidates_5pct` | 0.863 | 0.240 | higher turnout |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block3_non_official_mother_tongue_share` | 0.846 | 0.235 | higher turnout |
| `block1_low_income_lim_at_share__x__block1_age_35_64_share` | 0.798 | -0.222 | lower turnout |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block1_unemployment_rate_share` | 0.767 | -0.213 | lower turnout |
| `block1_average_household_size__x__block1_age_35_64_share` | 0.753 | 0.210 | higher turnout |
| `block1_average_household_size__x__block5_ksi_collision_events_2021_2025_per_1000` | 0.725 | -0.202 | lower turnout |
| `block1_low_income_lim_at_share__x__block5_requests_311_per_1000` | 0.704 | 0.196 | higher turnout |
| `block1_age_65_plus_share__x__block1_average_household_size` | 0.572 | -0.159 | lower turnout |


## Interpretation Of Retained Interactions

- bachelor or higher education share with effective mayoral candidates above five percent: this asks whether education or class resources change how local electoral fragmentation relates to turnout. It is useful for a story about whether complex local contests are easier to navigate in higher-resource places.
- KSI collisions per 1000 residents with non official mother tongue share: this asks whether service-contact geography has a different meaning in immigrant, language, or citizenship contexts. It may point to places where municipal service contact and civic participation are linked unevenly.
- low income share with age 35 to 64 share: this asks whether class or household structure has a different turnout relationship depending on the age profile of the tract. It helps separate youth, working-age, and older-adult versions of the turnout story.
- KSI collisions per 1000 residents with unemployment rate: this asks whether service-contact intensity is associated with turnout differently in higher-need or higher-resource places. It is especially relevant for interpreting 311 requests, development applications, and collision exposure as civic-contact context rather than simple services.
- average household size with age 35 to 64 share: this asks whether class or household structure has a different turnout relationship depending on the age profile of the tract. It helps separate youth, working-age, and older-adult versions of the turnout story.
- average household size with KSI collisions per 1000 residents: this asks whether service-contact intensity is associated with turnout differently in higher-need or higher-resource places. It is especially relevant for interpreting 311 requests, development applications, and collision exposure as civic-contact context rather than simple services.
- low income share with 311 requests per 1000 residents: this asks whether service-contact intensity is associated with turnout differently in higher-need or higher-resource places. It is especially relevant for interpreting 311 requests, development applications, and collision exposure as civic-contact context rather than simple services.
- age 65 plus share with average household size: this asks whether class or household structure has a different turnout relationship depending on the age profile of the tract. It helps separate youth, working-age, and older-adult versions of the turnout story.

## Reference Categories For Interactions

The interaction results mainly point to four conditional reference categories: class and service contact, education and local electoral fragmentation, language or immigrant geography and service contact, and age structure interacting with class or household size. These should not all become final hypotheses automatically. They are candidate story lines that can be checked against maps, plots, and substantive plausibility.

## Remaining VIF In Interaction Model

| Variable | Family | VIF |
| --- | --- | --- |
| `block1_age_18_34_share` | age_structure | 118.541 |
| `block1_age_65_plus_share` | age_structure | 103.655 |
| `block5_school_age_5_17_share` | service_contact | 45.526 |
| `block1_age_35_64_share` | age_structure | 38.511 |
| `block1_average_household_size` | household_class | 26.825 |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block1_unemployment_rate_share` | other | 16.688 |
| `block1_low_income_lim_at_share__x__block5_requests_311_per_1000` | other | 16.204 |
| `block2_apartment_share` | housing_form_density | 15.919 |
| `block5_ksi_collision_events_2021_2025_per_1000__x__block3_non_official_mother_tongue_share` | other | 15.433 |
| `block2_renter_share` | housing_tenure | 15.194 |
| `block3_non_citizen_share` | immigration_citizenship | 14.031 |
| `block1_average_household_size__x__block5_ksi_collision_events_2021_2025_per_1000` | other | 11.071 |
| `block2_condo_share` | housing_form_density | 10.652 |
| `block2_same_address_5yr_share` | residential_stability | 10.401 |
| `block3_recent_immigrant_share` | immigration_citizenship | 10.269 |


## Interpretation

Interactions should be used as story devices only when they describe a plausible conditional relationship. The strongest candidates here are not arbitrary products; they mainly ask whether the turnout penalty associated with social composition becomes sharper in places with particular housing form, electoral fragmentation, or service/contact contexts. If an interaction improves prediction only trivially, it should still be kept out of the final narrative unless it clarifies a substantive mechanism.
