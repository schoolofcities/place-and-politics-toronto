# Interpolation Data

Generated poll-to-census-tract interpolation products are split into:

```text
interpolation/
  processed/
  map/
```

- `processed/` contains election-specific CT estimates, poll-to-CT and
  district-to-CT crosswalks, exclusions, audit tables, and validation reports.
- `map/` contains compact validated GeoJSON used by the Leaflet interpolation
  viewer.

Rebuild the processed results and audits with:

```bash
cd analysis/toronto_election_turnout/interpolation
python3 run_interpolation.py
python3 audit_geographic_temporal_coverage.py
python3 audit_official_results.py
```

Build map-ready GeoJSON after the blocking integrity gates pass:

```bash
cd analysis/toronto_election_turnout
npm run build:interpolation-map
```

See the interpolation module README for methodology, assumptions, output
schemas, and quality flags.
