import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd


ANALYSIS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "data" / "toronto_election_turnout"
OUT = DATA_ROOT / "processed"
RAW = DATA_ROOT / "raw"
SOURCE_DOWNLOADS = RAW / "source_downloads"

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
    if value is None or value == "" or (isinstance(value, float) and math.isnan(value)):
        return 0
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return 0


def maybe_int(value):
    if value is None or value == "" or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return None


def proportion(votes, electors):
    return None if votes is None or not electors else votes / electors


def turnout_ratio(votes, electors):
    value = proportion(votes, electors)
    return None if value is not None and value > 1 else value


def over_one_note(votes, electors):
    value = proportion(votes, electors)
    if value is not None and value > 1:
        return (
            "Official votes exceed official electors for this row; turnout ratio left null "
            "because the source denominator is not coherent for division-level turnout."
        )
    return None


def load_geojson(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_geojson(path, features):
    OUT.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)


def write_csv(path, features):
    OUT.mkdir(exist_ok=True)
    fieldnames = [
        "electoral_district_number",
        "polling_division_number",
        "polling_division_name",
        "vote_type",
        "number_of_votes",
        "number_of_electors",
        "proportion_of_turnout",
        "vote_in_other_division",
        "source_note",
        "geometry",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for feat in features:
            row = dict(feat["properties"])
            row["geometry"] = json.dumps(feat["geometry"], ensure_ascii=False) if feat["geometry"] else ""
            writer.writerow(row)


def optimized_features(features):
    optimized = []
    for feat in features:
        props = dict(feat["properties"])
        props.pop("electoral_district_name", None)
        optimized.append(feature(props, feat["geometry"]))
    return optimized


def district_rows(features):
    rows = {}
    for feat in features:
        props = feat["properties"]
        number = props.get("electoral_district_number")
        name = props.get("electoral_district_name")
        if number and name and number not in rows:
            rows[number] = {
                "electoral_district_number": number,
                "electoral_district_name": name,
            }
    return [rows[k] for k in sorted(rows, key=lambda value: (len(str(value)), str(value)))]


def write_district_lookup(path, rows):
    OUT.mkdir(exist_ok=True)
    if path.suffix == ".json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False)
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["electoral_district_number", "electoral_district_name"],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_dataset(stem, features):
    rows = district_rows(features)
    lean_features = optimized_features(features)
    write_geojson(OUT / f"{stem}.geojson", lean_features)
    write_csv(OUT / f"{stem}.csv", lean_features)
    write_district_lookup(OUT / f"{stem}_districts.csv", rows)
    write_district_lookup(OUT / f"{stem}_districts.json", rows)


def feature(properties, geometry):
    return {"type": "Feature", "properties": properties, "geometry": geometry}


def cleaned_federal_poll_name(value):
    if value is None or pd.isna(value):
        return None
    name = str(value).strip()
    return name or None


def cleaned_municipal_ward_name(value):
    name = str(value).replace("City Ward ", "").strip()
    return re.sub(r"^\d+\s+", "", name)


def unique_join(values):
    cleaned = []
    seen = set()
    for value in values:
        if value is None or pd.isna(value):
            continue
        text = str(value).strip()
        if not text or text in seen:
            continue
        cleaned.append(text)
        seen.add(text)
    return "; ".join(cleaned) if cleaned else None


def combine_notes(*notes):
    cleaned = [note for note in notes if note]
    return " ".join(cleaned) if cleaned else None


def municipal_special_poll_name(poll):
    return {
        "096": "Long-term care combined reporting bucket",
        "097": "Mail-in voting reporting bucket",
        "098": "Advance vote reporting bucket",
        "099": "Advance vote reporting bucket",
    }.get(str(poll).zfill(3))


def municipal_vote_type(poll):
    poll = str(poll).zfill(3)
    if poll == "097":
        return "mail_in"
    if poll in {"098", "099"}:
        return "advance"
    if poll == "096":
        return "special"
    return "election_day"


def provincial_vote_type(value):
    return "advance" if str(value or "").strip().lower() == "advance" else "election_day"


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


def municipal_regular_note(votes, electors, code, in_workbook):
    details = []
    if not in_workbook:
        if electors is None:
            details.append(
                "Official subdivision geometry exists, but the official mayoral result workbook has no vote count "
                "and the official voter-statistics workbook has no elector count."
            )
        else:
            details.append(
                f"Official voter-statistics workbook reports {electors} electors, but the official mayoral result workbook has no vote count."
            )
    if in_workbook and electors is None:
        details.append(
            f"The official mayoral result workbook reports {votes} votes, but the official voter-statistics workbook has no elector count."
        )
    if votes is not None and electors is not None and votes > electors:
        details.append(
            f"The official mayoral result workbook reports {votes} votes, while the official voter-statistics workbook "
            f"reports {electors} electors. The original counts are retained, but turnout is left blank because the "
            "denominator is not coherent for division-level turnout."
        )
    if details:
        details.append(
            "No explicit source join to or from another ordinary subdivision was found."
        )
    return " ".join(details) if details else None


def municipal_special_note(code, votes):
    ward = str(int(code[:2]))
    poll = code[2:]
    if poll == "096":
        origin = "long-term care institutions"
    elif poll == "097":
        origin = "mail-in voting"
    else:
        origin = "advance voting"
    return (
        f"Subdivision {int(poll)} in ward {ward} is a special ward-level reporting bucket for {origin}, "
        f"not an ordinary mapped voting subdivision. The official mayoral result workbook reports {votes} votes in this bucket. "
        "The subdivision geometry source has no polygon for this bucket. "
        f"Join in: {votes} votes from {origin}. "
        "Join out: none indicated. Contributing ordinary subdivision numbers are not identified in the source."
    )


def federal_geometry_index():
    index = {}
    attrs = {}
    for code in FEDERAL_CODES:
        data = load_geojson(SOURCE_DOWNLOADS / "federal_polygons" / f"{code}.geojson")
        for feat in data["features"]:
            props = feat["properties"]
            poll = str(props.get("EMRP_NAME") or props.get("PD_NUM") or "").strip()
            if poll:
                index[(str(code), poll)] = feat["geometry"]
                attrs[(str(code), poll)] = props
    return index, attrs


def build_federal():
    geom, geom_attrs = federal_geometry_index()
    features = []
    format2_dir = SOURCE_DOWNLOADS / "federal_csv_format2"
    summary = {
        "combined_rows": 0,
        "official_format2_rows_used": 0,
        "official_rows_with_suffix_aggregated": 0,
        "official_rows_without_geometry": 0,
        "source_polygons_without_official_turnout": 0,
    }
    emitted_source_keys = set()

    def canonical_poll(value):
        if value is None or pd.isna(value):
            return ""
        text = str(value or "").strip()
        special_match = re.match(r"^S/R\s*(\d+)$", text, re.IGNORECASE)
        if special_match:
            return f"SVR-{special_match.group(1)}"
        letter_match = re.match(r"^(\d+)[A-Za-z]$", text)
        if letter_match:
            return letter_match.group(1)
        return text

    def poll_sort_value(value):
        text = str(value)
        if text.startswith("SVR-"):
            return 999998, int(text.split("-", 1)[1]), ""
        m = re.match(r"^(\d+)(?:-(\d+))?$", text)
        if not m:
            return 999999, 0, text
        return int(m.group(1)), int(m.group(2) or 0), text

    for code in FEDERAL_CODES:
        path = format2_dir / f"{code}.csv"
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
        summary["official_format2_rows_used"] += len(df)
        district_name_col = "Electoral District Name_English/Nom de circonscription_Anglais"
        poll_col = "Polling Division Number/Numéro de section de vote"
        poll_name_col = "Polling Division Name/Nom de section de vote"
        combined_col = "Combined with No./Résultats combinés à ceux du n°"
        rejected_col = "Rejected Ballots for poll/Bulletins rejetés du bureau"
        electors_col = "Electors for poll/Électeurs du bureau"
        candidate_vote_col = "Candidate Vote Count/Votes du candidat"
        void_col = "Void Poll Indicator/Indicateur de bureau supprimé"
        no_poll_col = "No Poll Held Indicator/Indicateur de bureau sans scrutin"

        records = {}
        combined_records = []
        elector_additions = defaultdict(int)
        elector_addition_sources = defaultdict(list)
        for raw_poll, group in df.groupby(poll_col, dropna=False, sort=False):
            source_poll = str(raw_poll or "").strip()
            if not source_poll:
                continue
            poll = canonical_poll(source_poll)
            if poll != source_poll:
                summary["official_rows_with_suffix_aggregated"] += 1
            first = group.iloc[0]
            combined_target = canonical_poll(first.get(combined_col))
            if combined_target:
                summary["combined_rows"] += 1
                combined_electors = maybe_int(first[electors_col])
                if combined_electors is not None:
                    elector_additions[combined_target] += combined_electors
                elector_addition_sources[combined_target].append(source_poll)
                combined_records.append((poll, source_poll, combined_target, first))
                continue
            record = records.setdefault(poll, {
                "row": first,
                "votes": 0,
                "electors": 0,
                "electors_known": False,
                "source_polls": [],
                "void": False,
                "no_poll": False,
            })
            record["votes"] += sum(nint(value) for value in group[candidate_vote_col]) + nint(first[rejected_col])
            electors_value = maybe_int(first[electors_col])
            if electors_value is not None:
                record["electors"] += electors_value
                record["electors_known"] = True
            record["source_polls"].append(source_poll)
            record["void"] = record["void"] or str(first.get(void_col, "")).strip().upper() == "Y"
            record["no_poll"] = record["no_poll"] or str(first.get(no_poll_col, "")).strip().upper() == "Y"

        for poll, record in sorted(records.items(), key=lambda item: poll_sort_value(item[0])):
            row = record["row"]
            votes = record["votes"]
            electors = record["electors"] if record["electors_known"] else None
            if elector_additions[poll]:
                electors = (electors or 0) + elector_additions[poll]
            zero_elector_bucket = electors == 0 and votes > 0
            if zero_elector_bucket:
                electors = None
            geometry = geom.get((str(code), poll))
            if geometry is None:
                summary["official_rows_without_geometry"] += 1
            else:
                emitted_source_keys.add((str(code), poll))
            source_polls = record["source_polls"]
            if poll.startswith("SVR-") and source_polls != [poll]:
                aggregated_note = f"Official source label normalized to {poll}: {', '.join(source_polls)}."
            elif source_polls != [poll]:
                aggregated_note = f"Official subpoll rows aggregated to match the atlas polygon: {', '.join(source_polls)}."
            else:
                aggregated_note = None
            no_geometry_note = (
                "No ordinary polling-division polygon was found in the atlas geometry source."
                if geometry is None else None
            )
            combined_target_note = (
                f"Electors from combined divisions added here: {', '.join(elector_addition_sources[poll])}."
                if elector_addition_sources[poll] else None
            )
            status_note = combine_notes(
                "Official source marks this as a void poll." if record["void"] else None,
                "Official source marks this as a no-poll-held row." if record["no_poll"] else None,
            )
            zero_elector_note = (
                "Elections Canada Format 2 reports 0 electors for this reporting bucket; treated as no supported elector denominator."
                if zero_elector_bucket else None
            )
            props = {
                "electoral_district_number": str(code),
                "electoral_district_name": str(row[district_name_col]),
                "polling_division_number": poll,
                "polling_division_name": cleaned_federal_poll_name(row[poll_name_col]),
                "vote_type": federal_vote_type(poll, row[poll_name_col]),
                "number_of_votes": votes,
                "number_of_electors": electors,
                "proportion_of_turnout": turnout_ratio(votes, electors),
                "vote_in_other_division": None,
                "source_note": combine_notes(
                    aggregated_note,
                    combined_target_note,
                    status_note,
                    zero_elector_note,
                    no_geometry_note,
                    over_one_note(votes, electors),
                ),
            }
            features.append(feature(props, geometry))

        for poll, source_poll, combined_target, row in combined_records:
            source_key = (str(code), source_poll)
            geometry = None if source_key in emitted_source_keys else geom.get(source_key)
            if geometry is None:
                summary["official_rows_without_geometry"] += 1
            else:
                emitted_source_keys.add(source_key)
            props = {
                "electoral_district_number": str(code),
                "electoral_district_name": str(row[district_name_col]),
                "polling_division_number": source_poll,
                "polling_division_name": cleaned_federal_poll_name(row[poll_name_col]),
                "vote_type": federal_vote_type(source_poll, row[poll_name_col]),
                "number_of_votes": None,
                "number_of_electors": maybe_int(row[electors_col]),
                "proportion_of_turnout": None,
                "vote_in_other_division": combined_target,
                "source_note": (
                    f"Combined official row {source_poll}; electors are added to division {combined_target}, "
                    "and votes are reported with that target division."
                ),
            }
            features.append(feature(props, geometry))

    def source_sort_key(item):
        code, poll = item[0]
        m = re.match(r"(\d+)", str(poll))
        return code, int(m.group(1)) if m else 999999, str(poll)

    for (code, poll), geometry in sorted(geom.items(), key=source_sort_key):
        if (code, poll) in emitted_source_keys:
            continue
        attrs = geom_attrs[(code, poll)]
        summary["source_polygons_without_official_turnout"] += 1
        votes = nint(attrs.get("TOTALVOTES"))
        props = {
            "electoral_district_number": code,
            "electoral_district_name": attrs.get("RIDINGNAME"),
            "polling_division_number": poll,
            "polling_division_name": None,
            "vote_type": federal_vote_type(poll),
            "number_of_votes": votes,
            "number_of_electors": None,
            "proportion_of_turnout": None,
            "vote_in_other_division": attrs.get("MERGED_WIT"),
            "source_note": "Atlas polygon had vote totals, but no matching official electors row was found; turnout left null.",
        }
        features.append(feature(props, geometry))
    write_dataset("toronto_federal_2025_turnout_poll_divisions", features)
    summary["features"] = len(features)
    summary["features_with_geometry"] = sum(1 for f in features if f["geometry"])
    return summary


def provincial_geometry_index():
    index = {}
    attrs = {}
    for code in PROVINCIAL_CODES:
        data = load_geojson(SOURCE_DOWNLOADS / "provincial_polygons" / f"{code}.geojson")
        for feat in data["features"]:
            props = feat["properties"]
            poll = str(props.get("POLLNO") or props.get("PD_LABEL") or "").strip()
            if poll:
                index[(str(code).zfill(3), poll.zfill(3))] = feat["geometry"]
                attrs[(str(code).zfill(3), poll.zfill(3))] = props
    return index, attrs


def build_provincial():
    geom, geom_attrs = provincial_geometry_index()
    df = pd.read_csv(RAW / "eo_2025_official_return.csv", dtype=str)
    df = df[df["EventNameEnglish"].str.contains("2025 Provincial General Election", na=False)]
    wanted = {str(c).zfill(3) for c in PROVINCIAL_CODES}
    df["district_number"] = df["ElectoralDistrictNameEnglish"].str.extract(r"^(\d{3})")
    df = df[df["district_number"].isin(wanted)]

    df["base_poll"] = df["PollNumber"].str.extract(r"^(\d+)", expand=False)
    advance_df = df[df["base_poll"].isna()].copy()
    df = df[df["base_poll"].notna()]

    grouped = {}
    suffix_aggregated = 0
    for (district, district_name, base_poll), g in df.groupby(
        ["district_number", "ElectoralDistrictNameEnglish", "base_poll"], dropna=False
    ):
        raw_polls = sorted(str(v) for v in g["PollNumber"].dropna().unique())
        if any(p != str(base_poll).zfill(3) and p != str(int(base_poll)) for p in raw_polls):
            suffix_aggregated += 1

        electors = 0
        rejected = 0
        unmarked = 0
        declined = 0
        for _, poll_rows in g.groupby("PollNumber", dropna=False):
            electors += nint(poll_rows["NamesOnListOfElectors"].dropna().iloc[0]) if len(poll_rows) else 0
            rejected += nint(poll_rows["BallotsFromBoxesRejectedAsMarkings"].dropna().iloc[0]) if len(poll_rows) else 0
            unmarked += nint(poll_rows["BallotsFromBoxesUnmarkedByVoters"].dropna().iloc[0]) if len(poll_rows) else 0
            declined += nint(poll_rows["BallotsDeclinedByVoters"].dropna().iloc[0]) if len(poll_rows) else 0

        votes = sum(nint(v) for v in g["AcceptedBallotCount"])
        combined_with = next((str(v) for v in g["CombinedWith"].dropna() if str(v).strip()), None)
        if combined_with:
            m = re.match(r"^(\d+)", combined_with)
            combined_with = m.group(1).zfill(3) if m else combined_with
        poll_s = str(base_poll).zfill(3)
        suffix_note = f"Aggregated official suffix polls: {', '.join(raw_polls)}." if len(raw_polls) > 1 else None
        combined_note = None
        if combined_with and combined_with != poll_s:
            combined_note = (
                f"Combined official poll; results are reported with division {combined_with}."
            )
        elif combined_with == poll_s:
            combined_note = "Official combined reporting target for one or more divisions."

        grouped[(district, poll_s)] = {
            "electoral_district_number": district,
            "electoral_district_name": re.sub(r"^\d{3}\s+", "", district_name),
            "polling_division_number": poll_s,
            "polling_division_name": unique_join(g["VotingPlaceAddressOrLocation"]),
            "vote_type": provincial_vote_type(unique_join(g["PollCategory"])),
            "number_of_votes": votes + rejected + unmarked + declined,
            "number_of_electors": electors,
            "proportion_of_turnout": turnout_ratio(votes + rejected + unmarked + declined, electors),
            "vote_in_other_division": combined_with if combined_with and combined_with != poll_s else None,
            "source_note": combine_notes(
                suffix_note,
                combined_note,
                over_one_note(votes + rejected + unmarked + declined, electors),
            ),
        }

    features = []
    official_without_geometry = 0
    emitted_source_keys = set()
    for key, props in sorted(grouped.items()):
        geometry = geom.get(key)
        if geometry is None:
            official_without_geometry += 1
        else:
            emitted_source_keys.add(key)
        features.append(feature(props, geometry))

    advance_rows = 0
    for (district, district_name, poll), g in advance_df.groupby(
        ["district_number", "ElectoralDistrictNameEnglish", "PollNumber"], dropna=False
    ):
        raw_electors = nint(g["NamesOnListOfElectors"].dropna().iloc[0]) if len(g) else 0
        electors = raw_electors or None
        rejected = nint(g["BallotsFromBoxesRejectedAsMarkings"].dropna().iloc[0]) if len(g) else 0
        unmarked = nint(g["BallotsFromBoxesUnmarkedByVoters"].dropna().iloc[0]) if len(g) else 0
        declined = nint(g["BallotsDeclinedByVoters"].dropna().iloc[0]) if len(g) else 0
        votes = sum(nint(v) for v in g["AcceptedBallotCount"]) + rejected + unmarked + declined
        if not votes:
            continue
        advance_rows += 1
        props = {
            "electoral_district_number": district,
            "electoral_district_name": re.sub(r"^\d{3}\s+", "", district_name),
            "polling_division_number": str(poll),
            "polling_division_name": unique_join(g["VotingPlaceAddressOrLocation"]),
            "vote_type": "advance",
            "number_of_votes": votes,
            "number_of_electors": electors,
            "proportion_of_turnout": turnout_ratio(votes, electors),
            "vote_in_other_division": None,
            "source_note": combine_notes(
                (
                    "Official advance-vote reporting bucket; no ordinary polling-division polygon is provided for this row. "
                    "Votes are included in the riding total."
                ),
                (
                    "No separate elector count is provided for this advance-vote row, so turnout is left blank."
                    if electors is None else None
                ),
                over_one_note(votes, electors),
            ),
        }
        features.append(feature(props, None))

    source_without_official = 0
    for key, geometry in sorted(geom.items()):
        if key in emitted_source_keys:
            continue
        attrs = geom_attrs[key]
        source_without_official += 1
        props = {
            "electoral_district_number": key[0],
            "electoral_district_name": attrs.get("RIDINGNAME"),
            "polling_division_number": attrs.get("PD_LABEL") or str(attrs.get("POLLNO")),
            "polling_division_name": None,
            "vote_type": "election_day",
            "number_of_votes": nint(attrs.get("TOTALVOTES")),
            "number_of_electors": None,
            "proportion_of_turnout": None,
            "vote_in_other_division": attrs.get("COMBINED") or attrs.get("NOTE"),
            "source_note": "Atlas polygon had vote totals, but no matching official electors row was found; turnout left null.",
        }
        features.append(feature(props, geometry))
    write_dataset("toronto_provincial_2025_turnout_poll_divisions", features)
    return {
        "features": len(features),
        "features_with_geometry": sum(1 for f in features if f["geometry"]),
        "official_rows_without_geometry": official_without_geometry,
        "official_advance_rows_without_geometry": advance_rows,
        "source_polygons_without_official_turnout": source_without_official,
        "official_suffix_poll_groups_aggregated": suffix_aggregated,
    }


def build_municipal():
    geom_data = load_geojson(RAW / "toronto_2023_subdivisions.geojson")
    geom = {}
    for feat in geom_data["features"]:
        code = str(feat["properties"]["AREA_LONG_CODE"]).zfill(5)
        geom[code] = feat["geometry"]

    stats = pd.read_excel(RAW / "toronto_2023_mayor_voter_statistics.xlsx", sheet_name="2023 Voter Turnout Statisti M")
    stats_by_code = {}
    for _, row in stats.iterrows():
        ward = maybe_int(row.get("Ward"))
        sub = maybe_int(row.get("Sub"))
        if ward is None or sub is None:
            continue
        code = f"{ward:02d}{sub:03d}"
        stats_by_code[code] = {
            "polling_division_name": str(row.get("Building Name")).strip() if not pd.isna(row.get("Building Name")) else None,
            "number_of_votes": maybe_int(row.get("Number Voted")),
            "number_of_electors": maybe_int(row.get("Total Eligible Electors")),
            "rejected_ballots": maybe_int(row.get("Rejected Ballots")),
            "declined_ballots": maybe_int(row.get("Declined Ballots")),
        }

    xls = pd.ExcelFile(RAW / "toronto_2023_mayor.xlsx")
    votes_by_code = defaultdict(int)
    ward_names = {}
    for sheet in xls.sheet_names:
        if not sheet.startswith("Ward "):
            continue
        ward = int(sheet.split()[1])
        df = pd.read_excel(xls, sheet_name=sheet, header=None)
        ward_title = str(df.iloc[0, 0])
        ward_names[str(ward).zfill(2)] = cleaned_municipal_ward_name(ward_title)
        subdivisions = [v for v in list(df.iloc[1, 1:]) if str(v) != "nan" and str(v) != "Total"]
        total_row = next(
            (
                idx for idx, value in df.iloc[:, 0].items()
                if str(value).strip().startswith(f"City Ward {ward} Totals")
            ),
            len(df),
        )
        for col_offset, sub in enumerate(subdivisions, start=1):
            sub_num = str(nint(sub)).zfill(3)
            code = f"{ward:02d}{sub_num}"
            votes = 0
            for value in df.iloc[3:total_row, col_offset]:
                votes += nint(value)
            votes_by_code[code] += votes

    features = []
    for code, geometry in sorted(geom.items()):
        ward = code[:2]
        stat = stats_by_code.get(code, {})
        votes = votes_by_code.get(code, stat.get("number_of_votes"))
        e = stat.get("number_of_electors")
        props = {
            "electoral_district_number": ward,
            "electoral_district_name": ward_names.get(ward),
            "polling_division_number": str(int(code[2:])),
            "polling_division_name": stat.get("polling_division_name"),
            "vote_type": municipal_vote_type(code[2:]),
            "number_of_votes": votes,
            "number_of_electors": e,
            "proportion_of_turnout": turnout_ratio(votes, e),
            "vote_in_other_division": None,
            "source_note": municipal_regular_note(votes, e, code, code in votes_by_code),
        }
        features.append(feature(props, geometry))
    for code, votes in sorted(votes_by_code.items()):
        if code in geom:
            continue
        ward = code[:2]
        poll = code[2:]
        stat = stats_by_code.get(code, {})
        votes = stat.get("number_of_votes", votes)
        e = stat.get("number_of_electors")
        props = {
            "electoral_district_number": ward,
            "electoral_district_name": ward_names.get(ward),
            "polling_division_number": str(int(poll)),
            "polling_division_name": stat.get("polling_division_name") or municipal_special_poll_name(poll),
            "vote_type": municipal_vote_type(poll),
            "number_of_votes": votes,
            "number_of_electors": e,
            "proportion_of_turnout": turnout_ratio(votes, e),
            "vote_in_other_division": None,
            "source_note": municipal_special_note(code, votes),
        }
        features.append(feature(props, None))
    write_dataset("toronto_municipal_2023_mayor_turnout_subdivisions", features)
    return {
        "features": len(features),
        "geometry_subdivisions_without_vote_result": sum(1 for k in geom if k not in votes_by_code),
        "workbook_vote_subdivisions_without_geometry": sum(1 for k in votes_by_code if k not in geom),
    }


def main():
    summary = {
        "municipal_2023": build_municipal(),
        "provincial_2025": build_provincial(),
        "federal_2025": build_federal(),
    }
    with open(OUT / "qa_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
