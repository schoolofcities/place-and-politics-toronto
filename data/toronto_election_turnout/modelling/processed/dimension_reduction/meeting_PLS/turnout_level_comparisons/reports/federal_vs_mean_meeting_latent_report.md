# Federal turnout Meeting-Variable PLS Compared With Mean Turnout

This report fits the same 14 meeting-specified predictors to `outcome_federal_participation_citizen_18plus` and compares that model with the previously specified mean-turnout construction. It does not model an election-level difference outcome; the comparison is between two separately supervised latent models.

## Model fit and robustness

| Outcome | Method | Components/selected | CV R2 | CV RMSE |
| --- | --- | --- | --- | --- |
| Mean turnout | PLS | 2 | 0.534 | 0.059 |
| Mean turnout | Supervised PCA | 6 | 0.521 | 0.060 |
| Mean turnout | Elastic net | 10.4 | 0.539 | 0.059 |
| Federal turnout | PLS | 3 | 0.317 | 0.082 |
| Federal turnout | Supervised PCA | 5 | 0.317 | 0.082 |
| Federal turnout | Elastic net | 8.1 | 0.327 | 0.081 |

The federal turnout PLS selected 3 component(s), with CV R2 `0.317` and CV RMSE `0.082`. The mean-turnout model selected 2 component(s), with CV R2 `0.534`. Supervised PCA tests whether a screened predictor-correlation structure predicts the outcome without PLS supervision; elastic net tests whether coefficient directions and predictive signal survive shrinkage and variable selection.

## Variable interpretation

The five highest-VIP predictors for federal turnout are average household size, bachelor or higher education share, visible minority share, immigrant share, condo share. The largest VIP shifts relative to mean turnout involve condo share, apartment share, same address five year share, immigrant share, citizen adult share.

| Variable | Mean VIP | Federal turnout VIP | VIP change | Same coefficient direction |
| --- | --- | --- | --- | --- |
| average household size | 1.398 | 1.595 | 0.197 | True |
| bachelor or higher education share | 1.586 | 1.584 | -0.002 | True |
| visible minority share | 1.838 | 1.522 | -0.315 | True |
| immigrant share | 1.662 | 1.291 | -0.371 | True |
| condo share | 0.313 | 0.845 | 0.531 | True |
| apartment share | 0.338 | 0.832 | 0.494 | True |
| same address five year share | 0.406 | 0.829 | 0.423 | True |
| age 65 plus share | 0.820 | 0.759 | -0.061 | True |
| age 18 to 34 share | 0.679 | 0.755 | 0.076 | True |
| TTS no car household share | 0.518 | 0.710 | 0.192 | False |
| citizen adult share | 1.027 | 0.704 | -0.322 | True |
| population density | 0.301 | 0.622 | 0.322 | True |
| low income share | 0.624 | 0.436 | -0.188 | True |
| renter share | 0.281 | 0.383 | 0.101 | True |

VIP values describe importance within each fitted model; they are not causal effects. “Same coefficient direction” checks whether the overall PLS regression direction agrees between the level-specific and mean models.

## Component construction compared with mean turnout

PLS component signs are arbitrary, so level components are sign-aligned to the closest mean-turnout loading vector before comparison.

### Component 1 versus Component 1

Loading cosine after accounting for arbitrary component sign: `0.842`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `0.453`; the matched mean component has projected outcome correlation `0.692`.

For the level-specific component, the high side is anchored by bachelor or higher education share, TTS no car household share, apartment share, population density, while the low side is anchored by average household size, visible minority share, immigrant share, same address five year share. For mean turnout, the matched high side is anchored by bachelor or higher education share, citizen adult share, TTS no car household share, population density, while its low side is anchored by visible minority share, immigrant share, average household size, low income share. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| apartment share | 0.032 | 0.242 | 0.211 |
| citizen adult share | 0.313 | 0.113 | 0.200 |
| low income share | -0.203 | -0.008 | 0.195 |
| same address five year share | -0.134 | -0.326 | 0.192 |
| age 18 to 34 share | -0.011 | 0.174 | 0.186 |
| condo share | 0.031 | 0.205 | 0.173 |
| population density | 0.067 | 0.233 | 0.166 |
| renter share | -0.037 | 0.122 | 0.158 |

### Component 2 versus Component 2

Loading cosine after accounting for arbitrary component sign: `0.519`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `-0.000`; the matched mean component has projected outcome correlation `0.000`.

For the level-specific component, the high side is anchored by citizen adult share, same address five year share, age 65 plus share, average household size, while the low side is anchored by age 18 to 34 share, renter share, low income share, apartment share. For mean turnout, the matched high side is anchored by age 65 plus share, immigrant share, same address five year share, low income share, while its low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| low income share | 0.129 | -0.354 | 0.483 |
| age 65 plus share | 0.812 | 0.347 | 0.464 |
| immigrant share | 0.251 | -0.181 | 0.432 |
| apartment share | 0.016 | -0.354 | 0.370 |
| citizen adult share | 0.033 | 0.387 | 0.354 |
| condo share | 0.123 | -0.187 | 0.309 |
| visible minority share | 0.045 | -0.264 | 0.309 |
| population density | -0.124 | -0.328 | 0.204 |

### Component 3 versus Component 2

Loading cosine after accounting for arbitrary component sign: `0.468`. Higher values indicate that the component constructs nearly the same predictor bundle. The aligned level component has projected outcome correlation `0.000`; the matched mean component has projected outcome correlation `0.000`.

For the level-specific component, the high side is anchored by age 65 plus share, immigrant share, condo share, low income share, while the low side is anchored by citizen adult share, average household size, same address five year share, age 18 to 34 share. For mean turnout, the matched high side is anchored by age 65 plus share, immigrant share, same address five year share, low income share, while its low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density. The table emphasizes the variables whose loadings changed most.

| Variable | Mean loading | Level loading (aligned) | Absolute loading difference |
| --- | --- | --- | --- |
| age 18 to 34 share | -0.528 | -0.069 | 0.460 |
| same address five year share | 0.250 | -0.143 | 0.393 |
| age 65 plus share | 0.812 | 0.432 | 0.380 |
| citizen adult share | 0.033 | -0.337 | 0.369 |
| apartment share | 0.016 | 0.357 | 0.341 |
| renter share | -0.192 | 0.107 | 0.298 |
| condo share | 0.123 | 0.407 | 0.284 |
| population density | -0.124 | 0.156 | 0.280 |

## Interpretation

Shared high VIP values and high loading cosine indicate a common citywide turnout geography. Differences in VIP and aligned loadings show which parts of that bundle are more characteristic of federal turnout than of the three-election mean. The PCA and elastic-net rows should be treated as robustness evidence, not as replacements for the PLS component narrative.

## Cautions

- These are ecological CT models using Census citizen-adult denominators, not individual voting models or official registered-elector turnout.
- Mean turnout contains the level-specific outcome being compared, so the two outcomes are mechanically related; this report describes construction differences and does not test an independent contrast.
- The repository's fixed shuffled 10-fold validation is retained for comparability and is not spatially blocked.
- Correlation screening for supervised PCA is performed on the analysis sample, so its CV score is exploratory rather than a fully nested estimate.
