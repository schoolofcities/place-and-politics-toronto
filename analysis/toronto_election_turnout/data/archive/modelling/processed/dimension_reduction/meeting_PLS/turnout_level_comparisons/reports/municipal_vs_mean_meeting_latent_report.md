# Municipal turnout Meeting-Variable PLS Compared With Mean Turnout

This report fits the same 14 meeting-specified predictors to `outcome_municipal_participation_citizen_18plus` and compares that model with the previously specified mean-turnout construction. It does not model an election-level difference outcome; the comparison is between two separately supervised latent models.

## Model fit and robustness

| Outcome | Method | Components/selected | CV R2 | CV RMSE |
| --- | --- | --- | --- | --- |
| Mean turnout | PLS | 2 | 0.534 | 0.059 |
| Mean turnout | Supervised PCA | 6 | 0.521 | 0.060 |
| Mean turnout | Elastic net | 10.4 | 0.539 | 0.059 |
| Municipal turnout | PLS | 3 | 0.629 | 0.063 |
| Municipal turnout | Supervised PCA | 8 | 0.626 | 0.063 |
| Municipal turnout | Elastic net | 12.9 | 0.639 | 0.062 |

The municipal turnout PLS selected 3 component(s), with CV R2 `0.629` and CV RMSE `0.063`. The mean-turnout model selected 2 component(s), with CV R2 `0.534`. Supervised PCA tests whether a screened predictor-correlation structure predicts the outcome without PLS supervision; elastic net tests whether coefficient directions and predictive signal survive shrinkage and variable selection.

## Variable interpretation

The five highest-VIP predictors for municipal turnout are visible minority share, immigrant share, bachelor or higher education share, citizen adult share, average household size. The largest VIP shifts relative to mean turnout involve average household size, low income share, citizen adult share, renter share, age 65 plus share.

| Variable | Mean VIP | Municipal turnout VIP | VIP change | Same coefficient direction |
| --- | --- | --- | --- | --- |
| visible minority share | 1.838 | 1.845 | 0.007 | True |
| immigrant share | 1.662 | 1.733 | 0.071 | True |
| bachelor or higher education share | 1.586 | 1.497 | -0.089 | True |
| citizen adult share | 1.027 | 1.287 | 0.260 | True |
| average household size | 1.398 | 1.043 | -0.355 | True |
| low income share | 0.624 | 0.890 | 0.266 | True |
| age 18 to 34 share | 0.679 | 0.755 | 0.077 | True |
| age 65 plus share | 0.820 | 0.656 | -0.163 | True |
| renter share | 0.281 | 0.532 | 0.251 | True |
| apartment share | 0.338 | 0.381 | 0.043 | True |
| TTS no car household share | 0.518 | 0.363 | -0.154 | True |
| same address five year share | 0.406 | 0.301 | -0.106 | False |
| population density | 0.301 | 0.290 | -0.010 | True |
| condo share | 0.313 | 0.286 | -0.027 | False |

VIP values describe importance within each fitted model; they are not causal effects. “Same coefficient direction” checks whether the overall PLS regression direction agrees between the level-specific and mean models.

## Component construction compared with mean turnout

PLS component signs are arbitrary, so level components are sign-aligned to the closest mean-turnout loading vector before comparison.

### Component 1 versus Component 1

Loading cosine after accounting for arbitrary component sign: `0.881`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `0.710`; the matched mean component has projected outcome correlation `0.692`.

For the level-specific component, the high side is anchored by citizen adult share, bachelor or higher education share, age 65 plus share, same address five year share, while the low side is anchored by visible minority share, immigrant share, low income share, average household size. For mean turnout, the matched high side is anchored by bachelor or higher education share, citizen adult share, TTS no car household share, population density, while its low side is anchored by visible minority share, immigrant share, average household size, low income share. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| same address five year share | -0.134 | 0.054 | 0.187 |
| apartment share | 0.032 | -0.155 | 0.187 |
| average household size | -0.360 | -0.180 | 0.179 |
| age 18 to 34 share | -0.011 | -0.167 | 0.156 |
| population density | 0.067 | -0.089 | 0.156 |
| TTS no car household share | 0.163 | 0.010 | 0.153 |
| condo share | 0.031 | -0.113 | 0.144 |
| renter share | -0.037 | -0.172 | 0.135 |

### Component 2 versus Component 2

Loading cosine after accounting for arbitrary component sign: `0.308`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `-0.000`; the matched mean component has projected outcome correlation `0.000`.

For the level-specific component, the high side is anchored by average household size, same address five year share, citizen adult share, visible minority share, while the low side is anchored by apartment share, population density, TTS no car household share, renter share. For mean turnout, the matched high side is anchored by age 65 plus share, immigrant share, same address five year share, low income share, while its low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| age 65 plus share | 0.812 | 0.033 | 0.779 |
| average household size | -0.053 | 0.442 | 0.496 |
| apartment share | 0.016 | -0.427 | 0.443 |
| low income share | 0.129 | -0.305 | 0.434 |
| condo share | 0.123 | -0.308 | 0.430 |
| population density | -0.124 | -0.366 | 0.242 |
| age 18 to 34 share | -0.528 | -0.298 | 0.230 |
| bachelor or higher education share | -0.010 | -0.229 | 0.219 |

### Component 3 versus Component 2

Loading cosine after accounting for arbitrary component sign: `0.976`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `-0.000`; the matched mean component has projected outcome correlation `0.000`.

For the level-specific component, the high side is anchored by age 65 plus share, same address five year share, immigrant share, low income share, while the low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density. For mean turnout, the matched high side is anchored by age 65 plus share, immigrant share, same address five year share, low income share, while its low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| condo share | 0.123 | -0.034 | 0.157 |
| average household size | -0.053 | 0.049 | 0.102 |
| apartment share | 0.016 | -0.074 | 0.090 |
| age 65 plus share | 0.812 | 0.736 | 0.076 |
| same address five year share | 0.250 | 0.326 | 0.075 |
| bachelor or higher education share | -0.010 | -0.045 | 0.035 |
| visible minority share | 0.045 | 0.075 | 0.030 |
| renter share | -0.192 | -0.169 | 0.023 |

## Interpretation

Shared high VIP values and high loading cosine indicate a common citywide turnout geography. Differences in VIP and aligned loadings show which parts of that bundle are more characteristic of municipal turnout than of the three-election mean. The PCA and elastic-net rows should be treated as robustness evidence, not as replacements for the PLS component narrative.

## Cautions

- These are ecological CT models using Census citizen-adult denominators, not individual voting models or official registered-elector turnout.
- Mean turnout contains the level-specific outcome being compared, so the two outcomes are mechanically related; this report describes construction differences and does not test an independent contrast.
- The repository's fixed shuffled 10-fold validation is retained for comparability and is not spatially blocked.
- Correlation screening for supervised PCA is performed on the analysis sample, so its CV score is exploratory rather than a fully nested estimate.
