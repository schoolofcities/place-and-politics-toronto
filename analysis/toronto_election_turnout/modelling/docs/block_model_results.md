# Blockwise CT Turnout Models

This exploratory pass runs 20 OLS models: five dependent variables by
four predictor blocks. Predictors come from Blocks 1-4 only; Blocks 5-6
are excluded because key variables remain missing or partially sourced.

Dependent variables use the curated CT participation fields with
`citizen_canadian_18over` as denominator.

P-values are normal approximations from a pure-Python OLS implementation
and should be treated as screening diagnostics, not publication-ready
inference.

## Model Fit

| Dependent variable | Block | N | Adjusted R2 | R2 | RMSE |
|---|---|---:|---:|---:|---:|
| outcome_municipal_participation_citizen_18plus | block_1_demographic | 583 | 0.6042039026 | 0.6096443988 | 0.06537532674 |
| outcome_municipal_participation_citizen_18plus | block_2_housing_stability | 583 | 0.2155578062 | 0.2276883556 | 0.09203618139 |
| outcome_municipal_participation_citizen_18plus | block_3_immigration_eligibility | 583 | 0.5488689781 | 0.5542949526 | 0.06979582816 |
| outcome_municipal_participation_citizen_18plus | block_4_competitiveness | 583 | 0.3897789381 | 0.3971183667 | 0.08117489121 |
| outcome_provincial_participation_citizen_18plus | block_1_demographic | 583 | 0.3859496623 | 0.3943902168 | 0.07248101457 |
| outcome_provincial_participation_citizen_18plus | block_2_housing_stability | 583 | 0.1627073789 | 0.175655203 | 0.08463712615 |
| outcome_provincial_participation_citizen_18plus | block_3_immigration_eligibility | 583 | 0.3142398522 | 0.3224878264 | 0.07659640699 |
| outcome_provincial_participation_citizen_18plus | block_4_competitiveness | 583 | 0.2462296449 | 0.2552956114 | 0.08030485517 |
| outcome_federal_participation_citizen_18plus | block_1_demographic | 583 | 0.34932642 | 0.3582703867 | 0.08033681084 |
| outcome_federal_participation_citizen_18plus | block_2_housing_stability | 583 | 0.1176396316 | 0.1312843796 | 0.09355262924 |
| outcome_federal_participation_citizen_18plus | block_3_immigration_eligibility | 583 | 0.2299026656 | 0.2391650047 | 0.08739886868 |
| outcome_federal_participation_citizen_18plus | block_4_competitiveness | 583 | 0.133162724 | 0.1435886019 | 0.0927260565 |
| outcome_federal_minus_municipal_participation | block_1_demographic | 583 | 0.1452488537 | 0.1569980103 | 0.08016991081 |
| outcome_federal_minus_municipal_participation | block_2_housing_stability | 583 | 0.196508166 | 0.2089332975 | 0.07772885819 |
| outcome_federal_minus_municipal_participation | block_3_immigration_eligibility | 583 | 0.2698166958 | 0.2785989692 | 0.07409817365 |
| outcome_federal_minus_municipal_participation | block_4_competitiveness | 583 | 0.1104286432 | 0.121127955 | 0.0817865615 |
| outcome_mean_participation_citizen_18plus | block_1_demographic | 583 | 0.5513620881 | 0.5575289322 | 0.05837295088 |
| outcome_mean_participation_citizen_18plus | block_2_housing_stability | 583 | 0.1795830099 | 0.1922698706 | 0.07893706705 |
| outcome_mean_participation_citizen_18plus | block_3_immigration_eligibility | 583 | 0.4277476849 | 0.4346304447 | 0.06592610871 |
| outcome_mean_participation_citizen_18plus | block_4_competitiveness | 583 | 0.3153362142 | 0.323571002 | 0.07211113673 |

## Best Block By Dependent Variable

- `outcome_municipal_participation_citizen_18plus`: `block_1_demographic` has the strongest adjusted R2 (0.6042039026).
- `outcome_provincial_participation_citizen_18plus`: `block_1_demographic` has the strongest adjusted R2 (0.3859496623).
- `outcome_federal_participation_citizen_18plus`: `block_1_demographic` has the strongest adjusted R2 (0.34932642).
- `outcome_federal_minus_municipal_participation`: `block_3_immigration_eligibility` has the strongest adjusted R2 (0.2698166958).
- `outcome_mean_participation_citizen_18plus`: `block_1_demographic` has the strongest adjusted R2 (0.5513620881).

## Top Predictors

### A_municipal_turnout__block_1_demographic
- dem_share_18_34: standardized beta -0.625640087, p~0
- dem_average_household_size: standardized beta -0.5574223487, p~0
- dem_bachelors_plus_share: standardized beta 0.3447636451, p~0

### A_municipal_turnout__block_2_housing_stability
- housing_renter_share: standardized beta -8.233204518, p~0.003918227996
- housing_owner_share: standardized beta -7.203744791, p~0.01154586765
- housing_apartment_share: standardized beta 1.138954706, p~0

### A_municipal_turnout__block_3_immigration_eligibility
- racialized_visible_minority_share: standardized beta -0.5250354099, p~2.309263891e-14
- immigration_immigrant_share: standardized beta -0.3038488894, p~0.004547510296
- language_english_french_knowledge_share: standardized beta -0.2040100351, p~3.556609091e-06

### A_municipal_turnout__block_4_competitiveness
- election_effective_mayoral_candidates_5pct: standardized beta -0.6417348515, p~1.006349837e-05
- election_mayoral_top_two_margin: standardized beta -0.2877605636, p~6.602185492e-07
- election_mayoral_vote_fragmentation: standardized beta -0.1569565446, p~0.3627465984

### B_provincial_turnout__block_1_demographic
- dem_average_household_size: standardized beta -0.6260694164, p~0
- dem_share_18_34: standardized beta -0.4139436194, p~1.34802492e-06
- dem_median_age: standardized beta -0.4008252652, p~0.001152344207

### B_provincial_turnout__block_2_housing_stability
- housing_renter_share: standardized beta -12.81530681, p~1.385886928e-05
- housing_owner_share: standardized beta -11.89158518, p~5.445900911e-05
- housing_apartment_share: standardized beta 1.065805202, p~2.864375404e-14

### B_provincial_turnout__block_3_immigration_eligibility
- racialized_visible_minority_share: standardized beta -0.5840399818, p~5.734079878e-12
- eligibility_citizen_adult_share: standardized beta -0.291315127, p~0.0006749255715
- immigration_non_citizen_share: standardized beta -0.1777389755, p~0.1866676205

### B_provincial_turnout__block_4_competitiveness
- election_effective_mayoral_candidates_5pct: standardized beta -0.5883320848, p~0.000269991891
- election_mayoral_top_two_margin: standardized beta -0.1467837592, p~0.02247424019
- election_federal_margin: standardized beta 0.1025157412, p~0.08997903334

### C_federal_turnout__block_1_demographic
- dem_average_household_size: standardized beta -0.5340671168, p~1.110223025e-15
- dem_share_18_34: standardized beta -0.4480612869, p~3.744638353e-07
- dem_median_age: standardized beta -0.2290763008, p~0.07113463739

### C_federal_turnout__block_2_housing_stability
- housing_renter_share: standardized beta -7.502036837, p~0.0131988585
- housing_owner_share: standardized beta -6.992579344, p~0.02079664341
- housing_recent_mover_share: standardized beta 0.9196826339, p~0.7323521475

### C_federal_turnout__block_3_immigration_eligibility
- immigration_non_citizen_share: standardized beta -0.606332175, p~2.129199325e-05
- racialized_visible_minority_share: standardized beta -0.5072498577, p~1.664052651e-08
- immigration_recent_immigrant_share: standardized beta 0.489096487, p~3.301408411e-07

### C_federal_turnout__block_4_competitiveness
- election_effective_mayoral_candidates_5pct: standardized beta -0.6758514328, p~9.542596154e-05
- election_mayoral_vote_fragmentation: standardized beta 0.2362887104, p~0.2503068233
- election_mayoral_top_two_margin: standardized beta -0.1736898047, p~0.01179152238

### D_federal_minus_municipal__block_1_demographic
- dem_share_18_34: standardized beta 0.23513001, p~0.01998579927
- dem_low_income_share: standardized beta 0.2337519559, p~0.0002549635224
- dem_bachelors_plus_share: standardized beta -0.2142945553, p~0.0003641074539

### D_federal_minus_municipal__block_2_housing_stability
- housing_renter_share: standardized beta 1.250029582, p~0.6651961475
- housing_condo_share: standardized beta 0.7368280376, p~3.916866831e-13
- housing_owner_share: standardized beta 0.601494332, p~0.8349346733

### D_federal_minus_municipal__block_3_immigration_eligibility
- immigration_non_citizen_share: standardized beta -0.5086070452, p~0.000250332593
- immigration_recent_immigrant_share: standardized beta 0.4326218816, p~3.523856658e-06
- eligibility_citizen_adult_share: standardized beta -0.3271665342, p~0.0002156144235

### D_federal_minus_municipal__block_4_competitiveness
- election_mayoral_vote_fragmentation: standardized beta 0.4594742362, p~0.02733441115
- election_mayoral_top_two_margin: standardized beta 0.1453526219, p~0.03749260107
- election_effective_provincial_parties_5pct: standardized beta -0.04799057636, p~0.4629293251

### E_mean_turnout__block_1_demographic
- dem_average_household_size: standardized beta -0.6464894385, p~0
- dem_share_18_34: standardized beta -0.5657942568, p~1.088018564e-14
- dem_median_age: standardized beta -0.3225304902, p~0.002214003583

### E_mean_turnout__block_2_housing_stability
- housing_renter_share: standardized beta -10.66397962, p~0.0002586834984
- housing_owner_share: standardized beta -9.733944522, p~0.0008463141479
- housing_apartment_share: standardized beta 1.163171899, p~0

### E_mean_turnout__block_3_immigration_eligibility
- racialized_visible_minority_share: standardized beta -0.6085320526, p~3.996802889e-15
- immigration_non_citizen_share: standardized beta -0.356134536, p~0.003774377421
- immigration_recent_immigrant_share: standardized beta 0.2278862364, p~0.005789016804

### E_mean_turnout__block_4_competitiveness
- election_effective_mayoral_candidates_5pct: standardized beta -0.7206596906, p~2.847184287e-06
- election_mayoral_top_two_margin: standardized beta -0.2324670001, p~0.0001491230872
- election_effective_federal_parties_5pct: standardized beta -0.0651093041, p~0.1791861641
