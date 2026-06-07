# Processed 2021 Census Profile Tables

This folder stores Toronto-only extracted Census Profile attributes used for
poll-to-census-tract interpolation.

## Files

- `statcan_2021_da_citizens_18plus.csv`
  - Dissemination area table.
  - 3,743 Toronto DA rows.
  - Characteristic `1525`: `Canadian citizens aged 18 and over`.
  - Total count: 1,869,930.
  - Missing/suppressed rows: 16.
  - All 16 blanks have a long-form quality flag of `9`, meaning Statistics
    Canada suppressed the values for confidentiality.

- `statcan_2021_ct_citizens_18plus.csv`
  - Census tract table.
  - 622 CT rows intersecting the Toronto clipping boundary.
  - Characteristic `1525`: `Canadian citizens aged 18 and over`.
  - The all-row total of 1,999,260 is not a Toronto city total.
  - The 585 CTs linked to verified Toronto DAs sum to 1,870,085.
  - Missing/suppressed rows: 2.

- `statcan_2021_citizens_18plus_extraction_metadata.json`
  - Source URLs, extraction timestamp, row counts, totals, and data notes.

- `statcan_2021_da_population_18plus.csv`
  - One row per Toronto DA.
  - All persons aged 18 years and over from 100% Census single-year-age data.
  - Distinct from Canadian citizens aged 18 and over.

- `statcan_2021_population_18plus_extraction_metadata.json`
  - Reconciles the DA sum with the independently published Toronto CSD value.

- `statcan_2021_adult_population_audit.json`
  - Summary reconciliation across DA, Toronto-linked CT, ADA, and CSD.

- `statcan_2021_ada_citizens_18plus_reconciliation.csv`
  - ADA-by-ADA comparison of component DA sums with the official ADA profile.

## Source and Reproducibility

The files were extracted from official Statistics Canada 2021 Census Profile
comprehensive CSV downloads with confidence intervals. The large source zips
are not stored in Git.

Rebuild with:

```bash
python3 analysis/toronto_election_turnout/census/scripts/extract_statcan_census_profile_citizens_18plus.py
```

The script expects the official source zips in `/private/tmp`:

- `/private/tmp/statcan_da_ontario_ci.zip`
- `/private/tmp/statcan_ct_ci.zip`

The DA table should be used as the primary ancillary population-weight input.
Its total closely matches the official Toronto CSD row in the same Census
Profile source. For a Toronto-wide CT comparison, use only the 585 CT
identifiers linked to Toronto DAs in the crosswalk. Summing all 622 clipped CT
features includes boundary-intersecting CTs outside the comparable Toronto DA
universe and is not a valid city total.

## Suppressed DA Values

`Canadian citizens aged 18 and over` is a 25% long-form Census Profile
estimate, not the basic short-form population count. For 16 Toronto DAs,
Statistics Canada suppresses the full citizenship block for confidentiality
under the Statistics Act.

The total, men+, women+, Canadian-citizen parent, and under-18 component values
are all unavailable. An exact 18+ citizen count therefore cannot be recovered
by subtraction. These rows are labelled `suppressed_confidentiality` in
`value_status` and remain null.
