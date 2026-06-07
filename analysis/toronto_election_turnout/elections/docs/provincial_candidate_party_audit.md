# Provincial Candidate Party Audit

This note documents how party affiliation was assigned to candidates in the
normalized Toronto 2025 provincial election outputs.

## Official Sources

All candidate-party relationships come from Elections Ontario.

1. `Official Return from the Records`
   - Poll-by-poll accepted candidate votes.
   - Stored as:
     `data/toronto_election_turnout/elections/raw/eo_2025_official_return.csv`

2. `Summary of Valid Votes Cast for Each Candidate`
   - Official candidate name, electoral district, final valid-vote total, and
     `PoliticalInterestCode`.
   - Elections Ontario report group `48`, output `1096`.
   - Stored as:
     `data/toronto_election_turnout/elections/raw/source_downloads/eo_2025_candidate_summary.csv`

3. `Political Interest Codes`
   - Maps each `PoliticalInterestCode` to the full registered party name.
   - Elections Ontario report group `48`, output `1094`.
   - Stored as:
     `data/toronto_election_turnout/elections/raw/source_downloads/eo_2025_political_interest_codes.csv`

Official API catalogue:

`https://results.elections.on.ca/api/report-groups/48`

Official CSV endpoints:

- `https://results.elections.on.ca/api/report-groups/48/report-outputs/1096/csv`
- `https://results.elections.on.ca/api/report-groups/48/report-outputs/1094/csv`

## Matching Method

The poll-level Official Return formats names as `FAMILY, GIVEN`, while the
candidate summary generally formats names as `GIVEN FAMILY`. To avoid fragile
name-order matching, candidates were linked using:

- electoral district number; and
- final candidate valid-vote total.

Within the 25 Toronto electoral districts, this key is unique for every
candidate in both official reports.

## Validation

- Toronto candidates in the poll-level Official Return: 144.
- Toronto candidates in the official candidate summary: 144.
- One-to-one matched candidates: 144.
- Unmatched candidates: 0.
- Duplicate district/vote-total keys: 0.
- Missing political-interest codes: 0.
- Codes without full party names: 0.
- Distinct full party names represented in Toronto: 15.

The intermediate candidate-party lookup is not stored as a separate processed
dataset because it can be regenerated from the two official source reports and
the builder script. Verified full party names are stored once in the candidate
catalog:

`data/toronto_election_turnout/elections/processed/candidate_details/toronto_provincial_2025_candidates.csv`

The poll summary stores aggregated `party_*_votes` columns, while the sparse
poll-candidate bridge stores only `poll_id`, `candidate_id`, and nonzero vote
counts.
