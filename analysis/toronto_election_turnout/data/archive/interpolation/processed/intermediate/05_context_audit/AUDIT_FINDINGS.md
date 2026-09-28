# Interpolation Audit Findings

## No-Geometry Allocation

Every vote-bearing no-geometry record was allocated through a
district-to-CT crosswalk weighted by DA `citizen_canadian_18over`:

| Election | Records | Source votes | Allocated votes | Failures |
| --- | ---: | ---: | ---: | ---: |
| Municipal 2023 | 100 | 160,371 | 160,371 | 0 |
| Provincial 2025 | 144 | 199,979 | 199,979 | 0 |
| Federal 2025 | 414 | 549,076 | 549,076 | 0 |

The remaining 382 federal no-geometry records have missing votes because their
votes are reported in another division. They are retained in the exclusion
audit and are not treated as zero-vote allocations.

## Preservation

All total-vote, party-vote, and candidate-vote checks pass globally, by
district, and by source poll/reporting row. There are no vote-bearing excluded
records.

## Census Citizen-Adult Participation

| Election | Matching-area official rate | Citizen 18+ rate | Broader/secondary context |
| --- | ---: | ---: | ---: |
| Municipal 2023 | 37.00% official rounded | 38.75% | 38.50% secondary reported rate |
| Provincial 2025 | 42.60% selected Toronto ridings | 47.64% | 45.22% Ontario official |
| Federal 2025 | 65.01% selected Toronto ridings | 70.51% | 69.10% Ontario official; 69.00% Canada final |

The municipal citizen-adult rate is within 0.25 percentage points of the
secondary 38.5% report. The federal citizen-adult rate is 1.41 percentage
points above Ontario's official federal turnout and 1.51 points above the
final national rate. The provincial citizen-adult rate is 2.42 points above
Ontario's official provincial turnout.

These close-margin comparisons are recorded as context, not direct validation:
Ontario and Canada rates cover broader geographies, and the municipal 38.5%
figure is secondary rather than the City's final rounded report. The direct
matching-geography checks remain the official elector rates for Toronto or the
selected Toronto ridings.

The Census variable is a useful eligibility proxy but is not the election-
specific registered-elector denominator. Two CT citizen-adult values are
suppressed; their CT participation rates remain null. Suppression can lower the
available denominator slightly, but should not be assumed to explain the full
difference.

## Official Result Reconciliation

The audit rebuilt official party and candidate totals independently from the
source files:

- 741 party comparisons passed globally and by ward/riding.
- 3,190 candidate comparisons passed globally and by ward/riding.
- All normalized party totals match the interpolated totals.
- Zero reconciliation failures were found.

## Map Decision

The vote-preservation, no-geometry allocation, vote-bearing exclusion, and
official-result reconciliation gates pass. Turnout-reference geography is now
treated as an interpretation flag rather than a vote-integrity failure.
Leaflet map generation is authorized from the validated CT result datasets.
