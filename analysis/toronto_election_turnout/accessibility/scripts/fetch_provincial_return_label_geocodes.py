"""Fetch City address-point candidates for Provincial 2025 official return labels.

The Provincial 2025 processed turnout file carries `polling_division_name`
from Elections Ontario's `VotingPlaceAddressOrLocation` official return field.
This script queries Open Toronto Address Points for those labels and stores the
top City address-point candidates for later manual/automated review.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
TURNOUT_CSV = (
    DATA_ROOT
    / "elections"
    / "processed"
    / "provincial_2025"
    / "turnout"
    / "toronto_provincial_2025_turnout_poll_divisions.csv"
)
OUTPUT_CSV = (
    DATA_ROOT
    / "accessibility"
    / "raw"
    / "provincial_2025"
    / "eo_official_return_label_address_point_candidates.csv"
)
ADDRESS_POINT_RESOURCE_ID = "0b3756af-9caf-4f0f-ac28-9c6617adede4"
ADDRESS_POINT_API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"


def normalized(value: str) -> str:
    text = value.upper().replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return " ".join(part for part in text.split() if part and part not in {"THE", "NONE"})


def token_score(left: str, right: str) -> float:
    left_tokens = set(normalized(left).split())
    right_tokens = set(normalized(right).split())
    if not left_tokens or not right_tokens:
        return 0.0
    return 2 * len(left_tokens & right_tokens) / (len(left_tokens) + len(right_tokens))


def read_labels() -> list[tuple[str, str]]:
    labels = set()
    with TURNOUT_CSV.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if not row.get("geometry", "").strip():
                continue
            label = row.get("polling_division_name", "").strip()
            district = str(int(row.get("electoral_district_number", "0")))
            if label:
                labels.add((district, label))
    return sorted(labels)


def query(label: str) -> list[dict]:
    params = urlencode(
        {
            "resource_id": ADDRESS_POINT_RESOURCE_ID,
            "q": label,
            "limit": 5,
        }
    )
    with urlopen(f"{ADDRESS_POINT_API}?{params}", timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("result", {}).get("records", [])


def main():
    existing = set()
    if OUTPUT_CSV.exists():
        with OUTPUT_CSV.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                existing.add((row["electoral_district_number"], row["official_return_label"]))

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_header = not OUTPUT_CSV.exists()
    fieldnames = [
        "electoral_district_number",
        "official_return_label",
        "candidate_rank",
        "address_point_id",
        "objectid",
        "address_full",
        "place_name",
        "place_name_all",
        "ward",
        "ward_name",
        "polling_location_lon",
        "polling_location_lat",
        "api_rank",
        "label_to_place_token_score",
        "label_to_address_token_score",
        "query_status",
    ]
    labels = read_labels()
    with OUTPUT_CSV.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for index, (district, label) in enumerate(labels, start=1):
            if (district, label) in existing:
                continue
            try:
                records = query(label)
            except Exception as exc:
                writer.writerow(
                    {
                        "electoral_district_number": district,
                        "official_return_label": label,
                        "candidate_rank": "",
                        "query_status": f"error:{type(exc).__name__}",
                    }
                )
                handle.flush()
                continue
            if not records:
                writer.writerow(
                    {
                        "electoral_district_number": district,
                        "official_return_label": label,
                        "candidate_rank": "",
                        "query_status": "no_candidates",
                    }
                )
                handle.flush()
                continue
            for rank, record in enumerate(records, start=1):
                lon = lat = ""
                if record.get("geometry"):
                    geometry = json.loads(record["geometry"])
                    lon, lat = geometry["coordinates"]
                writer.writerow(
                    {
                        "electoral_district_number": district,
                        "official_return_label": label,
                        "candidate_rank": rank,
                        "address_point_id": record.get("ADDRESS_POINT_ID", ""),
                        "objectid": record.get("OBJECTID", ""),
                        "address_full": record.get("ADDRESS_FULL", ""),
                        "place_name": record.get("PLACE_NAME", ""),
                        "place_name_all": record.get("PLACE_NAME_ALL", ""),
                        "ward": record.get("WARD", ""),
                        "ward_name": record.get("WARD_NAME", ""),
                        "polling_location_lon": f"{float(lon):.8f}" if lon != "" else "",
                        "polling_location_lat": f"{float(lat):.8f}" if lat != "" else "",
                        "api_rank": record.get("rank", ""),
                        "label_to_place_token_score": f"{token_score(label, record.get('PLACE_NAME_ALL', '')):.4f}",
                        "label_to_address_token_score": f"{token_score(label, record.get('ADDRESS_FULL', '')):.4f}",
                        "query_status": "candidate_returned",
                    }
                )
            handle.flush()
            if index % 100 == 0:
                print(f"Queried {index} / {len(labels)} labels")
    print(f"Wrote candidates to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
