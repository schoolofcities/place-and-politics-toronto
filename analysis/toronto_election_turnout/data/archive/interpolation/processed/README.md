# Final Interpolated CT Results

This directory contains the final analysis-ready CSV outputs. Each election has
one wide CT results table and one long candidate results table:

- `municipal_2023_mayor_ct_estimated_results.csv`
- `municipal_2023_mayor_ct_candidate_estimated_votes.csv`
- `provincial_2025_ct_estimated_results.csv`
- `provincial_2025_ct_candidate_estimated_votes.csv`
- `federal_2025_ct_estimated_results.csv`
- `federal_2025_ct_candidate_estimated_votes.csv`

All crosswalks, audits, exclusions, validations, and run summaries are stored
under `intermediate/`. Geometry-inclusive delivery files are stored in
`../map/`.

## CT Results Tables

The `*_ct_estimated_results.csv` files contain one row for each of the 585
Toronto-linked 2021 census tracts.

### Identifiers and Counts

- `election_id`: election dataset identifier.
- `ct_id`: 2021 census tract identifier; read as text.
- `estimated_total_votes`: allocated official turnout numerator or ballots
  reported by the election source.
- `estimated_electors`: allocated official elector count where available.
- `estimated_valid_candidate_votes`: allocated votes accepted for candidates.
  This can be lower than total votes when rejected, declined, or unmarked
  ballots are included in the turnout numerator.

### Turnout and Census Denominator

- `estimated_turnout`: `estimated_total_votes / estimated_electors`.
- `citizen_canadian_18over`: 2021 Census Canadian citizens aged 18 and over.
- `citizen_canadian_18over_status`: publication/suppression status of the
  direct CT Census value.
- `estimated_turnout_citizen_18plus`: citizen-18+ participation rate.
- `estimated_participation_citizen_18plus`: identical production field,
  calculated as `estimated_total_votes / citizen_canadian_18over`.

The citizen-18+ rate is a census-denominator participation measure, not the
official registered-elector turnout rate.

### Party Votes

Columns matching `party_*_votes` contain allocated valid candidate votes
grouped by official party affiliation.

- Provincial and federal tables contain one column per party.
- Municipal contains `party_non_partisan_votes` because Toronto mayoral
  ballots do not report official party affiliations. Use the candidate table
  for meaningful municipal vote distributions.

### Allocation Diagnostics

- `num_source_polls`: mapped source polls contributing to the CT.
- `num_source_district_vote_type_groups`: no-geometry district/vote-type
  groups contributing to the CT.
- `share_from_largest_source`: largest single source contribution.
- `allocation_method`: semicolon-separated methods used for the CT.
- `fallback_area_weight_used`: whether any mapped poll required area fallback.
- `zero_population_weight`: whether a contributing source had zero usable
  population weight.
- `suppressed_da_count`: contributing DAs with suppressed ancillary values.
- `suppressed_da_area_share`: share of contributing area associated with
  suppressed DAs.
- `excluded_weight_area_share`: area share excluded from population weighting.
- `ancillary_weight_variable`: always `citizen_canadian_18over` in production.
- `ancillary_weight_status`: status of the ancillary weights contributing to
  the CT.
- `no_geometry_district_allocation_used`: whether district-to-CT allocation
  contributed.
- `votes_exceed_electors_flag`: denominator-quality flag preserved from source
  rows.
- `missing_votes_excluded_flag`: indicates excluded missing-vote source rows.

## Candidate Results Tables

The `*_ct_candidate_estimated_votes.csv` files are long tables with one row per
CT-candidate combination:

- `election_id`
- `ct_id`
- `candidate_id`
- `candidate_name`
- `party_name`
- `estimated_candidate_votes`

Join these tables to the matching CT results table using
`election_id + ct_id`. They are the preferred source for municipal candidate
analysis and can also support provincial or federal candidate-level analysis.

## Geometry

These CSVs intentionally omit geometry. Use the matching file in `../map/`
when a single GeoJSON containing CT geometry, votes, citizen population,
turnout, and party/candidate distributions is required.
