# Block 1-3 Restricted Latent Variable Report: Mean Turnout

This report answers a follow-up question: what do the latent turnout components look like when the input set omits non-demographic/contextual variables and keeps only the approximate Block 1-3 predictors? The earlier latent report remains unchanged. This is a separate restricted-input analysis.

## Report Structure

**Section 1: Purpose and Input Restriction.** Defines the Block 1-3 restricted-input question and explains which kinds of non-demographic variables are omitted.

**Section 2: Variables Included and Omitted.** Lists the included Block 1-3 variables and the cleaned restricted PLS variables used for interpretation.

**Section 3: Restricted Model Summary.** Reports the restricted model fit and compares it with the earlier full, cleaned, interaction-augmented, and supervised PCA model summaries.

**Section 4: Restricted Latent Component Interpretation.** Interprets each cleaned Block 1-3 PLS component, including component sides, dominant variables, reference CTs, and turnout direction.

**Section 5: Comparison With the Previous Latent Report.** Explains what remains stable and what disappears when election, service, transportation, and civic-context variables are removed.

**Section 6: Suggested Takeaway.** Summarizes the restricted-input contribution to the broader turnout story.

**Appendix A: Full Component Loading Table.** Provides the complete cleaned restricted component loading table.

## Section 1: Purpose and Input Restriction

The restricted model keeps only the model-ready predictors from Blocks 1-3: demographic and socioeconomic composition; housing, tenure, built form, and residential stability; and immigration, citizenship, language, and racialized geography. It omits election competitiveness, service-contact, civic facility access, transportation/service access, road-safety, development, and other local-context variables.

This restriction is useful because it asks whether the main turnout story is already visible from demographic and housing composition alone. It also shows which parts of the previous latent report depended on non-demographic variables such as mayoral competition, federal/provincial margins, 311 requests, KSI collisions, development applications, and civic/service proximity.

## Section 2: Variables Included and Omitted

The original model-ready predictor universe contains 70 variables. The Block 1-3 restriction keeps 33 variables and omits 37 variables. From the kept variables, the cleaned restricted PLS uses 13 hand-picked representatives, following the same cleaned-model logic used in the earlier report.

### Included Block 1-3 Variables

| Variable | Family | Block |
| --- | --- | --- |
| age 18 to 34 share | Age structure | Block 1: Demographic and Socioeconomic Composition |
| age 35 to 64 share | Age structure | Block 1: Demographic and Socioeconomic Composition |
| age 65 plus share | Age structure | Block 1: Demographic and Socioeconomic Composition |
| median age | Age structure | Block 1: Demographic and Socioeconomic Composition |
| average household size | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| bachelor or higher education share | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| low income share | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| unemployment rate | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| owner share | Renter/owner tenure | Block 2: Housing, Tenure, Built Form, and Stability |
| renter share | Renter/owner tenure | Block 2: Housing, Tenure, Built Form, and Stability |
| same address five year share | Residential stability | Block 2: Housing, Tenure, Built Form, and Stability |
| same address one year share | Residential stability | Block 2: Housing, Tenure, Built Form, and Stability |
| apartment duplex count | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| apartment five plus storeys count | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| apartment share | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| apartment total count | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| apartment under five storeys count | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| apartments per square kilometre | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| condo share | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| condo status total dwellings | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| condominium dwellings count | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| condos per square kilometre | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| detached house share | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| population density | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| semi detached house share | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| structural type total dwellings | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| English or French knowledge share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| citizen adult share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| immigrant share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| non citizen share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| non official mother tongue share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| visible minority share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |

### Cleaned Restricted PLS Variables

| Variable | Family | Block |
| --- | --- | --- |
| age 18 to 34 share | Age structure | Block 1: Demographic and Socioeconomic Composition |
| age 65 plus share | Age structure | Block 1: Demographic and Socioeconomic Composition |
| average household size | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| bachelor or higher education share | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| low income share | Education, income, and household class | Block 1: Demographic and Socioeconomic Composition |
| renter share | Renter/owner tenure | Block 2: Housing, Tenure, Built Form, and Stability |
| same address five year share | Residential stability | Block 2: Housing, Tenure, Built Form, and Stability |
| apartment share | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| condo share | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| population density | Urban form and density | Block 2: Housing, Tenure, Built Form, and Stability |
| non citizen share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |
| visible minority share | Immigration, citizenship, language, and racialized geography | Block 3: Immigration, Citizenship, Language, and Racialized Geography |

The omitted variables are not listed in this report to keep the focus on the restricted demographic/housing/immigration model. They are saved separately in `non_block1_3_omitted_predictors.csv` for audit purposes.

## Section 3: Restricted Model Summary

| Model | Predictors | Components | CV R2 | CV RMSE |
| --- | --- | --- | --- | --- |
| Full original PLS | 70 | 12 | 0.565 | 0.057 |
| Theory-cleaned PLS | 27 | 5 | 0.558 | 0.058 |
| Interaction-augmented PLS | 38 | 1 | 0.566 | 0.057 |
| Supervised PCA | 15 | 8 | 0.540 | 0.059 |
| Block 1-3 full PLS | 33 | 10 | 0.528 | 0.060 |
| Block 1-3 cleaned PLS | 13 | 6 | 0.539 | 0.059 |

The full Block 1-3 PLS uses all 33 restricted predictors and reaches `CV R2 0.528` with `CV RMSE 0.060`. The cleaned Block 1-3 PLS uses 13 interpretable representatives and reaches `CV R2 0.539` with `CV RMSE 0.059`. The performance is lower than the previous interaction-augmented benchmark (`CV R2 0.566`), but it remains close enough to show that demographic, housing, and immigration/citizenship structure carries a large share of the turnout signal.

Most important cleaned restricted variables:

| Variable | Family | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- |
| visible minority share | Immigration, citizenship, language, and racialized geography | 1.900 | -0.642 | lower turnout |
| bachelor or higher education share | Education, income, and household class | 1.646 | 0.554 | higher turnout |
| average household size | Education, income, and household class | 1.455 | -0.485 | lower turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | 1.248 | -0.417 | lower turnout |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | 0.971 | -0.317 | lower turnout |
| age 65 plus share | Age structure | 0.659 | 0.182 | higher turnout |
| low income share | Education, income, and household class | 0.658 | -0.199 | higher turnout |
| age 18 to 34 share | Age structure | 0.610 | -0.136 | lower turnout |
| same address five year share | Residential stability | 0.460 | -0.120 | lower turnout |
| apartment share | Urban form and density | 0.435 | 0.089 | higher turnout |
| population density | Urban form and density | 0.412 | 0.102 | higher turnout |
| renter share | Renter/owner tenure | 0.392 | -0.081 | lower turnout |
| condo share | Urban form and density | 0.315 | 0.084 | higher turnout |

## Section 4: Restricted Latent Component Interpretation

The component interpretations below focus on the cleaned Block 1-3 PLS, because it is the most readable restricted-input model. As before, component signs are arbitrary; the interpretation should compare the two sides of each component rather than treating positive loadings as inherently good or negative loadings as inherently bad.

### Component 1: education and older-resource profile versus newcomer/citizenship/racialized household geography

**Interpretive summary.** This is the main restricted-input turnout axis. The high side is anchored by bachelor-or-higher education and, more weakly, older age/condo context. The low side is anchored by visible minority share, non-citizenship, recent immigration, larger household size, low income, renter share, and younger age. Its reference scores line up strongly with mean turnout, so this component reproduces the earlier report's primary education/resource versus newcomer/citizenship-racialized geography without needing election or service variables. The projected component score has correlation 0.658 with mean turnout.

Most influential variables:

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| visible minority share | Immigration, citizenship, language, and racialized geography | low side | -0.562 | 1.900 | -0.642 | lower turnout |
| bachelor or higher education share | Education, income, and household class | high side | 0.452 | 1.646 | 0.554 | higher turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | low side | -0.420 | 1.248 | -0.417 | lower turnout |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.356 | 0.971 | -0.317 | lower turnout |
| average household size | Education, income, and household class | low side | -0.337 | 1.455 | -0.485 | lower turnout |
| low income share | Education, income, and household class | low side | -0.270 | 0.658 | -0.199 | higher turnout |
| renter share | Renter/owner tenure | low side | -0.138 | 0.392 | -0.081 | lower turnout |
| age 65 plus share | Age structure | high side | 0.133 | 0.659 | 0.182 | higher turnout |
| age 18 to 34 share | Age structure | low side | -0.107 | 0.610 | -0.136 | lower turnout |
| same address five year share | Residential stability | low side | -0.056 | 0.460 | -0.120 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 2.0 | 0.727 | 3.791 | 0.658 |
| high side | 229.0 | 0.639 | 3.728 | 0.658 |
| high side | 87.0 | 0.560 | 3.600 | 0.658 |
| high side | 228.0 | 0.572 | 3.571 | 0.658 |
| high side | 226.0 | 0.595 | 3.395 | 0.658 |
| low side | 194.01 | 0.471 | -5.026 | 0.658 |
| low side | 260.05 | 0.353 | -4.661 | 0.658 |
| low side | 260.04 | 0.403 | -4.579 | 0.658 |
| low side | 250.05 | 0.399 | -4.235 | 0.658 |
| low side | 316.03 | 0.391 | -4.229 | 0.658 |

### Component 2: dense renter/apartment urban form versus larger-household residential stability

**Interpretive summary.** This component is mainly an urban-form and tenure contrast. The high side combines apartments, density, renter share, low income, recent immigration, younger age, and non-citizenship. The low side is more strongly tied to five-year residential stability and larger household size. Because its direct component-turnout correlation is near zero, it is best read as a secondary geography that separates kinds of urban places rather than as a simple turnout gradient. The projected component score has correlation 0.000 with mean turnout.

Most influential variables:

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| apartment share | Urban form and density | high side | 0.432 | 0.435 | 0.089 | higher turnout |
| same address five year share | Residential stability | low side | -0.386 | 0.460 | -0.120 | lower turnout |
| average household size | Education, income, and household class | low side | -0.366 | 1.455 | -0.485 | lower turnout |
| population density | Urban form and density | high side | 0.355 | 0.412 | 0.102 | higher turnout |
| renter share | Renter/owner tenure | high side | 0.329 | 0.392 | -0.081 | lower turnout |
| low income share | Education, income, and household class | high side | 0.327 | 0.658 | -0.199 | higher turnout |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | high side | 0.316 | 0.971 | -0.317 | lower turnout |
| condo share | Urban form and density | high side | 0.308 | 0.315 | 0.084 | higher turnout |
| age 18 to 34 share | Age structure | high side | 0.306 | 0.610 | -0.136 | lower turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | high side | 0.286 | 1.248 | -0.417 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 62.04 | 0.499 | 10.222 | 0.000 |
| high side | 63.05 | 0.503 | 8.721 | 0.000 |
| high side | 11.02 | 0.489 | 8.060 | 0.000 |
| high side | 11.03 | 0.503 | 7.832 | 0.000 |
| high side | 300.01 | 0.464 | 7.800 | 0.000 |
| low side | 224.0 | 0.604 | -4.392 | 0.000 |
| low side | 232.0 | 0.584 | -4.264 | 0.000 |
| low side | 229.0 | 0.639 | -4.231 | 0.000 |
| low side | 226.0 | 0.595 | -4.216 | 0.000 |
| low side | 361.02 | 0.542 | -4.186 | 0.000 |

### Component 3: older residential stability versus younger educated dense geography

**Interpretive summary.** This component is the cleanest age/stability contrast in the restricted model. The high side is older and more residentially stable, with some low-income and renter/apartment signal; the low side is younger, more educated, more condo/dense, and somewhat more non-citizen/recent-immigrant. Its direct turnout relationship is weak, but it helps show that age and stability are not identical to the main education/newcomer axis. The projected component score has correlation 0.000 with mean turnout.

Most influential variables:

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| age 65 plus share | Age structure | high side | 0.659 | 0.659 | 0.182 | higher turnout |
| age 18 to 34 share | Age structure | low side | -0.639 | 0.610 | -0.136 | lower turnout |
| same address five year share | Residential stability | high side | 0.425 | 0.460 | -0.120 | lower turnout |
| low income share | Education, income, and household class | high side | 0.231 | 0.658 | -0.199 | higher turnout |
| bachelor or higher education share | Education, income, and household class | low side | -0.218 | 1.646 | 0.554 | higher turnout |
| condo share | Urban form and density | low side | -0.167 | 0.315 | 0.084 | higher turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | low side | -0.117 | 1.248 | -0.417 | lower turnout |
| population density | Urban form and density | low side | -0.084 | 0.412 | 0.102 | higher turnout |
| renter share | Renter/owner tenure | high side | 0.074 | 0.392 | -0.081 | lower turnout |
| apartment share | Urban form and density | high side | 0.073 | 0.435 | 0.089 | higher turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 376.06 | 0.979 | 9.164 | 0.000 |
| high side | 205.0 | 0.521 | 8.045 | 0.000 |
| high side | 6.0 | 0.521 | 7.785 | 0.000 |
| high side | 324.03 | 0.597 | 3.418 | 0.000 |
| high side | 2.0 | 0.727 | 3.262 | 0.000 |
| low side | 11.02 | 0.489 | -7.424 | 0.000 |
| low side | 11.03 | 0.503 | -6.653 | 0.000 |
| low side | 8.01 | 0.527 | -6.365 | 0.000 |
| low side | 62.04 | 0.499 | -6.206 | 0.000 |
| low side | 12.03 | 0.430 | -5.837 | 0.000 |

### Component 4: dense educated mixed-newcomer geography versus older renter/lower-income contrast

**Interpretive summary.** This component mixes density and education with recent immigration and household size on one side, against older age, renter share, low income, and younger age on the other. It is not a clean high-turnout/low-turnout component. Its usefulness is interpretive: after the main demographic turnout axis, the model still separates different combinations of density, education, settlement, and household form. The projected component score has correlation -0.000 with mean turnout.

Most influential variables:

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| age 65 plus share | Age structure | low side | -0.503 | 0.659 | 0.182 | higher turnout |
| population density | Urban form and density | high side | 0.443 | 0.412 | 0.102 | higher turnout |
| bachelor or higher education share | Education, income, and household class | high side | 0.381 | 1.646 | 0.554 | higher turnout |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | high side | 0.373 | 0.971 | -0.317 | lower turnout |
| renter share | Renter/owner tenure | low side | -0.356 | 0.392 | -0.081 | lower turnout |
| low income share | Education, income, and household class | low side | -0.339 | 0.658 | -0.199 | higher turnout |
| average household size | Education, income, and household class | high side | 0.275 | 1.455 | -0.485 | lower turnout |
| age 18 to 34 share | Age structure | low side | -0.252 | 0.610 | -0.136 | lower turnout |
| condo share | Urban form and density | high side | 0.225 | 0.315 | 0.084 | higher turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | high side | 0.166 | 1.248 | -0.417 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 300.02 | 0.577 | 3.084 | -0.000 |
| high side | 307.06 | 0.591 | 2.757 | -0.000 |
| high side | 307.03 | 0.509 | 2.707 | -0.000 |
| high side | 128.06 | 0.623 | 2.696 | -0.000 |
| high side | 301.03 | 0.499 | 2.642 | -0.000 |
| low side | 376.06 | 0.979 | -7.165 | -0.000 |
| low side | 205.0 | 0.521 | -4.267 | -0.000 |
| low side | 6.0 | 0.521 | -3.696 | -0.000 |
| low side | 9.0 | 0.304 | -2.412 | -0.000 |
| low side | 192.0 | 0.610 | -2.394 | -0.000 |

### Component 5: renter/apartment lower-income profile versus older educated condo and citizenship contrast

**Interpretive summary.** This component contrasts a renter/apartment/lower-income profile with an opposite side containing older age, higher education, non-citizenship, visible minority share, condo share, and larger household size. The mixed signs show why later components need caution: they are not one-variable stories, but residual bundles left after Component 1 has already captured the strongest turnout gradient. The projected component score has correlation 0.000 with mean turnout.

Most influential variables:

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| age 65 plus share | Age structure | low side | -0.795 | 0.659 | 0.182 | higher turnout |
| bachelor or higher education share | Education, income, and household class | low side | -0.525 | 1.646 | 0.554 | higher turnout |
| renter share | Renter/owner tenure | high side | 0.524 | 0.392 | -0.081 | lower turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | low side | -0.385 | 1.248 | -0.417 | lower turnout |
| apartment share | Urban form and density | high side | 0.375 | 0.435 | 0.089 | higher turnout |
| visible minority share | Immigration, citizenship, language, and racialized geography | low side | -0.356 | 1.900 | -0.642 | lower turnout |
| condo share | Urban form and density | low side | -0.346 | 0.315 | 0.084 | higher turnout |
| low income share | Education, income, and household class | high side | 0.310 | 0.658 | -0.199 | higher turnout |
| population density | Urban form and density | low side | -0.246 | 0.412 | 0.102 | higher turnout |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.234 | 0.971 | -0.317 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 341.03 | 0.514 | 4.102 | 0.000 |
| high side | 9.0 | 0.304 | 3.431 | 0.000 |
| high side | 7.02 | 0.524 | 3.315 | 0.000 |
| high side | 4.0 | 0.500 | 3.176 | 0.000 |
| high side | 217.0 | 0.507 | 3.078 | 0.000 |
| low side | 6.0 | 0.521 | -6.379 | 0.000 |
| low side | 205.0 | 0.521 | -6.352 | 0.000 |
| low side | 376.06 | 0.979 | -5.167 | 0.000 |
| low side | 304.05 | 0.590 | -3.422 | 0.000 |
| low side | 307.06 | 0.591 | -3.413 | 0.000 |

### Component 6: condo/older profile versus renter dense-stability profile

**Interpretive summary.** This component is mostly a housing-form contrast. The high side is dominated by condo share, older age, and some visible-minority/non-citizen signal; the low side is dominated by renter share, population density, five-year stability, recent immigration, and larger household size. It is useful mainly as a reminder that condo, renter, and density variables do not all describe the same kind of urban place. The projected component score has correlation 0.000 with mean turnout.

Most influential variables:

| Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- |
| condo share | Urban form and density | high side | 0.815 | 0.315 | 0.084 | higher turnout |
| renter share | Renter/owner tenure | low side | -0.788 | 0.392 | -0.081 | lower turnout |
| population density | Urban form and density | low side | -0.420 | 0.412 | 0.102 | higher turnout |
| age 65 plus share | Age structure | high side | 0.353 | 0.659 | 0.182 | higher turnout |
| visible minority share | Immigration, citizenship, language, and racialized geography | high side | 0.326 | 1.900 | -0.642 | lower turnout |
| same address five year share | Residential stability | low side | -0.269 | 0.460 | -0.120 | lower turnout |
| low income share | Education, income, and household class | high side | 0.130 | 0.658 | -0.199 | higher turnout |
| recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.081 | 0.971 | -0.317 | lower turnout |
| non citizen share | Immigration, citizenship, language, and racialized geography | high side | 0.080 | 1.248 | -0.417 | lower turnout |
| average household size | Education, income, and household class | low side | -0.068 | 1.455 | -0.485 | lower turnout |

Reference CTs:

| Reference side | Reference CT | Mean turnout | Reference score | Component-turnout correlation |
| --- | --- | --- | --- | --- |
| high side | 376.06 | 0.979 | 8.513 | 0.000 |
| high side | 376.15 | 0.473 | 4.372 | 0.000 |
| high side | 378.2 | 0.549 | 4.164 | 0.000 |
| high side | 368.01 | 0.501 | 3.601 | 0.000 |
| high side | 260.07 | 0.522 | 3.545 | 0.000 |
| low side | 65.02 | 0.502 | -5.394 | 0.000 |
| low side | 128.06 | 0.623 | -3.869 | 0.000 |
| low side | 102.02 | 0.676 | -3.634 | 0.000 |
| low side | 194.01 | 0.471 | -3.518 | 0.000 |
| low side | 123.0 | 0.577 | -3.362 | 0.000 |


## Section 5: Comparison With the Previous Latent Report

The restricted analysis confirms the previous report's central demographic story. Even after removing election competitiveness, service-contact, civic access, transportation access, collisions, and development variables, the strongest remaining structure still separates education and older/stable or higher-resource CT profiles from newcomer/citizenship/racialized geography, larger households, renter/apartment urban form, and lower-income composition. This means the main education-versus-settlement/citizenship geography was not created by the non-demographic variables; it is already present inside Blocks 1-3.

The main difference is that the restricted model cannot express the earlier report's institutional and contextual layer. In the previous report, mayoral fragmentation and election margins helped connect social geography to electoral attachment. The interaction-augmented model also showed that service-contact variables, especially 311 requests, KSI collisions, and development applications, had conditional turnout meanings across different social geographies. Those mechanisms disappear by design here. The restricted model therefore gives a cleaner demographic map, but it gives a thinner civic-context story.

The restricted model also shifts more interpretive weight onto housing form, tenure, density, and residential stability. In the earlier cleaned PLS, these appeared as secondary dimensions after the main turnout-resource/newcomer-fragmentation axis. In the Block 1-3 version, they become more central because the model has no election or service variables available. This is helpful for showing that density and tenure are not just background controls: they are part of the compositional structure through which turnout differences appear.

The performance comparison is important but should not be overread. The restricted cleaned PLS (`CV R2 0.539`) underperforms the earlier theory-cleaned PLS (`CV R2 0.558`) and the interaction-augmented PLS (`CV R2 0.566`). That drop is expected because the restricted model excludes predictive non-demographic information. Substantively, the finding is that demographics/housing/citizenship explain much of the turnout geography, while election context and service/contact variables add extra explanatory structure.

## Section 6: Suggested Takeaway

The Block 1-3 restricted model supports a cautious version of the original story: mean turnout is strongly structured by demographic and residential composition even before election competitiveness and service-contact variables are allowed into the model. The most stable latent contrast is a resource/education/stability side versus a newcomer/citizenship/racialized/larger-household side. This should be interpreted ecologically, not as an individual-level statement about voters.

The earlier full latent report remains the richer story because it adds the political and municipal-context layers. The restricted report shows the demographic foundation underneath that story. Together, they suggest that turnout differences are not simply about one variable such as education, immigration, age, or renter status. They are about overlapping social geographies, with non-demographic variables adding evidence about electoral attachment and local civic/service context.

## Appendix A: Full Component Loading Table

| Component | Variable | Family | Component side | Component loading | VIP | Bivariate turnout correlation | PLS turnout direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Component 1 | visible minority share | Immigration, citizenship, language, and racialized geography | low side | -0.562 | 1.900 | -0.642 | lower turnout |
| Component 1 | bachelor or higher education share | Education, income, and household class | high side | 0.452 | 1.646 | 0.554 | higher turnout |
| Component 1 | non citizen share | Immigration, citizenship, language, and racialized geography | low side | -0.420 | 1.248 | -0.417 | lower turnout |
| Component 1 | recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.356 | 0.971 | -0.317 | lower turnout |
| Component 1 | average household size | Education, income, and household class | low side | -0.337 | 1.455 | -0.485 | lower turnout |
| Component 1 | low income share | Education, income, and household class | low side | -0.270 | 0.658 | -0.199 | higher turnout |
| Component 1 | renter share | Renter/owner tenure | low side | -0.138 | 0.392 | -0.081 | lower turnout |
| Component 1 | age 65 plus share | Age structure | high side | 0.133 | 0.659 | 0.182 | higher turnout |
| Component 1 | age 18 to 34 share | Age structure | low side | -0.107 | 0.610 | -0.136 | lower turnout |
| Component 1 | same address five year share | Residential stability | low side | -0.056 | 0.460 | -0.120 | lower turnout |
| Component 1 | apartment share | Urban form and density | low side | -0.047 | 0.435 | 0.089 | higher turnout |
| Component 1 | condo share | Urban form and density | high side | 0.009 | 0.315 | 0.084 | higher turnout |
| Component 1 | population density | Urban form and density | low side | -0.006 | 0.412 | 0.102 | higher turnout |
| Component 2 | apartment share | Urban form and density | high side | 0.432 | 0.435 | 0.089 | higher turnout |
| Component 2 | same address five year share | Residential stability | low side | -0.386 | 0.460 | -0.120 | lower turnout |
| Component 2 | average household size | Education, income, and household class | low side | -0.366 | 1.455 | -0.485 | lower turnout |
| Component 2 | population density | Urban form and density | high side | 0.355 | 0.412 | 0.102 | higher turnout |
| Component 2 | renter share | Renter/owner tenure | high side | 0.329 | 0.392 | -0.081 | lower turnout |
| Component 2 | low income share | Education, income, and household class | high side | 0.327 | 0.658 | -0.199 | higher turnout |
| Component 2 | recent immigrant share | Immigration, citizenship, language, and racialized geography | high side | 0.316 | 0.971 | -0.317 | lower turnout |
| Component 2 | condo share | Urban form and density | high side | 0.308 | 0.315 | 0.084 | higher turnout |
| Component 2 | age 18 to 34 share | Age structure | high side | 0.306 | 0.610 | -0.136 | lower turnout |
| Component 2 | non citizen share | Immigration, citizenship, language, and racialized geography | high side | 0.286 | 1.248 | -0.417 | lower turnout |
| Component 2 | bachelor or higher education share | Education, income, and household class | high side | 0.144 | 1.646 | 0.554 | higher turnout |
| Component 2 | age 65 plus share | Age structure | low side | -0.082 | 0.659 | 0.182 | higher turnout |
| Component 2 | visible minority share | Immigration, citizenship, language, and racialized geography | high side | 0.055 | 1.900 | -0.642 | lower turnout |
| Component 3 | age 65 plus share | Age structure | high side | 0.659 | 0.659 | 0.182 | higher turnout |
| Component 3 | age 18 to 34 share | Age structure | low side | -0.639 | 0.610 | -0.136 | lower turnout |
| Component 3 | same address five year share | Residential stability | high side | 0.425 | 0.460 | -0.120 | lower turnout |
| Component 3 | low income share | Education, income, and household class | high side | 0.231 | 0.658 | -0.199 | higher turnout |
| Component 3 | bachelor or higher education share | Education, income, and household class | low side | -0.218 | 1.646 | 0.554 | higher turnout |
| Component 3 | condo share | Urban form and density | low side | -0.167 | 0.315 | 0.084 | higher turnout |
| Component 3 | non citizen share | Immigration, citizenship, language, and racialized geography | low side | -0.117 | 1.248 | -0.417 | lower turnout |
| Component 3 | population density | Urban form and density | low side | -0.084 | 0.412 | 0.102 | higher turnout |
| Component 3 | renter share | Renter/owner tenure | high side | 0.074 | 0.392 | -0.081 | lower turnout |
| Component 3 | apartment share | Urban form and density | high side | 0.073 | 0.435 | 0.089 | higher turnout |
| Component 3 | recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.071 | 0.971 | -0.317 | lower turnout |
| Component 3 | visible minority share | Immigration, citizenship, language, and racialized geography | high side | 0.035 | 1.900 | -0.642 | lower turnout |
| Component 3 | average household size | Education, income, and household class | high side | 0.033 | 1.455 | -0.485 | lower turnout |
| Component 4 | age 65 plus share | Age structure | low side | -0.503 | 0.659 | 0.182 | higher turnout |
| Component 4 | population density | Urban form and density | high side | 0.443 | 0.412 | 0.102 | higher turnout |
| Component 4 | bachelor or higher education share | Education, income, and household class | high side | 0.381 | 1.646 | 0.554 | higher turnout |
| Component 4 | recent immigrant share | Immigration, citizenship, language, and racialized geography | high side | 0.373 | 0.971 | -0.317 | lower turnout |
| Component 4 | renter share | Renter/owner tenure | low side | -0.356 | 0.392 | -0.081 | lower turnout |
| Component 4 | low income share | Education, income, and household class | low side | -0.339 | 0.658 | -0.199 | higher turnout |
| Component 4 | average household size | Education, income, and household class | high side | 0.275 | 1.455 | -0.485 | lower turnout |
| Component 4 | age 18 to 34 share | Age structure | low side | -0.252 | 0.610 | -0.136 | lower turnout |
| Component 4 | condo share | Urban form and density | high side | 0.225 | 0.315 | 0.084 | higher turnout |
| Component 4 | non citizen share | Immigration, citizenship, language, and racialized geography | high side | 0.166 | 1.248 | -0.417 | lower turnout |
| Component 4 | apartment share | Urban form and density | low side | -0.100 | 0.435 | 0.089 | higher turnout |
| Component 4 | same address five year share | Residential stability | high side | 0.095 | 0.460 | -0.120 | lower turnout |
| Component 4 | visible minority share | Immigration, citizenship, language, and racialized geography | low side | -0.042 | 1.900 | -0.642 | lower turnout |
| Component 5 | age 65 plus share | Age structure | low side | -0.795 | 0.659 | 0.182 | higher turnout |
| Component 5 | bachelor or higher education share | Education, income, and household class | low side | -0.525 | 1.646 | 0.554 | higher turnout |
| Component 5 | renter share | Renter/owner tenure | high side | 0.524 | 0.392 | -0.081 | lower turnout |
| Component 5 | non citizen share | Immigration, citizenship, language, and racialized geography | low side | -0.385 | 1.248 | -0.417 | lower turnout |
| Component 5 | apartment share | Urban form and density | high side | 0.375 | 0.435 | 0.089 | higher turnout |
| Component 5 | visible minority share | Immigration, citizenship, language, and racialized geography | low side | -0.356 | 1.900 | -0.642 | lower turnout |
| Component 5 | condo share | Urban form and density | low side | -0.346 | 0.315 | 0.084 | higher turnout |
| Component 5 | low income share | Education, income, and household class | high side | 0.310 | 0.658 | -0.199 | higher turnout |
| Component 5 | population density | Urban form and density | low side | -0.246 | 0.412 | 0.102 | higher turnout |
| Component 5 | recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.234 | 0.971 | -0.317 | lower turnout |
| Component 5 | average household size | Education, income, and household class | low side | -0.210 | 1.455 | -0.485 | lower turnout |
| Component 5 | same address five year share | Residential stability | high side | 0.175 | 0.460 | -0.120 | lower turnout |
| Component 5 | age 18 to 34 share | Age structure | low side | -0.120 | 0.610 | -0.136 | lower turnout |
| Component 6 | condo share | Urban form and density | high side | 0.815 | 0.315 | 0.084 | higher turnout |
| Component 6 | renter share | Renter/owner tenure | low side | -0.788 | 0.392 | -0.081 | lower turnout |
| Component 6 | population density | Urban form and density | low side | -0.420 | 0.412 | 0.102 | higher turnout |
| Component 6 | age 65 plus share | Age structure | high side | 0.353 | 0.659 | 0.182 | higher turnout |
| Component 6 | visible minority share | Immigration, citizenship, language, and racialized geography | high side | 0.326 | 1.900 | -0.642 | lower turnout |
| Component 6 | same address five year share | Residential stability | low side | -0.269 | 0.460 | -0.120 | lower turnout |
| Component 6 | low income share | Education, income, and household class | high side | 0.130 | 0.658 | -0.199 | higher turnout |
| Component 6 | recent immigrant share | Immigration, citizenship, language, and racialized geography | low side | -0.081 | 0.971 | -0.317 | lower turnout |
| Component 6 | non citizen share | Immigration, citizenship, language, and racialized geography | high side | 0.080 | 1.248 | -0.417 | lower turnout |
| Component 6 | average household size | Education, income, and household class | low side | -0.068 | 1.455 | -0.485 | lower turnout |
| Component 6 | bachelor or higher education share | Education, income, and household class | high side | 0.037 | 1.646 | 0.554 | higher turnout |
| Component 6 | age 18 to 34 share | Age structure | low side | -0.020 | 0.610 | -0.136 | lower turnout |
| Component 6 | apartment share | Urban form and density | high side | 0.002 | 0.435 | 0.089 | higher turnout |
