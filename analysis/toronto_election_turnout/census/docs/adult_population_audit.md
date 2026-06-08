# Adult Population Audit

## Variable Distinction

The repository keeps two different measures separate:

- `population_18plus`: all persons aged 18 years and over. It comes from
  Statistics Canada table `98-10-0023-01`, uses 100% Census data, and includes
  institutional residents. It is calculated from `Total - Age`, the published
  `0 to 14 years` aggregate, and ages 15, 16, and 17.
- `citizen_canadian_18over`: Canadian citizens aged 18 years and over. It is
  characteristic `1525` in the 25% sample Census Profile and is the preferred
  weighting concept in the supplied election-interpolation method.

The second measure is not total adult population. The first is not a count of
citizens or eligible electors.

Nine Toronto DAs are marked `x` in the official 100% age table and remain null.
They are not interpreted as zero. This is distinct from the 16 DAs whose
25% Census Profile value for Canadian citizens aged 18+ is suppressed.

The seven DAs suppressed only for the citizenship measure have these official
all-resident age-table values:

| DA | All residents aged 18+ |
| --- | ---: |
| 35200545 | 225 |
| 35201461 | 120 |
| 35203185 | 0 |
| 35203717 | 55 |
| 35204479 | 45 |
| 35204599 | 285 |
| 35204701 | 145 |

These values do not fill the citizenship field because the two variables have
different universes.

For all persons aged 18+:

| Geography/source | Toronto total | Difference |
| --- | ---: | ---: |
| Official Toronto CSD | 2,331,130 | 0 |
| Sum of 3,743 DA records | 2,331,690 | +560 |

The DA sum is 0.024% above the official city value. This small difference is
consistent with independent random rounding across the five published cells
used for each DA calculation, even though nine DA rows remain suppressed.

## Canadian Citizens Aged 18+

| Geography/source | Toronto total | Difference from official CSD |
| --- | ---: | ---: |
| Official Toronto CSD profile | 1,870,055 | 0 |
| Sum of 3,743 DA records | 1,869,930 | -125 |
| Sum of 585 Toronto-linked CT records | 1,870,085 | +30 |
| Sum of 279 ADA reference records | 1,870,025 | -30 |

The DA difference is 0.0067% below the official Toronto total. It is consistent
with 16 confidentiality-suppressed DA values plus independent random rounding.
The CT and ADA totals are each within 30 people of the official city value.

The sum of all 622 stored clipped CT features is not a Toronto total. Some CTs
intersect the Toronto boundary but do not contain a Toronto DA. Only the 585 CT
identifiers in the DA-to-CT crosswalk form the comparable Toronto universe.

Within those 585 CTs, all-resident population aged 18+ is published for every
CT. Canadian citizens aged 18+ is suppressed for two CTs: `5350006.00` and
`5350205.00`. Their values remain null.

## ADA Reference Check

The ADA reference profile contains the same characteristic:

- 279 of 279 ADAs have a published value.
- 77 DA sums equal their official ADA value.
- 196 are within 5 people.
- 252 are within 10 people.
- Mean absolute difference: 5.79 people.
- Maximum absolute difference: 30 people.

These differences are consistent with independent random rounding. An ADA
total cannot be used as an exact replacement for a suppressed component DA.

## Zack Taylor Reference

The Zack Taylor CT file contains election-derived eligible-voter variables and
historical city population fields. It does not contain a 2021 Census variable
equivalent to Canadian citizens aged 18+, so it is not a valid reference for
this reconciliation. The ADA reference has broad age-distribution variables,
but not the single-year detail needed to calculate all persons aged 18+
exactly.

## Sources

- Toronto Census Profile:
  https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?DGUIDlist=2021A00053520005&GENDERlist=1&HEADERlist=0&Lang=E&STATISTIClist=1
- Single-year age table `98-10-0023-01`:
  https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810002301
- CT single-year age table `98-10-0024-01`:
  https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810002401
- Random rounding:
  https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/dt-td/about.cfm
