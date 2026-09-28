# Social geography and the mayoral vote — data

Data for the tool at
`src/routes/social-geography-and-the-mayoral-vote/`, ported from
Zack Taylor's prototype (https://github.com/zacktayloruwo/toronto-elections-mapper,
commit `7ab8d24`, 2026-09-21).

- `build_data.R` — Zack's script that builds the tool's data files (`census.parquet`,
  `elections.parquet`, `turnout.parquet`, `meta.json`, `tracts.geojson`). It reads
  election results, 2021 census tract boundaries and census tables from his own
  project folders, so it only runs on his machine; the files it produced are copied
  into the page's `data/` folder.
- `tor_varname_lookup.csv` — census variable names and labels used by the script.
- `build_wards_2000_2014.py` — converts the City's 44-ward boundaries (used for the
  2000–2014 elections; City of Toronto Open Data, "City Wards") to
  `wards-2000-2014.geojson` at 5 decimal places, and assigns each tract to the ward
  covering most of it (`tract-wards-2000-2014.json`).
- `build_city_boundary.py` — dissolves the current 25 wards (`src/data/wards.geo.json`)
  into the city outline, `city-boundary.geojson`.

Both Python scripts need `pyshp` and/or `shapely`, which aren't part of the site's
dependencies.

Changes from Zack's original script: Walk Score, Transit Score and Bike Score are
dropped right after the census data is loaded. They're proprietary (Walk Score /
Redfin) and not licensed for republication; the Statistics Canada proximity
measures (`pmi_prox_idx_*`, open data) cover the same ground. The data files in the
page folder were edited to match (6 columns removed from `census.parquet`, 3
variables from `meta.json`).

To update the tool for a new census or election, rerun `build_data.R` and copy the
new files into `src/routes/social-geography-and-the-mayoral-vote/data/`.
Variable labels, groups and the curated short list are set in the script
(`extra_labels`, `group_of`, `curated`); candidate names are in `full_names`.
