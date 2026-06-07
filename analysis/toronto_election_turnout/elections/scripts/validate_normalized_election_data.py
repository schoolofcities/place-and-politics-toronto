#!/usr/bin/env python3
"""Validate keys, joins, and vote totals in normalized election outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[4]
PROCESSED = (
    REPO_ROOT / "data" / "toronto_election_turnout" / "elections" / "processed"
)
CANDIDATE_DETAILS = PROCESSED / "candidate_details"
TURNOUT = PROCESSED / "turnout"


def main():
    with open(
        CANDIDATE_DETAILS / "normalized_election_results_metadata.json",
        encoding="utf-8",
    ) as f:
        metadata = json.load(f)

    for election_id, config in metadata.items():
        polls = pd.read_csv(
            TURNOUT / config["poll_summary_csv"],
            dtype={"poll_id": str},
            low_memory=False,
        )
        candidates = pd.read_csv(
            CANDIDATE_DETAILS / config["candidate_file"],
            dtype={"candidate_id": str},
        )
        votes = pd.read_csv(
            CANDIDATE_DETAILS / config["poll_candidate_vote_file"],
            dtype={"poll_id": str, "candidate_id": str},
        )
        party_fields = list(config["party_columns"].values())
        party_totals = polls[party_fields].sum(axis=1, min_count=1)
        covered = polls["poll_total_candidate_votes"].notna()

        checks = {
            "poll_id is unique": polls["poll_id"].is_unique,
            "candidate_id is unique": candidates["candidate_id"].is_unique,
            "geometry is the final CSV column": polls.columns[-1] == "geometry",
            "has_geometry is not published": "has_geometry" not in polls.columns,
            "party fields immediately follow turnout": list(
                polls.columns[
                    polls.columns.get_loc("proportion_of_turnout") + 1 :
                    polls.columns.get_loc("vote_in_other_division")
                ]
            )
            == party_fields,
            "poll-candidate key is unique": not votes.duplicated(
                ["poll_id", "candidate_id"]
            ).any(),
            "all bridge polls exist": votes["poll_id"].isin(polls["poll_id"]).all(),
            "all bridge candidates exist": votes["candidate_id"]
            .isin(candidates["candidate_id"])
            .all(),
            "bridge and poll candidate totals match": (
                votes["candidate_vote_count"].sum()
                == polls["poll_total_candidate_votes"].sum()
            ),
            "party and poll candidate totals match": (
                party_totals[covered]
                == polls.loc[covered, "poll_total_candidate_votes"]
            ).all(),
            "uncovered polls have no party values": not polls.loc[
                ~covered, party_fields
            ]
            .notna()
            .any(axis=1)
            .any(),
        }
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            raise ValueError(f"{election_id} validation failed: {', '.join(failed)}")

        print(
            f"{election_id}: validated {len(polls):,} polls, "
            f"{len(candidates):,} candidates, and {len(votes):,} vote rows"
        )


if __name__ == "__main__":
    main()
