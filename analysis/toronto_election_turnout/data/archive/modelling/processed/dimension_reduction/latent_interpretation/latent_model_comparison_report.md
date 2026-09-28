# Latent Model Comparison Report

This report compares the two more interpretable latent approaches back to the strongest predictive benchmark, the interaction-augmented PLS. No new models were fit. The comparison uses existing loadings, VIP tables, model summaries, supervised PCA loadings, and the prior interaction screen.

## Report Structure

**Section 1: Benchmark Model - Interaction-Augmented PLS.** This section introduces the strongest predictive model, explains why it is used as the benchmark, and summarizes its model performance, main component terms, and interaction-screen evidence.

**Section 2: Cleaned PLS Compared With The Benchmark.** This section compares the theory-cleaned PLS with the interaction-augmented PLS. It focuses on whether cleaned PLS recovers the benchmark's main turnout axis and what extra interpretive structure its five components add.

**Section 3: Supervised PCA Compared With The Benchmark.** This section compares supervised PCA with the interaction-augmented PLS. It treats PCA as a more familiar validation check and asks which benchmark themes reappear under PCA and which are separated differently.

**Section 4: Overall Interpretation.** This section synthesizes what the comparisons imply for the turnout story: which findings are stable across models, which are specific to the augmented interaction model, and how the strongest predictive model can be understood as a compressed version of the broader latent geography.

**Tables Included.** The report includes model performance, augmented PLS component terms, interaction-screen results, cleaned PLS Component 1 terms, shared/distinct variable comparisons, cleaned PLS component themes, supervised PCA high-loading variables, and supervised PCA component terms.

## Benchmark: Interaction-Augmented PLS

The interaction-augmented PLS is the strongest existing dimension-reduction model by cross-validation. It has the highest CV R2 and lowest CV RMSE among the focused latent candidates, but it keeps only one retained PLS component. That means it is best interpreted as a compact benchmark axis plus interaction evidence, not as a multi-component explanation of Toronto's turnout geography.

| Model | Predictors | Latent components | Cross-validated R2 | Cross-validated RMSE | Training R2 | Training RMSE |
| --- | --- | --- | --- | --- | --- | --- |
| Interaction-augmented PLS | 38 | 1 | 0.566 | 0.057 | 0.587 | 0.056 |
| Theory-cleaned PLS | 27 | 5 | 0.558 | 0.058 | 0.625 | 0.053 |
| Supervised PCA | 15 | 8 | 0.540 | 0.059 | 0.569 | 0.057 |

The benchmark component is substantively close to the main axis found in the cleaned PLS: education and electoral attachment on one side, and newcomer/racialized/language/class-fragmentation geography on the other. Its strongest negative-loading variables include visible minority share, effective mayoral candidates above 5 percent, unemployment, non-official mother tongue, average household size, non-citizenship, and recent immigration. Its strongest positive-loading variables include bachelor-or-higher education, mayoral top-two margin, federal margin, shelter/library/service-contact variables, and age 65 plus share.

Top augmented PLS component terms:

| Variable | Variable family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| visible minority share | immigration, citizenship, and racialized geography | low side | -0.346 | 2.307 | -0.642 | lower turnout |
| effective mayoral candidates above 5 percent | local mayoral competitiveness | low side | -0.330 | 1.923 | -0.535 | lower turnout |
| unemployment rate share | education, income, and household class | low side | -0.317 | 1.912 | -0.532 | lower turnout |
| bachelors or higher 25-64 share | education, income, and household class | high side | 0.305 | 1.991 | 0.554 | higher turnout |
| non official mother tongue share | immigration, citizenship, and racialized geography | low side | -0.281 | 1.764 | -0.491 | lower turnout |
| average household size | education, income, and household class | low side | -0.263 | 1.745 | -0.485 | lower turnout |
| non citizen share | immigration, citizenship, and racialized geography | low side | -0.235 | 1.500 | -0.417 | lower turnout |
| mayoral top two margin | local mayoral competitiveness | high side | 0.210 | 1.036 | 0.288 | higher turnout |
| recent immigrant share | immigration, citizenship, and racialized geography | low side | -0.204 | 1.140 | -0.317 | lower turnout |
| federal margin | federal competitiveness | high side | 0.172 | 0.979 | 0.272 | higher turnout |
| school age 5-17 share | service contact and local need | low side | -0.153 | 0.698 | -0.194 | lower turnout |
| low income share x age 35-64 share | interaction term | low side | -0.140 | 0.798 | -0.222 | lower turnout |
| average household size x age 35-64 share | interaction term | high side | 0.140 | 0.753 | 0.210 | higher turnout |
| ksi collision events 2021-2025 per 1000 x non official mother tongue share | interaction term | high side | 0.136 | 0.846 | 0.235 | higher turnout |

The interaction evidence is why this model predicts slightly better. The benchmark does not simply say that service-contact variables matter; it says they matter conditionally, especially when paired with low income, education, unemployment, household size, language/citizenship geography, and age.

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

## Cleaned PLS Compared With Interaction-Augmented PLS

The cleaned PLS is slightly weaker predictively than the augmented PLS, but it is the best interpretive companion to it. The key finding is that cleaned PLS Component 1 reproduces the same broad benchmark axis: education/electoral attachment versus newcomer/racialized-fragmentation geography. This supports the view that the augmented model's strongest predictive component is not an artifact of the interaction screen.

The difference is that cleaned PLS decomposes the benchmark story into five dimensions. Component 1 carries the direct turnout gradient. Components 2-5 then separate older stability, young dense renter/carless geography, vertical rental/newcomer urban form, family/social-housing/service-need context, and service-contact/road-exposure context. In other words, cleaned PLS does not beat the benchmark; it explains what the benchmark compresses.

Cleaned PLS Component 1 terms:

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
| shelter access within 1200m | civic/service proximity | high side | 0.185 | 0.716 | 0.139 | lower turnout |
| provincial margin | provincial competitiveness | high side | 0.161 | 0.675 | 0.184 | higher turnout |

Shared and distinct top variables:

| Variable | In augmented PLS top terms | In cleaned PLS top terms | Variable family |
| --- | --- | --- | --- |
| average household size | True | True | education, income, and household class |
| bachelors or higher 25-64 share | True | True | education, income, and household class |
| effective mayoral candidates above 5 percent | True | True | local mayoral competitiveness |
| federal margin | True | True | federal competitiveness |
| mayoral top two margin | True | True | local mayoral competitiveness |
| non citizen share | True | True | immigration, citizenship, and racialized geography |
| recent immigrant share | True | True | immigration, citizenship, and racialized geography |
| visible minority share | True | True | immigration, citizenship, and racialized geography |
| average household size x age 35-64 share | True | False | interaction term |
| bachelors or higher 25-64 share x effective mayoral candidates above 5 percent | True | False | interaction term |
| ksi collision events 2021-2025 per 1000 x non official mother tongue share | True | False | interaction term |
| ksi collision events 2021-2025 per 1000 x unemployment rate share | True | False | interaction term |
| low income share x age 35-64 share | True | False | interaction term |
| non official mother tongue share | True | False | immigration, citizenship, and racialized geography |
| unemployment rate share | True | False | education, income, and household class |
| age 18-34 share | False | True | age structure |
| age 65 plus share | False | True | age structure |
| low income share | False | True | education, income, and household class |
| no car household share | False | True | transportation access |
| provincial margin | False | True | provincial competitiveness |
| school age 5-17 share | False | True | service contact and local need |
| shelter access within 1200m | False | True | civic/service proximity |

Cleaned PLS component themes:

| Cleaned PLS component | Dominant theme | Share of absolute loading | Representative variables |
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

Interpretively, the cleaned PLS adds three things that the augmented PLS does not show as clearly. First, it shows that the strongest turnout axis is only one part of the latent structure. Second, it separates density into different meanings: young/renter/carless density is not the same as condo/education density or family/social-housing density. Third, it shows why some variables have mixed signs or weak standalone interpretations: service access, 311 requests, KSI collisions, and development applications appear in secondary components and interactions rather than as simple one-direction predictors.

## Supervised PCA Compared With Interaction-Augmented PLS

Supervised PCA is weaker predictively than the augmented PLS, but it is valuable because it is more familiar and less directly supervised once the screening step is done. It independently recovers many of the same ingredients: visible minority share, bachelor-or-higher education, mayoral competitiveness, non-citizenship, recent immigration, federal/provincial margins, low income, age, no-car households, social housing, school-age share, and KSI collisions.

The main difference is conceptual. The augmented PLS builds the strongest turnout-predictive axis directly. Supervised PCA first screens variables by turnout association, then decomposes covariance among the screened variables. So PCA gives clearer mechanical contrasts, but those contrasts are not necessarily the best turnout-predictive axes. This is why supervised PCA is useful as a confirmation check rather than the central story model.

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

Supervised PCA component terms:

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

Shared and distinct top variables:

| Variable | In augmented PLS top terms | In supervised PCA top terms | Variable family |
| --- | --- | --- | --- |
| average household size | True | True | education, income, and household class |
| bachelors or higher 25-64 share | True | True | education, income, and household class |
| effective mayoral candidates above 5 percent | True | True | local mayoral competitiveness |
| federal margin | True | True | federal competitiveness |
| mayoral top two margin | True | True | local mayoral competitiveness |
| non citizen share | True | True | immigration, citizenship, and racialized geography |
| recent immigrant share | True | True | immigration, citizenship, and racialized geography |
| visible minority share | True | True | immigration, citizenship, and racialized geography |
| average household size x age 35-64 share | True | False | interaction term |
| bachelors or higher 25-64 share x effective mayoral candidates above 5 percent | True | False | interaction term |
| ksi collision events 2021-2025 per 1000 x non official mother tongue share | True | False | interaction term |
| ksi collision events 2021-2025 per 1000 x unemployment rate share | True | False | interaction term |
| low income share x age 35-64 share | True | False | interaction term |
| non official mother tongue share | True | False | immigration, citizenship, and racialized geography |
| unemployment rate share | True | False | education, income, and household class |
| age 65 plus share | False | True | age structure |
| ksi collision events 2021-2025 per 1000 | False | True | service contact and local need |
| low income share | False | True | education, income, and household class |
| no car household share | False | True | transportation access |
| provincial margin | False | True | provincial competitiveness |
| school age 5-17 share | False | True | service contact and local need |
| social housing share | False | True | service contact and local need |

The PCA comparison mainly confirms the benchmark story rather than replacing it. PCA Component 1 mirrors the same broad divide, though with signs reversed: racialized/newcomer/household/electoral-fragmentation variables sit opposite education and electoral margins. Later PCA components separate service need, age, social housing, KSI collisions, and electoral margins in ways that are substantively useful, but less directly tied to predictive performance.

## Overall Interpretation

The three-model comparison strengthens the story. The strongest model is interaction-augmented PLS, but the same social-geographic structure appears in cleaned PLS and supervised PCA. That means the main interpretation does not depend on one modeling choice.

The safest core story is this: mean turnout is highest where education, clearer electoral attachment, and institutional/civic resources cluster together. It is lower where newcomer/racialized/citizenship/language geography overlaps with larger households, unemployment or lower income, and fragmented local electoral competition. The interaction model adds that service-contact variables matter conditionally, not as simple standalone effects.

Cleaned PLS is the best model for explaining the benchmark because it decomposes the benchmark axis into readable secondary dimensions. Supervised PCA is the best model for validating the benchmark because it uses a familiar PCA structure and still recovers the same broad ingredients. Together, they make the augmented PLS less opaque: the strongest predictive model is not a black box, but a compressed version of a broader turnout geography.
