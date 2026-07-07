"""Geocode Elections Ontario proposed voting-location addresses.

This script uses official source tables only:
- Elections Ontario proposed voting-location CSV exports already saved locally.
- Open Toronto Address Points datastore API for address-point coordinates.

The output is a raw-source cache used by build_accessibility_audit.py. It is
kept separate from processed outputs because it is an API-derived geocode cache,
not an election-results table.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parents[4]
RAW_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "accessibility" / "raw"
PVL_ROOT = RAW_ROOT / "provincial_2025" / "eo_proposed_voting_locations"
OUTPUT_CSV = RAW_ROOT / "provincial_2025" / "eo_proposed_voting_locations_geocoded.csv"
ADDRESS_POINTS_CSV = RAW_ROOT / "open_toronto" / "address_points.csv"
ADDRESS_POINT_RESOURCE_ID = "0b3756af-9caf-4f0f-ac28-9c6617adede4"
ADDRESS_POINT_API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
CITY_SUFFIXES = {
    "TORONTO",
    "EAST YORK",
    "ETOBICOKE",
    "NORTH YORK",
    "SCARBOROUGH",
    "YORK",
}


def read_pvl_rows() -> list[dict[str, str]]:
    rows = []
    for path in sorted(PVL_ROOT.glob("eo_pvl_*.csv")):
        district = path.stem.split("_")[-1]
        with path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                row = dict(row)
                row["electoral_district_number"] = str(int(district))
                row["source_file"] = path.name
                rows.append(row)
    return rows


def load_address_points() -> dict[tuple[int, str], list[dict[str, str]]]:
    index: dict[tuple[int, str], list[dict[str, str]]] = {}
    with ADDRESS_POINTS_CSV.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            try:
                number = int(float(row.get("LO_NUM") or 0))
            except ValueError:
                continue
            street = str(row.get("LINEAR_NAME_FULL") or "").strip().lower()
            if number and street:
                index.setdefault((number, street), []).append(row)
    return index


def query_address_point(address: str, address_index: dict[tuple[int, str], list[dict[str, str]]]) -> dict[str, str]:
    query_address = clean_address_query(address)
    match = query_address_point_local(query_address, address_index)
    if match:
        match["geocode_method"] = "open_toronto_address_points_local_structured_address_match"
        return match
    return {}


def query_address_point_local(
    query_address: str, address_index: dict[tuple[int, str], list[dict[str, str]]]
) -> dict[str, str]:
    parsed = parse_street_address(query_address)
    if not parsed:
        return {}
    number, street = parsed
    for candidate in street_name_candidates(street):
        records = address_index.get((number, candidate.lower()), [])
        if records:
            return choose_best_address_record(records, number, candidate)
    return {}


def fetch_records(params: dict, timeout: int = 8) -> list[dict]:
    with urlopen(f"{ADDRESS_POINT_API}?{urlencode(params)}", timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("result", {}).get("records", [])


def query_address_point_text(query_address: str) -> dict[str, str]:
    params = urlencode(
        {
            "resource_id": ADDRESS_POINT_RESOURCE_ID,
            "q": query_address,
            "limit": 5,
        }
    )
    with urlopen(f"{ADDRESS_POINT_API}?{params}", timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    records = payload.get("result", {}).get("records", [])
    if not records:
        return {}
    return records[0]


def query_address_point_structured(query_address: str) -> dict[str, str]:
    parsed = parse_street_address(query_address)
    if not parsed:
        return {}
    number, street = parsed
    candidates = street_name_candidates(street)
    for candidate in candidates:
        records = fetch_records(
            {
                "resource_id": ADDRESS_POINT_RESOURCE_ID,
                "filters": json.dumps({"LO_NUM": number, "LINEAR_NAME_FULL": candidate}),
                "limit": 10,
            }
        )
        if records:
            return choose_best_address_record(records, number, candidate)
    return {}


def clean_address_query(address: str) -> str:
    text = re.sub(r"\s+[A-Z]\d[A-Z]\s*\d[A-Z]\d\s*$", "", address.strip().upper())
    for suffix in sorted(CITY_SUFFIXES, key=len, reverse=True):
        if text.endswith(f" {suffix}"):
            text = text[: -len(suffix)].strip()
            break
    return text


def parse_street_address(address: str) -> tuple[int, str] | None:
    text = address.strip()
    match = re.match(r"^(\d+)-(\d+)\s+(.+)$", text)
    if match:
        left = int(match.group(1))
        right = int(match.group(2))
        # Elections Ontario sometimes uses unit-civic forms such as
        # 201-10 Maple Leaf Dr. Keep true civic ranges like 5-7 Concorde Pl.
        number = right if len(match.group(1)) > len(match.group(2)) or left > right + 100 else left
        return number, match.group(3).strip()
    match = re.match(r"^(\d+)[A-Z]+\d*\s+(.+)$", text)
    if match:
        return int(match.group(1)), match.group(2).strip()
    match = re.match(r"^(\d+)1/2\s+(.+)$", text)
    if match:
        number = match.group(1)
        return int(number), match.group(2).strip()
    match = re.match(r"^(\d+)/2\s+(.+)$", text)
    if match:
        return int(match.group(1)), match.group(2).strip()
    match = re.match(r"^(\d+)[A-Z]?\s+(.+)$", text)
    if not match:
        return None
    return int(match.group(1)), match.group(2).strip()


def street_name_candidates(street: str) -> list[str]:
    parts = street.split()
    if not parts:
        return []
    suffix_map = {
        "AVENUE": "Ave",
        "AVE": "Ave",
        "BOULEVARD": "Blvd",
        "BLVD": "Blvd",
        "CIRCLE": "Cir",
        "CIR": "Cir",
        "CRCL": "Crcl",
        "COURT": "Crt",
        "CRT": "Crt",
        "CRESCENT": "Cres",
        "CRES": "Cres",
        "CIRCT": "Crct",
        "CRCT": "Crct",
        "DRIVE": "Dr",
        "DR": "Dr",
        "GATE": "Gate",
        "GROVE": "Grv",
        "GRV": "Grv",
        "LANE": "Lane",
        "LINE": "Line",
        "PARKWAY": "Pkwy",
        "PKWY": "Pkwy",
        "PKY": "Pkwy",
        "PLACE": "Pl",
        "PL": "Pl",
        "POINT": "Pt",
        "PT": "Pt",
        "ROAD": "Rd",
        "RD": "Rd",
        "STREET": "St",
        "ST": "St",
        "TERRACE": "Ter",
        "TERR": "Ter",
        "TER": "Ter",
        "TRAIL": "Trl",
        "TRL": "Trl",
        "WAY": "Way",
    }
    direction_map = {
        "EAST": "E",
        "E": "E",
        "WEST": "W",
        "W": "W",
        "NORTH": "N",
        "N": "N",
        "SOUTH": "S",
        "S": "S",
    }
    normalized = []
    for index, part in enumerate(parts):
        stripped = part.strip(".")
        upper = stripped.upper()
        is_last = index == len(parts) - 1
        if upper == "AVENUE" and index == 0 and len(parts) > 1:
            normalized.append("Avenue")
        elif upper == "GARDENS" and not is_last:
            normalized.append("Gardens")
        elif upper in suffix_map:
            normalized.append(suffix_map[upper])
        elif upper in direction_map and is_last:
            normalized.append(direction_map[upper])
        else:
            normalized.append(stripped.title())
    if len(normalized) >= 2 and normalized[-1].lower() == normalized[-2].lower():
        normalized = normalized[:-1]
    candidates = [" ".join(normalized)]
    if normalized and normalized[-1] == "Cir":
        candidates.append(" ".join(normalized[:-1] + ["Crcl"]))
    if normalized and normalized[-1] == "Circt":
        candidates.append(" ".join(normalized[:-1] + ["Crct"]))
    if normalized and normalized[-1] == "Line" and len(normalized) >= 2:
        if normalized[-2].endswith("s"):
            candidates.append(" ".join(normalized[:-2] + [normalized[-2][:-1] + "'s", "Line"]))
    if len(parts) >= 2:
        title_original = " ".join(part.strip(".").title() for part in parts)
        candidates.append(title_original)
    if len(normalized) > 1 and normalized[-1] in {"E", "W", "N", "S"}:
        candidates.append(" ".join(normalized[:-1]))
    return list(dict.fromkeys(candidates))


def choose_best_address_record(records: list[dict], number: int, street: str) -> dict:
    for record in records:
        if (
            str(record.get("LO_NUM", "")) == str(number)
            and str(record.get("LINEAR_NAME_FULL", "")).lower() == street.lower()
        ):
            return record
    return records[0]


def main():
    rows = read_pvl_rows()
    address_index = load_address_points()
    cache: dict[str, dict[str, str]] = {}
    fieldnames = [
        "electoral_district_number",
        "voting_location_name",
        "voting_location_address",
        "room_to_be_used",
        "source_file",
        "address_point_match_address_full",
        "address_point_match_place_name",
        "address_point_id",
        "address_point_objectid",
        "polling_location_lon",
        "polling_location_lat",
        "geocode_method",
        "geocode_source_url",
    ]
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    output_tmp = OUTPUT_CSV.with_name(f"{OUTPUT_CSV.name}.{os.getpid()}.tmp")
    with output_tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        processed = 0
        for row in rows:
            address = row.get("Voting Location Address", "").strip()
            if address and address not in cache:
                try:
                    cache[address] = query_address_point(address, address_index)
                except Exception as exc:
                    cache[address] = {"geocode_method": f"error:{type(exc).__name__}"}
            match = cache.get(address, {})
            lon = lat = ""
            if match.get("geometry"):
                geometry = json.loads(match["geometry"])
                lon, lat = geometry["coordinates"]
            writer.writerow(
                {
                    "electoral_district_number": row["electoral_district_number"],
                    "voting_location_name": row.get("Voting Location Name", ""),
                    "voting_location_address": address,
                    "room_to_be_used": row.get("Room To be used", ""),
                    "source_file": row["source_file"],
                    "address_point_match_address_full": match.get("ADDRESS_FULL", ""),
                    "address_point_match_place_name": match.get("PLACE_NAME", ""),
                    "address_point_id": match.get("ADDRESS_POINT_ID", ""),
                    "address_point_objectid": match.get("OBJECTID", ""),
                    "polling_location_lon": f"{float(lon):.8f}" if lon != "" else "",
                    "polling_location_lat": f"{float(lat):.8f}" if lat != "" else "",
                    "geocode_method": match.get("geocode_method", "not_geocoded")
                    if match
                    else "not_geocoded",
                    "geocode_source_url": ADDRESS_POINT_API,
                }
            )
            processed += 1
            if processed % 25 == 0:
                print(f"Geocoded {processed} new proposed-location addresses")
            handle.flush()
    output_tmp.replace(OUTPUT_CSV)
    print(f"Wrote geocoded proposed voting locations to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
