# Poll-to-Census-Tract Interpolation

This module allocates Toronto election results from polling records to the 585
2021 census tract polygons linked to Toronto dissemination areas.

## Method

The workflow implements the supplied population-weighted interpolation method:

1. Load poll, CT, DA, and district geometries.
2. Transform every geometry to EPSG:3347.
3. Repair invalid geometries and retain polygonal components only.
4. Intersect mapped polls with CTs and DAs.
5. Estimate the DA weight in each mapped poll-CT overlap as:

   ```text
   citizen_canadian_18over * overlap_area / DA_area
   ```

6. Normalize the resulting CT weights within each poll.
7. Allocate total votes, available electors, valid candidate votes, party
   votes, and sparse candidate-bridge votes with the same weights.
8. Build a separate district-to-CT crosswalk for geometryless records using
   the same DA-level `citizen_canadian_18over` variable.
9. Allocate geometryless votes, electors, party votes, and candidate votes
   through that district crosswalk and aggregate them by district and vote
   type in the CT result.

Because allocation is linear, applying one district crosswalk to each source
row and summing by `district + vote_type` is mathematically identical to
pre-summing those rows. The CT output identifies each such aggregate as one
source group.

## Fixed Decisions

- Mapped polls and geometryless district allocations both use
  `citizen_canadian_18over`.
- Its 16 suppressed DA values are treated as zero and are never replaced with
  another population variable.
- All overlay and area calculations use EPSG:3347.
- Only CT polygons with `contains_toronto_da = true` are retained. This yields
  585 CTs and excludes 37 boundary-touch line remnants.
- Invalid poll geometries are repaired with GDAL `MakeValid`.
- A mapped vote-containing poll with zero DA weight uses CT intersection area
  as its fallback and is explicitly flagged.
- A district with zero population weight is not area-allocated. Its records
  remain unallocated.
- Rows with missing votes are excluded rather than treated as zero.
- Votes that exceed their reported elector denominator are preserved and
  flagged.
- Municipal candidate estimates come from the sparse candidate bridge, not
  the combined `party_non_partisan_votes` field.
- CT output includes `citizen_canadian_18over`,
  `estimated_turnout_citizen_18plus`, and
  `estimated_participation_citizen_18plus = estimated_total_votes /
  citizen_canadian_18over`.
- The two CTs with suppressed citizen-adult counts receive a null estimated
  participation rate.
- Census citizen-adult participation is diagnostic. It must not be interpreted
  as official turnout because it is not the election-specific registered-
  elector denominator.

## Run

The script requires Python 3 with GDAL's `osgeo` bindings:

```bash
cd analysis/toronto_election_turnout/interpolation
python3 run_interpolation.py
```

Additional geographic and temporal coverage diagnostics can be regenerated
with:

```bash
cd analysis/toronto_election_turnout/interpolation
python3 audit_geographic_temporal_coverage.py
```

Official party, candidate, and turnout-reference reconciliation can be
regenerated with the project data runtime:

```bash
python3 audit_official_results.py
```

After the audit gates pass, build and run the CT Leaflet map with:

```bash
cd analysis/toronto_election_turnout
npm run build:interpolation-map
npm run start:interpolation
```

Outputs are written to:

```text
data/toronto_election_turnout/interpolation/processed/
```

## Outputs

Each election receives:

- `*_poll_to_ct_crosswalk.csv`
- `*_district_to_ct_crosswalk.csv`
- `*_ct_estimated_results.csv`
- `*_ct_candidate_estimated_votes.csv`
- `*_excluded_unallocated.csv`
- `*_no_geometry_allocation_audit.csv`
- `*_turnout_comparison.csv`
- `*_audit.csv`
- `*_validation.csv`
- `*_summary.json`

Combined files include:

- `census_input_audit.json`
- `geographic_coverage_audit.csv`
- `temporal_population_proxy_audit.csv`
- `geographic_temporal_audit_summary.json`
- `official_party_vote_reconciliation.csv`
- `official_candidate_vote_reconciliation.csv`
- `official_result_reconciliation_summary.json`
- `turnout_reference_audit.csv`

Map-ready files are written under:

```text
data/toronto_election_turnout/interpolation/map/
```
- `suppressed_da_audit.csv`
- `interpolation_audit.csv`
- `excluded_unallocated_report.csv`
- `no_geometry_allocation_audit.csv`
- `turnout_comparison.csv`
- `validation_report.csv`
- `validation_summary.json`

Validation compares source and allocated totals globally and by district for
total votes, electors, valid candidate votes, every party column, and every
candidate represented in the sparse bridge. It also validates each individual
vote-bearing source poll/reporting row after summing its CT allocations.

The validation summary contains a map gate. A map should be built only when
vote preservation, no-geometry allocation, vote-bearing exclusion, and
participation-rate alignment checks all pass.

## Geographic Coverage Decision

The coverage audit compares the selected municipal, provincial, and federal
district union with the broader official CT and DA bounding-box downloads.
It distinguishes positive-area boundary intersections from geographies whose
representative point is inside the selected election universe.

Result: all representative-point CTs and DAs are already present in the stored
Toronto target universe. The extra intersections are boundary/water/sliver
contacts: 37 CTs and 63 DAs are touched by the selected district union but are
not selected populated components. No CT or DA geography was added, and the
interpolation weights were not rerun for a changed target universe.

## Temporal Population Decision

The temporal audit uses official Statistics Canada annual estimates as
diagnostics only:

- Table 17-10-0155-01 for Toronto CSD total population.
- Table 17-10-0152-01 for Toronto CD single-year age population, summed for
  ages 18 and over.

Those tables show population growth between 2021 and the election years, but
they do not publish `citizen_canadian_18over` annually at DA, CT, Toronto CSD,
or Toronto CD geography. Because the production denominator and interpolation
weight variable are Canadian citizens aged 18 and over, the workflow does not
multiply the production CT citizen denominator by either total-population or
all-adult growth proxies. The proxy rates are reported in
`temporal_population_proxy_audit.csv` for sensitivity review only.

## Official Result Reconciliation

Party and candidate totals are rebuilt independently from the official source
files and compared with the normalized election tables globally and within
each ward or riding. Party totals are then compared with the interpolated
validation totals at the same levels.

The reconciliation distinguishes valid candidate votes from total ballots
cast. Provincial and federal turnout numerators include rejected, unmarked, or
declined ballots, so they can be larger than the sum of candidate or party
votes. The municipal mayoral race is non-partisan; candidate totals are the
finest meaningful result measure.

Turnout references are also tagged by geography. Ontario-wide and Canada-wide
federal turnout are useful context, but they are not direct validation targets
for selected Toronto ridings. Likewise, Elections Ontario's province-wide
turnout is context for the provincial election, not a substitute for the
selected Toronto-riding rate.

`turnout_reference_audit.csv` records both the absolute percentage-point
difference and whether the citizen-18+ estimate is within a 2.5 percentage
point contextual margin. This margin is descriptive only; direct validation
still requires matching election geography and denominator definitions.

Suppressed DA citizen estimates are treated as zero for weighting, but the
available city-level reconciliation indicates that suppression alone should
not be assumed to explain a material turnout-rate difference. Census year,
citizenship estimate methodology, and the distinction between citizens and
registered electors remain important denominator differences.

## Leaflet Map

The dedicated interpolation viewer maps all 585 target CTs for municipal,
provincial, and federal elections. It supports:

- citizen-18+ participation rate;
- allocated-elector turnout rate;
- party vote-share choropleths for provincial and federal elections;
- Toronto-wide official and contextual turnout comparisons;
- tract-level total votes, citizen population aged 18+, turnout, and complete
  nonzero party vote distributions with both share and estimated vote count;
- municipal candidate-share details because the mayoral election is
  non-partisan.
- municipal candidate-share filtering across all 102 certified candidates.

Party map intensity uses vote share rather than raw vote count. Vote share is
the standard comparative election-map measure because it is not mechanically
larger in more populous CTs. Raw estimated party votes remain visible in hover
and popup details.

Map generation is blocked unless vote preservation, no-geometry allocation,
vote-bearing exclusion, and official-result reconciliation checks pass.
Turnout-reference proximity is displayed with its geography and source status;
it is not used as a substitute for vote-integrity validation.

The municipal party-affiliation decision and official sources are documented
in `MUNICIPAL_PARTY_AFFILIATION_AUDIT.md`. Historical federal/provincial party
service is not converted into an official Toronto mayoral ballot affiliation.
