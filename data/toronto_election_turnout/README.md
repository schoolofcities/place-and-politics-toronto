# Toronto Election Turnout Data

This folder is split into three data batches:

- `elections/`: municipal, provincial, and federal election source files and processed polling-division turnout outputs.
- `census/`: 2021 census geography, Census Profile attributes, and census-tract reference/interpolation inputs.
- `interpolation/`: generated poll/district-to-census-tract crosswalks,
  estimates, audits, exclusions, and validation reports.

This separation is intentional. Election files describe votes, electors, polling
divisions, wards, and ridings. Census files describe DAs, CTs, CSD geography,
and population-like denominators used for later poll-to-CT interpolation.

## Folder Map

```text
data/toronto_election_turnout/
  elections/
    raw/
    processed/
      municipal_2023_mayor/
      provincial_2025/
      federal_2025/
      metadata/
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
  interpolation/
    processed/
      intermediate/
    map/
```

## Election Data

`elections/raw/` stores official or source election files used to build the
polling-division turnout datasets:

- City of Toronto 2023 mayoral by-election workbooks and subdivision geometry.
- Elections Ontario 2025 Official Return CSV.
- Elections Canada 2025 poll-by-poll files and election-atlas geometry downloads.

`elections/processed/` is grouped by election. Each election folder contains
`turnout/` for the GIS-ready poll summaries and `candidate_details/` for the
candidate catalog and sparse poll-candidate vote bridge. Shared QA and schema
metadata is stored in `elections/processed/metadata/`.

The processed election rows preserve official missingness. Counts are not
estimated or assigned to polygons unless a source supports that relationship.
See `analysis/toronto_election_turnout/elections/docs/` for election QA notes.

## Census Data

`census/raw/` stores official Statistics Canada 2021 geometry:

- Toronto CSD.
- Toronto CTs.
- Toronto DAs.
- Raw StatCan REST GeoJSON source downloads used to build those files.
- Official single-year-age and annual population estimate tables used for
  adult-population and temporal diagnostics.

`census/processed/` is grouped by geography. The `da/`, `ct/`, and `ada/`
folders each keep geometry and a canonical wide profile table together.
Current profile variables include
`citizen_canadian_18over` and `population_18plus`; future profile variables can
be added as columns without creating another set of geography files.

`census/reference/ada_2021/` stores the ADA files provided for variable
discovery and lower-resolution checks.

`census/reference/zack_taylor_ct2021/` stores the Zack Taylor-provided
census-tract election dataset converted from Stata to CSV, plus schema and
metadata sidecars.

See `analysis/toronto_election_turnout/census/docs/` for interpolation notes,
the Zack Taylor comparison, and the source PDF.

## Interpolation Data

`interpolation/processed/` stores final CT-level result and candidate tables.
Its `intermediate/` subfolder stores crosswalks, exclusions, audits,
validation reports, and summaries. The default workflow uses DA-level
`citizen_canadian_18over` as the population weight, treats suppressed DA
values as zero, and writes separate poll-to-CT and district-to-CT crosswalks.

`interpolation/map/` stores the three validated, compact CT GeoJSON datasets
used by the interpolation viewer plus `map_build_summary.json`.
