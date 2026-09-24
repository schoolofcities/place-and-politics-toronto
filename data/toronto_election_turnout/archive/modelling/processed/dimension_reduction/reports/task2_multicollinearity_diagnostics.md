# Step 2: Multicollinearity and Redundancy Diagnostics

This step diagnoses the full predictor universe used in Step 1. It does not decide the final variable set by itself. It flags where the same concept is probably being counted more than once.

## Headline Findings

- Predictor count checked: 70
- High-correlation pairs with |r| >= 0.70: 51
- Near duplicate or inverse pairs with |r| >= 0.95: 10
- Variables with VIF >= 10: 43
- Variables with VIF >= 5: 51

## Highest VIF Variables

| Variable | Family | VIF |
| --- | --- | --- |
| `block2_apartment_lt5_storeys_count` | housing_form_density | inf |
| `block2_apartment_total_count` | housing_form_density | inf |
| `block5_no_car_household_share` | transportation_access | inf |
| `block5_transit_commute_share_preferred` | transportation_access | inf |
| `block5_tts_no_car_household_share` | transportation_access | inf |
| `block5_tts_transit_trip_share` | transportation_access | inf |
| `block4_mayoral_top_two_margin` | mayoral_competitiveness | inf |
| `block2_apartment_duplex_count` | housing_form_density | inf |
| `block2_apartment_5plus_storeys_count` | housing_form_density | inf |
| `block4_mayoral_winner_margin` | mayoral_competitiveness | inf |
| `block2_renter_share` | housing_tenure | 8100.055 |
| `block2_owner_share` | housing_tenure | 8033.196 |
| `block2_structural_type_total_dwellings` | housing_form_density | 284.495 |
| `block2_condo_status_total_dwellings` | housing_form_density | 259.010 |
| `block4_federal_vote_fragmentation` | federal_competitiveness | 163.980 |
| `block4_effective_federal_parties_5pct` | federal_competitiveness | 154.937 |
| `block1_age_65_plus_share` | age_structure | 146.305 |
| `block1_age_18_34_share` | age_structure | 129.804 |
| `block4_provincial_vote_fragmentation` | provincial_competitiveness | 99.928 |
| `block4_effective_provincial_parties_5pct` | provincial_competitiveness | 89.222 |


## Strongest Correlated Pairs

| A | B | r | Flag |
| --- | --- | --- | --- |
| `block5_no_car_household_share` | `block5_tts_no_car_household_share` | 1.000 | near_duplicate_or_inverse |
| `block5_transit_commute_share_preferred` | `block5_tts_transit_trip_share` | 1.000 | near_duplicate_or_inverse |
| `block4_mayoral_top_two_margin` | `block4_mayoral_winner_margin` | 1.000 | near_duplicate_or_inverse |
| `block2_renter_share` | `block2_owner_share` | -1.000 | near_duplicate_or_inverse |
| `block2_structural_type_total_dwellings` | `block2_condo_status_total_dwellings` | 0.994 | near_duplicate_or_inverse |
| `block4_effective_federal_parties_5pct` | `block4_federal_vote_fragmentation` | 0.994 | near_duplicate_or_inverse |
| `block4_effective_provincial_parties_5pct` | `block4_provincial_vote_fragmentation` | 0.989 | near_duplicate_or_inverse |
| `block2_population_density_per_km2` | `block2_apartments_per_km2` | 0.971 | near_duplicate_or_inverse |
| `block4_effective_mayoral_candidates_5pct` | `block4_mayoral_vote_fragmentation` | 0.967 | near_duplicate_or_inverse |
| `block2_apartment_5plus_storeys_count` | `block2_apartment_total_count` | 0.960 | near_duplicate_or_inverse |
| `block2_same_address_1yr_share` | `block2_same_address_5yr_share` | 0.928 | strong |
| `block2_structural_type_total_dwellings` | `block2_apartment_total_count` | 0.924 | strong |
| `block2_apartment_total_count` | `block2_condo_status_total_dwellings` | 0.923 | strong |
| `block1_age_65_plus_share` | `block1_median_age` | 0.918 | strong |
| `block3_immigrant_share` | `block3_non_official_mother_tongue_share` | 0.916 | strong |
| `block3_non_citizen_share` | `block3_citizen_adult_share` | -0.913 | strong |
| `block3_recent_immigrant_share` | `block3_non_citizen_share` | 0.899 | strong |
| `block3_immigrant_share` | `block3_visible_minority_share` | 0.889 | strong |
| `block2_apartment_5plus_storeys_count` | `block2_condominium_dwellings_count` | 0.876 | strong |
| `block2_apartment_5plus_storeys_count` | `block2_condo_status_total_dwellings` | 0.865 | strong |
| `block2_structural_type_total_dwellings` | `block2_apartment_5plus_storeys_count` | 0.865 | strong |
| `block2_apartment_share` | `block2_detached_share` | -0.856 | strong |
| `block2_apartments_per_km2` | `block2_condos_per_km2` | 0.851 | strong |
| `block2_apartment_total_count` | `block2_condominium_dwellings_count` | 0.844 | moderate_high |
| `block1_age_18_34_share` | `block2_same_address_1yr_share` | -0.827 | moderate_high |


## Plain-Language Redundancy Summary

The most important high-correlation or inverse relationships are no car household share and TTS no car household share with correlation 1.000; transit commute share and TTS transit trip share with correlation 1.000; mayoral top two margin and mayoral winner margin with correlation 1.000; renter share and owner share with correlation -1.000; structural type total dwellings and condo status total dwellings with correlation 0.994; effective federal parties above five percent and federal vote fragmentation with correlation 0.994; effective provincial parties above five percent and provincial vote fragmentation with correlation 0.989; population density and apartments per square kilometre with correlation 0.971; effective mayoral candidates above five percent and mayoral vote fragmentation with correlation 0.967; apartment five plus storeys count and apartment total count with correlation 0.960. These are the relationships most likely to double-count the same social concept if they are fed into dimension reduction together.

## Family-Level Redundancy

| Family | Vars | Max |r| |
| --- | --- | --- |
| mayoral_competitiveness | 5 | 1.000 |
| transportation_access | 5 | 1.000 |
| housing_tenure | 2 | 1.000 |
| housing_form_density | 14 | 0.994 |
| federal_competitiveness | 4 | 0.994 |
| provincial_competitiveness | 4 | 0.989 |
| residential_stability | 2 | 0.928 |
| age_structure | 4 | 0.918 |
| immigration_citizenship | 7 | 0.916 |
| service_access | 11 | 0.808 |
| service_contact | 8 | 0.679 |
| household_class | 4 | 0.677 |


## Interpretation

The diagnostics confirm Zack's warning: the modelling table contains variables that are not merely correlated but sometimes structurally tied. Tenure is the clearest example because renter and owner shares are inverse codings of the same concept. Housing form and density also form a dense cluster, especially because apartment counts, apartment shares, condo variables, density variables, and total dwelling counts partly track the same urban form.

VIF is stricter than pairwise correlation because it asks whether a variable can be reconstructed from all other predictors together. High VIF does not mean the variable is unimportant; it means the model cannot cleanly separate its unique contribution from nearby variables. That is why Step 3 should use family comparisons rather than deleting variables mechanically by VIF.

The practical conclusion is that the final cleaned model should choose representatives from correlated families, then test substitutions and connected-family combinations. That preserves the idea that A may work better with D than with C, which pairwise correlation alone cannot discover.
