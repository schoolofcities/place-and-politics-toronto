# Social geography and the mayoral vote — data

The data for `src/routes/social-geography-and-the-mayoral-vote/` comes from Zack
Taylor's Toronto elections mapper (https://github.com/zacktayloruwo/toronto-elections-mapper,
commit `7ab8d24`, 2026-09-21). `census.parquet`, `elections.parquet`, `turnout.parquet`,
`meta.json` and `tracts.geojson` were copied from its `docs/data/` folder, and the
scripts that built them are in its `prep/` folder.

## Changes made to Zack's data

- **Walk Score, Transit Score and Bike Score removed.** They're proprietary (Walk Score
  / Redfin) and not licensed for republication; the Statistics Canada proximity
  measures cover the same ground. 6 columns were removed from `census.parquet` and 3
  variables from `meta.json`.
- **Three labels corrected in `meta.json`:** "% Atheist" → "% No Religion" (the census
  category is no religious affiliation), "% Pentacostal" → "% Pentecostal", and
  "% Unemployed" → "% Unemployed (of pop. 15+)" (a share of everyone 15 and over, not
  the unemployment rate).
- **2003 election results corrected.** The City's 2003 poll-by-poll sheets list
  candidates in order of votes within each ward, and the source data read them by
  position as Miller, Tory, Hall, Nunziata. In wards with a different order the votes
  went to the wrong candidates (e.g. Miller and Tory swapped in the 21 wards Tory won).
  Each tract's votes were moved back to the right candidates using its ward's order in
  the City's official results (Toronto Open Data, "Elections – Official Results",
  2003); tracts spanning two wards were split by area, so those are estimates. 367
  tracts changed in `elections.parquet`, and the 2003 citywide figures in `meta.json`
  are now the official election-day counts. The same correction was made to the 2003
  columns used by earlier posts (`src/data/ctWithResults.geo.json`,
  `ctWithResults2023.geo.json`, `source-data/ctWithResults.csv`,
  `candidate_correlations.csv`, `candidate_links.json`). The error is still in Zack's
  source files, so rebuilt data from his repo would bring it back until it's fixed there.

## Files added

- `wards-2000-2014.geojson` — the City's 44 wards used for the 2000–2014 elections
  (Toronto Open Data, "City Wards"), at 5 decimal places.
- `tract-wards-2000-2014.json` — each tract's ward among those 44, by the ward covering
  most of the tract.
- `city-boundary.geojson` — the city outline, dissolved from the current 25 wards
  (`src/data/wards.geo.json`).
