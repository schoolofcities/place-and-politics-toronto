# Latent Variable Interpretation Report: Mean Turnout

This report interprets the existing dimension-reduction outputs for mean CT turnout (`outcome_mean_participation_citizen_18plus`). No new models were fit. The analysis reads prior model summaries, loadings, VIP tables, interaction screens, and the existing CT model input.

## Report Structure

**Section 1: Main Findings.** Summarizes the overall latent-variable story for mean turnout and explains why the theory-cleaned PLS is the main interpretive model.

**Section 2: Cleaned PLS Latent Meanings.** Interprets the five cleaned PLS components, including their high/low sides, dominant variable families, and substantive meanings.

**Section 3: Cleaned PLS Model Results.** Reports model performance and the most important cleaned PLS variables by VIP, coefficient direction, and bivariate turnout correlation.

**Section 4: Direction Toward Turnout And Reference Categories.** Explains how the components relate to turnout and gives high/low reference CTs for each cleaned PLS component.

**Section 5: Interactions And Bundles.** Interprets the interaction-augmented PLS evidence, especially why service-contact variables matter conditionally rather than as simple standalone predictors.

**Section 6: Cleaned PLS Compared With Supervised PCA.** Compares the cleaned PLS latent interpretation with supervised PCA, highlighting shared reference categories, sign reversals, and PCA-specific additions.

**Section 7: Suggested Story.** Synthesizes the model interpretation into a coherent turnout narrative.

**Section 8: Robustness Across Model Types.** Places sparse PLS and PCA robustness evidence after the main story as supporting evidence.

**Section 9: Appendices.** Provides selected model, component, reference geography, PCA, and caution tables.

## Section 1: Main Findings

The strongest practical finding is that mean turnout is not organized by one isolated predictor. Across the existing PLS, sparse PLS, supervised PCA, and interaction checks, turnout is structured by bundled social geographies: immigration/citizenship/racialized composition, education and class resources, local electoral competitiveness, age and household composition, housing form, and a weaker but recurring urban-service/transportation layer. The latent variables matter because these dimensions overlap in Toronto CTs; they are not cleanly separable in ordinary single-variable rankings.

The best cross-validated latent candidate is the interaction-augmented PLS (`CV R2 0.566`, `CV RMSE 0.057`). However, the theory-cleaned PLS is nearly as strong (`CV R2 0.558`, `CV RMSE 0.058`) and is the better main interpretive model because it avoids the worst duplicate and inverse-variable double counting. Sparse PLS (`CV R2 0.560`) and supervised PCA (`CV R2 0.540`) are best used as robustness checks: they show that the same broad ingredients reappear even when the model is simplified or PCA-screened.

The main substantive axis is Component 1 of the cleaned PLS: education and electoral attachment on one side, and newcomer/racialized-fragmentation geography on the other. The high side of this component aligns with higher mean turnout; the low side aligns with lower mean turnout. That does not mean immigrant or racialized residents are inherently less politically engaged. At the CT level, the component is more plausibly capturing eligibility, settlement timing, campaign contact, institutional inclusion, household structure, and local political context together.

The other cleaned PLS components are still important, but they should be read differently. Components 2-5 describe the structure of Toronto's social geography after the strongest turnout gradient has already been extracted. They separate older stability from younger dense renter geography, vertical rental/newcomer urban form from larger-household stability, family/service need from older condo contexts, and service-contact variables from simple one-direction turnout claims. In short: Component 1 is the clearest turnout gradient; Components 2-5 help explain what kinds of places sit behind that gradient.

## Section 2: Cleaned PLS Latent Meanings

The theory-cleaned PLS should be the main interpretive model because it keeps most of the full model's predictive power while using 27 selected predictors instead of 70. It retains enough predictive power to be credible, while its components are much easier to interpret than the full 70-variable PLS.

### Component 1: education and electoral attachment versus newcomer/racialized-fragmentation geography

**Component 1: education and electoral attachment versus newcomer/racialized-fragmentation geography.** This is the main direct turnout axis. Its high side combines university education and larger election margins; its low side combines visible minority share, non-citizenship, recent immigration, larger household size, and mayoral fragmentation.

The high-score CTs on Component 1 are the clearest examples of the turnout-resource side of the model: they align with education, stronger electoral margins, and lower values on the newcomer/racialized-fragmentation bundle. The low-score CTs sit on the opposite side and have much lower mean turnout in the reference table. This is the component where the reference scores are most directly interpretable as a turnout gradient.

Most influential variables in this component:

| Variable | Variable family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| effective mayoral candidates above 5 percent | local mayoral competitiveness | low side | -0.408 | 1.787 | -0.535 | lower turnout |
| visible minority share | immigration, citizenship, and racialized geography | low side | -0.401 | 2.145 | -0.642 | lower turnout |
| bachelors or higher 25-64 share | education, income, and household class | high side | 0.360 | 1.847 | 0.554 | higher turnout |
| average household size | education, income, and household class | low side | -0.312 | 1.672 | -0.485 | lower turnout |
| mayoral top two margin | local mayoral competitiveness | high side | 0.280 | 1.084 | 0.288 | lower turnout |
| non citizen share | immigration, citizenship, and racialized geography | low side | -0.261 | 1.433 | -0.417 | lower turnout |
| recent immigrant share | immigration, citizenship, and racialized geography | low side | -0.227 | 1.137 | -0.317 | lower turnout |
| federal margin | federal competitiveness | high side | 0.225 | 0.967 | 0.272 | higher turnout |
| school age 5-17 share | service contact and local need | low side | -0.194 | 0.820 | -0.194 | higher turnout |
| no car household share | transportation access | high side | 0.186 | 0.741 | 0.174 | lower turnout |

Main variable-family composition:

| Latent theme | Share of absolute loading | Representative variables |
| --- | --- | --- |
| immigration, citizenship, and racialized geography | 0.206 | visible minority share; non citizen share; recent immigrant share |
| education, income, and household class | 0.186 | bachelors or higher 25-64 share; average household size; low income share |
| local mayoral competitiveness | 0.159 | effective mayoral candidates above 5 percent; mayoral top two margin |
| service contact and local need | 0.151 | school age 5-17 share; social housing share; requests 311 per 1000; development applications 2021-2025 per 1000; ksi collision events 2021-2025 per 1000 |
| civic/service proximity | 0.078 | shelter access within 1200m; library access within 1200m; community centre access within 1200m |

### Component 2: established older stability versus young dense carless-renter geography

**Component 2: established older stability versus young dense carless-renter geography.** This axis separates older, longer-residence CTs from younger, denser, more carless, renter/newcomer CTs. It is more compositional than directly predictive after Component 1.

Component 2 is best read as a contrast between older residential stability and younger dense renter/carless urban geography. The reference CTs show that both sides can include moderate turnout, which is why this component should not be read as a simple high-turnout/low-turnout axis. Its value is in describing the type of place after the main Component 1 turnout gradient has already done much of the explanatory work.

Most influential variables in this component:

| Variable | Variable family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| age 18-34 share | age structure | low side | -0.548 | 0.833 | -0.136 | lower turnout |
| no car household share | transportation access | low side | -0.447 | 0.741 | 0.174 | lower turnout |
| same address 5yr share | residential stability | high side | 0.407 | 0.575 | -0.120 | lower turnout |
| age 65 plus share | age structure | high side | 0.381 | 0.805 | 0.182 | higher turnout |
| population density per km2 | urban form and density | low side | -0.377 | 0.609 | 0.102 | higher turnout |
| non citizen share | immigration, citizenship, and racialized geography | low side | -0.375 | 1.433 | -0.417 | lower turnout |
| shelter access within 1200m | civic/service proximity | low side | -0.373 | 0.716 | 0.139 | lower turnout |
| renter share | renter/owner tenure | low side | -0.369 | 0.517 | -0.081 | lower turnout |
| apartment share | urban form and density | low side | -0.352 | 0.669 | 0.089 | higher turnout |
| low income share | education, income, and household class | low side | -0.341 | 0.770 | -0.199 | lower turnout |

Main variable-family composition:

| Latent theme | Share of absolute loading | Representative variables |
| --- | --- | --- |
| age structure | 0.141 | age 18-34 share; age 65 plus share |
| urban form and density | 0.138 | population density per km2; apartment share; condo share |
| immigration, citizenship, and racialized geography | 0.136 | non citizen share; recent immigrant share; visible minority share |
| transportation access | 0.108 | no car household share; transit commute share preferred |
| civic/service proximity | 0.098 | shelter access within 1200m; library access within 1200m; community centre access within 1200m |

### Component 3: vertical rental/newcomer urban form versus larger-household stability

**Component 3: vertical rental/newcomer urban form versus larger-household stability.** The high side is apartment/condo/renter/density with recent immigration and low income; the opposite side is more stable and larger-household. This helps distinguish different kinds of urban density.

Component 3 separates vertical rental/newcomer urban form from more stable and larger-household contexts. The high side combines apartments, condos, renters, density, recent immigration, and low income; the low side contains places that do not share that same vertical-rental profile. This helps distinguish dense urban form from the education/electoral-attachment pattern in Component 1.

Most influential variables in this component:

| Variable | Variable family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| apartment share | urban form and density | high side | 0.425 | 0.669 | 0.089 | higher turnout |
| average household size | education, income, and household class | low side | -0.354 | 1.672 | -0.485 | lower turnout |
| condo share | urban form and density | high side | 0.321 | 0.491 | 0.084 | higher turnout |
| recent immigrant share | immigration, citizenship, and racialized geography | high side | 0.311 | 1.137 | -0.317 | lower turnout |
| same address 5yr share | residential stability | low side | -0.297 | 0.575 | -0.120 | lower turnout |
| renter share | renter/owner tenure | high side | 0.291 | 0.517 | -0.081 | lower turnout |
| low income share | education, income, and household class | high side | 0.287 | 0.770 | -0.199 | lower turnout |
| population density per km2 | urban form and density | high side | 0.276 | 0.609 | 0.102 | higher turnout |
| non citizen share | immigration, citizenship, and racialized geography | high side | 0.232 | 1.433 | -0.417 | lower turnout |
| school age 5-17 share | service contact and local need | low side | -0.195 | 0.820 | -0.194 | higher turnout |

Main variable-family composition:

| Latent theme | Share of absolute loading | Representative variables |
| --- | --- | --- |
| urban form and density | 0.231 | apartment share; condo share; population density per km2 |
| education, income, and household class | 0.174 | average household size; low income share; bachelors or higher 25-64 share |
| immigration, citizenship, and racialized geography | 0.129 | recent immigrant share; non citizen share; visible minority share |
| service contact and local need | 0.110 | school age 5-17 share; requests 311 per 1000; development applications 2021-2025 per 1000; ksi collision events 2021-2025 per 1000; social housing share |
| transportation access | 0.083 | transit commute share preferred; no car household share |

### Component 4: family/social-housing/service need with electoral margins versus older condo geography

**Component 4: family/social-housing/service need with electoral margins versus older condo geography.** This is a mixed axis linking school-age share, social housing, and federal/provincial margins against older and condo-heavy contexts.

Component 4 is a mixed family/service-need and electoral-margin dimension. Its high side includes school-age share, social housing, renter share, residential stability, and federal/provincial margins; its low side includes older and condo-heavy contexts. Because the loading pattern mixes social need with electoral context, it is useful for story-building but should be described cautiously.

Most influential variables in this component:

| Variable | Variable family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| school age 5-17 share | service contact and local need | high side | 0.518 | 0.820 | -0.194 | higher turnout |
| provincial margin | provincial competitiveness | high side | 0.399 | 0.675 | 0.184 | higher turnout |
| federal margin | federal competitiveness | high side | 0.399 | 0.967 | 0.272 | higher turnout |
| condo share | urban form and density | low side | -0.347 | 0.491 | 0.084 | higher turnout |
| social housing share | service contact and local need | high side | 0.340 | 0.674 | -0.191 | lower turnout |
| age 65 plus share | age structure | low side | -0.318 | 0.805 | 0.182 | higher turnout |
| same address 5yr share | residential stability | high side | 0.256 | 0.575 | -0.120 | lower turnout |
| renter share | renter/owner tenure | high side | 0.249 | 0.517 | -0.081 | lower turnout |
| transit commute share preferred | transportation access | high side | 0.223 | 0.327 | -0.002 | higher turnout |
| age 18-34 share | age structure | low side | -0.213 | 0.833 | -0.136 | lower turnout |

Main variable-family composition:

| Latent theme | Share of absolute loading | Representative variables |
| --- | --- | --- |
| service contact and local need | 0.240 | school age 5-17 share; social housing share; development applications 2021-2025 per 1000; requests 311 per 1000; ksi collision events 2021-2025 per 1000 |
| age structure | 0.110 | age 65 plus share; age 18-34 share |
| urban form and density | 0.093 | condo share; population density per km2; apartment share |
| provincial competitiveness | 0.083 | provincial margin |
| federal competitiveness | 0.083 | federal margin |

### Component 5: service-contact/road-exposure and condo-education versus rental/service-access vulnerability

**Component 5: service-contact/road-exposure and condo-education versus rental/service-access vulnerability.** This is the most ambiguous cleaned component. It mainly says that service-contact variables matter as part of urban context rather than as simple standalone turnout predictors.

Component 5 is the most tentative component. It places service-contact and road-exposure indicators alongside condo and education signals, while the opposite side includes community-centre/library access, social housing, renters, no-car households, and residential stability. This is less a standalone turnout mechanism than a reminder that service context changes meaning depending on the social geography around it.

Most influential variables in this component:

| Variable | Variable family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| community centre access within 1200m | civic/service proximity | low side | -0.451 | 0.224 | -0.037 | lower turnout |
| ksi collision events 2021-2025 per 1000 | service contact and local need | high side | 0.346 | 0.592 | 0.157 | higher turnout |
| social housing share | service contact and local need | low side | -0.323 | 0.674 | -0.191 | lower turnout |
| condo share | urban form and density | high side | 0.320 | 0.491 | 0.084 | higher turnout |
| renter share | renter/owner tenure | low side | -0.317 | 0.517 | -0.081 | lower turnout |
| no car household share | transportation access | low side | -0.273 | 0.741 | 0.174 | lower turnout |
| library access within 1200m | civic/service proximity | low side | -0.261 | 0.552 | 0.137 | lower turnout |
| bachelors or higher 25-64 share | education, income, and household class | high side | 0.259 | 1.847 | 0.554 | higher turnout |
| age 65 plus share | age structure | low side | -0.256 | 0.805 | 0.182 | higher turnout |
| requests 311 per 1000 | service contact and local need | high side | 0.253 | 0.527 | 0.140 | lower turnout |

Main variable-family composition:

| Latent theme | Share of absolute loading | Representative variables |
| --- | --- | --- |
| service contact and local need | 0.216 | ksi collision events 2021-2025 per 1000; social housing share; requests 311 per 1000; development applications 2021-2025 per 1000; school age 5-17 share |
| civic/service proximity | 0.146 | community centre access within 1200m; library access within 1200m; shelter access within 1200m |
| urban form and density | 0.113 | condo share; population density per km2; apartment share |
| immigration, citizenship, and racialized geography | 0.100 | recent immigrant share; non citizen share; visible minority share |
| education, income, and household class | 0.098 | bachelors or higher 25-64 share; low income share; average household size |


## Section 3: Cleaned PLS Model Results

The table below gives the main model-level results. The interaction-augmented PLS has the best cross-validated fit, but the cleaned PLS is the main interpretive model because it is almost as predictive and produces five readable latent dimensions.

| Model | Predictors | Latent components | Cross-validated R2 | Cross-validated RMSE | Training R2 | Training RMSE |
| --- | --- | --- | --- | --- | --- | --- |
| Interaction-augmented PLS | 38 | 1 | 0.566 | 0.057 | 0.587 | 0.056 |
| Full unfiltered PLS | 70 | 12 | 0.565 | 0.057 | 0.693 | 0.048 |
| Sparse PLS | 27 | 5 | 0.560 | 0.058 | 0.624 | 0.053 |
| Theory-cleaned PLS | 27 | 5 | 0.558 | 0.058 | 0.625 | 0.053 |
| Supervised PCA | 15 | 8 | 0.540 | 0.059 | 0.569 | 0.057 |

The next table reports the most important variables in the cleaned PLS model. VIP values above 1 indicate above-average contribution to the supervised latent projection. The cleaned PLS coefficient gives the direction inside the cleaned PLS prediction; the bivariate correlation is included as a simpler reference point.

| Variable | Variable family | VIP | Cleaned PLS coefficient | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- |
| visible minority share | immigration, citizenship, and racialized geography | 2.145 | -0.097 | -0.642 | lower turnout |
| bachelors or higher 25-64 share | education, income, and household class | 1.847 | 0.109 | 0.554 | higher turnout |
| effective mayoral candidates above 5 percent | local mayoral competitiveness | 1.787 | -0.017 | -0.535 | lower turnout |
| average household size | education, income, and household class | 1.672 | -0.038 | -0.485 | lower turnout |
| non citizen share | immigration, citizenship, and racialized geography | 1.433 | -0.124 | -0.417 | lower turnout |
| recent immigrant share | immigration, citizenship, and racialized geography | 1.137 | -0.064 | -0.317 | lower turnout |
| mayoral top two margin | local mayoral competitiveness | 1.084 | -0.021 | 0.288 | lower turnout |
| federal margin | federal competitiveness | 0.967 | 0.061 | 0.272 | higher turnout |
| age 18-34 share | age structure | 0.833 | -0.188 | -0.136 | lower turnout |
| school age 5-17 share | service contact and local need | 0.820 | 0.166 | -0.194 | higher turnout |
| age 65 plus share | age structure | 0.805 | 0.096 | 0.182 | higher turnout |
| low income share | education, income, and household class | 0.770 | -0.052 | -0.199 | lower turnout |
| no car household share | transportation access | 0.741 | -0.011 | 0.174 | lower turnout |
| shelter access within 1200m | civic/service proximity | 0.716 | -0.012 | 0.139 | lower turnout |
| provincial margin | provincial competitiveness | 0.675 | 0.023 | 0.184 | higher turnout |

## Section 4: Direction Toward Turnout And Reference Categories

The strongest cleaned PLS VIP evidence points to lower mean turnout in CTs with higher visible minority share, larger household size, higher non-citizen share, higher recent immigrant share, and more fragmented mayoral competition. Higher bachelor-or-higher education is the strongest positive counterweight. Federal and provincial margin variables are weaker but generally point toward higher turnout in places with clearer/stronger party geography.

Only Component 1 behaves like a strong direct turnout gradient in the projection-based reference scores (`r about 0.67` with mean turnout). Components 2-5 should be read as secondary dimensions: they organize the remaining social geography after the primary turnout-resource/newcomer-fragmentation axis is accounted for.

### Reference Categories

The high/low ends of the cleaned PLS components should be read as reference categories, not individual-level claims. High component scores identify CTs whose standardized variable profile aligns with the existing component loadings; low scores identify the opposite side of the same latent axis.

These reference geographies help keep interpretation grounded. A component name should be checked against both its variable composition and the places sitting at the high and low ends. The reference scores are interpretive projections from existing loadings and standardized existing predictors, not newly fitted model scores.

### Component 1 Reference CTs

The high-score CTs on Component 1 are the clearest examples of the turnout-resource side of the model: they align with education, stronger electoral margins, and lower values on the newcomer/racialized-fragmentation bundle. The low-score CTs sit on the opposite side and have much lower mean turnout in the reference table. This is the component where the reference scores are most directly interpretable as a turnout gradient.

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| High Component 1 profile | CT 1.0 | 0.522 | 7.363 | 0.671 |
| High Component 1 profile | CT 2.0 | 0.727 | 6.716 | 0.671 |
| High Component 1 profile | CT 55.0 | 0.604 | 4.525 | 0.671 |
| High Component 1 profile | CT 44.02 | 0.579 | 4.449 | 0.671 |
| High Component 1 profile | CT 92.0 | 0.589 | 4.324 | 0.671 |
| High Component 1 profile | CT 60.0 | 0.545 | 4.023 | 0.671 |
| High Component 1 profile | CT 47.03 | 0.656 | 4.016 | 0.671 |
| High Component 1 profile | CT 18.0 | 0.596 | 3.975 | 0.671 |
| Low Component 1 profile | CT 316.05 | 0.360 | -3.679 | 0.671 |
| Low Component 1 profile | CT 316.06 | 0.346 | -3.686 | 0.671 |
| Low Component 1 profile | CT 312.04 | 0.365 | -3.751 | 0.671 |
| Low Component 1 profile | CT 367.01 | 0.407 | -3.970 | 0.671 |
| Low Component 1 profile | CT 249.05 | 0.346 | -3.996 | 0.671 |
| Low Component 1 profile | CT 250.05 | 0.399 | -4.246 | 0.671 |
| Low Component 1 profile | CT 314.01 | 0.425 | -4.529 | 0.671 |
| Low Component 1 profile | CT 316.03 | 0.391 | -5.074 | 0.671 |

### Component 2 Reference CTs

Component 2 is best read as a contrast between older residential stability and younger dense renter/carless urban geography. The reference CTs show that both sides can include moderate turnout, which is why this component should not be read as a simple high-turnout/low-turnout axis. Its value is in describing the type of place after the main Component 1 turnout gradient has already done much of the explanatory work.

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| High Component 2 profile | CT 223.01 | 0.595 | 4.746 | 0.000 |
| High Component 2 profile | CT 224.0 | 0.604 | 4.502 | 0.000 |
| High Component 2 profile | CT 232.0 | 0.584 | 4.488 | 0.000 |
| High Component 2 profile | CT 223.02 | 0.592 | 4.213 | 0.000 |
| High Component 2 profile | CT 802.01 | 0.557 | 4.151 | 0.000 |
| High Component 2 profile | CT 235.01 | 0.663 | 4.141 | 0.000 |
| High Component 2 profile | CT 226.0 | 0.595 | 4.058 | 0.000 |
| High Component 2 profile | CT 361.01 | 0.549 | 4.037 | 0.000 |
| Low Component 2 profile | CT 35.0 | 0.567 | -7.209 | 0.000 |
| Low Component 2 profile | CT 34.02 | 0.521 | -7.223 | 0.000 |
| Low Component 2 profile | CT 63.04 | 0.532 | -7.276 | 0.000 |
| Low Component 2 profile | CT 11.03 | 0.503 | -7.428 | 0.000 |
| Low Component 2 profile | CT 65.01 | 0.449 | -7.465 | 0.000 |
| Low Component 2 profile | CT 11.02 | 0.489 | -7.874 | 0.000 |
| Low Component 2 profile | CT 63.05 | 0.503 | -8.804 | 0.000 |
| Low Component 2 profile | CT 62.04 | 0.499 | -10.104 | 0.000 |

### Component 3 Reference CTs

Component 3 separates vertical rental/newcomer urban form from more stable and larger-household contexts. The high side combines apartments, condos, renters, density, recent immigration, and low income; the low side contains places that do not share that same vertical-rental profile. This helps distinguish dense urban form from the education/electoral-attachment pattern in Component 1.

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| High Component 3 profile | CT 62.04 | 0.499 | 8.153 | 0.000 |
| High Component 3 profile | CT 63.05 | 0.503 | 7.396 | 0.000 |
| High Component 3 profile | CT 300.01 | 0.464 | 6.616 | 0.000 |
| High Component 3 profile | CT 11.02 | 0.489 | 6.591 | 0.000 |
| High Component 3 profile | CT 136.02 | 0.593 | 6.467 | 0.000 |
| High Component 3 profile | CT 11.03 | 0.503 | 6.392 | 0.000 |
| High Component 3 profile | CT 128.06 | 0.623 | 6.365 | 0.000 |
| High Component 3 profile | CT 307.05 | 0.481 | 6.106 | 0.000 |
| Low Component 3 profile | CT 378.27 | 0.519 | -4.258 | 0.000 |
| Low Component 3 profile | CT 226.0 | 0.595 | -4.261 | 0.000 |
| Low Component 3 profile | CT 232.0 | 0.584 | -4.397 | 0.000 |
| Low Component 3 profile | CT 378.26 | 0.430 | -4.441 | 0.000 |
| Low Component 3 profile | CT 378.25 | 0.513 | -4.557 | 0.000 |
| Low Component 3 profile | CT 224.0 | 0.604 | -4.634 | 0.000 |
| Low Component 3 profile | CT 2.0 | 0.727 | -4.880 | 0.000 |
| Low Component 3 profile | CT 1.0 | 0.522 | -5.987 | 0.000 |

### Component 4 Reference CTs

Component 4 is a mixed family/service-need and electoral-margin dimension. Its high side includes school-age share, social housing, renter share, residential stability, and federal/provincial margins; its low side includes older and condo-heavy contexts. Because the loading pattern mixes social need with electoral context, it is useful for story-building but should be described cautiously.

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| High Component 4 profile | CT 341.03 | 0.514 | 4.899 | 0.000 |
| High Component 4 profile | CT 72.01 | 0.589 | 4.327 | 0.000 |
| High Component 4 profile | CT 260.05 | 0.353 | 4.165 | 0.000 |
| High Component 4 profile | CT 194.01 | 0.471 | 4.104 | 0.000 |
| High Component 4 profile | CT 75.0 | 0.682 | 3.679 | 0.000 |
| High Component 4 profile | CT 74.0 | 0.602 | 3.401 | 0.000 |
| High Component 4 profile | CT 248.02 | 0.337 | 3.311 | 0.000 |
| High Component 4 profile | CT 82.0 | 0.643 | 3.178 | 0.000 |
| Low Component 4 profile | CT 13.02 | 0.616 | -3.574 | 0.000 |
| Low Component 4 profile | CT 377.09 | 0.465 | -3.730 | 0.000 |
| Low Component 4 profile | CT 11.02 | 0.489 | -3.814 | 0.000 |
| Low Component 4 profile | CT 307.05 | 0.481 | -3.827 | 0.000 |
| Low Component 4 profile | CT 210.03 | 0.603 | -3.889 | 0.000 |
| Low Component 4 profile | CT 11.03 | 0.503 | -3.974 | 0.000 |
| Low Component 4 profile | CT 305.06 | 0.593 | -4.607 | 0.000 |
| Low Component 4 profile | CT 376.06 | 0.979 | -5.636 | 0.000 |

### Component 5 Reference CTs

Component 5 is the most tentative component. It places service-contact and road-exposure indicators alongside condo and education signals, while the opposite side includes community-centre/library access, social housing, renters, no-car households, and residential stability. This is less a standalone turnout mechanism than a reminder that service context changes meaning depending on the social geography around it.

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| High Component 5 profile | CT 1.0 | 0.522 | 11.942 | 0.000 |
| High Component 5 profile | CT 3.0 | 0.814 | 9.015 | 0.000 |
| High Component 5 profile | CT 296.0 | 0.495 | 5.684 | 0.000 |
| High Component 5 profile | CT 210.03 | 0.603 | 4.237 | 0.000 |
| High Component 5 profile | CT 213.02 | 0.713 | 4.123 | 0.000 |
| High Component 5 profile | CT 324.06 | 0.616 | 3.634 | 0.000 |
| High Component 5 profile | CT 248.03 | 0.371 | 3.410 | 0.000 |
| High Component 5 profile | CT 266.0 | 0.516 | 3.319 | 0.000 |
| Low Component 5 profile | CT 108.0 | 0.540 | -2.539 | 0.000 |
| Low Component 5 profile | CT 248.02 | 0.337 | -2.684 | 0.000 |
| Low Component 5 profile | CT 72.01 | 0.589 | -2.701 | 0.000 |
| Low Component 5 profile | CT 283.02 | 0.440 | -2.721 | 0.000 |
| Low Component 5 profile | CT 341.03 | 0.514 | -2.819 | 0.000 |
| Low Component 5 profile | CT 155.0 | 0.390 | -2.996 | 0.000 |
| Low Component 5 profile | CT 6.0 | 0.521 | -2.997 | 0.000 |
| Low Component 5 profile | CT 312.07 | 0.437 | -3.289 | 0.000 |


## Section 5: Interactions And Bundles

The interaction screen was already conducted in the prior workflow. The rows below are therefore not proposed future tests; they are screened interaction results, ranked by cross-validated performance. The strongest interaction candidate is low-income share with 311 requests per 1,000 residents, which reached `CV R2 0.618` and `CV RMSE 0.054`. Substantively, this means service-contact intensity should not be read as a simple standalone variable. It appears to matter differently depending on whether a CT is lower-income, higher-education, larger-household, higher-unemployment, immigrant/language, or otherwise socially distinct.

| Interaction term | Variable families | Best PLS components | Cross-validated R2 | Cross-validated RMSE | Interaction VIP | Interpretive result |
| --- | --- | --- | --- | --- | --- | --- |
| low income share x requests 311 per 1000 | education, income, and household class x service contact and local need | 4 | 0.618 | 0.054 | 0.954 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.618, CV RMSE 0.054, and interaction VIP 0.954; substantively, it suggests that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts. |
| bachelors or higher 25-64 share x requests 311 per 1000 | education, income, and household class x service contact and local need | 5 | 0.607 | 0.055 | 0.775 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.607, CV RMSE 0.055, and interaction VIP 0.775; substantively, it suggests that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts. |
| ksi collision events 2021-2025 per 1000 x unemployment rate share | service contact and local need x education, income, and household class | 4 | 0.596 | 0.055 | 0.808 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.596, CV RMSE 0.055, and interaction VIP 0.808; substantively, it suggests that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts. |
| low income share x development applications 2021-2025 per 1000 | education, income, and household class x service contact and local need | 5 | 0.595 | 0.055 | 0.645 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.595, CV RMSE 0.055, and interaction VIP 0.645; substantively, it suggests that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts. |
| average household size x requests 311 per 1000 | education, income, and household class x service contact and local need | 5 | 0.593 | 0.055 | 0.711 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.593, CV RMSE 0.055, and interaction VIP 0.711; substantively, it suggests that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts. |
| ksi collision events 2021-2025 per 1000 x non official mother tongue share | service contact and local need x immigration, citizenship, and racialized geography | 5 | 0.591 | 0.056 | 1.086 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.591, CV RMSE 0.056, and interaction VIP 1.086; substantively, it suggests that service-contact indicators may work differently in immigrant, language, or citizenship geographies. |
| bachelors or higher 25-64 share x median age | education, income, and household class x age structure | 5 | 0.584 | 0.056 | 0.774 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.584, CV RMSE 0.056, and interaction VIP 0.774; substantively, it suggests that class and education patterns are conditioned by local age structure. |
| requests 311 per 1000 x immigrant share | service contact and local need x immigration, citizenship, and racialized geography | 6 | 0.582 | 0.056 | 0.651 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.582, CV RMSE 0.056, and interaction VIP 0.651; substantively, it suggests that service-contact indicators may work differently in immigrant, language, or citizenship geographies. |
| low income share x age 35-64 share | education, income, and household class x age structure | 5 | 0.582 | 0.056 | 0.933 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.582, CV RMSE 0.056, and interaction VIP 0.933; substantively, it suggests that class and education patterns are conditioned by local age structure. |
| average household size x ksi collision events 2021-2025 per 1000 | education, income, and household class x service contact and local need | 4 | 0.581 | 0.056 | 0.827 | Screened interaction was already tested in the prior workflow. It reached CV R2 0.581, CV RMSE 0.056, and interaction VIP 0.827; substantively, it suggests that service-contact intensity is not neutral: it has a different turnout meaning in lower-income, higher-education, larger-household, or higher-unemployment contexts. |

The important pattern is not just the top individual interaction. Several of the strongest interactions pair household/class variables with service-contact variables, especially 311 requests, KSI collision rates, and development applications. A second cluster links service-contact variables with immigrant, language, or citizenship geography. These results support a bundled interpretation: local service demand, neighbourhood change, and civic infrastructure may have different turnout meanings in different social geographies.

For the story, this means service contact should not be described only as "more 311 equals more turnout" or "less 311 equals lower turnout." Its meaning changes with class, need, and settlement context. The more defensible phrasing is that service-contact intensity appears as part of a broader civic-demand or neighbourhood-condition bundle, and the interaction-augmented PLS performs best because it lets that conditional structure enter the model.

## Section 6: Cleaned PLS Compared With Supervised PCA

Supervised PCA is useful here because it offers a familiar comparison point. It first screens variables by turnout association and then applies PCA to the screened set. That makes it less directly supervised than PLS after the screen, but easier to interpret as a covariance structure among turnout-relevant variables. The main question is whether PCA uncovers the same latent geography as cleaned PLS, or whether it separates the story in a different way.

The strongest similarity is that both models recover the same main reference category: education and electoral attachment versus newcomer/racialized/citizenship and household-fragmentation geography. Cleaned PLS Component 1 puts bachelor-or-higher education, mayoral margin, and federal margin on one side, while visible minority share, non-citizenship, recent immigration, larger household size, and effective mayoral candidates above 5 percent sit on the other. Supervised PCA Component 1 captures a very similar contrast, but with the signs reversed: visible minority share, effective mayoral candidates above 5 percent, and average household size load positively, while bachelor-or-higher education, mayoral top-two margin, and federal margin load negatively. This is still a similarity, not a contradiction, because component signs are arbitrary; the two models are describing the same opposing reference categories.

The second similarity is that both models repeatedly return the same broad variable families: immigration/citizenship/racialized geography, education and household class, local electoral competitiveness, service contact, age, and transportation access. The exact component numbers differ, but the reference categories are stable. For example, age 65 plus share, low income share, no-car households, school-age share, social housing, KSI collisions, and provincial/federal margins all appear as important in PCA even when they are secondary or lower-VIP terms in cleaned PLS.

The main difference is how the models distribute these ideas across components. Cleaned PLS is turnout-supervised and therefore concentrates the main turnout story into Component 1, then uses Components 2-5 to organize secondary social geography. Supervised PCA spreads the same variables across more components: service need, KSI collisions, social housing, age, and provincial/federal margins become more visible as separate PCA contrasts. This does not mean PCA has found a stronger turnout model; its predictive performance is weaker. But it does mean PCA is useful for checking what cleaned PLS may compress into secondary components or lower-ranked variables.

The most important additions from supervised PCA are service-contact and age contrasts. KSI collisions per 1,000, social housing share, age 65 plus share, provincial margin, and school-age share are among the highest-loading PCA variables. Cleaned PLS includes these variables, but its main interpretation is dominated by the Component 1 education/newcomer-fragmentation axis. PCA therefore adds a helpful caution: the turnout story should not ignore service need, road-exposure context, age structure, and social housing simply because they are not the strongest cleaned-PLS VIP terms.

Shared and distinct high-ranking variables:

| Variable | In cleaned PLS top terms | In supervised PCA top terms | Variable family |
| --- | --- | --- | --- |
| age 65 plus share | True | True | age structure |
| average household size | True | True | education, income, and household class |
| bachelors or higher 25-64 share | True | True | education, income, and household class |
| effective mayoral candidates above 5 percent | True | True | local mayoral competitiveness |
| federal margin | True | True | federal competitiveness |
| low income share | True | True | education, income, and household class |
| mayoral top two margin | True | True | local mayoral competitiveness |
| no car household share | True | True | transportation access |
| non citizen share | True | True | immigration, citizenship, and racialized geography |
| provincial margin | True | True | provincial competitiveness |
| recent immigrant share | True | True | immigration, citizenship, and racialized geography |
| school age 5-17 share | True | True | service contact and local need |
| visible minority share | True | True | immigration, citizenship, and racialized geography |
| age 18-34 share | True | False | age structure |
| shelter access within 1200m | True | False | civic/service proximity |
| ksi collision events 2021-2025 per 1000 | False | True | service contact and local need |
| social housing share | False | True | service contact and local need |

Highest-loading supervised PCA variables:

| Variable | Variable family | Maximum absolute PCA loading |
| --- | --- | --- |
| ksi collision events 2021-2025 per 1000 | service contact and local need | 0.633 |
| age 65 plus share | age structure | 0.630 |
| mayoral top two margin | local mayoral competitiveness | 0.554 |
| bachelors or higher 25-64 share | education, income, and household class | 0.513 |
| social housing share | service contact and local need | 0.498 |
| provincial margin | provincial competitiveness | 0.488 |
| low income share | education, income, and household class | 0.434 |
| effective mayoral candidates above 5 percent | local mayoral competitiveness | 0.430 |
| no car household share | transportation access | 0.403 |
| visible minority share | immigration, citizenship, and racialized geography | 0.402 |
| federal margin | federal competitiveness | 0.401 |
| non citizen share | immigration, citizenship, and racialized geography | 0.396 |
| recent immigrant share | immigration, citizenship, and racialized geography | 0.389 |
| school age 5-17 share | service contact and local need | 0.358 |
| average household size | education, income, and household class | 0.355 |

## Section 7: Suggested Story

Mean turnout in Toronto CTs appears highest where the latent geography combines education, clearer electoral attachment, and forms of civic embeddedness. In the cleaned PLS, this appears most clearly in Component 1, where bachelor-or-higher education and stronger election margins sit opposite visible minority share, non-citizenship, recent immigration, larger household size, and mayoral fragmentation. This is the strongest and most direct turnout-facing result of the latent-variable analysis.

Lower mean turnout is most consistently associated with CTs where newcomer/racialized/citizenship geography overlaps with larger households and fragmented local electoral competition. This should be interpreted carefully. The model is not identifying individual political interest or individual willingness to vote. It is describing places where eligibility, settlement timing, language/citizenship context, campaign contact, institutional familiarity, and household/community structure may combine to produce lower observed turnout.

Education is the strongest positive counterweight in the results. It appears with high VIP in cleaned PLS, sparse PLS, supervised PCA, and robustness checks. This suggests that educational resources may proxy civic skills, political information access, institutional familiarity, or class position. But education does not operate alone: in the latent structure, it sits alongside election margins and against several citizenship/settlement variables. That is why the story should be about a resource-and-attachment geography rather than "education alone raises turnout."

The secondary components deepen the geographic story. Older stability is not identical to high turnout, dense apartment/condo geography is not a single political type, and service-contact variables are not simple signs of participation or disengagement. Components 2-5 show that Toronto's turnout geography contains multiple kinds of density, multiple kinds of stability, and multiple kinds of service context. This helps explain why ordinary one-variable rankings can feel thin: the politically meaningful object is often the combination of variables, not one variable by itself.

The interaction results add one more layer to the story. The best-performing model overall is the interaction-augmented PLS, and its strongest screened interactions involve class/household variables with service-contact measures. This implies that neighbourhood condition and service demand matter conditionally: 311 requests, KSI collisions, or development pressure may not have one stable meaning across all CTs. Their turnout meaning changes depending on income, education, household structure, age, and immigrant/citizenship geography.

The supervised PCA comparison adds a final robustness note. PCA confirms the main cleaned-PLS divide even when the signs are reversed: education and electoral margins sit opposite visible minority share, household size, non-citizenship, recent immigration, and local electoral fragmentation. At the same time, PCA makes service-contact and age variables more visible, especially KSI collisions, social housing, age 65 plus share, school-age share, and provincial/federal margins. So the final story should keep both layers: the primary turnout-resource/newcomer-fragmentation axis, and a secondary layer about service need, age, and urban condition.

The substantive contribution of the latent-variable analysis is therefore to turn the project away from a simple predictor ranking. It shows that turnout is structured by combinations: newcomer/racialized/citizenship geographies overlap with household composition and class; education and electoral attachment offset part of that pattern; local electoral competitiveness has a surprisingly strong place in the same latent space; and service-contact variables become most meaningful when read through interactions with class, need, and settlement context.

## Section 8: Robustness Across Model Types

Supervised PCA independently screens to a compact set and still recovers the same broad ingredients:

- Component 1 concentrates immigration, citizenship, and racialized geography, education, income, and household class, local mayoral competitiveness. Positive side: effective mayoral candidates above 5 percent, visible minority share, average household size, non citizen share. Negative side: bachelors or higher 25-64 share, mayoral top two margin, federal margin.
- Component 2 concentrates immigration, citizenship, and racialized geography, education, income, and household class, service contact and local need. Positive side: average household size, school age 5-17 share, age 65 plus share. Negative side: low income share, no car household share, non citizen share, recent immigrant share.
- Component 3 concentrates service contact and local need, education, income, and household class, immigration, citizenship, and racialized geography. Positive side: social housing share, federal margin, provincial margin, school age 5-17 share. Negative side: bachelors or higher 25-64 share, age 65 plus share.
- Component 4 concentrates service contact and local need, age structure, education, income, and household class. Positive side: recent immigrant share, school age 5-17 share, non citizen share, mayoral top two margin. Negative side: age 65 plus share, ksi collision events 2021-2025 per 1000, social housing share, low income share.
- Component 5 concentrates service contact and local need, immigration, citizenship, and racialized geography, local mayoral competitiveness. Positive side: ksi collision events 2021-2025 per 1000, provincial margin, mayoral top two margin, average household size. Negative side: social housing share, no car household share, effective mayoral candidates above 5 percent.

Sparse PLS also keeps the same strongest signals under a simpler component constraint. Its highest VIP variables are:

| Variable | Variable family | VIP | Sparse PLS coefficient | Selected in sparse weights | Nonzero component count |
| --- | --- | --- | --- | --- | --- |
| visible minority share | immigration, citizenship, and racialized geography | 2.217 | -0.096 | True | 3 |
| bachelors or higher 25-64 share | education, income, and household class | 1.921 | 0.114 | True | 2 |
| effective mayoral candidates above 5 percent | local mayoral competitiveness | 1.861 | -0.018 | True | 3 |
| average household size | education, income, and household class | 1.731 | -0.038 | True | 3 |
| non citizen share | immigration, citizenship, and racialized geography | 1.444 | -0.128 | True | 3 |
| mayoral top two margin | local mayoral competitiveness | 1.211 | -0.021 | True | 2 |
| recent immigrant share | immigration, citizenship, and racialized geography | 1.146 | -0.040 | True | 5 |
| federal margin | federal competitiveness | 0.956 | 0.072 | True | 3 |
| age 65 plus share | age structure | 0.877 | 0.120 | True | 3 |
| school age 5-17 share | service contact and local need | 0.823 | 0.168 | True | 4 |
| age 18-34 share | age structure | 0.753 | -0.156 | True | 2 |
| no car household share | transportation access | 0.737 | -0.011 | True | 5 |

The recurring variables across PLS, sparse PLS, PCA, and Elastic Net robustness are therefore the safest story material: visible minority share, bachelor-or-higher education, mayoral competitiveness/fragmentation, household size, non-citizenship, recent immigration, low income, age structure, and selected service-contact measures.

## Section 9: Appendices

### Appendix A: Model Selection

| Model | Predictors | Latent components | Cross-validated R2 | Cross-validated RMSE | Training R2 | Training RMSE |
| --- | --- | --- | --- | --- | --- | --- |
| Interaction-augmented PLS | 38 | 1 | 0.566 | 0.057 | 0.587 | 0.056 |
| Full unfiltered PLS | 70 | 12 | 0.565 | 0.057 | 0.693 | 0.048 |
| Sparse PLS | 27 | 5 | 0.560 | 0.058 | 0.624 | 0.053 |
| Theory-cleaned PLS | 27 | 5 | 0.558 | 0.058 | 0.625 | 0.053 |
| Supervised PCA | 15 | 8 | 0.540 | 0.059 | 0.569 | 0.057 |

### Appendix B: Component Family Themes

The appendix table below keeps the top three variable families for each cleaned PLS component. It shows which broad concept groups dominate each latent variable.

| Component | Variable family theme | Share of absolute loading | Representative variables |
| --- | --- | --- | --- |
| Component 1 | immigration, citizenship, and racialized geography | 0.206 | visible minority share; non citizen share; recent immigrant share |
| Component 1 | education, income, and household class | 0.186 | bachelors or higher 25-64 share; average household size; low income share |
| Component 1 | local mayoral competitiveness | 0.159 | effective mayoral candidates above 5 percent; mayoral top two margin |
| Component 2 | age structure | 0.141 | age 18-34 share; age 65 plus share |
| Component 2 | urban form and density | 0.138 | population density per km2; apartment share; condo share |
| Component 2 | immigration, citizenship, and racialized geography | 0.136 | non citizen share; recent immigrant share; visible minority share |
| Component 3 | urban form and density | 0.231 | apartment share; condo share; population density per km2 |
| Component 3 | education, income, and household class | 0.174 | average household size; low income share; bachelors or higher 25-64 share |
| Component 3 | immigration, citizenship, and racialized geography | 0.129 | recent immigrant share; non citizen share; visible minority share |
| Component 4 | service contact and local need | 0.240 | school age 5-17 share; social housing share; development applications 2021-2025 per 1000; requests 311 per 1000; ksi collision events 2021-2025 per 1000 |
| Component 4 | age structure | 0.110 | age 65 plus share; age 18-34 share |
| Component 4 | urban form and density | 0.093 | condo share; population density per km2; apartment share |
| Component 5 | service contact and local need | 0.216 | ksi collision events 2021-2025 per 1000; social housing share; requests 311 per 1000; development applications 2021-2025 per 1000; school age 5-17 share |
| Component 5 | civic/service proximity | 0.146 | community centre access within 1200m; library access within 1200m; shelter access within 1200m |
| Component 5 | urban form and density | 0.113 | condo share; population density per km2; apartment share |

### Appendix C: Component Compositions

The appendix table below lists the top terms by absolute loading for each cleaned PLS component. These are the core empirical evidence behind the component names.

| Component | Variable | Variable family | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| Component 1 | effective mayoral candidates above 5 percent | local mayoral competitiveness | -0.408 | 1.787 | -0.535 | lower turnout |
| Component 1 | visible minority share | immigration, citizenship, and racialized geography | -0.401 | 2.145 | -0.642 | lower turnout |
| Component 1 | bachelors or higher 25-64 share | education, income, and household class | 0.360 | 1.847 | 0.554 | higher turnout |
| Component 1 | average household size | education, income, and household class | -0.312 | 1.672 | -0.485 | lower turnout |
| Component 1 | mayoral top two margin | local mayoral competitiveness | 0.280 | 1.084 | 0.288 | lower turnout |
| Component 1 | non citizen share | immigration, citizenship, and racialized geography | -0.261 | 1.433 | -0.417 | lower turnout |
| Component 1 | recent immigrant share | immigration, citizenship, and racialized geography | -0.227 | 1.137 | -0.317 | lower turnout |
| Component 1 | federal margin | federal competitiveness | 0.225 | 0.967 | 0.272 | higher turnout |
| Component 2 | age 18-34 share | age structure | -0.548 | 0.833 | -0.136 | lower turnout |
| Component 2 | no car household share | transportation access | -0.447 | 0.741 | 0.174 | lower turnout |
| Component 2 | same address 5yr share | residential stability | 0.407 | 0.575 | -0.120 | lower turnout |
| Component 2 | age 65 plus share | age structure | 0.381 | 0.805 | 0.182 | higher turnout |
| Component 2 | population density per km2 | urban form and density | -0.377 | 0.609 | 0.102 | higher turnout |
| Component 2 | non citizen share | immigration, citizenship, and racialized geography | -0.375 | 1.433 | -0.417 | lower turnout |
| Component 2 | shelter access within 1200m | civic/service proximity | -0.373 | 0.716 | 0.139 | lower turnout |
| Component 2 | renter share | renter/owner tenure | -0.369 | 0.517 | -0.081 | lower turnout |
| Component 3 | apartment share | urban form and density | 0.425 | 0.669 | 0.089 | higher turnout |
| Component 3 | average household size | education, income, and household class | -0.354 | 1.672 | -0.485 | lower turnout |
| Component 3 | condo share | urban form and density | 0.321 | 0.491 | 0.084 | higher turnout |
| Component 3 | recent immigrant share | immigration, citizenship, and racialized geography | 0.311 | 1.137 | -0.317 | lower turnout |
| Component 3 | same address 5yr share | residential stability | -0.297 | 0.575 | -0.120 | lower turnout |
| Component 3 | renter share | renter/owner tenure | 0.291 | 0.517 | -0.081 | lower turnout |
| Component 3 | low income share | education, income, and household class | 0.287 | 0.770 | -0.199 | lower turnout |
| Component 3 | population density per km2 | urban form and density | 0.276 | 0.609 | 0.102 | higher turnout |
| Component 4 | school age 5-17 share | service contact and local need | 0.518 | 0.820 | -0.194 | higher turnout |
| Component 4 | provincial margin | provincial competitiveness | 0.399 | 0.675 | 0.184 | higher turnout |
| Component 4 | federal margin | federal competitiveness | 0.399 | 0.967 | 0.272 | higher turnout |
| Component 4 | condo share | urban form and density | -0.347 | 0.491 | 0.084 | higher turnout |
| Component 4 | social housing share | service contact and local need | 0.340 | 0.674 | -0.191 | lower turnout |
| Component 4 | age 65 plus share | age structure | -0.318 | 0.805 | 0.182 | higher turnout |
| Component 4 | same address 5yr share | residential stability | 0.256 | 0.575 | -0.120 | lower turnout |
| Component 4 | renter share | renter/owner tenure | 0.249 | 0.517 | -0.081 | lower turnout |
| Component 5 | community centre access within 1200m | civic/service proximity | -0.451 | 0.224 | -0.037 | lower turnout |
| Component 5 | ksi collision events 2021-2025 per 1000 | service contact and local need | 0.346 | 0.592 | 0.157 | higher turnout |
| Component 5 | social housing share | service contact and local need | -0.323 | 0.674 | -0.191 | lower turnout |
| Component 5 | condo share | urban form and density | 0.320 | 0.491 | 0.084 | higher turnout |
| Component 5 | renter share | renter/owner tenure | -0.317 | 0.517 | -0.081 | lower turnout |
| Component 5 | no car household share | transportation access | -0.273 | 0.741 | 0.174 | lower turnout |
| Component 5 | library access within 1200m | civic/service proximity | -0.261 | 0.552 | 0.137 | lower turnout |
| Component 5 | bachelors or higher 25-64 share | education, income, and household class | 0.259 | 1.847 | 0.554 | higher turnout |

### Appendix D: Reference Geographies

The appendix table below gives near-zero reference CTs for the cleaned PLS components. These are useful as middle/reference cases when interpreting the high and low sides of each latent dimension.

| Component | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| Component 1 | CT 160.0 | 0.556 | 0.000 | 0.671 |
| Component 1 | CT 376.15 | 0.473 | -0.011 | 0.671 |
| Component 1 | CT 269.02 | 0.521 | -0.012 | 0.671 |
| Component 1 | CT 378.2 | 0.549 | 0.016 | 0.671 |
| Component 1 | CT 235.01 | 0.663 | 0.029 | 0.671 |
| Component 1 | CT 260.07 | 0.522 | 0.036 | 0.671 |
| Component 1 | CT 233.0 | 0.573 | 0.037 | 0.671 |
| Component 1 | CT 334.0 | 0.563 | -0.039 | 0.671 |
| Component 2 | CT 378.2 | 0.549 | -0.002 | 0.000 |
| Component 2 | CT 173.0 | 0.392 | -0.005 | 0.000 |
| Component 2 | CT 76.0 | 0.710 | 0.015 | 0.000 |
| Component 2 | CT 320.01 | 0.470 | -0.017 | 0.000 |
| Component 2 | CT 83.0 | 0.621 | -0.024 | 0.000 |
| Component 2 | CT 370.01 | 0.506 | -0.034 | 0.000 |
| Component 2 | CT 283.01 | 0.459 | -0.059 | 0.000 |
| Component 2 | CT 290.01 | 0.452 | 0.060 | 0.000 |
| Component 3 | CT 165.0 | 0.603 | -0.012 | 0.000 |
| Component 3 | CT 139.01 | 0.589 | 0.017 | 0.000 |
| Component 3 | CT 209.0 | 0.555 | 0.032 | 0.000 |
| Component 3 | CT 173.0 | 0.392 | 0.033 | 0.000 |
| Component 3 | CT 263.03 | 0.541 | 0.034 | 0.000 |
| Component 3 | CT 319.0 | 0.396 | -0.039 | 0.000 |
| Component 3 | CT 353.04 | 0.401 | 0.045 | 0.000 |
| Component 3 | CT 376.02 | 0.423 | -0.051 | 0.000 |
| Component 4 | CT 20.0 | 0.621 | -0.003 | 0.000 |
| Component 4 | CT 370.03 | 0.419 | 0.006 | 0.000 |
| Component 4 | CT 153.0 | 0.508 | -0.009 | 0.000 |
| Component 4 | CT 67.0 | 0.635 | 0.013 | 0.000 |
| Component 4 | CT 249.01 | 0.406 | 0.014 | 0.000 |
| Component 4 | CT 117.0 | 0.590 | -0.015 | 0.000 |
| Component 4 | CT 345.0 | 0.473 | 0.015 | 0.000 |
| Component 4 | CT 280.0 | 0.421 | -0.016 | 0.000 |
| Component 5 | CT 314.02 | 0.454 | -0.007 | 0.000 |
| Component 5 | CT 275.0 | 0.615 | 0.008 | 0.000 |
| Component 5 | CT 378.08 | 0.463 | -0.009 | 0.000 |
| Component 5 | CT 323.02 | 0.575 | 0.018 | 0.000 |
| Component 5 | CT 207.0 | 0.477 | -0.021 | 0.000 |
| Component 5 | CT 364.02 | 0.473 | -0.025 | 0.000 |
| Component 5 | CT 225.01 | 0.562 | -0.027 | 0.000 |
| Component 5 | CT 239.0 | 0.467 | 0.027 | 0.000 |

The complete CSV outputs remain available in the same folder for reproducibility, but the key report-facing selections are included directly above.

### Appendix E: Supervised PCA Comparison Tables

The table below lists the top supervised PCA component terms. These are included because the PCA comparison introduces or elevates several variables that are less central in the cleaned PLS narrative, especially KSI collisions, social housing, age, and provincial margin.

| Component | Variable | Variable family | Component side | PCA loading | Absolute loading |
| --- | --- | --- | --- | --- | --- |
| Component 1 | effective mayoral candidates above 5 percent | local mayoral competitiveness | high side | 0.430 | 0.430 |
| Component 1 | visible minority share | immigration, citizenship, and racialized geography | high side | 0.402 | 0.402 |
| Component 1 | bachelors or higher 25-64 share | education, income, and household class | low side | -0.338 | 0.338 |
| Component 1 | mayoral top two margin | local mayoral competitiveness | low side | -0.328 | 0.328 |
| Component 1 | average household size | education, income, and household class | high side | 0.286 | 0.286 |
| Component 2 | low income share | education, income, and household class | low side | -0.434 | 0.434 |
| Component 2 | no car household share | transportation access | low side | -0.403 | 0.403 |
| Component 2 | non citizen share | immigration, citizenship, and racialized geography | low side | -0.396 | 0.396 |
| Component 2 | recent immigrant share | immigration, citizenship, and racialized geography | low side | -0.389 | 0.389 |
| Component 2 | average household size | education, income, and household class | high side | 0.355 | 0.355 |
| Component 3 | social housing share | service contact and local need | high side | 0.498 | 0.498 |
| Component 3 | federal margin | federal competitiveness | high side | 0.401 | 0.401 |
| Component 3 | provincial margin | provincial competitiveness | high side | 0.381 | 0.381 |
| Component 3 | bachelors or higher 25-64 share | education, income, and household class | low side | -0.328 | 0.328 |
| Component 3 | school age 5-17 share | service contact and local need | high side | 0.318 | 0.318 |
| Component 4 | age 65 plus share | age structure | low side | -0.630 | 0.630 |
| Component 4 | ksi collision events 2021-2025 per 1000 | service contact and local need | low side | -0.381 | 0.381 |
| Component 4 | social housing share | service contact and local need | low side | -0.335 | 0.335 |
| Component 4 | recent immigrant share | immigration, citizenship, and racialized geography | high side | 0.272 | 0.272 |
| Component 4 | school age 5-17 share | service contact and local need | high side | 0.264 | 0.264 |
| Component 5 | ksi collision events 2021-2025 per 1000 | service contact and local need | high side | 0.633 | 0.633 |
| Component 5 | provincial margin | provincial competitiveness | high side | 0.413 | 0.413 |
| Component 5 | social housing share | service contact and local need | low side | -0.317 | 0.317 |
| Component 5 | mayoral top two margin | local mayoral competitiveness | high side | 0.291 | 0.291 |
| Component 5 | average household size | education, income, and household class | high side | 0.261 | 0.261 |
| Component 6 | mayoral top two margin | local mayoral competitiveness | low side | -0.554 | 0.554 |
| Component 6 | ksi collision events 2021-2025 per 1000 | service contact and local need | high side | 0.367 | 0.367 |
| Component 6 | effective mayoral candidates above 5 percent | local mayoral competitiveness | high side | 0.366 | 0.366 |
| Component 6 | age 65 plus share | age structure | low side | -0.358 | 0.358 |
| Component 6 | federal margin | federal competitiveness | high side | 0.347 | 0.347 |
| Component 7 | ksi collision events 2021-2025 per 1000 | service contact and local need | low side | -0.538 | 0.538 |
| Component 7 | provincial margin | provincial competitiveness | high side | 0.488 | 0.488 |
| Component 7 | age 65 plus share | age structure | high side | 0.401 | 0.401 |
| Component 7 | school age 5-17 share | service contact and local need | low side | -0.286 | 0.286 |
| Component 7 | social housing share | service contact and local need | low side | -0.277 | 0.277 |
| Component 8 | bachelors or higher 25-64 share | education, income, and household class | high side | 0.513 | 0.513 |
| Component 8 | provincial margin | provincial competitiveness | high side | 0.421 | 0.421 |
| Component 8 | school age 5-17 share | service contact and local need | high side | 0.358 | 0.358 |
| Component 8 | no car household share | transportation access | low side | -0.300 | 0.300 |
| Component 8 | recent immigrant share | immigration, citizenship, and racialized geography | high side | 0.252 | 0.252 |

### Appendix F: Important Cautions

- The component reference scores are interpretive projections from existing loadings. They are not new fitted latent models.
- PLS components are supervised by mean turnout, so they should be interpreted as turnout-oriented social-geographic dimensions.
- Some component signs are arbitrary. Interpret the high and low sides together rather than treating a positive loading as inherently good or bad.
- The analysis is ecological at the CT level. It should not be converted into claims about individual voters.
- Citizenship and turnout eligibility are central to interpretation; lower turnout associations in newcomer-heavy areas may reflect eligibility, settlement, mobilization, and institutional barriers.
