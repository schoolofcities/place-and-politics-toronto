# Meeting-PLS Handoff Dictionary

This is the compact direct-use package for the meeting analysis. It combines
the selected meeting variables, four outcomes, and meeting-PLS outputs in one
585-row CT table, so Aniket or another analyst does not need to join the broader
release tables first.

## Files and Grain

- `toronto_ct_meeting_pls.csv`: authoritative analytical table.
- `toronto_ct_meeting_pls.geojson`: the same 65 properties with EPSG:4326 CT
  geometry for mapping.
- `toronto_ct_meeting_pls.xlsx`: formatted convenience workbook with frozen
  headers and a Read Me sheet.

Grain: one row per CT. Primary key: `ct_id`. Dimensions: 585 rows × 65 columns.

## Column Groups

### Identifiers

`ct_id`, `ctuid`, `dguid`, `geo_name`, and `census_year` identify the CT and
census reference.

### Fourteen Meeting Variables

| Domain | Variables |
| --- | --- |
| Demographic/socioeconomic | `block1_age_18_34_share`, `block1_age_65_plus_share`, `block1_average_household_size`, `block1_bachelors_or_higher_25_64_share`, `block1_low_income_lim_at_share` |
| Housing/urban form | `block2_renter_share`, `block2_same_address_5yr_share`, `block2_apartment_share`, `block2_condo_share`, `block2_population_density_per_km2` |
| Immigration/citizenship | `block3_citizen_adult_share`, `block3_immigrant_share`, `block3_visible_minority_share` |
| Transportation | `block5_tts_no_car_household_share` |

### Outcomes

The four `outcome_*_participation_citizen_18plus` columns contain mean,
municipal, provincial, and federal participation using the citizen-18+
denominator.

### Latent Scores

`meeting_{outcome}_pls_component_{N}_score` stores the fitted PLS component
score; the paired `_percentile` column gives its within-model CT rank. The mean
model has two components; municipal, provincial, and federal models each have
three.

### Predictions and Residuals

For each outcome-specific meeting model:

| Suffix | Meaning |
| --- | --- |
| `_fitted_participation` | In-sample fitted participation |
| `_residual` | Observed minus fitted participation |
| `_cv_prediction` | Fixed shuffled 10-fold CV prediction |
| `_cv_residual` | Observed minus CV prediction |
| `_included_flag` | CT inclusion indicator |

Use `../model_definitions/` for predictor order, component labels, loadings,
coefficients, VIP, and model performance. Use `../robustness_checks/` when
comparing meeting PLS with supervised PCA and Elastic Net.
