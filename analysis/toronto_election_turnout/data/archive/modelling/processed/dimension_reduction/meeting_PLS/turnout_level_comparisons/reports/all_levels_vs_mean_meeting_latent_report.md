# Meeting-Variable Turnout-Level Comparison: Executive Summary

This report gives a quick narrative comparison of separately supervised municipal, provincial, and federal meeting-variable PLS models with mean turnout. Detailed loadings, VIP tables, component matching, and robustness grids remain in the three level-specific reports. Mean turnout includes all three election outcomes, so similarities are partly expected and the comparisons are descriptive rather than independent difference tests.

## Municipal turnout

### Interpretation

Municipal turnout is the most strongly structured of the three levels by the meeting variables. Its three-component PLS reaches CV R2 `0.629`, compared with `0.534` for mean turnout. The primary municipal construction contrasts higher education and citizen attachment with visible-minority, immigrant, larger-household, and lower-income geography. Visible-minority share, immigrant share, bachelor-level education, citizen-adult share, and household size carry the highest VIP values.

### Similarity with mean turnout

The first municipal and mean components are strongly aligned: their loading cosine is `0.881`. Both express essentially the same central social-geographic turnout gradient, and both are reproduced closely by supervised PCA and elastic net. This indicates that the main municipal story is not an artifact of one estimator or of averaging election levels.

### Difference from mean turnout

Municipal turnout gives more importance than the mean model to low-income share, citizen-adult share, renter share, and the young-adult share. Average household size, the age-65-plus share, no-car households, and five-year residential stability contribute less relative importance. The municipal model is also markedly more predictive, with robustness CV R2 values around `0.626–0.639`, suggesting a sharper social gradient than the average outcome.

### Discussion

The municipal pattern is therefore best read as a more socially selective version of the shared turnout geography. Citizenship eligibility, income, tenure, and younger-adult context sharpen the separation between high- and low-participation CTs. This supports a story about unequal municipal incorporation, while remaining an ecological association rather than evidence about individual voters.

## Provincial turnout

### Interpretation

Provincial turnout retains the same main demographic axis but is less predictable: its three-component PLS has CV R2 `0.371`. Visible-minority share, immigrant share, household size, bachelor-level education, and citizen-adult share remain the leading variables. Its secondary construction gives more space to urban form, stability, density, and transportation context.

### Similarity with mean turnout

The provincial primary component is the closest match to the mean model of any election level, with loading cosine `0.983`. The high- and low-side variable bundles are nearly the same, showing that provincial turnout closely represents the central construction captured by the three-election average.

### Difference from mean turnout

Apartment share, population density, no-car household share, and five-year residential stability become more important provincially. Bachelor-level education, both age shares, and low-income share become somewhat less important. PLS, supervised PCA, and elastic net all produce CV R2 near `0.36–0.38`, so the weaker fit is consistent across estimators.

### Discussion

Provincial turnout looks like the clearest middle case: it shares the mean model's central social divide almost exactly, but supplements it with an urban-form and mobility layer. The similarity of the component construction combined with lower predictive power suggests the same geography is present, but it organizes provincial participation less tightly than municipal participation.

## Federal turnout

### Interpretation

Federal turnout is the least predictable from the meeting variables. Its three-component PLS has CV R2 `0.317`. Household size and bachelor-level education lead the VIP ranking, followed by visible-minority and immigrant shares; condo, apartment, residential-stability, and density variables are much more prominent than in the mean model.

### Similarity with mean turnout

The federal primary component still has a strong loading cosine of `0.842` with the mean primary component. Education/resources versus immigrant/racialized household geography therefore remains recognizable. PCA and elastic net again return almost the same predictive performance as PLS, supporting the existence of a stable but weaker common signal.

### Difference from mean turnout

Federal turnout shifts strongly toward housing form: condo share, apartment share, five-year residential stability, and density show the largest positive VIP changes. Immigrant share, citizen-adult share, visible-minority share, and low-income share become less important than in mean turnout. Its robustness CV R2 values remain only about `0.317–0.327`.

### Discussion

The federal result suggests broader mobilization across social groups, leaving less of the sharply selective pattern seen municipally. Where federal turnout still varies, stable residential and built-form differences become relatively more informative. This does not mean immigration or racialized geography disappears; rather, those variables dominate less once federal participation is considered by itself.

## Overall similarities and differences

All three election levels share one central construction: education and resource attachment on one side, and immigrant/racialized, larger-household geography on the other. This common axis is strongest for municipal turnout, almost identical in construction for provincial turnout, and still visible but weaker for federal turnout. Agreement among PLS, supervised PCA, and elastic net supports treating it as a recurring feature of the data rather than a PLS-specific artifact.

The main difference is emphasis. Municipal turnout accentuates citizenship, income, tenure, and young-adult inequality; provincial turnout most closely follows the mean while adding urban form and transportation; federal turnout places greater relative weight on housing form, density, and residential stability. In short, the same underlying Toronto social geography is present at every level, but it is most consequential municipally and least determinative federally.

These comparisons summarize associations among CT characteristics. They do not identify individual behavior, causal mechanisms, or statistically independent differences from the mean outcome.
