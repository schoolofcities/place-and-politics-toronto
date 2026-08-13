"""Collect raw non-Census datasets for Blocks 4-5.

This is a data acquisition script only. It does not derive variables,
aggregate observations, calculate accessibility, or perform spatial joins.
"""

from __future__ import annotations

import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
VARIABLES_RAW = DATA_ROOT / "variables" / "raw"
VARIABLES_METADATA = DATA_ROOT / "variables" / "metadata"
VARIABLES_DOCS = DATA_ROOT / "variables" / "documentation"
PROJECT_METADATA = DATA_ROOT / "metadata"
ELECTIONS_RAW = DATA_ROOT / "elections" / "raw"
ACCESSIBILITY_RAW = DATA_ROOT / "accessibility" / "raw"

TOD_API = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id={package}"
TOD_LICENSE_NOTE = "Open Government Licence - Toronto; package license field may be 'License not specified' in CKAN metadata."
TTS_REPO_API = "https://api.github.com/repos/schoolofcities/transportation-tomorrow-survey"
TTS_LITERATURE = "Marshall & Siemiatycki (2014); Couture, Bherer & Breux (2014); Geys (2006); Cancela & Geys (2016); McGregor (2018); Breux, Couture & Koop (2017); Breux, Couture & Goodman (2017)"
TOD_LITERATURE = TTS_LITERATURE

DOWNLOAD_DATE = date.today().isoformat()


TORONTO_DATASETS = [
    {
        "variable_names": "311_requests_per_capita",
        "dataset_group": "311_service_requests",
        "package": "311-service-requests-customer-initiated",
        "destination": "toronto_open_data/311_service_requests_customer_initiated",
        "geographic_level": "service request record; address/intersection/service location fields",
        "temporal_coverage": "2023-2025 resources selected",
        "coordinate_reference_system": "Not explicit in ZIP metadata; verify during processing.",
        "notes": "Collected raw annual ZIP files for election-relevant years plus the readme. No aggregation performed.",
        "resources": [
            "311 Service Requests 2023",
            "311 Service Requests 2024",
            "311 Service Requests 2025",
            "311-service-requests-readme",
        ],
    },
    {
        "variable_names": "social_housing_share",
        "dataset_group": "social_housing",
        "package": "active-affordable-and-social-housing-units",
        "destination": "toronto_open_data/active_affordable_and_social_housing_units",
        "geographic_level": "tabular housing stock record",
        "temporal_coverage": "current active stock as published",
        "coordinate_reference_system": "No CRS expected unless geometry fields are present.",
        "notes": "Used Toronto Open Data because a direct StatCan social-housing stock dataset was not available for this non-Census acquisition task.",
        "resources": ["Social and Affordable Housing.csv", "Social and Affordable Housing.json"],
    },
    {
        "variable_names": "library_access_15m_walk_transit",
        "dataset_group": "libraries",
        "package": "library-branch-general-information",
        "destination": "toronto_open_data/library_branch_general_information",
        "geographic_level": "library branch point",
        "temporal_coverage": "current; 2023 branch information also available in package",
        "coordinate_reference_system": "EPSG:4326 for selected 4326 resources",
        "notes": "Collected branch attributes and geospatial files. No buffers or travel-time calculations.",
        "resources": [
            "tpl-branch-general-information-2023.csv",
            "tpl-branch-general-information - 4326.csv",
            "tpl-branch-general-information - 4326.geojson",
            "tpl-branch-general-information - 4326.gpkg",
        ],
    },
    {
        "variable_names": "community_centre_access; park_access",
        "dataset_group": "parks_recreation_facilities",
        "package": "parks-and-recreation-facilities",
        "destination": "toronto_open_data/parks_and_recreation_facilities",
        "geographic_level": "parks/recreation facility point",
        "temporal_coverage": "current as published",
        "coordinate_reference_system": "EPSG:4326 for selected 4326 resources",
        "notes": "Supervisor-recommended source for community centres and candidate source for park access.",
        "resources": [
            "Parks and Recreation Facilities - 4326.csv",
            "Parks and Recreation Facilities - 4326.geojson",
            "Parks and Recreation Facilities - 4326.gpkg",
        ],
    },
    {
        "variable_names": "park_access",
        "dataset_group": "parks",
        "package": "parks",
        "destination": "toronto_open_data/parks",
        "geographic_level": "park polygon",
        "temporal_coverage": "current/legacy as published; CKAN package marked retired",
        "coordinate_reference_system": "WGS84 per resource name",
        "notes": "Collected official Toronto Open Data park boundary shapefile before considering OpenStreetMap.",
        "resources": ["parks-wgs84"],
    },
    {
        "variable_names": "school_location_reference",
        "dataset_group": "school_locations",
        "package": "school-locations-all-types",
        "destination": "toronto_open_data/school_locations_all_types",
        "geographic_level": "school point",
        "temporal_coverage": "current as published",
        "coordinate_reference_system": "EPSG:4326 for selected 4326 resources",
        "notes": "External school-location reference only. No school-age population or accessibility calculations.",
        "resources": [
            "School locations-all types data - 4326.csv",
            "School locations-all types data - 4326.geojson",
            "School locations-all types data - 4326.gpkg",
        ],
    },
    {
        "variable_names": "road_safety_exposure",
        "dataset_group": "road_safety",
        "package": "motor-vehicle-collisions-involving-killed-or-seriously-injured-persons",
        "destination": "toronto_open_data/ksi_collisions",
        "geographic_level": "collision point/event",
        "temporal_coverage": "since 2006 as described by package",
        "coordinate_reference_system": "EPSG:4326 for selected 4326 resources",
        "notes": "Collected KSI collision candidate dataset. No counts, densities, or exposure measures computed.",
        "resources": [
            "Motor Vehicle Collisions with KSI Data - 4326.csv",
            "Motor Vehicle Collisions with KSI Data - 4326.geojson",
            "Motor Vehicle Collisions with KSI Data - 4326.gpkg",
        ],
    },
    {
        "variable_names": "development_applications_per_capita",
        "dataset_group": "development_applications",
        "package": "development-applications",
        "destination": "toronto_open_data/development_applications",
        "geographic_level": "planning application record",
        "temporal_coverage": "current/open applications as published",
        "coordinate_reference_system": "No CRS expected unless coordinate fields are present.",
        "notes": "Collected current Development Applications CSV only. No temporal filtering or aggregation.",
        "resources": ["Development Applications.csv"],
    },
    {
        "variable_names": "development_applications_per_capita",
        "dataset_group": "committee_of_adjustment",
        "package": "committee-of-adjustment-applications",
        "destination": "toronto_open_data/committee_of_adjustment_applications",
        "geographic_level": "committee application record",
        "temporal_coverage": "since 2017 plus closed 2023 where separately published",
        "coordinate_reference_system": "No CRS expected unless coordinate fields are present.",
        "notes": "Collected current since-2017 file and 2023 closed applications file. No filtering or aggregation.",
        "resources": [
            "Committee of Adjustments Applications since 2017.csv",
            "Closed Applications 2023.csv",
        ],
    },
    {
        "variable_names": "shelter_service_proximity",
        "dataset_group": "shelters",
        "package": "shelter-profile-information",
        "destination": "toronto_open_data/shelter_profile_information",
        "geographic_level": "shelter profile record",
        "temporal_coverage": "2010-2011 as published",
        "coordinate_reference_system": "Not applicable for tabular profile workbook.",
        "notes": "Collected profile workbooks with type, location, ward/former municipality, hours, and per diem rate fields.",
        "resources": ["shelter-profile-2011", "shelter-profile-2010", "readme"],
    },
    {
        "variable_names": "shelter_service_proximity",
        "dataset_group": "shelters",
        "package": "hostel-services-homeless-shelter-locations",
        "destination": "toronto_open_data/hostel_services_homeless_shelter_locations",
        "geographic_level": "shelter point/location",
        "temporal_coverage": "current/legacy as published",
        "coordinate_reference_system": "WGS84 per resource name",
        "notes": "Collected official shelter-location shapefile and readme. No proximity calculations.",
        "resources": ["shelter-locations-wgs84", "shelter-locations-readme"],
    },
]

TTS_FILES = [
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/metrics_tts2022.csv",
        "destination": "transportation_tomorrow_survey_2022",
        "geographic_level": "TTS zone or repository-defined metric geography",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "Not applicable for metrics table.",
        "notes": "Supervisor-recommended TTS metrics table.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/tts2022zones.geojson",
        "destination": "transportation_tomorrow_survey_2022",
        "geographic_level": "TTS zone polygon",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "GeoJSON CRS default EPSG:4326 unless documented otherwise.",
        "notes": "TTS zone geography.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/tts2022zones_data.geojson",
        "destination": "transportation_tomorrow_survey_2022",
        "geographic_level": "TTS zone polygon with data",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "GeoJSON CRS default EPSG:4326 unless documented otherwise.",
        "notes": "Zone geometry with repository-provided data fields.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/tts2022zones_data.pmtiles",
        "destination": "transportation_tomorrow_survey_2022",
        "geographic_level": "TTS zone vector tiles",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "Vector tile package; verify during processing.",
        "notes": "Repository map-ready raw tile artifact.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/test-data/tts-people-hhlds-vehicles.csv",
        "destination": "transportation_tomorrow_survey_2022/test-data",
        "geographic_level": "person/household/vehicle record or repository test-data geography",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "Not applicable for tabular survey extract.",
        "notes": "Household/person/vehicle file for vehicle-ownership source review. No indicators computed.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/readme.txt",
        "destination": "transportation_tomorrow_survey_2022",
        "geographic_level": "documentation",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "Not applicable.",
        "notes": "Repository data readme.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/vkt-notes.txt",
        "destination": "transportation_tomorrow_survey_2022",
        "geographic_level": "documentation",
        "temporal_coverage": "2022",
        "coordinate_reference_system": "Not applicable.",
        "notes": "Repository notes.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/layers/Lower_Tier.geojson",
        "destination": "transportation_tomorrow_survey_2022/layers",
        "geographic_level": "lower-tier municipal boundary",
        "temporal_coverage": "repository current",
        "coordinate_reference_system": "GeoJSON CRS default EPSG:4326 unless documented otherwise.",
        "notes": "Geographic lookup/context layer.",
    },
    {
        "variable_names": "transit_commute_share; no_car_household_share",
        "url": "https://raw.githubusercontent.com/schoolofcities/transportation-tomorrow-survey/main/data/layers/Upper_Single_Tier.geojson",
        "destination": "transportation_tomorrow_survey_2022/layers",
        "geographic_level": "upper/single-tier boundary",
        "temporal_coverage": "repository current",
        "coordinate_reference_system": "GeoJSON CRS default EPSG:4326 unless documented otherwise.",
        "notes": "Geographic lookup/context layer.",
    },
]


def request_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def filename_from_url(url: str) -> str:
    return Path(urlparse(url).path).name or "downloaded_resource"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> tuple[str, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return "existing", ""
    temp = destination.with_suffix(destination.suffix + ".download")
    try:
        with urllib.request.urlopen(url, timeout=180) as response, temp.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
        temp.rename(destination)
        return "downloaded", ""
    except Exception as exc:
        if temp.exists():
            temp.unlink()
        return "failed", repr(exc)


def resource_map(package_json: dict) -> dict[str, dict]:
    return {resource.get("name", ""): resource for resource in package_json.get("resources", [])}


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def validate_file(path: Path) -> dict:
    result = {"row_count": "", "header": "", "valid_zip": "", "validation_note": ""}
    if not path.exists():
        result["validation_note"] = "file missing"
        return result
    suffix = path.suffix.lower()
    if suffix == ".csv":
        try:
            with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
                reader = csv.reader(handle)
                header = next(reader, [])
                count = sum(1 for _ in reader)
            result["row_count"] = str(count)
            result["header"] = "|".join(header[:25])
            result["validation_note"] = "csv readable"
        except Exception as exc:
            result["validation_note"] = f"csv read failed: {exc!r}"
    elif suffix == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                result["valid_zip"] = "true" if bad is None else "false"
                result["validation_note"] = "zip readable" if bad is None else f"zip first bad file: {bad}"
        except Exception as exc:
            result["valid_zip"] = "false"
            result["validation_note"] = f"zip read failed: {exc!r}"
    else:
        result["validation_note"] = "downloaded; no parser validation attempted"
    return result


def collect_toronto_open_data() -> list[dict]:
    rows: list[dict] = []
    for item in TORONTO_DATASETS:
        package_id = item["package"]
        package_json = request_json(TOD_API.format(package=package_id))["result"]
        package_dir = VARIABLES_RAW / item["destination"]
        metadata_path = package_dir / f"{package_id}_package_show_{DOWNLOAD_DATE}.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        if not metadata_path.exists():
            metadata_path.write_text(json.dumps(package_json, indent=2), encoding="utf-8")
        resources = resource_map(package_json)
        for resource_name in item["resources"]:
            resource = resources.get(resource_name)
            if not resource:
                rows.append(
                    {
                        "dataset_name": package_json.get("title", package_id),
                        "variable_names": item["variable_names"],
                        "official_source": "Toronto Open Data",
                        "source_url": TOD_API.format(package=package_id),
                        "download_url": "",
                        "download_date": DOWNLOAD_DATE,
                        "license": package_json.get("license_title") or TOD_LICENSE_NOTE,
                        "update_frequency": package_json.get("refresh_rate") or package_json.get("frequency", ""),
                        "geographic_level": item["geographic_level"],
                        "temporal_coverage": item["temporal_coverage"],
                        "coordinate_reference_system": item["coordinate_reference_system"],
                        "original_filename": resource_name,
                        "local_path": "",
                        "download_status": "missing_resource",
                        "file_size_bytes": "",
                        "sha256": "",
                        "row_count": "",
                        "header": "",
                        "valid_zip": "",
                        "validation_note": "resource named in script was not found in package metadata",
                        "notes": item["notes"],
                    }
                )
                continue
            url = resource.get("url", "")
            filename = filename_from_url(url)
            local_path = package_dir / filename
            status, error = download(url, local_path)
            validation = validate_file(local_path)
            rows.append(
                {
                    "dataset_name": package_json.get("title", package_id),
                    "variable_names": item["variable_names"],
                    "official_source": "Toronto Open Data",
                    "source_url": f"https://open.toronto.ca/dataset/{package_id}/",
                    "download_url": url,
                    "download_date": DOWNLOAD_DATE,
                    "license": package_json.get("license_title") or TOD_LICENSE_NOTE,
                    "update_frequency": package_json.get("refresh_rate") or package_json.get("frequency", ""),
                    "geographic_level": item["geographic_level"],
                    "temporal_coverage": item["temporal_coverage"],
                    "coordinate_reference_system": item["coordinate_reference_system"],
                    "original_filename": filename,
                    "local_path": str(local_path.relative_to(REPO_ROOT)) if local_path.exists() else "",
                    "download_status": status,
                    "file_size_bytes": str(local_path.stat().st_size) if local_path.exists() else "",
                    "sha256": sha256(local_path) if local_path.exists() else "",
                    **validation,
                    "notes": item["notes"] + (f" Download error: {error}" if error else ""),
                }
            )
            time.sleep(0.1)
    return rows


def collect_tts() -> list[dict]:
    rows: list[dict] = []
    repo_metadata = request_json(TTS_REPO_API)
    license_metadata = {}
    try:
        license_metadata = request_json(TTS_REPO_API + "/license")
    except urllib.error.HTTPError:
        license_metadata = {"license": {"name": ""}}
    repo_dir = VARIABLES_RAW / "transportation_tomorrow_survey_2022"
    repo_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = repo_dir / f"github_repo_metadata_{DOWNLOAD_DATE}.json"
    if not metadata_path.exists():
        metadata_path.write_text(
            json.dumps({"repository": repo_metadata, "license": license_metadata}, indent=2),
            encoding="utf-8",
        )
    for item in TTS_FILES:
        filename = filename_from_url(item["url"])
        local_path = VARIABLES_RAW / item["destination"] / filename
        status, error = download(item["url"], local_path)
        validation = validate_file(local_path)
        rows.append(
            {
                "dataset_name": "Transportation Tomorrow Survey 2022",
                "variable_names": item["variable_names"],
                "official_source": "School of Cities Transportation Tomorrow Survey repository",
                "source_url": "https://github.com/schoolofcities/transportation-tomorrow-survey/tree/main/data",
                "download_url": item["url"],
                "download_date": DOWNLOAD_DATE,
                "license": (license_metadata.get("license") or {}).get("name", ""),
                "update_frequency": "Repository updated as maintained",
                "geographic_level": item["geographic_level"],
                "temporal_coverage": item["temporal_coverage"],
                "coordinate_reference_system": item["coordinate_reference_system"],
                "original_filename": filename,
                "local_path": str(local_path.relative_to(REPO_ROOT)) if local_path.exists() else "",
                "download_status": status,
                "file_size_bytes": str(local_path.stat().st_size) if local_path.exists() else "",
                "sha256": sha256(local_path) if local_path.exists() else "",
                **validation,
                "notes": item["notes"] + (f" Download error: {error}" if error else ""),
            }
        )
        time.sleep(0.1)
    return rows


def existing_election_rows() -> list[dict]:
    election_variables = (
        "election_mayoral_winner_margin; election_mayoral_top_two_margin; "
        "election_effective_mayoral_candidates_5pct; election_mayoral_vote_fragmentation; "
        "election_federal_margin; election_provincial_margin; "
        "election_effective_federal_parties_5pct; election_effective_provincial_parties_5pct"
    )
    checks = [
        ("municipal_2023_official_results", ELECTIONS_RAW / "toronto_2023_mayor.xlsx"),
        ("municipal_2023_voter_statistics", ELECTIONS_RAW / "toronto_2023_mayor_voter_statistics.xlsx"),
        ("municipal_2023_subdivisions", ELECTIONS_RAW / "toronto_2023_subdivisions.geojson"),
        ("provincial_2025_official_return", ELECTIONS_RAW / "eo_2025_official_return.csv"),
        ("provincial_2025_candidate_summary", ELECTIONS_RAW / "source_downloads" / "eo_2025_candidate_summary.csv"),
        ("provincial_2025_party_codes", ELECTIONS_RAW / "source_downloads" / "eo_2025_political_interest_codes.csv"),
        ("federal_2025_poll_by_poll_format2_dir", ELECTIONS_RAW / "source_downloads" / "federal_csv_format2"),
        ("federal_2025_polling_polygons_dir", ELECTIONS_RAW / "source_downloads" / "federal_polygons"),
        ("provincial_2025_polling_polygons_dir", ELECTIONS_RAW / "source_downloads" / "provincial_polygons"),
    ]
    rows = []
    for name, path in checks:
        exists = path.exists()
        if path.is_dir():
            size = ""
            note = f"{len(list(path.iterdir()))} files"
        else:
            size = str(path.stat().st_size) if exists else ""
            note = ""
        rows.append(
            {
                "dataset_name": name,
                "variable_names": election_variables,
                "official_source": "existing repository raw election module",
                "source_url": "",
                "download_url": "",
                "download_date": "",
                "license": "",
                "update_frequency": "",
                "geographic_level": "polling division / ward / riding",
                "temporal_coverage": "2023 municipal; 2025 provincial/federal",
                "coordinate_reference_system": "",
                "original_filename": path.name,
                "local_path": str(path.relative_to(REPO_ROOT)) if exists else "",
                "download_status": "existing" if exists else "missing_existing_election_source",
                "file_size_bytes": size,
                "sha256": sha256(path) if exists and path.is_file() else "",
                "row_count": "",
                "header": "",
                "valid_zip": "",
                "notes": "Existing raw election source; not duplicated in Task 2. " + note,
            }
        )
    return rows


def update_registry(inventory_rows: list[dict]) -> None:
    registry_fields = [
        "variable_name",
        "block",
        "literature_source",
        "preferred_data_source",
        "official_dataset",
        "raw_dataset_location",
        "processed_dataset_location",
        "geographic_level",
        "denominator",
        "status",
        "notes",
    ]
    if (PROJECT_METADATA / "variable_registry.csv").exists():
        with (PROJECT_METADATA / "variable_registry.csv").open(newline="", encoding="utf-8-sig") as handle:
            existing = list(csv.DictReader(handle))
    else:
        existing = []
    variable_to_rows: dict[str, list[dict]] = {}
    for row in inventory_rows:
        for variable in [part.strip() for part in row["variable_names"].split(";") if part.strip()]:
            variable_to_rows.setdefault(variable, []).append(row)
    task_variables = set(variable_to_rows)
    preserved = [
        row
        for row in existing
        if row.get("variable_name") not in task_variables
        and row.get("variable_name") != "Block 4 election competitiveness and fragmentation"
    ]
    additions = []
    for variable, rows in sorted(variable_to_rows.items()):
        successful = [row for row in rows if row["download_status"] in {"downloaded", "existing"}]
        first = successful[0] if successful else rows[0]
        is_election = variable.startswith("election_")
        additions.append(
            {
                "variable_name": variable,
                "block": "Block 4" if is_election else "Block 5",
                "literature_source": TOD_LITERATURE,
                "preferred_data_source": (
                    "Official municipal/provincial/federal election sources already in repository"
                    if is_election
                    else first["official_source"]
                ),
                "official_dataset": (
                    "Municipal 2023, Provincial 2025, and Federal 2025 raw election datasets"
                    if is_election
                    else first["dataset_name"]
                ),
                "raw_dataset_location": "; ".join(row["local_path"] for row in successful if row["local_path"]),
                "processed_dataset_location": "",
                "geographic_level": first["geographic_level"],
                "denominator": "",
                "status": "raw_collected" if successful else "missing",
                "notes": "Raw data collected only; no variables derived. " + first["notes"],
            }
        )
    write_csv(PROJECT_METADATA / "variable_registry.csv", preserved + additions, registry_fields)


def write_reports(inventory: list[dict]) -> None:
    fields = [
        "dataset_name",
        "variable_names",
        "official_source",
        "source_url",
        "download_url",
        "download_date",
        "license",
        "update_frequency",
        "geographic_level",
        "temporal_coverage",
        "coordinate_reference_system",
        "original_filename",
        "local_path",
        "download_status",
        "file_size_bytes",
        "sha256",
        "row_count",
        "header",
        "valid_zip",
        "validation_note",
        "notes",
    ]
    write_csv(VARIABLES_METADATA / "non_census_raw_dataset_inventory.csv", inventory, fields)
    missing = [row for row in inventory if row["download_status"] not in {"downloaded", "existing"}]
    write_csv(VARIABLES_METADATA / "non_census_missing_data_report.csv", missing, fields)
    qa_lines = [
        "# Non-Census Raw Dataset Collection QA",
        "",
        f"Generated: {DOWNLOAD_DATE}",
        "",
        "## Scope",
        "",
        "Raw acquisition only. No variables were derived, no observations were aggregated, and no spatial joins were performed.",
        "",
        "## Summary",
        "",
        f"- Inventory records: {len(inventory)}",
        f"- Downloaded files in this run: {sum(1 for row in inventory if row['download_status'] == 'downloaded')}",
        f"- Existing files reused: {sum(1 for row in inventory if row['download_status'] == 'existing')}",
        f"- Local raw file records present: {sum(1 for row in inventory if row['download_status'] in {'downloaded', 'existing'})}",
        f"- Missing or failed records: {len(missing)}",
        f"- CSV files readable: {sum(1 for row in inventory if row.get('validation_note') == 'csv readable')}",
        f"- ZIP files readable: {sum(1 for row in inventory if row['valid_zip'] == 'true')}",
        "",
        "## Task 1 Census QA Summary Carried Forward",
        "",
        "- CT Census master rows: 622.",
        "- Interpolation-universe CT rows: 585.",
        "- Duplicate CT ids: 0.",
        "- Interpolation CT ids missing from Census master: 0.",
        "- Invalid Census share values documented: 1 (`citizen_adult_share` for CT `5350047.03`).",
        "",
        "## Known Limitations",
        "",
        "- Toronto CKAN package metadata often reports `License not specified`; the inventory notes the Toronto Open Data licence context.",
        "- The Toronto Open Data `parks` and shelter location packages are marked as legacy/current-as-published in metadata; future processing should assess whether newer park/shelter alternatives are needed.",
        "- Federal 2025 polling-place coordinates remain unavailable in the existing election/accessibility raw data.",
        "- TTS files were collected from the supervisor-recommended School of Cities GitHub repository; no TTS indicator was computed.",
    ]
    if missing:
        qa_lines.extend(["", "## Missing/Failed Records", ""])
        qa_lines.extend(f"- {row['dataset_name']} / {row['original_filename']}: {row['download_status']} {row['notes']}" for row in missing)
    (VARIABLES_DOCS / "non_census_raw_collection_report.md").parent.mkdir(parents=True, exist_ok=True)
    (VARIABLES_DOCS / "non_census_raw_collection_report.md").write_text("\n".join(qa_lines) + "\n", encoding="utf-8")


def main() -> None:
    VARIABLES_RAW.mkdir(parents=True, exist_ok=True)
    VARIABLES_METADATA.mkdir(parents=True, exist_ok=True)
    VARIABLES_DOCS.mkdir(parents=True, exist_ok=True)
    inventory = []
    inventory.extend(collect_tts())
    inventory.extend(collect_toronto_open_data())
    inventory.extend(existing_election_rows())
    write_reports(inventory)
    update_registry(inventory)
    print(f"Wrote {len(inventory)} inventory records")
    print(f"Inventory: {VARIABLES_METADATA / 'non_census_raw_dataset_inventory.csv'}")
    print(f"Report: {VARIABLES_DOCS / 'non_census_raw_collection_report.md'}")


if __name__ == "__main__":
    main()
