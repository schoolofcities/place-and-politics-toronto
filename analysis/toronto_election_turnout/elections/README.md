# Election Analysis

This folder contains election-specific scripts, documentation, and the local map
viewer.

## Structure

```text
elections/
  scripts/
  docs/
  viewer/
```

## Scripts

- `scripts/build_election_datasets.py`
  - Canonical entry point. Rebuilds turnout outputs, then normalized candidate
    and party outputs.

- `scripts/build_turnout_geojson.py`
  - Builds optimized turnout CSV/GeoJSON files from election sources.
  - Writes to `data/toronto_election_turnout/elections/processed/turnout/`.

- `scripts/build_candidate_party_votes.py`
  - Adds `poll_id`, candidate-vote totals, and wide party totals to poll
    summaries.
  - Builds candidate catalogs and sparse poll-candidate vote bridges.
  - Writes metadata and normalized tables to
    `data/toronto_election_turnout/elections/processed/candidate_details/`.

- `scripts/validate_normalized_election_data.py`
  - Checks unique keys, bridge joins, and equality among candidate, party, and
    poll-level valid-vote totals.

## Docs

- `docs/data_notes.md`: compact source, schema, missingness, and field-use notes.
- `docs/official_totals_audit.md`: reconciliation against official source totals.
- `docs/granularity_audit.md`: checks for atlas dots, no-geometry rows, and polygon coverage.
- `docs/provincial_candidate_party_audit.md`: official-source party-affiliation
  matching and validation for all 144 Toronto provincial candidates.
- `docs/normalized_election_data_model.md`: table roles, keys, join rules, and
  count semantics for the normalized election outputs.

## Viewer

The viewer is served through the parent package:

```bash
cd analysis/toronto_election_turnout
npm start
```

Open `http://127.0.0.1:5173`.

Rebuild all election data with:

```bash
npm run build:data
```

Processed turnout geometry is written to
`data/toronto_election_turnout/elections/processed/turnout/`; normalized
candidate catalogs and sparse candidate-vote bridges are written to
`data/toronto_election_turnout/elections/processed/candidate_details/`.
