# Suppressed DA Citizenship Counts

## Question

Sixteen Toronto dissemination areas (DAs) have no published value for
`Canadian citizens aged 18 and over`. This audit checks whether another
official Statistics Canada product publishes the values or whether a value can
be recovered by subtracting the other DAs from the containing census tract
(CT).

## Official-Source Search

The exact characteristic is available in the 2021 Census Profile, including at
the DA level. The 16 affected rows are not missing because of a failed
download, join, or map operation. Their fourth data-quality-flag digit is `9`,
which Statistics Canada defines as long-form data suppressed to meet the
confidentiality requirements of the Statistics Act.

The complete citizenship block is suppressed for these DAs, including:

- the citizenship universe;
- Canadian citizens;
- Canadian citizens aged under 18;
- Canadian citizens aged 18 and over;
- people who are not Canadian citizens; and
- the men+ and women+ components.

No alternate official public product was found that releases the suppressed
DA-level values. The Census Profile and Census Program Data Viewer expose the
same disseminated census data. Citizenship highlight tables and special
profiles do not provide an unsuppressed DA substitute, and public-use
microdata do not identify respondents at DA geography.

Official sources:

- Census Profile catalogue and geography coverage:
  https://www150.statcan.gc.ca/n1/en/catalogue/98-401-X2021006
- Census Profile methodology:
  https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/about-apropos/about-apropos.cfm?Lang=e
- Census Program Data Viewer methodology:
  https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/dv-vd/cpdv-vdpr/about-apropos-eng.cfm
- 2021 Census guide on confidentiality and suppression:
  https://www12.statcan.gc.ca/census-recensement/2021/ref/98-304/98-304-x2021001-eng.pdf

## CT Residual Test

For each suppressed DA, the audit calculates:

```text
published CT value - sum of published values for the other DAs in that CT
```

All 16 affected CT groups contain exactly one suppressed Toronto DA. However:

- 2 parent CT values are also suppressed, so no residual is available;
- 6 residuals are positive;
- 2 residuals are zero; and
- 6 residuals are negative.

A negative population count is impossible. It occurs here because Statistics
Canada independently randomly rounds values, totals, and subtotals to
multiples of 5 or 10. Statistics Canada explicitly warns that independently
rounded geographic totals may not equal the sum of their components.

Official random-rounding explanation:

https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/dt-td/about.cfm

## Decision

The official DA values remain null. The residuals are retained only as
diagnostics in:

`data/toronto_election_turnout/census/processed/geography_2021/statcan_2021_toronto_da_ct_residual_diagnostics.csv`

They must not be interpreted as official values, used to overwrite the
suppressed cells, or used as exact interpolation weights. A later modelling
stage may define an explicit imputation method, but modeled values must be kept
in separate columns with uncertainty and provenance.

The 100% age profile is not an exact substitute. It can describe the adult-age
population, but it cannot identify which adults are Canadian citizens. Mixing
it into the citizenship field would change the variable's meaning.
