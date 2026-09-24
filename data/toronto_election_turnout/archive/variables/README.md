# Engineered Variables Data

This module is reserved for cross-source modelling variables that do not belong
cleanly to a single upstream source module.

Use this module when a variable combines Census, elections, accessibility,
municipal service, or other official data into a reusable CT-level or
ward-level feature.

## Structure

```text
variables/
  raw/
  processed/
  metadata/
  documentation/
```

## Expected Contents

- `raw/`: source extracts used only for variable engineering when they do not
  fit better inside an existing source module.
- `processed/`: engineered variable tables, preferably one row per stable
  geography such as 2021 CT.
- `metadata/`: variable dictionaries, source inventories, and QA summaries for
  engineered variables.
- `documentation/`: variable-specific methodology notes when the logic is too
  detailed for the module README.

## Naming Conventions

Prefer filenames that identify geography, source period, and variable family,
for example:

```text
toronto_ct_2021_municipal_service_variables.csv
toronto_ct_2021_demographic_housing_variables.csv
```

Use `ct_id` as the preferred CT join key for outputs that join to modelling and
interpolation products. Preserve official identifiers such as `DGUID`, `CTUID`,
and `DAUID` when they are available.

## Workflow Notes

Raw downloads remain immutable in their source modules whenever possible. This
module should hold engineered feature tables and cross-source metadata, not
duplicate large official downloads.

When a new variable is added here, update
`data/toronto_election_turnout/metadata/variable_registry.csv`.

## Task 2 Raw Non-Census Collection

Task 2 collected raw non-Census source files for Blocks 4-5 only. These files
are acquisition artifacts, not modelling variables.

Raw files are grouped by source:

```text
raw/
  transportation_tomorrow_survey_2022/
  toronto_open_data/
    311_service_requests_customer_initiated/
    active_affordable_and_social_housing_units/
    committee_of_adjustment_applications/
    development_applications/
    hostel_services_homeless_shelter_locations/
    ksi_collisions/
    library_branch_general_information/
    parks/
    parks_and_recreation_facilities/
    school_locations_all_types/
    shelter_profile_information/
```

The collection inventory is:

```text
metadata/non_census_raw_dataset_inventory.csv
```

The missing-data report is:

```text
metadata/non_census_missing_data_report.csv
```

The collection/QA report is:

```text
documentation/non_census_raw_collection_report.md
```

Known issue: the official Toronto Open Data `Committee of Adjustments
Applications since 2017` resource returned HTTP 500 during collection from its
CSV and JSON URLs. The package metadata and `Closed Applications 2023.csv`
were collected, and the failed current resource is recorded in the missing-data
report.

No per-capita measures, accessibility calculations, densities, aggregations, or
spatial joins were performed during Task 2.

## Task 3 Modelling Variables

Task 3 constructs the CT-level Blocks 1-5 modelling database from the collected
raw and processed inputs.

Primary outputs:

```text
processed/toronto_ct_blocks_1_5_modelling_master.csv
processed/toronto_ct_blocks_1_5_modelling_master.geojson
processed/toronto_ct_blocks_1_5_summary_statistics.csv
metadata/toronto_ct_blocks_1_5_variable_dictionary.csv
documentation/toronto_ct_blocks_1_5_methodology_report.md
documentation/toronto_ct_blocks_1_5_qa_report.md
documentation/toronto_ct_blocks_1_5_processing_log.md
documentation/toronto_ct_blocks_1_5_limitations.md
```

The master table has one row per 2021 Census Tract in the 585-CT
interpolation universe. It uses `ct_id` as the preferred join key and includes
Census variables, interpolated election outcomes and competitiveness measures,
TTS transit/no-car variables, accessibility proxies, road-safety exposure, and
development-application exposure.

Known limitations are documented in the QA and limitations reports. The 311
variable is an area-weighted ward-to-CT allocation estimate because the
collected official raw files do not include CT-compatible point coordinates.
Social housing is represented with the 2021 Census Profile measure `% of
tenant households in subsidized housing`, converted to a 0-1 share; its
denominator is tenant households, not all households.
