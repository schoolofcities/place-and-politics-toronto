#!/usr/bin/env python3
"""Build Toronto census geography crosswalks and map-ready GeoJSON."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "census"
RAW = DATA_ROOT / "raw"
PROFILE = DATA_ROOT / "processed" / "profile_2021"
ADA_REFERENCE = DATA_ROOT / "reference" / "ada_2021"
OUT = DATA_ROOT / "processed" / "geography_2021"


def run(*args):
    subprocess.run(args, check=True)


def read_csv(path, key):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return {row[key]: row for row in csv.DictReader(f)}


def nullable_number(value, integer=False):
    text = str(value or "").strip()
    if not text:
        return None
    number = float(text)
    return int(number) if integer else number


def export_layer(source, target, layer):
    run(
        "ogr2ogr",
        "-f",
        "GeoJSON",
        str(target),
        str(source),
        layer,
        "-t_srs",
        "EPSG:4326",
        "-simplify",
        "1",
    )


def spatial_crosswalk(work, sql, name):
    output_dir = work / name
    run(
        "ogr2ogr",
        "-f",
        "CSV",
        str(output_dir),
        str(work / "overlay.gpkg"),
        "-dialect",
        "SQLITE",
        "-sql",
        sql,
    )
    return next(output_dir.glob("*.csv"))


def main():
    if not shutil.which("ogr2ogr"):
        raise RuntimeError("GDAL ogr2ogr is required to build census geography files")

    OUT.mkdir(parents=True, exist_ok=True)
    da_profile = read_csv(PROFILE / "statcan_2021_da_citizens_18plus.csv", "geo_id")
    ct_profile = read_csv(PROFILE / "statcan_2021_ct_citizens_18plus.csv", "geo_id")

    ada_profile = {}
    with (ADA_REFERENCE / "toronto_ada_2021_profile.csv").open(
        newline="", encoding="utf-8-sig"
    ) as f:
        for row in csv.DictReader(f):
            if row["CHARACTERISTIC_CODE"] == "citizen_canadian_18over":
                ada_profile[row["GEO_NAME"]] = row

    with tempfile.TemporaryDirectory(prefix="toronto-census-") as tmp:
        work = Path(tmp)
        overlay = work / "overlay.gpkg"
        run(
            "ogr2ogr",
            "-f",
            "GPKG",
            str(overlay),
            str(RAW / "statcan_2021_da_toronto_clipped.gpkg"),
            "-nln",
            "da",
        )
        run(
            "ogr2ogr",
            "-f",
            "GPKG",
            "-update",
            "-append",
            str(overlay),
            str(RAW / "statcan_2021_ct_toronto_clipped.gpkg"),
            "-nln",
            "ct",
        )
        run(
            "ogr2ogr",
            "-f",
            "GPKG",
            "-update",
            "-append",
            str(overlay),
            str(ADA_REFERENCE / "toronto_ada_2021_boundaries.gpkg"),
            "-nln",
            "ada",
        )

        da_links_path = spatial_crosswalk(
            work,
            """
            SELECT da.DAUID AS da_id, ct.CTUID AS ct_id, ada.ADAUID AS ada_id
            FROM da
            JOIN ct ON ST_Contains(ct.geom, ST_PointOnSurface(da.geom))
            JOIN ada ON ST_Contains(ada.geom, ST_PointOnSurface(da.geom))
            """,
            "da_links",
        )
        ct_links_path = spatial_crosswalk(
            work,
            """
            SELECT ct.CTUID AS ct_id, ada.ADAUID AS ada_id
            FROM ct
            JOIN ada ON ST_Contains(ada.geom, ST_PointOnSurface(ct.geom))
            """,
            "ct_links",
        )

        da_links = read_csv(da_links_path, "da_id")
        ct_links = read_csv(ct_links_path, "ct_id")
        missing_da_links = sorted(set(da_profile) - set(da_links))
        if missing_da_links:
            raise ValueError(f"Toronto DAs without CT/ADA link: {missing_da_links}")

        crosswalk_rows = []
        for da_id in sorted(da_profile):
            link = da_links[da_id]
            crosswalk_rows.append(
                {"da_id": da_id, "ct_id": link["ct_id"], "ada_id": link["ada_id"]}
            )
        with (OUT / "statcan_2021_toronto_da_ct_ada_crosswalk.csv").open(
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["da_id", "ct_id", "ada_id"])
            writer.writeheader()
            writer.writerows(crosswalk_rows)
        linked_ct_ids = {row["ct_id"] for row in crosswalk_rows}

        suppressed_rows = []
        for da_id, profile_row in sorted(da_profile.items()):
            if profile_row["value_status"] != "published":
                suppressed_rows.append(
                    {
                        "da_id": da_id,
                        "ct_id": da_links[da_id]["ct_id"],
                        "ada_id": da_links[da_id]["ada_id"],
                        "data_quality_flag": profile_row["data_quality_flag"],
                        "tnr_sf": profile_row["tnr_sf"],
                        "tnr_lf": profile_row["tnr_lf"],
                        "value_status": profile_row["value_status"],
                        "source_note": profile_row["source_note"],
                    }
                )
        with (OUT / "statcan_2021_toronto_da_suppressed_values.csv").open(
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "da_id",
                    "ct_id",
                    "ada_id",
                    "data_quality_flag",
                    "tnr_sf",
                    "tnr_lf",
                    "value_status",
                    "source_note",
                ],
            )
            writer.writeheader()
            writer.writerows(suppressed_rows)

        raw_da = work / "da.geojson"
        raw_ct = work / "ct.geojson"
        raw_ada = work / "ada.geojson"
        export_layer(RAW / "statcan_2021_da_toronto_clipped.gpkg", raw_da, "dissemination_areas_2021_toronto")
        export_layer(RAW / "statcan_2021_ct_toronto_clipped.gpkg", raw_ct, "census_tracts_2021_toronto")
        export_layer(ADA_REFERENCE / "toronto_ada_2021_boundaries.gpkg", raw_ada, "toronto-ada")

        da_aggregates = defaultdict(
            lambda: {"component_da_count": 0, "missing_da_count": 0, "citizens": 0}
        )
        ct_counts = defaultdict(set)
        for da_id, profile_row in da_profile.items():
            ada_id = da_links[da_id]["ada_id"]
            ct_id = da_links[da_id]["ct_id"]
            aggregate = da_aggregates[ada_id]
            aggregate["component_da_count"] += 1
            ct_counts[ada_id].add(ct_id)
            value = nullable_number(profile_row["citizen_canadian_18over"], integer=True)
            if value is None:
                aggregate["missing_da_count"] += 1
            else:
                aggregate["citizens"] += value

        def update_da(feature):
            p = feature["properties"]
            da_id = str(p["DAUID"])
            if da_id not in da_profile:
                return False
            profile_row = da_profile[da_id]
            p.update(
                {
                    "geo_level": "DA",
                    "geo_id": da_id,
                    "ct_id": da_links[da_id]["ct_id"],
                    "ada_id": da_links[da_id]["ada_id"],
                    "citizen_canadian_18over": nullable_number(
                        profile_row["citizen_canadian_18over"], integer=True
                    ),
                    "rate_total": nullable_number(profile_row["rate_total"]),
                    "data_quality_flag": profile_row["data_quality_flag"],
                    "value_status": profile_row["value_status"],
                    "source_note": profile_row["source_note"],
                }
            )
            return True

        def update_ct(feature):
            p = feature["properties"]
            ct_id = str(p["CTUID"])
            if ct_id not in ct_profile:
                return False
            profile_row = ct_profile[ct_id]
            linked_to_toronto_da = ct_id in linked_ct_ids
            profile_value = nullable_number(
                profile_row["citizen_canadian_18over"], integer=True
            )
            p.update(
                {
                    "geo_level": "CT",
                    "geo_id": ct_id,
                    "ada_id": ct_links.get(ct_id, {}).get("ada_id"),
                    "contains_toronto_da": linked_to_toronto_da,
                    "citizen_canadian_18over": (
                        profile_value if linked_to_toronto_da else None
                    ),
                    "profile_citizen_canadian_18over": profile_value,
                    "rate_total": nullable_number(profile_row["rate_total"]),
                    "data_quality_flag": profile_row["data_quality_flag"],
                    "value_status": (
                        profile_row["value_status"]
                        if linked_to_toronto_da
                        else "boundary_intersection_not_toronto_da_universe"
                    ),
                    "source_note": (
                        profile_row["source_note"]
                        if linked_to_toronto_da
                        else "CT geometry intersects the Toronto boundary, but no "
                        "verified Toronto DA maps to this CT. Its full-CT profile "
                        "count is retained separately and excluded from Toronto totals."
                    ),
                }
            )
            return True

        def update_ada(feature):
            p = feature["properties"]
            ada_id = str(p["ADAUID"])
            aggregate = da_aggregates[ada_id]
            official = ada_profile.get(ada_id, {})
            p.update(
                {
                    "geo_level": "ADA",
                    "geo_id": ada_id,
                    "component_ct_count": len(ct_counts[ada_id]),
                    "component_da_count": aggregate["component_da_count"],
                    "component_da_missing_count": aggregate["missing_da_count"],
                    "da_sum_citizen_canadian_18over": aggregate["citizens"],
                    "ada_profile_citizen_canadian_18over": nullable_number(
                        official.get("C1_COUNT_TOTAL"), integer=True
                    ),
                    "ada_profile_rate_total": nullable_number(
                        official.get("C10_RATE_TOTAL")
                    ),
                }
            )
            return True

        outputs = [
            (
                raw_da,
                OUT / "statcan_2021_toronto_da.geojson",
                update_da,
            ),
            (
                raw_ct,
                OUT / "statcan_2021_toronto_ct.geojson",
                update_ct,
            ),
            (
                raw_ada,
                OUT / "statcan_2021_toronto_ada.geojson",
                update_ada,
            ),
        ]
        output_counts = {}
        for source, target, updater in outputs:
            with source.open(encoding="utf-8") as f:
                geojson = json.load(f)
            geojson["features"] = [
                feature for feature in geojson["features"] if updater(feature)
            ]
            output_counts[target.stem] = len(geojson["features"])
            with target.open("w", encoding="utf-8") as f:
                json.dump(geojson, f, ensure_ascii=False, separators=(",", ":"))

    audit = {
        "crs_source": "EPSG:3347",
        "map_crs": "EPSG:4326",
        "da_count": len(da_profile),
        "ct_count": len(ct_profile),
        "toronto_linked_ct_count": len(linked_ct_ids),
        "boundary_only_ct_count": len(ct_profile) - len(linked_ct_ids),
        "ada_count": len(ada_profile),
        "da_suppressed_confidentiality_count": sum(
            row["value_status"] == "suppressed_confidentiality"
            for row in da_profile.values()
        ),
        "da_to_ada_relationship": (
            "Toronto ADAs are formed from CT building units. DAs respect CT "
            "boundaries, so the published crosswalk follows DA to CT to ADA."
        ),
        "da_per_ada_min": min(v["component_da_count"] for v in da_aggregates.values()),
        "da_per_ada_max": max(v["component_da_count"] for v in da_aggregates.values()),
        "da_per_ada_mean": sum(
            v["component_da_count"] for v in da_aggregates.values()
        )
        / len(da_aggregates),
        "outputs": output_counts,
    }
    with (OUT / "statcan_2021_toronto_geography_audit.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(audit, f, indent=2)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
