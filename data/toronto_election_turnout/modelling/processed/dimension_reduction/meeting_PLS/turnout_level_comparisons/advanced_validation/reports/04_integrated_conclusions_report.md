# Step 4 Report: Integrated Advanced Validation Conclusions

## What has been done

This synthesis combines three distinct questions: spatial nested CV tests geographic generalization; spatial-block bootstrap tests stability of the PLS latent construction; and domain commonality/Shapley analysis separates unique from shared domain importance.

## Integrated results

| Outcome | Spatial PLS R2 | Primary loading sign stability | Leading Shapley domain | Leading domain share |
| --- | --- | --- | --- | --- |
| Mean turnout | 0.480 | 0.429 | Education, income, and household | 0.385 |
| Municipal turnout | 0.533 | 0.714 | Immigration and citizenship | 0.385 |
| Provincial turnout | 0.332 | 0.500 | Education, income, and household | 0.365 |
| Federal turnout | 0.263 | 0.643 | Education, income, and household | 0.385 |

## Interpretation

Municipal turnout remains the clearest result: it has the strongest spatial prediction, a stable primary construction, and is the only outcome whose leading Shapley domain is immigration/citizenship. Provincial turnout retains the same central construction but generalizes less strongly. Federal turnout has the weakest spatial prediction and shifts relatively toward age and urban form. Mean turnout falls between these cases.

Across outcomes, education/resources and immigration/citizenship explain most of the modelled variation, but much of that contribution is shared. The correct story is therefore not that one domain independently determines turnout. It is that overlapping class, education, household, citizenship, and racialized geographies form the main turnout structure, with election-level differences in how strongly that structure predicts participation.

Predictive performance, latent stability, and domain attribution should not be collapsed into one statistic. A model can have modest spatial prediction but a stable descriptive component. A domain can be highly important by Shapley allocation while contributing little uniquely because it overlaps with other domains.

## Further analysis

Map the stored outer-fold residuals and inspect the bootstrap interval tables before publication. If strict inference is required, add repeated alternative spatial partitions and report sensitivity to block definition. Causal language remains inappropriate for these cross-sectional ecological CT associations.

## Conclusion

The advanced workflow replaces a single bundled PLS reading with three layers of evidence: where prediction travels, which latent features survive geography, and how the seven prespecified domains divide unique and shared explanatory power.
