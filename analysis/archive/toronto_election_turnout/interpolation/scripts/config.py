"""Paths and election-specific configuration for interpolation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
ANALYSIS_ROOT = REPO_ROOT / "analysis" / "toronto_election_turnout"
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"

CENSUS_ROOT = DATA_ROOT / "census" / "processed"
ELECTION_ROOT = DATA_ROOT / "elections" / "processed"
OUTPUT_ROOT = DATA_ROOT / "interpolation" / "processed"
INTERMEDIATE_ROOT = OUTPUT_ROOT / "intermediate"
INPUT_AUDIT_ROOT = INTERMEDIATE_ROOT / "01_input_audit"
CROSSWALK_ROOT = INTERMEDIATE_ROOT / "02_spatial_crosswalks"
ALLOCATION_AUDIT_ROOT = INTERMEDIATE_ROOT / "03_allocation_audit"
VALIDATION_ROOT = INTERMEDIATE_ROOT / "04_validation"
CONTEXT_AUDIT_ROOT = INTERMEDIATE_ROOT / "05_context_audit"

CT_PATH = CENSUS_ROOT / "ct" / "statcan_2021_toronto_ct.geojson"
DA_PATH = CENSUS_ROOT / "da" / "statcan_2021_toronto_da.geojson"
ANCILLARY_WEIGHT_FIELD = "citizen_canadian_18over"
WORKING_EPSG = 3347


@dataclass(frozen=True)
class ElectionConfig:
    election_id: str
    poll_csv: Path
    candidate_csv: Path
    candidate_votes_csv: Path
    district_geojson: Path
    district_id_field: str
    district_id_width: int
    published_turnout_rate: float
    published_turnout_source_note: str

    def normalize_district_id(self, value: object) -> str:
        text = "" if value is None else str(value).strip()
        if not text:
            return ""
        try:
            text = str(int(float(text)))
        except ValueError:
            pass
        return text.zfill(self.district_id_width)


ELECTIONS = (
    ElectionConfig(
        election_id="municipal_2023_mayor",
        poll_csv=ELECTION_ROOT
        / "municipal_2023_mayor"
        / "turnout"
        / "toronto_municipal_2023_mayor_turnout_subdivisions.csv",
        candidate_csv=ELECTION_ROOT
        / "municipal_2023_mayor"
        / "candidate_details"
        / "toronto_municipal_2023_mayor_candidates.csv",
        candidate_votes_csv=ELECTION_ROOT
        / "municipal_2023_mayor"
        / "candidate_details"
        / "toronto_municipal_2023_mayor_poll_candidate_votes.csv",
        district_geojson=REPO_ROOT / "src" / "data" / "wards.geo.json",
        district_id_field="num",
        district_id_width=2,
        published_turnout_rate=0.37,
        published_turnout_source_note=(
            "Toronto supplementary report describes final turnout as 37%."
        ),
    ),
    ElectionConfig(
        election_id="provincial_2025",
        poll_csv=ELECTION_ROOT
        / "provincial_2025"
        / "turnout"
        / "toronto_provincial_2025_turnout_poll_divisions.csv",
        candidate_csv=ELECTION_ROOT
        / "provincial_2025"
        / "candidate_details"
        / "toronto_provincial_2025_candidates.csv",
        candidate_votes_csv=ELECTION_ROOT
        / "provincial_2025"
        / "candidate_details"
        / "toronto_provincial_2025_poll_candidate_votes.csv",
        district_geojson=DATA_ROOT
        / "elections"
        / "raw"
        / "ont_2025_ridings.geojson",
        district_id_field="RIDINGNO",
        district_id_width=3,
        published_turnout_rate=0.4260,
        published_turnout_source_note=(
            "Elections Ontario official-return rows for selected Toronto ridings."
        ),
    ),
    ElectionConfig(
        election_id="federal_2025",
        poll_csv=ELECTION_ROOT
        / "federal_2025"
        / "turnout"
        / "toronto_federal_2025_turnout_poll_divisions.csv",
        candidate_csv=ELECTION_ROOT
        / "federal_2025"
        / "candidate_details"
        / "toronto_federal_2025_candidates.csv",
        candidate_votes_csv=ELECTION_ROOT
        / "federal_2025"
        / "candidate_details"
        / "toronto_federal_2025_poll_candidate_votes.csv",
        district_geojson=DATA_ROOT
        / "elections"
        / "raw"
        / "fed_2025_ridings.geojson",
        district_id_field="FED_NUM",
        district_id_width=5,
        published_turnout_rate=0.6501,
        published_turnout_source_note=(
            "Elections Canada Format 2 rows for selected Toronto ridings."
        ),
    ),
)
