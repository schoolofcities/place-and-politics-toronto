# Provincial turnout Meeting-Variable PLS Compared With Mean Turnout

This report fits the same 14 meeting-specified predictors to `outcome_provincial_participation_citizen_18plus` and compares that model with the previously specified mean-turnout construction. It does not model an election-level difference outcome; the comparison is between two separately supervised latent models.

## Model fit and robustness

| Outcome | Method | Components/selected | CV R2 | CV RMSE |
| --- | --- | --- | --- | --- |
| Mean turnout | PLS | 2 | 0.534 | 0.059 |
| Mean turnout | Supervised PCA | 6 | 0.521 | 0.060 |
| Mean turnout | Elastic net | 10.4 | 0.539 | 0.059 |
| Provincial turnout | PLS | 3 | 0.371 | 0.073 |
| Provincial turnout | Supervised PCA | 4 | 0.363 | 0.074 |
| Provincial turnout | Elastic net | 14.0 | 0.375 | 0.073 |

The provincial turnout PLS selected 3 component(s), with CV R2 `0.371` and CV RMSE `0.073`. The mean-turnout model selected 2 component(s), with CV R2 `0.534`. Supervised PCA tests whether a screened predictor-correlation structure predicts the outcome without PLS supervision; elastic net tests whether coefficient directions and predictive signal survive shrinkage and variable selection.

## Variable interpretation

The five highest-VIP predictors for provincial turnout are visible minority share, immigrant share, average household size, bachelor or higher education share, citizen adult share. The largest VIP shifts relative to mean turnout involve apartment share, TTS no car household share, population density, bachelor or higher education share, age 18 to 34 share.

| Variable | Mean VIP | Provincial turnout VIP | VIP change | Same coefficient direction |
| --- | --- | --- | --- | --- |
| visible minority share | 1.838 | 1.819 | -0.019 | True |
| immigrant share | 1.662 | 1.633 | -0.030 | True |
| average household size | 1.398 | 1.524 | 0.126 | True |
| bachelor or higher education share | 1.586 | 1.443 | -0.143 | True |
| citizen adult share | 1.027 | 0.961 | -0.066 | True |
| TTS no car household share | 0.518 | 0.712 | 0.194 | True |
| age 65 plus share | 0.820 | 0.697 | -0.123 | True |
| apartment share | 0.338 | 0.569 | 0.231 | True |
| age 18 to 34 share | 0.679 | 0.549 | -0.130 | True |
| low income share | 0.624 | 0.548 | -0.076 | True |
| same address five year share | 0.406 | 0.534 | 0.128 | False |
| population density | 0.301 | 0.495 | 0.194 | True |
| condo share | 0.313 | 0.399 | 0.085 | True |
| renter share | 0.281 | 0.300 | 0.019 | True |

VIP values describe importance within each fitted model; they are not causal effects. “Same coefficient direction” checks whether the overall PLS regression direction agrees between the level-specific and mean models.

## Component construction compared with mean turnout

PLS component signs are arbitrary, so level components are sign-aligned to the closest mean-turnout loading vector before comparison.

### Component 1 versus Component 1

Loading cosine after accounting for arbitrary component sign: `0.983`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `0.574`; the matched mean component has projected outcome correlation `0.692`.

For the level-specific component, the high side is anchored by bachelor or higher education share, citizen adult share, TTS no car household share, population density, while the low side is anchored by visible minority share, immigrant share, average household size, same address five year share. For mean turnout, the matched high side is anchored by bachelor or higher education share, citizen adult share, TTS no car household share, population density, while its low side is anchored by visible minority share, immigrant share, average household size, low income share. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| apartment share | 0.032 | 0.103 | 0.072 |
| renter share | -0.037 | 0.027 | 0.063 |
| age 18 to 34 share | -0.011 | 0.052 | 0.063 |
| low income share | -0.203 | -0.143 | 0.061 |
| same address five year share | -0.134 | -0.194 | 0.060 |
| TTS no car household share | 0.163 | 0.223 | 0.060 |
| population density | 0.067 | 0.125 | 0.058 |
| citizen adult share | 0.313 | 0.259 | 0.054 |

### Component 2 versus Component 2

Loading cosine after accounting for arbitrary component sign: `0.675`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `0.000`; the matched mean component has projected outcome correlation `0.000`.

For the level-specific component, the high side is anchored by age 65 plus share, same address five year share, citizen adult share, average household size, while the low side is anchored by age 18 to 34 share, renter share, population density, apartment share. For mean turnout, the matched high side is anchored by age 65 plus share, immigrant share, same address five year share, low income share, while its low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| low income share | 0.129 | -0.281 | 0.410 |
| apartment share | 0.016 | -0.368 | 0.384 |
| condo share | 0.123 | -0.237 | 0.360 |
| citizen adult share | 0.033 | 0.363 | 0.330 |
| immigrant share | 0.251 | -0.037 | 0.288 |
| average household size | -0.053 | 0.222 | 0.276 |
| age 65 plus share | 0.812 | 0.540 | 0.272 |
| population density | -0.124 | -0.382 | 0.258 |

### Component 3 versus Component 1

Loading cosine after accounting for arbitrary component sign: `0.160`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `-0.000`; the matched mean component has projected outcome correlation `0.692`.

For the level-specific component, the high side is anchored by average household size, citizen adult share, same address five year share, bachelor or higher education share, while the low side is anchored by apartment share, low income share, condo share, population density. For mean turnout, the matched high side is anchored by bachelor or higher education share, citizen adult share, TTS no car household share, population density, while its low side is anchored by visible minority share, immigrant share, average household size, low income share. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| average household size | -0.360 | 0.328 | 0.688 |
| apartment share | 0.032 | -0.443 | 0.474 |
| bachelor or higher education share | 0.438 | 0.010 | 0.428 |
| TTS no car household share | 0.163 | -0.236 | 0.400 |
| condo share | 0.031 | -0.343 | 0.374 |
| same address five year share | -0.134 | 0.228 | 0.362 |
| population density | 0.067 | -0.294 | 0.361 |
| visible minority share | -0.516 | -0.169 | 0.348 |

## Interpretation

Shared high VIP values and high loading cosine indicate a common citywide turnout geography. Differences in VIP and aligned loadings show which parts of that bundle are more characteristic of provincial turnout than of the three-election mean. The PCA and elastic-net rows should be treated as robustness evidence, not as replacements for the PLS component narrative.

## Cautions

- These are ecological CT models using Census citizen-adult denominators, not individual voting models or official registered-elector turnout.
- Mean turnout contains the level-specific outcome being compared, so the two outcomes are mechanically related; this report describes construction differences and does not test an independent contrast.
- The repository's fixed shuffled 10-fold validation is retained for comparability and is not spatially blocked.
- Correlation screening for supervised PCA is performed on the analysis sample, so its CV score is exploratory rather than a fully nested estimate.
