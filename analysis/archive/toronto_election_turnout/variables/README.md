# Engineered Variables Analysis

This module is reserved for scripts and notes that build cross-source modelling
variables after source data are collected.

## Structure

```text
variables/
  scripts/
  docs/
```

Scripts in this module should read canonical source outputs from the existing
research modules and write engineered feature tables under
`data/toronto_election_turnout/variables/processed/`.

Do not download new official source data from this module when the source
belongs more clearly to `census/`, `elections/`, or `accessibility/`.

## Raw Acquisition Scripts

`scripts/collect_non_census_raw_datasets.py` reproduces the Task 2 raw data
acquisition for Blocks 4-5. It downloads official/supervisor-recommended raw
files only, skips existing files, writes an inventory and QA report, and updates
the project variable registry.

The script must not be extended to calculate variables, aggregate records, or
run spatial joins. Put those operations in a later processing script.

## Modelling Variable Construction

`scripts/build_blocks_1_5_master.py` reproduces the Task 3 variable engineering
pipeline. It reads the Task 1 Census CT master, existing interpolated election
outputs, and Task 2 raw non-Census sources, then writes the modelling-ready
Blocks 1-5 CT database under:

```text
data/toronto_election_turnout/variables/processed/
```

The script also regenerates the variable dictionary, QA report, methodology
report, processing log, summary statistics, limitations report, and project
variable registry entries.

Important methodological choices:

- Accessibility is represented with Euclidean CT-centroid distance, nearest
  facility distance, facility counts within 1200 metres, and binary 1200 metre
  access flags.
- TTS 2022 variables are area-weighted from TTS zones to CT polygons.
- KSI collisions and development applications are point-in-polygon counts to
  2021 CTs, with per-1000 rates using Census population.
- 311 request intensity is estimated by aggregating official 2023-2025 311
  records by ward, allocating ward totals to CTs by CT-ward intersection-area
  share with the existing municipal ward-to-CT crosswalk, and dividing by
  Census population.
- Social housing is represented with the Census Profile subsidized-housing
  tenant-household share.
