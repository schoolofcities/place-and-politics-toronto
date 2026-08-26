# Step 3 Report: Domain Commonality and Shapley Relative Importance

## What has been done

The seven manually specified research domains were held fixed exactly as proposed. All 128 possible domain-subset OLS models were fit for each outcome. Unique R2 is the loss from removing a domain from the full model. Shapley R2 averages its incremental contribution over every possible domain entry order. The difference is the domain's allocated share of variance jointly explained with other domains. A 500-draw spatial-block bootstrap supplies uncertainty files.

## Results

| Outcome | Domain | Unique R2 | Shapley R2 | Allocated shared R2 | Share of explained R2 |
| --- | --- | --- | --- | --- | --- |
| Federal turnout | Education, income, and household | 0.018 | 0.141 | 0.124 | 0.385 |
| Federal turnout | Immigration and citizenship | 0.014 | 0.103 | 0.089 | 0.280 |
| Federal turnout | Urban form | 0.021 | 0.042 | 0.020 | 0.113 |
| Federal turnout | Age structure | 0.024 | 0.041 | 0.017 | 0.113 |
| Mean turnout | Education, income, and household | 0.027 | 0.226 | 0.199 | 0.385 |
| Mean turnout | Immigration and citizenship | 0.028 | 0.209 | 0.181 | 0.356 |
| Mean turnout | Age structure | 0.022 | 0.054 | 0.033 | 0.093 |
| Mean turnout | Urban form | 0.021 | 0.034 | 0.013 | 0.058 |
| Municipal turnout | Immigration and citizenship | 0.034 | 0.261 | 0.228 | 0.385 |
| Municipal turnout | Education, income, and household | 0.039 | 0.248 | 0.210 | 0.365 |
| Municipal turnout | Age structure | 0.023 | 0.065 | 0.042 | 0.096 |
| Municipal turnout | Tenure | 0.022 | 0.036 | 0.015 | 0.053 |
| Provincial turnout | Education, income, and household | 0.015 | 0.162 | 0.147 | 0.365 |
| Provincial turnout | Immigration and citizenship | 0.029 | 0.157 | 0.128 | 0.354 |
| Provincial turnout | Urban form | 0.032 | 0.038 | 0.006 | 0.085 |
| Provincial turnout | Age structure | 0.006 | 0.027 | 0.021 | 0.062 |

The largest Shapley domain for each outcome was: Federal turnout: Education, income, and household; Mean turnout: Education, income, and household; Municipal turnout: Immigration and citizenship; Provincial turnout: Education, income, and household.

## Interpretation and analysis

Unique R2 answers whether a domain adds information after every other domain is present. Shapley R2 answers how much of the total explained variation should be attributed to that domain after shared explanatory power is distributed fairly. Education/resources and immigration/citizenship jointly receive Mean turnout 74.1%, Municipal turnout 75.0%, Provincial turnout 71.9%, Federal turnout 66.5% of explained R2. They dominate every outcome, but their unique contributions are much smaller than their Shapley allocations. This directly confirms the bundled interpretation: both domains are important largely because they describe overlapping Toronto social geography.

Municipal turnout is the only outcome led by immigration/citizenship; mean, provincial, and federal turnout are led by education/income/household. Federal turnout gives a noticeably larger relative role to age and urban form, consistent with the earlier level-versus-mean interpretation. Residential stability and transportation have very small unique R2 even when they receive some shared allocation.

## Further analysis

The spatial-bootstrap intervals should govern claims about rank. Domains with overlapping intervals should be described as jointly important rather than strictly ordered. Single-variable domains—tenure, stability, and transportation—are observed blocks, not latent constructs.

## Conclusion

This stage does not eliminate correlated bundles. It makes the bundling explicit by separating unique contribution from shared allocated contribution, allowing the final story to say which domains add distinct information and which describe the same Toronto geography.
