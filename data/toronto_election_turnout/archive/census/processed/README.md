# Processed 2021 Census Data

Processed outputs are organized by geography so each area's geometry and
profile attributes live together.

```text
processed/
  da/
    statcan_2021_toronto_da.geojson
    statcan_2021_da_profile.csv
    intermediate/
  ct/
    statcan_2021_toronto_ct.geojson
    statcan_2021_ct_profile.csv
    statcan_2021_ct_census_variables_master.csv
    intermediate/
  ada/
    statcan_2021_toronto_ada.geojson
    statcan_2021_ada_profile.csv
  crosswalks/
  metadata/
  audits/
    geography/
    profile_extraction/
    reconciliation/
  variable_dictionary.csv
```

## Geography Folders

Each geography folder contains:

- A map-ready GeoJSON in EPSG:4326.
- A canonical wide profile CSV with one row per geography.

The DA and CT `intermediate/` folders retain the original narrow variable
extracts used to build the wide profiles. They are reproducibility inputs, not
the default analytical tables.

Current profile variables include:

- `citizen_canadian_18over`: Canadian citizens aged 18+, from the 25% Census
  Profile sample. This is the production interpolation weight.
- `population_18plus`: all residents aged 18+, calculated from 100% Census age
  tables and retained for diagnostics and sensitivity analysis.

The wide profiles preserve variable-specific status, confidence interval,
quality, and source fields. `variable_dictionary.csv` records definitions and
source universes.

## Crosswalks

`crosswalks/statcan_2021_toronto_da_ct_ada_crosswalk.csv` contains one row per
Toronto DA with `da_id`, `ct_id`, and `ada_id`.

The verified hierarchy is:

```text
DA -> CT -> ADA
```

## Audits

- `audits/geography/`: feature counts, CRS details, target-universe counts,
  hierarchy statistics, and suppressed-DA geography links.
- `audits/profile_extraction/`: source URLs, extraction counts, totals, and
  missing-value metadata.
- `audits/reconciliation/`: DA/CT/ADA and Toronto total comparisons,
  suppression comparisons, and CT residual diagnostics.

Suppressed values remain null in canonical profiles. Residual diagnostics do
not replace official values.

## CT Census Variable Master

`ct/statcan_2021_ct_census_variables_master.csv` is the research-ready
CT-level Census variable database for turnout modelling. It contains Blocks 1-3
and Census-derived Block 5 variables, preserving raw counts and official rates
alongside derived 0-1 shares.

Its dictionary is stored at:

```text
metadata/statcan_2021_ct_census_variables_dictionary.csv
```

Its QA, missingness, and processing logs are stored under
`audits/profile_extraction/`.

## Counts

- DA: 3,743 rows/features.
- CT: 622 stored clipped features, including 585 CTs linked to Toronto DAs.
- ADA: 279 rows/features.
- DA-CT-ADA crosswalk: 3,743 rows.

## Rebuild

From `analysis/toronto_election_turnout/`:

```bash
npm run build:census-map
```

This builds wide profiles, geography and crosswalk outputs, then rebuilds the
ADA profile after the crosswalk is available.

Build the CT Census variable master from the project root with:

```bash
python3 analysis/toronto_election_turnout/census/scripts/build_ct_census_variables.py
```
