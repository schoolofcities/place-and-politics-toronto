# Granularity and Mapping Audit

## Atlas Small Circles

The small circles on election-atlas are not a smaller polling geography and are not turnout-rate marks.

For provincial and federal maps, the atlas loads two files after a riding is clicked:

- `polygons/.../<riding>.geojson`: polling-division polygons.
- `centroids/.../<riding>.geojson`: one point centroid for each same polling-division polygon.

The atlas dot-style JavaScript sets the dot radius from `sqrt(TOTALVOTES)`, and color/opacity from candidate or party vote share fields such as `PCT1`, `PCPCT`, `LIBPCT`, and similar fields. So the dots encode vote volume and winning-party/candidate strength, not turnout. Turnout requires electors, which the atlas polygon/centroid files do not consistently include.

The viewer now has an optional `Show vote-size dots` overlay. These dots are explicitly labelled as vote volume, not turnout.

## Mapping Integrity

The updated data builder includes every source polygon available from the geometry source. If an official turnout/elector row cannot be matched to that polygon, the polygon is still retained and shown with:

- `number_of_votes`: atlas total votes, when present.
- `number_of_electors`: null.
- `proportion_of_turnout`: null.
- `source_note`: explanation that no matching official electors row was found.

Official rows that do not have a polygon are retained in the CSV/GeoJSON with null geometry, but cannot be drawn on the map without making up geometry.

Combined/reporting-elsewhere areas are also retained as their own polygons. When a source row says its results are reported with another division, `vote_in_other_division` stores the target division and `source_note` explains the relationship. These polygons intentionally show as no-turnout areas when their own votes are not separately reported; this avoids confusing "reported elsewhere" with a real zero-turnout result.

## Current QA Counts

Municipal 2023:

- Final rows/features: 1,545.
- Features with geometry: 1,445.
- Geometry subdivisions without an official vote result: 94. These remain mapped but `number_of_votes`, `number_of_electors`, and turnout are null.
- Workbook vote buckets without subdivision polygons: 100, corresponding to ward-level special subdivisions 96-99. These are retained as null-geometry rows with notes, but cannot be mapped as ordinary polygons.
- Electors now come from Toronto's official 2023 by-election voter-statistics workbook, not from the subdivision geometry `VOTER_COUNT` field. This aligns the municipal aggregate with the government's final revised voters' list: 724,638 voted and 1,947,242 total eligible electors. Toronto's December 2023 supplementary report describes final turnout as 37%; the commonly cited 38.5% figure uses an earlier, smaller elector denominator.
- Examples checked: Ward 15 subdivision 16 and Ward 10 subdivision 4 exist in the 2023 subdivision geometry file, but are absent from the official 2023 mayoral workbook columns.
- Subdivision 96 is the ward-level long-term-care reporting bucket, subdivision 97 is mail-in voting, and subdivisions 98/99 are advance vote. The source does not identify contributing ordinary subdivision numbers for these buckets.

Provincial 2025:

- Final features: 1,532.
- Features with geometry: 1,388.
- Official ordinary/special rows without geometry: 17.
- Official advance-vote rows without geometry: 127. These `ADV...` rows are retained with their vote counts and null electors because Elections Ontario does not provide a separate polling-division denominator for advance-vote buckets.
- Source polygons without matching official elector rows: 0 after aggregating official suffix polls like `001A` and `001B` to atlas polygon `001`.
- Official suffix poll groups aggregated: 29.
- Examples checked: Don Valley East 001 is built from official 001A/001B, and Scarborough Centre 015 is built from official 015A/015B.

Federal 2025:

- Final features: 5,069.
- Features with geometry: 4,273.
- Official rows with suffixes such as `2A` and `2B` are aggregated back to the base atlas polygon, such as `2`.
- Official numbered rows without geometry: 748, mostly special/mobile/advance-like or combined rows.
- Official special-voting-rules group rows without ordinary poll numbers: 48. These are retained as no-geometry `special` rows.
- Source polygons without matching official elector rows: 0 after preserving official numeric hyphen polls such as `459-1` and `459-2`, and after aggregating lettered source subpolls such as `2A`/`2B` to the atlas polygon where the atlas only has `2`.
- Federal combined-source rows keep their polygons, keep their elector contribution, point to the target in `vote_in_other_division`, and leave `number_of_votes`/`proportion_of_turnout` null because those votes are reported with the target division.

## Area Size Versus Elector Count

Polling-division land area is not expected to scale with votes/electors. Some small polygons represent dense apartment buildings or campuses; some large polygons include parks, industrial land, ravines, roads, or low-density areas.

Example checked in Scarborough North:

- Poll 409: 254 votes, 680 electors, about 0.020 km2, voting place `Ridgeford Apartments`.
- Poll 017: 1,036 votes, 3,028 electors, about 3.49 km2, voting place `Anson S. Taylor Jr. Public School`.

The count difference is therefore plausible and supported by Elections Ontario official rows rather than a mapping mismatch.

## Integrity Rule

No turnout rate is calculated unless both votes and electors are supported by source data. Where only votes are available from the atlas geometry source, turnout remains null.

Rows with vote totals but no usable elector denominator are treated as unknown electors, not zero electors. This matters most for federal `600+` advance-poll reporting buckets: Elections Canada Format 2 records vote totals and reports `0` electors for these administrative buckets, and the atlas does not provide ordinary polling-division polygons for them. Those rows are retained for auditability but cannot produce a turnout rate or map polygon.

Turnout rates above 100% are not emitted. The municipal source workbook includes a ward-total row at the bottom of each sheet; the builder excludes that row from subdivision vote sums. Any remaining row where source votes exceed source electors keeps the original counts but leaves `proportion_of_turnout` null with a `source_note`, because the denominator is not coherent for division-level turnout.

## Optimized Schema Notes

Election level and election year are encoded in the output file names and are no longer repeated as per-row fields.

Riding/ward names are normalized into companion district lookup files instead of repeated on every polling-division row. Join on `electoral_district_number` to recover `electoral_district_name`; the map viewer performs this join when rendering filters and popups.

Municipal ward names are normalized from labels like `City Ward 1 Etobicoke North` to `Etobicoke North` in the lookup. The municipal sources do not provide separate human-readable polling subdivision names; the numeric subdivision remains the stable identifier.

Municipal notes are intentionally plain-language and division-specific. Ordinary missing-data rows use one concise join-status sentence; special reporting buckets state join-in and join-out separately.

Provincial `polling_division_name` is the official Elections Ontario voting-place location for that poll. When official suffix polls are aggregated to a single atlas polygon, multiple distinct locations are joined with `; `.

Federal ordinary poll names are not available at finer detail in the checked Elections Canada Format 1 or Format 2 files: ordinary rows are labeled `Toronto`. The optimized dataset keeps that official source label, but it should not be interpreted as a unique neighbourhood or polling-place name.
