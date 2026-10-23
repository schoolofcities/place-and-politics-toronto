# Data, Methods, and Results

This analysis examines how electoral participation varies across Toronto and which combinations of neighbourhood characteristics are most strongly associated with consistently higher or lower turnout.

The analysis covers 585 Toronto census tracts (CTs) and three recent elections: the 2023 Toronto mayoral election, the 2025 Ontario provincial election, and the 2025 federal election. The main outcome is mean turnout across all three elections. The main model is Partial Least Squares regression (PLS) using 70 neighbourhood predictors across 14 social-geographic domains.

The final PLS model retains four components, with training R² = 0.6609, 10-fold cross-validated R² = 0.5860, and cross-validated RMSE = 0.0559. The aim is not to identify one demographic variable as the explanation for turnout. It is to identify broader combinations of neighbourhood characteristics that recur together and are related to participation.

The analysis is documented in the notebooks in this folder, which run in order:

| Step | Notebook |
| --- | --- |
| Normalizing the three elections' poll-level results | [01_normalize_election_results.ipynb](01_normalize_election_results.ipynb) |
| Extracting Toronto's census tracts from the 2021 Census Profile | [02_extract_toronto_census_tracts.ipynb](02_extract_toronto_census_tracts.ipynb) |
| Building the census tract profile | [03_build_census_tract_profile.ipynb](03_build_census_tract_profile.ipynb) |
| Interpolating votes to census tracts | [04_interpolate_votes_to_tracts.ipynb](04_interpolate_votes_to_tracts.ipynb) |
| Preparing the predictor universe | [05_prepare_ct_predictor_universe.ipynb](05_prepare_ct_predictor_universe.ipynb) |
| Exploring and curating the 70 predictors | [06_explore_and_curate_predictors.ipynb](06_explore_and_curate_predictors.ipynb) |
| Fitting the PLS model | [07_fit_latent_pls_model.ipynb](07_fit_latent_pls_model.ipynb) |
| Robustness checks and alternative models | [08_robustness_and_alternative_models.ipynb](08_robustness_and_alternative_models.ipynb) |
| Final synthesis and the data exported to the web page | [09_final_synthesis.ipynb](09_final_synthesis.ipynb) |

## 1. Election data, geography, and turnout

Election results are originally reported using election-specific polling geographies rather than 2021 census tracts. We therefore use population-weighted areal interpolation to transfer votes to a common CT geography. Smaller dissemination areas are used to estimate where the relevant population lives within overlapping election and Census polygons, rather than assuming that residents are evenly distributed across land area.

The weighting population and turnout denominator is Canadian citizens aged 18 and over. For each CT, we estimate votes cast and turnout for the 2023 mayoral, 2025 provincial, and 2025 federal elections.

The main outcome is the simple mean of these three turnout measures. Averaging across elections reduces dependence on one candidate field, campaign, or election-specific context and instead captures where participation is consistently higher or lower.

This differs from official turnout based on registered electors. The citizen-adult denominator provides a common population-based measure across the three elections and does not treat registration itself as outside the participation process.

The final modelling table contains the CT identifier, citizen-adult population, votes cast and turnout for each election, mean turnout, and all final predictors.

## 2. Predictor set

The final model uses 70 predictors across 14 domains. The intention is to admit a broad range of plausible neighbourhood characteristics while avoiding direct complements and unnecessary duplication.

| Domain | Included variables |
| --- | --- |
| Age / life stage | age 18–29 share; age 30–64 share; age 65+ share; school-age population aged 5–17 share |
| Household / family | average household size; one-person household share; one-parent family share; multigenerational household share; married or common-law share; never-married share |
| Education | bachelor's degree or higher among ages 25–64 share; college or trades credential among ages 25–64 share; high-school-or-less share |
| Income / class | median household income; Low Income Measure, After Tax share |
| Labour market | employment rate; unemployment rate; not-in-labour-force share; temporary-worker share; self-employment share |
| Occupation | management occupation share; business, finance and administration occupation share; education, law and social/government services occupation share; natural and applied sciences occupation share; sales and service occupation share; trades and transport occupation share; manufacturing and utilities occupation share; arts, recreation and sport occupation share |
| Housing tenure / stability | renter share; same-address-five-years share; recent-mover-in-past-year share |
| Housing form | apartment share; condominium share; single-detached-house share; high-rise-apartment share; dwellings built before 1960 share; dwellings built 1961–1990 share |
| Housing affordability / need | households spending 30% or more of income on shelter costs share; core housing need share; tenant households in subsidized housing share; dwellings needing major repairs share |
| Immigration / citizenship | immigrant share; recent-immigrant share; non-citizen share; first-generation Canadian share; second-generation Canadian share |
| Culture / language | visible-minority share; no religious affiliation share; non-official language spoken at home share; knowledge of neither English nor French share |
| Transportation | TTS no-car household share; TTS vehicles per household; TTS transit trip share; TTS auto trip share; TTS walk-or-bike trip share; TTS average trip distance in kilometres; TTS trips per person; Census 60+ minute commute share; Census work-from-home share |
| Urban form / location | population density per km²; distance from City Hall in kilometres |
| Accessibility | jobs proximity index; transit proximity index; grocery proximity index; health-care proximity index; childcare proximity index; elementary-school proximity index; secondary-school proximity index; library proximity index; parks proximity index |

Transportation Tomorrow Survey (TTS) measures are preferred where they provide an equivalent mobility measure. Census variables are retained where they capture distinct concepts such as 60+ minute work commutes or working from home.

Earlier exploratory variables such as KSI collisions, 311 requests, development applications, candidate fragmentation, and election margins are not included in this version. The final model is limited to the pre-specified social, economic, housing, transportation, and accessibility variables above.

## 3. Why PLS, and how the model was selected

Many of the predictors overlap substantially. Education is related to occupation and work arrangements. Immigrant settlement is related to household structure, language, and commuting. Housing form is related to density and transportation. Trying to interpret 70 separate conditional regression coefficients would make these overlapping relationships difficult to summarize.

PLS is useful here for two reasons. First, it handles a predictor set with substantial multicollinearity by replacing the original variables with a smaller number of latent components. Second, unlike ordinary PCA, those components are constructed with the turnout outcome in mind. The resulting axes are therefore designed to capture combinations of neighbourhood characteristics that are relevant to participation.

All predictors are standardized before modelling. We tested between one and 12 PLS components using 10-fold cross-validation:

| Components | Train R² | CV R² | CV RMSE |
| --- | --- | --- | --- |
| 1 | 0.4746 | 0.4578 | 0.0640 |
| 2 | 0.5515 | 0.5061 | 0.0611 |
| 3 | 0.6332 | 0.5638 | 0.0574 |
| **4** | **0.6609** | **0.5860** | **0.0559** |
| 5 | 0.6818 | 0.5739 | 0.0567 |
| 6 | 0.6914 | 0.5586 | 0.0578 |
| 12 | 0.7139 | 0.5528 | 0.0581 |

Four components were retained because they produce the highest cross-validated R². Additional components continue to improve in-sample fit but predict held-out CTs less well.

## 4. PLS results

The four components describe different dimensions of Toronto's social geography, but they are not equally related to turnout. Their correlations with mean turnout are:

- Component 1: r = 0.72 (across the 582 tracts with reliable data)
- Component 2: r = 0.2773
- Component 3: r = 0.2859
- Component 4: r = 0.1662

Component 1 is therefore the main turnout-facing axis. Components 2 to 4 identify additional neighbourhood structure, but their direct relationship with turnout is much weaker. (Within the model fit itself, on all 585 CTs, Component 1's correlation with turnout is 0.6889.)

### Component 1: professional and flexible-work geography versus working-class settlement and commuting geography

The positive direction is associated most strongly with work from home (+0.213), bachelor's degree or higher (+0.195), education/law/social/government occupations (+0.177), arts/recreation/sport occupations (+0.176), employment (+0.169), TTS trips per person (+0.165), business/finance/administration occupations (+0.163), and management occupations (+0.157).

The negative direction is associated most strongly with high-school-or-less education (−0.189), immigrant share (−0.188), visible-minority share (−0.181), trades/transport occupations (−0.180), distance from City Hall (−0.176), sales/service occupations (−0.175), 60+ minute commuting (−0.175), manufacturing occupations (−0.173), first-generation population (−0.171), multigenerational households (−0.167), one-parent families (−0.167), and unemployment (−0.157).

The component therefore combines education, occupational class, work flexibility, immigrant settlement, household structure, commuting burden, and location. Its r = 0.72 relationship with turnout is much stronger than that of the later components.

The main result is not that one variable such as education, immigration, or commuting independently explains turnout. These characteristics form a broader neighbourhood gradient that is closely aligned with participation.

### Component 2: settled family stability versus younger mobile neighbourhoods

The positive direction is associated with same-address-five-years share (+0.274), married/common-law share (+0.217), detached-house share (+0.210), age 65+ share (+0.206), school-age population share (+0.176), and median household income (+0.174).

The negative direction is associated with age 18–29 share (−0.326), never-married share (−0.320), recent-mover share (−0.276), non-citizen share (−0.263), recent-immigrant share (−0.240), shelter-cost burden (−0.231), apartment share (−0.227), and renter share (−0.212).

This is a clear contrast between relatively settled family neighbourhoods and younger, more mobile, renter-heavy areas. Its turnout correlation is only r = 0.2773, so it is better treated as secondary social geography than as the main turnout explanation.

### Component 3: renter and housing-need geography versus higher-income family ownership

The positive direction is associated with apartment share (+0.280), core housing need (+0.269), one-person households (+0.244), low-income share (+0.242), high-rise-apartment share (+0.234), shelter-cost burden (+0.204), and renter share (+0.198).

The negative direction is associated with detached-house share (−0.261), median household income (−0.248), average household size (−0.236), married/common-law share (−0.179), and multigenerational households (−0.177).

This component mainly captures a housing and household-economic contrast. Its relationship with turnout is modest at r = 0.2859.

### Component 4: newer professional housing versus older-stock and employment hardship

The positive direction is associated especially with condominium share (+0.432), natural and applied sciences occupations (+0.407), married/common-law share (+0.282), employment (+0.227), and business/finance/administration occupations (+0.202).

The negative direction is associated most strongly with dwellings needing major repairs (−0.522), subsidized housing (−0.328), dwellings built before 1960 (−0.309), renter share (−0.291), self-employment (−0.271), temporary work (−0.260), and unemployment (−0.260).

Its turnout correlation is only r = 0.1662, and it is less stable under resampling than the first three components. It is therefore mainly a secondary descriptive result.

## 5. Why retain PLS? Robustness and alternative specifications

The robustness tests serve two purposes. The first is to test whether the main PLS result depends on one particular outcome, predictor set, or sample. The second is to test whether PLS is giving us a structure that could only be produced by PLS.

The comparison matters because PLS is not retained simply because it has the highest predictive score in every test. It does not. We retain it because it performs competitively while directly answering the substantive question of the analysis: which combinations of correlated neighbourhood characteristics form turnout-relevant latent dimensions?

PCR and PCA construct their components without using turnout itself. Elastic Net predicts turnout well but leaves us with individual coefficients rather than a small number of neighbourhood dimensions. PLS provides a useful middle ground. It reduces a highly correlated predictor set, remains explicitly supervised by turnout, and produces components that can be interpreted and mapped.

### Random and spatial cross-validation

Under ordinary shuffled 10-fold CV, the four-component PLS model produces R² = 0.5860 and RMSE = 0.0559.

Because nearby CTs tend to resemble one another, shuffled CV can overstate geographic generalization. We therefore repeated the comparison by holding out spatial blocks.

With 5 spatial blocks:

| Method | R² | RMSE |
| --- | --- | --- |
| **PCR** | **0.4946** | **0.0618** |
| Elastic Net | 0.4839 | 0.0624 |
| Supervised PCA | 0.4720 | 0.0632 |
| PLS | 0.4614 | 0.0638 |

With 10 spatial blocks:

| Method | R² | RMSE |
| --- | --- | --- |
| **Elastic Net** | **0.5008** | **0.0614** |
| PLS | 0.4703 | 0.0633 |
| Supervised PCA | 0.4208 | 0.0662 |
| PCR | 0.4132 | 0.0666 |

The spatial tests provide two useful checks. First, PLS performance falls from 0.5860 under shuffled CV to 0.4614–0.4703 under spatial CV, showing that some of the original predictive fit reflects spatial autocorrelation. Second, PLS remains in the same general predictive range as the alternative models. It ranks fourth under the five-block split and second under the ten-block split.

For a purely predictive exercise, there would therefore be no strong reason to insist on PLS. For this analysis, however, prediction is only one criterion. PCR's components are optimized for variation in the predictors rather than turnout, while Elastic Net does not provide a comparable latent geography. PLS retains substantial out-of-area predictive performance while giving us turnout-oriented components that can be examined directly.

### Separate election outcomes

The model was refitted separately to each election using the same 70 predictors.

| Outcome | Components | CV R² | CV RMSE | Component 1 similarity to mean model |
| --- | --- | --- | --- | --- |
| Mean turnout | 4 | 0.5860 | 0.0559 | 1.0000 |
| Municipal | 4 | **0.6662** | 0.0599 | **0.9871** |
| Provincial | 4 | 0.4049 | 0.0712 | **0.9971** |
| Federal | 4 | 0.3579 | 0.0796 | **0.9887** |

The leading PLS component is almost unchanged across the three elections. This is important for the use of PLS because it shows that the first latent dimension is not being manufactured by averaging unlike elections together. The same supervised axis reappears when the outcome is changed independently.

Neighbourhood characteristics predict municipal turnout considerably better than provincial or federal turnout, but the social-geographic direction of the first component remains essentially the same.

### Broad versus compact predictor sets

The current 70-variable model was also compared with the earlier compact PLS model.

| Model | Predictors | CTs | Components | CV R² | Component 1 correlation with final model |
| --- | --- | --- | --- | --- | --- |
| Final PLS | 70 | 585 | 4 | **0.5860** | 1.0000 |
| Earlier compact PLS | 14 | 583 | 3 | 0.5599 | **0.9373** |

The broader predictor set improves CV R² by about 0.0261, but more importantly, it produces almost the same first component. This suggests that PLS is recovering a fairly persistent underlying gradient rather than simply reflecting the specific variables chosen for one version of the model.

### Removing transportation

Transportation measures are prominent in Component 1, so the model was rerun with the entire transportation family removed.

The reduced model uses 61 predictors, still selects four components, and produces CV R² = 0.5910, compared with 0.5860 in the full model. Its first-component scores correlate r = 0.9968 with the full model.

This is a particularly useful check on the interpretation of PLS. The transportation variables help characterize the first latent dimension, but they are not creating it. Almost exactly the same supervised component is reconstructed from the remaining social, economic, housing, settlement, and accessibility variables.

### Sparse PLS

Standard PLS gives every variable some opportunity to contribute to a component. We therefore also tested sparse PLS, which adds shrinkage and can set weak weights to zero.

The shrinkage parameter was selected through inner cross-validation, with λ = 0.1 retained. On Component 1, 65 of 70 predictors remain non-zero.

The sparse result does not suggest that 65 variables have separate effects. Instead, it supports the interpretation that Component 1 is a broad latent structure spread across several correlated domains. A very sparse solution in which only two or three variables survived would have pointed toward a much narrower explanation.

### Bootstrap stability

The PLS model was repeated across 300 spatial-block bootstrap samples to test how sensitive the component loadings are to the particular set of CTs in the sample.

| Component | Median sign stability | Variables with ≥90% sign stability |
| --- | --- | --- |
| 1 | **0.9967** | **57 / 70** |
| 2 | 0.8700 | 30 / 70 |
| 3 | 0.9433 | 44 / 70 |
| 4 | 0.8083 | 10 / 70 |

In a separate sparse-PLS bootstrap, 52 of 70 predictors are selected in at least 90% of draws.

This provides the strongest reason to emphasize Component 1 over the later components. Its interpretation is not only more closely related to turnout, but also substantially more stable to changes in the observed sample. Components 2 to 4 remain useful descriptions of neighbourhood structure, but their individual loadings should be interpreted more cautiously.

### Core-periphery sensitivity

Because Component 1 has a clear core-periphery geography, we tested whether this pattern was being mechanically driven by explicitly spatial variables. We progressively removed distance from City Hall, commuting measures, and then a broader set of contextual measures including density, transportation, accessibility, housing age, and housing form.

The result is highly stable. Removing distance alone leaves Component 1 effectively unchanged, while the broader contextual exclusion still produces a component correlated 0.98 with the baseline. Even a compositional-only model using 43 population and household variables retains essentially the same education, occupation, employment, settlement, and household structure axis, with only a small decline in cross-validated performance from R² = 0.586 to 0.575.

The component also remains spatially patterned even when no direct location variables are included: its correlation with distance from City Hall declines from −0.78 to about −0.66, rather than disappearing. This suggests that the core-periphery pattern is not primarily imposed by distance or commuting variables. Instead, much of it reflects the fact that Toronto's demographic and socioeconomic characteristics are themselves spatially organized. We therefore interpret Component 1 primarily as a social-compositional turnout gradient with a strong core-periphery geography, rather than as a direct spatial effect.

## 6. Interpretation and limitations

The analysis is ecological. It describes census tracts, not individual voters. A low-turnout tract with a high immigrant share does not establish that immigrants within that tract are the residents who abstained. The same caution applies to education, occupation, household type, housing, and every other predictor.

The PLS components are also continuous mathematical summaries, not natural categories of neighbourhoods. Their signs are arbitrary, and individual loadings or VIP values should not be interpreted as independent causal coefficients.

The election results are spatially interpolated estimates. The citizen-adult denominator comes from the 2021 Census, while the elections took place between 2023 and 2025. Population change and interpolation therefore introduce some tract-level uncertainty, including a small number of implausible turnout estimates above 100%.

The predictor set also does not contain every plausible mechanism. Campaign contact, individual political interest, exact polling-place access, non-standard work schedules, candidate quality, and election-day conditions are not observed directly.

For these reasons, the model is best read as identifying a robust social geography of participation, rather than establishing why particular individuals vote or do not vote.

## 7. Main findings

The clearest result is that Toronto's turnout geography is organized around one broad social-geographic gradient rather than one isolated demographic characteristic.

The positive side of the main component combines university education, professional occupations, work-from-home flexibility, employment, and relatively central location. The negative side combines immigrant and racialized settlement, trades/service/manufacturing work, long commuting, larger and multigenerational households, lone-parent families, unemployment, and more peripheral location.

This first component is strongly related to mean turnout (r = 0.72) and unusually stable. It remains very similar when the predictor pool is reduced from 70 to 14 variables (r = 0.9373), when transportation variables are removed (r = 0.9968), and when municipal, provincial, and federal turnout are modelled separately (component similarity = 0.9871–0.9971). Its median bootstrap sign stability is 0.9967.

Other dimensions of Toronto's social geography are also visible. In particular, the model separates settled family stability from younger mobile renter geography, and housing need from higher-income family ownership. Their relationships with turnout are much weaker, however, with correlations between 0.1662 and 0.2859.

Taken together, the results suggest that persistent differences in participation are embedded in a wider geography of class, work, settlement, household structure, mobility, housing, and location. PLS is useful because it organizes those overlapping characteristics into a small number of turnout-relevant dimensions. The robustness checks show that the main dimension is not dependent on one election, one predictor set, or one particular sample, while the alternative modelling results make clear that PLS is being used primarily for its combination of prediction and interpretable latent structure, rather than because it dominates every predictive benchmark.
