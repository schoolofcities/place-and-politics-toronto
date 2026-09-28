"""Build the City of Toronto outline drawn on the Toronto Mayoral Elections and
Social Geography page, by dissolving the 25 current wards (src/data/wards.geo.json).

Usage (needs shapely):
    python build_city_boundary.py

Writes city-boundary.geojson into the page's data/ folder, coordinates rounded to
5 decimal places (about 1 m).
"""

import json
from pathlib import Path

from shapely.geometry import mapping, shape, Polygon, MultiPolygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
WARDS = ROOT / "src/data/wards.geo.json"
OUT = ROOT / "src/routes/social-geography-and-the-mayoral-vote/data/city-boundary.geojson"
PRECISION = 5
# Neighbouring wards don't meet exactly once rounded, which would leave hairline
# slivers inside the dissolved outline; closing by ~2 m removes them.
CLOSE = 0.00002


def rounded_ring(ring):
    out = []
    for x, y in ring:
        pt = [round(x, PRECISION), round(y, PRECISION)]
        if not out or pt != out[-1]:
            out.append(pt)
    return out


def main():
    wards = [shape(f["geometry"]).buffer(0) for f in json.load(open(WARDS))["features"]]
    city = unary_union(wards).buffer(CLOSE, join_style=2).buffer(-CLOSE, join_style=2)

    polys = list(city.geoms) if isinstance(city, MultiPolygon) else [city]
    # Only the outer edge is drawn: the one hole left is a small enclosed patch of
    # water by the Ship Channel, not a gap in the city.
    polys = [Polygon(p.exterior) for p in polys]
    city = MultiPolygon(polys) if len(polys) > 1 else polys[0]

    geom = mapping(city)
    if geom["type"] == "Polygon":
        coords = [rounded_ring(r) for r in geom["coordinates"]]
    else:
        coords = [[rounded_ring(r) for r in poly] for poly in geom["coordinates"]]

    feature = {"type": "Feature", "properties": {"name": "City of Toronto"},
               "geometry": {"type": geom["type"], "coordinates": coords}}
    with open(OUT, "w") as f:
        json.dump({"type": "FeatureCollection", "features": [feature]}, f, separators=(",", ":"))

    parts = len(polys)
    holes = sum(len(p.interiors) for p in polys)
    print(f"{OUT.name}: {geom['type']}, {parts} part(s), {holes} hole(s), {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
