# Polling Station Accessibility Data

This folder contains outputs for the polling station accessibility audit and
future distance-vs-turnout analysis.

## Processed Outputs

```text
processed/
  polling_locations/
  poll_to_location_links/
  poll_accessibility_metrics/
  turnout_distance_analysis/
  audits/
map/
raw/
```

### `processed/polling_locations/`

One file per election level. Municipal 2023 stores one official Open Toronto
point per mapped polling subdivision. Provincial 2025 currently stores
candidate location labels from the official return but no accepted final
coordinates. Federal 2025 currently has no useful ordinary polling-location
labels.

### `processed/poll_to_location_links/`

One file per election level. These files link every mapped original election
row to a polling location when one can be inferred, and otherwise explain why
the row is not linkable.

### `processed/poll_accessibility_metrics/`

One file per election level. These files preserve every mapped original
election row and add geometry-side accessibility fields such as `poll_area_km2`,
`poll_centroid_lon`, `poll_centroid_lat`, `poll_point_on_surface_lon`, and
`poll_point_on_surface_lat`.

Municipal 2023 includes station coordinates and straight-line distance fields.
Provincial 2025 and Federal 2025 keep distance fields blank until complete,
verified polling station coordinates are added.

### `processed/turnout_distance_analysis/`

Exploratory turnout-vs-distance outputs for elections with usable station
points:

- `turnout_distance_analysis_rows.csv` contains the modeled poll rows, turnout,
  point-on-surface distance to the assigned station/building point, poll area,
  votes, electors, and source-status flag.
- `turnout_distance_summary.csv` reports sample size, mean turnout, mean and
  median distance, area-turnout correlations, and distance-turnout correlations.
- `turnout_distance_models.csv` reports simple OLS model summaries for distance,
  distance plus area, distance plus district fixed effects, and distance plus
  area plus district fixed effects.

Municipal 2023 is complete. Provincial 2025 is partial and conservative:
accepted coordinates include exact Elections Ontario proposed voting-location
name matches geocoded to Open Toronto Address Points, plus exact Open Toronto
place-name/civic-address matches for official-return labels. Federal 2025 is
excluded because no official bulk station-location table has been found.

### `processed/audits/`

Contains source-readiness, exclusion, and model-readiness summaries. Municipal
mapped rows with valid votes, electors, and turnout are model-ready. Provincial
and federal mapped rows remain excluded from distance modelling because verified
coordinate sources have not been added.

Provincial-specific source coverage files:

- `provincial_2025_eo_pvl_match_summary.csv` records mapped 2025 poll rows,
  downloaded Elections Ontario proposed voting-location rows, exact name-match
  counts, fuzzy-review counts, and no-candidate counts.
- `provincial_2025_eo_pvl_match_detail.csv` records row-level match status and
  the best proposed-location candidate. Fuzzy candidates are audit leads only;
  they are not accepted station assignments.

Federal-specific source coverage file:

- `federal_2025_polling_location_source_search_audit.csv` records the official
  2025 sources checked so far: local Elections Canada poll-by-poll CSV
  downloads, the official 45th General Election results pages, the Open
  Government 2025 electoral geography boundary package, and Elections Canada's
  Voter Information Service. These sources support vote/geography auditing but
  do not provide a public per-poll building coordinate table.

## Important Limitation

Municipal 2023 has verified Open Toronto polling-location coordinates for all
mapped polling subdivisions.

Provincial 2025 has a partial official-source path, but not a complete accepted
poll-to-station coordinate table yet. Elections Ontario proposed voting-location
CSV exports were downloaded for the Toronto districts under
`raw/provincial_2025/eo_proposed_voting_locations/`. These files include voting
location names and addresses. Open Toronto Address Points can be used to
geocode those addresses through the reproducible analysis script. Where the
proposed-location list does not exactly match a mapped 2025 polling row by
district and name, the workflow accepts only exact Open Toronto place-name or
civic-address matches to the official-return label. Fuzzy proposed-location
candidates remain audit leads only.

Federal 2025 does not yet have a bulk official polling station coordinate
source. Elections Canada's Voter Information Service is a voter/district lookup
service and states that polling-place locations are available during an
election, but the repository does not currently contain a post-election bulk
table linking each mapped federal polling division to a station coordinate.

Current provincial outputs support partial distance analysis for resolved
building points, plus source auditing, linkage auditing, mapped-poll area
metrics, and model-readiness checks. Federal distance fields remain blank until
official or high-confidence polling station coordinates are added.

## Raw Source Files

```text
raw/
  municipal_2023_mayor/
    open_toronto_voting_locations_2023.csv
  open_toronto/
    address_points.csv  # local-only cache; not committed because it exceeds 100 MB
  provincial_2025/
    eo_proposed_voting_locations/
      eo_pvl_*.csv
    eo_proposed_voting_locations_geocoded.csv  # optional cache, if fetched
    eo_official_return_label_address_point_candidates.csv
```

Municipal raw source:
Open Toronto `Elections Voting Locations`, downloaded from the City of
Toronto open data portal. `POINT_LONG_CODE` joins to municipal ward/subdivision
codes and covers all mapped 2023 mayoral rows.

Provincial raw source:
Elections Ontario Voter Information Service proposed voting-location CSV export
endpoint, one file per Toronto electoral district. These files are useful for
candidate location/address discovery. Exact proposed-location name matches are
geocoded through the official Open Toronto Address Points bulk table at
`raw/open_toronto/address_points.csv`.
That Address Points CSV is intentionally kept as a local raw cache rather than
committed to Git because the full official table is larger than GitHub's
single-file limit. The processed geocoded outputs in this folder preserve the
accepted station coordinates used by the analysis.

The `eo_proposed_voting_locations_geocoded.csv` cache is produced by parsing
Elections Ontario proposed-location addresses and matching them locally to
Open Toronto Address Points by street number and street name. This replaced the
earlier live-API-only geocode pass, which missed many valid addresses because
free-text datastore search did not handle all street abbreviations.

The `eo_official_return_label_address_point_candidates.csv` cache is produced
by querying Open Toronto Address Points with the official-return
`VotingPlaceAddressOrLocation` labels used in the processed provincial turnout
file. It is a candidate-review table; only exact place-name or exact
civic-address matches are promoted to final coordinate assignments. In the
current processed output, 1,182 of 1,388 mapped provincial rows have accepted
coordinates, and 1,180 are distance-model-ready after turnout/elector
exclusions. Accepted rows include 1,139 exact proposed-location/address-point
matches, 32 exact official-label place-name matches, and 11 exact official-label
civic-address matches. The remaining 206 mapped rows stay unresolved; fuzzy
matches remain review items unless a more precise official match can be
established.

## Key Join Field

Use `poll_id` to join accessibility outputs back to original election turnout
rows. Do not join only on polling division number because those identifiers
repeat across elections and districts.
