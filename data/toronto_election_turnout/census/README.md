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

## CT Modelling Census Variables

`processed/ct/statcan_2021_ct_census_variables_master.csv` is the CT-level
master Census variable database for Blocks 1-3 and Census-derived Block 5
components. It is built only from official Statistics Canada sources already
stored in `raw/source_downloads/`:

- `statcan_2021_ct_profile.zip`: 2021 Census Profile downloadable CT table.
- `statcan_2021_ct_age_single_year_98100024-eng.zip`: official single-year age
  cube used to construct age bands and school-age population.

The master table preserves official raw counts and rates, then adds derived
0-1 share fields. It retains all 622 CTs from the stored Toronto CT geometry
and includes:

- `ct_id`: preferred CT join key for interpolation and modelling outputs.
- `ctuid` and `dguid`: official Census identifiers preserved for traceability.
- `contains_toronto_da`: whether the CT contains a Toronto DA in the stored
  Census geography.
- `in_interpolation_universe`: whether the CT is one of the 585 CTs used by
  the interpolation outputs.

The matching data dictionary is:

```text
processed/metadata/statcan_2021_ct_census_variables_dictionary.csv
```

QA, missingness, and processing logs are:

```text
processed/audits/profile_extraction/statcan_2021_ct_census_variables_qa_report.md
processed/audits/profile_extraction/statcan_2021_ct_census_variables_missing_report.csv
processed/audits/profile_extraction/statcan_2021_ct_census_variables_processing_log.md
```

Rebuild from the project root with:

```bash
python3 analysis/toronto_election_turnout/census/scripts/build_ct_census_variables.py
```

Important assumptions:

- Shares are reported as 0-1 proportions.
- Official Census percentages, such as unemployment rate and LIM-AT prevalence,
  are preserved as published percent fields with `_pct_official` suffixes.
- Recent immigrants are defined as persons whose period of immigration is
  `2016 to 2021`.
- English/French knowledge share is calculated as everyone except the
  `Neither English nor French` category.
- Racialized population is operationalized using the Census visible minority
  concept.
- School-age population is operationalized as ages 5 to 17.
- Small differences between Census Profile population totals and the
  single-year age cube are expected from published table rounding.

## Reference Files

`reference/ada_2021/` stores the provided ADA profile and boundary files. These
are useful for variable discovery and sensitivity checks, but ADA geography is
coarser than DA.

`reference/zack_taylor_ct2021/` stores the Zack Taylor-provided election dataset
converted from Stata to CSV. It is a census-tract-apportioned election dataset,
not a polling-division source file.
