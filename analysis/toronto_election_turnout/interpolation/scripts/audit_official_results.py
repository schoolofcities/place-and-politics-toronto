#!/usr/bin/env python3
"""Reconcile normalized and interpolated votes with official result files."""

from __future__ import annotations

import json
import warnings
from collections import defaultdict
from pathlib import Path

import pandas as pd

from config import CONTEXT_AUDIT_ROOT, REPO_ROOT, VALIDATION_ROOT
from io_utils import read_csv, write_csv, write_json


ELECTION_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "elections"
RAW = ELECTION_ROOT / "raw"
PROCESSED = ELECTION_ROOT / "processed"
METADATA = PROCESSED / "metadata" / "normalized_election_results_metadata.json"

ELECTION_FILES = {
    "municipal_2023_mayor": {
        "turnout": "toronto_municipal_2023_mayor_turnout_subdivisions.csv",
        "candidates": "toronto_municipal_2023_mayor_candidates.csv",
        "bridge": "toronto_municipal_2023_mayor_poll_candidate_votes.csv",
    },
    "provincial_2025": {
        "turnout": "toronto_provincial_2025_turnout_poll_divisions.csv",
        "candidates": "toronto_provincial_2025_candidates.csv",
        "bridge": "toronto_provincial_2025_poll_candidate_votes.csv",
    },
    "federal_2025": {
        "turnout": "toronto_federal_2025_turnout_poll_divisions.csv",
        "candidates": "toronto_federal_2025_candidates.csv",
        "bridge": "toronto_federal_2025_poll_candidate_votes.csv",
    },
}

PROVINCIAL_CODES = {
    "007", "019", "020", "021", "022", "025", "028", "029", "030", "041",
    "083", "093", "094", "095", "096", "097", "098", "101", "109", "110",
    "111", "112", "117", "120", "122",
}
FEDERAL_CODES = {
    "35007", "35022", "35023", "35024", "35026", "35029", "35030", "35031",
    "35041", "35092", "35093", "35094", "35095", "35096", "35097", "35100",
    "35105", "35109", "35110", "35111", "35112", "35117", "35120", "35122",
}
TOLERANCE = 1e-6

TURNOUT_REFERENCES = {
    "municipal_2023_mayor": [
        {
            "reference_name": "City of Toronto final report",
            "reference_scope": "Toronto",
            "reference_rate": 0.37,
            "reference_status": "official_rounded",
            "source_url": (
                "https://www.toronto.ca/wp-content/uploads/2023/12/"
                "8bb4-Final-for-web-2023-Mayor-ByElection-Report.pdf"
            ),
        },
        {
            "reference_name": "Wikipedia reported turnout",
            "reference_scope": "Toronto",
            "reference_rate": 0.385,
            "reference_status": "secondary_source",
            "source_url": (
                "https://en.wikipedia.org/wiki/"
                "2023_Toronto_mayoral_by-election"
            ),
        },
    ],
    "provincial_2025": [
        {
            "reference_name": "Elections Ontario provincial total",
            "reference_scope": "Ontario",
            "reference_rate": 0.4522,
            "reference_status": "official_broader_geography",
            "source_url": (
                "https://results.elections.on.ca/api/report-groups/48/"
                "report-outputs/1088/pdf/en"
            ),
        },
    ],
    "federal_2025": [
        {
            "reference_name": "Elections Canada selected Toronto ridings",
            "reference_scope": "Selected Toronto ridings",
            "reference_rate": 0.6501,
            "reference_status": "official_matching_geography",
            "source_url": (
                "https://www.elections.ca/res/rep/off/ovrGE45/62/"
                "table11E.html"
            ),
        },
        {
            "reference_name": "Elections Canada Ontario total",
            "reference_scope": "Ontario",
            "reference_rate": 0.691,
            "reference_status": "official_broader_geography",
            "source_url": (
                "https://www.elections.ca/res/rep/off/ovrGE45/62/"
                "table3E.html"
            ),
        },
        {
            "reference_name": "Elections Canada national final total",
            "reference_scope": "Canada",
            "reference_rate": 0.690,
            "reference_status": "official_broader_geography",
            "source_url": (
                "https://www.elections.ca/res/rep/off/ovrGE45/62/"
                "table3E.html"
            ),
        },
        {
            "reference_name": "Elections Canada preliminary national release",
            "reference_scope": "Canada",
            "reference_rate": 0.6946,
            "reference_status": "official_preliminary_broader_geography",
            "source_url": (
                "https://www.elections.ca/content.aspx?section=med&dir=pre&"
                "document=apr2925&lang=e"
            ),
        },
    ],
}


def clean(value):
    return "" if pd.isna(value) else str(value).strip()


def number(value):
    text = clean(value).replace(",", "")
    return float(text) if text else 0.0


def canonical_candidate_name(value):
    name = " ".join(clean(value).upper().split())
    if "," in name:
        family, given = (part.strip() for part in name.split(",", 1))
        name = f"{given} {family}"
    return name


def municipal_official():
    party = defaultdict(float)
    candidate = defaultdict(float)
    workbook = RAW / "toronto_2023_mayor.xlsx"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        excel = pd.ExcelFile(workbook)
        for sheet in excel.sheet_names:
            if not sheet.startswith("Ward "):
                continue
            district = str(int(sheet.split()[1])).zfill(2)
            frame = pd.read_excel(excel, sheet_name=sheet, header=None)
            total_column = frame.columns[-1]
            for _, row in frame.iloc[3:].iterrows():
                name = clean(row.iloc[0])
                if not name or name.startswith("City Ward"):
                    continue
                votes = number(row[total_column])
                candidate[(district, canonical_candidate_name(name))] += votes
                party[(district, "Non-partisan")] += votes
    return party, candidate


def provincial_official():
    summary = pd.read_csv(
        RAW / "source_downloads" / "eo_2025_candidate_summary.csv",
        dtype=str,
        encoding="utf-8-sig",
    )
    summary = summary[
        summary["EventNameEnglish"].eq("2025 Provincial General Election")
    ].copy()
    summary["district"] = summary["ElectoralDistrictNumber"].str.zfill(3)
    summary = summary[summary["district"].isin(PROVINCIAL_CODES)]

    codes = pd.read_csv(
        RAW / "source_downloads" / "eo_2025_political_interest_codes.csv",
        dtype=str,
        encoding="utf-8-sig",
    )
    codes = codes[
        codes["EventNameEnglish"].eq("2025 Provincial General Election")
    ][["PoliticalInterestCode", "PartyFullNameEnglish"]].drop_duplicates()
    summary = summary.merge(codes, on="PoliticalInterestCode", how="left")

    party = defaultdict(float)
    candidate = defaultdict(float)
    for _, row in summary.iterrows():
        district = row["district"]
        votes = number(row["TotalValidBallotsCast"])
        party[(district, clean(row["PartyFullNameEnglish"]))] += votes
        candidate[
            (district, canonical_candidate_name(row["NameOfCandidates"]))
        ] += votes
    return party, candidate


def federal_official():
    party = defaultdict(float)
    candidate = defaultdict(float)
    for district in sorted(FEDERAL_CODES):
        frame = pd.read_csv(
            RAW / "source_downloads" / "federal_csv_format2" / f"{district}.csv",
            dtype=str,
            encoding="utf-8-sig",
        )
        family = "Candidate’s Family Name/Nom de famille du candidat"
        middle = "Candidate’s Middle Name/Second prénom du candidat"
        first = "Candidate’s First Name/Prénom du candidat"
        combined = "Combined with No./Résultats combinés à ceux du n°"
        affiliation = (
            "Political Affiliation Name_English/Appartenance politique_Anglais"
        )
        votes_field = "Candidate Vote Count/Votes du candidat"
        for _, row in frame.iterrows():
            if clean(row[combined]):
                continue
            name = " ".join(
                part for part in (
                    clean(row[first]),
                    clean(row[middle]),
                    clean(row[family]),
                )
                if part
            )
            votes = number(row[votes_field])
            party[(district, clean(row[affiliation]))] += votes
            candidate[(district, canonical_candidate_name(name))] += votes
    return party, candidate


def normalized_party(election_id, party_columns):
    rows = read_csv(
        PROCESSED
        / election_id
        / "turnout"
        / ELECTION_FILES[election_id]["turnout"]
    )
    output = defaultdict(float)
    reverse = {field: party for party, field in party_columns.items()}
    for row in rows:
        district = row["electoral_district_number"]
        for field, party in reverse.items():
            output[(district, party)] += number(row.get(field))
    return output


def normalized_candidate(election_id):
    files = ELECTION_FILES[election_id]
    candidates = PROCESSED / election_id / "candidate_details"
    catalog = {
        row["candidate_id"]: row
        for row in read_csv(candidates / files["candidates"])
    }
    output = defaultdict(float)
    for row in read_csv(candidates / files["bridge"]):
        district = row["poll_id"].split("|", 3)[1]
        candidate_row = catalog[row["candidate_id"]]
        output[
            (district, canonical_candidate_name(candidate_row["candidate_name"]))
        ] += number(row["candidate_vote_count"])
    return output


def interpolated_party(election_id, party_columns):
    field_to_party = {field: party for party, field in party_columns.items()}
    output = {}
    validation = read_csv(
        VALIDATION_ROOT / f"{election_id}_validation.csv"
    )
    for row in validation:
        if row["measure_type"] != "party":
            continue
        field = row["measure_id"].removeprefix("party:")
        party = field_to_party[field]
        district = "" if row["geography_level"] == "global" else row["geography_id"]
        output[(district, party)] = number(row["allocated_total"])
    return output


def comparison_rows(election_id, measure_type, official, normalized, interpolated=None):
    rows = []
    keys = sorted(set(official) | set(normalized))
    for district, measure_name in keys:
        official_value = official.get((district, measure_name), 0.0)
        normalized_value = normalized.get((district, measure_name), 0.0)
        allocated_value = (
            interpolated.get((district, measure_name))
            if interpolated is not None
            else None
        )
        official_difference = normalized_value - official_value
        allocation_difference = (
            allocated_value - normalized_value
            if allocated_value is not None
            else None
        )
        rows.append(
            {
                "election_id": election_id,
                "geography_level": "district",
                "geography_id": district,
                "measure_type": measure_type,
                "measure_name": measure_name,
                "official_total": official_value,
                "normalized_total": normalized_value,
                "official_to_normalized_difference": official_difference,
                "official_to_normalized_match": abs(official_difference) <= TOLERANCE,
                "interpolated_total": allocated_value,
                "normalized_to_interpolated_difference": allocation_difference,
                "normalized_to_interpolated_match": (
                    abs(allocation_difference) <= TOLERANCE
                    if allocation_difference is not None
                    else ""
                ),
            }
        )

    names = sorted({name for _, name in keys})
    for measure_name in names:
        official_value = sum(
            value for (district, name), value in official.items()
            if name == measure_name
        )
        normalized_value = sum(
            value for (district, name), value in normalized.items()
            if name == measure_name
        )
        allocated_value = (
            interpolated.get(("", measure_name))
            if interpolated is not None
            else None
        )
        official_difference = normalized_value - official_value
        allocation_difference = (
            allocated_value - normalized_value
            if allocated_value is not None
            else None
        )
        rows.append(
            {
                "election_id": election_id,
                "geography_level": "global",
                "geography_id": "ALL",
                "measure_type": measure_type,
                "measure_name": measure_name,
                "official_total": official_value,
                "normalized_total": normalized_value,
                "official_to_normalized_difference": official_difference,
                "official_to_normalized_match": abs(official_difference) <= TOLERANCE,
                "interpolated_total": allocated_value,
                "normalized_to_interpolated_difference": allocation_difference,
                "normalized_to_interpolated_match": (
                    abs(allocation_difference) <= TOLERANCE
                    if allocation_difference is not None
                    else ""
                ),
            }
        )
    return rows


def turnout_reference_rows():
    rows = []
    for election_id, references in TURNOUT_REFERENCES.items():
        comparison = read_csv(
            CONTEXT_AUDIT_ROOT / f"{election_id}_turnout_comparison.csv"
        )[0]
        citizen_rate = number(
            comparison["interpolated_citizen_18plus_participation_rate"]
        )
        official_row_rate = number(comparison["official_row_turnout_rate"])
        for reference in references:
            matching_scope = (
                reference["reference_scope"]
                in {"Toronto", "Selected Toronto ridings"}
                and reference["reference_status"].startswith("official")
            )
            difference = abs(citizen_rate - reference["reference_rate"])
            rows.append(
                {
                    "election_id": election_id,
                    **reference,
                    "official_row_turnout_rate": official_row_rate,
                    "citizen_18plus_participation_rate": citizen_rate,
                    "citizen_rate_absolute_difference": difference,
                    "citizen_rate_difference_percentage_points": difference * 100,
                    "comparison_category": (
                        "direct_validation"
                        if matching_scope
                        else "contextual_close_margin"
                    ),
                    "within_2_5_percentage_point_context_margin": (
                        difference <= 0.025
                    ),
                    "geography_suitable_for_direct_validation": matching_scope,
                    "interpretation": (
                        "Direct comparison is appropriate only when election, "
                        "geography, numerator, and denominator definitions match."
                    ),
                }
            )
    return rows


def main():
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    loaders = {
        "municipal_2023_mayor": municipal_official,
        "provincial_2025": provincial_official,
        "federal_2025": federal_official,
    }
    party_rows = []
    candidate_rows = []
    for election_id, loader in loaders.items():
        official_party, official_candidate = loader()
        party_columns = metadata[election_id]["party_columns"]
        party_rows.extend(
            comparison_rows(
                election_id,
                "party",
                official_party,
                normalized_party(election_id, party_columns),
                interpolated_party(election_id, party_columns),
            )
        )
        candidate_rows.extend(
            comparison_rows(
                election_id,
                "candidate",
                official_candidate,
                normalized_candidate(election_id),
            )
        )

    write_csv(
        VALIDATION_ROOT / "official_party_vote_reconciliation.csv",
        party_rows,
    )
    write_csv(
        VALIDATION_ROOT / "official_candidate_vote_reconciliation.csv",
        candidate_rows,
    )
    write_csv(
        CONTEXT_AUDIT_ROOT / "turnout_reference_audit.csv",
        turnout_reference_rows(),
    )
    failures = [
        row
        for row in party_rows + candidate_rows
        if not row["official_to_normalized_match"]
        or row["normalized_to_interpolated_match"] is False
    ]
    write_json(
        VALIDATION_ROOT / "official_result_reconciliation_summary.json",
        {
            "official_source_match": not failures,
            "failure_count": len(failures),
            "party_comparison_rows": len(party_rows),
            "candidate_comparison_rows": len(candidate_rows),
            "comparison_granularity": ["global", "district"],
            "municipal_party_note": (
                "The mayoral election is non-partisan; candidate totals are the "
                "finest meaningful official result measure."
            ),
            "turnout_numerator_note": (
                "Party and candidate totals are valid votes. Total ballots cast "
                "can be larger because it includes rejected, unmarked, or "
                "declined ballots."
            ),
        },
    )


if __name__ == "__main__":
    main()
