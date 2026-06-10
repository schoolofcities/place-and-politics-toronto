# Processed Election Data

Outputs are grouped by election:

```text
processed/
  municipal_2023_mayor/
    turnout/
    candidate_details/
  provincial_2025/
    turnout/
    candidate_details/
  federal_2025/
    turnout/
    candidate_details/
  metadata/
```

## Turnout

Each `turnout/` folder contains:

- A poll/subdivision `.csv` with geometry serialized as GeoJSON text.
- A matching `.geojson` for mapping.
- District lookup files ending in `_districts.csv` and `_districts.json`.

Important fields include `poll_id`, district and poll identifiers,
`vote_type`, `number_of_votes`, `poll_total_candidate_votes`,
`number_of_electors`, turnout, `party_*_votes`, source notes, and geometry.

Rows without geometry are valid official reporting buckets and are retained
for district-to-CT interpolation.

## Candidate Details

Each `candidate_details/` folder contains:

- `toronto_*_candidates.csv`: candidate identity, district, party, and source.
- `toronto_*_poll_candidate_votes.csv`: sparse nonzero
  `poll_id + candidate_id + candidate_vote_count` bridge.

Municipal mayoral candidates are officially non-partisan. Candidate-level
results are therefore the finest meaningful municipal result measure.

## Metadata

- `metadata/qa_summary.json`: election source and geometry row counts.
- `metadata/normalized_election_results_metadata.json`: filenames, party
  column mappings, row counts, and sparse-bridge rules.

Join candidate vote rows to turnout using `poll_id` and to candidate catalogs
using `candidate_id`.
