# Census and Interpolation Data

This folder contains the census-specific data batch for poll-to-census-tract
interpolation.

## Structure

```text
census/
  raw/
    source_downloads/
  processed/
    profile_2021/
    geography_2021/
  reference/
    ada_2021/
    zack_taylor_ct2021/
```

## Raw Geometry

`raw/` stores official Statistics Canada 2021 geography files:

- Toronto CSD boundary.
- Toronto CT boundaries.
- Toronto DA boundaries.

The `raw/source_downloads/` folder keeps the raw StatCan REST GeoJSON pulls used
to build those GeoPackages.

## Processed Census Profile

`processed/profile_2021/` stores Toronto-only Census Profile extracts. The
current extracted variable is characteristic `1525`, `Canadian citizens aged 18
and over`, at DA and CT levels.

The DA table is the preferred ancillary population-weight input for
poll-to-CT interpolation.

`processed/geography_2021/` stores map-ready DA, CT, and ADA GeoJSON files plus
the verified `DA -> CT -> ADA` crosswalk.

## Reference Files

`reference/ada_2021/` stores the provided ADA profile and boundary files. These
are useful for variable discovery and sensitivity checks, but ADA geography is
coarser than DA.

`reference/zack_taylor_ct2021/` stores the Zack Taylor-provided election dataset
converted from Stata to CSV. It is a census-tract-apportioned election dataset,
not a polling-division source file.
