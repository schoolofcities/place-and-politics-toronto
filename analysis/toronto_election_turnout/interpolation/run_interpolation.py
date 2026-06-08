#!/usr/bin/env python3
"""Build all population-weighted poll-to-CT interpolation outputs."""

from __future__ import annotations

import sys

from config import (
    ANCILLARY_WEIGHT_FIELD,
    CT_PATH,
    DA_PATH,
    ELECTIONS,
    OUTPUT_ROOT,
)
from io_utils import write_csv, write_json
from spatial import load_census
from workflow import run_election


def main():
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    cts, das, suppressed_rows = load_census(CT_PATH, DA_PATH)
    if len(cts) != 585:
        raise ValueError(f"Expected 585 Toronto CT polygons, found {len(cts)}")

    write_csv(OUTPUT_ROOT / "suppressed_da_audit.csv", suppressed_rows)
    census_audit = {
        "target_ct_count": len(cts),
        "da_count": len(das),
        "suppressed_da_weight_rows": len(suppressed_rows),
        "suppressed_da_weight_treatment": "zero",
        "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
        "target_universe": "CT polygons with contains_toronto_da = true",
    }
    write_json(OUTPUT_ROOT / "census_input_audit.json", census_audit)

    results = []
    for config in ELECTIONS:
        print(f"Building {config.election_id}...", flush=True)
        result = run_election(config, cts, das)
        results.append(result)
        print(
            f"  {result['summary']['ct_result_rows']} CT rows; "
            f"{result['summary']['excluded_or_unallocated_rows']} exclusions; "
            f"primary validation pass="
            f"{result['summary']['all_primary_vote_validations_pass']}",
            flush=True,
        )

    combined_audit = [
        row for result in results for row in result["audit"]
    ]
    combined_validation = [
        row for result in results for row in result["validation"]
    ]
    combined_exclusions = [
        row for result in results for row in result["exclusions"]
    ]
    combined_no_geometry_audit = [
        row for result in results for row in result["no_geometry_audit"]
    ]
    turnout_comparison = [
        result["turnout_comparison"] for result in results
    ]
    write_csv(OUTPUT_ROOT / "interpolation_audit.csv", combined_audit)
    write_csv(OUTPUT_ROOT / "validation_report.csv", combined_validation)
    write_csv(
        OUTPUT_ROOT / "excluded_unallocated_report.csv", combined_exclusions
    )
    write_csv(
        OUTPUT_ROOT / "no_geometry_allocation_audit.csv",
        combined_no_geometry_audit,
    )
    write_csv(
        OUTPUT_ROOT / "turnout_comparison.csv",
        turnout_comparison,
    )

    primary_failures = [
        row
        for row in combined_validation
        if row["measure_type"] in {"total_votes", "party", "candidate"}
        and not row["within_tolerance"]
    ]
    no_geometry_failures = [
        row for row in combined_no_geometry_audit if not row["fully_allocated"]
    ]
    vote_bearing_exclusions = [
        row
        for row in combined_exclusions
        if str(row.get("number_of_votes", "")).strip()
        and float(row["number_of_votes"]) > 0
    ]
    turnout_alignment_failures = [
        row
        for row in turnout_comparison
        if not row[
            "citizen_18plus_rate_closer_to_published_than_official_row_rate"
        ]
    ]
    map_gate_passed = (
        not primary_failures
        and not no_geometry_failures
        and not vote_bearing_exclusions
        and not turnout_alignment_failures
    )
    final_summary = {
        "elections": [result["summary"] for result in results],
        "primary_validation_failure_count": len(primary_failures),
        "all_primary_vote_validations_pass": not primary_failures,
        "excluded_or_unallocated_row_count": len(combined_exclusions),
        "vote_bearing_exclusion_count": len(vote_bearing_exclusions),
        "no_geometry_allocation_failure_count": len(no_geometry_failures),
        "turnout_alignment_failure_count": len(turnout_alignment_failures),
        "map_gate_passed": map_gate_passed,
        "map_created": False,
    }
    write_json(OUTPUT_ROOT / "validation_summary.json", final_summary)
    if primary_failures:
        print(
            f"Primary vote preservation failed in {len(primary_failures)} checks.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
