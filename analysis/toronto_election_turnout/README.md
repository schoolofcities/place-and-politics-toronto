# Toronto Election Turnout Analysis

This folder mirrors the data split:

- `elections/`: scripts, notes, and viewer for polling-division election turnout.
- `census/`: scripts, notes, and viewer for 2021 census inputs, reference CT
  files, and interpolation readiness.
- `interpolation/`: population-weighted poll/district-to-CT allocation, audits,
  preservation validation, and the CT election viewer.

```text
analysis/toronto_election_turnout/
  elections/
    scripts/
    docs/
    viewer/
  census/
    scripts/
    docs/
    viewer/
  interpolation/
    *.py
    viewer/
    README.md
    MUNICIPAL_PARTY_AFFILIATION_AUDIT.md
  package.json
  requirements.txt
```

## Python Setup

The election builders require Python 3 plus `pandas` and `openpyxl`:

```bash
python -m pip install -r requirements.txt
```

## Available Maps

From this folder:

### 1. Polling-Division Election Map

Displays the original municipal, provincial, and federal election records at
their available polling-division geography. This is not the interpolated CT
map.

```bash
npm start
```

Open:

```text
http://127.0.0.1:5173
```

### 2. Census Geography Map

Displays the 2021 census CT, DA, and related census geography/profile inputs
used by the analysis.

```bash
npm run start:census
```

Open:

```text
http://127.0.0.1:5174
```

### 3. Interpolated Census-Tract Election Map

This is the latest map. It displays the population-weighted municipal,
provincial, and federal CT estimates, citizen-18+ participation, official
turnout comparisons, party-share maps, and mayoral candidate-share maps.

Rebuild its map-ready datasets when interpolation outputs change:

```bash
npm run build:interpolation-map
```

Run the viewer:

```bash
npm run start:interpolation
```

Open:

```text
http://127.0.0.1:5180
```

All three viewers can run at the same time because they use separate ports.
No package installation is required. They use small local Node servers and
local Leaflet files. Map tiles come from OpenStreetMap, so the background maps
need internet access.

## Rebuild Election Outputs

```bash
python elections/scripts/build_election_datasets.py
```

Outputs go to:

- `../../data/toronto_election_turnout/elections/processed/turnout/`
- `../../data/toronto_election_turnout/elections/processed/candidate_details/`

The wrapper first rebuilds turnout data, then adds poll IDs, party totals,
candidate catalogs, and sparse poll-candidate vote bridges. The two component
scripts can still be run separately when debugging.

## Rebuild Census/Profile Outputs

```bash
python census/scripts/extract_statcan_census_profile_citizens_18plus.py
```

Outputs go to:

- `../../data/toronto_election_turnout/census/processed/profile_2021/`

Build the census geography crosswalk and viewer data:

```bash
python census/scripts/build_census_geography_viewer_data.py
```

To convert the Zack Taylor Stata file:

```bash
python census/scripts/convert_zack_taylor_stata.py /path/to/tor_electoral_ct2021_pct.dta
```

Outputs go to:

- `../../data/toronto_election_turnout/census/reference/zack_taylor_ct2021/`

Build the poll-to-CT interpolation:

```bash
cd interpolation
python3 run_interpolation.py
```

Outputs go to:

- `../../data/toronto_election_turnout/interpolation/processed/`

After rebuilding interpolation outputs, regenerate the map-ready GeoJSON:

```bash
cd ..
npm run build:interpolation-map
```

## Notes

Election QA notes live in:

- `elections/docs/`

Census/interpolation notes live in:

- `census/docs/`
- `interpolation/README.md`
- `interpolation/MUNICIPAL_PARTY_AFFILIATION_AUDIT.md`

Generated audit findings and output dictionaries live under:

- `../../data/toronto_election_turnout/interpolation/processed/`
