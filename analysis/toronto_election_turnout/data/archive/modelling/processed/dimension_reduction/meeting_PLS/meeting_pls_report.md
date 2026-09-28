# Meeting PLS Report: Mean Turnout

This report fits a meeting-specified PLS model using 14 selected predictors across age, education/income/household, tenure, residential stability, urban form, immigration/citizenship, and transportation. The outcome is mean CT turnout (`outcome_mean_participation_citizen_18plus`).

## Report Structure

**Section 1: Model Input.** Lists the exact meeting-specified variables used in the model.

**Section 2: Model Results.** Reports predictive fit, selected component count, and the most important variables by VIP.

**Section 3: Component Interpretation.** Interprets each retained PLS component as a latent social-geographic contrast.

**Section 4: Short Takeaway.** Summarizes what this compact meeting PLS adds to the earlier latent reports.

**Appendix A: Full Component Loading Table.** Provides all component loadings for audit.

## Section 1: Model Input

The model uses 14 predictors:

| Variable | Family | Model column |
| --- | --- | --- |
| age 18 to 34 share | Age structure | block1_age_18_34_share |
| age 65 plus share | Age structure | block1_age_65_plus_share |
| average household size | Education, income, and household | block1_average_household_size |
| bachelor or higher education share | Education, income, and household | block1_bachelors_or_higher_25_64_share |
| low income share | Education, income, and household | block1_low_income_lim_at_share |
| renter share | Tenure | block2_renter_share |
| same address five year share | Residential stability | block2_same_address_5yr_share |
| apartment share | Urban form | block2_apartment_share |
| condo share | Urban form | block2_condo_share |
| population density | Urban form | block2_population_density_per_km2 |
| citizen adult share | Immigration and citizenship | block3_citizen_adult_share |
| immigrant share | Immigration and citizenship | block3_immigrant_share |
| visible minority share | Immigration and citizenship | block3_visible_minority_share |
| TTS no car household share | Transportation | block5_tts_no_car_household_share |

## Section 2: Model Results

| Model | Observations | Predictors | Components | Train R2 | CV R2 | CV RMSE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Meeting PLS | 585 | 14 | 2 | 0.562 | 0.534 | 0.059 |

The meeting PLS selects 2 components by cross-validation. Its cross-validated R2 is `0.534`, with cross-validated RMSE `0.059`. This is a compact model, so the useful question is less whether it beats the larger models and more whether it preserves the main interpretable turnout axes.

Most important variables:

| Variable | Family | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- |
| visible minority share | Immigration and citizenship | 1.838 | -0.642 | lower turnout |
| immigrant share | Immigration and citizenship | 1.662 | -0.573 | lower turnout |
| bachelor or higher education share | Education, income, and household | 1.586 | 0.554 | higher turnout |
| average household size | Education, income, and household | 1.398 | -0.485 | lower turnout |
| citizen adult share | Immigration and citizenship | 1.027 | 0.353 | higher turnout |
| age 65 plus share | Age structure | 0.820 | 0.182 | higher turnout |
| age 18 to 34 share | Age structure | 0.679 | -0.136 | lower turnout |
| low income share | Education, income, and household | 0.624 | -0.199 | lower turnout |
| TTS no car household share | Transportation | 0.518 | 0.174 | higher turnout |
| same address five year share | Residential stability | 0.406 | -0.120 | lower turnout |
| apartment share | Urban form | 0.338 | 0.089 | higher turnout |
| condo share | Urban form | 0.313 | 0.084 | higher turnout |
| population density | Urban form | 0.301 | 0.102 | higher turnout |
| renter share | Tenure | 0.281 | -0.081 | lower turnout |

## Section 3: Component Interpretation

### Component 1: education/resource attachment versus racialized-immigrant household geography

**Interpretive summary.** The high side is anchored by bachelor or higher education share, citizen adult share, TTS no car household share, population density, age 65 plus share. The low side is anchored by visible minority share, immigrant share, average household size, low income share, same address five year share. The projected component score correlates 0.692 with mean turnout, so this component is best read as a direct higher-turnout axis.

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| visible minority share | Immigration and citizenship | low side | -0.516 | 1.838 | -0.642 | lower turnout |
| immigrant share | Immigration and citizenship | low side | -0.503 | 1.662 | -0.573 | lower turnout |
| bachelor or higher education share | Education, income, and household | high side | 0.438 | 1.586 | 0.554 | higher turnout |
| average household size | Education, income, and household | low side | -0.360 | 1.398 | -0.485 | lower turnout |
| citizen adult share | Immigration and citizenship | high side | 0.313 | 1.027 | 0.353 | higher turnout |
| low income share | Education, income, and household | low side | -0.203 | 0.624 | -0.199 | lower turnout |
| TTS no car household share | Transportation | high side | 0.163 | 0.518 | 0.174 | higher turnout |
| same address five year share | Residential stability | low side | -0.134 | 0.406 | -0.120 | lower turnout |
| population density | Urban form | high side | 0.067 | 0.301 | 0.102 | higher turnout |
| renter share | Tenure | low side | -0.037 | 0.281 | -0.081 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 47.03 | 0.656 | 3.685 | 0.692 |
| high side | 87.0 | 0.560 | 3.439 | 0.692 |
| high side | 102.04 | 0.539 | 3.348 | 0.692 |
| low side | 194.01 | 0.471 | -3.921 | 0.692 |
| low side | 377.06 | 0.432 | -3.907 | 0.692 |
| low side | 376.06 | 0.979 | -3.861 | 0.692 |

### Component 2: older residential stability versus younger no-car renter/density geography

**Interpretive summary.** The high side is anchored by age 65 plus share, immigrant share, same address five year share, low income share, condo share. The low side is anchored by age 18 to 34 share, TTS no car household share, renter share, population density, average household size. The projected component score correlates 0.000 with mean turnout, so this component is best read as a secondary social-geographic contrast.

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| age 65 plus share | Age structure | high side | 0.812 | 0.820 | 0.182 | higher turnout |
| age 18 to 34 share | Age structure | low side | -0.528 | 0.679 | -0.136 | lower turnout |
| immigrant share | Immigration and citizenship | high side | 0.251 | 1.662 | -0.573 | lower turnout |
| same address five year share | Residential stability | high side | 0.250 | 0.406 | -0.120 | lower turnout |
| TTS no car household share | Transportation | low side | -0.218 | 0.518 | 0.174 | higher turnout |
| renter share | Tenure | low side | -0.192 | 0.281 | -0.081 | lower turnout |
| low income share | Education, income, and household | high side | 0.129 | 0.624 | -0.199 | lower turnout |
| population density | Urban form | low side | -0.124 | 0.301 | 0.102 | higher turnout |
| condo share | Urban form | high side | 0.123 | 0.313 | 0.084 | higher turnout |
| average household size | Education, income, and household | low side | -0.053 | 1.398 | -0.485 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 376.06 | 0.979 | 11.432 | 0.000 |
| high side | 205.0 | 0.521 | 9.164 | 0.000 |
| high side | 6.0 | 0.521 | 8.123 | 0.000 |
| low side | 11.02 | 0.489 | -5.861 | 0.000 |
| low side | 62.04 | 0.499 | -5.372 | 0.000 |
| low side | 44.02 | 0.579 | -5.289 | 0.000 |


## Section 4: Short Takeaway

The meeting PLS keeps the main demographic story visible in a smaller, more directed variable set. The strongest component again separates education/resource variables from visible-minority, immigrant, larger-household, renter, and lower-income geography. This supports the earlier interpretation that the main turnout pattern is not dependent on service or election-context variables alone.

The second component mostly separates age, stability, tenure, density, and no-car/transportation context. It is useful as descriptive geography, but only the first component should be read as a strong direct turnout gradient. The compact variable list therefore gives a clean meeting-friendly version of the broader latent story: turnout is structured by overlapping education/class, settlement/citizenship, household, tenure, density, and transportation geographies.

## Appendix A: Full Component Loading Table

| Component | Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Component 1 | visible minority share | Immigration and citizenship | low side | -0.516 | 1.838 | -0.642 | lower turnout |
| Component 1 | immigrant share | Immigration and citizenship | low side | -0.503 | 1.662 | -0.573 | lower turnout |
| Component 1 | bachelor or higher education share | Education, income, and household | high side | 0.438 | 1.586 | 0.554 | higher turnout |
| Component 1 | average household size | Education, income, and household | low side | -0.360 | 1.398 | -0.485 | lower turnout |
| Component 1 | citizen adult share | Immigration and citizenship | high side | 0.313 | 1.027 | 0.353 | higher turnout |
| Component 1 | low income share | Education, income, and household | low side | -0.203 | 0.624 | -0.199 | lower turnout |
| Component 1 | TTS no car household share | Transportation | high side | 0.163 | 0.518 | 0.174 | higher turnout |
| Component 1 | same address five year share | Residential stability | low side | -0.134 | 0.406 | -0.120 | lower turnout |
| Component 1 | population density | Urban form | high side | 0.067 | 0.301 | 0.102 | higher turnout |
| Component 1 | renter share | Tenure | low side | -0.037 | 0.281 | -0.081 | lower turnout |
| Component 1 | age 65 plus share | Age structure | high side | 0.034 | 0.820 | 0.182 | higher turnout |
| Component 1 | apartment share | Urban form | high side | 0.032 | 0.338 | 0.089 | higher turnout |
| Component 1 | condo share | Urban form | high side | 0.031 | 0.313 | 0.084 | higher turnout |
| Component 1 | age 18 to 34 share | Age structure | low side | -0.011 | 0.679 | -0.136 | lower turnout |
| Component 2 | age 65 plus share | Age structure | high side | 0.812 | 0.820 | 0.182 | higher turnout |
| Component 2 | age 18 to 34 share | Age structure | low side | -0.528 | 0.679 | -0.136 | lower turnout |
| Component 2 | immigrant share | Immigration and citizenship | high side | 0.251 | 1.662 | -0.573 | lower turnout |
| Component 2 | same address five year share | Residential stability | high side | 0.250 | 0.406 | -0.120 | lower turnout |
| Component 2 | TTS no car household share | Transportation | low side | -0.218 | 0.518 | 0.174 | higher turnout |
| Component 2 | renter share | Tenure | low side | -0.192 | 0.281 | -0.081 | lower turnout |
| Component 2 | low income share | Education, income, and household | high side | 0.129 | 0.624 | -0.199 | lower turnout |
| Component 2 | population density | Urban form | low side | -0.124 | 0.301 | 0.102 | higher turnout |
| Component 2 | condo share | Urban form | high side | 0.123 | 0.313 | 0.084 | higher turnout |
| Component 2 | average household size | Education, income, and household | low side | -0.053 | 1.398 | -0.485 | lower turnout |
| Component 2 | visible minority share | Immigration and citizenship | high side | 0.045 | 1.838 | -0.642 | lower turnout |
| Component 2 | citizen adult share | Immigration and citizenship | high side | 0.033 | 1.027 | 0.353 | higher turnout |
| Component 2 | apartment share | Urban form | high side | 0.016 | 0.338 | 0.089 | higher turnout |
| Component 2 | bachelor or higher education share | Education, income, and household | low side | -0.010 | 1.586 | 0.554 | higher turnout |
