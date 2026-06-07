#!/usr/bin/env python3
"""Audit whether suppressed DA citizenship counts can be inferred from CT totals."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "census"
PROFILE = DATA_ROOT / "processed" / "profile_2021"
GEOGRAPHY = DATA_ROOT / "processed" / "geography_2021"
OUTPUT = GEOGRAPHY / "statcan_2021_toronto_da_ct_residual_diagnostics.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def nullable_int(value: str | None) -> int | None:
    text = str(value or "").strip()
    return int(text) if text else None


def main() -> None:
    da_rows = read_rows(PROFILE / "statcan_2021_da_citizens_18plus.csv")
    ct_rows = {
        row["geo_id"]: row
        for row in read_rows(PROFILE / "statcan_2021_ct_citizens_18plus.csv")
    }
    crosswalk = {
        row["da_id"]: row
        for row in read_rows(
            GEOGRAPHY / "statcan_2021_toronto_da_ct_ada_crosswalk.csv"
        )
    }

    das_by_ct: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in da_rows:
        das_by_ct[crosswalk[row["geo_id"]]["ct_id"]].append(row)

    output_rows = []
    for row in da_rows:
        if row["value_status"] == "published":
            continue

        da_id = row["geo_id"]
        link = crosswalk[da_id]
        ct_id = link["ct_id"]
        ct_row = ct_rows.get(ct_id)
        siblings = das_by_ct[ct_id]
        published_siblings = [
            sibling
            for sibling in siblings
            if sibling["geo_id"] != da_id
            and sibling["value_status"] == "published"
        ]
        suppressed_siblings = [
            sibling
            for sibling in siblings
            if sibling["value_status"] != "published"
        ]
        sibling_sum = sum(
            nullable_int(sibling["citizen_canadian_18over"]) or 0
            for sibling in published_siblings
        )
        ct_value = (
            nullable_int(ct_row["citizen_canadian_18over"]) if ct_row else None
        )
        raw_residual = ct_value - sibling_sum if ct_value is not None else None

        if ct_row is None:
            status = "parent_ct_not_in_profile"
        elif ct_row["value_status"] != "published":
            status = "parent_ct_suppressed"
        elif len(suppressed_siblings) != 1:
            status = "multiple_suppressed_das_in_ct"
        elif raw_residual is not None and raw_residual < 0:
            status = "negative_residual_from_independent_rounding"
        else:
            status = "nonnegative_residual_diagnostic"

        output_rows.append(
            {
                "da_id": da_id,
                "ct_id": ct_id,
                "ada_id": link["ada_id"],
                "official_da_value": "",
                "official_da_value_status": row["value_status"],
                "ct_official_value": "" if ct_value is None else ct_value,
                "ct_value_status": (
                    ct_row["value_status"] if ct_row else "not_published"
                ),
                "ct_da_count": len(siblings),
                "ct_suppressed_da_count": len(suppressed_siblings),
                "published_other_da_count": len(published_siblings),
                "published_other_da_sum": sibling_sum,
                "raw_ct_minus_other_da_residual": (
                    "" if raw_residual is None else raw_residual
                ),
                "residual_status": status,
                "can_replace_official_null": "false",
                "method_note": (
                    "Diagnostic only. The residual subtracts independently "
                    "rounded published DA counts from the independently rounded "
                    "CT count. It is not an official DA value and must not replace "
                    "the confidentiality-suppressed null."
                ),
            }
        )

    fields = [
        "da_id",
        "ct_id",
        "ada_id",
        "official_da_value",
        "official_da_value_status",
        "ct_official_value",
        "ct_value_status",
        "ct_da_count",
        "ct_suppressed_da_count",
        "published_other_da_count",
        "published_other_da_sum",
        "raw_ct_minus_other_da_residual",
        "residual_status",
        "can_replace_official_null",
        "method_note",
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    status_counts: dict[str, int] = defaultdict(int)
    for output_row in output_rows:
        status_counts[output_row["residual_status"]] += 1
    print(f"Wrote {len(output_rows)} rows to {OUTPUT}")
    for status, count in sorted(status_counts.items()):
        print(f"{status}: {count}")


if __name__ == "__main__":
    main()
