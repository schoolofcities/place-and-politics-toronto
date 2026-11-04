"""Build polls_2026.json for the poll map (components/PollMap.svelte).

Joins Chow's, Bradford's and everyone else's election-day votes in each 2026 voting subdivision
(source/resultsbyvsd_2026.csv) to the subdivision polygons (source/vsd_2026.gpkg), simplifies
the shapes for the web and adds the 25 wards. Both source files are from Zack Taylor's
tor_elections_2023_2026 workflow; the 97-99 ward-level advance and mail-in counts have no
polygon and are not in them.

usage: python prep_polls.py
"""

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"

res = pd.read_csv(SRC / "resultsbyvsd_2026.csv", dtype={"vsdid": str})
res = res[res.type == "eday"]
votes = pd.DataFrame({
    "vsdid": res.vsdid,
    "c": (res.pctchow_olivia2026 * res.voted2026).round().astype(int),
    "b": (res.pctbradford_brad2026 * res.voted2026).round().astype(int),
    "total": res.voted2026.astype(int),
})
votes["o"] = votes.total - votes.c - votes.b

shapes = gpd.read_file(SRC / "vsd_2026.gpkg")
joined = shapes[["vsdid", "ward", "sub", "geometry"]].merge(votes, on="vsdid", how="outer", indicator=True)
assert (joined._merge == "both").all(), joined[joined._merge != "both"][["vsdid", "_merge"]]
joined = gpd.GeoDataFrame(joined, geometry="geometry", crs=shapes.crs)

# simplify in metres, then round to 5 decimals (about a metre)
joined = joined.to_crs(3857)
joined["geometry"] = joined.geometry.simplify(4, preserve_topology=True)
joined = joined.to_crs(4326)


def rnd(x):
    return [rnd(v) for v in x] if isinstance(x[0], list) else [round(v, 5) for v in x]


def feature(geom, props):
    g = geom.__geo_interface__
    return {"type": "Feature", "properties": props,
            "geometry": {"type": g["type"], "coordinates": rnd(json.loads(json.dumps(g["coordinates"])))}}


polls = [feature(r.geometry, {"w": int(r.ward), "s": int(r.sub), "c": int(r.c), "b": int(r.b), "o": int(r.o)})
         for r in joined.itertuples()]

wards = gpd.read_file(SRC / "wards.geo.json").to_crs(3857)
wards["geometry"] = wards.geometry.simplify(10, preserve_topology=True)
wards = wards.to_crs(4326)
ward_features = [feature(r.geometry, {"num": int(r.num), "name": r.name}) for r in wards.itertuples()]

out = {
    "polls": {"type": "FeatureCollection", "features": polls},
    "wards": {"type": "FeatureCollection", "features": ward_features},
}
json.dump(out, open(HERE / "polls_2026.json", "w"), separators=(",", ":"))

print(len(polls), "polls;", {k: int(votes[k].sum()) for k in ("c", "b", "o", "total")})
print("polls_2026.json", round((HERE / "polls_2026.json").stat().st_size / 1e6, 2), "MB")
