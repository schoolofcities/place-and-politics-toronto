# Turnout vs Polling-Station Distance

## Scope

This report overwrites the prior distance analysis and uses the current accepted polling-station coordinates.
Municipal 2023 has complete official Open Toronto station points. Provincial 2025 is a partial official-location sample: exact Elections Ontario proposed-location matches and exact Open Toronto official-label recoveries are included; unresolved/fuzzy rows are excluded.
Federal 2025 remains out of this distance model because no official bulk station-location table has been found.

## Model Specification

The two main models are estimated separately:

`turnout_rate = beta0 + beta1 * distance_km + beta2 * poll_area_km2 + district fixed effects + error`

Distance is measured from the polling-division point-on-surface to the assigned polling-station/building point. Coefficients are turnout-rate units; multiply by 100 for percentage-point interpretation.

## Sample And Correlations

| Election | N | Mean turnout | Mean distance km | Median distance km | Pearson distance/turnout | Spearman distance/turnout | Pearson area/turnout |
|---|---|---|---|---|---|---|---|
| municipal_2023_mayor | 1351 | 32.1% | 0.212 | 0.138 | -0.225 | -0.299 | -0.170 |
| provincial_2025_partial | 1180 | 36.6% | 0.253 | 0.109 | -0.142 | -0.478 | -0.232 |

## Municipal 2023 Model

Model-ready rows: 1351. Adjusted R2: 0.144. RMSE: 0.112 turnout-rate units.

### Municipal Variable Summary

| Variable | N | Mean | Median | SD | Min | Max |
|---|---|---|---|---|---|---|
| Turnout rate | 1351 | 0.321 | 0.304 | 0.121 | 0.012 | 1.000 |
| Distance to polling station (km) | 1351 | 0.212 | 0.138 | 0.267 | 0.001 | 3.124 |
| Polling division area (km2) | 1351 | 0.498 | 0.302 | 0.902 | 0.000 | 19.118 |
| Votes | 1351 | 417.666 | 386.000 | 290.824 | 1.000 | 1504.000 |
| Electors | 1351 | 1435.826 | 1466.000 | 969.224 | 7.000 | 5229.000 |

### Municipal Coefficients

| Term | Estimate, percentage points | SE, percentage points | t | p approx. |
|---|---|---|---|---|
| Intercept | 25.87 | 1.67 | 15.49 | <0.001 |
| Distance to station (km) | -10.99 | 1.71 | -6.43 | <0.001 |
| Poll area (km2) | 0.57 | 0.51 | 1.13 | 0.258 |

### Municipal Figures

![distance_turnout_scatter for municipal_2023_mayor](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/municipal_2023_distance_turnout_scatter.svg)

![area_turnout_scatter for municipal_2023_mayor](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/municipal_2023_area_turnout_scatter.svg)

![distance_histogram for municipal_2023_mayor](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/municipal_2023_distance_histogram.svg)

![residual_fitted for municipal_2023_mayor](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/municipal_2023_residual_fitted.svg)

## Provincial 2025 Model

Model-ready rows: 1180. Adjusted R2: 0.159. RMSE: 0.088 turnout-rate units.

### Provincial Variable Summary

| Variable | N | Mean | Median | SD | Min | Max |
|---|---|---|---|---|---|---|
| Turnout rate | 1180 | 0.366 | 0.352 | 0.096 | 0.050 | 0.916 |
| Distance to polling station (km) | 1180 | 0.253 | 0.109 | 0.758 | 0.001 | 14.670 |
| Polling division area (km2) | 1180 | 0.536 | 0.158 | 1.068 | 0.000 | 15.067 |
| Votes | 1180 | 508.626 | 367.500 | 445.374 | 7.000 | 2642.000 |
| Electors | 1180 | 1546.120 | 1141.500 | 1416.386 | 18.000 | 6326.000 |

### Provincial Coefficients

| Term | Estimate, percentage points | SE, percentage points | t | p approx. |
|---|---|---|---|---|
| Intercept | 40.38 | 1.52 | 26.52 | <0.001 |
| Distance to station (km) | -0.96 | 0.35 | -2.72 | 0.007 |
| Poll area (km2) | -1.87 | 0.26 | -7.06 | <0.001 |

### Provincial Figures

![distance_turnout_scatter for provincial_2025_partial](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/provincial_2025_distance_turnout_scatter.svg)

![area_turnout_scatter for provincial_2025_partial](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/provincial_2025_area_turnout_scatter.svg)

![distance_histogram for provincial_2025_partial](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/provincial_2025_distance_histogram.svg)

![residual_fitted for provincial_2025_partial](../../../../data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/figures/provincial_2025_residual_fitted.svg)

## Comparison

Both elections show a negative distance-turnout relationship, but it is much stronger in the municipal sample. With district fixed effects and poll area in the model, an additional kilometre to the assigned station is associated with about -11.0 percentage points lower municipal turnout, compared with about -1.0 percentage points lower provincial turnout. Poll area behaves differently: the municipal coefficient is small, positive, and not clearly distinguishable from zero (0.6 percentage points per km2), while the provincial partial model shows a clearer negative association (-1.9 percentage points per km2). The municipal model explains slightly less variance than the provincial partial model after district fixed effects (adjusted R2 0.144 vs. 0.159), but the municipal location coverage is complete, making it the better evidence base for a clean accessibility story.

## Caveats

The municipal model is cleaner because station coverage is complete. The provincial model should be read as directional and exploratory because about 206 mapped provincial rows still lack a high-confidence station coordinate. The distance measure is straight-line point-on-surface distance, not walking-network distance, and polling-area size is a rough proxy for urban form as well as accessibility.
