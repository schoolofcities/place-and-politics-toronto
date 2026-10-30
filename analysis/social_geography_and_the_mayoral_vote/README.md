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
- **Election results rebuilt from Zack's updated tract file (2026-10-30).** All
  election rows in `elections.parquet` and `turnout.parquet` now come from
  `tor_electoral_ct2021_pct_update.dta`, which Zack sent on 2026-10-30. It re-estimates
  the tract shares for 2003–2022 (citywide totals are essentially unchanged), fixes a
  2003 error where the City's poll-by-poll sheets, which list candidates in each ward's
  own vote order, had been read in one fixed order, and adds eligible voters for 2022
  and 2023. 1997, 2000, 2023 and 2026 are unchanged. The rows were rebuilt with the
  rules that reproduce the previous files exactly from the previous `.dta`: `share` is the tract share rounded to 4 places;
  `votes` is share × votes cast for 1997–2018 and the tract vote count from 2022;
  `votes_cast` and `eligible` are the tract totals. In `meta.json`, 2022's citywide
  figures and the 2022 and 2023 eligible totals were updated; the other citywide
  figures already matched the new file. The same file was used for the tract data of
  Parts 2–4 (`src/data/ctWithResults.geo.json`, `source-data/ctWithResults.csv`,
  `candidate_correlations.csv`, `candidate_links.json`). Part 5's
  `ctWithResults2023.geo.json` was not updated.

## Files added

- `wards-2000-2014.geojson` — the City's 44 wards used for the 2000–2014 elections
  (Toronto Open Data, "City Wards"), at 5 decimal places.
- `tract-wards-2000-2014.json` — each tract's ward among those 44, by the ward covering
  most of the tract.
- `city-boundary.geojson` — the city outline, dissolved from the current 25 wards
  (`src/data/wards.geo.json`).
