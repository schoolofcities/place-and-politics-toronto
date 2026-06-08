#!/usr/bin/env python3
"""Build compact CT GeoJSON files for the interpolation Leaflet viewer."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from config import CT_PATH, ELECTIONS, OUTPUT_ROOT, REPO_ROOT
from io_utils import read_csv, write_json


MAP_DATA_ROOT = (
    REPO_ROOT
    / "data"
    / "toronto_election_turnout"
    / "interpolation"
    / "map"
)
TOP_CANDIDATE_COUNT = 5


def number(value):
    text = "" if value is None else str(value).strip()
    return float(text) if text else None


def require_audit_pass():
    validation = json.loads(
        (OUTPUT_ROOT / "validation_summary.json").read_text(encoding="utf-8")
    )
    reconciliation = json.loads(
        (
            OUTPUT_ROOT / "official_result_reconciliation_summary.json"
        ).read_text(encoding="utf-8")
    )
    blockers = {
        "primary_vote_validation": validation[
            "all_primary_vote_validations_pass"
        ],
        "no_geometry_allocation": (
            validation["no_geometry_allocation_failure_count"] == 0
        ),
        "vote_bearing_exclusions": (
            validation["vote_bearing_exclusion_count"] == 0
        ),
        "official_result_reconciliation": reconciliation[
            "official_source_match"
        ],
    }
    failed = [name for name, passed in blockers.items() if not passed]
    if failed:
        raise RuntimeError(
            "Map build blocked by failed audit gates: " + ", ".join(failed)
        )
    return blockers


def target_geometries():
    collection = json.loads(CT_PATH.read_text(encoding="utf-8"))
    return {
        str(feature["properties"]["geo_id"]): feature["geometry"]
        for feature in collection["features"]
        if feature["properties"].get("contains_toronto_da")
    }


def candidate_summaries(election_id):
    grouped = defaultdict(list)
    path = OUTPUT_ROOT / f"{election_id}_ct_candidate_estimated_votes.csv"
    for row in read_csv(path):
        grouped[row["ct_id"]].append(
            {
                "candidate_name": row["candidate_name"],
                "party_name": row["party_name"],
                "estimated_votes": number(row["estimated_candidate_votes"]),
            }
        )
    output = {}
    for ct_id, rows in grouped.items():
        sorted_rows = sorted(
            rows,
            key=lambda row: row["estimated_votes"] or 0,
            reverse=True,
        )
        output[ct_id] = {
            "top_candidates": sorted_rows[:TOP_CANDIDATE_COUNT],
            "candidate_votes": {
                row["candidate_name"]: row["estimated_votes"]
                for row in sorted_rows
            },
        }
    return output


def build_election(config, geometries):
    results = read_csv(
        OUTPUT_ROOT / f"{config.election_id}_ct_estimated_results.csv"
    )
    candidates = candidate_summaries(config.election_id)
    features = []
    for row in results:
        ct_id = row["ct_id"]
        party_votes = {
            field.removeprefix("party_").removesuffix("_votes"): number(value)
            for field, value in row.items()
            if field.startswith("party_") and field.endswith("_votes")
        }
        properties = {
            "election_id": config.election_id,
            "ct_id": ct_id,
            "estimated_total_votes": number(row["estimated_total_votes"]),
            "estimated_electors": number(row["estimated_electors"]),
            "estimated_valid_candidate_votes": number(
                row["estimated_valid_candidate_votes"]
            ),
            "estimated_turnout": number(row["estimated_turnout"]),
            "citizen_canadian_18over": number(
                row["citizen_canadian_18over"]
            ),
            "citizen_canadian_18over_status": row[
                "citizen_canadian_18over_status"
            ],
            "estimated_participation_citizen_18plus": number(
                row["estimated_participation_citizen_18plus"]
            ),
            "allocation_method": row["allocation_method"],
            "fallback_area_weight_used": row["fallback_area_weight_used"],
            "suppressed_da_count": number(row["suppressed_da_count"]),
            "suppressed_da_area_share": number(
                row["suppressed_da_area_share"]
            ),
            "no_geometry_district_allocation_used": row[
                "no_geometry_district_allocation_used"
            ],
            "party_votes": party_votes,
            "top_candidates": candidates.get(ct_id, {}).get(
                "top_candidates", []
            ),
            "candidate_votes": (
                candidates.get(ct_id, {}).get("candidate_votes", {})
                if config.election_id == "municipal_2023_mayor"
                else {}
            ),
        }
        features.append(
            {
                "type": "Feature",
                "properties": properties,
                "geometry": geometries[ct_id],
            }
        )

    collection = {
        "type": "FeatureCollection",
        "name": f"{config.election_id}_ct_interpolation",
        "features": features,
    }
    MAP_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    path = MAP_DATA_ROOT / f"{config.election_id}_ct_map.geojson"
    path.write_text(
        json.dumps(collection, ensure_ascii=True, separators=(",", ":")),
        encoding="utf-8",
    )
    return {"election_id": config.election_id, "feature_count": len(features)}


def main():
    gates = require_audit_pass()
    geometries = target_geometries()
    datasets = [build_election(config, geometries) for config in ELECTIONS]
    write_json(
        MAP_DATA_ROOT / "map_build_summary.json",
        {
            "map_created": True,
            "audit_gates": gates,
            "target_ct_count": len(geometries),
            "datasets": datasets,
            "primary_metric": "estimated_participation_citizen_18plus",
            "ancillary_weight_variable": "citizen_canadian_18over",
        },
    )


if __name__ == "__main__":
    main()
