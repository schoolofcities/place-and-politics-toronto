#!/usr/bin/env python3
"""Build one wide 2021 Census profile table per geography level."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
CENSUS_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "census"
PROCESSED_ROOT = CENSUS_ROOT / "processed"
DA_ROOT = PROCESSED_ROOT / "da"
CT_ROOT = PROCESSED_ROOT / "ct"
ADA_ROOT = PROCESSED_ROOT / "ada"
CROSSWALK_ROOT = PROCESSED_ROOT / "crosswalks"
ADA_REFERENCE = CENSUS_ROOT / "reference" / "ada_2021"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def wide_rows(level: str) -> list[dict[str, object]]:
    source_root = PROCESSED_ROOT / level / "intermediate"
    citizens = {
        row["geo_id"]: row
        for row in read_rows(
            source_root / f"statcan_2021_{level}_citizens_18plus.csv"
        )
    }
    population = {
        row["geo_id"]: row
        for row in read_rows(
            source_root / f"statcan_2021_{level}_population_18plus.csv"
        )
    }
    rows = []
    for geo_id in sorted(citizens):
        citizen = citizens[geo_id]
        adult = population[geo_id]
        rows.append(
            {
                "geo_level": level.upper(),
                "dguid": citizen["dguid"],
                "geo_id": geo_id,
                "geo_name": citizen["geo_name"],
                "census_year": citizen["census_year"],
                "citizen_canadian_18over": citizen[
                    "citizen_canadian_18over"
                ],
                "citizen_canadian_18over_status": citizen["value_status"],
                "citizen_canadian_18over_men_plus": citizen[
                    "citizen_canadian_18over_men_plus"
                ],
                "citizen_canadian_18over_women_plus": citizen[
                    "citizen_canadian_18over_women_plus"
                ],
                "citizen_canadian_18over_count_low_ci": citizen[
                    "count_low_ci_total"
                ],
                "citizen_canadian_18over_count_high_ci": citizen[
                    "count_hi_ci_total"
                ],
                "citizen_canadian_18over_rate": citizen["rate_total"],
                "citizen_canadian_18over_rate_low_ci": citizen[
                    "rate_low_ci_total"
                ],
                "citizen_canadian_18over_rate_high_ci": citizen[
                    "rate_hi_ci_total"
                ],
                "citizen_canadian_18over_data_quality_flag": citizen[
                    "data_quality_flag"
                ],
                "citizen_canadian_18over_tnr_short_form": citizen["tnr_sf"],
                "citizen_canadian_18over_tnr_long_form": citizen["tnr_lf"],
                "citizen_canadian_18over_source_note": citizen["source_note"],
                "population_total": adult["population_total"],
                "population_under18": adult["population_under18"],
                "population_18plus": adult["population_18plus"],
                "population_18plus_status": adult["value_status"],
                "population_18plus_source_symbol": adult["source_symbol"],
                "population_18plus_source_table": adult["source_table"],
                "population_18plus_method_note": adult["method_note"],
            }
        )
    return rows


def ada_rows() -> list[dict[str, object]]:
    crosswalk_path = (
        CROSSWALK_ROOT / "statcan_2021_toronto_da_ct_ada_crosswalk.csv"
    )
    if not crosswalk_path.exists():
        return []

    da_profiles = {
        row["geo_id"]: row
        for row in read_rows(DA_ROOT / "statcan_2021_da_profile.csv")
    }
    aggregates = defaultdict(
        lambda: {
            "component_da_count": 0,
            "citizen_sum": 0,
            "citizen_missing": 0,
            "population_sum": 0,
            "population_missing": 0,
        }
    )
    for link in read_rows(crosswalk_path):
        profile = da_profiles[link["da_id"]]
        aggregate = aggregates[link["ada_id"]]
        aggregate["component_da_count"] += 1
        citizen = profile["citizen_canadian_18over"].strip()
        adult = profile["population_18plus"].strip()
        if citizen:
            aggregate["citizen_sum"] += int(float(citizen))
        else:
            aggregate["citizen_missing"] += 1
        if adult:
            aggregate["population_sum"] += int(float(adult))
        else:
            aggregate["population_missing"] += 1

    official = {}
    for row in read_rows(ADA_REFERENCE / "toronto_ada_2021_profile.csv"):
        if row["CHARACTERISTIC_CODE"] == "citizen_canadian_18over":
            official[row["GEO_NAME"]] = row

    boundary_path = ADA_REFERENCE / "toronto_ada_2021_boundaries.gpkg"
    dguids = {}
    try:
        import sqlite3

        with sqlite3.connect(boundary_path) as connection:
            for ada_id, dguid in connection.execute(
                'select ADAUID, DGUID from "toronto-ada"'
            ):
                dguids[str(ada_id)] = str(dguid)
    except (sqlite3.Error, ImportError):
        pass

    rows = []
    for ada_id, aggregate in sorted(aggregates.items()):
        profile = official[ada_id]
        citizen_value = profile["C1_COUNT_TOTAL"]
        population_complete = aggregate["population_missing"] == 0
        rows.append(
            {
                "geo_level": "ADA",
                "dguid": dguids.get(ada_id, ""),
                "geo_id": ada_id,
                "geo_name": ada_id,
                "census_year": 2021,
                "citizen_canadian_18over": citizen_value,
                "citizen_canadian_18over_status": (
                    "published" if citizen_value.strip() else "not_published"
                ),
                "citizen_canadian_18over_rate": profile["C10_RATE_TOTAL"],
                "citizen_canadian_18over_component_da_sum": aggregate[
                    "citizen_sum"
                ],
                "citizen_canadian_18over_missing_da_count": aggregate[
                    "citizen_missing"
                ],
                "population_18plus": (
                    aggregate["population_sum"] if population_complete else ""
                ),
                "population_18plus_status": (
                    "aggregated_from_published_das"
                    if population_complete
                    else "incomplete_due_to_suppressed_das"
                ),
                "population_18plus_component_da_sum": aggregate[
                    "population_sum"
                ],
                "population_18plus_missing_da_count": aggregate[
                    "population_missing"
                ],
                "component_da_count": aggregate["component_da_count"],
            }
        )
    return rows


def write_dictionary() -> None:
    rows = [
        {
            "column_name": "citizen_canadian_18over",
            "statcan_characteristic_id": 1525,
            "label": "Canadian citizens aged 18 and over",
            "source_table": "2021 Census Profile",
            "universe": "Canadian citizens",
            "method": "Official published count; 25% sample data.",
        },
        {
            "column_name": "population_total",
            "statcan_characteristic_id": "",
            "label": "Total population",
            "source_table": "98-10-0023-01 / 98-10-0024-01",
            "universe": "Total population",
            "method": "Official 100% Census age-table count.",
        },
        {
            "column_name": "population_under18",
            "statcan_characteristic_id": "",
            "label": "Population under age 18",
            "source_table": "98-10-0023-01 / 98-10-0024-01",
            "universe": "Total population",
            "method": "Published age 0-14 plus single-year ages 15, 16, and 17.",
        },
        {
            "column_name": "population_18plus",
            "statcan_characteristic_id": "",
            "label": "Population aged 18 years and over",
            "source_table": "98-10-0023-01 / 98-10-0024-01",
            "universe": "Total population",
            "method": "Total population minus population under age 18.",
        },
    ]
    write_rows(PROCESSED_ROOT / "variable_dictionary.csv", rows)


def main() -> None:
    for level in ("da", "ct"):
        rows = wide_rows(level)
        write_rows(
            PROCESSED_ROOT
            / level
            / f"statcan_2021_{level}_profile.csv",
            rows,
        )
        print(f"{level.upper()}: wrote {len(rows)} profile rows")
    ada = ada_rows()
    if ada:
        write_rows(ADA_ROOT / "statcan_2021_ada_profile.csv", ada)
        print(f"ADA: wrote {len(ada)} profile rows")
    else:
        print("ADA: skipped until the DA-CT-ADA crosswalk is available")
    write_dictionary()


if __name__ == "__main__":
    main()
