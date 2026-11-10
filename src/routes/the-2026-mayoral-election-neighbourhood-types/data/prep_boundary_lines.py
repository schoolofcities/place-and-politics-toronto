"""Build the boundary lines the lead maps (components/NeighbourhoodMaps.svelte) can draw over the tracts:

    municipality_lines.geojson  between the six former municipalities (new_votes_municipalities.geojson)
    ward_lines.geojson          between the 25 wards (the series' src/data/wards.geo.json)

Drawing each area's own outline would put every shared boundary down twice, and lay a line over the
city's edge too, so the lines came out uneven; these keep only the edges two areas share, each once.
The municipality shapes were simplified separately, so neighbours' edges are close but don't coincide
exactly (the wards' nearly all do). Each shared edge is therefore taken from one side only: the
stretch of the first area's outline within TOLERANCE of the second.

usage: python prep_boundary_lines.py
"""

import json
from itertools import combinations
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import linemerge, unary_union

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TOLERANCE = 40 / 111_000  # degrees, about 40 m: how far apart two neighbours' versions of an edge can be


def rnd(x):
    return [rnd(v) for v in x] if isinstance(x[0], (list, tuple)) else [round(v, 5) for v in x]


def shared_lines(source, out, simplify=0.0):
    """the edges the areas in `source` share, each once, written to `out` as one (multi)line feature"""
    shapes = [shape(f["geometry"]) for f in json.load(open(source))["features"]]
    shared = []
    for a, b in combinations(shapes, 2):
        edge = a.boundary.intersection(b.buffer(TOLERANCE))
        lines = [g for g in getattr(edge, "geoms", [edge]) if g.geom_type in ("LineString", "MultiLineString")]
        if lines and unary_union(lines).length > 2 * TOLERANCE:  # corners where two only touch drop out
            shared.append(unary_union(lines))
    merged = linemerge(unary_union(shared))
    if simplify:
        merged = merged.simplify(simplify, preserve_topology=True)
    geom = mapping(merged)
    geom = {"type": geom["type"], "coordinates": rnd(json.loads(json.dumps(geom["coordinates"])))}
    json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": geom}]},
              open(out, "w"), separators=(",", ":"))
    parts = len(geom["coordinates"]) if geom["type"] == "MultiLineString" else 1
    print(f"{out.name}: {len(shared)} shared boundaries, {parts} line(s), {out.stat().st_size / 1e3:.1f} KB")


shared_lines(HERE / "new_votes_municipalities.geojson", HERE / "municipality_lines.geojson")
# the wards are drawn in detail in the source; about 10 m is far finer than the maps show
shared_lines(REPO / "src/data/wards.geo.json", HERE / "ward_lines.geojson", simplify=10 / 111_000)
