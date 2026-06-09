# Census and Interpolation Analysis

This folder contains census-specific scripts and methodology notes for
poll-to-census-tract interpolation.

## Structure

```text
census/
  scripts/
  docs/
  viewer/
```

## Scripts

- `scripts/extract_statcan_census_profile_citizens_18plus.py`
  - Extracts characteristic `1525`, `Canadian citizens aged 18 and over`, from
    official Statistics Canada Census Profile bulk CSV downloads.
  - Writes to `data/toronto_election_turnout/census/processed/profile_2021/`.

- `scripts/convert_zack_taylor_stata.py`
  - Converts the Zack Taylor-provided CT-apportioned Stata dataset to CSV.
  - Writes to `data/toronto_election_turnout/census/reference/zack_taylor_ct2021/`.

- `scripts/build_census_geography_viewer_data.py`
  - Builds the Toronto `DA -> CT -> ADA` crosswalk and map-ready GeoJSON.
  - Requires the GDAL `ogr2ogr` command.
  - Writes to `data/toronto_election_turnout/census/processed/geography_2021/`.

- `scripts/audit_suppressed_da_ct_residuals.py`
  - Calculates CT-minus-other-DA residual diagnostics for suppressed DAs.
  - Keeps the official suppressed values null.

- `scripts/extract_statcan_population_18plus.py`
  - Extracts all persons aged 18+ from official single-year-age 100% Census data.

- `scripts/audit_census_adult_population.py`
  - Reconciles adult-population and adult-citizen totals across DA, CT, ADA,
    and Toronto CSD geographies.

- `scripts/audit_adult_suppression_reconciliation.py`
  - Distinguishes suppression of Canadian citizens aged 18+ from suppression
    of all residents aged 18+ at DA and CT levels.

## Docs

- `docs/poll_to_ct_interpolation_readiness.md`: current readiness and unresolved interpolation issues.
- `docs/census_geography_granularity.md`: DA, CT, and ADA spatial granularity and hierarchy audit.
- `docs/suppressed_da_residual_analysis.md`: official-source and CT-residual audit for suppressed DA citizenship values.
- `docs/adult_population_audit.md`: official and reference reconciliation for both adult-population concepts.
- `docs/zack_taylor_ct_comparison.md`: comparison with Zack Taylor's CT-apportioned election data.
- `docs/population_weighted_poll_to_ct_interpolation.pdf`: provided interpolation algorithm note.

## Census Map

From `analysis/toronto_election_turnout/`:

```bash
npm run build:census-map
npm run start:census
```

Open `http://127.0.0.1:5174`.

The viewer reads the map-ready DA, CT, and ADA GeoJSON under
`data/toronto_election_turnout/census/processed/geography_2021/`.
