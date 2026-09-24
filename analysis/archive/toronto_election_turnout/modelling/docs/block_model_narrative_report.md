# CT Turnout Models: Narrative Report

This report summarizes the first blockwise modelling pass for Toronto CT-level turnout.
The models use the clean curated CT dataset and include only Blocks 1-4 because Blocks
5-6 still require additional official service/campaign data.

The dependent variables are municipal, provincial, federal, federal-minus-municipal,
and mean participation. All turnout outcomes use the Census citizen-adult denominator
rather than registered-elector denominators.

## Figure 1. Model Fit

![Adjusted R2 heatmap](../../../../data/toronto_election_turnout/modelling/processed/models/figures/adjusted_r2_heatmap.svg)

Adjusted R2 by outcome and block:

| Outcome | Block 1 demographics | Block 2 housing | Block 3 immigration | Block 4 competitiveness |
|---|---:|---:|---:|---:|
| Municipal turnout | 0.604 | 0.216 | 0.549 | 0.390 |
| Provincial turnout | 0.386 | 0.163 | 0.314 | 0.246 |
| Federal turnout | 0.349 | 0.118 | 0.230 | 0.133 |
| Federal - municipal gap | 0.145 | 0.197 | 0.270 | 0.110 |
| Mean turnout | 0.551 | 0.180 | 0.428 | 0.315 |

The first result is hard to miss: demographic composition is the strongest block for
municipal, provincial, federal, and mean turnout. This is especially pronounced for
municipal turnout, where Block 1 reaches an adjusted R2 of 0.604. Mean turnout is
similar, with Block 1 at 0.551. Housing is consistently the weakest of the four blocks
for direct turnout levels.

## Figure 2. Best Block By Outcome

![Best block bars](../../../../data/toronto_election_turnout/modelling/processed/models/figures/best_block_adjusted_r2.svg)

The federal-minus-municipal gap is the exception. Its best block is not demographics;
it is Block 3, immigration/citizenship/eligibility, with adjusted R2 of 0.270. That
suggests that the geography of municipal drop-off is not simply about high-turnout
versus low-turnout places. It appears tied to places where federal participation
remains comparatively high while municipal participation falls away.

## Figure 3. Mean Turnout Predictors

![Mean turnout top predictors](../../../../data/toronto_election_turnout/modelling/processed/models/figures/mean_turnout_top_predictors.svg)

Across the mean-turnout models, the most consistent negative predictors are larger
household size, young-adult share, visible-minority share, non-citizen share, and
mayoral electoral fragmentation. Bachelor-plus share is the clearest positive
demographic predictor.

Top predictors for mean turnout:

| Block | Predictor | Std. beta | Direction |
|---|---|---:|---|
| Block 1: Demographics | `dem_average_household_size` | -0.646 | lower turnout |
| Block 1: Demographics | `dem_share_18_34` | -0.566 | lower turnout |
| Block 1: Demographics | `dem_median_age` | -0.323 | lower turnout |
| Block 2: Housing/stability | `housing_renter_share` | -10.664 | lower turnout |
| Block 2: Housing/stability | `housing_owner_share` | -9.734 | lower turnout |
| Block 2: Housing/stability | `housing_apartment_share` | 1.163 | higher turnout |
| Block 3: Immigration/eligibility | `racialized_visible_minority_share` | -0.609 | lower turnout |
| Block 3: Immigration/eligibility | `immigration_non_citizen_share` | -0.356 | lower turnout |
| Block 3: Immigration/eligibility | `immigration_recent_immigrant_share` | 0.228 | higher turnout |
| Block 4: Competitiveness | `election_effective_mayoral_candidates_5pct` | -0.721 | lower turnout |
| Block 4: Competitiveness | `election_mayoral_top_two_margin` | -0.232 | lower turnout |
| Block 4: Competitiveness | `election_effective_federal_parties_5pct` | -0.065 | lower turnout |

## What Stands Out

### 1. Municipal turnout is the most socially structured outcome

Municipal turnout is explained unusually well by basic demographic and immigration
variables. Block 1 adjusted R2 is 0.604 and Block 3 adjusted R2 is 0.549. In practical
terms, this means the municipal electorate varies sharply across CT social geography.
Places with higher young-adult share, larger household size, lower income, lower
bachelor-plus share, and higher racialized/immigrant shares tend to have lower municipal
participation.

### 2. Federal turnout is higher, but less tightly explained

Federal participation is much higher on average, but the block fits are weaker. Block 1
still leads with adjusted R2 of 0.349, but that is far below the municipal model. This
supports a narrative where federal elections activate more people across the city, but
do not erase the underlying turnout gradient.

### 3. The municipal drop-off story is about immigration/citizenship geography

For federal-minus-municipal participation, Block 3 is strongest. The top terms include
non-citizen share, recent immigrant share, citizen-adult share, immigrant share, and
English/French knowledge. This is promising because it points toward a sharper research
question: which communities participate federally but are not being mobilized municipally?

### 4. Competitiveness is meaningful but should be handled carefully

Block 4 performs well for municipal and mean turnout. The effective number of mayoral
candidates above 5% is strongly negative across several outcomes. This probably means
that fragmented mayoral vote geographies overlap with lower-turnout social geography.
It is interesting, but not yet causal: competitiveness is computed from the same vote
data we are trying to explain.

### 5. Housing variables need a reduced specification

The housing block has the weakest overall fit and shows signs of collinearity. Renter
share and owner share are mechanically related, and apartment/condo/density are also
tightly coupled. The next modelling pass should reduce this block to a smaller set,
such as renter share, condo share, apartment share, same-address-five-years share, and
density.

## Suggested Next Story

The strongest narrative is: **Toronto municipal turnout is not just lower than federal
turnout; it is more socially selective.** The places most likely to disappear municipally
are not random low-turnout places. They appear to be structured by age, household form,
education, racialized/immigrant geography, and citizenship-related context.

A strong next model would be a combined reduced model for mean turnout and municipal
drop-off, using a small non-collinear set of predictors from Blocks 1-4, then adding
Block 5 service-contact variables once we finish the Open Toronto data build.

## Caveats

- This is exploratory OLS, not a final causal model.
- P-values are normal approximations from the local pure-Python implementation.
- Spatial autocorrelation and robust standard errors are not yet included.
- Several predictors are compositionally related, so multicollinearity needs to be checked.
- Turnout uses Census citizen-adult denominators, not official registered-elector denominators.
