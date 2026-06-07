#!/usr/bin/env python3
"""Rebuild all processed election tables in dependency order."""

import build_candidate_party_votes
import build_turnout_geojson
import validate_normalized_election_data


def main():
    build_turnout_geojson.main()
    build_candidate_party_votes.main()
    validate_normalized_election_data.main()


if __name__ == "__main__":
    main()
