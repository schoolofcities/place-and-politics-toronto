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

The build is blocked unless vote preservation, no-geometry allocation,
vote-bearing exclusion, and official party/candidate reconciliation checks
pass. `map_build_summary.json` records the gate results and feature counts.
