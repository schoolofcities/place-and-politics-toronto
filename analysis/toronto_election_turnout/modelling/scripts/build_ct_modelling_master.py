"""Build the CT-level modelling master dataset."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
CENSUS_ROOT = DATA_ROOT / "census"
INTERP_ROOT = DATA_ROOT / "interpolation" / "processed"
MODELLING_ROOT = DATA_ROOT / "modelling"
PROCESSED_ROOT = MODELLING_ROOT / "processed"
ANALYSIS_ROOT = REPO_ROOT / "analysis" / "toronto_election_turnout" / "modelling"

CT_PROFILE = CENSUS_ROOT / "processed" / "ct" / "statcan_2021_ct_profile.csv"
CT_GEOMETRY = CENSUS_ROOT / "processed" / "ct" / "statcan_2021_toronto_ct.geojson"
CT_PROFILE_ZIP = CENSUS_ROOT / "raw" / "source_downloads" / "statcan_2021_ct_profile.zip"
CT_AGE_ZIP = (
    CENSUS_ROOT / "raw" / "source_downloads" / "statcan_2021_ct_age_single_year_98100024-eng.zip"
)

ELECTIONS = {
    "municipal": "municipal_2023_mayor",
    "provincial": "provincial_2025",
    "federal": "federal_2025",
}

PROFILE_CHARACTERISTICS = {
    "median_age": 40,
    "average_household_size": 57,
    "population_density_per_km2": 6,
    "land_area_km2": 7,
    "total_occupied_private_dwellings_structural_type": 41,
    "single_detached_house_count": 42,
    "semi_detached_house_count": 43,
    "row_house_count": 44,
    "apartment_duplex_count": 45,
    "apartment_lt5_storeys_count": 46,
    "apartment_5plus_storeys_count": 47,
    "total_lim_low_income_status": 335,
    "low_income_lim_at_count": 340,
    "low_income_lim_at_prevalence": 345,
    "official_language_knowledge_total": 383,
    "neither_official_language_count": 387,
    "mother_tongue_total": 393,
    "non_official_mother_tongue_count": 398,
    "tenure_total_households": 1414,
    "owner_households": 1415,
    "renter_households": 1416,
    "condo_status_total_dwellings": 1418,
    "condominium_dwellings": 1419,
    "citizenship_total": 1522,
    "not_canadian_citizens": 1526,
    "immigrant_status_total": 1527,
    "immigrants": 1529,
    "recent_immigrants_2016_2021": 1536,
    "visible_minority_total": 1683,
    "visible_minority_population": 1684,
    "mobility_1yr_total": 1974,
    "same_address_1yr_count": 1975,
    "moved_1yr_count": 1976,
    "mobility_5yr_total": 1983,
    "same_address_5yr_count": 1984,
    "moved_5yr_count": 1985,
    "education_25_64_total": 2014,
    "bachelors_or_higher_25_64_count": 2024,
    "labour_force_total": 2223,
    "unemployment_rate": 2230,
    "commute_mode_total": 2603,
    "car_truck_van_commute_count": 2604,
    "public_transit_commute_count": 2607,
    "walked_commute_count": 2608,
    "bicycle_commute_count": 2609,
    "other_commute_count": 2610,
    "dwelling_condition_total": 1449,
    "major_repairs_needed_count": 1451,
    "shelter_cost_income_total": 1465,
    "shelter_cost_30plus_count": 1467,
    "housing_indicators_total": 1469,
    "housing_indicators_any_issue_count": 1470,
    "core_housing_need_total": 1479,
    "core_housing_need_count": 1480,
    "tenant_households_total": 1490,
    "tenant_households_in_subsidized_housing_pct": 1491,
    "tenant_shelter_cost_30plus_pct": 1492,
    "tenant_core_housing_need_pct": 1493,
}

PROFILE_SOURCE_URL = (
    "https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/"
    "details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=007"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def as_number(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text or text in {"x", "F", "..", "..."}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in {None, 0}:
        return None
    return numerator / denominator


def csv_member(zip_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        data_names = [name for name in names if "data" in name.lower()]
        return data_names[0] if data_names else names[0]


def load_profile_characteristics(target_dguids: set[str]) -> tuple[dict[str, dict], dict[int, str]]:
    wanted = {str(value): key for key, value in PROFILE_CHARACTERISTICS.items()}
    rows = {dguid: {} for dguid in target_dguids}
    labels = {}
    member = csv_member(CT_PROFILE_ZIP)
    with zipfile.ZipFile(CT_PROFILE_ZIP) as archive:
        with archive.open(member) as raw:
            reader = csv.DictReader((line.decode("latin-1") for line in raw))
            for row in reader:
                dguid = row["DGUID"]
                if dguid not in rows:
                    continue
                characteristic_id = row["CHARACTERISTIC_ID"]
                if characteristic_id not in wanted:
                    continue
                column = wanted[characteristic_id]
                labels[int(characteristic_id)] = " ".join(row["CHARACTERISTIC_NAME"].split())
                rows[dguid][column] = as_number(row.get("C1_COUNT_TOTAL"))
                rows[dguid][f"{column}_status"] = row.get("SYMBOL", "")
                rows[dguid][f"{column}_characteristic_id"] = characteristic_id
    return rows, labels


def load_age_bands(target_dguids: set[str]) -> dict[str, dict]:
    output = {
        dguid: {
            "population_age_total": None,
            "school_age_5_17_count": 0,
            "age_18_34_count": 0,
            "age_35_64_count": 0,
            "age_65_plus_count": None,
        }
        for dguid in target_dguids
    }
    with zipfile.ZipFile(CT_AGE_ZIP) as archive:
        with archive.open("98100024.csv") as raw:
            reader = csv.DictReader((line.decode("utf-8-sig") for line in raw))
            for row in reader:
                dguid = row["DGUID"]
                if dguid not in output:
                    continue
                age = row["Age (in single years), average age and median age (128)"]
                count = as_number(row["Gender (3):Total - Gender[1]"])
                if count is None:
                    continue
                record = output[dguid]
                if age == "Total - Age":
                    record["population_age_total"] = count
                elif age == "65 years and over":
                    record["age_65_plus_count"] = count
                elif age.isdigit():
                    age_int = int(age)
                    if 5 <= age_int <= 17:
                        record["school_age_5_17_count"] += count
                    if 18 <= age_int <= 34:
                        record["age_18_34_count"] += count
                    if 35 <= age_int <= 64:
                        record["age_35_64_count"] += count
    return output


def load_ct_base() -> dict[str, dict]:
    return {row["geo_id"]: dict(row) for row in read_csv(CT_PROFILE)}


def load_ct_geometries() -> dict[str, dict]:
    geojson = json.loads(CT_GEOMETRY.read_text(encoding="utf-8"))
    return {feature["properties"]["geo_id"]: feature for feature in geojson["features"]}


def election_results(prefix: str, election_id: str) -> dict[str, dict]:
    rows = {}
    for row in read_csv(INTERP_ROOT / f"{election_id}_ct_estimated_results.csv"):
        rows[row["ct_id"]] = row
    return rows


def party_vote_values(row: dict[str, str]) -> list[float]:
    return [
        value
        for key, raw in row.items()
        if key.startswith("party_") and key.endswith("_votes")
        for value in [as_number(raw)]
        if value is not None and value > 0
    ]


def candidate_vote_values(election_id: str) -> dict[str, list[float]]:
    path = INTERP_ROOT / f"{election_id}_ct_candidate_estimated_votes.csv"
    by_ct: dict[str, list[float]] = {}
    for row in read_csv(path):
        value = as_number(row.get("estimated_candidate_votes"))
        if value is not None and value > 0:
            by_ct.setdefault(row["ct_id"], []).append(value)
    return by_ct


def competition(values: list[float], threshold: float = 0.0) -> dict[str, float | None]:
    total = sum(values)
    if total <= 0:
        return {
            "top_two_margin": None,
            "effective_number": None,
            "fragmentation": None,
            "candidate_or_party_count": None,
        }
    shares_all = sorted((value / total for value in values if value > 0), reverse=True)
    shares = [share for share in shares_all if share >= threshold]
    hhi = sum(share * share for share in shares)
    return {
        "top_two_margin": shares_all[0] - shares_all[1] if len(shares_all) > 1 else None,
        "effective_number": 1 / hhi if hhi else None,
        "fragmentation": 1 - hhi if hhi else None,
        "candidate_or_party_count": len(shares),
    }


def fmt(value: float | int | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return f"{value:.10g}"
        return ""
    return str(value)


def add_rate(row: dict, name: str, numerator: str, denominator: str) -> None:
    row[name] = divide(as_number(row.get(numerator)), as_number(row.get(denominator)))


def build_master() -> tuple[list[dict], dict[str, dict]]:
    election_tables = {
        prefix: election_results(prefix, election_id)
        for prefix, election_id in ELECTIONS.items()
    }
    target_ct_ids = set(election_tables["municipal"])
    base = load_ct_base()
    geometries = load_ct_geometries()
    dguids = {base[ct_id]["dguid"] for ct_id in target_ct_ids if ct_id in base}
    profile_values, labels = load_profile_characteristics(dguids)
    age_values = load_age_bands(dguids)
    municipal_candidate_votes = candidate_vote_values(ELECTIONS["municipal"])

    rows = []
    for ct_id in sorted(target_ct_ids):
        census = base.get(ct_id, {})
        dguid = census.get("dguid", "")
        row = {
            "ct_id": ct_id,
            "dguid": dguid,
            "geo_name": census.get("geo_name", ""),
            "census_year": census.get("census_year", "2021"),
            "citizen_canadian_18over": census.get("citizen_canadian_18over", ""),
            "citizen_canadian_18over_status": census.get("citizen_canadian_18over_status", ""),
            "population_total": census.get("population_total", ""),
            "population_under18": census.get("population_under18", ""),
            "population_18plus": census.get("population_18plus", ""),
            "population_18plus_status": census.get("population_18plus_status", ""),
        }
        row.update(profile_values.get(dguid, {}))
        row.update(age_values.get(dguid, {}))

        for prefix, table in election_tables.items():
            election = table.get(ct_id, {})
            row[f"{prefix}_turnout_electors"] = election.get("estimated_turnout", "")
            row[f"{prefix}_participation_citizen_18plus"] = election.get(
                "estimated_participation_citizen_18plus",
                election.get("estimated_turnout_citizen_18plus", ""),
            )
            row[f"{prefix}_estimated_total_votes"] = election.get("estimated_total_votes", "")
            row[f"{prefix}_estimated_electors"] = election.get("estimated_electors", "")
            row[f"{prefix}_estimated_valid_candidate_votes"] = election.get(
                "estimated_valid_candidate_votes", ""
            )
            for flag in [
                "suppressed_da_count",
                "suppressed_da_area_share",
                "excluded_weight_area_share",
                "fallback_area_weight_used",
                "no_geometry_district_allocation_used",
                "votes_exceed_electors_flag",
                "missing_votes_excluded_flag",
                "ancillary_weight_status",
            ]:
                row[f"{prefix}_{flag}"] = election.get(flag, "")

        participation_values = [
            as_number(row.get(f"{prefix}_participation_citizen_18plus"))
            for prefix in ELECTIONS
        ]
        present = [value for value in participation_values if value is not None]
        row["mean_participation_citizen_18plus"] = sum(present) / len(present) if present else None
        row["mean_participation_component_count"] = len(present)
        row["federal_minus_municipal_participation"] = (
            participation_values[2] - participation_values[0]
            if participation_values[2] is not None and participation_values[0] is not None
            else None
        )
        row["provincial_minus_municipal_participation"] = (
            participation_values[1] - participation_values[0]
            if participation_values[1] is not None and participation_values[0] is not None
            else None
        )

        for count_name, share_name, denominator in [
            ("age_18_34_count", "share_age_18_34", "population_age_total"),
            ("age_35_64_count", "share_age_35_64", "population_age_total"),
            ("age_65_plus_count", "share_age_65_plus", "population_age_total"),
            ("school_age_5_17_count", "school_age_population_share", "population_age_total"),
            ("bachelors_or_higher_25_64_count", "bachelors_degree_share", "education_25_64_total"),
            ("low_income_lim_at_count", "low_income_share", "total_lim_low_income_status"),
            ("renter_households", "renter_share", "tenure_total_households"),
            ("owner_households", "owner_share", "tenure_total_households"),
            ("moved_1yr_count", "recent_mover_share", "mobility_1yr_total"),
            ("same_address_1yr_count", "same_address_1yr_share", "mobility_1yr_total"),
            ("same_address_5yr_count", "same_address_5yr_share", "mobility_5yr_total"),
            ("condominium_dwellings", "condo_share", "condo_status_total_dwellings"),
            ("immigrants", "immigrant_share", "immigrant_status_total"),
            ("recent_immigrants_2016_2021", "recent_immigrant_share", "immigrant_status_total"),
            ("not_canadian_citizens", "non_citizen_share", "citizenship_total"),
            ("visible_minority_population", "visible_minority_share", "visible_minority_total"),
            ("non_official_mother_tongue_count", "non_official_language_mother_tongue_share", "mother_tongue_total"),
            ("public_transit_commute_count", "transit_commute_share", "commute_mode_total"),
            ("car_truck_van_commute_count", "car_commute_share", "commute_mode_total"),
            ("walked_commute_count", "walked_commute_share", "commute_mode_total"),
            ("bicycle_commute_count", "bicycle_commute_share", "commute_mode_total"),
            ("other_commute_count", "other_commute_share", "commute_mode_total"),
            ("major_repairs_needed_count", "major_repairs_needed_share", "dwelling_condition_total"),
            ("shelter_cost_30plus_count", "shelter_cost_30plus_share", "shelter_cost_income_total"),
            ("housing_indicators_any_issue_count", "housing_condition_issue_share", "housing_indicators_total"),
            ("core_housing_need_count", "core_housing_need_share", "core_housing_need_total"),
        ]:
            row[share_name] = divide(as_number(row.get(count_name)), as_number(row.get(denominator)))
        non_car_commute = None
        car_commute = row.get("car_commute_share")
        if car_commute is not None:
            non_car_commute = 1 - float(car_commute)
        row["non_car_commute_share"] = non_car_commute
        walked_value = as_number(row.get("walked_commute_share"))
        bicycle_value = as_number(row.get("bicycle_commute_share"))
        walked = walked_value or 0
        bicycle = bicycle_value or 0
        row["active_commute_share"] = (
            walked + bicycle
            if walked_value is not None or bicycle_value is not None
            else None
        )
        row["citizen_adult_share"] = divide(
            as_number(row.get("citizen_canadian_18over")),
            as_number(row.get("population_18plus")),
        )
        row["official_language_knowledge_share"] = (
            1
            - divide(
                as_number(row.get("neither_official_language_count")),
                as_number(row.get("official_language_knowledge_total")),
            )
            if divide(
                as_number(row.get("neither_official_language_count")),
                as_number(row.get("official_language_knowledge_total")),
            )
            is not None
            else None
        )
        apartment_count = sum(
            as_number(row.get(key)) or 0
            for key in [
                "apartment_duplex_count",
                "apartment_lt5_storeys_count",
                "apartment_5plus_storeys_count",
            ]
        )
        detached_semi_count = sum(
            as_number(row.get(key)) or 0
            for key in ["single_detached_house_count", "semi_detached_house_count"]
        )
        row["apartment_share"] = divide(
            apartment_count, as_number(row.get("total_occupied_private_dwellings_structural_type"))
        )
        row["detached_or_semi_detached_share"] = divide(
            detached_semi_count,
            as_number(row.get("total_occupied_private_dwellings_structural_type")),
        )
        row["no_car_household_share"] = ""
        row["no_car_household_proxy_note"] = (
            "No direct household vehicle-availability variable found in the official 2021 CT Census Profile; "
            "use non_car_commute_share only as a commuter-mode proxy, not a household no-car measure."
        )
        subsidized_pct = as_number(row.get("tenant_households_in_subsidized_housing_pct"))
        row["social_housing_share"] = subsidized_pct / 100 if subsidized_pct is not None else None
        for service_column in [
            "library_accessibility",
            "community_centre_accessibility",
            "park_accessibility",
            "road_safety_exposure",
            "development_applications_per_capita",
            "shelter_service_proximity",
            "311_requests_per_capita",
        ]:
            row[service_column] = ""

        municipal_comp = competition(municipal_candidate_votes.get(ct_id, []))
        municipal_comp_5pct = competition(municipal_candidate_votes.get(ct_id, []), threshold=0.05)
        row["municipal_top_two_margin"] = municipal_comp["top_two_margin"]
        row["municipal_effective_number_of_candidates"] = municipal_comp["effective_number"]
        row["municipal_vote_fragmentation"] = municipal_comp["fragmentation"]
        row["municipal_top_two_margin_5pct"] = municipal_comp_5pct["top_two_margin"]
        row["municipal_effective_number_of_candidates_5pct"] = municipal_comp_5pct["effective_number"]
        row["municipal_candidate_count_5pct"] = municipal_comp_5pct["candidate_or_party_count"]
        row["municipal_vote_fragmentation_5pct"] = municipal_comp_5pct["fragmentation"]
        for prefix in ["provincial", "federal"]:
            values = party_vote_values(election_tables[prefix].get(ct_id, {}))
            comp = competition(values)
            comp_5pct = competition(values, threshold=0.05)
            row[f"{prefix}_top_two_party_margin"] = comp["top_two_margin"]
            row[f"{prefix}_effective_number_of_parties"] = comp["effective_number"]
            row[f"{prefix}_vote_fragmentation"] = comp["fragmentation"]
            row[f"{prefix}_top_two_party_margin_5pct"] = comp_5pct["top_two_margin"]
            row[f"{prefix}_effective_number_of_parties_5pct"] = comp_5pct["effective_number"]
            row[f"{prefix}_party_count_5pct"] = comp_5pct["candidate_or_party_count"]
            row[f"{prefix}_vote_fragmentation_5pct"] = comp_5pct["fragmentation"]

        rows.append({key: fmt(value) for key, value in row.items()})
    return rows, geometries


def write_geojson(rows: list[dict], geometries: dict[str, dict]) -> None:
    features = []
    by_ct = {row["ct_id"]: row for row in rows}
    for ct_id in sorted(by_ct):
        feature = geometries.get(ct_id)
        if not feature:
            continue
        output_feature = {
            "type": "Feature",
            "properties": by_ct[ct_id],
            "geometry": feature["geometry"],
        }
        features.append(output_feature)
    payload = {"type": "FeatureCollection", "features": features}
    path = PROCESSED_ROOT / "toronto_ct_modelling_master.geojson"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


CURATED_SCHEMA = [
    ("ct_id", "ct_id"),
    ("dguid", "dguid"),
    ("dem_share_18_34", "share_age_18_34"),
    ("dem_share_35_64", "share_age_35_64"),
    ("dem_share_65_plus", "share_age_65_plus"),
    ("dem_median_age", "median_age"),
    ("dem_average_household_size", "average_household_size"),
    ("dem_bachelors_plus_share", "bachelors_degree_share"),
    ("dem_low_income_share", "low_income_share"),
    ("dem_unemployment_rate", "unemployment_rate"),
    ("housing_renter_share", "renter_share"),
    ("housing_owner_share", "owner_share"),
    ("housing_recent_mover_share", "recent_mover_share"),
    ("housing_same_address_1yr_share", "same_address_1yr_share"),
    ("housing_same_address_5yr_share", "same_address_5yr_share"),
    ("housing_condo_share", "condo_share"),
    ("housing_apartment_share", "apartment_share"),
    ("housing_detached_semi_share", "detached_or_semi_detached_share"),
    ("housing_population_density_per_km2", "population_density_per_km2"),
    ("immigration_immigrant_share", "immigrant_share"),
    ("immigration_recent_immigrant_share", "recent_immigrant_share"),
    ("immigration_non_citizen_share", "non_citizen_share"),
    ("eligibility_citizen_adult_share", "citizen_adult_share"),
    ("racialized_visible_minority_share", "visible_minority_share"),
    ("language_english_french_knowledge_share", "official_language_knowledge_share"),
    ("language_non_official_mother_tongue_share", "non_official_language_mother_tongue_share"),
    ("election_mayoral_winner_margin", "municipal_top_two_margin"),
    ("election_mayoral_top_two_margin", "municipal_top_two_margin"),
    ("election_effective_mayoral_candidates_5pct", "municipal_effective_number_of_candidates_5pct"),
    ("election_mayoral_candidate_count_5pct", "municipal_candidate_count_5pct"),
    ("election_mayoral_vote_fragmentation", "municipal_vote_fragmentation_5pct"),
    ("election_federal_margin", "federal_top_two_party_margin"),
    ("election_provincial_margin", "provincial_top_two_party_margin"),
    ("election_effective_federal_parties_5pct", "federal_effective_number_of_parties_5pct"),
    ("election_effective_provincial_parties_5pct", "provincial_effective_number_of_parties_5pct"),
    ("election_federal_party_count_5pct", "federal_party_count_5pct"),
    ("election_provincial_party_count_5pct", "provincial_party_count_5pct"),
    ("service_transit_commute_share", "transit_commute_share"),
    ("service_no_car_household_share", "no_car_household_share"),
    ("service_non_car_commute_share_proxy", "non_car_commute_share"),
    ("service_social_housing_share", "social_housing_share"),
    ("service_311_requests_per_capita", "311_requests_per_capita"),
    ("service_library_access_15m_walk_transit", "library_accessibility"),
    ("service_community_centre_access", "community_centre_accessibility"),
    ("service_park_access", "park_accessibility"),
    ("service_school_age_population_share", "school_age_population_share"),
    ("service_road_safety_exposure", "road_safety_exposure"),
    ("service_development_applications_per_capita", "development_applications_per_capita"),
    ("service_shelter_service_proximity", "shelter_service_proximity"),
    ("info_education_bachelors_plus_share", "bachelors_degree_share"),
    ("info_age_median", "median_age"),
    ("info_age_share_18_34", "share_age_18_34"),
    ("info_federal_turnout_proxy", "federal_participation_citizen_18plus"),
    ("info_provincial_turnout_proxy", "provincial_participation_citizen_18plus"),
    ("info_municipal_candidate_count_5pct", "municipal_candidate_count_5pct"),
    ("info_campaign_spending", ""),
    ("info_local_media_coverage_by_ward", ""),
    ("info_candidate_website_platform_availability", ""),
    ("info_candidate_events", ""),
    ("info_endorsement_density", ""),
    ("outcome_municipal_participation_citizen_18plus", "municipal_participation_citizen_18plus"),
    ("outcome_provincial_participation_citizen_18plus", "provincial_participation_citizen_18plus"),
    ("outcome_federal_participation_citizen_18plus", "federal_participation_citizen_18plus"),
    ("outcome_mean_participation_citizen_18plus", "mean_participation_citizen_18plus"),
    ("outcome_federal_minus_municipal_participation", "federal_minus_municipal_participation"),
    ("outcome_provincial_minus_municipal_participation", "provincial_minus_municipal_participation"),
]


def curated_rows(master_rows: list[dict]) -> list[dict]:
    output = []
    for row in master_rows:
        curated = {}
        for clean_name, source_name in CURATED_SCHEMA:
            curated[clean_name] = row.get(source_name, "") if source_name else ""
        output.append(curated)
    return output


def write_curated_geojson(rows: list[dict], geometries: dict[str, dict]) -> None:
    features = []
    for row in rows:
        feature = geometries.get(row["ct_id"])
        if not feature:
            continue
        features.append(
            {
                "type": "Feature",
                "properties": row,
                "geometry": feature["geometry"],
            }
        )
    (PROCESSED_ROOT / "toronto_ct_modelling_curated.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def curated_missingness_rows(rows: list[dict]) -> list[dict]:
    total = len(rows)
    output = []
    for clean_name, _ in CURATED_SCHEMA:
        missing = sum(1 for row in rows if not str(row.get(clean_name, "")).strip())
        block = clean_name.split("_", 1)[0]
        output.append(
            {
                "variable_name": clean_name,
                "variable_group": block,
                "missing_count": missing,
                "missing_share": f"{missing / total:.6f}" if total else "",
                "availability": (
                    "complete"
                    if missing == 0
                    else "some_missing"
                    if missing < total
                    else "missing_all"
                ),
            }
        )
    return output


def inventory_rows(master_rows: list[dict]) -> list[dict]:
    rows = []
    total = len(master_rows)
    for column in master_rows[0]:
        missing = sum(1 for row in master_rows if str(row.get(column, "")).strip() == "")
        block = "identifier"
        if column in {"ct_id", "dguid", "geo_name", "census_year"}:
            block = "identifier"
        elif "municipal" in column or "provincial" in column or "federal" in column or column.startswith("mean_"):
            block = "dependent_or_election_construct"
        elif any(token in column for token in ["age", "household_size", "bachelors", "income", "unemployment"]):
            block = "block_1_demographic"
        elif any(token in column for token in ["renter", "owner", "mover", "address", "condo", "apartment", "detached", "density"]):
            block = "block_2_housing_stability"
        elif any(token in column for token in ["immigrant", "citizen", "visible", "language", "mother_tongue"]):
            block = "block_3_immigration_citizenship"
        elif any(
            token in column
            for token in [
                "transit",
                "commute",
                "school_age",
                "social_housing",
                "no_car",
                "library",
                "community_centre",
                "park",
                "road_safety",
                "development",
                "shelter",
                "311",
                "core_housing",
                "major_repairs",
                "housing_condition",
            ]
        ):
            block = "block_5_service_contact"
        rows.append(
            {
                "variable_name": column,
                "concept_block": block,
                "description": column.replace("_", " "),
                "source_dataset": "derived modelling master",
                "source_file": "toronto_ct_modelling_master.csv",
                "source_year": "2021/2023/2025",
                "geographic_level": "CT",
                "ct_join_key": "ct_id",
                "available_now": "yes" if missing < total else "no",
                "requires_new_download": "no" if missing < total else "yes",
                "missing_count": missing,
                "missing_share": f"{missing / total:.6f}" if total else "",
                "status_or_quality_field": "",
                "notes": "",
            }
        )
    return rows


def missing_variable_rows() -> list[dict]:
    return [
        {
            "dataset_name": "Statistics Canada 2021 CT Census Profile",
            "variable_block": "Block 5",
            "needed_variables": "no_car_household_share",
            "official_source": "Statistics Canada",
            "download_url_or_api": PROFILE_SOURCE_URL,
            "geographic_level": "CT",
            "source_year": "2021",
            "license": "Statistics Canada Open Licence",
            "processing_method": "Searched official CT Census Profile labels for vehicle/car/no-car wording.",
            "estimated_difficulty": "not available in source",
            "priority": "low",
            "notes": "No direct household vehicle-availability variable found. Added non_car_commute_share, car_commute_share, transit_commute_share, walked_commute_share, bicycle_commute_share, and active_commute_share as official commuter-mode proxies only.",
        },
        {
            "dataset_name": "Statistics Canada 2021 CT Census Profile housing proxies",
            "variable_block": "Block 5",
            "needed_variables": "shelter_service_proximity; road_safety_exposure",
            "official_source": "Statistics Canada",
            "download_url_or_api": PROFILE_SOURCE_URL,
            "geographic_level": "CT",
            "source_year": "2021",
            "license": "Statistics Canada Open Licence",
            "processing_method": "Searched official CT Census Profile labels for shelter, housing indicators, repairs, core housing need, and commuting mode.",
            "estimated_difficulty": "proxy only",
            "priority": "medium",
            "notes": "Added shelter_cost_30plus_share, housing_condition_issue_share, core_housing_need_share, major_repairs_needed_share, social_housing_share, car_commute_share, and active_commute_share. These are contextual proxies, not direct proximity/exposure measures.",
        },
        {
            "dataset_name": "Open Toronto 311 service requests",
            "variable_block": "Block 5",
            "needed_variables": "311_requests_per_capita",
            "official_source": "City of Toronto Open Data",
            "download_url_or_api": "To be selected from Open Toronto 311 datasets",
            "geographic_level": "point/address or service request record",
            "source_year": "2023-2025",
            "license": "Open Government Licence - Toronto",
            "processing_method": "geocode or use provided coordinates; spatially aggregate to 2021 CT; divide by citizen_canadian_18over",
            "estimated_difficulty": "medium",
            "priority": "medium",
            "notes": "Not a Census Profile variable; requires service-request scope decisions.",
        },
        {
            "dataset_name": "Open Toronto civic facility points",
            "variable_block": "Block 5",
            "needed_variables": "library_accessibility; community_centre_accessibility; park_accessibility; shelter_service_proximity",
            "official_source": "City of Toronto Open Data",
            "download_url_or_api": "Open Toronto libraries/community centres/parks/shelters datasets",
            "geographic_level": "point/polygon",
            "source_year": "current",
            "license": "Open Government Licence - Toronto",
            "processing_method": "distance from CT centroid or population-weighted centroid to nearest facility; optionally count facilities per capita",
            "estimated_difficulty": "medium",
            "priority": "medium",
            "notes": "Requires choosing distance versus density operationalization.",
        },
        {
            "dataset_name": "Open Toronto development applications",
            "variable_block": "Block 5",
            "needed_variables": "development_applications_per_capita",
            "official_source": "City of Toronto Open Data",
            "download_url_or_api": "Open Toronto development application datasets",
            "geographic_level": "point/address/polygon",
            "source_year": "2021-2025",
            "license": "Open Government Licence - Toronto",
            "processing_method": "spatially aggregate applications to CT and divide by citizen_canadian_18over",
            "estimated_difficulty": "medium",
            "priority": "low",
            "notes": "Time window should be chosen before implementation.",
        },
        {
            "dataset_name": "Road safety collision/exposure data",
            "variable_block": "Block 5",
            "needed_variables": "road_safety_exposure",
            "official_source": "City of Toronto Open Data",
            "download_url_or_api": "Open Toronto collision/KSI or traffic volume datasets",
            "geographic_level": "point/segment",
            "source_year": "multi-year",
            "license": "Open Government Licence - Toronto",
            "processing_method": "spatially aggregate collisions/exposure to CT; normalize by population or road length",
            "estimated_difficulty": "medium-high",
            "priority": "low",
            "notes": "Needs conceptual decision: collision counts, KSI counts, traffic volume, or road length.",
        },
        {
            "dataset_name": "Vehicle availability / no-car households",
            "variable_block": "Block 5",
            "needed_variables": "no_car_household_share",
            "official_source": "Not found in 2021 Census Profile CT extract",
            "download_url_or_api": "TBD",
            "geographic_level": "CT or custom geography",
            "source_year": "TBD",
            "license": "TBD",
            "processing_method": "TBD",
            "estimated_difficulty": "unknown",
            "priority": "low",
            "notes": "Not populated in master dataset.",
        },
    ]


def write_docs(master_rows: list[dict]) -> None:
    ANALYSIS_ROOT.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_ROOT / "README.md").write_text(
        "# CT Turnout Modelling\n\n"
        "Builds a CT-level modelling master dataset from the existing census, "
        "interpolation, and election outputs.\n\n"
        "Run from `analysis/toronto_election_turnout/`:\n\n"
        "```bash\nnpm run build:modelling\n```\n",
        encoding="utf-8",
    )
    (MODELLING_ROOT / "README.md").write_text(
        "# CT Modelling Data\n\n"
        "`processed/toronto_ct_modelling_curated.csv` is the recommended "
        "analysis-ready one-row-per-CT modelling table. It contains only the "
        "selected modelling variables and outcomes.\n\n"
        "`processed/toronto_ct_modelling_master.csv` is the verbose provenance "
        "table with raw counts, source status fields, and StatCan characteristic "
        "IDs. Use it for auditing, not as the default modelling input.\n\n"
        "The CT universe follows the 585 CTs used by the interpolation outputs. "
        "Use `ct_id` as the join key.\n",
        encoding="utf-8",
    )
    docs = [
        "# CT Modelling Dataset Methodology",
        "",
        f"Rows: {len(master_rows)} CTs, matching the interpolation target universe.",
        "",
        "The primary dependent variable for Model E is",
        "`mean_participation_citizen_18plus`, the mean of municipal, provincial,",
        "and federal CT participation rates calculated with",
        "`citizen_canadian_18over` as the denominator.",
        "",
        "Official elector turnout fields are retained separately as",
        "`*_turnout_electors`. These are not forced to match Census population",
        "variables.",
        "",
        "Blocks 1-3 are extracted from the official Statistics Canada 2021 CT",
        "Census Profile and the official 2021 CT single-year age table. Block 4",
        "competitiveness variables are computed from the existing CT interpolated",
        "candidate/party vote outputs. Block 5 variables are populated where a",
        "Census Profile variable is directly available, and non-Census service",
        "variables are listed in the missing-variable checklist for future",
        "official Open Toronto acquisition.",
        "",
        "Competitiveness formulas:",
        "",
        "- share = candidate or party votes / total valid candidate or party votes",
        "- top-two margin = top share - second share",
        "- effective number = 1 / sum(share_i^2)",
        "- fragmentation = 1 - sum(share_i^2)",
        "",
        "Downloaded official Census Profile source:",
        "",
        f"- {PROFILE_SOURCE_URL}",
        "",
    ]
    (ANALYSIS_ROOT / "docs" / "ct_modelling_dataset_methodology.md").parent.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_ROOT / "docs" / "ct_modelling_dataset_methodology.md").write_text(
        "\n".join(docs), encoding="utf-8"
    )


def main() -> None:
    master_rows, geometries = build_master()
    clean_rows = curated_rows(master_rows)
    PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)
    write_csv(PROCESSED_ROOT / "toronto_ct_modelling_master.csv", master_rows)
    write_geojson(master_rows, geometries)
    write_csv(PROCESSED_ROOT / "toronto_ct_modelling_curated.csv", clean_rows)
    write_curated_geojson(clean_rows, geometries)
    write_csv(PROCESSED_ROOT / "toronto_ct_modelling_curated_missingness.csv", curated_missingness_rows(clean_rows))
    write_csv(PROCESSED_ROOT / "variable_inventory.csv", inventory_rows(master_rows))
    write_csv(PROCESSED_ROOT / "missing_variable_checklist.csv", missing_variable_rows())
    write_docs(master_rows)
    print(f"Wrote {len(master_rows)} CT modelling rows to {PROCESSED_ROOT}")


if __name__ == "__main__":
    main()
