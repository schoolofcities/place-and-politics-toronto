"""Build the 2000-2014 (44-ward) boundaries used by the Toronto Mayoral Elections
and Social Geography page, and assign each census tract to one of those wards.

Source: City of Toronto Open Data, "City Wards" dataset
(https://open.toronto.ca/dataset/city-wards/), resource
"44-ward-model-may-2010-wgs84-latitude-longitude" (a zipped shapefile). These are
the wards used for the 2000, 2003, 2006, 2010 and 2014 elections.

Usage (needs pyshp and shapely):
    python build_wards_2000_2014.py path/to/icitw_wgs84.shp

Writes, into the page's data/ folder:
  - wards-2000-2014.geojson: the 44 wards, coordinates rounded to 5 decimal
    places (about 1 m), with properties {num, name}
  - tract-wards-2000-2014.json: {census tract id: ward number}, the ward holding
    the largest share of each tract's area
"""

import json
import re
import sys
from pathlib import Path

import shapefile  # pyshp
from shapely.geometry import shape

PAGE_DATA = Path(__file__).resolve().parents[2] / "src/routes/social-geography-and-the-mayoral-vote/data"
PRECISION = 5


def rounded_ring(ring):
    """Round a ring's coordinates, dropping points that round onto the previous one."""
    out = []
    for x, y in ring:
        pt = [round(x, PRECISION), round(y, PRECISION)]
        if not out or pt != out[-1]:
            out.append(pt)
    return out


def rounded_geometry(geom):
    if geom["type"] == "Polygon":
        return {"type": "Polygon", "coordinates": [rounded_ring(r) for r in geom["coordinates"]]}
    if geom["type"] == "MultiPolygon":
        return {"type": "MultiPolygon",
                "coordinates": [[rounded_ring(r) for r in poly] for poly in geom["coordinates"]]}
    raise ValueError(geom["type"])


def main(shp_path):
    reader = shapefile.Reader(shp_path)
    features = []
    for sr in reader.shapeRecords():
        rec = sr.record.as_dict()
        num = int(rec["SCODE_NAME"])
        # "Scarborough-Rouge River (41)" -> "Scarborough-Rouge River"
        name = re.sub(r"\s*\(\d+\)\s*$", "", rec["NAME"]).strip()
        features.append({
            "type": "Feature",
            "properties": {"num": num, "name": name},
            "geometry": rounded_geometry(sr.shape.__geo_interface__),
        })
    features.sort(key=lambda f: f["properties"]["num"])
    assert len(features) == 44, len(features)

    wards_path = PAGE_DATA / "wards-2000-2014.geojson"
    with open(wards_path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, separators=(",", ":"))

    # Each tract goes to the ward covering most of its area
    tracts = json.load(open(PAGE_DATA / "tracts.geojson"))["features"]
    wards = [(f["properties"]["num"], shape(f["geometry"]).buffer(0)) for f in features]
    assignment = {}
    for t in tracts:
        g = shape(t["geometry"]).buffer(0)
        overlaps = [(g.intersection(w).area, num) for num, w in wards if g.intersects(w)]
        assignment[t["properties"]["ct"]] = max(overlaps)[1]
    assert len(assignment) == len(tracts)

    with open(PAGE_DATA / "tract-wards-2000-2014.json", "w") as f:
        json.dump(assignment, f, separators=(",", ":"), sort_keys=True)

    print(f"{len(features)} wards -> {wards_path.name} ({wards_path.stat().st_size / 1024:.0f} KB); "
          f"{len(assignment)} tracts assigned")


if __name__ == "__main__":
    main(sys.argv[1])
