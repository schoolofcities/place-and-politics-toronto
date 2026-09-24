"""Build polling-location availability and accessibility-readiness outputs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
from statistics import mean

from osgeo import ogr, osr


ogr.UseExceptions()

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
ANALYSIS_ROOT = REPO_ROOT / "analysis" / "toronto_election_turnout"
ELECTION_ROOT = DATA_ROOT / "elections" / "processed"
OUTPUT_ROOT = DATA_ROOT / "accessibility"
RAW_ROOT = OUTPUT_ROOT / "raw"
PROCESSED_ROOT = OUTPUT_ROOT / "processed"
LOCATION_ROOT = PROCESSED_ROOT / "polling_locations"
LINK_ROOT = PROCESSED_ROOT / "poll_to_location_links"
METRIC_ROOT = PROCESSED_ROOT / "poll_accessibility_metrics"
AUDIT_ROOT = PROCESSED_ROOT / "audits"
MAP_ROOT = OUTPUT_ROOT / "map"
REPORT_PATH = ANALYSIS_ROOT / "accessibility" / "docs" / "summary_report.md"
WORKING_EPSG = 3347
MUNICIPAL_2023_LOCATION_CSV = (
    RAW_ROOT
    / "municipal_2023_mayor"
    / "open_toronto_voting_locations_2023.csv"
)
PROVINCIAL_2025_PVL_ROOT = (
    RAW_ROOT / "provincial_2025" / "eo_proposed_voting_locations"
)
PROVINCIAL_2025_GEOCODED_CSV = (
    RAW_ROOT / "provincial_2025" / "eo_proposed_voting_locations_geocoded.csv"
)
OPEN_TORONTO_ADDRESS_POINTS_CSV = RAW_ROOT / "open_toronto" / "address_points.csv"
PROVINCIAL_2025_MATCH_DETAIL_CSV = (
    AUDIT_ROOT / "provincial_2025_eo_pvl_match_detail.csv"
)


@dataclass(frozen=True)
class Election:
    election_id: str
    turnout_csv: Path
    location_label_status: str
    location_source_note: str
    source_url: str


ELECTIONS = (
    Election(
        election_id="municipal_2023_mayor",
        turnout_csv=ELECTION_ROOT
        / "municipal_2023_mayor"
        / "turnout"
        / "toronto_municipal_2023_mayor_turnout_subdivisions.csv",
        location_label_status="location_name_available_address_missing",
        location_source_note=(
            "Processed polling_division_name comes from Toronto voter-statistics "
            "voting-place labels for ordinary rows, but no verified address or "
            "coordinate field is present in the repository."
        ),
        source_url="https://www.toronto.ca/city-government/elections/",
    ),
    Election(
        election_id="provincial_2025",
        turnout_csv=ELECTION_ROOT
        / "provincial_2025"
        / "turnout"
        / "toronto_provincial_2025_turnout_poll_divisions.csv",
        location_label_status="location_or_address_text_available_coordinates_missing",
        location_source_note=(
            "Processed polling_division_name is derived from Elections Ontario "
            "VotingPlaceAddressOrLocation. This is a location/address text field, "
            "not a verified coordinate field. Elections Ontario proposed voting "
            "location CSV exports were downloaded for Toronto districts, but they "
            "match only part of the mapped 2025 polling rows by district and "
            "location name, so they are not yet treated as a complete final "
            "poll-to-station source."
        ),
        source_url="https://www.elections.on.ca/",
    ),
    Election(
        election_id="federal_2025",
        turnout_csv=ELECTION_ROOT
        / "federal_2025"
        / "turnout"
        / "toronto_federal_2025_turnout_poll_divisions.csv",
        location_label_status="no_useful_polling_location_field",
        location_source_note=(
            "Processed polling_division_name mostly preserves the official "
            "Polling Division Name, which is commonly a generic label such as "
            "Toronto for ordinary polls. It should not be read as a polling "
            "station name or address."
        ),
        source_url="https://www.elections.ca/",
    ),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def number(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def transformer(source_epsg: int, target_epsg: int):
    source = osr.SpatialReference()
    source.ImportFromEPSG(source_epsg)
    source.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    target = osr.SpatialReference()
    target.ImportFromEPSG(target_epsg)
    target.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return osr.CoordinateTransformation(source, target)


TO_WORKING = transformer(4326, WORKING_EPSG)
TO_WGS84 = transformer(WORKING_EPSG, 4326)


def polygonal_parts(geometry):
    flat_type = ogr.GT_Flatten(geometry.GetGeometryType())
    if flat_type == ogr.wkbPolygon:
        return [geometry.Clone()]
    if flat_type == ogr.wkbMultiPolygon:
        return [geometry.GetGeometryRef(i).Clone() for i in range(geometry.GetGeometryCount())]
    if flat_type == ogr.wkbGeometryCollection:
        parts = []
        for i in range(geometry.GetGeometryCount()):
            parts.extend(polygonal_parts(geometry.GetGeometryRef(i)))
        return parts
    return []


def make_valid_polygonal(geometry: ogr.Geometry | None) -> ogr.Geometry | None:
    if geometry is None or geometry.IsEmpty():
        return None
    geometry = geometry.Clone()
    geometry.Transform(TO_WORKING)
    if not geometry.IsValid():
        geometry = geometry.MakeValid()
    output = ogr.Geometry(ogr.wkbMultiPolygon)
    for part in polygonal_parts(geometry):
        if not part.IsEmpty() and part.GetArea() > 0:
            output.AddGeometry(part)
    return output if output.GetGeometryCount() else None


def geometry_from_text(text: str) -> ogr.Geometry | None:
    if not text or not text.strip():
        return None
    return make_valid_polygonal(ogr.CreateGeometryFromJson(text))


def point_to_lon_lat(point: ogr.Geometry | None) -> tuple[str, str]:
    if point is None or point.IsEmpty():
        return "", ""
    point = point.Clone()
    point.Transform(TO_WGS84)
    return f"{point.GetX():.8f}", f"{point.GetY():.8f}"


def location_id(election_id: str, label: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "_" for ch in label.strip())
    normalized = "_".join(part for part in normalized.split("_") if part)
    return f"{election_id}__{normalized[:80]}" if normalized else ""


def normalized_name(value: str) -> str:
    text = value.upper().replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return " ".join(part for part in text.split() if part and part != "THE")


def address_point_lon_lat(row: dict[str, str]) -> tuple[float, float] | None:
    try:
        geometry = json.loads(row.get("geometry", ""))
        lon, lat = geometry["coordinates"]
        return float(lon), float(lat)
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        return None


def load_address_point_label_indexes() -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    by_place: dict[str, list[dict]] = {}
    by_address: dict[str, list[dict]] = {}
    if not OPEN_TORONTO_ADDRESS_POINTS_CSV.exists():
        return by_place, by_address
    for row in read_csv(OPEN_TORONTO_ADDRESS_POINTS_CSV):
        for field in ("PLACE_NAME", "PLACE_NAME_ALL"):
            key = normalized_name(row.get(field, ""))
            if key:
                by_place.setdefault(key, []).append(row)
        key = normalized_name(row.get("ADDRESS_FULL", ""))
        if key:
            by_address.setdefault(key, []).append(row)
    return by_place, by_address


def closest_address_point(
    records: list[dict], poll_geometry: ogr.Geometry | None
) -> dict | None:
    usable = [(row, address_point_lon_lat(row)) for row in records]
    usable = [(row, lon_lat) for row, lon_lat in usable if lon_lat is not None]
    if not usable:
        return None
    if len(usable) == 1 or poll_geometry is None:
        return usable[0][0]
    surface = poll_geometry.PointOnSurface()
    best_row = usable[0][0]
    best_distance = math.inf
    for row, lon_lat in usable:
        point = station_point_working(lon_lat[0], lon_lat[1])
        if point is None:
            continue
        distance = surface.Distance(point)
        if distance < best_distance:
            best_row = row
            best_distance = distance
    return best_row


def open_toronto_label_match(
    row: dict[str, str],
    by_place: dict[str, list[dict]],
    by_address: dict[str, list[dict]],
) -> dict | None:
    label = row.get("polling_division_name", "")
    key = normalized_name(label)
    if not key:
        return None
    match_type = ""
    records = by_place.get(key, [])
    if records:
        match_type = "official_return_label_exact_place_name_match"
    else:
        records = by_address.get(key, [])
        if records:
            match_type = "official_return_label_exact_civic_address_match"
    if not records:
        return None
    address_row = closest_address_point(records, geometry_from_text(row.get("geometry", "")))
    if not address_row:
        return None
    lon_lat = address_point_lon_lat(address_row)
    if lon_lat is None:
        return None
    return {
        "source_row": {
            "voting_location_name": label,
            "voting_location_address": address_row.get("ADDRESS_FULL", ""),
            "address_point_match_address_full": address_row.get("ADDRESS_FULL", ""),
            "address_point_match_place_name": address_row.get("PLACE_NAME_ALL")
            or address_row.get("PLACE_NAME", ""),
            "address_point_id": address_row.get("ADDRESS_POINT_ID", ""),
            "address_point_objectid": address_row.get("_id", ""),
            "geocode_method": f"{match_type}_open_toronto_address_point",
            "geocode_source_url": "https://open.toronto.ca/dataset/address-points/",
        },
        "lon": lon_lat[0],
        "lat": lon_lat[1],
        "assignment_type": match_type,
        "confidence": "exact_official_address_point_label_match",
        "source_name": "Open Toronto Address Points",
        "source_url": "https://open.toronto.ca/dataset/address-points/",
    }


def load_provincial_pvl_rows() -> list[dict[str, str]]:
    rows = []
    for path in sorted(PROVINCIAL_2025_PVL_ROOT.glob("eo_pvl_*.csv")):
        district = str(int(path.stem.split("_")[-1]))
        for row in read_csv(path):
            row = dict(row)
            row["electoral_district_number"] = district
            row["source_file"] = path.name
            rows.append(row)
    return rows


def name_similarity(left: str, right: str) -> float:
    left_tokens = set(normalized_name(left).split())
    right_tokens = set(normalized_name(right).split())
    if not left_tokens or not right_tokens:
        return 0.0
    return 2 * len(left_tokens & right_tokens) / (len(left_tokens) + len(right_tokens))


def municipal_poll_code(row: dict[str, str]) -> str:
    district = str(row.get("electoral_district_number", "")).strip().zfill(2)
    division = str(row.get("polling_division_number", "")).strip().zfill(3)
    return f"{district}{division}"


def load_municipal_locations() -> dict[str, dict]:
    if not MUNICIPAL_2023_LOCATION_CSV.exists():
        return {}
    locations = {}
    for row in read_csv(MUNICIPAL_2023_LOCATION_CSV):
        code = str(row.get("POINT_LONG_CODE", "")).strip().zfill(5)
        geometry_text = row.get("geometry", "")
        lon = lat = ""
        if geometry_text:
            geometry = json.loads(geometry_text)
            lon, lat = geometry["coordinates"]
        locations[code] = {
            "source_row": row,
            "lon": float(lon) if lon != "" else None,
            "lat": float(lat) if lat != "" else None,
        }
    return locations


def load_provincial_geocoded_locations(rows: list[dict[str, str]]) -> dict[str, dict]:
    if not PROVINCIAL_2025_GEOCODED_CSV.exists():
        return {}
    geocoded = {}
    for row in read_csv(PROVINCIAL_2025_GEOCODED_CSV):
        if not row.get("polling_location_lon") or not row.get("polling_location_lat"):
            continue
        key = (
            str(int(row["electoral_district_number"])),
            normalized_name(row.get("voting_location_name", "")),
        )
        geocoded[key] = row

    match_status = {}
    if PROVINCIAL_2025_MATCH_DETAIL_CSV.exists():
        for row in read_csv(PROVINCIAL_2025_MATCH_DETAIL_CSV):
            match_status[row.get("poll_id", "")] = row.get("match_status", "")
    by_place, by_address = load_address_point_label_indexes()
    locations = {}
    for row in rows:
        if not row.get("geometry", "").strip():
            continue
        district = str(int(row.get("electoral_district_number", "0")))
        label = row.get("polling_division_name", "")
        match = geocoded.get((district, normalized_name(label)))
        poll_id = row.get("poll_id", "")
        if match:
            locations[poll_id] = {
                "source_row": match,
                "lon": float(match["polling_location_lon"]),
                "lat": float(match["polling_location_lat"]),
                "assignment_type": "exact_proposed_location_name_match_address_point",
                "confidence": "exact_name_match_address_point",
                "source_name": "Elections Ontario proposed voting locations + Open Toronto Address Points",
                "source_url": match.get("geocode_source_url", ""),
            }
            continue

        status = match_status.get(poll_id, "")
        if status in {"exact_name_match", "no_reliable_candidate"}:
            label_match = open_toronto_label_match(row, by_place, by_address)
            if label_match:
                locations[poll_id] = label_match
                continue
    return locations


def station_point_working(lon: float | None, lat: float | None) -> ogr.Geometry | None:
    if lon is None or lat is None:
        return None
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(float(lon), float(lat))
    point.Transform(TO_WORKING)
    return point


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_den == 0 or y_den == 0:
        return None
    return numerator / (x_den * y_den)


def ranks(values: list[float]) -> list[float]:
    order = sorted(enumerate(values), key=lambda item: item[1])
    result = [0.0] * len(values)
    index = 0
    while index < len(order):
        end = index + 1
        while end < len(order) and order[end][1] == order[index][1]:
            end += 1
        rank = (index + 1 + end) / 2
        for original_index, _ in order[index:end]:
            result[original_index] = rank
        index = end
    return result


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    return pearson(ranks(xs), ranks(ys))


def build_for_election(election: Election) -> dict:
    rows = read_csv(election.turnout_csv)
    mapped_rows = [row for row in rows if row.get("geometry", "").strip()]
    municipal_locations = (
        load_municipal_locations() if election.election_id == "municipal_2023_mayor" else {}
    )
    provincial_locations = (
        load_provincial_geocoded_locations(rows)
        if election.election_id == "provincial_2025"
        else {}
    )
    locations = {}
    links = []
    metrics = []
    geojson_features = []
    area_turnout_xs = []
    area_turnout_ys = []

    for row in mapped_rows:
        vote_type = row.get("vote_type", "")
        geometry = geometry_from_text(row.get("geometry", ""))
        has_geometry = geometry is not None
        votes = number(row.get("number_of_votes"))
        electors = number(row.get("number_of_electors"))
        turnout = number(row.get("proportion_of_turnout"))
        label = row.get("polling_division_name", "").strip()
        exact_location = None
        if election.election_id == "municipal_2023_mayor":
            exact_location = municipal_locations.get(municipal_poll_code(row))
        elif election.election_id == "provincial_2025":
            exact_location = provincial_locations.get(row.get("poll_id", ""))

        use_label = election.election_id != "federal_2025" and bool(label)
        loc_id = ""
        if exact_location:
            loc_id = (
                f"{election.election_id}__{municipal_poll_code(row)}"
                if election.election_id == "municipal_2023_mayor"
                else location_id(
                    election.election_id,
                    "|".join(
                        [
                            row.get("electoral_district_number", ""),
                            exact_location["source_row"].get("voting_location_name", label),
                        ]
                    ),
                )
            )
        elif use_label:
            loc_id = location_id(election.election_id, label)
        if loc_id and loc_id not in locations:
            source_row = exact_location["source_row"] if exact_location else {}
            source_note = election.location_source_note
            if exact_location and election.election_id == "municipal_2023_mayor":
                geocode_method = "official_open_toronto_point"
                geocode_confidence = "verified_official_point"
                source_name = "Open Toronto Elections Voting Locations"
                source_url = "https://open.toronto.ca/dataset/elections-voting-locations/"
                source_date = "2026-02-20"
                source_license = "Open Government Licence - Toronto"
                location_name = source_row.get("POINT_NAME") or label
                address_raw = source_row.get("ADDRESS_FULL", "")
                address_standardized = source_row.get("ADDRESS_FULL", "")
                source_polling_code = municipal_poll_code(row)
                source_voter_count = source_row.get("VOTER_COUNT", "")
            elif exact_location and election.election_id == "provincial_2025":
                geocode_method = source_row.get(
                    "geocode_method",
                    "exact_eo_proposed_location_name_match_open_toronto_address_point",
                )
                geocode_confidence = exact_location.get(
                    "confidence", "exact_name_match_address_point"
                )
                source_name = exact_location.get(
                    "source_name",
                    "Elections Ontario proposed voting locations + Open Toronto Address Points",
                )
                source_url = exact_location.get("source_url") or source_row.get(
                    "geocode_source_url", ""
                )
                source_date = ""
                source_license = "Open Government Licence - Ontario; Open Government Licence - Toronto"
                location_name = source_row.get("voting_location_name") or label
                address_raw = source_row.get("voting_location_address", "")
                address_standardized = source_row.get("address_point_match_address_full", "")
                source_polling_code = ""
                source_voter_count = ""
            else:
                geocode_method = "not_geocoded"
                geocode_confidence = "none"
                source_name = "current_processed_election_label"
                source_url = election.source_url
                source_date = ""
                source_license = ""
                location_name = label
                address_raw = label if election.election_id == "provincial_2025" else ""
                address_standardized = ""
                source_polling_code = ""
                source_voter_count = ""
            locations[loc_id] = {
                "election_id": election.election_id,
                "polling_location_id": loc_id,
                "polling_location_name": location_name,
                "polling_location_address_raw": address_raw,
                "polling_location_address_standardized": address_standardized,
                "polling_location_lat": f"{exact_location['lat']:.8f}" if exact_location else "",
                "polling_location_lon": f"{exact_location['lon']:.8f}" if exact_location else "",
                "polling_location_source": source_name,
                "polling_location_source_url": source_url,
                "polling_location_source_date": source_date,
                "polling_location_geocode_method": geocode_method,
                "polling_location_geocode_provider": "",
                "polling_location_geocode_confidence": geocode_confidence,
                "polling_location_license": source_license,
                "polling_location_notes": source_note,
                "source_polling_code": source_polling_code,
                "source_voter_count": source_voter_count,
            }

        exclude_reasons = []
        if votes is None:
            exclude_reasons.append("missing_votes")
        if electors is None or electors <= 0:
            exclude_reasons.append("missing_or_zero_electors")
        if turnout is None:
            exclude_reasons.append("missing_turnout")
        if not loc_id:
            exclude_reasons.append("no_verified_polling_location")
        elif not exact_location:
            exclude_reasons.append("polling_location_not_geocoded")
        if vote_type != "election_day":
            exclude_reasons.append("non_election_day_reporting_bucket")

        assignment_type = "unavailable"
        if exact_location:
            assignment_type = "official_point_one_to_one"
            if election.election_id == "provincial_2025":
                assignment_type = exact_location.get(
                    "assignment_type", "exact_proposed_location_name_match_address_point"
                )
        elif loc_id:
            assignment_type = "candidate_location_label_only"
        if vote_type != "election_day":
            assignment_type = f"{vote_type}_bucket"

        links.append(
            {
                "election_id": election.election_id,
                "poll_id": row.get("poll_id", ""),
                "electoral_district_number": row.get("electoral_district_number", ""),
                "polling_division_number": row.get("polling_division_number", ""),
                "vote_type": vote_type,
                "polling_location_id": loc_id,
                "location_assignment_type": assignment_type,
                "location_assignment_source": "Open Toronto Elections Voting Locations"
                if exact_location and election.election_id == "municipal_2023_mayor"
                else exact_location.get(
                    "source_name",
                    "Elections Ontario proposed voting locations + Open Toronto Address Points",
                )
                if exact_location and election.election_id == "provincial_2025"
                else ("current_processed_election_label" if loc_id else "none"),
                "location_assignment_confidence": "high"
                if exact_location
                else ("low" if loc_id else "none"),
                "location_uncertain_flag": "0" if exact_location else "1",
                "exclude_from_distance_model_flag": "1" if exclude_reasons else "0",
                "exclude_reason": ";".join(exclude_reasons),
            }
        )

        area_km2 = ""
        centroid_lon = centroid_lat = surface_lon = surface_lat = ""
        feature_geometry = None
        station_point = station_point_working(
            exact_location["lon"] if exact_location else None,
            exact_location["lat"] if exact_location else None,
        )
        point_surface_distance = ""
        centroid_distance = ""
        if geometry is not None:
            area_km2 = f"{geometry.GetArea() / 1_000_000:.8f}"
            centroid = geometry.Centroid()
            surface = geometry.PointOnSurface()
            centroid_lon, centroid_lat = point_to_lon_lat(centroid)
            surface_lon, surface_lat = point_to_lon_lat(surface)
            if station_point is not None:
                point_surface_distance = f"{surface.Distance(station_point):.3f}"
                centroid_distance = f"{centroid.Distance(station_point):.3f}"
            feature_geometry = geometry.Clone()
            feature_geometry.Transform(TO_WGS84)
            if turnout is not None and area_km2:
                area_turnout_xs.append(float(area_km2))
                area_turnout_ys.append(turnout)

        metric = {
            "election_id": election.election_id,
            "poll_id": row.get("poll_id", ""),
            "electoral_district_number": row.get("electoral_district_number", ""),
            "polling_division_number": row.get("polling_division_number", ""),
            "polling_division_name": label,
            "vote_type": vote_type,
            "number_of_votes": row.get("number_of_votes", ""),
            "number_of_electors": row.get("number_of_electors", ""),
            "proportion_of_turnout": row.get("proportion_of_turnout", ""),
            "has_poll_geometry": "1" if has_geometry else "0",
            "polling_location_id": loc_id,
            "has_polling_location": "1" if loc_id else "0",
            "poll_area_km2": area_km2,
            "poll_centroid_lon": centroid_lon,
            "poll_centroid_lat": centroid_lat,
            "poll_point_on_surface_lon": surface_lon,
            "poll_point_on_surface_lat": surface_lat,
            "polling_location_lon": f"{exact_location['lon']:.8f}" if exact_location else "",
            "polling_location_lat": f"{exact_location['lat']:.8f}" if exact_location else "",
            "poll_point_on_surface_distance_m": point_surface_distance,
            "poll_centroid_distance_m": centroid_distance,
            "population_weighted_distance_m": "",
            "walk_distance_m": "",
            "walk_time_min": "",
            "location_assignment_type": assignment_type,
            "location_uncertain_flag": "0" if exact_location else "1",
            "exclude_from_distance_model_flag": "1" if exclude_reasons else "0",
            "exclude_reason": ";".join(exclude_reasons),
        }
        metrics.append(metric)

        if feature_geometry is not None:
            properties = {key: value for key, value in metric.items() if key != "geometry"}
            geojson_features.append(
                {
                    "type": "Feature",
                    "properties": properties,
                    "geometry": json.loads(feature_geometry.ExportToJson()),
                }
            )

    location_rows = list(locations.values())
    location_geojson = {
        "type": "FeatureCollection",
        "features": [],
    }
    metrics_geojson = {"type": "FeatureCollection", "features": geojson_features}

    source_audit = {
        "election_id": election.election_id,
        "source": election.source_url,
        "coverage": "mapped polling divisions only",
        "location_label_status": election.location_label_status,
        "coordinates_available_in_repo": "1"
        if any(location.get("polling_location_lon") and location.get("polling_location_lat") for location in location_rows)
        else "0",
        "addresses_available_in_repo": "1"
        if any(location.get("polling_location_address_raw") for location in location_rows)
        else "0",
        "missing_records": str(
            sum(
                1
                for link in links
                if link["location_assignment_confidence"] != "high"
            )
        ),
        "confidence": "high"
        if election.election_id == "municipal_2023_mayor"
        else "partial"
        if any(location.get("polling_location_lon") and location.get("polling_location_lat") for location in location_rows)
        else "low",
        "notes": election.location_source_note,
    }
    if election.election_id == "municipal_2023_mayor":
        source_audit["source"] = "https://open.toronto.ca/dataset/elections-voting-locations/"
        source_audit["notes"] = (
            "Open Toronto Elections Voting Locations has 1,445 point records for "
            "the 2023 mayoral by-election. POINT_LONG_CODE matched all 1,445 "
            "mapped municipal polling-subdivision rows."
        )

    model_ready = [
        metric
        for metric in metrics
        if metric["exclude_from_distance_model_flag"] != "1"
    ]
    summary = {
        "election_id": election.election_id,
        "rows": len(rows),
        "target_mapped_rows": len(mapped_rows),
        "mapped_rows": sum(1 for metric in metrics if metric["has_poll_geometry"] == "1"),
        "rows_with_votes": sum(1 for row in rows if number(row.get("number_of_votes")) is not None),
        "rows_with_electors": sum(1 for row in rows if number(row.get("number_of_electors")) is not None),
        "candidate_location_labels": len(location_rows),
        "model_ready_distance_rows": len(model_ready),
        "area_turnout_pearson": pearson(area_turnout_xs, area_turnout_ys),
        "area_turnout_spearman": spearman(area_turnout_xs, area_turnout_ys),
    }

    write_csv(
        LOCATION_ROOT / f"{election.election_id}_polling_locations.csv",
        location_rows,
        [
            "election_id",
            "polling_location_id",
            "polling_location_name",
            "polling_location_address_raw",
            "polling_location_address_standardized",
            "polling_location_lat",
            "polling_location_lon",
            "polling_location_source",
            "polling_location_source_url",
            "polling_location_source_date",
            "polling_location_geocode_method",
            "polling_location_geocode_provider",
            "polling_location_geocode_confidence",
            "polling_location_license",
            "polling_location_notes",
            "source_polling_code",
            "source_voter_count",
        ],
    )
    write_json(
        LOCATION_ROOT / f"{election.election_id}_polling_locations.geojson",
        location_geojson,
    )
    write_csv(LINK_ROOT / f"{election.election_id}_poll_to_location_links.csv", links)
    write_csv(
        METRIC_ROOT / f"{election.election_id}_poll_accessibility_metrics.csv",
        metrics,
    )
    write_json(
        METRIC_ROOT / f"{election.election_id}_poll_accessibility_metrics.geojson",
        metrics_geojson,
    )
    write_json(MAP_ROOT / f"{election.election_id}_poll_accessibility_map.geojson", metrics_geojson)
    write_csv(AUDIT_ROOT / f"{election.election_id}_polling_location_source_audit.csv", [source_audit])
    write_csv(
        AUDIT_ROOT / f"{election.election_id}_distance_model_exclusion_audit.csv",
        links,
    )

    return summary


def format_float(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def write_report(summaries: list[dict]):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Polling Station Accessibility Audit Summary",
        "",
        "## Main Finding",
        "",
        "Municipal 2023 polling-station coordinates were found and recorded for",
        "all mapped municipal polling-subdivision rows. Provincial 2025 and",
        "Federal 2025 remain unresolved as complete distance-analysis datasets.",
        "Provincial 2025 has a partial official-source path through Elections",
        "Ontario proposed voting-location CSV exports, Open Toronto Address",
        "Points, and exact official-return label recoveries. These sources still",
        "do not cover every mapped 2025 polling row. Federal 2025 still lacks a",
        "bulk official source tying mapped poll divisions to polling-place coordinates.",
        "",
        "## Election-Level Readiness",
        "",
        "| Election | Rows | Mapped rows | Candidate location labels | Distance-model-ready rows | Area/turnout Pearson | Area/turnout Spearman |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        lines.append(
            "| {election_id} | {rows} | {mapped_rows} | {candidate_location_labels} | "
            "{model_ready_distance_rows} | {pearson} | {spearman} |".format(
                election_id=summary["election_id"],
                rows=summary["rows"],
                mapped_rows=summary["mapped_rows"],
                candidate_location_labels=summary["candidate_location_labels"],
                model_ready_distance_rows=summary["model_ready_distance_rows"],
                pearson=format_float(summary["area_turnout_pearson"]),
                spearman=format_float(summary["area_turnout_spearman"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Municipal 2023 is ready for an exploratory distance-vs-turnout pass.",
            "  The official Open Toronto `Elections Voting Locations` point table",
            "  has 1,445 records for 2023 and matches all 1,445 mapped municipal",
            "  polling-subdivision rows by ward/subdivision code.",
            "- Provincial 2025 has the strongest starting point because the raw official",
            "  return includes `VotingPlaceAddressOrLocation`. Elections Ontario",
            "  proposed voting-location exports provide names and addresses for many",
            "  Toronto locations, and Open Toronto Address Points can geocode those",
            "  addresses. Where proposed-location matching fails, exact Open Toronto",
            "  place-name or civic-address matches to official-return labels are used.",
            "  Fuzzy proposed-location candidates remain review leads only.",
            "- Federal 2025 is the weakest starting point: the processed ordinary poll",
            "  label is usually not a polling-place address, so an additional official",
            "  or archived source is needed.",
            "- Poll area can be computed now and is included as a possible accessibility",
            "  proxy. It should not be treated as a substitute for polling-station",
            "  distance because large polling areas may reflect land-use/geography,",
            "  apartment density, institutional voting, or district design choices.",
            "",
            "## Possible Covariates Worth Adding Later",
            "",
            "- density or apartment share",
            "- age composition",
            "- income or deprivation measures",
            "- transit access",
            "- car ownership, if available",
            "- advance/mail/special voting availability",
            "- riding or ward fixed effects",
            "",
            "## Next Step",
            "",
            "Proceed with municipal and partial provincial exploratory analysis.",
            "For federal analysis, locate an official polling-place coordinate table",
            "or a defensible address source before estimating distances.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_federal_2025_source_search_audit():
    rows = [
        {
            "election_id": "federal_2025",
            "source_name": "Local Elections Canada 2025 poll-by-poll CSV downloads",
            "source_url": "data/toronto_election_turnout/elections/raw/source_downloads/federal_csv/",
            "official_source": "1",
            "coverage": "Toronto federal electoral districts collected in the repository",
            "contains_polling_place_address": "0",
            "contains_polling_place_coordinates": "0",
            "contains_polling_division_geometry": "0",
            "status": "result_rows_only",
            "notes": (
                "The raw CSV header includes electoral district number/name, "
                "polling division number/name, candidate vote columns, rejected "
                "ballots, total votes, and electors. It does not include a "
                "polling-place building name, street address, latitude, or longitude."
            ),
        },
        {
            "election_id": "federal_2025",
            "source_name": "45th General Election: Official Voting Results",
            "source_url": "https://www.elections.ca/res/rep/off/ovrGE45/home.html",
            "official_source": "1",
            "coverage": "Canada; official result tables and reports",
            "contains_polling_place_address": "0",
            "contains_polling_place_coordinates": "0",
            "contains_polling_division_geometry": "0",
            "status": "official_results_only",
            "notes": (
                "Official turnout/result pages are suitable for vote and turnout "
                "validation, but they do not provide a public bulk table linking "
                "each polling division to a polling-place building coordinate."
            ),
        },
        {
            "election_id": "federal_2025",
            "source_name": "Electoral Geography Boundary Files (45th General Election) - Canada 2025",
            "source_url": "https://open.canada.ca/data/en/dataset/97a2a33c-54cc-4f2e-82c1-047ad8212f05",
            "official_source": "1",
            "coverage": "Canada; 2025 polling division, advance polling district, and riding boundaries",
            "contains_polling_place_address": "0",
            "contains_polling_place_coordinates": "0",
            "contains_polling_division_geometry": "1",
            "status": "polygon_boundaries_only",
            "notes": (
                "The official 2025 geography package provides polygon boundaries "
                "and map services. It does not include the assigned voting building "
                "for each polling division."
            ),
        },
        {
            "election_id": "federal_2025",
            "source_name": "Elections Canada Voter Information Service",
            "source_url": "https://www.elections.ca/Scripts/vis/FindED?L=e&PAGEID=20",
            "official_source": "1",
            "coverage": "Current voter/district lookup interface",
            "contains_polling_place_address": "0",
            "contains_polling_place_coordinates": "0",
            "contains_polling_division_geometry": "0",
            "status": "not_bulk_post_election_data",
            "notes": (
                "The public lookup can expose polling-place information during an "
                "active election, but no reproducible post-election bulk 2025 "
                "poll-to-building coordinate table was found through this interface. "
                "A postal-code probe using M5V 3A8 returned the Spadina--Harbourfront "
                "district profile and last-election information, but no polling-place "
                "building/address. A second probe using a representative point from "
                "federal_2025|35100|1|election_day reverse-geocoded to M5X 2A1, and "
                "VIS required a full civic-address form before district resolution; "
                "it still did not expose a polling-place result through the tested "
                "post-election route."
            ),
        },
    ]
    write_csv(AUDIT_ROOT / "federal_2025_polling_location_source_search_audit.csv", rows)


def write_provincial_pvl_match_audit():
    provincial = next(election for election in ELECTIONS if election.election_id == "provincial_2025")
    mapped_rows = [
        row for row in read_csv(provincial.turnout_csv) if row.get("geometry", "").strip()
    ]
    pvl_rows = load_provincial_pvl_rows()
    pvl_by_district: dict[str, list[dict[str, str]]] = {}
    for row in pvl_rows:
        pvl_by_district.setdefault(row["electoral_district_number"], []).append(row)

    detail_rows = []
    exact_matches = 0
    fuzzy_candidates = 0
    no_candidate = 0
    for row in mapped_rows:
        district = str(int(row.get("electoral_district_number", "0")))
        label = row.get("polling_division_name", "")
        candidates = pvl_by_district.get(district, [])
        exact = [
            candidate
            for candidate in candidates
            if normalized_name(candidate.get("Voting Location Name", ""))
            == normalized_name(label)
        ]
        best = None
        best_score = 0.0
        for candidate in candidates:
            score = name_similarity(label, candidate.get("Voting Location Name", ""))
            if score > best_score:
                best = candidate
                best_score = score
        if exact:
            status = "exact_name_match"
            exact_matches += 1
            best = exact[0]
            best_score = 1.0
        elif best and best_score >= 0.72:
            status = "fuzzy_candidate_review_required"
            fuzzy_candidates += 1
        else:
            status = "no_reliable_candidate"
            no_candidate += 1
        detail_rows.append(
            {
                "poll_id": row.get("poll_id", ""),
                "electoral_district_number": district,
                "polling_division_number": row.get("polling_division_number", ""),
                "processed_polling_division_name": label,
                "match_status": status,
                "best_pvl_name": best.get("Voting Location Name", "") if best else "",
                "best_pvl_address": best.get("Voting Location Address", "") if best else "",
                "best_name_token_similarity": f"{best_score:.4f}" if best else "",
                "source_file": best.get("source_file", "") if best else "",
            }
        )

    summary = [
        {
            "election_id": "provincial_2025",
            "mapped_poll_rows": len(mapped_rows),
            "eo_pvl_rows": len(pvl_rows),
            "exact_name_match_rows": exact_matches,
            "fuzzy_candidate_review_required_rows": fuzzy_candidates,
            "no_reliable_candidate_rows": no_candidate,
            "accepted_as_complete_poll_to_station_source": "0",
            "notes": (
                "Elections Ontario proposed voting-location files provide names "
                "and addresses, but exact district/name matching does not cover "
                "all mapped 2025 polling rows. Fuzzy candidates are for manual "
                "review only and are not used as accepted station assignments."
            ),
        }
    ]
    write_csv(AUDIT_ROOT / "provincial_2025_eo_pvl_match_summary.csv", summary)
    write_csv(AUDIT_ROOT / "provincial_2025_eo_pvl_match_detail.csv", detail_rows)


def main():
    summaries = [build_for_election(election) for election in ELECTIONS]
    write_provincial_pvl_match_audit()
    write_federal_2025_source_search_audit()
    write_csv(AUDIT_ROOT / "accessibility_readiness_summary.csv", summaries)
    write_json(AUDIT_ROOT / "accessibility_readiness_summary.json", summaries)
    write_report(summaries)
    print(f"Wrote accessibility outputs under {OUTPUT_ROOT}")
    print(f"Wrote summary report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
