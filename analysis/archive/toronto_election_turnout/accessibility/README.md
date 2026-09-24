# Polling Station Accessibility Analysis

This module audits whether polling station distance can be analyzed with the
current original polling-division election datasets.

The workflow uses the original election rows under
`data/toronto_election_turnout/elections/processed/`, not the interpolated
Census Tract outputs. The canonical row key is `poll_id`.

## Current Status

Municipal 2023 has verified polling station coordinates from Open Toronto's
`Elections Voting Locations` point dataset. The 1,445 official 2023 location
points match all 1,445 mapped municipal polling-subdivision rows.

Provincial 2025 and Federal 2025 do not yet have complete verified polling
station coordinate sources in the repository. Their mapped polling divisions
are retained in the accessibility audit outputs, but distance fields remain
blank and model-ready flags remain false until authoritative location data are
found.

For Provincial 2025, Elections Ontario's proposed voting-location CSV exports
were downloaded for the Toronto electoral districts and stored under
`data/toronto_election_turnout/accessibility/raw/provincial_2025/`. These files
provide location names and street addresses, but they do not exactly cover all
mapped 2025 polling rows by district and location name. The optional geocode
script can resolve those proposed-location addresses through Open Toronto's
official Address Points API, but those address-derived points should remain
flagged as provisional until the poll-to-location assignment is complete.

For Federal 2025, the workflow records the official source search in
`data/toronto_election_turnout/accessibility/processed/audits/federal_2025_polling_location_source_search_audit.csv`.
The raw Elections Canada result CSVs and official geography files do not
include polling-place building coordinates, so federal station-distance rows
remain excluded until a true poll-to-building source is found.

## Outputs

Outputs are written to:

```text
data/toronto_election_turnout/accessibility/
  processed/
    polling_locations/
    poll_to_location_links/
    poll_accessibility_metrics/
    turnout_distance_analysis/
    audits/
  map/
```

## Rebuild

From `analysis/toronto_election_turnout/`:

```bash
python3 accessibility/scripts/build_accessibility_audit.py
```

or:

```bash
npm run build:accessibility
```

The script uses EPSG:3347 for poll area, point, and distance calculations, then
writes map-ready GeoJSON in EPSG:4326.

To run the available turnout-vs-distance analysis:

```bash
npm run analyze:accessibility
```

This analysis currently includes complete Municipal 2023 station points and a
partial Provincial 2025 sample. Federal 2025 is excluded because no official
bulk station-location source has been found. The provincial sample is limited
to exact Elections Ontario proposed voting-location name matches that also
resolve to Open Toronto Address Points.

To refresh the optional Provincial 2025 proposed-location address geocode cache:

```bash
npm run fetch:accessibility-provincial-geocodes
```

That fetch script uses the already-downloaded Elections Ontario proposed voting
location CSVs and the official Open Toronto Address Points bulk table at
`data/toronto_election_turnout/accessibility/raw/open_toronto/address_points.csv`.
It parses proposed-location street addresses and matches locally by street
number and street name. It writes a raw cache at
`data/toronto_election_turnout/accessibility/raw/provincial_2025/eo_proposed_voting_locations_geocoded.csv`.

To probe Open Toronto Address Points directly with the Provincial 2025 official
return labels from `VotingPlaceAddressOrLocation`:

```bash
npm run fetch:accessibility-provincial-label-geocodes
```

This writes candidate matches to
`data/toronto_election_turnout/accessibility/raw/provincial_2025/eo_official_return_label_address_point_candidates.csv`.
These are candidate geocodes only. Strong matches can help triage missing
provincial locations, but weak/no-candidate rows remain unresolved and should
not be silently promoted to final station coordinates.
