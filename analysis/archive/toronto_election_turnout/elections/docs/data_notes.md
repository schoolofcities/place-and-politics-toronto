# Data Notes

## Sources

- Toronto Open Data: 2023 mayoral by-election results, 2023 by-election voter statistics, and 2023 voting subdivisions.
- City of Toronto 2023 mayoral by-election candidate bulletin: special reporting subdivisions 96-99.
- Elections Ontario: 2025 Official Return from the Records CSV.
- Elections Canada: 45th general election poll-by-poll Format 2 CSV files, with Format 1 used only as a cross-check.
- election-atlas.ca: federal and Ontario polling-division polygon GeoJSON files.

## QA Summary

See `data/toronto_election_turnout/elections/processed/metadata/qa_summary.json` for generated counts.

Some official-result rows do not have polygon geometry in the map source, especially advance, mail-in, mobile, and combined/no-poll reporting categories. These rows are retained in the CSV and GeoJSON with blank/null geometry.

Each row has a normalized `vote_type` for filtering and aggregate checks: `election_day`, `advance`, `mail_in`, or `special`. `special` includes municipal long-term-care reporting buckets and Elections Canada special-voting-rules group rows.

Federal combined polls are flagged in `vote_in_other_division`; their elector counts are added to the target polling division for turnout calculation, following the requested method. The contributing combined-source polygons remain in the dataset and on the map, but their own `number_of_votes` and `proportion_of_turnout` are null because their votes are reported with the target division.

Provincial combined polls are also flagged in `vote_in_other_division`. Target rows and contributing rows both receive `source_note` text so the viewer can distinguish a true missing turnout value from a poll whose results are reported elsewhere.

Municipal subdivisions that exist in the geometry but are absent from the official mayoral result workbook are kept as polygons with null turnout and a concise `source_note`; they are not merged into another subdivision unless the source explicitly says so. Each note states the missing count and uses one join-status sentence.

Municipal workbook-only subdivisions 96, 97, 98, and 99 are retained as rows with null geometry. Toronto's voter-statistics workbook identifies these as special ward-level reporting buckets: subdivision 96 is long-term care, subdivision 97 is mail-in voting, and subdivisions 98 and 99 are advance vote. The workbook provides vote totals for these buckets; subdivision 96 also has elector counts, while mail-in and advance rows do not have separate elector denominators. Their notes state the special bucket, the vote count joined into that bucket, and that contributing ordinary subdivision numbers are not identified by the source.

Municipal electors use the official voter-statistics workbook's final `Total Eligible Electors`, after additions and deletions to the voters' list. This produces 1,947,242 eligible electors and 37.21% when the dataset's `Number Voted` numerator is used. Toronto's December 2023 supplementary report describes final turnout as 37%. The commonly cited 38.5% figure uses an earlier, smaller elector denominator and should not be substituted into subdivision-level rows.

Rows with votes but no supported elector count use `number_of_electors = null`, not `0`. For federal 2025, the affected rows are official `600+` advance-poll reporting buckets and some special-voting-rules group rows: Elections Canada Format 2 reports 0 electors for these reporting buckets, which is not a usable turnout denominator, and the atlas does not provide ordinary polling-division polygons for them. For provincial 2025, most official `ADV...` advance-vote rows are retained as no-geometry rows with null electors because Elections Ontario does not provide a separate polling-division denominator for those buckets. For municipal 2023, mail-in and advance special rows keep their vote totals, leave turnout null, and carry a `source_note`.

Rows where the official vote count exceeds the available elector denominator also keep their vote/elector counts but set `proportion_of_turnout = null`. This avoids displaying impossible turnout rates above 100%. After switching municipal electors to Toronto's voter-statistics workbook, the remaining source-denominator exceptions are 3 federal rows and 1 provincial advance-vote row; municipal has none.

Election level and year are not stored as repeated columns in the optimized datasets because those values are fixed by file.

Riding/ward names are no longer repeated in every polling-division row. Each dataset has a companion `_districts.csv` and `_districts.json` lookup with `electoral_district_number` and `electoral_district_name`; division rows join to that lookup by `electoral_district_number`. Municipal ward names have the repeated ward number removed in the lookup.

When reading the CSV files in pandas or R, load `electoral_district_number` and `polling_division_number` as text if you want to preserve leading zeros exactly as delivered. The GeoJSON and JSON lookup files already preserve those IDs as strings.

`polling_division_name` is source-dependent:

- Provincial 2025 is filled from Elections Ontario `VotingPlaceAddressOrLocation`.
- Federal 2025 does not have finer ordinary poll names in either Elections Canada Format 1 or Format 2. The official `Polling Division Name` field is mostly `Toronto` for ordinary polls, so the dataset now keeps that official value while preserving mobile and special-group labels where they appear. It should be read as the source label, not as a unique neighbourhood or polling-place name.
- Municipal 2023 ordinary polling-division names are filled from Toronto's voter-statistics workbook voting-place names. Special municipal rows 96-99 use descriptive reporting-bucket labels from the same workbook where available.

See `analysis/toronto_election_turnout/elections/docs/granularity_audit.md` for the detailed check of atlas dots, polygon coverage, no-geometry rows, and no-turnout polygons.

## Reference Comparison Dataset

Zack Taylor provided `tor_electoral_ct2021_pct.dta`, a Stata dataset of Toronto municipal election results from 1997 to 2023 apportioned to 2021 census tracts. The exact Stata file was not found as a checked file in this repository, but related census-tract outputs used by the Place and Politics site are present under `src/data/`.

This reference dataset is not a replacement for the polling-division turnout
files under each
`data/toronto_election_turnout/elections/processed/<election>/turnout/`
folder. It is election-day-only for 2023 and excludes advance-poll votes,
while this project retains advance, mail-in, and special reporting buckets
where the official source supports them.

See `analysis/toronto_election_turnout/census/docs/zack_taylor_ct_comparison.md` for the full comparison and official-source reconciliation.
