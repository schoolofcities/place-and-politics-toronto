#!/usr/bin/env python3
"""Reconcile suppressed adult-population variables at DA and CT levels."""

from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "census"
PROFILE = DATA_ROOT / "processed" / "profile_2021"
GEOGRAPHY = DATA_ROOT / "processed" / "geography_2021"


def read_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        return {row["geo_id"]: row for row in csv.DictReader(source)}


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def status_note(citizen_status: str, population_status: str) -> str:
    if citizen_status == "published":
        return "Both adult measures are officially published."
    if population_status == "published":
        return (
            "Canadian citizens aged 18+ is suppressed in the 25% Census Profile; "
            "all residents aged 18+ remains published in the 100% age table."
        )
    return (
        "Both Canadian citizens aged 18+ and all residents aged 18+ are "
        "officially suppressed. Values remain null."
    )


def main() -> None:
    crosswalk = {}
    with (
        GEOGRAPHY / "statcan_2021_toronto_da_ct_ada_crosswalk.csv"
    ).open(newline="", encoding="utf-8-sig") as source:
        crosswalk = {row["da_id"]: row for row in csv.DictReader(source)}

    outputs = []
    for level in ("da", "ct"):
        citizens = read_rows(
            PROFILE / f"statcan_2021_{level}_citizens_18plus.csv"
        )
        population = read_rows(
            PROFILE / f"statcan_2021_{level}_population_18plus.csv"
        )
        rows = []
        for geo_id in sorted(citizens):
            citizen_row = citizens[geo_id]
            population_row = population[geo_id]
            citizen_status = citizen_row["value_status"]
            population_status = population_row["value_status"]
            if citizen_status == "published" and population_status == "published":
                continue
            link = crosswalk.get(geo_id, {})
            rows.append(
                {
                    "geo_level": level.upper(),
                    "geo_id": geo_id,
                    "ct_id": link.get("ct_id", geo_id if level == "ct" else ""),
                    "ada_id": link.get("ada_id", ""),
                    "citizens_18plus": citizen_row["citizen_canadian_18over"],
                    "citizens_18plus_status": citizen_status,
                    "population_18plus": population_row["population_18plus"],
                    "population_18plus_status": population_status,
                    "data_quality_flag": citizen_row["data_quality_flag"],
                    "interpretation": status_note(
                        citizen_status, population_status
                    ),
                    "can_fill_suppressed_value": "false",
                }
            )
        output = (
            PROFILE
            / f"statcan_2021_{level}_adult_suppression_reconciliation.csv"
        )
        write_rows(output, rows)
        outputs.append((level.upper(), output, rows))

    for level, output, rows in outputs:
        citizen_missing = sum(
            row["citizens_18plus_status"] != "published" for row in rows
        )
        population_missing = sum(
            row["population_18plus_status"] != "published" for row in rows
        )
        print(
            f"{level}: {citizen_missing} citizenship suppressions; "
            f"{population_missing} all-resident age suppressions; wrote {output}"
        )


if __name__ == "__main__":
    main()
