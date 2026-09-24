# Interpolation Data

Generated poll-to-census-tract interpolation products are split into:

```text
interpolation/
  processed/
    intermediate/
      01_input_audit/
      02_spatial_crosswalks/
      03_allocation_audit/
      04_validation/
      05_context_audit/
  map/
```

- `processed/` contains the final election-specific CT result and candidate
  tables.
- `processed/intermediate/` contains poll-to-CT and district-to-CT crosswalks,
  exclusions, audit tables, validation reports, and run summaries.
- `map/` contains compact validated GeoJSON used by the Leaflet interpolation
  viewer.

Rebuild the processed results and audits with:

```bash
cd analysis/toronto_election_turnout
python3 interpolation/scripts/run_interpolation.py
python3 interpolation/scripts/audit_geographic_temporal_coverage.py
python3 interpolation/scripts/audit_official_results.py
```

Build map-ready GeoJSON after the blocking integrity gates pass:

```bash
cd analysis/toronto_election_turnout
npm run build:interpolation-map
```

See the interpolation module README for methodology, assumptions, output
schemas, and quality flags.
