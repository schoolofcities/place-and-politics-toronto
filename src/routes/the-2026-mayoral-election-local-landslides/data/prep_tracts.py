"""Build tracts_progressive.json for the small-multiple maps (components/ProgressiveMaps.svelte).

Each progressive candidate's election-day share in each 2021 census tract, for the same ten
candidates as the where-the-votes-came-from chart, joined to the tract shapes used by Part 6
(source/tracts.geojson). The maps' city edge and former City of Toronto outline come from
former_municipalities.geo.json (the five-torontos page's), not from here.

The shares come from Zack Taylor's tor_electoral_ct2021_pct.dta (tor_elections_2023_2026/output).
Given its path, the needed columns are first saved to source/progressive_shares_ct.csv; without
one, that CSV is read.

usage: python prep_tracts.py [/path/to/tor_electoral_ct2021_pct.dta]
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"

# key, label, year, column in the .dta (as in plot_core_suburb_shares.R), and whether they won
CANDIDATES = [
    ("hall1997", "Hall", 1997, "pcthall1997", False),
    ("gomberg2000", "Gomberg", 2000, "pctgomberg2000", False),
    ("miller2003", "Miller", 2003, "pctmiller_david2003", True),
    ("miller2006", "Miller", 2006, "pctmiller_david2006", True),
    ("smitherman2010", "Smitherman", 2010, "pctsmitherman_george2010", False),
    ("chow2014", "Chow", 2014, "pctchow_olivia2014", False),
    ("keesmaat2018", "Keesmaat", 2018, "pctkeesmaat_jennifer2018", False),
    ("penalosa2022", "Peñalosa", 2022, "pctpenalosa_gil2022", False),
    ("chow2023", "Chow", 2023, "pctchow_olivia2023", True),
    ("chow2026", "Chow", 2026, "pctchow_olivia2026", True),
]
COLS = [c[3] for c in CANDIDATES]
CSV = SRC / "progressive_shares_ct.csv"

if len(sys.argv) > 1:
    pd.read_stata(sys.argv[1])[["ctuid2021"] + COLS].to_csv(CSV, index=False)
shares = pd.read_csv(CSV, dtype={"ctuid2021": str}).set_index("ctuid2021")

tracts = gpd.read_file(SRC / "tracts.geojson")
assert set(tracts.ct) == set(shares.index), "tracts and shares differ"


def rnd(x):
    return [rnd(v) for v in x] if isinstance(x[0], list) else [round(v, 5) for v in x]


def geometry(geom):
    g = geom.__geo_interface__
    return {"type": g["type"], "coordinates": rnd(json.loads(json.dumps(g["coordinates"])))}


def share(ct, col):  # null where the tract has no result (three tracts in 1997 and 2000)
    v = shares.at[ct, col]
    return None if pd.isna(v) else round(float(v), 3)


features = [{
    "type": "Feature",
    "properties": {"s": [share(r.ct, c) for c in COLS]},
    "geometry": geometry(r.geometry),
} for r in tracts.itertuples()]

out = {
    "candidates": [{"key": k, "label": l, "year": y, "won": w} for k, l, y, _, w in CANDIDATES],
    "tracts": {"type": "FeatureCollection", "features": features},
}
json.dump(out, open(HERE / "tracts_progressive.json", "w"), separators=(",", ":"))
print(len(features), "tracts; tracts_progressive.json", round((HERE / "tracts_progressive.json").stat().st_size / 1e6, 2), "MB")
