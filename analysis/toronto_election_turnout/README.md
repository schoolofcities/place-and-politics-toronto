# Toronto Election Turnout Analysis

This folder mirrors the data split:

- `elections/`: scripts, notes, and viewer for polling-division election turnout.
- `census/`: scripts and notes for 2021 census inputs, reference CT files, and poll-to-CT interpolation readiness.
- `interpolation/`: population-weighted poll/district-to-CT allocation, audits,
  and preservation validation.

## Python Setup

The election builders require Python 3 plus `pandas` and `openpyxl`:

```bash
python -m pip install -r requirements.txt
```

## Run the Election Map

From this folder:

```bash
npm start
```

Open the printed local URL, usually:

```text
http://localhost:5173
```

No package installation is required. The viewer uses a small local Node server
and local Leaflet files. Map tiles come from OpenStreetMap, so the background
map needs internet access.

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

Run the census geography map:

```bash
npm run start:census
```

Open `http://127.0.0.1:5174`.

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

## Notes

Election QA notes live in:

- `elections/docs/`

Census/interpolation notes live in:

- `census/docs/`
