# Census and Interpolation Data

This folder contains the census-specific data batch for poll-to-census-tract
interpolation.

## Structure

```text
census/
  raw/
    source_downloads/
  processed/
    da/
    ct/
    ada/
    crosswalks/
    audits/
  reference/
    ada_2021/
    zack_taylor_ct2021/
```

## Raw Geometry

`raw/` stores official Statistics Canada 2021 geography files:

- Toronto CSD boundary.
- Toronto CT boundaries.
- Toronto DA boundaries.

The `raw/source_downloads/` folder keeps the raw StatCan REST GeoJSON pulls,
official single-year-age tables, and annual population-estimate tables used by
the census and temporal diagnostic scripts.

## Processed Census Profile

`processed/da/`, `processed/ct/`, and `processed/ada/` each store the
geography's map-ready geometry and canonical wide profile table together. The
current variables are
`citizen_canadian_18over` and `population_18plus`, with variable-specific
while reproducible DA and CT narrow source extracts remain in each geography's
`intermediate/` folder.

The DA profile table's `citizen_canadian_18over` field is the production
ancillary weight for poll-to-CT interpolation. `population_18plus` is retained
for sensitivity and suppression diagnostics.

`processed/crosswalks/` stores the verified `DA -> CT -> ADA` crosswalk.
`processed/audits/` separates geography, profile-extraction, and
reconciliation diagnostics by purpose.

## Reference Files

`reference/ada_2021/` stores the provided ADA profile and boundary files. These
are useful for variable discovery and sensitivity checks, but ADA geography is
coarser than DA.

`reference/zack_taylor_ct2021/` stores the Zack Taylor-provided election dataset
converted from Stata to CSV. It is a census-tract-apportioned election dataset,
not a polling-division source file.
