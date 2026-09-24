#!/usr/bin/env python3
"""Build normalized candidate tables and add party totals to poll results.

The poll CSV/GeoJSON files remain the GIS-friendly master tables. This script
adds poll IDs, candidate-valid-vote totals, and wide party-vote columns. It also
writes a compact candidate catalog and a narrow poll-candidate vote bridge for
each election.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout" / "elections"
RAW = DATA_ROOT / "raw"
PROCESSED = DATA_ROOT / "processed"
METADATA_OUT = PROCESSED / "metadata"

FEDERAL_CODES = [
    35007, 35022, 35023, 35024, 35026, 35029, 35030, 35031, 35041, 35092,
    35093, 35094, 35095, 35096, 35097, 35100, 35105, 35109, 35110, 35111,
    35112, 35117, 35120, 35122,
]

PROVINCIAL_CODES = [
    7, 19, 20, 21, 22, 25, 28, 29, 30, 41, 83, 93, 94, 95, 96, 97, 98,
    101, 109, 110, 111, 112, 117, 120, 122,
]


def nint(value):
    if value is None or pd.isna(value) or str(value).strip() == "":
        return 0
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return 0


def clean_text(value):
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def load_turnout_context(stem):
    path = election_output(election_id_for_stem(stem), "turnout") / f"{stem}.csv"
    df = pd.read_csv(
        path,
        dtype={"electoral_district_number": str, "polling_division_number": str},
    )
    context = {}
    for _, row in df.iterrows():
        district = clean_text(row["electoral_district_number"]).zfill(2)
        if stem.startswith("toronto_provincial"):
            district = district.zfill(3)
        if stem.startswith("toronto_federal"):
            district = clean_text(row["electoral_district_number"])
        poll = clean_text(row["polling_division_number"])
        key = (district, poll)
        context[key] = {
            "polling_division_name": clean_text(row.get("polling_division_name")) or None,
            "vote_type": clean_text(row.get("vote_type")) or None,
            "poll_total_votes": nint(row.get("number_of_votes")) if clean_text(row.get("number_of_votes")) else None,
            "poll_total_electors": nint(row.get("number_of_electors")) if clean_text(row.get("number_of_electors")) else None,
            "vote_in_other_division": clean_text(row.get("vote_in_other_division")) or None,
        }
    return context


def slug(value):
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def poll_id(election_id, district, poll, vote_type):
    poll_value = clean_text(poll)
    if poll_value.isdigit():
        poll_value = str(int(poll_value))
    return "|".join(
        [
            election_id,
            clean_text(district),
            poll_value,
            clean_text(vote_type),
        ]
    )


def candidate_id(election_id, district, candidate_name):
    identity = "|".join(
        [election_id, clean_text(district), clean_text(candidate_name)]
    )
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:10]
    readable = slug(candidate_name)[:36]
    return f"{election_id}_{readable}_{digest}"


def write_dict_rows(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalized_candidate_tables(election_id, rows, citywide_candidates=False):
    candidates = {}
    vote_rows = []
    for row in rows:
        district = "" if citywide_candidates else row["electoral_district_number"]
        cid = candidate_id(election_id, district, row["candidate_name"])
        pid = poll_id(
            election_id,
            row["electoral_district_number"],
            row["polling_division_number"],
            row["vote_type"],
        )
        candidates[cid] = {
            "candidate_id": cid,
            "electoral_district_number": district or None,
            "candidate_name": row["candidate_name"],
            "party_name": row["party_name"],
            "source_note": row["source_note"],
        }
        if row["candidate_vote_count"] != 0:
            vote_rows.append(
                {
                    "poll_id": pid,
                    "candidate_id": cid,
                    "candidate_vote_count": row["candidate_vote_count"],
                }
            )
    candidate_rows = sorted(
        candidates.values(),
        key=lambda row: (
            clean_text(row["electoral_district_number"]),
            row["candidate_name"],
        ),
    )
    vote_rows.sort(key=lambda row: (row["poll_id"], row["candidate_id"]))
    return candidate_rows, vote_rows


def party_columns(rows):
    parties = sorted({row["party_name"] for row in rows if row["party_name"]})
    return {party: f"party_{slug(party)}_votes" for party in parties}


def poll_candidate_aggregates(election_id, rows):
    columns = party_columns(rows)
    aggregates = {}
    for row in rows:
        pid = poll_id(
            election_id,
            row["electoral_district_number"],
            row["polling_division_number"],
            row["vote_type"],
        )
        if pid not in aggregates:
            aggregates[pid] = {
                "poll_total_candidate_votes": 0,
                **{column: 0 for column in columns.values()},
            }
        aggregates[pid]["poll_total_candidate_votes"] += row["candidate_vote_count"]
        aggregates[pid][columns[row["party_name"]]] += row["candidate_vote_count"]
    return columns, aggregates


def enrich_poll_outputs(election_id, stem, candidate_rows):
    turnout = election_output(election_id, "turnout")
    csv_path = turnout / f"{stem}.csv"
    geojson_path = turnout / f"{stem}.geojson"
    columns, aggregates = poll_candidate_aggregates(election_id, candidate_rows)
    party_fields = list(columns.values())

    poll_df = pd.read_csv(
        csv_path,
        dtype={
            "electoral_district_number": str,
            "polling_division_number": str,
            "vote_type": str,
        },
    )
    poll_df["poll_id"] = poll_df.apply(
        lambda row: poll_id(
            election_id,
            row["electoral_district_number"],
            row["polling_division_number"],
            row["vote_type"],
        ),
        axis=1,
    )
    poll_df["poll_total_candidate_votes"] = poll_df["poll_id"].map(
        lambda pid: aggregates.get(pid, {}).get("poll_total_candidate_votes")
    )
    for field in party_fields:
        poll_df[field] = poll_df["poll_id"].map(
            lambda pid, field=field: aggregates.get(pid, {}).get(field)
        )
    ordered_fields = [
        "poll_id",
        "electoral_district_number",
        "polling_division_number",
        "polling_division_name",
        "vote_type",
        "number_of_votes",
        "poll_total_candidate_votes",
        "number_of_electors",
        "proportion_of_turnout",
        *party_fields,
        "vote_in_other_division",
        "source_note",
    ]
    extra_fields = [
        field
        for field in poll_df.columns
        if field not in ordered_fields and field != "geometry"
    ]
    poll_df = poll_df[
        [field for field in ordered_fields if field in poll_df.columns]
        + extra_fields
        + (["geometry"] if "geometry" in poll_df.columns else [])
    ]
    poll_df.to_csv(csv_path, index=False)

    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)
    for feature in geojson["features"]:
        properties = feature["properties"]
        pid = poll_id(
            election_id,
            properties.get("electoral_district_number"),
            properties.get("polling_division_number"),
            properties.get("vote_type"),
        )
        aggregate = aggregates.get(pid)
        properties["poll_id"] = pid
        properties["poll_total_candidate_votes"] = (
            aggregate["poll_total_candidate_votes"] if aggregate else None
        )
        for field in party_fields:
            properties[field] = aggregate[field] if aggregate else None
        property_order = [
            "poll_id",
            "electoral_district_number",
            "polling_division_number",
            "polling_division_name",
            "vote_type",
            "number_of_votes",
            "poll_total_candidate_votes",
            "number_of_electors",
            "proportion_of_turnout",
            *party_fields,
            "vote_in_other_division",
            "source_note",
        ]
        extra_properties = [
            field for field in properties if field not in property_order
        ]
        feature["properties"] = {
            field: properties[field]
            for field in property_order + extra_properties
            if field in properties
        }
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    return {
        "party_columns": columns,
        "poll_rows": len(poll_df),
        "polls_with_candidate_results": len(aggregates),
    }


def municipal_rows():
    context = load_turnout_context("toronto_municipal_2023_mayor_turnout_subdivisions")
    xls = pd.ExcelFile(RAW / "toronto_2023_mayor.xlsx")
    rows = []
    for sheet in xls.sheet_names:
        if not sheet.startswith("Ward "):
            continue
        ward = str(int(sheet.split()[1])).zfill(2)
        df = pd.read_excel(xls, sheet_name=sheet, header=None)
        subdivisions = []
        for value in df.iloc[1, 1:].tolist():
            if pd.isna(value) or str(value).strip() == "Total":
                continue
            subdivisions.append(str(nint(value)))
        total_row = next(
            (
                idx for idx, value in df.iloc[:, 0].items()
                if str(value).strip().startswith(f"City Ward {int(ward)} Totals")
            ),
            len(df),
        )
        for col_offset, poll in enumerate(subdivisions, start=1):
            poll_rows = []
            for row_idx in range(3, total_row):
                candidate = clean_text(df.iloc[row_idx, 0])
                if not candidate:
                    continue
                votes = nint(df.iloc[row_idx, col_offset])
                poll_rows.append((candidate, votes))
            poll_total_candidate_votes = sum(v for _, v in poll_rows)
            ctx = context.get((ward, poll), {})
            for candidate, votes in poll_rows:
                rows.append({
                    "electoral_district_number": ward,
                    "polling_division_number": poll,
                    "polling_division_name": ctx.get("polling_division_name"),
                    "vote_type": ctx.get("vote_type") or ("election_day" if poll not in {"96", "97", "98", "99"} else None),
                    "candidate_name": candidate,
                    "party_name": "Non-partisan",
                    "candidate_vote_count": votes,
                    "poll_total_candidate_votes": poll_total_candidate_votes,
                    "poll_total_votes": ctx.get("poll_total_votes"),
                    "poll_total_electors": ctx.get("poll_total_electors"),
                    "vote_in_other_division": ctx.get("vote_in_other_division"),
                    "source_note": "Municipal mayoral race is non-partisan; candidate share is available, not party share.",
                })
    return rows


def provincial_rows():
    context = load_turnout_context("toronto_provincial_2025_turnout_poll_divisions")
    wanted = {str(code).zfill(3) for code in PROVINCIAL_CODES}
    df = pd.read_csv(RAW / "eo_2025_official_return.csv", dtype=str)
    df = df[df["EventNameEnglish"].str.contains("2025 Provincial General Election", na=False)]
    df["district_number"] = df["ElectoralDistrictNameEnglish"].str.extract(r"^(\d{3})")
    df = df[df["district_number"].isin(wanted)].copy()
    df["base_poll"] = df["PollNumber"].str.extract(r"^(\d+)", expand=False)
    df["output_poll"] = df["base_poll"].where(df["base_poll"].notna(), df["PollNumber"])
    df["output_poll"] = df["output_poll"].map(lambda value: str(value).zfill(3) if str(value).isdigit() else str(value))
    df["candidate_votes"] = df["AcceptedBallotCount"].map(nint)

    candidate_summary = pd.read_csv(
        RAW / "source_downloads" / "eo_2025_candidate_summary.csv",
        dtype=str,
        encoding="utf-8-sig",
    )
    candidate_summary = candidate_summary[
        candidate_summary["EventNameEnglish"].eq("2025 Provincial General Election")
    ].copy()
    candidate_summary["district_number"] = candidate_summary["ElectoralDistrictNumber"].str.zfill(3)
    candidate_summary = candidate_summary[candidate_summary["district_number"].isin(wanted)]
    candidate_summary["candidate_total_votes"] = candidate_summary["TotalValidBallotsCast"].map(nint)

    party_codes = pd.read_csv(
        RAW / "source_downloads" / "eo_2025_political_interest_codes.csv",
        dtype=str,
        encoding="utf-8-sig",
    )
    party_codes = party_codes[
        party_codes["EventNameEnglish"].eq("2025 Provincial General Election")
    ][["PoliticalInterestCode", "PartyFullNameEnglish"]].drop_duplicates()

    party_lookup = (
        candidate_summary.merge(party_codes, on="PoliticalInterestCode", how="left")
        .set_index(["district_number", "candidate_total_votes"])["PartyFullNameEnglish"]
        .to_dict()
    )

    rows = []
    grouped = df.groupby(["district_number", "output_poll", "NameOfCandidates"], dropna=False)
    totals = (
        df.groupby(["district_number", "output_poll"])["candidate_votes"]
        .sum()
        .to_dict()
    )
    candidate_totals = (
        df.groupby(["district_number", "NameOfCandidates"])["candidate_votes"]
        .sum()
        .to_dict()
    )
    for (district, poll, candidate), g in grouped:
        candidate = clean_text(candidate)
        if not candidate:
            continue
        votes = sum(nint(v) for v in g["AcceptedBallotCount"])
        candidate_total_votes = candidate_totals[(district, candidate)]
        party_name = party_lookup.get((district, candidate_total_votes))
        if not party_name:
            raise ValueError(
                f"No official party match for provincial candidate {candidate!r} "
                f"in district {district} with {candidate_total_votes} votes"
            )
        poll_for_context = str(int(poll)) if str(poll).isdigit() else str(poll)
        ctx = context.get((district, poll_for_context), context.get((district, str(poll)), {}))
        rows.append({
            "electoral_district_number": district,
            "polling_division_number": poll_for_context,
            "polling_division_name": ctx.get("polling_division_name") or clean_text(g["VotingPlaceAddressOrLocation"].dropna().iloc[0]) if len(g["VotingPlaceAddressOrLocation"].dropna()) else None,
            "vote_type": ctx.get("vote_type") or ("advance" if str(poll).startswith("ADV") else "election_day"),
            "candidate_name": candidate,
            "party_name": party_name,
            "candidate_vote_count": votes,
            "poll_total_candidate_votes": totals.get((district, poll), 0),
            "poll_total_votes": ctx.get("poll_total_votes"),
            "poll_total_electors": ctx.get("poll_total_electors"),
            "vote_in_other_division": ctx.get("vote_in_other_division"),
            "source_note": (
                "Party name joined from Elections Ontario's official Summary of Valid Votes "
                "Cast for Each Candidate and Political Interest Codes reports."
            ),
        })
    return rows


def canonical_federal_poll(value):
    text = clean_text(value)
    special_match = re.match(r"^S/R\s*(\d+)$", text, re.IGNORECASE)
    if special_match:
        return f"SVR-{special_match.group(1)}"
    letter_match = re.match(r"^(\d+)[A-Za-z]$", text)
    if letter_match:
        return letter_match.group(1)
    return text


def federal_vote_type(poll, poll_name=None):
    poll_text = str(poll or "").strip()
    name = str(poll_name or "").lower()
    if poll_text.startswith("SVR") or poll_text.startswith("S/R"):
        return "special"
    if poll_text.isdigit() and int(poll_text) >= 600:
        return "advance"
    if "group" in name or "groupe" in name:
        return "special"
    return "election_day"


def federal_rows():
    context = load_turnout_context("toronto_federal_2025_turnout_poll_divisions")
    frames = []
    for code in FEDERAL_CODES:
        path = RAW / "source_downloads" / "federal_csv_format2" / f"{code}.csv"
        frames.append(pd.read_csv(path, encoding="utf-8-sig", dtype=str))
    df = pd.concat(frames, ignore_index=True)

    district_col = "Electoral District Number/Numéro de circonscription"
    poll_col = "Polling Division Number/Numéro de section de vote"
    poll_name_col = "Polling Division Name/Nom de section de vote"
    combined_col = "Combined with No./Résultats combinés à ceux du n°"
    family_col = "Candidate’s Family Name/Nom de famille du candidat"
    middle_col = "Candidate’s Middle Name/Second prénom du candidat"
    first_col = "Candidate’s First Name/Prénom du candidat"
    party_col = "Political Affiliation Name_English/Appartenance politique_Anglais"
    vote_col = "Candidate Vote Count/Votes du candidat"

    df["output_poll"] = df[poll_col].map(canonical_federal_poll)
    df = df[df[combined_col].fillna("").str.strip().eq("")].copy()

    def candidate_name(row):
        parts = [clean_text(row[first_col]), clean_text(row[middle_col]), clean_text(row[family_col])]
        return " ".join(part for part in parts if part)

    df["candidate_name"] = df.apply(candidate_name, axis=1)
    df["candidate_votes"] = df[vote_col].map(nint)
    totals = df.groupby([district_col, "output_poll"])["candidate_votes"].sum().to_dict()

    rows = []
    for (district, poll, candidate, party), g in df.groupby([district_col, "output_poll", "candidate_name", party_col], dropna=False):
        district = clean_text(district)
        poll = clean_text(poll)
        if not candidate:
            continue
        ctx = context.get((district, poll), {})
        poll_name = clean_text(g[poll_name_col].dropna().iloc[0]) if len(g[poll_name_col].dropna()) else None
        rows.append({
            "electoral_district_number": district,
            "polling_division_number": poll,
            "polling_division_name": ctx.get("polling_division_name") or poll_name,
            "vote_type": ctx.get("vote_type") or federal_vote_type(poll, poll_name),
            "candidate_name": candidate,
            "party_name": clean_text(party) or None,
            "candidate_vote_count": int(g["candidate_votes"].sum()),
            "poll_total_candidate_votes": totals.get((district, poll), 0),
            "poll_total_votes": ctx.get("poll_total_votes"),
            "poll_total_electors": ctx.get("poll_total_electors"),
            "vote_in_other_division": ctx.get("vote_in_other_division"),
            "source_note": None,
        })
    return rows


def main():
    METADATA_OUT.mkdir(parents=True, exist_ok=True)
    configs = [
        {
            "election_id": "municipal_2023_mayor",
            "stem": "toronto_municipal_2023_mayor_turnout_subdivisions",
            "candidate_file": "toronto_municipal_2023_mayor_candidates.csv",
            "vote_file": "toronto_municipal_2023_mayor_poll_candidate_votes.csv",
            "rows": municipal_rows(),
            "citywide_candidates": True,
        },
        {
            "election_id": "provincial_2025",
            "stem": "toronto_provincial_2025_turnout_poll_divisions",
            "candidate_file": "toronto_provincial_2025_candidates.csv",
            "vote_file": "toronto_provincial_2025_poll_candidate_votes.csv",
            "rows": provincial_rows(),
            "citywide_candidates": False,
        },
        {
            "election_id": "federal_2025",
            "stem": "toronto_federal_2025_turnout_poll_divisions",
            "candidate_file": "toronto_federal_2025_candidates.csv",
            "vote_file": "toronto_federal_2025_poll_candidate_votes.csv",
            "rows": federal_rows(),
            "citywide_candidates": False,
        },
    ]

    metadata = {}
    for config in configs:
        candidate_output = election_output(
            config["election_id"], "candidate_details"
        )
        candidate_rows, vote_rows = normalized_candidate_tables(
            config["election_id"],
            config["rows"],
            citywide_candidates=config["citywide_candidates"],
        )
        write_dict_rows(
            candidate_output / config["candidate_file"],
            candidate_rows,
            [
                "candidate_id",
                "electoral_district_number",
                "candidate_name",
                "party_name",
                "source_note",
            ],
        )
        write_dict_rows(
            candidate_output / config["vote_file"],
            vote_rows,
            ["poll_id", "candidate_id", "candidate_vote_count"],
        )
        poll_metadata = enrich_poll_outputs(
            config["election_id"],
            config["stem"],
            config["rows"],
        )
        metadata[config["election_id"]] = {
            **poll_metadata,
            "candidate_rows": len(candidate_rows),
            "source_poll_candidate_rows": len(config["rows"]),
            "poll_candidate_vote_rows": len(vote_rows),
            "omitted_zero_vote_rows": len(config["rows"]) - len(vote_rows),
            "zero_vote_storage_rule": (
                "The bridge stores only nonzero candidate votes. For polls with "
                "a non-null poll_total_candidate_votes value, an applicable "
                "candidate absent from the bridge has zero votes."
            ),
            "candidate_file": config["candidate_file"],
            "poll_candidate_vote_file": config["vote_file"],
            "poll_summary_csv": f"{config['stem']}.csv",
            "poll_summary_geojson": f"{config['stem']}.geojson",
        }
        print(
            f"{config['election_id']}: {len(candidate_rows):,} candidates, "
            f"{len(vote_rows):,} poll-candidate vote rows"
        )

    obsolete = (
        election_output("federal_2025", "candidate_details")
        / "toronto_federal_2025_poll_candidate_party_votes.csv"
    )
    if obsolete.exists():
        obsolete.unlink()

    with open(
        METADATA_OUT / "normalized_election_results_metadata.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
def election_output(election_id, product):
    return PROCESSED / election_id / product


def election_id_for_stem(stem):
    if stem.startswith("toronto_municipal"):
        return "municipal_2023_mayor"
    if stem.startswith("toronto_provincial"):
        return "provincial_2025"
    if stem.startswith("toronto_federal"):
        return "federal_2025"
    raise ValueError(f"Unknown election output stem: {stem}")
