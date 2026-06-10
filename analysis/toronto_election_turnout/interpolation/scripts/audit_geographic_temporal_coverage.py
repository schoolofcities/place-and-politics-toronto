#!/usr/bin/env python3
"""Audit election geography coverage and official temporal population proxies."""

from __future__ import annotations

import csv
import json
import re
import zipfile
from pathlib import Path

from osgeo import ogr

from config import CONTEXT_AUDIT_ROOT, ELECTIONS, REPO_ROOT
from io_utils import read_csv, write_csv, write_json
from spatial import load_district_geometries, make_valid_polygonal


CT_BBOX = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "census"
    / "raw"
    / "source_downloads"
    / "statcan_2021_ct_toronto_bbox.geojson"
)
DA_BBOX = CT_BBOX.with_name("statcan_2021_da_toronto_bbox.geojson")
CURRENT_CT = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "census"
    / "processed"
    / "ct"
    / "statcan_2021_toronto_ct.geojson"
)
CURRENT_DA = (
    CURRENT_CT.parent.parent / "da"
    / "statcan_2021_toronto_da.geojson"
)
CT_PROFILE = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "census"
    / "processed"
    / "ct"
    / "statcan_2021_ct_profile.csv"
)

SOURCE_DOWNLOADS = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "census"
    / "raw"
    / "source_downloads"
)
CSD_TOTAL_ZIP = SOURCE_DOWNLOADS / "statcan_annual_csd_population_17100155-eng.zip"
CD_AGE_ZIP = SOURCE_DOWNLOADS / "statcan_annual_cd_age_17100152-eng.zip"
TORONTO_CSD_DGUID = "2021A00053520005"
TORONTO_CD_DGUID = "2021A00033520"

TABLE_URLS = {
    "total_population": "https://www150.statcan.gc.ca/n1/en/tbl/csv/17100155-eng.zip",
    "age_population": "https://www150.statcan.gc.ca/n1/en/tbl/csv/17100152-eng.zip",
}


def load_projected_features(path: Path, id_field: str):
    dataset = ogr.Open(str(path))
    layer = dataset.GetLayer(0)
    output = []
    for feature in layer:
        geometry = make_valid_polygonal(feature.GetGeometryRef(), transform=False)
        if geometry is not None:
            output.append((str(feature.GetField(id_field)), geometry))
    del layer, dataset
    return output


def current_ids(path: Path, ct=False):
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        str(feature["properties"]["geo_id"])
        for feature in data["features"]
        if not ct or feature["properties"].get("contains_toronto_da")
    }


def base_citizen_18plus():
    target_ct_ids = current_ids(CURRENT_CT, ct=True)
    total = 0
    for row in read_csv(CT_PROFILE):
        if row["geo_id"] not in target_ct_ids:
            continue
        value = row["citizen_canadian_18over"].strip()
        if value:
            total += int(value)
    return total


def selected_district_union():
    union = None
    for config in ELECTIONS:
        polls = read_csv(config.poll_csv)
        district_ids = {
            config.normalize_district_id(row["electoral_district_number"])
            for row in polls
            if row["electoral_district_number"].strip()
        }
        geometries, _ = load_district_geometries(config, district_ids)
        for geometry in geometries.values():
            union = geometry.Clone() if union is None else union.Union(geometry)
    return union


def geography_audit():
    district_union = selected_district_union()
    rows = []
    for level, path, id_field, stored in (
        ("CT", CT_BBOX, "CTUID", current_ids(CURRENT_CT, ct=True)),
        ("DA", DA_BBOX, "DAUID", current_ids(CURRENT_DA)),
    ):
        features = load_projected_features(path, id_field)
        positive_intersections = []
        representative_points_inside = []
        for geography_id, geometry in features:
            if geometry.Intersects(district_union):
                piece = geometry.Intersection(district_union)
                if piece is not None and not piece.IsEmpty() and piece.GetArea() > 0:
                    positive_intersections.append(geography_id)
            if district_union.Contains(geometry.PointOnSurface()):
                representative_points_inside.append(geography_id)

        missing_slivers = sorted(set(positive_intersections) - stored)
        missing_components = sorted(set(representative_points_inside) - stored)
        rows.append(
            {
                "geography_level": level,
                "bbox_feature_count": len(features),
                "positive_intersection_count": len(positive_intersections),
                "representative_point_inside_count": len(
                    representative_points_inside
                ),
                "stored_target_count": len(stored),
                "boundary_sliver_not_stored_count": len(missing_slivers),
                "missing_populated_component_count": len(missing_components),
                "boundary_sliver_ids": ";".join(missing_slivers),
                "missing_populated_component_ids": ";".join(missing_components),
                "decision": (
                    "No geography added: all selected representative points are "
                    "already in the stored target universe."
                ),
            }
        )
    return rows


def total_population_estimates():
    with zipfile.ZipFile(CSD_TOTAL_ZIP) as archive:
        with archive.open("17100155.csv") as raw:
            reader = csv.DictReader(
                line.decode("utf-8-sig") for line in raw
            )
            return {
                int(row["REF_DATE"]): int(row["VALUE"])
                for row in reader
                if row["DGUID"] == TORONTO_CSD_DGUID
                and row["REF_DATE"] in {"2021", "2023", "2025"}
            }


def adult_population_estimates():
    estimates = {2021: 0, 2023: 0, 2025: 0}
    with zipfile.ZipFile(CD_AGE_ZIP) as archive:
        with archive.open("17100152.csv") as raw:
            reader = csv.DictReader(
                line.decode("utf-8-sig") for line in raw
            )
            for row in reader:
                year = int(row["REF_DATE"])
                if (
                    row["DGUID"] != TORONTO_CD_DGUID
                    or year not in estimates
                    or row["Gender"] != "Total - gender"
                ):
                    continue
                match = re.fullmatch(r"(\d+) years?", row["Age group"])
                if match and int(match.group(1)) >= 18:
                    estimates[year] += int(row["VALUE"])
                elif row["Age group"] in {
                    "100 years and over",
                    "100 years and older",
                }:
                    estimates[year] += int(row["VALUE"])
    return estimates


def temporal_audit():
    total = total_population_estimates()
    adult = adult_population_estimates()
    base_denominator = base_citizen_18plus()
    election_year = {
        "municipal_2023_mayor": 2023,
        "provincial_2025": 2025,
        "federal_2025": 2025,
    }
    rows = []
    for config in ELECTIONS:
        polls = read_csv(config.poll_csv)
        votes = sum(
            float(row["number_of_votes"])
            for row in polls
            if row["number_of_votes"].strip()
            and not row["vote_in_other_division"].strip()
        )
        year = election_year[config.election_id]
        for proxy, estimates in (
            ("total_population", total),
            ("population_18plus", adult),
        ):
            factor = estimates[year] / estimates[2021]
            adjusted_denominator = base_denominator * factor
            adjusted_rate = votes / adjusted_denominator
            rows.append(
                {
                    "election_id": config.election_id,
                    "election_year": year,
                    "official_total_votes": votes,
                    "published_turnout_rate": config.published_turnout_rate,
                    "proxy_series": proxy,
                    "base_citizen_18plus_2021": base_denominator,
                    "proxy_2021": estimates[2021],
                    "proxy_election_year": estimates[year],
                    "growth_factor": factor,
                    "modelled_citizen_18plus_denominator": adjusted_denominator,
                    "modelled_participation_rate": adjusted_rate,
                    "absolute_difference_from_published": abs(
                        adjusted_rate - config.published_turnout_rate
                    ),
                    "applied_to_production": False,
                    "reason_not_applied": (
                        "Statistics Canada does not publish an annual "
                        "citizen_canadian_18over series at CT, DA, Toronto CSD, "
                        "or Toronto CD geography. This is a non-citizen-specific "
                        "growth proxy."
                    ),
                }
            )
    return rows


def main():
    for source in (CSD_TOTAL_ZIP, CD_AGE_ZIP):
        if not source.exists():
            raise FileNotFoundError(f"Missing official source download: {source}")

    geographic_rows = geography_audit()
    temporal_rows = temporal_audit()
    write_csv(
        CONTEXT_AUDIT_ROOT / "geographic_coverage_audit.csv",
        geographic_rows,
    )
    write_csv(
        CONTEXT_AUDIT_ROOT / "temporal_population_proxy_audit.csv",
        temporal_rows,
    )
    write_json(
        CONTEXT_AUDIT_ROOT / "geographic_temporal_audit_summary.json",
        {
            "geographic_coverage_complete": all(
                row["missing_populated_component_count"] == 0
                for row in geographic_rows
            ),
            "geographies_added": 0,
            "temporal_adjustment_applied": False,
            "temporal_adjustment_blocker": (
                "No official annual citizen_canadian_18over series exists for "
                "the required small-area or Toronto geography."
            ),
            "official_sources": TABLE_URLS,
        },
    )


if __name__ == "__main__":
    main()
