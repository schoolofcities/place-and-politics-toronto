# Interpolation Intermediate Files

Intermediate outputs are grouped in algorithm order:

```text
intermediate/
  01_input_audit/
  02_spatial_crosswalks/
  03_allocation_audit/
  04_validation/
  05_context_audit/
```

Election-specific filenames begin with `municipal_2023_mayor`,
`provincial_2025`, or `federal_2025`.

## 01 Input Audit

Confirms the census target and ancillary population inputs before spatial
allocation.

- `census_input_audit.json`: target CT count, DA count, suppression treatment,
  target-universe rule, and ancillary weight variable.
- `suppressed_da_audit.csv`: `da_id`, parent `ct_id`, `value_status`,
  `ancillary_weight_variable`, and `ancillary_weight_status`.

## 02 Spatial Crosswalks

Stores the normalized spatial weights used to allocate source records.

### `*_poll_to_ct_crosswalk.csv`

One row per mapped poll-to-CT relationship:

- Source keys: `election_id`, `poll_id`, district, `source_id`, and `ct_id`.
- Weight fields: `population_weight`, `intersection_area_m2`, and
  `allocation_weight`.
- Quality fields: allocation method, area fallback, zero population,
  suppression counts/shares, excluded area, ancillary status, and
  votes-exceed-electors flag.

### `*_district_to_ct_crosswalk.csv`

One row per district-to-CT relationship used for no-geometry records. It
contains the same weight and suppression fields plus
`no_geometry_district_allocation_used`.

## 03 Allocation Audit

Records allocation execution, exclusions, and no-geometry preservation.

- `*_excluded_unallocated.csv`: poll/district/vote type, votes, electors,
  exclusion reason, and missing-vote flag.
- `excluded_unallocated_report.csv`: combined exclusions.
- `*_no_geometry_allocation_audit.csv`: source and allocated votes,
  difference, weight sum, party/candidate failures, method, and
  `fully_allocated`.
- `no_geometry_allocation_audit.csv`: combined no-geometry audit.
- `*_audit.csv`: election-level processing metrics.
- `interpolation_audit.csv`: combined processing metrics.

## 04 Validation

Checks preservation of official totals and provides the blocking map gates.

- `*_validation.csv`: source versus allocated totals by global, district, and
  source-row geography for total votes, electors, parties, and candidates.
- `validation_report.csv`: combined validation rows.
- `*_summary.json`: election row counts, methods, rates, and validation status.
- `validation_summary.json`: combined preservation, exclusion, no-geometry,
  and historical turnout-proximity status.
- `official_party_vote_reconciliation.csv`: official, normalized, and
  interpolated party totals globally and by district.
- `official_candidate_vote_reconciliation.csv`: official versus normalized
  candidate totals globally and by district.
- `official_result_reconciliation_summary.json`: official-result gate used by
  the map builder.

## 05 Context Audit

Stores diagnostic comparisons that explain geography, denominator, and
published-turnout differences but do not alter production weights.

- `*_turnout_comparison.csv`: election-specific official-elector and
  citizen-18+ rates.
- `turnout_comparison.csv`: combined turnout comparison.
- `turnout_reference_audit.csv`: reference rate, source URL, geography status,
  comparison margin, and interpretation.
- `geographic_coverage_audit.csv`: CT/DA coverage and boundary-sliver checks.
- `temporal_population_proxy_audit.csv`: 2021-to-election-year population
  sensitivities not applied to production.
- `geographic_temporal_audit_summary.json`: coverage and temporal decisions.
- `AUDIT_FINDINGS.md`: narrative audit findings.

## Regeneration

From `analysis/toronto_election_turnout/`:

```bash
python3 interpolation/scripts/run_interpolation.py
python3 interpolation/scripts/audit_geographic_temporal_coverage.py
python3 interpolation/scripts/audit_official_results.py
```

The map builder reads final CT tables from `processed/` and blocking validation
files from `04_validation/`.
