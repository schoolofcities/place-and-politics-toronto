#!/usr/bin/env python3
"""Extract 2021 population aged 18+ for Toronto DAs and CTs."""

from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "census"
DA_SOURCE_ZIP = DATA_ROOT / "raw" / "source_downloads" / "statcan_2021_age_single_year_98100023-eng.zip"
CT_SOURCE_ZIP = DATA_ROOT / "raw" / "source_downloads" / "statcan_2021_ct_age_single_year_98100024-eng.zip"
PROCESSED = DATA_ROOT / "processed"
DA_INTERMEDIATE = PROCESSED / "da" / "intermediate"
CT_INTERMEDIATE = PROCESSED / "ct" / "intermediate"
AUDITS = PROCESSED / "audits" / "profile_extraction"
DA_SOURCE = DA_INTERMEDIATE / "statcan_2021_da_citizens_18plus.csv"
CT_SOURCE = CT_INTERMEDIATE / "statcan_2021_ct_citizens_18plus.csv"
DA_OUTPUT = DA_INTERMEDIATE / "statcan_2021_da_population_18plus.csv"
CT_OUTPUT = CT_INTERMEDIATE / "statcan_2021_ct_population_18plus.csv"
METADATA = AUDITS / "statcan_2021_population_18plus_extraction_metadata.json"
TORONTO_CSD_DGUID = "2021A00053520005"


def as_int(value: str) -> int | None:
    text = value.strip()
    return int(float(text)) if text else None


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def extract_values(
    source_zip: Path, member: str, wanted_dguids: set[str]
) -> dict[str, dict[str, int | str | None]]:
    values: dict[str, dict[str, int | str | None]] = {
        dguid: {
            "geo_name": "",
            "total": None,
            "under15": None,
            "ages_15_17": 0,
            "age_15_17_count": 0,
            "symbol": "",
        }
        for dguid in wanted_dguids
    }
    with zipfile.ZipFile(source_zip) as archive:
        with archive.open(member) as raw:
            text = (line.decode("utf-8-sig") for line in raw)
            for row in csv.DictReader(text):
                dguid = row["DGUID"]
                if dguid not in wanted_dguids:
                    continue
                record = values[dguid]
                record["geo_name"] = row["GEO"]
                if row["Symbol"]:
                    record["symbol"] = row["Symbol"]
                age = row["Age (in single years), average age and median age (128)"]
                count = as_int(row["Gender (3):Total - Gender[1]"])
                if age == "Total - Age":
                    record["total"] = count
                elif age == "0 to 14 years":
                    record["under15"] = count
                elif age in {"15", "16", "17"}:
                    if count is not None:
                        record["ages_15_17"] = int(record["ages_15_17"]) + count
                    record["age_15_17_count"] = int(record["age_15_17_count"]) + 1
    return values


def build_output_rows(
    source_rows: list[dict[str, str]],
    values: dict[str, dict[str, int | str | None]],
    geo_level: str,
    source_table: str,
) -> list[dict[str, object]]:
    output_rows = []
    for source_row in source_rows:
        record = values[source_row["dguid"]]
        complete = (
            record["total"] is not None
            and record["under15"] is not None
            and record["age_15_17_count"] == 3
        )
        under18 = (
            int(record["under15"]) + int(record["ages_15_17"])
            if complete
            else None
        )
        population_18plus = (
            int(record["total"]) - under18 if complete else None
        )
        output_rows.append(
            {
                "geo_level": geo_level,
                "dguid": source_row["dguid"],
                "geo_id": source_row["geo_id"],
                "geo_name": source_row["geo_name"],
                "census_year": 2021,
                "characteristic_code": "population_18plus",
                "characteristic_name": "Population aged 18 years and over",
                "population_total": record["total"] if complete else "",
                "population_under18": under18 if complete else "",
                "population_18plus": population_18plus if complete else "",
                "value_status": (
                    "published"
                    if complete
                    else "suppressed_confidentiality"
                    if record["symbol"] == "x"
                    else "not_published"
                ),
                "source_symbol": record["symbol"],
                "source_table": source_table,
                "method_note": (
                    "Total - Age minus the published 0-to-14 aggregate and "
                    "single-year counts for ages 15, 16, and 17; 100% Census data."
                ),
            }
        )
    return output_rows


def write_rows(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    DA_INTERMEDIATE.mkdir(parents=True, exist_ok=True)
    CT_INTERMEDIATE.mkdir(parents=True, exist_ok=True)
    AUDITS.mkdir(parents=True, exist_ok=True)
    da_rows = read_rows(DA_SOURCE)
    ct_rows = read_rows(CT_SOURCE)
    da_values = extract_values(
        DA_SOURCE_ZIP,
        "98100023.csv",
        {row["dguid"] for row in da_rows} | {TORONTO_CSD_DGUID},
    )
    ct_values = extract_values(
        CT_SOURCE_ZIP,
        "98100024.csv",
        {row["dguid"] for row in ct_rows},
    )
    da_output_rows = build_output_rows(
        da_rows, da_values, "DA", "98-10-0023-01"
    )
    ct_output_rows = build_output_rows(
        ct_rows, ct_values, "CT", "98-10-0024-01"
    )
    write_rows(DA_OUTPUT, da_output_rows)
    write_rows(CT_OUTPUT, ct_output_rows)

    city = da_values[TORONTO_CSD_DGUID]
    city_complete = (
        city["total"] is not None
        and city["under15"] is not None
        and city["age_15_17_count"] == 3
    )
    city_under18 = (
        int(city["under15"]) + int(city["ages_15_17"]) if city_complete else None
    )
    city_18plus = int(city["total"]) - city_under18 if city_complete else None
    da_total = sum(
        int(row["population_18plus"])
        for row in da_output_rows
        if row["population_18plus"] != ""
    )
    ct_total = sum(
        int(row["population_18plus"])
        for row in ct_output_rows
        if row["population_18plus"] != ""
    )
    metadata = {
        "source_tables": {
            "DA_and_CSD": {
                "table": "98-10-0023-01",
                "url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810002301",
            },
            "CT": {
                "table": "98-10-0024-01",
                "url": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810002401",
            },
        },
        "universe": "Total population, including institutional residents, 2021 Census - 100% data",
        "calculation": "Total - Age minus ages 0 to 14, 15, 16, and 17",
        "toronto_da_rows": len(da_output_rows),
        "toronto_da_missing_rows": sum(
            row["value_status"] != "published" for row in da_output_rows
        ),
        "toronto_da_sum_population_18plus": da_total,
        "toronto_clipped_ct_rows": len(ct_output_rows),
        "toronto_clipped_ct_missing_rows": sum(
            row["value_status"] != "published" for row in ct_output_rows
        ),
        "toronto_clipped_ct_sum_population_18plus": ct_total,
        "official_toronto_csd_population_total": city["total"],
        "official_toronto_csd_population_under18": city_under18,
        "official_toronto_csd_population_18plus": city_18plus,
        "da_sum_minus_official_csd": da_total - city_18plus,
        "notes": [
            "This is all persons aged 18+, not Canadian citizens aged 18+.",
            "Counts are independently randomly rounded.",
            "Rows marked x by Statistics Canada remain null.",
        ],
    }
    with METADATA.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
