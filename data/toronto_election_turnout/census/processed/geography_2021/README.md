# Toronto 2021 Census Geography

This folder contains map-ready Toronto census geography and a spatial
correspondence table.

## Files

- `statcan_2021_toronto_da.geojson`
  - 3,743 Toronto dissemination areas.
  - Includes DA, CT, and ADA identifiers plus Canadian citizens aged 18+.

- `statcan_2021_toronto_ct.geojson`
  - 622 stored Toronto-clipped census tract features.
  - Includes the direct CT Census Profile value for Canadian citizens aged 18+.
  - Only 585 CTs contain a verified Toronto DA. The other 37 boundary-only
    features retain the source profile value in
    `profile_citizen_canadian_18over`, while the mapped analysis value is null
    so they cannot inflate Toronto totals.

- `statcan_2021_toronto_ada.geojson`
  - 279 aggregate dissemination areas.
  - Includes the official ADA profile value and a separately summed DA value.

- `statcan_2021_toronto_da_ct_ada_crosswalk.csv`
  - One row per Toronto DA.
  - Columns: `da_id`, `ct_id`, and `ada_id`.

- `statcan_2021_toronto_da_suppressed_values.csv`
  - Audit table for the 16 DAs whose long-form citizenship values were
    suppressed for confidentiality.

- `statcan_2021_toronto_da_ct_residual_diagnostics.csv`
  - CT-minus-other-DA calculations for the 16 suppressed DAs.
  - Diagnostic only: independent random rounding makes these residuals
    unsuitable as exact replacements for the official null values.

- `statcan_2021_toronto_geography_audit.json`
  - Feature counts, CRS details, and DA-per-ADA summary statistics.

## Geography Hierarchy

Within census metropolitan areas containing census tracts, Statistics Canada
constructs ADAs by grouping CTs. DAs respect CT boundaries, so the Toronto
relationship is:

```text
DA -> CT -> ADA
```

The crosswalk assigns each DA using an interior point. All 3,743 Toronto DA
profile identifiers receive exactly one CT and one ADA.

The CT geometry file has 622 Toronto-clipped features, while 585 CT identifiers
contain the interior point of at least one Toronto DA in the crosswalk. The
remaining clipped CT features are retained for transparency; they should not be
treated as additional containers of Toronto DAs.

## Granularity

| Geography | Features | Median land area |
| --- | ---: | ---: |
| DA | 3,743 | 0.095 km² |
| CT | 622 | 0.788 km² |
| ADA | 279 | 1.792 km² |

The average ADA contains 13.4 Toronto DAs. The observed range is 1 to 46.

## Count Reconciliation

Summed DA-level Canadian citizens aged 18+:

`1,869,930`

Official ADA-profile total:

`1,870,025`

The 95-person difference is not adjusted. Small-area Census Profile values are
rounded and can also be suppressed, so summing independently published DA
estimates does not always equal the independently published ADA estimate.

## Suppressed DA Residuals

No alternate official public source was found for the 16 suppressed DA values.
Subtracting the other published DAs from the parent CT produces 6 positive, 2
zero, and 6 negative residuals; 2 parent CT values are also suppressed.
Negative results demonstrate that independently rounded CT and DA values are
not exactly additive. The residual audit is therefore kept separate and does
not fill the official nulls.
