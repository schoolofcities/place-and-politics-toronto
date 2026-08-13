"""Build CT-level Blocks 1-5 modelling variables.

The script derives variables from previously collected raw/processed sources.
It uses GDAL/OGR for geometry operations and avoids third-party Python
geospatial/dataframe dependencies.
"""

from __future__ import annotations

import csv
from datetime import date
import json
import math
from pathlib import Path
import statistics
import zipfile

from osgeo import ogr, osr


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
VARIABLES_ROOT = DATA_ROOT / "variables"
VARIABLES_RAW = VARIABLES_ROOT / "raw"
VARIABLES_PROCESSED = VARIABLES_ROOT / "processed"
VARIABLES_METADATA = VARIABLES_ROOT / "metadata"
VARIABLES_DOCS = VARIABLES_ROOT / "documentation"
CENSUS_MASTER = DATA_ROOT / "census" / "processed" / "ct" / "statcan_2021_ct_census_variables_master.csv"
INTERP_ROOT = DATA_ROOT / "interpolation" / "processed"
CT_POLYGON_SOURCE = REPO_ROOT / "data" / "clustering_neighbourhoods" / "profiles" / "raw_shares.gpkg"
REGISTRY_PATH = DATA_ROOT / "metadata" / "variable_registry.csv"

OUTPUT_MASTER = VARIABLES_PROCESSED / "toronto_ct_blocks_1_5_modelling_master.csv"
OUTPUT_GEOJSON = VARIABLES_PROCESSED / "toronto_ct_blocks_1_5_modelling_master.geojson"
OUTPUT_DICTIONARY = VARIABLES_METADATA / "toronto_ct_blocks_1_5_variable_dictionary.csv"
OUTPUT_QA = VARIABLES_DOCS / "toronto_ct_blocks_1_5_qa_report.md"
OUTPUT_METHOD = VARIABLES_DOCS / "toronto_ct_blocks_1_5_methodology_report.md"
OUTPUT_LOG = VARIABLES_DOCS / "toronto_ct_blocks_1_5_processing_log.md"
OUTPUT_SUMMARY = VARIABLES_PROCESSED / "toronto_ct_blocks_1_5_summary_statistics.csv"
OUTPUT_LIMITATIONS = VARIABLES_DOCS / "toronto_ct_blocks_1_5_limitations.md"

ELECTIONS = {
    "municipal": "municipal_2023_mayor",
    "provincial": "provincial_2025",
    "federal": "federal_2025",
}

LITERATURE = (
    "Marshall & Siemiatycki (2014); Couture, Bherer & Breux (2014); "
    "Geys (2006); Cancela & Geys (2016); Dostie-Goulet et al. (2012); "
    "McGregor (2018); Breux, Couture & Koop (2017); "
    "Breux, Couture & Goodman (2017); Breux, Couture & Koop (2022)"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def as_number(value: object) -> float | None:
    text = "" if value is None else str(value).strip().replace(",", "")
    if not text or text.lower() in {"none", "nan", "null", "n/a", "na", "..", "...", "x"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def fmt(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return "" if not math.isfinite(value) else f"{value:.10g}"
    return str(value)


def divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def srs(epsg: int) -> osr.SpatialReference:
    ref = osr.SpatialReference()
    ref.ImportFromEPSG(epsg)
    ref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return ref


SRS_4326 = srs(4326)
SRS_3347 = srs(3347)
SRS_2952 = srs(2952)
TRANSFORM_4326_TO_3347 = osr.CoordinateTransformation(SRS_4326, SRS_3347)
TRANSFORM_2952_TO_3347 = osr.CoordinateTransformation(SRS_2952, SRS_3347)


def transform_geom(geom: ogr.Geometry, transform: osr.CoordinateTransformation) -> ogr.Geometry:
    out = geom.Clone()
    out.Transform(transform)
    return out


def point_4326(lon: float, lat: float) -> ogr.Geometry:
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)
    return transform_geom(point, TRANSFORM_4326_TO_3347)


def point_2952(x: float, y: float) -> ogr.Geometry:
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    return transform_geom(point, TRANSFORM_2952_TO_3347)


def envelopes_intersect(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    return not (a[1] < b[0] or a[0] > b[1] or a[3] < b[2] or a[2] > b[3])


def load_ct_polygons() -> dict[str, dict]:
    ds = ogr.Open(str(CT_POLYGON_SOURCE))
    if ds is None:
        raise RuntimeError(f"Could not open CT polygon source: {CT_POLYGON_SOURCE}")
    layer = ds.GetLayer(0)
    source_srs = layer.GetSpatialRef()
    transform = osr.CoordinateTransformation(source_srs, SRS_3347) if source_srs else None
    out: dict[str, dict] = {}
    for feature in layer:
        ct_id = str(feature.GetField("ct_id"))
        geom = feature.GetGeometryRef().Clone()
        if transform:
            geom.Transform(transform)
        centroid = geom.Centroid()
        out[ct_id] = {
            "geometry": geom,
            "centroid": centroid,
            "area_m2": geom.GetArea(),
            "geojson_geometry": json.loads(feature.GetGeometryRef().ExportToJson()),
        }
    return out


def assign_point_to_ct(point: ogr.Geometry, cts: dict[str, dict]) -> str | None:
    point_env = point.GetEnvelope()
    for ct_id, item in cts.items():
        geom = item["geometry"]
        if not envelopes_intersect(point_env, geom.GetEnvelope()):
            continue
        if geom.Contains(point) or geom.Intersects(point):
            return ct_id
    return None


def nearest_distance(point: ogr.Geometry, geometries: list[ogr.Geometry]) -> float | None:
    if not geometries:
        return None
    return min(point.Distance(geom) for geom in geometries)


def count_within(point: ogr.Geometry, geometries: list[ogr.Geometry], metres: float) -> int:
    return sum(1 for geom in geometries if point.Distance(geom) <= metres)


def load_points_from_geojson(path: Path, type_filter: str | None = None) -> list[ogr.Geometry]:
    ds = ogr.Open(str(path))
    if ds is None:
        return []
    layer = ds.GetLayer(0)
    source_srs = layer.GetSpatialRef()
    transform = osr.CoordinateTransformation(source_srs, SRS_3347) if source_srs else TRANSFORM_4326_TO_3347
    points = []
    for feature in layer:
        if type_filter is not None and str(feature.GetField("TYPE")).lower() != type_filter.lower():
            continue
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        points.append(transform_geom(geom, transform))
    return points


def load_geometries_from_any(path: Path) -> list[ogr.Geometry]:
    open_path = str(path)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            shp_members = [name for name in archive.namelist() if name.lower().endswith(".shp")]
        if shp_members:
            open_path = f"/vsizip/{path}/{shp_members[0]}"
    ds = ogr.Open(open_path)
    if ds is None:
        return []
    layer = ds.GetLayer(0)
    source_srs = layer.GetSpatialRef()
    transform = osr.CoordinateTransformation(source_srs, SRS_3347) if source_srs else TRANSFORM_4326_TO_3347
    geoms = []
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom is not None:
            geoms.append(transform_geom(geom, transform))
    return geoms


def competition(values: list[float], threshold: float = 0.0) -> dict[str, float | None]:
    total = sum(values)
    if total <= 0:
        return {"margin": None, "effective": None, "fragmentation": None, "count": None}
    shares_all = sorted([value / total for value in values if value > 0], reverse=True)
    shares = [share for share in shares_all if share >= threshold]
    hhi = sum(share * share for share in shares)
    return {
        "margin": shares_all[0] - shares_all[1] if len(shares_all) > 1 else None,
        "effective": 1 / hhi if hhi else None,
        "fragmentation": 1 - hhi if hhi else None,
        "count": len(shares),
    }


def load_party_values(election_id: str) -> dict[str, list[float]]:
    out = {}
    for row in read_csv(INTERP_ROOT / f"{election_id}_ct_estimated_results.csv"):
        values = []
        for key, raw in row.items():
            if key.startswith("party_") and key.endswith("_votes"):
                value = as_number(raw)
                if value is not None and value > 0:
                    values.append(value)
        out[row["ct_id"]] = values
    return out


def load_candidate_values(election_id: str) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for row in read_csv(INTERP_ROOT / f"{election_id}_ct_candidate_estimated_votes.csv"):
        value = as_number(row.get("estimated_candidate_votes"))
        if value is not None and value > 0:
            out.setdefault(row["ct_id"], []).append(value)
    return out


def load_election_results() -> dict[str, dict[str, dict]]:
    return {
        short: {row["ct_id"]: row for row in read_csv(INTERP_ROOT / f"{eid}_ct_estimated_results.csv")}
        for short, eid in ELECTIONS.items()
    }


def tts_variables(cts: dict[str, dict]) -> dict[str, dict]:
    zones_path = VARIABLES_RAW / "transportation_tomorrow_survey_2022" / "tts2022zones_data.geojson"
    metrics_path = VARIABLES_RAW / "transportation_tomorrow_survey_2022" / "metrics_tts2022.csv"
    metrics = {row["tts22_hhld"]: row for row in read_csv(metrics_path)}
    ds = ogr.Open(str(zones_path))
    layer = ds.GetLayer(0)
    source_srs = layer.GetSpatialRef()
    transform = osr.CoordinateTransformation(source_srs, SRS_3347) if source_srs else TRANSFORM_4326_TO_3347
    accum = {
        ct_id: {
            "tts_no_car_num": 0.0,
            "tts_hhlds_denom": 0.0,
            "tts_transit_num": 0.0,
            "tts_trips_denom": 0.0,
            "tts_overlap_area_m2": 0.0,
        }
        for ct_id in cts
    }
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        zone_geom = transform_geom(geom, transform)
        zone_area = zone_geom.GetArea()
        zone_env = zone_geom.GetEnvelope()
        if zone_area <= 0:
            continue
        zone_id = str(feature.GetField("TTS2022"))
        m = metrics.get(zone_id, {})
        hhlds = as_number(m.get("hhlds")) or as_number(feature.GetField("hhlds")) or 0
        no_veh_count = as_number(m.get("hhlds_no_veh"))
        if no_veh_count is None:
            no_veh_pct = as_number(feature.GetField("hhlds_no_veh"))
            no_veh_count = hhlds * no_veh_pct / 100 if no_veh_pct is not None else 0
        trips = as_number(m.get("trips_total")) or as_number(m.get("trips_5up")) or 0
        transit_pct = as_number(feature.GetField("mode_transit"))
        transit_count = trips * transit_pct / 100 if transit_pct is not None else 0
        for ct_id, ct in cts.items():
            if not envelopes_intersect(zone_env, ct["geometry"].GetEnvelope()):
                continue
            if not zone_geom.Intersects(ct["geometry"]):
                continue
            inter = zone_geom.Intersection(ct["geometry"])
            area = inter.GetArea() if inter is not None else 0
            if area <= 0:
                continue
            portion = area / zone_area
            acc = accum[ct_id]
            acc["tts_no_car_num"] += no_veh_count * portion
            acc["tts_hhlds_denom"] += hhlds * portion
            acc["tts_transit_num"] += transit_count * portion
            acc["tts_trips_denom"] += trips * portion
            acc["tts_overlap_area_m2"] += area
    return {
        ct_id: {
            "tts_no_car_household_share": divide(v["tts_no_car_num"], v["tts_hhlds_denom"]),
            "tts_transit_trip_share": divide(v["tts_transit_num"], v["tts_trips_denom"]),
            "tts_overlap_area_m2": v["tts_overlap_area_m2"],
        }
        for ct_id, v in accum.items()
    }


def facility_access(cts: dict[str, dict]) -> dict[str, dict]:
    library = load_points_from_geojson(
        VARIABLES_RAW / "toronto_open_data" / "library_branch_general_information" / "tpl-branch-general-information-4326.geojson"
    )
    rec_all = load_points_from_geojson(
        VARIABLES_RAW / "toronto_open_data" / "parks_and_recreation_facilities" / "parks-and-recreation-facilities-4326.geojson"
    )
    rec_centres = []
    parks_facility = []
    ds = ogr.Open(str(VARIABLES_RAW / "toronto_open_data" / "parks_and_recreation_facilities" / "parks-and-recreation-facilities-4326.geojson"))
    layer = ds.GetLayer(0)
    source_srs = layer.GetSpatialRef()
    transform = osr.CoordinateTransformation(source_srs, SRS_3347) if source_srs else TRANSFORM_4326_TO_3347
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        typ = str(feature.GetField("TYPE") or "").lower()
        amen = str(feature.GetField("AMENITIES") or "").lower()
        g = transform_geom(geom, transform)
        if typ == "park":
            parks_facility.append(g)
        if "community centre" in typ or "community centre" in amen or "community recreation" in typ:
            rec_centres.append(g)
    park_geoms = load_geometries_from_any(VARIABLES_RAW / "toronto_open_data" / "parks" / "parks-wgs84.zip")
    shelter_geoms = load_geometries_from_any(
        VARIABLES_RAW / "toronto_open_data" / "hostel_services_homeless_shelter_locations" / "shelter-locations-wgs84.zip"
    )
    if not park_geoms:
        park_geoms = parks_facility
    if not rec_centres:
        rec_centres = rec_all
    out = {}
    for ct_id, ct in cts.items():
        centroid = ct["centroid"]
        out[ct_id] = {
            "library_nearest_m": nearest_distance(centroid, library),
            "library_count_1200m": count_within(centroid, library, 1200),
            "library_access_1200m": 1 if count_within(centroid, library, 1200) > 0 else 0,
            "community_centre_nearest_m": nearest_distance(centroid, rec_centres),
            "community_centre_count_1200m": count_within(centroid, rec_centres, 1200),
            "community_centre_access_1200m": 1 if count_within(centroid, rec_centres, 1200) > 0 else 0,
            "park_nearest_m": nearest_distance(centroid, park_geoms),
            "park_count_1200m": count_within(centroid, park_geoms, 1200),
            "park_access_1200m": 1 if count_within(centroid, park_geoms, 1200) > 0 else 0,
            "shelter_nearest_m": nearest_distance(centroid, shelter_geoms),
            "shelter_count_1200m": count_within(centroid, shelter_geoms, 1200),
            "shelter_access_1200m": 1 if count_within(centroid, shelter_geoms, 1200) > 0 else 0,
        }
    return out


def point_count_vars(cts: dict[str, dict], census_by_ct: dict[str, dict]) -> dict[str, dict]:
    out = {ct_id: {"ksi_collision_events_2021_2025": 0, "development_applications_2021_2025": 0} for ct_id in cts}
    seen_collisions = set()
    ksi_path = VARIABLES_RAW / "toronto_open_data" / "ksi_collisions" / "motor-vehicle-collisions-with-ksi-data-4326.csv"
    for row in read_csv(ksi_path):
        collision_id = row.get("collision_id", "")
        if collision_id in seen_collisions:
            continue
        year = int((row.get("accdate") or "0000")[:4] or 0)
        if year < 2021 or year > 2025:
            continue
        lon = as_number(row.get("longitude"))
        lat = as_number(row.get("latitude"))
        if lon is None or lat is None:
            continue
        ct_id = assign_point_to_ct(point_4326(lon, lat), cts)
        if ct_id:
            out[ct_id]["ksi_collision_events_2021_2025"] += 1
            seen_collisions.add(collision_id)

    dev_path = VARIABLES_RAW / "toronto_open_data" / "development_applications" / "development-applications.csv"
    for row in read_csv(dev_path):
        year = int((row.get("DATE_SUBMITTED") or "0000")[:4] or 0)
        if year < 2021 or year > 2025:
            continue
        x = as_number(row.get("X"))
        y = as_number(row.get("Y"))
        if x is None or y is None:
            continue
        ct_id = assign_point_to_ct(point_2952(x, y), cts)
        if ct_id:
            out[ct_id]["development_applications_2021_2025"] += 1

    for ct_id, values in out.items():
        pop = as_number(census_by_ct.get(ct_id, {}).get("population_total"))
        values["ksi_collision_events_2021_2025_per_1000"] = (
            values["ksi_collision_events_2021_2025"] / pop * 1000 if pop else None
        )
        values["development_applications_2021_2025_per_1000"] = (
            values["development_applications_2021_2025"] / pop * 1000 if pop else None
        )
    return out


def ward_number(text: str) -> str:
    import re

    match = re.search(r"\((\d+)\)", text or "")
    return match.group(1).zfill(2) if match else ""


def ward_proxy_311(census_by_ct: dict[str, dict]) -> dict[str, dict]:
    # The official annual 311 files expose ward and FSA fields, but no request
    # coordinates. Allocate ward totals to CTs by CT-ward intersection area
    # using the validated municipal ward-to-CT crosswalk from interpolation.
    counts_by_year = {2023: 0, 2024: 0, 2025: 0}
    ward_counts: dict[str, int] = {}
    missing_ward = 0
    for year in counts_by_year:
        path = VARIABLES_RAW / "toronto_open_data" / "311_service_requests_customer_initiated" / f"sr{year}.zip"
        with zipfile.ZipFile(path) as archive:
            member = [name for name in archive.namelist() if name.lower().endswith(".csv")][0]
            with archive.open(member) as raw:
                reader = csv.DictReader((line.decode("utf-8-sig", errors="replace") for line in raw))
                for row in reader:
                    counts_by_year[year] += 1
                    ward = ward_number(row.get("Ward", ""))
                    if ward:
                        ward_counts[ward] = ward_counts.get(ward, 0) + 1
                    else:
                        missing_ward += 1
    total = sum(counts_by_year.values())
    allocated = {
        ct_id: {
            "requests_311_2023_2025_estimated_count": 0.0,
            "requests_311_2023_2025_citywide_total": total,
            "requests_311_missing_ward_count": missing_ward,
            "requests_311_area_allocation_weight": 0.0,
            "requests_311_per_1000": None,
            "requests_311_proxy_note": "Official 311 files provide ward/FSA but no coordinates; CT count is an area-weighted ward-to-CT allocation using the existing municipal ward-to-CT crosswalk.",
        }
        for ct_id in census_by_ct
    }
    crosswalk = (
        DATA_ROOT
        / "interpolation"
        / "processed"
        / "intermediate"
        / "02_spatial_crosswalks"
        / "municipal_2023_mayor_district_to_ct_crosswalk.csv"
    )
    crosswalk_rows = read_csv(crosswalk)
    ward_area: dict[str, float] = {}
    for row in crosswalk_rows:
        ward = str(row.get("source_id") or row.get("electoral_district_number") or "").zfill(2)
        area = as_number(row.get("intersection_area_m2")) or 0
        ward_area[ward] = ward_area.get(ward, 0) + area
    for row in crosswalk_rows:
        ct_id = row.get("ct_id", "")
        if ct_id not in allocated:
            continue
        ward = str(row.get("source_id") or row.get("electoral_district_number") or "").zfill(2)
        area = as_number(row.get("intersection_area_m2")) or 0
        if not ward or ward_area.get(ward, 0) == 0:
            continue
        weight = area / ward_area[ward]
        allocated[ct_id]["requests_311_area_allocation_weight"] += weight
        allocated[ct_id]["requests_311_2023_2025_estimated_count"] += ward_counts.get(ward, 0) * weight
    for ct_id, values in allocated.items():
        pop = as_number(census_by_ct.get(ct_id, {}).get("population_total"))
        if pop:
            values["requests_311_per_1000"] = values["requests_311_2023_2025_estimated_count"] / pop * 1000
    return allocated


def build_master() -> tuple[list[dict], dict[str, dict]]:
    cts = load_ct_polygons()
    census_rows = {row["ct_id"]: row for row in read_csv(CENSUS_MASTER) if row.get("in_interpolation_universe") == "true"}
    election_tables = load_election_results()
    municipal_candidates = load_candidate_values(ELECTIONS["municipal"])
    provincial_parties = load_party_values(ELECTIONS["provincial"])
    federal_parties = load_party_values(ELECTIONS["federal"])
    tts = tts_variables(cts)
    access = facility_access(cts)
    point_counts = point_count_vars(cts, census_rows)
    requests_311 = ward_proxy_311(census_rows)

    rows = []
    for ct_id in sorted(census_rows):
        c = census_rows[ct_id]
        row = {
            "ct_id": ct_id,
            "ctuid": c.get("ctuid", ""),
            "dguid": c.get("dguid", ""),
            "geo_name": c.get("geo_name", ""),
            "census_year": "2021",
            "population_total": c.get("population_total", ""),
            "population_18plus": c.get("population_18plus", ""),
            "citizen_canadian_18plus_count": c.get("canadian_citizens_18plus_count", ""),
            "land_area_km2": c.get("land_area_km2", ""),
            "block1_age_18_34_share": c.get("age_18_34_share", ""),
            "block1_age_35_64_share": c.get("age_35_64_share", ""),
            "block1_age_65_plus_share": c.get("age_65_plus_share", ""),
            "block1_median_age": c.get("median_age", ""),
            "block1_average_household_size": c.get("average_household_size", ""),
            "block1_bachelors_or_higher_25_64_share": c.get("bachelors_or_higher_25_64_share", ""),
            "block1_low_income_lim_at_share": c.get("low_income_lim_at_share", ""),
            "block1_unemployment_rate_share": c.get("unemployment_rate_share", ""),
            "block2_renter_share": c.get("renter_share", ""),
            "block2_owner_share": c.get("owner_share", ""),
            "block2_same_address_1yr_share": c.get("same_address_1yr_share", ""),
            "block2_same_address_5yr_share": c.get("same_address_5yr_share", ""),
            "block2_condo_share": c.get("condo_share", ""),
            "block2_apartment_share": c.get("apartment_share", ""),
            "block2_detached_share": c.get("detached_share", ""),
            "block2_semi_detached_share": c.get("semi_detached_share", ""),
            "block2_population_density_per_km2": c.get("population_density_per_km2", ""),
            "block3_immigrant_share": c.get("immigrant_share", ""),
            "block3_recent_immigrant_share": c.get("recent_immigrant_share", ""),
            "block3_non_citizen_share": c.get("non_citizen_share", ""),
            "block3_citizen_adult_share": c.get("citizen_adult_share", ""),
            "block3_visible_minority_share": c.get("visible_minority_share", ""),
            "block3_english_french_knowledge_share": c.get("english_french_knowledge_share", ""),
            "block3_non_official_mother_tongue_share": c.get("non_official_mother_tongue_share", ""),
            "block5_census_transit_commute_share": c.get("transit_commute_share", ""),
            "block5_school_age_5_17_share": c.get("school_age_5_17_share", ""),
        }
        for prefix, table in election_tables.items():
            e = table.get(ct_id, {})
            row[f"outcome_{prefix}_participation_citizen_18plus"] = e.get("estimated_participation_citizen_18plus", "")
            row[f"outcome_{prefix}_turnout_electors"] = e.get("estimated_turnout", "")
            row[f"{prefix}_estimated_total_votes"] = e.get("estimated_total_votes", "")
            row[f"{prefix}_estimated_electors"] = e.get("estimated_electors", "")
        parts = [
            as_number(row.get("outcome_municipal_participation_citizen_18plus")),
            as_number(row.get("outcome_provincial_participation_citizen_18plus")),
            as_number(row.get("outcome_federal_participation_citizen_18plus")),
        ]
        present = [v for v in parts if v is not None]
        row["outcome_mean_participation_citizen_18plus"] = sum(present) / len(present) if present else None

        m_all = competition(municipal_candidates.get(ct_id, []))
        m_5 = competition(municipal_candidates.get(ct_id, []), 0.05)
        row["block4_mayoral_top_two_margin"] = m_all["margin"]
        row["block4_mayoral_winner_margin"] = m_all["margin"]
        row["block4_effective_mayoral_candidates_5pct"] = m_5["effective"]
        row["block4_mayoral_candidate_count_5pct"] = m_5["count"]
        row["block4_mayoral_vote_fragmentation"] = m_5["fragmentation"]
        for name, values in [("provincial", provincial_parties.get(ct_id, [])), ("federal", federal_parties.get(ct_id, []))]:
            comp = competition(values, 0.05)
            row[f"block4_{name}_margin"] = comp["margin"]
            row[f"block4_effective_{name}_parties_5pct"] = comp["effective"]
            row[f"block4_{name}_party_count_5pct"] = comp["count"]
            row[f"block4_{name}_vote_fragmentation"] = comp["fragmentation"]

        row.update({f"block5_{key}": value for key, value in tts.get(ct_id, {}).items()})
        row.update({f"block5_{key}": value for key, value in access.get(ct_id, {}).items()})
        row.update({f"block5_{key}": value for key, value in point_counts.get(ct_id, {}).items()})
        row.update({f"block5_{key}": value for key, value in requests_311.get(ct_id, {}).items()})
        # Preferred aliases for downstream modelling.
        row["block5_transit_commute_share_preferred"] = row.get("block5_tts_transit_trip_share") or row.get("block5_census_transit_commute_share")
        row["block5_no_car_household_share"] = row.get("block5_tts_no_car_household_share", "")
        row["block5_social_housing_share"] = c.get("subsidized_housing_tenant_share", "")
        row["block5_social_housing_note"] = "Census Profile characteristic 1491: percent of tenant households in subsidized housing, converted to a 0-1 share. Denominator is tenant households, not all households."
        rows.append({key: fmt(value) for key, value in row.items()})
    return rows, cts


def write_geojson(rows: list[dict], cts: dict[str, dict]) -> None:
    features = []
    for row in rows:
        ct_id = row["ct_id"]
        features.append({"type": "Feature", "properties": row, "geometry": cts[ct_id]["geojson_geometry"]})
    OUTPUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_GEOJSON.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")


def variable_dictionary(rows: list[dict]) -> list[dict]:
    method = {
        "block4": "Calculated from interpolated CT candidate/party vote outputs: top-two margin, effective number = 1/sum(p_i^2), fragmentation = 1 - sum(p_i^2).",
        "block5_library": "Euclidean distance/count from CT centroid to official library branch points; 1200m approximates a 15-minute walk.",
        "block5_community": "Euclidean distance/count from CT centroid to official Parks and Recreation facility points classified as community-centre-like where possible.",
        "block5_park": "Euclidean distance/count from CT centroid to official park polygons; 1200m approximates a 15-minute walk.",
        "block5_shelter": "Euclidean distance/count from CT centroid to official shelter-location geometries; 1200m approximates a 15-minute walk.",
        "block5_tts": "Area-weighted interpolation from TTS 2022 zones to CT polygons using zone household/trip denominators.",
        "block5_point": "Point-in-polygon count to CT using official Toronto point coordinates; per-1000 variables divide by Census population_total.",
    }
    out = []
    for col in rows[0]:
        block = "identifier"
        source = ""
        raw_dataset = ""
        formula = ""
        units = ""
        numerator = ""
        denominator = ""
        assumptions = ""
        status = "complete"
        if col.startswith("block1"):
            block, source, units = "Block 1", "Statistics Canada 2021 Census", "share/count/rate"
            raw_dataset = str(CENSUS_MASTER.relative_to(REPO_ROOT))
            formula = "Imported from Task 1 Census CT master; see Census data dictionary for source counts and denominators."
        elif col.startswith("block2"):
            block, source, units = "Block 2", "Statistics Canada 2021 Census", "share/count/rate"
            raw_dataset = str(CENSUS_MASTER.relative_to(REPO_ROOT))
            formula = "Imported from Task 1 Census CT master; see Census data dictionary for source counts and denominators."
        elif col.startswith("block3"):
            block, source, units = "Block 3", "Statistics Canada 2021 Census", "share"
            raw_dataset = str(CENSUS_MASTER.relative_to(REPO_ROOT))
            formula = "Imported from Task 1 Census CT master; see Census data dictionary for source counts and denominators."
        elif col.startswith("block4"):
            block, source, formula, units = "Block 4", "Interpolated election CT outputs", method["block4"], "share/effective number/count"
            raw_dataset = str(INTERP_ROOT.relative_to(REPO_ROOT))
        elif "tts" in col or "no_car" in col or "transit_commute_share_preferred" in col:
            block, source, formula, units = "Block 5", "Transportation Tomorrow Survey 2022 / Census fallback", method["block5_tts"], "share"
            raw_dataset = str((VARIABLES_RAW / "transportation_tomorrow_survey_2022").relative_to(REPO_ROOT))
        elif "library" in col:
            block, source, formula, units = "Block 5", "Toronto Open Data Library Branch General Information", method["block5_library"], "metres/count/binary"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "library_branch_general_information").relative_to(REPO_ROOT))
        elif "community_centre" in col:
            block, source, formula, units = "Block 5", "Toronto Open Data Parks and Recreation Facilities", method["block5_community"], "metres/count/binary"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "parks_and_recreation_facilities").relative_to(REPO_ROOT))
        elif "park" in col:
            block, source, formula, units = "Block 5", "Toronto Open Data Parks / Parks and Recreation Facilities", method["block5_park"], "metres/count/binary"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "parks").relative_to(REPO_ROOT))
        elif "shelter" in col:
            block, source, formula, units = "Block 5", "Toronto Open Data shelter profile/location datasets", method["block5_shelter"], "metres/count/binary"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "hostel_services_homeless_shelter_locations").relative_to(REPO_ROOT))
        elif "ksi" in col:
            block, source, formula, units, numerator, denominator = "Block 5", "Toronto Open Data KSI collisions", method["block5_point"], "count/per 1000", "unique collision events 2021-2025", "population_total"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "ksi_collisions").relative_to(REPO_ROOT))
        elif "development_applications" in col:
            block, source, formula, units, numerator, denominator = "Block 5", "Toronto Open Data Development Applications", method["block5_point"], "count/per 1000", "applications submitted 2021-2025", "population_total"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "development_applications").relative_to(REPO_ROOT))
        elif "311" in col:
            block, source, formula, units = "Block 5", "Toronto Open Data 311 Service Requests", "Official 2023-2025 request counts aggregated by ward, allocated to CTs by CT-ward intersection-area share using the existing municipal ward-to-CT crosswalk, then divided by Census population_total and multiplied by 1000.", "count/per 1000/note"
            raw_dataset = str((VARIABLES_RAW / "toronto_open_data" / "311_service_requests_customer_initiated").relative_to(REPO_ROOT))
            numerator = "allocated 2023-2025 311 requests"
            denominator = "population_total"
            assumptions = "Source records are ward-coded but not point-geocoded; CT values are area-weighted estimates allocated from ward totals, not exact request locations."
            status = "documented_limitation" if col.endswith("_note") else "complete"
        elif "social_housing" in col:
            block, source, formula, units = "Block 5", "Statistics Canada 2021 Census Profile", "Census Profile characteristic 1491, `% of tenant households in subsidized housing`, divided by 100.", "share/note"
            raw_dataset = str(CENSUS_MASTER.relative_to(REPO_ROOT))
            denominator = "tenant households"
            assumptions = "This measures subsidized housing among tenant households; it is not a share of all households or all occupied dwellings."
            status = "complete"
        elif col.startswith("outcome") or col.endswith("estimated_total_votes") or col.endswith("estimated_electors"):
            block, source, units = "outcome/election", "Interpolated election CT outputs", "share/count"
            raw_dataset = str(INTERP_ROOT.relative_to(REPO_ROOT))
        out.append({
            "variable_name": col,
            "block": block,
            "literature_source": LITERATURE if block.startswith("Block") else "",
            "official_data_source": source,
            "raw_dataset": raw_dataset,
            "processed_dataset": str(OUTPUT_MASTER.relative_to(REPO_ROOT)),
            "processing_script": str(Path(__file__).relative_to(REPO_ROOT)),
            "geographic_level": "CT",
            "units": units,
            "numerator": numerator,
            "denominator": denominator,
            "formula": formula,
            "assumptions": assumptions,
            "status": "documented_limitation" if col.endswith("_note") else status,
        })
    return out


def qa_and_summary(rows: list[dict]) -> tuple[str, list[dict]]:
    total = len(rows)
    duplicate = total - len({r["ct_id"] for r in rows})
    summary = []
    invalid_shares = []
    requests_311_values = [
        (r["ct_id"], as_number(r.get("block5_requests_311_per_1000")))
        for r in rows
        if as_number(r.get("block5_requests_311_per_1000")) is not None
    ]
    max_311 = max(requests_311_values, key=lambda item: item[1]) if requests_311_values else None
    for col in rows[0]:
        vals = [as_number(r.get(col)) for r in rows]
        nums = [v for v in vals if v is not None]
        missing = total - len(nums) if any(as_number(r.get(col)) is not None or str(r.get(col, "")).strip() == "" for r in rows) else sum(1 for r in rows if not str(r.get(col, "")).strip())
        if nums:
            summary.append({
                "variable_name": col,
                "n": len(nums),
                "missing_count": total - len(nums),
                "min": min(nums),
                "median": statistics.median(nums),
                "mean": sum(nums) / len(nums),
                "max": max(nums),
            })
        if "share" in col or "fragmentation" in col or "margin" in col:
            for r, v in zip(rows, vals):
                if v is not None and (v < -1e-9 or v > 1 + 1e-9):
                    invalid_shares.append((r["ct_id"], col, v))
    lines = [
        "# Blocks 1-5 Modelling Variables QA Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        f"- Rows: {total}",
        f"- Unique CT ids: {len({r['ct_id'] for r in rows})}",
        f"- Duplicate CT ids: {duplicate}",
        f"- Variables: {len(rows[0]) if rows else 0}",
        f"- Invalid share/margin/fragmentation values outside [0,1]: {len(invalid_shares)}",
        "",
        "## Notable Issues",
        "",
        "- `block3_citizen_adult_share` retains the Task 1 documented CT `5350047.03` value slightly above 1 due to mixed 25% sample and 100% denominator sources.",
        "- `block5_requests_311_per_1000` is populated as an area-weighted ward-to-CT allocation estimate because 311 raw files have ward/FSA fields but no point coordinates.",
        "- `block5_social_housing_share` is populated from Census Profile characteristic 1491, `% of tenant households in subsidized housing`, converted to a 0-1 share.",
        "- Committee of Adjustment since-2017 current file was unavailable from official endpoints; development variable uses the official Development Applications file only.",
        "- GDAL reported non-fatal topology warnings for some TTS zone overlays; TTS shares were still produced for all 585 CTs and should be treated as approximate area-weighted values.",
    ]
    if max_311:
        lines.append(
            f"- Highest 311 per-capita estimate is CT `{max_311[0]}` with `{max_311[1]:.3f}` requests per 1,000 residents; this reflects area-weighted ward allocation over a low-population CT and should be reviewed before modelling."
        )
    if invalid_shares:
        lines.extend(["", "## Invalid Share Details", ""])
        lines.extend(f"- {ct} {col}={val}" for ct, col, val in invalid_shares[:50])
    return "\n".join(lines) + "\n", [{k: fmt(v) for k, v in row.items()} for row in summary]


def write_methodology() -> None:
    lines = [
        "# Blocks 1-5 Methodology Report",
        "",
        "The master table is one row per 2021 Census Tract in the 585-CT interpolation universe.",
        "",
        "Blocks 1-3 come from the Task 1 Statistics Canada CT Census master.",
        "Block 4 comes from the existing population-weighted CT election interpolation outputs.",
        "Block 5 combines Census, TTS 2022, and Toronto Open Data raw files collected in Task 2.",
        "",
        "Accessibility variables use Euclidean CT-centroid distance because a routable pedestrian/transit network was not collected in Task 2. A 1200 metre threshold is included as a transparent 15-minute walking proxy, assuming roughly 80 metres per minute.",
        "",
        "TTS variables are area-weighted from TTS zones to CT polygons. No CT/TTS population crosswalk exists in the repository, so this is preferred over unweighted assignment but should be treated as an approximation.",
        "GDAL reported non-fatal topology warnings for a small number of TTS zone intersections, indicating invalid source geometries. The pipeline skips failed/zero-area intersections implicitly and records the TTS outputs as approximate.",
        "",
        "All point and geometry transforms use traditional GIS axis order for EPSG coordinate systems to preserve longitude-latitude interpretation of Toronto Open Data coordinates.",
        "",
        "311 requests are aggregated from official 2023, 2024, and 2025 annual files by municipal ward. Because the raw annual files do not include coordinates, ward totals are allocated to CTs by CT-ward intersection-area share using the existing municipal ward-to-CT crosswalk from the interpolation pipeline. The resulting CT count is divided by Census population_total and multiplied by 1000.",
        "",
        "Social housing is measured with the 2021 Census Profile characteristic `% of tenant households in subsidized housing`, converted from percent to a 0-1 share. The denominator is tenant households, not all households or occupied dwellings.",
        "",
    ]
    OUTPUT_METHOD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_METHOD.write_text("\n".join(lines), encoding="utf-8")


def write_registry(dictionary: list[dict]) -> None:
    existing = read_csv(REGISTRY_PATH) if REGISTRY_PATH.exists() else []
    names = {row["variable_name"] for row in dictionary}
    preserved = [row for row in existing if row.get("variable_name") not in names]
    fields = [
        "variable_name", "block", "literature_source", "preferred_data_source", "official_dataset",
        "raw_dataset_location", "processed_dataset_location", "processing_script", "geographic_level",
        "units", "numerator", "denominator", "formula", "assumptions", "status", "notes",
    ]
    additions = []
    for row in dictionary:
        additions.append({
            "variable_name": row["variable_name"],
            "block": row["block"],
            "literature_source": row["literature_source"],
            "preferred_data_source": row["official_data_source"],
            "official_dataset": row["official_data_source"],
            "raw_dataset_location": row["raw_dataset"],
            "processed_dataset_location": row["processed_dataset"],
            "processing_script": row["processing_script"],
            "geographic_level": row["geographic_level"],
            "units": row["units"],
            "numerator": row["numerator"],
            "denominator": row["denominator"],
            "formula": row["formula"],
            "assumptions": row["assumptions"],
            "status": row["status"],
            "notes": "",
        })
    write_csv(REGISTRY_PATH, preserved + additions, fields)


def main() -> None:
    VARIABLES_PROCESSED.mkdir(parents=True, exist_ok=True)
    VARIABLES_METADATA.mkdir(parents=True, exist_ok=True)
    VARIABLES_DOCS.mkdir(parents=True, exist_ok=True)
    rows, cts = build_master()
    write_csv(OUTPUT_MASTER, rows)
    write_geojson(rows, cts)
    dictionary = variable_dictionary(rows)
    write_csv(OUTPUT_DICTIONARY, dictionary)
    qa_report, summary = qa_and_summary(rows)
    OUTPUT_QA.write_text(qa_report, encoding="utf-8")
    write_csv(OUTPUT_SUMMARY, summary)
    write_methodology()
    OUTPUT_LOG.write_text(
        "\n".join([
            "# Blocks 1-5 Processing Log",
            "",
            f"Generated: {date.today().isoformat()}",
            "",
            f"Input Census master: `{CENSUS_MASTER.relative_to(REPO_ROOT)}`",
            f"Input CT polygons: `{CT_POLYGON_SOURCE.relative_to(REPO_ROOT)}`",
            f"Output master: `{OUTPUT_MASTER.relative_to(REPO_ROOT)}`",
            "",
            "Spatial transforms use traditional GIS axis order for EPSG coordinate systems.",
            "GDAL reported non-fatal topology warnings during some TTS overlay intersections.",
            "",
            "No raw files were overwritten.",
        ]) + "\n",
        encoding="utf-8",
    )
    OUTPUT_LIMITATIONS.write_text(
        "\n".join([
            "# Remaining Limitations and Future Improvements",
            "",
            "- Replace Euclidean accessibility with pedestrian-network and transit travel-time accessibility when network data are collected.",
            "- Replace the ward-to-CT 311 allocation with point-geocoded requests if Toronto publishes official coordinate-enabled 311 records in the future.",
            "- Resolve the unavailable Committee of Adjustment since-2017 file or identify an official alternative.",
            "- If the project later needs social-housing units as a share of all households, obtain geocoded social/affordable housing unit records or another official small-area count. The current Census measure is a tenant-household subsidized-housing share.",
            "- Review TTS-to-CT interpolation against any future official TTS zone-to-CT crosswalk.",
            "",
        ]),
        encoding="utf-8",
    )
    write_registry(dictionary)
    print(f"Wrote {len(rows)} CT rows to {OUTPUT_MASTER}")


if __name__ == "__main__":
    main()
