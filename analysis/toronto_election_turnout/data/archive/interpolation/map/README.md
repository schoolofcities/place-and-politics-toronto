# Interpolation Map Data

This folder contains compact census-tract GeoJSON built for the interpolation
Leaflet viewer:

- `municipal_2023_mayor_ct_map.geojson`
- `provincial_2025_ct_map.geojson`
- `federal_2025_ct_map.geojson`
- `map_build_summary.json`

Each election file contains the same 585 Toronto-linked 2021 CT polygons plus
allocated votes, `citizen_canadian_18over`, citizen-18+ participation,
allocated-elector turnout where available, quality flags, and party or
candidate vote distributions.

Rebuild from `analysis/toronto_election_turnout/`:

```bash
npm run build:interpolation-map
```

The build reads final CT tables from `../processed/` and validation summaries
from `../processed/intermediate/04_validation/`. It is blocked unless vote
preservation, no-geometry allocation, vote-bearing exclusion, and official
party/candidate reconciliation checks pass. `map_build_summary.json` records
the gate results and feature counts.

The GeoJSON retains fractional interpolated votes and electors. The Leaflet
viewer rounds tract-level allocated vote and elector counts to the nearest
whole number only in hover and popup details. Stored values, Toronto-wide
totals, vote shares, and turnout calculations continue to use the unrounded
estimates.
