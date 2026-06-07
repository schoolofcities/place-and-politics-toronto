# Poll-to-CT Interpolation Readiness

This note summarizes the current readiness for population-weighted interpolation from election polling divisions to 2021 census tracts.

## Step 1: Attached ADA Files

Two ADA reference files were inspected:

- `toronto-ada.csv`
- `toronto-ada.gpkg`

The CSV is long-form profile data with 44,919 rows, 279 ADA geographies, and 161 characteristics per ADA. It includes `citizen_canadian_18over`, which is a strong match for the algorithm's preferred weighting concept, `citizens_above_18`.

The GeoPackage has 279 ADA polygons in EPSG:3347, NAD83 / Statistics Canada Lambert. Fields are `ADAUID`, `DGUID`, `LANDAREA`, and `PRUID`.

Important limitation: ADA is not the preferred ancillary unit for this method. ADA geography is coarser than DA. Use it for variable discovery and possible sensitivity checks, not as the main ancillary unit if DA variables can be obtained.

Stored copies:

- `data/toronto_election_turnout/census/reference/ada_2021/toronto_ada_2021_profile.csv`
- `data/toronto_election_turnout/census/reference/ada_2021/toronto_ada_2021_boundaries.gpkg`

## Step 2: Algorithm Requirements and Census Inputs

The interpolation PDF requires:

1. Election poll layer:
   - `poll_id`
   - poll geometry
   - total votes
   - party/candidate votes if estimating party shares

2. Census tract layer:
   - `ct_id`
   - CT geometry
   - optional CT population denominator for approximate turnout

3. Ancillary population layer:
   - `unit_id`
   - unit geometry
   - one population-like weight variable

Preferred ancillary weight hierarchy:

1. `citizens_above_18`
2. `voting_age_population`
3. `adult_population`
4. `total_population`
5. `dwelling_count`

Current stored census geometry:

- `data/toronto_election_turnout/census/raw/statcan_2021_toronto_csd.gpkg`
- `data/toronto_election_turnout/census/raw/statcan_2021_ct_toronto_clipped.gpkg`
- `data/toronto_election_turnout/census/raw/statcan_2021_da_toronto_clipped.gpkg`

Feature counts:

- Toronto CSD: 1 feature.
- Toronto clipped CTs: 622 features.
- Toronto clipped DAs: 3,807 features.
- Toronto DA records used for Census Profile extraction: 3,743 records with
  `DAUID` prefix `3520`.

Newly extracted Census Profile attributes:

- DA-level `Canadian citizens aged 18 and over`: 3,743 rows, total 1,869,930,
  16 blank/suppressed rows.
- CT-level `Canadian citizens aged 18 and over`: 622 boundary-intersecting
  rows. The 585 CTs linked to verified Toronto DAs total 1,870,085, with
  2 blank/suppressed rows.
- Official Toronto CSD row in the same Census Profile source: 1,870,055.
- DA-level all-person population aged 18+: 3,743 rows, total 2,331,690,
  9 officially suppressed rows.
- Official Toronto CSD all-person population aged 18+: 2,331,130.

The DA total aligns with the official Toronto CSD row within 125 people, which
is consistent with rounding/suppression in small-area 25% sample data. The
Toronto-linked CT total aligns within 30 people. The 1,999,260 sum across all
622 clipped CTs is invalid as a city total because 37 boundary-only CT features
carry whole-tract profile counts from outside the comparable Toronto DA
universe.

Available for party/candidate interpolation:

- Poll summary files under
  `data/toronto_election_turnout/elections/processed/turnout/` contain geometry,
  total votes, electors, turnout, valid-candidate-vote totals, and wide party
  totals.
- Candidate catalogs and sparse poll-candidate vote bridges are stored under
  `data/toronto_election_turnout/elections/processed/candidate_details/`.
- Federal party labels come from Elections Canada. Municipal mayoral results
  are nonpartisan. Provincial full party names are joined from Elections
  Ontario's official candidate-summary and political-interest-code reports.

Official source identified for DA/CT attributes:

- Statistics Canada 2021 Census Profile comprehensive CSV downloads.
- The DA source used here is the Ontario-only comprehensive CSV with confidence
  intervals, about 615 MB zipped. The CT source is the CMA/CA/CT comprehensive
  CSV with confidence intervals, about 226 MB zipped. These large official zips
  are not stored in Git; the extraction script records the source URLs and
  expects the zips in `/private/tmp`.

## Step 3: Election Dataset Issues for Weighting

The current processed turnout files can support turnout interpolation for rows with geometry and valid vote/elector counts. However, several official reporting buckets do not have ordinary polling-division geometry.

### Municipal 2023

- Rows: 1,545.
- With geometry: 1,445.
- Without geometry: 100.
- Votes without geometry: 160,371.
- No-geometry rows with riding/ward number but no division number: 0.
- No-geometry rows are advance, mail-in, and special/LTC ward-level reporting buckets.

Main implication: ordinary election-day subdivisions can be interpolated directly. Advance, mail-in, and LTC/special votes cannot be assigned to CTs by poll geometry. They need a separate coarser allocation method, probably by ward, or should be reported separately from the geometry-based CT interpolation.

### Provincial 2025

- Rows: 1,532.
- With geometry: 1,388.
- Without geometry: 144.
- Votes without geometry: 199,979.
- No-geometry rows with riding/ward number but no division number: 0.
- Most no-geometry rows are advance voting. Some no-geometry election-day rows are combined polls or special reporting locations.

Main implication: geometry-backed election-day polls can be interpolated directly. Advance votes and no-geometry election-day rows need a separate allocation method by riding or should be retained as unallocated reporting buckets.

### Federal 2025

- Rows: 5,069.
- With geometry: 4,273.
- Without geometry: 796.
- Votes without geometry: 549,076.
- No-geometry rows with riding/ward number but no division number: 0.
- No-geometry rows include advance polls, special voting rules rows, and some election-day/reporting rows without atlas polygons.

Main implication: a poll-geometry interpolation of federal data will exclude or separately handle a large share of valid votes unless we define an allocation strategy for advance/special/no-geometry rows.

## Recommended Treatment

For a first defensible CT interpolation:

1. Build an `election_day_geometry_only` interpolation for each election level.
2. Preserve official totals separately so readers can see what is excluded from the geometry-based CT layer.
3. Add quality fields:
   - `allocated_votes_geometry_only`
   - `unallocated_votes_no_geometry`
   - `vote_type`
   - `allocation_method`
   - `fallback_area_weight_used`
   - `num_source_polls_t`
   - `share_from_largest_poll_t`
4. For advance/mail/special rows, do not force them into ordinary poll polygons. If they must be estimated to CTs, allocate them separately using ward/riding-level population weights and flag them as coarser-method estimates.

This keeps data integrity: official votes are preserved, but the map makes clear which votes were directly poll-geocoded and which were not.
