# Election Data

This folder contains the election-specific data batch for Toronto turnout by
polling division.

## Structure

```text
elections/
  raw/
    source_downloads/
  processed/
    turnout/
    candidate_details/
```

## Raw Sources

Files directly under `raw/` are source inputs used by the election builders:

- `toronto_2023_mayor.xlsx`: City of Toronto 2023 mayoral by-election result workbook.
- `toronto_2023_mayor_voter_statistics.xlsx`: City of Toronto voter-statistics workbook.
- `toronto_2023_subdivisions.geojson`: City of Toronto voting-subdivision geometry.
- `eo_2025_official_return.csv`: Elections Ontario 2025 Official Return.
- `ont_2025_ridings.geojson`: election-atlas Ontario riding source file.
- `fed_2025_ridings.geojson`: election-atlas federal riding source file.

`raw/source_downloads/` stores riding-by-riding source downloads:

- `provincial_polygons/`: election-atlas Ontario polling-division polygon GeoJSON files.
- `federal_polygons/`: election-atlas federal polling-division polygon GeoJSON files.
- `federal_csv/`: Elections Canada Format 1 CSV files retained for cross-checking.
- `federal_csv_format2/`: Elections Canada Format 2 CSV files used as the primary federal source.
- `eo_2025_candidate_summary.csv`: Elections Ontario Summary of Valid Votes
  Cast for Each Candidate, used to link provincial candidates to political
  interest codes.
- `eo_2025_political_interest_codes.csv`: Elections Ontario Political Interest
  Codes, used to expand provincial codes to full party names.

## Processed Outputs

`processed/turnout/` contains the optimized turnout CSV/GeoJSON files used by
the map viewer. Election level and year are encoded in filenames, not repeated
as columns.

`processed/candidate_details/` contains normalized candidate catalogs and sparse
poll-candidate vote tables. These join to the poll summary files through
`poll_id`; candidate identity and party affiliation join through
`candidate_id`.

The poll summary CSV/GeoJSON files in `processed/turnout/` also contain wide
party vote totals for convenient GIS and interpolation analysis. See
`processed/candidate_details/README.md` for the data model and join rules.

## Official Source Pages

- City of Toronto official by-election results: https://open.toronto.ca/dataset/elections-official-by-election-results/
- City of Toronto voting subdivisions: https://open.toronto.ca/dataset/elections-subdivisions/
- Elections Ontario results portal / official return: https://results.elections.on.ca/
- Elections Canada 45th general election official voting results: https://www.elections.ca/content.aspx?section=res&dir=rep/off/45gedata&document=byed&lang=e
- election-atlas Ontario map: https://www.election-atlas.ca/ont/
- election-atlas federal map: https://www.election-atlas.ca/fed/
