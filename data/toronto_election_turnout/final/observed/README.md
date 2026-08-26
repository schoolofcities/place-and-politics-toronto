# Observed and Engineered Data Dictionary

This folder contains cleaned source-derived variables and spatially allocated
election estimates. It excludes latent scores and model predictions.

## `toronto_ct_2021_observed_variables`

Files: `toronto_ct_2021_observed_variables.csv` and
`toronto_ct_2021_observed_variables.geojson`. Grain: one row per CT. Primary key: `ct_id`.
Dimensions: 585 rows × 90 columns.

Column families:

| Prefix/family | Contents |
| --- | --- |
| identifiers and population | CT identifiers, census year, population denominators, and land area |
| `block1_` | Demographic and socioeconomic composition: age, education, household size, income, and unemployment |
| `block2_` | Housing, tenure, residential stability, dwelling form, and density |
| `block3_` | Immigration, citizenship, visible-minority, and language measures |
| `block4_` | Municipal, provincial, and federal competitiveness and fragmentation |
| `block5_` | Transportation, service access, neighbourhood events, 311, and housing-support measures |
| `outcome_` | Municipal, provincial, federal, and mean participation/turnout outcomes |

Shares are stored as proportions unless the machine-readable variable
dictionary specifies otherwise. Use `metadata/variable_dictionary.csv` for the
exact unit, numerator, denominator, source, and missingness of every column.

## `toronto_ct_election_results`

Files: `toronto_ct_election_results.csv` and
`toronto_ct_election_results.geojson`. Grain: one row per CT. Primary key: `ct_id`.
Dimensions: 585 rows × 94 columns.

Columns are grouped by `municipal_2023_mayor_`, `provincial_2025_`, and
`federal_2025_`. Within each election prefix:

| Suffix family | Meaning |
| --- | --- |
| vote/elector totals | Estimated CT votes, valid candidate votes, and registered electors |
| turnout/participation | Rates using registered electors or citizen-18+ denominators |
| `party_*_votes` | Estimated CT votes by party or affiliation |
| source/allocation fields | Number and concentration of source polls and the allocation method |
| suppression/coverage fields | Suppressed geography counts and excluded-area shares |
| `*_flag` and `*_status` | Allocation, denominator, or data-quality diagnostics |

These are allocated estimates derived from official election geography; they
are not official CT returns. Retain the diagnostic columns when auditing or
filtering estimates.

## `toronto_ct_candidate_results`

File: `toronto_ct_candidate_results.csv`. Grain: one row per election × CT ×
candidate. Primary key: `election_id + ct_id + candidate_id`. Dimensions:
62,201 rows × 10 columns.

| Column | Meaning |
| --- | --- |
| `election_id` | Election identifier |
| `ct_id` | Canonical CT join key |
| `candidate_id` | Candidate identifier within the source election |
| `candidate_name` | Candidate display name |
| `party_name` | Party or affiliation label |
| `estimated_candidate_votes` | Spatially allocated candidate votes in the CT |
| `estimated_candidate_vote_share` | Candidate votes divided by valid candidate votes in the CT |
| `candidate_results_available_flag` | Whether a usable CT candidate denominator exists |
| `candidate_rank_in_ct` | Vote rank within election and CT; blank when unavailable |
| `candidate_winner_in_ct_flag` | Whether the candidate is tied for rank 1 in the CT |

Do not force this table into a single row per CT: the candidate roster differs
across elections. Aggregate explicitly by election and CT when a wide table is
needed.
