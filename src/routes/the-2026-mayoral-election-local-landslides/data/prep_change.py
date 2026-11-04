"""Build tracts_votes.json for the change-in-Chow's-share map (components/ChangeMap.svelte).

For each 2021 census tract, in the same order as the tracts in tracts_progressive.json (which also
has the tracts' shapes and Chow's 2023 and 2026 shares): [election-day votes cast in 2023, in 2026,
former municipality, ward number, ward name]. The municipality and ward (the one most of the tract
is in) are from source/tracts.geojson, Part 6's tracts. The vote counts are Zack Taylor's, from tor_electoral_ct2021_pct.dta
(tor_elections_2023_2026/output): given its path, the needed columns are first saved to
source/votes_ct.csv; without one, that CSV is read.

usage: python prep_change.py [/path/to/tor_electoral_ct2021_pct.dta]
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"
CSV = SRC / "votes_ct.csv"

if len(sys.argv) > 1:
    pd.read_stata(sys.argv[1])[["ctuid2021", "voted2023", "voted2026"]].to_csv(CSV, index=False)
votes = pd.read_csv(CSV, dtype={"ctuid2021": str}).set_index("ctuid2021")

tracts = gpd.read_file(SRC / "tracts.geojson")  # the order prep_tracts.py writes
assert set(tracts.ct) == set(votes.index), "tracts and votes differ"
out = [[int(votes.at[r.ct, "voted2023"]), int(votes.at[r.ct, "voted2026"]), r.oldcity, int(r.ward), r.wardname]
       for r in tracts.itertuples()]
json.dump(out, open(HERE / "tracts_votes.json", "w"), separators=(",", ":"))
print(len(out), "tracts;", sum(v[1] for v in out), "votes in 2026")
