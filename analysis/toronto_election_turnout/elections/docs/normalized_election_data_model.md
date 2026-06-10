# Normalized Election Data Model

The processed election data uses an analysis-friendly poll summary plus
normalized candidate detail. This preserves every source variable while
avoiding repeated geometry, elector counts, turnout, and source notes.

## 1. Poll Summary

Location:

`data/toronto_election_turnout/elections/processed/<election>/turnout/`

One row represents one election, district, polling division, and vote type.
The election and year are encoded in the filename.

The poll summary is the GIS master table. It contains:

- `poll_id`
- district and polling-division identifiers and names
- `vote_type`
- `number_of_votes`
- `number_of_electors`
- `proportion_of_turnout`
- geometry
- source and combined-poll notes
- `poll_total_candidate_votes`
- wide `party_*_votes` totals

The CSV and GeoJSON carry the same poll properties. Use the GeoJSON for direct
mapping and the CSV for tabular analysis.

## 2. Candidate Catalog

Location:

`data/toronto_election_turnout/elections/processed/<election>/candidate_details/toronto_*_candidates.csv`

One row represents one candidate in the election. It contains:

- `candidate_id`
- `electoral_district_number`
- `candidate_name`
- `party_name`
- `source_note`

Municipal mayoral candidates are citywide, so their district field is blank
and their party is `Non-partisan`.

## 3. Poll-Candidate Vote Bridge

Location:

`data/toronto_election_turnout/elections/processed/<election>/candidate_details/toronto_*_poll_candidate_votes.csv`

One row represents a nonzero candidate result in one poll:

- `poll_id`
- `candidate_id`
- `candidate_vote_count`

This table intentionally does not repeat district names, geometry, poll totals,
electors, turnout, candidate names, party names, or source notes.

## Join Rules

- Join the bridge to a poll summary on `poll_id`.
- Join the bridge to a candidate catalog on `candidate_id`.
- Provincial and federal candidates apply only to their catalogued district.
- Municipal mayoral candidates apply citywide.
- If `poll_total_candidate_votes` is non-null, an applicable candidate absent
  from the sparse bridge has zero votes.
- If `poll_total_candidate_votes` is null, candidate results are unavailable
  for that poll; absence must not be interpreted as zero.

## Count Semantics

`number_of_votes` is the turnout numerator supported by the election source.
It can include rejected, declined, or unmarked ballots.

`poll_total_candidate_votes` is the sum of valid votes assigned to candidates.
The sum of all `party_*_votes` fields equals
`poll_total_candidate_votes`. It can therefore be lower than
`number_of_votes`.

The exact full-party-name to column-name mapping is stored in:

`data/toronto_election_turnout/elections/processed/metadata/normalized_election_results_metadata.json`

## Rebuild

From `analysis/toronto_election_turnout/`:

```bash
python elections/scripts/build_election_datasets.py
```

The wrapper rebuilds turnout outputs first and then regenerates all normalized
candidate and party fields. It finishes by validating keys, joins, and vote
total reconciliation.
