# Variable Lists for the Dimension-Reduction Models

This note lists the model-ready predictors used in the dimension-reduction workflow and the hand-picked cleaned PLS subset used for the main latent-variable interpretation. The labels below are readable variable descriptions rather than raw database column names.

- Original model-ready predictor set: 70 variables
- Pared-down theory-cleaned PLS set: 27 variables
- Excluded from the cleaned PLS set: 43 variables

## Section 1: Original Model-Ready Predictor Set

### Age Structure

- age 18-34 share
- age 35-64 share
- age 65 plus share
- median age

### Education, Income, and Household Class

- average household size
- bachelors or higher 25-64 share
- low income share
- unemployment rate share

### Renter/Owner Tenure

- owner share
- renter share

### Residential Stability

- same address 1yr share
- same address 5yr share

### Urban Form and Density

- apartment 5plus storeys count
- apartment duplex count
- apartment lt5 storeys count
- apartment share
- apartment total count
- apartments per km2
- condo share
- condo status total dwellings
- condominium dwellings count
- condos per km2
- detached share
- population density per km2
- semi detached share
- structural type total dwellings

### Immigration, Citizenship, and Racialized Geography

- citizen adult share
- english french knowledge share
- immigrant share
- non citizen share
- non official mother tongue share
- recent immigrant share
- visible minority share

### Local Mayoral Competitiveness

- effective mayoral candidates above 5 percent
- mayoral candidate count above 5 percent
- mayoral top two margin
- mayoral vote fragmentation
- mayoral winner margin

### Federal Competitiveness

- effective federal parties above 5 percent
- federal margin
- federal party count above 5 percent
- federal vote fragmentation

### Provincial Competitiveness

- effective provincial parties above 5 percent
- provincial margin
- provincial party count above 5 percent
- provincial vote fragmentation

### Transportation Access

- no car household share
- transit commute share preferred
- tts no car household share
- tts overlap area m2
- tts transit trip share

### Civic/Service Proximity

- community centre access within 1200m
- community centre count within 1200m
- community centre nearest m
- library access within 1200m
- library count within 1200m
- library nearest m
- park count within 1200m
- park nearest m
- shelter access within 1200m
- shelter count within 1200m
- shelter nearest m

### Service Contact and Local Need

- development applications 2021-2025
- development applications 2021-2025 per 1000
- ksi collision events 2021-2025
- ksi collision events 2021-2025 per 1000
- requests 311 2023 2025 estimated count
- requests 311 per 1000
- school age 5-17 share
- social housing share

## Section 2: Pared-Down Hand-Picked Set Used in the Cleaned PLS

### Age Structure

- age 18-34 share
- age 65 plus share

### Education, Income, and Household Class

- average household size
- bachelors or higher 25-64 share
- low income share

### Renter/Owner Tenure

- renter share

### Residential Stability

- same address 5yr share

### Urban Form and Density

- apartment share
- condo share
- population density per km2

### Immigration, Citizenship, and Racialized Geography

- non citizen share
- recent immigrant share
- visible minority share

### Local Mayoral Competitiveness

- effective mayoral candidates above 5 percent
- mayoral top two margin

### Federal Competitiveness

- federal margin

### Provincial Competitiveness

- provincial margin

### Transportation Access

- no car household share
- transit commute share preferred

### Civic/Service Proximity

- community centre access within 1200m
- library access within 1200m
- shelter access within 1200m

### Service Contact and Local Need

- development applications 2021-2025 per 1000
- ksi collision events 2021-2025 per 1000
- requests 311 per 1000
- school age 5-17 share
- social housing share

## Section 3: Variables Excluded From the Cleaned PLS Set

These variables were available in the original model-ready predictor set, but were not included in the hand-picked cleaned PLS set. Most were removed either to avoid double-weighting very similar concepts or to keep the cleaned model compact enough for interpretation.

### Age Structure

| Excluded variable | Reason |
| --- | --- |
| age 35-64 share | Excluded to keep the cleaned model smaller and easier to interpret. |
| median age | Excluded to avoid double-counting a highly correlated concept. |

### Education, Income, and Household Class

| Excluded variable | Reason |
| --- | --- |
| unemployment rate share | Excluded to keep the cleaned model smaller and easier to interpret. |

### Renter/Owner Tenure

| Excluded variable | Reason |
| --- | --- |
| owner share | Excluded because it is near-duplicate/inverse/compositional with selected family information. |

### Residential Stability

| Excluded variable | Reason |
| --- | --- |
| same address 1yr share | Excluded to avoid double-counting a highly correlated concept. |

### Urban Form and Density

| Excluded variable | Reason |
| --- | --- |
| apartment 5plus storeys count | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| apartment duplex count | Excluded to keep the cleaned model smaller and easier to interpret. |
| apartment lt5 storeys count | Excluded to keep the cleaned model smaller and easier to interpret. |
| apartment total count | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| apartments per km2 | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| condo status total dwellings | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| condominium dwellings count | Excluded to avoid double-counting a highly correlated concept. |
| condos per km2 | Excluded to avoid double-counting a highly correlated concept. |
| detached share | Excluded to avoid double-counting a highly correlated concept. |
| semi detached share | Excluded to keep the cleaned model smaller and easier to interpret. |
| structural type total dwellings | Excluded because it is near-duplicate/inverse/compositional with selected family information. |

### Immigration, Citizenship, and Racialized Geography

| Excluded variable | Reason |
| --- | --- |
| citizen adult share | Excluded to avoid double-counting a highly correlated concept. |
| english french knowledge share | Excluded to keep the cleaned model smaller and easier to interpret. |
| immigrant share | Excluded to avoid double-counting a highly correlated concept. |
| non official mother tongue share | Excluded to avoid double-counting a highly correlated concept. |

### Local Mayoral Competitiveness

| Excluded variable | Reason |
| --- | --- |
| mayoral candidate count above 5 percent | Excluded to keep the cleaned model smaller and easier to interpret. |
| mayoral vote fragmentation | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| mayoral winner margin | Excluded because it is near-duplicate/inverse/compositional with selected family information. |

### Federal Competitiveness

| Excluded variable | Reason |
| --- | --- |
| effective federal parties above 5 percent | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| federal party count above 5 percent | Excluded to keep the cleaned model smaller and easier to interpret. |
| federal vote fragmentation | Excluded because it is near-duplicate/inverse/compositional with selected family information. |

### Provincial Competitiveness

| Excluded variable | Reason |
| --- | --- |
| effective provincial parties above 5 percent | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| provincial party count above 5 percent | Excluded to keep the cleaned model smaller and easier to interpret. |
| provincial vote fragmentation | Excluded because it is near-duplicate/inverse/compositional with selected family information. |

### Transportation Access

| Excluded variable | Reason |
| --- | --- |
| tts no car household share | Excluded because it is near-duplicate/inverse/compositional with selected family information. |
| tts overlap area m2 | Excluded to avoid double-counting a highly correlated concept. |
| tts transit trip share | Excluded because it is near-duplicate/inverse/compositional with selected family information. |

### Civic/Service Proximity

| Excluded variable | Reason |
| --- | --- |
| community centre count within 1200m | Excluded to keep the cleaned model smaller and easier to interpret. |
| community centre nearest m | Excluded to keep the cleaned model smaller and easier to interpret. |
| library count within 1200m | Excluded to avoid double-counting a highly correlated concept. |
| library nearest m | Excluded to avoid double-counting a highly correlated concept. |
| park count within 1200m | Excluded to keep the cleaned model smaller and easier to interpret. |
| park nearest m | Excluded to keep the cleaned model smaller and easier to interpret. |
| shelter count within 1200m | Excluded to keep the cleaned model smaller and easier to interpret. |
| shelter nearest m | Excluded to keep the cleaned model smaller and easier to interpret. |

### Service Contact and Local Need

| Excluded variable | Reason |
| --- | --- |
| development applications 2021-2025 | Excluded to keep the cleaned model smaller and easier to interpret. |
| ksi collision events 2021-2025 | Excluded to keep the cleaned model smaller and easier to interpret. |
| requests 311 2023 2025 estimated count | Excluded to avoid double-counting a highly correlated concept. |
