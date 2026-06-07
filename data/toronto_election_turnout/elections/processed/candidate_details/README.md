# Normalized Candidate Data

These files hold candidate identity and candidate-level vote detail without
repeating poll geometry, turnout, electors, or source notes on every candidate
row.

## Files

- `toronto_*_candidates.csv`
  - One row per candidate.
  - Contains `candidate_id`, district, candidate name, party, and source note.
  - Municipal mayoral candidates are labelled `Non-partisan`.

- `toronto_*_poll_candidate_votes.csv`
  - Sparse bridge with one row per nonzero candidate result in a poll.
  - Contains only `poll_id`, `candidate_id`, and `candidate_vote_count`.
  - Zero-vote rows are omitted to reduce storage.

- `normalized_election_results_metadata.json`
  - Records row counts, source-row counts, zero-vote omissions, and the mapping
    from full party names to party-total columns in the poll summary files.

Election level and year are encoded in each filename. The redundant
`election_level` and `election_year` columns are intentionally omitted.

## Join Rules

1. Join a bridge row to `toronto_*_candidates.csv` using `candidate_id`.
2. Join a bridge row to the matching turnout CSV/GeoJSON using `poll_id`.
3. For a poll with non-null `poll_total_candidate_votes`, an applicable
   candidate absent from the sparse bridge has zero votes.
4. For a poll with null `poll_total_candidate_votes`, absence from the bridge
   means candidate-level results are unavailable, not zero.

Candidate applicability is district-specific for provincial and federal
elections. Municipal mayoral candidates are citywide.

## Important Count Difference

`candidate_vote_count` sums accepted/valid votes for candidates. It does not include rejected, declined, or unmarked ballots.

The turnout files' `number_of_votes` field is the turnout numerator where
supported by the source. `poll_total_candidate_votes` is the sum of valid
candidate votes, and the `party_*_votes` columns sum to that value. Candidate
totals can therefore be lower than turnout totals.

Geometry lives only in the poll summary files under `../turnout/`. Geometry
availability is read directly from that field rather than duplicated in a
`has_geometry` column.
