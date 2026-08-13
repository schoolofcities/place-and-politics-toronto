"""Build CT-level 2021 Census variables for turnout modelling.

This script uses only official Statistics Canada files already stored under
data/toronto_election_turnout/census/raw/source_downloads.
"""

from __future__ import annotations

import csv
from datetime import date
import json
import math
from pathlib import Path
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
CENSUS_ROOT = DATA_ROOT / "census"
PROCESSED_ROOT = CENSUS_ROOT / "processed"
CT_GEOMETRY = PROCESSED_ROOT / "ct" / "statcan_2021_toronto_ct.geojson"
CT_PROFILE_BASE = PROCESSED_ROOT / "ct" / "statcan_2021_ct_profile.csv"
CT_PROFILE_ZIP = CENSUS_ROOT / "raw" / "source_downloads" / "statcan_2021_ct_profile.zip"
CT_AGE_ZIP = (
    CENSUS_ROOT / "raw" / "source_downloads" / "statcan_2021_ct_age_single_year_98100024-eng.zip"
)
INTERPOLATION_ROOT = DATA_ROOT / "interpolation" / "processed"
REGISTRY_PATH = DATA_ROOT / "metadata" / "variable_registry.csv"

OUTPUT_MASTER = PROCESSED_ROOT / "ct" / "statcan_2021_ct_census_variables_master.csv"
OUTPUT_DICTIONARY = (
    PROCESSED_ROOT / "metadata" / "statcan_2021_ct_census_variables_dictionary.csv"
)
OUTPUT_QA = (
    PROCESSED_ROOT
    / "audits"
    / "profile_extraction"
    / "statcan_2021_ct_census_variables_qa_report.md"
)
OUTPUT_MISSING = (
    PROCESSED_ROOT
    / "audits"
    / "profile_extraction"
    / "statcan_2021_ct_census_variables_missing_report.csv"
)
OUTPUT_LOG = (
    PROCESSED_ROOT
    / "audits"
    / "profile_extraction"
    / "statcan_2021_ct_census_variables_processing_log.md"
)

PROFILE_SOURCE_URL = (
    "https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/"
    "details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=007"
)
AGE_SOURCE_URL = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810002401"
LITERATURE = (
    "Marshall & Siemiatycki (2014); Couture, Bherer & Breux (2014); "
    "Geys (2006); Cancela & Geys (2016); Dostie-Goulet et al. (2012); "
    "McGregor (2018); Siaroff & Wesley (2015)"
)


PROFILE_CHARACTERISTICS = {
    "population_total": 1,
    "population_density_per_km2": 6,
    "land_area_km2": 7,
    "median_age": 40,
    "structural_type_total_dwellings": 41,
    "single_detached_house_count": 42,
    "semi_detached_house_count": 43,
    "apartment_duplex_count": 45,
    "apartment_lt5_storeys_count": 46,
    "apartment_5plus_storeys_count": 47,
    "average_household_size": 57,
    "low_income_status_total": 335,
    "low_income_lim_at_count": 340,
    "low_income_lim_at_prevalence_pct_official": 345,
    "official_language_knowledge_total": 383,
    "neither_english_nor_french_count": 387,
    "mother_tongue_total": 393,
    "non_official_mother_tongue_count": 398,
    "tenure_total_households": 1414,
    "owner_households_count": 1415,
    "renter_households_count": 1416,
    "condo_status_total_dwellings": 1418,
    "condominium_dwellings_count": 1419,
    "subsidized_housing_tenant_pct_official": 1491,
    "citizenship_total": 1522,
    "canadian_citizens_18plus_count": 1525,
    "not_canadian_citizens_count": 1526,
    "immigrant_status_total": 1527,
    "immigrants_count": 1529,
    "recent_immigrants_2016_2021_count": 1536,
    "visible_minority_total": 1683,
    "visible_minority_population_count": 1684,
    "mobility_1yr_total": 1974,
    "same_address_1yr_count": 1975,
    "moved_1yr_count": 1976,
    "mobility_5yr_total": 1983,
    "same_address_5yr_count": 1984,
    "moved_5yr_count": 1985,
    "education_25_64_total": 2014,
    "bachelors_or_higher_25_64_count": 2024,
    "labour_force_total": 2223,
    "unemployment_rate_pct_official": 2230,
    "commute_mode_total": 2603,
    "public_transit_commute_count": 2607,
}

DERIVED_VARIABLES = [
    {
        "name": "age_18_34_share",
        "block": "Block 1",
        "denominator": "population_age_total",
        "formula": "age_18_34_count / population_age_total",
        "units": "share",
        "notes": "Single-year age cube, total population including institutional residents.",
    },
    {
        "name": "age_35_64_share",
        "block": "Block 1",
        "denominator": "population_age_total",
        "formula": "age_35_64_count / population_age_total",
        "units": "share",
        "notes": "Single-year age cube, total population including institutional residents.",
    },
    {
        "name": "age_65_plus_share",
        "block": "Block 1",
        "denominator": "population_age_total",
        "formula": "age_65_plus_count / population_age_total",
        "units": "share",
        "notes": "Uses the official 65 years and over age aggregate.",
    },
    {
        "name": "bachelors_or_higher_25_64_share",
        "block": "Block 1",
        "denominator": "education_25_64_total",
        "formula": "bachelors_or_higher_25_64_count / education_25_64_total",
        "units": "share",
        "notes": "Population aged 25 to 64 in private households.",
    },
    {
        "name": "low_income_lim_at_share",
        "block": "Block 1",
        "denominator": "low_income_status_total",
        "formula": "low_income_lim_at_count / low_income_status_total",
        "units": "share",
        "notes": "LIM-AT low-income status for population in private households.",
    },
    {
        "name": "unemployment_rate_share",
        "block": "Block 1",
        "denominator": "labour_force_total",
        "formula": "unemployment_rate_pct_official / 100",
        "units": "share",
        "notes": "Official Census unemployment rate converted from percent to share.",
    },
    {
        "name": "renter_share",
        "block": "Block 2",
        "denominator": "tenure_total_households",
        "formula": "renter_households_count / tenure_total_households",
        "units": "share",
        "notes": "Private households by tenure, 25% sample.",
    },
    {
        "name": "owner_share",
        "block": "Block 2",
        "denominator": "tenure_total_households",
        "formula": "owner_households_count / tenure_total_households",
        "units": "share",
        "notes": "Private households by tenure, 25% sample.",
    },
    {
        "name": "same_address_1yr_share",
        "block": "Block 2",
        "denominator": "mobility_1yr_total",
        "formula": "same_address_1yr_count / mobility_1yr_total",
        "units": "share",
        "notes": "Census non-movers are interpreted as same address one year ago.",
    },
    {
        "name": "same_address_5yr_share",
        "block": "Block 2",
        "denominator": "mobility_5yr_total",
        "formula": "same_address_5yr_count / mobility_5yr_total",
        "units": "share",
        "notes": "Census non-movers are interpreted as same address five years ago.",
    },
    {
        "name": "condo_share",
        "block": "Block 2",
        "denominator": "condo_status_total_dwellings",
        "formula": "condominium_dwellings_count / condo_status_total_dwellings",
        "units": "share",
        "notes": "Occupied private dwellings by condominium status.",
    },
    {
        "name": "subsidized_housing_tenant_share",
        "block": "Block 5",
        "denominator": "tenant households",
        "formula": "subsidized_housing_tenant_pct_official / 100",
        "units": "share",
        "notes": "Official Census Profile characteristic 1491: percent of tenant households in subsidized housing, converted from percent to share.",
    },
    {
        "name": "apartment_share",
        "block": "Block 2",
        "denominator": "structural_type_total_dwellings",
        "formula": "(apartment_duplex_count + apartment_lt5_storeys_count + apartment_5plus_storeys_count) / structural_type_total_dwellings",
        "units": "share",
        "notes": "Apartments include duplex, fewer-than-five-storey, and five-plus-storey apartment categories.",
    },
    {
        "name": "detached_share",
        "block": "Block 2",
        "denominator": "structural_type_total_dwellings",
        "formula": "single_detached_house_count / structural_type_total_dwellings",
        "units": "share",
        "notes": "Single-detached houses only.",
    },
    {
        "name": "semi_detached_share",
        "block": "Block 2",
        "denominator": "structural_type_total_dwellings",
        "formula": "semi_detached_house_count / structural_type_total_dwellings",
        "units": "share",
        "notes": "Semi-detached houses only.",
    },
    {
        "name": "immigrant_share",
        "block": "Block 3",
        "denominator": "immigrant_status_total",
        "formula": "immigrants_count / immigrant_status_total",
        "units": "share",
        "notes": "Population in private households by immigrant status.",
    },
    {
        "name": "recent_immigrant_share",
        "block": "Block 3",
        "denominator": "immigrant_status_total",
        "formula": "recent_immigrants_2016_2021_count / immigrant_status_total",
        "units": "share",
        "notes": "Recent immigrants are persons whose period of immigration is 2016 to 2021.",
    },
    {
        "name": "non_citizen_share",
        "block": "Block 3",
        "denominator": "citizenship_total",
        "formula": "not_canadian_citizens_count / citizenship_total",
        "units": "share",
        "notes": "Population in private households by citizenship.",
    },
    {
        "name": "citizen_adult_share",
        "block": "Block 3",
        "denominator": "population_18plus",
        "formula": "canadian_citizens_18plus_count / population_18plus",
        "units": "share",
        "notes": "Canadian citizens aged 18+ divided by total 18+ population from the official single-year age cube.",
    },
    {
        "name": "visible_minority_share",
        "block": "Block 3",
        "denominator": "visible_minority_total",
        "formula": "visible_minority_population_count / visible_minority_total",
        "units": "share",
        "notes": "Census visible minority concept is used as the racialized-population operationalization.",
    },
    {
        "name": "english_french_knowledge_share",
        "block": "Block 3",
        "denominator": "official_language_knowledge_total",
        "formula": "(official_language_knowledge_total - neither_english_nor_french_count) / official_language_knowledge_total",
        "units": "share",
        "notes": "Share knowing English, French, or both; excludes institutional residents.",
    },
    {
        "name": "non_official_mother_tongue_share",
        "block": "Block 3",
        "denominator": "mother_tongue_total",
        "formula": "non_official_mother_tongue_count / mother_tongue_total",
        "units": "share",
        "notes": "Non-official languages mother tongue category.",
    },
    {
        "name": "transit_commute_share",
        "block": "Block 5",
        "denominator": "commute_mode_total",
        "formula": "public_transit_commute_count / commute_mode_total",
        "units": "share",
        "notes": "Main mode of commuting; preserved as the Census version for comparison.",
    },
    {
        "name": "school_age_5_17_share",
        "block": "Block 5",
        "denominator": "population_age_total",
        "formula": "school_age_5_17_count / population_age_total",
        "units": "share",
        "notes": "School-age population operationalized as ages 5 to 17 from the single-year age cube.",
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
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
    if not text or text in {"..", "...", "x", "F"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def fmt(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return round(value, 10)
    return value


def csv_member(zip_path: Path, preferred_name: str | None = None) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if preferred_name and preferred_name in names:
            return preferred_name
        data_names = [name for name in names if "data" in name.lower()]
        return data_names[0] if data_names else names[0]


def load_ct_geometry_properties() -> dict[str, dict]:
    geojson = json.loads(CT_GEOMETRY.read_text(encoding="utf-8"))
    output = {}
    for feature in geojson["features"]:
        props = feature["properties"]
        ct_id = props["geo_id"]
        output[ct_id] = {
            "ct_id": ct_id,
            "ctuid": props.get("CTUID", ct_id),
            "dguid": props.get("DGUID", ""),
            "geo_name": props.get("CTNAME", props.get("geo_name", "")),
            "contains_toronto_da": str(props.get("contains_toronto_da", "")).lower(),
        }
    return output


def load_existing_ct_profile() -> dict[str, dict]:
    return {row["geo_id"]: row for row in read_csv(CT_PROFILE_BASE)}


def load_profile_characteristics(target_dguids: set[str]) -> tuple[dict[str, dict], dict[int, str]]:
    wanted = {str(value): key for key, value in PROFILE_CHARACTERISTICS.items()}
    rows = {dguid: {} for dguid in target_dguids}
    labels: dict[int, str] = {}
    member = csv_member(CT_PROFILE_ZIP)
    with zipfile.ZipFile(CT_PROFILE_ZIP) as archive:
        with archive.open(member) as raw:
            reader = csv.DictReader((line.decode("latin-1") for line in raw))
            for row in reader:
                dguid = row["DGUID"]
                if dguid not in rows:
                    continue
                characteristic_id = row["CHARACTERISTIC_ID"]
                variable = wanted.get(characteristic_id)
                if not variable:
                    continue
                labels[int(characteristic_id)] = " ".join(row["CHARACTERISTIC_NAME"].split())
                rows[dguid][variable] = as_number(row.get("C1_COUNT_TOTAL"))
                rows[dguid][f"{variable}_characteristic_id"] = characteristic_id
                rows[dguid][f"{variable}_characteristic_name"] = labels[int(characteristic_id)]
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
    member = csv_member(CT_AGE_ZIP, "98100024.csv")
    with zipfile.ZipFile(CT_AGE_ZIP) as archive:
        with archive.open(member) as raw:
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
                    age_value = int(age)
                    if 5 <= age_value <= 17:
                        record["school_age_5_17_count"] += count
                    if 18 <= age_value <= 34:
                        record["age_18_34_count"] += count
                    if 35 <= age_value <= 64:
                        record["age_35_64_count"] += count
    return output


def add_derived(row: dict) -> None:
    row["age_18_34_share"] = divide(row.get("age_18_34_count"), row.get("population_age_total"))
    row["age_35_64_share"] = divide(row.get("age_35_64_count"), row.get("population_age_total"))
    row["age_65_plus_share"] = divide(row.get("age_65_plus_count"), row.get("population_age_total"))
    row["bachelors_or_higher_25_64_share"] = divide(
        row.get("bachelors_or_higher_25_64_count"), row.get("education_25_64_total")
    )
    row["low_income_lim_at_share"] = divide(
        row.get("low_income_lim_at_count"), row.get("low_income_status_total")
    )
    row["unemployment_rate_share"] = divide(row.get("unemployment_rate_pct_official"), 100)
    row["renter_share"] = divide(row.get("renter_households_count"), row.get("tenure_total_households"))
    row["owner_share"] = divide(row.get("owner_households_count"), row.get("tenure_total_households"))
    row["same_address_1yr_share"] = divide(row.get("same_address_1yr_count"), row.get("mobility_1yr_total"))
    row["same_address_5yr_share"] = divide(row.get("same_address_5yr_count"), row.get("mobility_5yr_total"))
    row["condo_share"] = divide(row.get("condominium_dwellings_count"), row.get("condo_status_total_dwellings"))
    row["subsidized_housing_tenant_share"] = divide(row.get("subsidized_housing_tenant_pct_official"), 100)
    apartments = sum(
        value or 0
        for value in [
            row.get("apartment_duplex_count"),
            row.get("apartment_lt5_storeys_count"),
            row.get("apartment_5plus_storeys_count"),
        ]
    )
    row["apartment_total_count"] = apartments
    row["apartment_share"] = divide(apartments, row.get("structural_type_total_dwellings"))
    row["detached_share"] = divide(row.get("single_detached_house_count"), row.get("structural_type_total_dwellings"))
    row["semi_detached_share"] = divide(
        row.get("semi_detached_house_count"), row.get("structural_type_total_dwellings")
    )
    row["immigrant_share"] = divide(row.get("immigrants_count"), row.get("immigrant_status_total"))
    row["recent_immigrant_share"] = divide(
        row.get("recent_immigrants_2016_2021_count"), row.get("immigrant_status_total")
    )
    row["non_citizen_share"] = divide(row.get("not_canadian_citizens_count"), row.get("citizenship_total"))
    row["citizen_adult_share"] = divide(row.get("canadian_citizens_18plus_count"), row.get("population_18plus"))
    row["visible_minority_share"] = divide(
        row.get("visible_minority_population_count"), row.get("visible_minority_total")
    )
    knows_official = None
    if row.get("official_language_knowledge_total") is not None and row.get("neither_english_nor_french_count") is not None:
        knows_official = row["official_language_knowledge_total"] - row["neither_english_nor_french_count"]
    row["english_french_knowledge_count"] = knows_official
    row["english_french_knowledge_share"] = divide(knows_official, row.get("official_language_knowledge_total"))
    row["non_official_mother_tongue_share"] = divide(
        row.get("non_official_mother_tongue_count"), row.get("mother_tongue_total")
    )
    row["transit_commute_share"] = divide(row.get("public_transit_commute_count"), row.get("commute_mode_total"))
    row["school_age_5_17_share"] = divide(row.get("school_age_5_17_count"), row.get("population_age_total"))


def interpolation_ct_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted(INTERPOLATION_ROOT.glob("*_ct_estimated_results.csv")):
        for row in read_csv(path):
            ids.add(row["ct_id"])
    return ids


def build_rows() -> tuple[list[dict], dict[int, str]]:
    geometry = load_ct_geometry_properties()
    existing_profile = load_existing_ct_profile()
    target_dguids = {row["dguid"] for row in geometry.values() if row["dguid"]}
    profile_values, labels = load_profile_characteristics(target_dguids)
    age_values = load_age_bands(target_dguids)
    interp_ids = interpolation_ct_ids()

    rows = []
    for ct_id in sorted(geometry):
        geo = geometry[ct_id]
        dguid = geo["dguid"]
        base = existing_profile.get(ct_id, {})
        row = {
            "ct_id": ct_id,
            "ctuid": geo["ctuid"],
            "dguid": dguid,
            "geo_name": geo["geo_name"],
            "census_year": "2021",
            "geographic_level": "CT",
            "contains_toronto_da": geo["contains_toronto_da"],
            "in_interpolation_universe": "true" if ct_id in interp_ids else "false",
            "source_profile_file": str(CT_PROFILE_ZIP.relative_to(REPO_ROOT)),
            "source_age_file": str(CT_AGE_ZIP.relative_to(REPO_ROOT)),
            "collection_date": date.today().isoformat(),
            "source": "Statistics Canada 2021 Census Profile and Table 98-10-0024-01",
        }
        row.update(profile_values.get(dguid, {}))
        row.update(age_values.get(dguid, {}))
        row["population_18plus"] = as_number(base.get("population_18plus"))
        row["population_18plus_status"] = base.get("population_18plus_status", "")
        if row.get("canadian_citizens_18plus_count") is None:
            row["canadian_citizens_18plus_count"] = as_number(base.get("citizen_canadian_18over"))
        row["canadian_citizens_18plus_status"] = base.get("citizen_canadian_18over_status", "")
        add_derived(row)
        rows.append({key: fmt(value) for key, value in row.items()})
    return rows, labels


def dictionary_rows(labels: dict[int, str]) -> list[dict]:
    rows: list[dict] = []
    for field, characteristic_id in PROFILE_CHARACTERISTICS.items():
        block = "identifier"
        if field in {
            "median_age",
            "average_household_size",
            "low_income_status_total",
            "low_income_lim_at_count",
            "low_income_lim_at_prevalence_pct_official",
            "education_25_64_total",
            "bachelors_or_higher_25_64_count",
            "labour_force_total",
            "unemployment_rate_pct_official",
        }:
            block = "Block 1"
        elif field in {
            "population_density_per_km2",
            "land_area_km2",
            "structural_type_total_dwellings",
            "single_detached_house_count",
            "semi_detached_house_count",
            "apartment_duplex_count",
            "apartment_lt5_storeys_count",
            "apartment_5plus_storeys_count",
            "tenure_total_households",
            "owner_households_count",
            "renter_households_count",
            "condo_status_total_dwellings",
            "condominium_dwellings_count",
            "mobility_1yr_total",
            "same_address_1yr_count",
            "moved_1yr_count",
            "mobility_5yr_total",
            "same_address_5yr_count",
            "moved_5yr_count",
        }:
            block = "Block 2"
        elif field in {
            "official_language_knowledge_total",
            "neither_english_nor_french_count",
            "mother_tongue_total",
            "non_official_mother_tongue_count",
            "citizenship_total",
            "canadian_citizens_18plus_count",
            "not_canadian_citizens_count",
            "immigrant_status_total",
            "immigrants_count",
            "recent_immigrants_2016_2021_count",
            "visible_minority_total",
            "visible_minority_population_count",
        }:
            block = "Block 3"
        elif field in {"commute_mode_total", "public_transit_commute_count"}:
            block = "Block 5"
        elif field in {"subsidized_housing_tenant_pct_official"}:
            block = "Block 5"
        rows.append(
            {
                "variable_name": field,
                "block": block,
                "literature_source": LITERATURE if block.startswith("Block") else "",
                "official_census_table": "2021 Census Profile downloadable CT table",
                "characteristic_id": characteristic_id,
                "raw_field_name": labels.get(characteristic_id, ""),
                "final_field_name": field,
                "geographic_level": "CT",
                "denominator": "",
                "processing_formula": "Direct official C1_COUNT_TOTAL value",
                "units": "count/rate as published",
                "missing_value_treatment": "Blank when StatCan value is unavailable or suppressed.",
                "notes": "",
            }
        )
    for item in DERIVED_VARIABLES:
        rows.append(
            {
                "variable_name": item["name"],
                "block": item["block"],
                "literature_source": LITERATURE,
                "official_census_table": (
                    "2021 Census Profile downloadable CT table"
                    if not item["name"].startswith(("age_", "school_age"))
                    else "Statistics Canada Table 98-10-0024-01"
                ),
                "characteristic_id": "",
                "raw_field_name": "",
                "final_field_name": item["name"],
                "geographic_level": "CT",
                "denominator": item["denominator"],
                "processing_formula": item["formula"],
                "units": item["units"],
                "missing_value_treatment": "Blank when numerator or denominator is missing or denominator is zero.",
                "notes": item["notes"],
            }
        )
    return rows


def qa_outputs(rows: list[dict], dictionary: list[dict]) -> tuple[str, list[dict]]:
    ct_ids = [row["ct_id"] for row in rows]
    interpolation_ids = interpolation_ct_ids()
    duplicate_cts = sorted({ct_id for ct_id in ct_ids if ct_ids.count(ct_id) > 1})
    missing_from_master = sorted(interpolation_ids - set(ct_ids))
    extra_not_interpolation = [row["ct_id"] for row in rows if row["in_interpolation_universe"] == "false"]
    share_fields = [row["variable_name"] for row in dictionary if row["units"] == "share"]
    invalid_share_rows = []
    negative_count_rows = []
    missing_rows = []
    for variable in share_fields:
        missing = 0
        invalid = 0
        for row in rows:
            value = as_number(row.get(variable))
            if value is None:
                missing += 1
            elif value < -1e-9 or value > 1 + 1e-9:
                invalid += 1
                invalid_share_rows.append((row["ct_id"], variable, value))
        missing_rows.append(
            {
                "variable_name": variable,
                "missing_count_all_cts": missing,
                "missing_count_interpolation_cts": sum(
                    1 for row in rows if row["in_interpolation_universe"] == "true" and as_number(row.get(variable)) is None
                ),
                "invalid_share_count": invalid,
            }
        )
    count_fields = [field for field in rows[0] if field.endswith("_count") or field.endswith("_total")]
    for row in rows:
        for field in count_fields:
            value = as_number(row.get(field))
            if value is not None and value < 0:
                negative_count_rows.append((row["ct_id"], field, value))
    population_mismatch = []
    population_differences = []
    for row in rows:
        pop_profile = as_number(row.get("population_total"))
        pop_age = as_number(row.get("population_age_total"))
        if pop_profile is not None and pop_age is not None:
            difference = abs(pop_profile - pop_age)
            population_differences.append(difference)
            if difference > 5:
                population_mismatch.append((row["ct_id"], pop_profile, pop_age))
    report = [
        "# CT Census Variables QA Report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "## Coverage",
        "",
        f"- Master CT rows: {len(rows)}",
        f"- Unique `ct_id` values: {len(set(ct_ids))}",
        f"- Duplicate `ct_id` values: {len(duplicate_cts)}",
        f"- Interpolation CT ids found across election outputs: {len(interpolation_ids)}",
        f"- Interpolation CT ids missing from master: {len(missing_from_master)}",
        f"- Master CTs outside interpolation universe: {len(extra_not_interpolation)}",
        "",
        "## Integrity",
        "",
        f"- Share fields checked: {len(share_fields)}",
        f"- Invalid share values outside [0, 1]: {len(invalid_share_rows)}",
        f"- Negative count/total values: {len(negative_count_rows)}",
        f"- Population total mismatches between profile and age cube greater than 5 persons: {len(population_mismatch)}",
        f"- Maximum absolute profile-vs-age population difference: {max(population_differences) if population_differences else 0}",
        "",
        "## Notes",
        "",
        "- The master retains 622 CTs from the existing Toronto CT geometry file.",
        "- `contains_toronto_da=true` and `in_interpolation_universe=true` identify the 585 CTs used by the interpolation pipeline.",
        "- Two interpolation-universe CTs have suppressed or unavailable citizen-adult denominators in the existing Census profile products.",
        "- Small profile-vs-age population differences are expected from published table rounding.",
        "- Citizen-adult share can exceed 1 in rare cases because the numerator is a 25% sample citizenship estimate and the denominator is a 100% age-table count.",
    ]
    if missing_from_master:
        report.extend(["", "Missing interpolation CT ids:", ""] + [f"- {ct_id}" for ct_id in missing_from_master])
    if invalid_share_rows:
        report.extend(["", "Invalid shares:", ""] + [f"- {ct} {var}={val}" for ct, var, val in invalid_share_rows[:50]])
    return "\n".join(report) + "\n", missing_rows


def registry_rows(dictionary: list[dict]) -> list[dict]:
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
    rows = []
    for item in dictionary:
        if not item["block"].startswith("Block"):
            continue
        rows.append(
            {
                "variable_name": item["final_field_name"],
                "block": item["block"],
                "literature_source": item["literature_source"],
                "preferred_data_source": "Statistics Canada 2021 Census",
                "official_dataset": item["official_census_table"],
                "raw_dataset_location": (
                    str(CT_AGE_ZIP.relative_to(REPO_ROOT))
                    if item["official_census_table"] == "Statistics Canada Table 98-10-0024-01"
                    else str(CT_PROFILE_ZIP.relative_to(REPO_ROOT))
                ),
                "processed_dataset_location": str(OUTPUT_MASTER.relative_to(REPO_ROOT)),
                "geographic_level": item["geographic_level"],
                "denominator": item["denominator"],
                "status": "collected",
                "notes": item["notes"],
            }
        )
    return rows, registry_fields


def write_registry(dictionary: list[dict]) -> None:
    rows, fields = registry_rows(dictionary)
    existing = read_csv(REGISTRY_PATH) if REGISTRY_PATH.exists() else []
    census_names = {row["variable_name"] for row in rows}
    preserved = [
        row
        for row in existing
        if not (
            row.get("preferred_data_source") == "Statistics Canada 2021 Census"
            and row.get("variable_name") in census_names
        )
    ]
    write_csv(REGISTRY_PATH, preserved + rows, fields)


def processing_log(rows: list[dict]) -> str:
    return "\n".join(
        [
            "# CT Census Variables Processing Log",
            "",
            f"Generated: {date.today().isoformat()}",
            "",
            "## Source Files",
            "",
            f"- `{CT_PROFILE_ZIP.relative_to(REPO_ROOT)}`",
            f"- `{CT_AGE_ZIP.relative_to(REPO_ROOT)}`",
            f"- `{CT_GEOMETRY.relative_to(REPO_ROOT)}`",
            f"- `{CT_PROFILE_BASE.relative_to(REPO_ROOT)}`",
            "",
            "No new datasets were downloaded. Existing official Statistics Canada source files were reused.",
            "",
            "## Outputs",
            "",
            f"- `{OUTPUT_MASTER.relative_to(REPO_ROOT)}`",
            f"- `{OUTPUT_DICTIONARY.relative_to(REPO_ROOT)}`",
            f"- `{OUTPUT_MISSING.relative_to(REPO_ROOT)}`",
            f"- `{OUTPUT_QA.relative_to(REPO_ROOT)}`",
            "",
            "## Row Counts",
            "",
            f"- Master rows: {len(rows)}",
            f"- Interpolation-universe rows: {sum(1 for row in rows if row['in_interpolation_universe'] == 'true')}",
            "",
            "## Processing Summary",
            "",
            "- Extracted selected official Census Profile characteristics by `DGUID`.",
            "- Summed single-year ages for 5-17, 18-34, and 35-64 age bands.",
            "- Used the official 65+ age aggregate from Table 98-10-0024-01.",
            "- Preserved raw counts and official rates, then added 0-1 derived shares.",
            "- Updated the project-level variable registry for collected Census variables.",
            "",
        ]
    )


def main() -> None:
    rows, labels = build_rows()
    dictionary = dictionary_rows(labels)
    qa_report, missing = qa_outputs(rows, dictionary)

    write_csv(OUTPUT_MASTER, rows)
    write_csv(OUTPUT_DICTIONARY, dictionary)
    write_csv(OUTPUT_MISSING, missing)
    OUTPUT_QA.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_QA.write_text(qa_report, encoding="utf-8")
    OUTPUT_LOG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_LOG.write_text(processing_log(rows), encoding="utf-8")
    write_registry(dictionary)

    print(f"Wrote {len(rows)} CT Census rows to {OUTPUT_MASTER}")
    print(f"Wrote dictionary to {OUTPUT_DICTIONARY}")
    print(f"Wrote QA report to {OUTPUT_QA}")


if __name__ == "__main__":
    main()
