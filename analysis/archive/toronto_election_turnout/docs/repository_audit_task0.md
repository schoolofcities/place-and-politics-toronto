# Task 0 Repository Audit

Date: 2026-07-09

Scope: `data/` and `analysis/` only.

No new datasets were collected and no existing datasets were processed during
this audit.

## Executive Summary

The repository is already organized around research modules rather than a
global raw/processed hierarchy. That structure remains appropriate for the next
phase of variable collection because the existing pipelines have clear module
ownership:

- `census`: 2021 StatCan geography, profile variables, DA/CT/ADA crosswalks.
- `elections`: municipal, provincial, and federal election inputs and
  normalized polling-division outputs.
- `interpolation`: poll/district-to-CT allocation and validation.
- `accessibility`: polling location linkage, distance metrics, and
  turnout-distance analysis.
- `modelling`: CT-level modelling tables and model outputs.

The main missing piece was a dedicated cross-source `variables` module and a
project-level variable registry. Those were initialized. No existing files were
relocated because current scripts encode the existing paths and broad movement
would create risk without a matching clarity gain.

## Structural Summary

### `data/clustering_neighbourhoods/`

Purpose: separate exploratory neighbourhood clustering outputs.

Contents:

- `explore/`: sensitivity and riding-residual comparison outputs.
- `figures/`: clustering figures.
- `profiles/`: cluster profiles and tract GeoPackages.

Relationship: appears separate from `toronto_election_turnout`; no direct
pipeline dependency was found in the audited election-turnout modules.

Assessment: location is acceptable as a separate root data module. It should
not be merged into the turnout modules unless reused by the turnout project.

### `analysis/clustering_neighbourhoods/`

Purpose: exploratory clustering notebook.

Contents: `explore_neighbourhood_clusters.ipynb`.

Relationship: matches `data/clustering_neighbourhoods/`.

Assessment: active status unknown from the turnout pipeline; leave unchanged.

### `data/toronto_election_turnout/`

Purpose: primary project data root.

Contents:

- `elections/`
- `census/`
- `interpolation/`
- `accessibility/`
- `modelling/`
- `variables/` newly initialized
- `metadata/` newly initialized

Relationship: mirrors `analysis/toronto_election_turnout/`.

Assessment: appropriate module-based organization. The new `variables/` module
fills the cross-source feature-engineering gap.

### `analysis/toronto_election_turnout/`

Purpose: primary project analysis root.

Contents:

- module scripts and docs for `elections`, `census`, `interpolation`,
  `accessibility`, `modelling`, and newly initialized `variables`.
- local browser viewers for election, census, and interpolation maps.
- project-level `package.json` and `requirements.txt`.

Relationship: scripts write to the corresponding data modules.

Assessment: appropriate. Top-level README now includes the new variable and
modelling modules.

## Pipeline Audit

### Census Processing

Analysis location: `analysis/toronto_election_turnout/census/`

Data location: `data/toronto_election_turnout/census/`

Inputs:

- `raw/statcan_2021_ct_toronto_clipped.gpkg`
- `raw/statcan_2021_da_toronto_clipped.gpkg`
- `raw/statcan_2021_toronto_csd.gpkg`
- `raw/source_downloads/statcan_2021_ct_profile.zip`
- `raw/source_downloads/statcan_2021_ct_profile_ci.zip`
- `raw/source_downloads/statcan_2021_age_single_year_98100023-eng.zip`
- `raw/source_downloads/statcan_2021_ct_age_single_year_98100024-eng.zip`
- `reference/ada_2021/`
- `reference/zack_taylor_ct2021/`

Scripts:

- `extract_statcan_census_profile_citizens_18plus.py`
- `extract_statcan_population_18plus.py`
- `build_census_profile_tables.py`
- `build_census_geography_viewer_data.py`
- `convert_zack_taylor_stata.py`
- census audit scripts for adult population, suppression, and residuals.

Outputs:

- `processed/da/statcan_2021_da_profile.csv`
- `processed/ct/statcan_2021_ct_profile.csv`
- `processed/ada/statcan_2021_ada_profile.csv`
- `processed/da/statcan_2021_toronto_da.geojson`
- `processed/ct/statcan_2021_toronto_ct.geojson`
- `processed/ada/statcan_2021_toronto_ada.geojson`
- `processed/crosswalks/statcan_2021_toronto_da_ct_ada_crosswalk.csv`
- `processed/variable_dictionary.csv`

Intermediate files:

- `processed/da/intermediate/`
- `processed/ct/intermediate/`

Audits:

- `processed/audits/geography/`
- `processed/audits/profile_extraction/`
- `processed/audits/reconciliation/`

Dependencies:

- Python standard library and pandas-style CSV workflow.
- GDAL/`ogr2ogr` for geometry conversion in the viewer-data builder.

Assessment: well separated. Audit outputs are separated under
`processed/audits/`, though they remain inside `processed/` because they are
generated products. That is acceptable and already documented.

### Election Processing

Analysis location: `analysis/toronto_election_turnout/elections/`

Data location: `data/toronto_election_turnout/elections/`

Inputs:

- City of Toronto 2023 mayoral workbooks and subdivision geometry.
- Elections Ontario 2025 official return and candidate/party lookup files.
- Elections Canada 2025 poll-by-poll CSVs.
- election-atlas provincial/federal polling polygons and riding geometry.

Scripts:

- `build_election_datasets.py`
- `build_turnout_geojson.py`
- `build_candidate_party_votes.py`
- `validate_normalized_election_data.py`

Outputs:

- `processed/<election>/turnout/*.csv`
- `processed/<election>/turnout/*.geojson`
- `processed/<election>/candidate_details/*_candidates.csv`
- `processed/<election>/candidate_details/*_poll_candidate_votes.csv`
- `processed/metadata/normalized_election_results_metadata.json`
- `processed/metadata/qa_summary.json`

Intermediate files:

- Source-download folders under `raw/source_downloads/`.
- No separate processed intermediate hierarchy; the election builder writes
  normalized outputs directly by election.

Audits/docs:

- `analysis/toronto_election_turnout/elections/docs/`

Dependencies:

- Python 3, `pandas`, `openpyxl`.
- Local GeoJSON inputs.

Assessment: clear. `processed/metadata/` is module-specific, not a duplicate of
the new project-level `metadata/`.

### Spatial Interpolation

Analysis location: `analysis/toronto_election_turnout/interpolation/`

Data location: `data/toronto_election_turnout/interpolation/`

Inputs:

- Processed election turnout/candidate tables.
- Processed CT and DA census geometries.
- Census DA-level `citizen_canadian_18over` weight.
- District boundary files for municipal wards, provincial ridings, and federal
  ridings.

Scripts:

- `run_interpolation.py`
- `workflow.py`
- `config.py`
- `spatial.py`
- `io_utils.py`
- `audit_geographic_temporal_coverage.py`
- `audit_official_results.py`
- `build_map_data.py`

Outputs:

- `processed/*_ct_estimated_results.csv`
- `processed/*_ct_candidate_estimated_votes.csv`
- `map/*_ct_map.geojson`
- `map/map_build_summary.json`

Intermediate files:

- `processed/intermediate/01_input_audit/`
- `processed/intermediate/02_spatial_crosswalks/`
- `processed/intermediate/03_allocation_audit/`
- `processed/intermediate/04_validation/`
- `processed/intermediate/05_context_audit/`

Dependencies:

- Python 3.
- GDAL `osgeo` bindings.
- Node/npm scripts for map generation and viewers.

Assessment: strong and reproducible. Numbered intermediate stages are useful
and should be preserved.

### Accessibility Analysis

Analysis location: `analysis/toronto_election_turnout/accessibility/`

Data location: `data/toronto_election_turnout/accessibility/`

Inputs:

- Processed election polling rows.
- Municipal 2023 Open Toronto voting locations.
- Provincial 2025 Elections Ontario proposed voting-location CSVs.
- Open Toronto Address Points local raw cache.
- Provincial official-return label candidate geocode cache.

Scripts:

- `build_accessibility_audit.py`
- `analyze_turnout_distance.py`
- `fetch_provincial_address_point_geocodes.py`
- `fetch_provincial_return_label_geocodes.py`

Outputs:

- `processed/polling_locations/`
- `processed/poll_to_location_links/`
- `processed/poll_accessibility_metrics/`
- `processed/turnout_distance_analysis/`
- `processed/audits/`
- `map/*_poll_accessibility_map.geojson`

Intermediate files:

- Raw provincial proposed-location exports.
- Geocode candidate/cache files under `raw/provincial_2025/`.

Dependencies:

- Python 3.
- GeoJSON/CSV handling.
- Optional Open Toronto Address Points cache for local geocoding.

Assessment: clear. The README documents that municipal is complete, provincial
is partial, and federal station coordinates are unavailable.

### Turnout-Distance Analysis

Analysis location: `analysis/toronto_election_turnout/accessibility/`

Data location: `data/toronto_election_turnout/accessibility/processed/turnout_distance_analysis/`

Inputs:

- `processed/poll_accessibility_metrics/*_poll_accessibility_metrics.csv`

Script:

- `analyze_turnout_distance.py`

Outputs:

- analysis rows, summaries, model coefficients, model summaries, and figures.

Dependencies:

- Python 3.

Assessment: correctly nested under accessibility because it depends on
polling-location linkage and distance fields.

### Modelling

Analysis location: `analysis/toronto_election_turnout/modelling/`

Data location: `data/toronto_election_turnout/modelling/`

Inputs:

- Processed CT Census profile and raw CT Census Profile ZIP.
- Interpolated CT election outputs.
- Existing derived service/election variables inside the modelling builder.

Scripts:

- `build_ct_modelling_master.py`
- `run_block_models.py`
- `write_block_model_report.py`

Outputs:

- `processed/toronto_ct_modelling_master.csv`
- `processed/toronto_ct_modelling_curated.csv`
- `processed/toronto_ct_modelling_master.geojson`
- `processed/toronto_ct_modelling_curated.geojson`
- `processed/variable_inventory.csv`
- `processed/missing_variable_checklist.csv`
- `processed/models/*`

Dependencies:

- Python 3.
- Census and interpolation outputs.

Assessment: useful current analysis module. Future cross-source variable
engineering should happen in `variables/` first, then modelling should consume
those stable variable tables.

## Organization Evaluation

Raw, processed, intermediate, reference, audit, script, figure, and
documentation separations are generally clear.

Good patterns to keep:

- Source modules own official raw downloads.
- `analysis/<module>/scripts/` writes to `data/<module>/`.
- Final interpolation outputs are distinct from numbered intermediate stages.
- Census reference datasets are separate from raw and processed official data.
- Accessibility keeps raw source caches away from processed metrics.

Areas improved in this task:

- Added `data/toronto_election_turnout/variables/` for future cross-source
  engineered variables.
- Added `analysis/toronto_election_turnout/variables/` for future variable
  scripts and notes.
- Added `data/toronto_election_turnout/metadata/variable_registry.csv` as the
  project-level modelling-variable registry.
- Updated top-level project READMEs to include `accessibility`, `variables`,
  `modelling`, and `metadata`.

Areas intentionally not changed:

- Existing audit outputs were not moved out of `processed/` because scripts
  currently write to those paths and the module READMEs already explain the
  distinction.
- Existing `modelling/` outputs were not moved into `variables/`; those files
  are active modelling products and are currently untracked in the worktree.
- Existing source downloads were not reorganized because filenames and paths
  are script dependencies.

## Existing Data Asset Inventory

### Census

Exists.

Locations:

- `data/toronto_election_turnout/census/raw/`
- `data/toronto_election_turnout/census/raw/source_downloads/`
- `data/toronto_election_turnout/census/processed/`

Completeness/currentness:

- 2021 CT, DA, ADA profiles and geometry are present.
- Processed CT profile has 622 CT rows; interpolation target uses 585 CTs with
  Toronto DA representative-point coverage.
- Current to 2021 Census. Not a 2026 or later update.

### Elections

Exists.

Locations:

- `data/toronto_election_turnout/elections/raw/`
- `data/toronto_election_turnout/elections/raw/source_downloads/`
- `data/toronto_election_turnout/elections/processed/`

Completeness/currentness:

- Municipal 2023, Provincial 2025, and Federal 2025 processed polling outputs
  exist.
- Processed turnout rows: municipal 1,545, provincial 1,532, federal 5,069.
- Current to the stated election years.

### Polling Locations

Exists.

Locations:

- `data/toronto_election_turnout/accessibility/raw/municipal_2023_mayor/`
- `data/toronto_election_turnout/accessibility/raw/provincial_2025/`
- `data/toronto_election_turnout/accessibility/processed/polling_locations/`
- `data/toronto_election_turnout/accessibility/processed/poll_to_location_links/`

Completeness/currentness:

- Municipal 2023 has 1,445 polling locations and complete mapped-poll linkage.
- Provincial 2025 has partial accepted coordinates; current processed polling
  locations file has 1,338 rows.
- Federal 2025 polling location file has zero rows; no bulk official station
  coordinate source is present.

### Dissemination Areas

Exists.

Locations:

- `data/toronto_election_turnout/census/raw/statcan_2021_da_toronto_clipped.gpkg`
- `data/toronto_election_turnout/census/processed/da/`

Completeness/currentness:

- 3,743 DA profile rows and GeoJSON features.
- Current to 2021 Census.

### Census Tracts

Exists.

Locations:

- `data/toronto_election_turnout/census/raw/statcan_2021_ct_toronto_clipped.gpkg`
- `data/toronto_election_turnout/census/processed/ct/`
- `data/toronto_election_turnout/interpolation/processed/`
- `data/toronto_election_turnout/modelling/processed/`

Completeness/currentness:

- 622 processed CT profile rows.
- 585 CTs used as the modelling/interpolation universe.
- Current to 2021 Census.

### Accessibility

Exists.

Locations:

- `data/toronto_election_turnout/accessibility/`

Completeness/currentness:

- Municipal complete.
- Provincial partial.
- Federal incomplete for station coordinates.

### Transportation

Partially exists.

Locations:

- Census commute-mode variables in
  `data/toronto_election_turnout/modelling/processed/toronto_ct_modelling_master.csv`.
- Accessibility/poll-distance outputs under `data/toronto_election_turnout/accessibility/`.

Completeness/currentness:

- Commute-mode variables are available from 2021 Census-derived modelling data.
- No separate Transportation Tomorrow Survey, GTFS, vehicle-availability, road
  network, or transit-access dataset was found.

### Libraries

Not found as a dedicated official dataset.

Existing proxy/status:

- `service_library_access_15m_walk_transit` exists as a column in the curated
  modelling table, but appears unpopulated based on the missing-variable
  checklist and absence of a raw library dataset.

### Parks

Not found as a dedicated official dataset.

Existing proxy/status:

- `service_park_access` exists as a curated modelling column but no parks raw
  dataset was found.

### Community Centres

Not found as a dedicated official dataset.

Existing proxy/status:

- `service_community_centre_access` exists as a curated modelling column but no
  community-centre raw dataset was found.

### Shelters

Not found as a dedicated official dataset.

Existing proxy/status:

- `service_shelter_service_proximity` exists as a curated modelling column.
- Census housing proxies exist in the modelling master, but no shelter-location
  official dataset was found.

### Development Applications

Not found.

Existing proxy/status:

- `service_development_applications_per_capita` exists as a curated modelling
  column but no source dataset was found.

### 311 Requests

Not found.

Existing proxy/status:

- `service_311_requests_per_capita` exists as a curated modelling column but no
  source dataset was found.

### Road Safety

Not found as a dedicated collision/exposure dataset.

Existing proxy/status:

- `service_road_safety_exposure` exists as a curated modelling column.
- No KSI/collision/traffic-exposure source dataset was found.

## Merge-Key Documentation

Preferred keys:

- CT-level outputs: `ct_id`.
- DA-level outputs: `da_id`.
- ADA-level outputs: `ada_id`.
- Census official identifiers: `DGUID`, `CTUID`, `DAUID` where present in
  source GeoJSON.
- Election/accessibility polling rows: `poll_id`.
- Candidate tables: `candidate_id`; candidate vote bridge joins on
  `poll_id` + `candidate_id`.
- Polling location tables: `polling_location_id`.
- Election-level partitioning: `election_id`.
- District/riding/ward partitioning: `electoral_district_number`.

Observed key behavior:

- `census/processed/crosswalks/statcan_2021_toronto_da_ct_ada_crosswalk.csv`
  has 3,743 unique `da_id` values, 585 unique `ct_id` values, and 279 unique
  `ada_id` values.
- Processed CT profile files use `geo_id`; interpolation and modelling use
  normalized `ct_id`.
- Municipal turnout has 1,545 unique `poll_id` values.
- Provincial turnout has 1,532 unique `poll_id` values.
- Federal turnout has 5,069 unique `poll_id` values.
- `polling_division_number` is not globally unique; it repeats across
  districts and elections. Use `poll_id`.
- Municipal accessibility metrics have 1,445 unique `poll_id` and 1,445 unique
  `polling_location_id` values.
- Municipal candidate vote bridge has 28,998 rows, 1,451 unique `poll_id`
  values, and 102 unique `candidate_id` values.
- CT modelling curated output has 585 rows with unique `ct_id`.

Type conventions:

- Treat `ct_id` as text because CT IDs include decimals and trailing zeros.
- Treat `da_id`, `ada_id`, `poll_id`, `candidate_id`, and
  `polling_location_id` as text.
- Treat `electoral_district_number` as text to preserve leading zeros in
  provincial IDs.

## Updated Structure

New folders:

```text
data/toronto_election_turnout/metadata/
data/toronto_election_turnout/variables/
data/toronto_election_turnout/variables/raw/
data/toronto_election_turnout/variables/processed/
data/toronto_election_turnout/variables/metadata/
data/toronto_election_turnout/variables/documentation/
analysis/toronto_election_turnout/docs/
analysis/toronto_election_turnout/variables/
analysis/toronto_election_turnout/variables/scripts/
analysis/toronto_election_turnout/variables/docs/
```

New documentation:

```text
data/toronto_election_turnout/metadata/README.md
data/toronto_election_turnout/variables/README.md
analysis/toronto_election_turnout/variables/README.md
analysis/toronto_election_turnout/docs/repository_audit_task0.md
```

New registry:

```text
data/toronto_election_turnout/metadata/variable_registry.csv
```

Relocated files: none.

Unchanged existing files: all existing datasets, scripts, figures, notebooks,
and module documentation were left in place. Only top-level project README maps
were updated to expose the new modules.

## Recommendations

1. Keep the module-based layout. It matches the research workflow and existing
   scripts.
2. Use `variables/` for future cross-source Blocks 1-5 engineered features.
3. Keep source downloads inside source-owning modules whenever possible.
4. Update `metadata/variable_registry.csv` before or during each future
   collection task.
5. Avoid moving existing audit files until scripts are refactored together;
   current audit paths are documented and active.
6. For service variables, avoid duplicate downloads by first checking
   `modelling/processed/missing_variable_checklist.csv` and the new registry.
7. Standardize new CT-level outputs on `ct_id` as text.
8. Preserve official IDs (`DGUID`, `CTUID`, `DAUID`) in engineered outputs for
   traceability.
9. Do not use `polling_division_number` alone as a merge key.
10. Consider moving future model-independent variable dictionaries from
    `modelling/processed/variable_inventory.csv` into `variables/metadata/`
    only after the modelling scripts are updated to consume that location.

## Remaining Concerns

- `analysis/toronto_election_turnout/package.json`, the modelling module, and
  several large source/data files were already modified or untracked before
  this task. They were not reverted or rewritten.
- Some desired Block 5 service variables are represented as curated modelling
  columns but do not yet have corresponding official raw datasets in the
  repository.
- Federal 2025 polling-location coordinates remain unavailable.
- Provincial 2025 polling-location linkage is useful but partial.
- The current modelling builder writes some README/docs as part of its output;
  future refactoring should avoid overwriting manual documentation unexpectedly.
