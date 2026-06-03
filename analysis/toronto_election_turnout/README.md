# Toronto Election Turnout Analysis

This folder contains the reproducible scripts, methodology notes, and local map viewer for the Toronto election turnout datasets stored under:

```text
data/toronto_election_turnout/
```

The datasets cover:

- Municipal 2023 mayoral by-election
- Ontario provincial 2025 election
- Federal 2025 election

## Run the map

Open `analysis/toronto_election_turnout/` in VS Code, then run:

```bash
npm start
```

Open the printed local URL, usually:

```text
http://localhost:5173
```

No package installation is required. The viewer uses a small local Node server and local Leaflet files. Map tiles come from OpenStreetMap, so the background map needs internet access.

## Folder Structure

- `viewer/`: interactive local map application
- `scripts/`: reproducible data-building script
- `docs/`: notes and QA information
- `../../data/toronto_election_turnout/raw/`: source downloads used to build the datasets
- `../../data/toronto_election_turnout/processed/`: final CSV and GeoJSON files

## Data Fields

The final files include:

- `number_of_votes`
- `number_of_electors`
- `proportion_of_turnout`
- `vote_type`
- `geometry`
- `vote_in_other_division`

Identifier fields for riding/ward number and polling division are also included. Election level and year are encoded in the file names, so they are not repeated as columns.

Riding/ward names are normalized into separate lookup files to avoid repeating the same name thousands of times:

- `toronto_municipal_2023_mayor_turnout_subdivisions_districts.csv/json`
- `toronto_provincial_2025_turnout_poll_divisions_districts.csv/json`
- `toronto_federal_2025_turnout_poll_divisions_districts.csv/json`

Join each division row to its lookup row using `electoral_district_number`. The viewer does this automatically.

`vote_type` is normalized for filtering and audit: `election_day`, `advance`, `mail_in`, or `special`.

`polling_division_name` is populated from the official source field. Provincial 2025 uses the Elections Ontario voting-place location. Federal 2025 uses Elections Canada Format 2; ordinary polls are usually labelled `Toronto`, while mobile and special-group labels are preserved where they appear. Municipal 2023 uses Toronto's voter-statistics voting-place names where available.

Rows that are missing turnout or whose results are reported with another division are kept rather than removed. Check `vote_in_other_division` and `source_note` to see whether a white/no-turnout polygon is genuinely missing source data or contributes to another reporting division.

Municipal `source_note` values are division-specific plain-language notes. They indicate whether votes/electors are present, whether the source identifies any joined division, and how many votes/electors were joined into special reporting buckets.

The map sidebar also includes a visible `Data notes` disclosure. It summarizes important source mismatches and methodology choices for the selected election level, including the municipal 2023 difference between the often-cited 38.5% turnout figure and Toronto's final revised voters' list.

## Audit Notes

The `docs/` folder has four focused notes:

- `data_notes.md`: compact source, schema, missingness, and field-use notes.
- `official_totals_audit.md`: reconciliation of built totals against official source totals.
- `granularity_audit.md`: mapping/granularity checks, including atlas dots, no-geometry rows, and polygon coverage.
- `zack_taylor_ct_comparison.md`: comparison with the Zack Taylor-provided 2021 census-tract Stata dataset and explanation of why it differs from the all-method polling-division files.

In short: the atlas circles are vote-size centroid markers for the same polling divisions, not finer turnout geography. The viewer includes all source polygons and leaves turnout blank where electors cannot be supported by source data.

To rebuild the processed data from the raw published sources, run:

```bash
python scripts/build_turnout_geojson.py
```

To convert Zack Taylor's Stata census-tract dataset to CSV, run:

```bash
python scripts/convert_zack_taylor_stata.py /path/to/tor_electoral_ct2021_pct.dta
```
