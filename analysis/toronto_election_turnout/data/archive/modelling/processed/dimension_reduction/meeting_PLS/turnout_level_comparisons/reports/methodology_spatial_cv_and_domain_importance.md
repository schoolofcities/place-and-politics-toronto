# Next-Step Methodology: Spatial Nested Validation and Domain Importance

This note explains two complementary extensions for the 585 Toronto Census Tracts and the 14 meeting variables. Spatially blocked nested cross-validation asks whether the models generalize to held-out parts of Toronto. Domain-level commonality and relative-importance analysis asks how much of the explained turnout variation is unique to each conceptual domain and how much is shared among correlated domains.

## 1. Spatially blocked, nested cross-validation

### What problem it solves

The current fixed shuffled folds treat CTs as exchangeable observations. Nearby CTs often share housing markets, built form, settlement histories, services, and turnout patterns. Randomly putting neighbouring CTs in both training and validation folds can therefore leak local spatial information and make predictive performance look better than it would be in a genuinely unseen area. The same data are also used to choose component counts and assess the chosen model, which adds tuning optimism.

Spatial blocking separates geographically proximate CTs into the same fold. Nesting then separates two decisions: inner spatial folds tune the model, while outer spatial folds estimate performance on unseen geographic regions. This addresses spatial leakage and tuning bias. It does not make the model causal or eliminate ecological inference.

### Proposed implementation for this project

1. Join the 585 modelling rows to the existing CT geometry by `ct_id` and project centroids to EPSG:3347.
2. Construct five outer spatial folds. A practical first version is spatially contiguous clustering of CT centroids, balanced so each fold has roughly similar CT counts and outcome coverage. A sensitivity version should repeat the analysis with several block widths or clustering seeds.
3. For each outer fold, hold out the entire geographic block. Use only the remaining four blocks for model development.
4. Inside that training set, create four spatial inner folds. Perform imputation, scaling, supervised-PCA screening, PLS component selection, and elastic-net tuning only within the inner-training data.
5. Select PLS components from 1–5; supervised-PCA threshold and components jointly; and elastic-net `alpha` plus `l1_ratio`, including ridge (`l1_ratio = 0`).
6. Refit the selected pipeline on the full outer-training set and predict the untouched outer block.
7. Combine the five outer-fold predictions and report spatial CV R2, RMSE, and MAE for mean, municipal, provincial, and federal turnout.
8. Map outer-fold residuals and calculate residual Moran's I. Remaining spatial autocorrelation would indicate geographic structure not captured by the 14 variables.
9. Repeat the outer blocking several times and report the distribution of performance, rather than relying on one convenient partition.

### What to compare

- Current shuffled-CV performance versus outer spatial-CV performance.
- Whether the selected PLS component count changes across outer folds.
- Loading, VIP, and coefficient stability after aligning component signs and order.
- Whether PLS, supervised PCA, ridge, and elastic net rank outcomes similarly under spatial validation.
- Which neighbourhood blocks are systematically over- or under-predicted.

A material drop from shuffled to spatial CV would not invalidate the substantive story. It would show that some apparent predictive strength depends on local spatial resemblance. Stable loadings but weaker spatial prediction would support a descriptive citywide latent interpretation while cautioning against geographic extrapolation.

## 2. Domain-level commonality and relative importance

### What problem it solves

PLS provides a useful bundled latent story but does not tell us how much turnout variation belongs uniquely to education, immigration, housing, or another correlated domain. Loadings and VIP scores can be shared across correlated variables and should not be read as unique effects.

Commonality analysis decomposes model R2 into unique and shared pieces. Relative-importance methods, such as dominance analysis or Shapley/LMG allocation, distribute shared explained variance across predictors or domains. These methods clarify attribution of association; they do not establish causality.

### Recommended seven domains

1. Age structure: age 18–34 and age 65+.
2. Education/income/household: household size, bachelor-level education, and low income.
3. Tenure: renter share.
4. Residential stability: same-address-five-years share.
5. Urban form: apartment share, condo share, and population density.
6. Immigration/citizenship: citizen-adult, immigrant, and visible-minority shares.
7. Transportation: TTS no-car household share.

Because tenure, stability, and transportation each contain one observed variable, these should be called domains or blocks rather than latent factors.

### Proposed implementation

1. Standardize the 14 variables and keep the seven domain definitions fixed before looking at outcome-specific results.
2. Fit all `2^7 = 128` possible domain-subset models separately for mean, municipal, provincial, and federal turnout. Domain-level subsets are more interpretable than presenting all `2^14 = 16,384` variable subsets.
3. For each domain, calculate its unique contribution: full-model R2 minus the R2 of the model omitting that domain.
4. Calculate shared commonality components for combinations of domains. Collapse the full decomposition into readable quantities: unique contribution, total shared contribution, and total involvement for each domain.
5. Calculate Shapley/LMG or general-dominance importance by averaging each domain's incremental R2 over all possible entry orders.
6. Bootstrap by spatial blocks, not individual CTs. Report median contribution, 95% interval, and the frequency with which each domain ranks first, second, or third.
7. Repeat using ridge predictions as a sensitivity analysis when subset OLS is unstable.

### How it would enrich the story

The analysis could distinguish statements such as:

- Immigration/citizenship has a substantial unique association with municipal turnout.
- Education/resources and immigration/citizenship explain mostly the same geographic variation.
- Urban form adds relatively little uniquely for municipal turnout but more for federal turnout.
- Transportation contributes primarily through shared variance with density and tenure rather than independently.

That is more precise than saying variables form one bundle. It reveals whether a domain contributes new information or mainly tags the same Toronto geography as another domain.

## Recommended sequence

First implement spatially blocked nested CV, because it changes how confidently every model's performance can be interpreted. Next add spatial-block bootstrap stability for PLS loadings and VIPs. Then run domain-level commonality and Shapley/LMG importance using the same outer spatial partitions. The final narrative can combine: PLS for the shape of the latent geography, bootstrap stability for confidence in that shape, and domain attribution for unique-versus-shared explanatory contributions.

## References

- [Roberts et al., cross-validation strategies for spatially structured data](https://www.wsl.ch/lud/biodiversity_events/papers/Roberts_et_al-2017-Ecography.pdf)
- [Spatial cross-validation and predictive error](https://www.nature.com/articles/s41467-020-18321-y)
- [Bair et al., supervised principal components](https://web.stanford.edu/~hastie/Papers/spca_JASA.pdf)
- [Commonality analysis for correlated predictors](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.12166)
