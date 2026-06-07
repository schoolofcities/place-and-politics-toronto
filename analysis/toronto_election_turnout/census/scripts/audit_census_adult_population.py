#!/usr/bin/env python3
"""Reconcile Toronto adult and adult-citizen Census values."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "census"
PROFILE = DATA_ROOT / "processed" / "profile_2021"
GEOGRAPHY = DATA_ROOT / "processed" / "geography_2021"
REFERENCE = DATA_ROOT / "reference" / "ada_2021"
SUMMARY = PROFILE / "statcan_2021_adult_population_audit.json"
ADA_OUTPUT = PROFILE / "statcan_2021_ada_citizens_18plus_reconciliation.csv"
OFFICIAL_CSD_CITIZENS_18PLUS = 1_870_055


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def number(value: str | None) -> int | None:
    text = str(value or "").strip()
    return int(float(text)) if text else None


def main() -> None:
    da_rows = read_rows(PROFILE / "statcan_2021_da_citizens_18plus.csv")
    ct_rows = read_rows(PROFILE / "statcan_2021_ct_citizens_18plus.csv")
    age_rows = read_rows(PROFILE / "statcan_2021_da_population_18plus.csv")
    crosswalk = read_rows(GEOGRAPHY / "statcan_2021_toronto_da_ct_ada_crosswalk.csv")
    linked_ct_ids = {row["ct_id"] for row in crosswalk}
    linked_ct_rows = [row for row in ct_rows if row["geo_id"] in linked_ct_ids]
    ada_reference = {
        row["GEO_NAME"]: row
        for row in read_rows(REFERENCE / "toronto_ada_2021_profile.csv")
        if row["CHARACTERISTIC_CODE"] == "citizen_canadian_18over"
    }

    da_by_id = {row["geo_id"]: row for row in da_rows}
    aggregates: dict[str, dict[str, int]] = defaultdict(
        lambda: {"da_count": 0, "suppressed_da_count": 0, "da_sum": 0}
    )
    for link in crosswalk:
        aggregate = aggregates[link["ada_id"]]
        aggregate["da_count"] += 1
        value = number(da_by_id[link["da_id"]]["citizen_canadian_18over"])
        if value is None:
            aggregate["suppressed_da_count"] += 1
        else:
            aggregate["da_sum"] += value

    reconciliation = []
    for ada_id, aggregate in sorted(aggregates.items()):
        official = number(ada_reference[ada_id]["C1_COUNT_TOTAL"])
        reconciliation.append(
            {
                "ada_id": ada_id,
                **aggregate,
                "official_ada_citizens_18plus": official,
                "da_sum_minus_official_ada": aggregate["da_sum"] - official,
                "comparison_note": (
                    "Difference may reflect independent random rounding and "
                    "confidentiality-suppressed DA values."
                ),
            }
        )
    with ADA_OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=reconciliation[0].keys())
        writer.writeheader()
        writer.writerows(reconciliation)

    sum_field = lambda rows, field: sum(number(row[field]) or 0 for row in rows)
    da_citizen_total = sum_field(da_rows, "citizen_canadian_18over")
    linked_ct_total = sum_field(linked_ct_rows, "citizen_canadian_18over")
    all_ct_total = sum_field(ct_rows, "citizen_canadian_18over")
    ada_total = sum(
        number(row["C1_COUNT_TOTAL"]) or 0 for row in ada_reference.values()
    )
    da_population_total = sum_field(age_rows, "population_18plus")
    with (PROFILE / "statcan_2021_population_18plus_extraction_metadata.json").open(
        encoding="utf-8"
    ) as f:
        age_metadata = json.load(f)
    differences = [row["da_sum_minus_official_ada"] for row in reconciliation]

    summary = {
        "variable_distinction": {
            "population_18plus": "All persons aged 18+; 100% Census data.",
            "citizen_canadian_18over": "Canadian citizens aged 18+; 25% sample Census Profile data.",
        },
        "population_18plus": {
            "da_row_count": len(age_rows),
            "da_missing_count": sum(
                row["value_status"] != "published" for row in age_rows
            ),
            "da_sum": da_population_total,
            "official_toronto_csd": age_metadata["official_toronto_csd_population_18plus"],
            "difference": age_metadata["da_sum_minus_official_csd"],
        },
        "canadian_citizens_18plus": {
            "official_toronto_csd": OFFICIAL_CSD_CITIZENS_18PLUS,
            "da_sum": da_citizen_total,
            "da_suppressed_count": sum(
                row["value_status"] != "published" for row in da_rows
            ),
            "da_difference": da_citizen_total - OFFICIAL_CSD_CITIZENS_18PLUS,
            "toronto_linked_ct_count": len(linked_ct_rows),
            "toronto_linked_ct_sum": linked_ct_total,
            "toronto_linked_ct_difference": linked_ct_total - OFFICIAL_CSD_CITIZENS_18PLUS,
            "all_clipped_ct_count": len(ct_rows),
            "all_clipped_ct_sum_not_city_total": all_ct_total,
            "ada_reference_count": len(ada_reference),
            "ada_reference_sum": ada_total,
            "ada_reference_difference": ada_total - OFFICIAL_CSD_CITIZENS_18PLUS,
        },
        "ada_reconciliation": {
            "ada_count": len(reconciliation),
            "exact_match_count": sum(value == 0 for value in differences),
            "within_5_count": sum(abs(value) <= 5 for value in differences),
            "within_10_count": sum(abs(value) <= 10 for value in differences),
            "mean_absolute_difference": sum(abs(value) for value in differences)
            / len(differences),
            "maximum_absolute_difference": max(abs(value) for value in differences),
        },
        "reference_dataset_findings": {
            "ada_profile": "Contains the same official characteristic and reconciles closely.",
            "zack_taylor_ct2021": (
                "Contains election-derived eligible-voter and historical population "
                "fields, but no equivalent 2021 Census Canadian-citizen 18+ variable."
            ),
        },
    }
    with SUMMARY.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
