# Processed Turnout Files

This folder stores the primary polling-division turnout outputs for the map and
downstream analysis.

## Files

For each election, there is:

- A `.csv` file with properties plus geometry serialized as GeoJSON text.
- A `.geojson` file for direct mapping.
- District lookup files ending in `_districts.csv` and `_districts.json`.

Current elections:

- `toronto_municipal_2023_mayor_turnout_subdivisions`
- `toronto_provincial_2025_turnout_poll_divisions`
- `toronto_federal_2025_turnout_poll_divisions`

## Key Fields

- `electoral_district_number`: ward or riding identifier.
- `polling_division_number`: polling division/subdivision identifier.
- `polling_division_name`: source polling-place label when available.
- `vote_type`: `election_day`, `advance`, `mail_in`, or `special`.
- `number_of_votes`: official votes for the reporting row.
- `number_of_electors`: official elector count where supported.
- `proportion_of_turnout`: `number_of_votes / number_of_electors` when coherent.
- `vote_in_other_division`: target division when a source reports this row with another division.
- `source_note`: plain-language source/missingness note.
- `poll_id`: stable key joining the poll to normalized candidate-vote tables.
- `poll_total_candidate_votes`: sum of valid votes cast for candidates.
- `party_*_votes`: wide party totals generated from candidate-level results.
- `geometry`: polygon geometry, blank for valid reporting rows without ordinary poll geometry.

The poll summary is the analysis-ready master table. Candidate identity and
candidate-level vote detail are normalized under `../candidate_details/` to avoid
repeating these poll fields for every candidate.

`number_of_votes` and `poll_total_candidate_votes` may differ because the
turnout numerator can include rejected, declined, or unmarked ballots that are
not votes for a candidate.

For readability, all `party_*_votes` fields appear immediately after
`proportion_of_turnout`, and `geometry` is the final CSV column. Geometry
availability is determined directly from `geometry`; no redundant
`has_geometry` field is published.

Rows without geometry are valid official reporting buckets, but they need a
separate allocation strategy before census-tract interpolation.
