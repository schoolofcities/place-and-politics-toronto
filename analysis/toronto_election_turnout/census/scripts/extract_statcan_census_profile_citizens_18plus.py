#!/usr/bin/env python3
"""Extract 2021 Census Profile Canadian-citizen adult counts for Toronto DA/CTs.

This script reads official Statistics Canada comprehensive Census Profile CSV
zip files and writes small Toronto-only outputs for characteristic 1525:
"Canadian citizens aged 18 and over".

The large source zips are expected in /private/tmp by default:
  - statcan_da_ontario_ci.zip, GEONO=006CI_Ontario
  - statcan_ct_ci.zip, GEONO=007CI
"""

from __future__ import annotations

import csv
import json
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CENSUS_DIR = ROOT / "data" / "toronto_election_turnout" / "census" / "raw"
OUTPUT_DIR = ROOT / "data" / "toronto_election_turnout" / "census" / "processed" / "profile_2021"

DA_ZIP = Path("/private/tmp/statcan_da_ontario_ci.zip")
CT_ZIP = Path("/private/tmp/statcan_ct_ci.zip")

DA_SOURCE_URL = (
    "https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/"
    "details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=006CI_Ontario"
)
CT_SOURCE_URL = (
    "https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/"
    "details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=007CI"
)

CHARACTERISTIC_ID = "1525"
CHARACTERISTIC_NAME = "Canadian citizens aged 18 and over"
CHARACTERISTIC_CODE = "citizen_canadian_18over"


def read_da_dguids() -> set[str]:
    """Toronto DAs are nested in Toronto CD/CSD and have DAUID prefix 3520."""
    gpkg = CENSUS_DIR / "statcan_2021_da_toronto_clipped.gpkg"
    with sqlite3.connect(gpkg) as conn:
        rows = conn.execute(
            "select DGUID from dissemination_areas_2021_toronto where DAUID like '3520%'"
        ).fetchall()
    return {row[0] for row in rows}


def read_ct_dguids() -> set[str]:
    """Use the current Toronto CT geometry universe."""
    gpkg = CENSUS_DIR / "statcan_2021_ct_toronto_clipped.gpkg"
    with sqlite3.connect(gpkg) as conn:
        rows = conn.execute("select DGUID from census_tracts_2021_toronto").fetchall()
    return {row[0] for row in rows}


def csv_member(zip_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as zf:
        names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        data_names = [name for name in names if "data" in name.lower()]
        return data_names[0] if data_names else names[0]


def as_int(value: str) -> int | None:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    return int(float(value))


def value_status(value: int | None, data_quality_flag: str) -> tuple[str, str | None]:
    flag = (data_quality_flag or "").strip().zfill(5)
    if value is not None:
        return "published", None
    if len(flag) == 5 and flag[3] == "9":
        return (
            "suppressed_confidentiality",
            "Long-form value suppressed by Statistics Canada to meet the "
            "confidentiality requirements of the Statistics Act.",
        )
    return "not_published", "No value was published in the official source."


def extract(zip_path: Path, dguids: set[str], level: str) -> list[dict[str, object]]:
    member = csv_member(zip_path)
    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as raw:
            text = (line.decode("latin-1") for line in raw)
            reader = csv.DictReader(text)
            for row in reader:
                if row["DGUID"] not in dguids:
                    continue
                if row["CHARACTERISTIC_ID"] != CHARACTERISTIC_ID:
                    continue
                value = as_int(row["C1_COUNT_TOTAL"])
                status, note = value_status(value, row["DATA_QUALITY_FLAG"])
                rows.append(
                    {
                        "geo_level": level,
                        "dguid": row["DGUID"],
                        "geo_id": row["ALT_GEO_CODE"],
                        "geo_name": row["GEO_NAME"],
                        "census_year": as_int(row["CENSUS_YEAR"]),
                        "characteristic_id": as_int(row["CHARACTERISTIC_ID"]),
                        "characteristic_code": CHARACTERISTIC_CODE,
                        "characteristic_name": row["CHARACTERISTIC_NAME"].strip(),
                        "citizen_canadian_18over": value,
                        "citizen_canadian_18over_men_plus": as_int(row["C2_COUNT_MEN+"]),
                        "citizen_canadian_18over_women_plus": as_int(row["C3_COUNT_WOMEN+"]),
                        "count_low_ci_total": as_int(row["C4_COUNT_LOW_CI_TOTAL"]),
                        "count_hi_ci_total": as_int(row["C7_COUNT_HI_CI_TOTAL"]),
                        "rate_total": row["C10_RATE_TOTAL"],
                        "rate_low_ci_total": row["C13_RATE_LOW_CI_TOTAL"],
                        "rate_hi_ci_total": row["C16_RATE_HI_CI_TOTAL"],
                        "tnr_sf": row["TNR_SF"],
                        "tnr_lf": row["TNR_LF"],
                        "data_quality_flag": row["DATA_QUALITY_FLAG"],
                        "value_status": status,
                        "source_note": note,
                    }
                )
    rows.sort(key=lambda item: str(item["geo_id"]))
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows extracted for {path}")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    for source in (DA_ZIP, CT_ZIP):
        if not source.exists():
            raise FileNotFoundError(f"Missing source zip: {source}")

    da_dguids = read_da_dguids()
    ct_dguids = read_ct_dguids()

    da_rows = extract(DA_ZIP, da_dguids, "DA")
    ct_rows = extract(CT_ZIP, ct_dguids, "CT")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    da_path = OUTPUT_DIR / "statcan_2021_da_citizens_18plus.csv"
    ct_path = OUTPUT_DIR / "statcan_2021_ct_citizens_18plus.csv"
    write_csv(da_path, da_rows)
    write_csv(ct_path, ct_rows)

    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Statistics Canada 2021 Census Profile comprehensive CSV downloads with confidence intervals",
        "da_source_url": DA_SOURCE_URL,
        "ct_source_url": CT_SOURCE_URL,
        "characteristic_id": int(CHARACTERISTIC_ID),
        "characteristic_code": CHARACTERISTIC_CODE,
        "characteristic_name": CHARACTERISTIC_NAME,
        "da_expected_rows": len(da_dguids),
        "da_extracted_rows": len(da_rows),
        "da_total_citizen_canadian_18over": sum(
            row["citizen_canadian_18over"] or 0 for row in da_rows
        ),
        "da_missing_citizen_canadian_18over_rows": sum(
            1 for row in da_rows if row["citizen_canadian_18over"] is None
        ),
        "ct_expected_rows": len(ct_dguids),
        "ct_extracted_rows": len(ct_rows),
        "ct_total_citizen_canadian_18over": sum(
            row["citizen_canadian_18over"] or 0 for row in ct_rows
        ),
        "ct_missing_citizen_canadian_18over_rows": sum(
            1 for row in ct_rows if row["citizen_canadian_18over"] is None
        ),
        "notes": [
            "The source zips are not stored in Git because they are large official comprehensive downloads.",
            "The DA universe is restricted to DAUID prefix 3520, which corresponds to Toronto census division/census subdivision geographies.",
            "The CT universe follows the stored Toronto CT geometry file.",
            "The direct CT-level Census Profile sum does not reconcile exactly to the Toronto CSD/DA sum for this 25% sample characteristic; use DA-level weights as the primary ancillary input.",
            "Values are Census Profile counts of Canadian citizens aged 18 and over, not election elector counts.",
            "Blank values with a fourth data-quality-flag digit of 9 are explicitly suppressed by Statistics Canada for long-form confidentiality; they are not survey non-response or zero population.",
        ],
    }
    (OUTPUT_DIR / "statcan_2021_citizens_18plus_extraction_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
