# Toronto Election Turnout Data

This folder contains source and processed turnout datasets for Toronto election polling divisions:

- Municipal 2023 mayoral by-election
- Ontario provincial 2025 election
- Federal 2025 election

## Folders

- `raw/`: official source downloads and geometry files used by the build script.
- `reference/`: optional comparison/reference outputs that are useful for QA but are not primary turnout sources.
- `processed/`: final CSV and GeoJSON outputs used for analysis and mapping.

The processed rows preserve official missingness. Counts are not estimated or assigned to polygons unless a source supports that relationship. See `analysis/toronto_election_turnout/docs/` for audit notes and methodology caveats.

## Raw Source Inventory

Files directly under `raw/` are source inputs used by the builder. They are not calculated from this project's processed files:

- `toronto_2023_mayor.xlsx`: City of Toronto official 2023 mayoral by-election result workbook downloaded from Toronto Open Data.
- `toronto_2023_mayor_voter_statistics.xlsx`: City of Toronto official 2023 mayoral by-election voter-statistics workbook, used for municipal elector counts and voting-place labels.
- `toronto_2023_subdivisions.geojson`: City of Toronto official 2023 voting-subdivision geometry downloaded from Toronto Open Data.
- `eo_2025_official_return.csv`: Elections Ontario 2025 Official Return from the Records CSV.
- `ont_2025_ridings.geojson`: election-atlas Ontario riding-level geometry/results source file used to identify and cross-check 2025 Ontario ridings.
- `fed_2025_ridings.geojson`: election-atlas federal riding-level geometry/results source file used to identify and cross-check 2025 federal ridings.

Files under `raw/source_downloads/` are riding-by-riding source downloads:

- `provincial_polygons/`: election-atlas Ontario 2025 polling-division polygon GeoJSON files for Toronto ridings.
- `federal_polygons/`: election-atlas federal 2025 polling-division polygon GeoJSON files for Toronto ridings.
- `federal_csv/`: Elections Canada 45th general election poll-by-poll Format 1 CSV files, retained as a cross-check.
- `federal_csv_format2/`: Elections Canada 45th general election poll-by-poll Format 2 CSV files, used as the primary federal vote/elector source.

Official source pages:

- City of Toronto official by-election results: https://open.toronto.ca/dataset/elections-official-by-election-results/
- City of Toronto voting subdivisions: https://open.toronto.ca/dataset/elections-subdivisions/
- Elections Ontario results portal / official return: https://results.elections.on.ca/
- Elections Canada 45th general election official voting results: https://www.elections.ca/content.aspx?section=res&dir=rep/off/45gedata&document=byed&lang=e
- election-atlas Ontario map: https://www.election-atlas.ca/ont/
- election-atlas federal map: https://www.election-atlas.ca/fed/

## Reference Data

`reference/` is for comparison datasets and conversion outputs, not for the primary turnout build. The Zack Taylor-provided Stata dataset `tor_electoral_ct2021_pct.dta` was not found as a checked source file in this repository, but related Place and Politics census-tract outputs are present under `src/data/`.

The conversion script for Zack's file is:

```bash
python analysis/toronto_election_turnout/scripts/convert_zack_taylor_stata.py /path/to/tor_electoral_ct2021_pct.dta
```

The converter writes:

- `reference/zack_taylor_tor_electoral_ct2021_pct.csv`: all Stata rows and columns in CSV form.
- `reference/zack_taylor_tor_electoral_ct2021_pct_schema.csv`: column schema and read notes.
- `reference/zack_taylor_tor_electoral_ct2021_pct_metadata.txt`: short human-readable metadata.
- `reference/zack_taylor_tor_electoral_ct2021_pct_metadata.json`: machine-readable metadata.

Read `ctuid2021` as text/string, not numeric. This preserves the 2021 census tract identifier exactly.

See `analysis/toronto_election_turnout/docs/zack_taylor_ct_comparison.md` before comparing the Zack CT file to this project's polling-division turnout data. The CT file is election-day-only and census-tract-apportioned, while this project keeps all official reporting buckets where the source supports them.
