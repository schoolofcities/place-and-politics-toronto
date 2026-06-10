"""Election allocation workflow built on population-weighted spatial crosswalks."""

from __future__ import annotations

from collections import defaultdict

from osgeo import ogr

from config import (
    ALLOCATION_AUDIT_ROOT,
    ANCILLARY_WEIGHT_FIELD,
    CONTEXT_AUDIT_ROOT,
    CROSSWALK_ROOT,
    OUTPUT_ROOT,
    VALIDATION_ROOT,
    WORKING_EPSG,
)
from io_utils import number, read_csv, write_csv, write_json
from spatial import (
    SpatialGrid,
    build_population_weights,
    geometry_from_json,
    load_district_geometries,
)


TOLERANCE = 1e-6


def _party_fields(rows):
    if not rows:
        return []
    return [
        field
        for field in rows[0]
        if field.startswith("party_") and field.endswith("_votes")
    ]


def _candidate_inputs(config):
    candidates = read_csv(config.candidate_csv)
    candidate_lookup = {row["candidate_id"]: row for row in candidates}
    bridge = defaultdict(list)
    for row in read_csv(config.candidate_votes_csv):
        bridge[row["poll_id"]].append(
            (row["candidate_id"], number(row["candidate_vote_count"]) or 0.0)
        )
    return candidate_lookup, bridge


def _new_ct_result(
    election_id,
    ct_id,
    citizen_canadian_18over,
    citizen_canadian_18over_status,
    party_fields,
):
    row = {
        "election_id": election_id,
        "ct_id": ct_id,
        "estimated_total_votes": 0.0,
        "estimated_electors": 0.0,
        "estimated_valid_candidate_votes": 0.0,
        "estimated_turnout": None,
        "citizen_canadian_18over": citizen_canadian_18over,
        "citizen_canadian_18over_status": citizen_canadian_18over_status,
        "estimated_turnout_citizen_18plus": None,
        "estimated_participation_citizen_18plus": None,
        "num_source_polls": 0,
        "num_source_district_vote_type_groups": 0,
        "share_from_largest_source": 0.0,
        "allocation_method": "",
        "fallback_area_weight_used": False,
        "zero_population_weight": False,
        "suppressed_da_count": 0,
        "suppressed_da_area_share": 0.0,
        "excluded_weight_area_share": 0.0,
        "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
        "ancillary_weight_status": "published_plus_suppressed_as_zero",
        "no_geometry_district_allocation_used": False,
        "votes_exceed_electors_flag": False,
        "missing_votes_excluded_flag": False,
    }
    for field in party_fields:
        row[field] = 0.0
    row["_source_votes"] = defaultdict(float)
    row["_methods"] = set()
    row["_suppressed_ids"] = set()
    row["_suppressed_area_weighted_sum"] = 0.0
    row["_excluded_area_weighted_sum"] = 0.0
    row["_quality_weight"] = 0.0
    return row


def _add_allocation(
    ct_result,
    source_key,
    source_kind,
    weight,
    poll,
    party_fields,
    diagnostics,
):
    votes = number(poll["number_of_votes"]) or 0.0
    electors = number(poll["number_of_electors"])
    valid_votes = number(poll["poll_total_candidate_votes"])
    allocated_votes = votes * weight
    ct_result["estimated_total_votes"] += allocated_votes
    if electors is not None:
        ct_result["estimated_electors"] += electors * weight
    if valid_votes is not None:
        ct_result["estimated_valid_candidate_votes"] += valid_votes * weight
    for field in party_fields:
        value = number(poll.get(field))
        if value is not None:
            ct_result[field] += value * weight
    ct_result["_source_votes"][source_key] += allocated_votes
    ct_result["_methods"].add(source_kind)
    quality_weight = abs(allocated_votes)
    ct_result["_quality_weight"] += quality_weight
    ct_result["_suppressed_area_weighted_sum"] += (
        diagnostics["suppressed_da_area_share"] * quality_weight
    )
    ct_result["_excluded_area_weighted_sum"] += (
        diagnostics["excluded_weight_area_share"] * quality_weight
    )
    ct_result["fallback_area_weight_used"] |= diagnostics[
        "fallback_area_weight_used"
    ]
    ct_result["zero_population_weight"] |= diagnostics["zero_population_weight"]
    ct_result["votes_exceed_electors_flag"] |= (
        electors is not None and votes > electors
    )
    if source_kind == "district_no_geometry_population_weighted":
        ct_result["no_geometry_district_allocation_used"] = True


def _finalize_ct_results(results, missing_vote_ct_ids):
    output = []
    for row in results.values():
        source_votes = row.pop("_source_votes")
        methods = row.pop("_methods")
        row.pop("_suppressed_ids")
        suppressed_sum = row.pop("_suppressed_area_weighted_sum")
        excluded_sum = row.pop("_excluded_area_weighted_sum")
        quality_weight = row.pop("_quality_weight")
        row["allocation_method"] = ";".join(sorted(methods))
        row["num_source_polls"] = sum(
            key.startswith("poll:") for key in source_votes
        )
        row["num_source_district_vote_type_groups"] = sum(
            key.startswith("district:") for key in source_votes
        )
        largest = max(source_votes.values(), default=0.0)
        row["share_from_largest_source"] = (
            largest / row["estimated_total_votes"]
            if row["estimated_total_votes"] > 0
            else 0.0
        )
        row["suppressed_da_area_share"] = (
            suppressed_sum / quality_weight if quality_weight else 0.0
        )
        row["excluded_weight_area_share"] = (
            excluded_sum / quality_weight if quality_weight else 0.0
        )
        row["estimated_turnout"] = (
            row["estimated_total_votes"] / row["estimated_electors"]
            if row["estimated_electors"] > 0
            else None
        )
        row["estimated_participation_citizen_18plus"] = (
            row["estimated_total_votes"] / row["citizen_canadian_18over"]
            if row["citizen_canadian_18over"] is not None
            and row["citizen_canadian_18over"] > 0
            else None
        )
        row["estimated_turnout_citizen_18plus"] = row[
            "estimated_participation_citizen_18plus"
        ]
        row["missing_votes_excluded_flag"] = row["ct_id"] in missing_vote_ct_ids
        output.append(row)
    return sorted(output, key=lambda item: item["ct_id"])


def _validation_row(
    election_id,
    geography_level,
    geography_id,
    measure_type,
    measure_id,
    source_total,
    allocated_total,
):
    difference = allocated_total - source_total
    return {
        "election_id": election_id,
        "geography_level": geography_level,
        "geography_id": geography_id,
        "measure_type": measure_type,
        "measure_id": measure_id,
        "source_total": source_total,
        "allocated_total": allocated_total,
        "difference": difference,
        "absolute_difference": abs(difference),
        "within_tolerance": abs(difference) <= TOLERANCE,
    }


def run_election(config, cts, das):
    polls = read_csv(config.poll_csv)
    party_fields = _party_fields(polls)
    candidate_lookup, candidate_bridge = _candidate_inputs(config)
    ct_grid = SpatialGrid(cts, lambda item: item.geometry)
    da_grid = SpatialGrid(das, lambda item: item.geometry)
    ct_results = {
        ct.ct_id: _new_ct_result(
            config.election_id,
            ct.ct_id,
            ct.citizen_canadian_18over,
            ct.citizen_canadian_18over_status,
            party_fields,
        )
        for ct in cts
    }

    poll_crosswalk = []
    district_crosswalk = []
    exclusions = []
    audit_rows = []
    candidate_allocated = defaultdict(float)
    candidate_allocated_by_district = defaultdict(float)
    source_totals = defaultdict(float)
    source_totals_by_district = defaultdict(float)
    source_totals_by_poll = defaultdict(float)
    allocated_totals = defaultdict(float)
    allocated_totals_by_district = defaultdict(float)
    allocated_totals_by_poll = defaultdict(float)
    candidate_source = defaultdict(float)
    candidate_source_by_district = defaultdict(float)
    candidate_source_by_poll = defaultdict(float)
    candidate_allocated_by_poll = defaultdict(float)

    mapped = []
    no_geometry = []
    invalid_geometry_repaired = 0
    missing_votes_count = 0
    votes_exceed_electors_count = 0
    missing_vote_ct_ids = set()

    for poll in polls:
        district_id = config.normalize_district_id(
            poll["electoral_district_number"]
        )
        poll["_district_id"] = district_id
        votes = number(poll["number_of_votes"])
        electors = number(poll["number_of_electors"])
        geometry_text = poll.get("geometry", "")
        has_geometry = bool(geometry_text and geometry_text.strip())

        if votes is None:
            missing_votes_count += 1
            if has_geometry:
                excluded_geometry = geometry_from_json(geometry_text)
                if excluded_geometry is not None:
                    for ct in ct_grid.query(excluded_geometry):
                        if excluded_geometry.Intersects(ct.geometry):
                            piece = excluded_geometry.Intersection(ct.geometry)
                            if (
                                piece is not None
                                and not piece.IsEmpty()
                                and piece.GetArea() > 0
                            ):
                                missing_vote_ct_ids.add(ct.ct_id)
            exclusions.append(
                {
                    "election_id": config.election_id,
                    "poll_id": poll["poll_id"],
                    "electoral_district_number": district_id,
                    "vote_type": poll["vote_type"],
                    "number_of_votes": "",
                    "number_of_electors": poll["number_of_electors"],
                    "exclusion_reason": (
                        "votes_reported_in_other_division"
                        if poll.get("vote_in_other_division", "").strip()
                        else "missing_votes"
                    ),
                    "missing_votes_excluded_flag": True,
                }
            )
            continue

        if electors is not None and votes > electors:
            votes_exceed_electors_count += 1

        source_totals["total_votes"] += votes
        source_totals_by_district[(district_id, "total_votes")] += votes
        source_totals_by_poll[(poll["poll_id"], "total_votes")] += votes
        if electors is not None:
            source_totals["electors"] += electors
            source_totals_by_district[(district_id, "electors")] += electors
            source_totals_by_poll[(poll["poll_id"], "electors")] += electors
        valid_votes = number(poll["poll_total_candidate_votes"])
        if valid_votes is not None:
            source_totals["valid_candidate_votes"] += valid_votes
            source_totals_by_district[
                (district_id, "valid_candidate_votes")
            ] += valid_votes
            source_totals_by_poll[
                (poll["poll_id"], "valid_candidate_votes")
            ] += valid_votes
        for field in party_fields:
            value = number(poll.get(field))
            if value is not None:
                source_totals[f"party:{field}"] += value
                source_totals_by_district[(district_id, f"party:{field}")] += value
                source_totals_by_poll[(poll["poll_id"], f"party:{field}")] += value
        for candidate_id, value in candidate_bridge.get(poll["poll_id"], ()):
            candidate_source[candidate_id] += value
            candidate_source_by_district[(district_id, candidate_id)] += value
            candidate_source_by_poll[(poll["poll_id"], candidate_id)] += value

        if has_geometry:
            original = ogr.CreateGeometryFromJson(geometry_text)
            if original is not None and not original.IsValid():
                invalid_geometry_repaired += 1
            geometry = geometry_from_json(geometry_text)
            if geometry is None:
                exclusions.append(
                    {
                        "election_id": config.election_id,
                        "poll_id": poll["poll_id"],
                        "electoral_district_number": district_id,
                        "vote_type": poll["vote_type"],
                        "number_of_votes": poll["number_of_votes"],
                        "number_of_electors": poll["number_of_electors"],
                        "exclusion_reason": "geometry_not_polygonal_after_repair",
                        "missing_votes_excluded_flag": False,
                    }
                )
                continue
            mapped.append((poll, geometry))
        else:
            no_geometry.append(poll)

    for poll, geometry in mapped:
        overlaps, diagnostics = build_population_weights(
            poll["poll_id"],
            geometry,
            ct_grid,
            da_grid,
            weight_variable=ANCILLARY_WEIGHT_FIELD,
            allow_area_fallback=True,
        )
        if not overlaps:
            exclusions.append(
                {
                    "election_id": config.election_id,
                    "poll_id": poll["poll_id"],
                    "electoral_district_number": poll["_district_id"],
                    "vote_type": poll["vote_type"],
                    "number_of_votes": poll["number_of_votes"],
                    "number_of_electors": poll["number_of_electors"],
                    "exclusion_reason": "mapped_poll_has_no_ct_overlap",
                    "missing_votes_excluded_flag": False,
                }
            )
            continue
        for overlap in overlaps:
            overlap.update(
                {
                    "election_id": config.election_id,
                    "poll_id": poll["poll_id"],
                    "electoral_district_number": poll["_district_id"],
                    "allocation_method": (
                        "poll_area_fallback"
                        if diagnostics["fallback_area_weight_used"]
                        else "poll_population_weighted"
                    ),
                    "fallback_area_weight_used": diagnostics[
                        "fallback_area_weight_used"
                    ],
                    "zero_population_weight": diagnostics[
                        "zero_population_weight"
                    ],
                    "suppressed_da_count": diagnostics["suppressed_da_count"],
                    "suppressed_da_area_share": diagnostics[
                        "suppressed_da_area_share"
                    ],
                    "excluded_weight_area_share": diagnostics[
                        "excluded_weight_area_share"
                    ],
                    "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
                    "ancillary_weight_status": (
                        "zero_weight_area_fallback"
                        if diagnostics["fallback_area_weight_used"]
                        else "published_plus_suppressed_as_zero"
                    ),
                    "votes_exceed_electors_flag": (
                        number(poll["number_of_electors"]) is not None
                        and number(poll["number_of_votes"])
                        > number(poll["number_of_electors"])
                    ),
                }
            )
            poll_crosswalk.append(overlap)
            method = overlap["allocation_method"]
            weight = overlap["allocation_weight"]
            result = ct_results[overlap["ct_id"]]
            _add_allocation(
                result,
                f"poll:{poll['poll_id']}",
                method,
                weight,
                poll,
                party_fields,
                diagnostics,
            )
            _track_allocated(
                poll,
                weight,
                party_fields,
                allocated_totals,
                allocated_totals_by_district,
                allocated_totals_by_poll,
            )
            for candidate_id, value in candidate_bridge.get(poll["poll_id"], ()):
                allocated = value * weight
                candidate_allocated[(overlap["ct_id"], candidate_id)] += allocated
                candidate_allocated_by_district[
                    (poll["_district_id"], candidate_id)
                ] += allocated
                candidate_allocated_by_poll[(poll["poll_id"], candidate_id)] += allocated

    no_geometry_district_ids = {
        poll["_district_id"] for poll in no_geometry if poll["_district_id"]
    }
    district_geometries, invalid_districts = load_district_geometries(
        config, no_geometry_district_ids
    )
    district_weights = {}
    for district_id in sorted(no_geometry_district_ids):
        geometry = district_geometries.get(district_id)
        if geometry is None:
            continue
        overlaps, diagnostics = build_population_weights(
            district_id,
            geometry,
            ct_grid,
            da_grid,
            weight_variable=ANCILLARY_WEIGHT_FIELD,
            allow_area_fallback=False,
        )
        district_weights[district_id] = (overlaps, diagnostics)
        for overlap in overlaps:
            overlap.update(
                {
                    "election_id": config.election_id,
                    "electoral_district_number": district_id,
                    "allocation_method": "district_no_geometry_population_weighted",
                    "fallback_area_weight_used": False,
                    "zero_population_weight": diagnostics[
                        "zero_population_weight"
                    ],
                    "suppressed_da_count": diagnostics["suppressed_da_count"],
                    "suppressed_da_area_share": diagnostics[
                        "suppressed_da_area_share"
                    ],
                    "excluded_weight_area_share": diagnostics[
                        "excluded_weight_area_share"
                    ],
                    "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
                    "ancillary_weight_status": (
                        "zero_weight_unallocated"
                        if diagnostics["zero_population_weight"]
                        else "published_plus_suppressed_as_zero"
                    ),
                    "no_geometry_district_allocation_used": True,
                }
            )
            district_crosswalk.append(overlap)

    for poll in no_geometry:
        district_id = poll["_district_id"]
        weights = district_weights.get(district_id)
        if not district_id or weights is None:
            exclusions.append(
                {
                    "election_id": config.election_id,
                    "poll_id": poll["poll_id"],
                    "electoral_district_number": district_id,
                    "vote_type": poll["vote_type"],
                    "number_of_votes": poll["number_of_votes"],
                    "number_of_electors": poll["number_of_electors"],
                    "exclusion_reason": (
                        "missing_district_id"
                        if not district_id
                        else "district_geometry_not_found"
                    ),
                    "missing_votes_excluded_flag": False,
                }
            )
            continue
        overlaps, diagnostics = weights
        if diagnostics["zero_population_weight"] or not overlaps:
            exclusions.append(
                {
                    "election_id": config.election_id,
                    "poll_id": poll["poll_id"],
                    "electoral_district_number": district_id,
                    "vote_type": poll["vote_type"],
                    "number_of_votes": poll["number_of_votes"],
                    "number_of_electors": poll["number_of_electors"],
                    "exclusion_reason": "district_has_zero_population_weight",
                    "missing_votes_excluded_flag": False,
                }
            )
            continue
        group_key = f"district:{district_id}:{poll['vote_type']}"
        for overlap in overlaps:
            weight = overlap["allocation_weight"]
            result = ct_results[overlap["ct_id"]]
            _add_allocation(
                result,
                group_key,
                "district_no_geometry_population_weighted",
                weight,
                poll,
                party_fields,
                diagnostics,
            )
            _track_allocated(
                poll,
                weight,
                party_fields,
                allocated_totals,
                allocated_totals_by_district,
                allocated_totals_by_poll,
            )
            for candidate_id, value in candidate_bridge.get(poll["poll_id"], ()):
                allocated = value * weight
                candidate_allocated[(overlap["ct_id"], candidate_id)] += allocated
                candidate_allocated_by_district[
                    (district_id, candidate_id)
                ] += allocated
                candidate_allocated_by_poll[(poll["poll_id"], candidate_id)] += allocated

    ct_output = _finalize_ct_results(ct_results, missing_vote_ct_ids)
    suppressed_by_ct = defaultdict(int)
    for da in das:
        if da.citizen_suppressed:
            suppressed_by_ct[da.ct_id] += 1
    for row in ct_output:
        row["suppressed_da_count"] = suppressed_by_ct[row["ct_id"]]

    candidate_output = []
    for (ct_id, candidate_id), value in sorted(candidate_allocated.items()):
        candidate = candidate_lookup[candidate_id]
        candidate_output.append(
            {
                "election_id": config.election_id,
                "ct_id": ct_id,
                "candidate_id": candidate_id,
                "candidate_name": candidate["candidate_name"],
                "party_name": candidate["party_name"],
                "estimated_candidate_votes": value,
            }
        )

    validation = []
    for measure_id, source_total in sorted(source_totals.items()):
        validation.append(
            _validation_row(
                config.election_id,
                "global",
                "ALL",
                measure_id.split(":", 1)[0],
                measure_id,
                source_total,
                allocated_totals[measure_id],
            )
        )
    for (district_id, measure_id), source_total in sorted(
        source_totals_by_district.items()
    ):
        validation.append(
            _validation_row(
                config.election_id,
                "district",
                district_id,
                measure_id.split(":", 1)[0],
                measure_id,
                source_total,
                allocated_totals_by_district[(district_id, measure_id)],
            )
        )
    for (poll_id, measure_id), source_total in sorted(source_totals_by_poll.items()):
        validation.append(
            _validation_row(
                config.election_id,
                "source_poll",
                poll_id,
                measure_id.split(":", 1)[0],
                measure_id,
                source_total,
                allocated_totals_by_poll[(poll_id, measure_id)],
            )
        )
    for candidate_id, source_total in sorted(candidate_source.items()):
        validation.append(
            _validation_row(
                config.election_id,
                "global",
                "ALL",
                "candidate",
                candidate_id,
                source_total,
                sum(
                    value
                    for (ct_id, current_id), value in candidate_allocated.items()
                    if current_id == candidate_id
                ),
            )
        )
    for (district_id, candidate_id), source_total in sorted(
        candidate_source_by_district.items()
    ):
        validation.append(
            _validation_row(
                config.election_id,
                "district",
                district_id,
                "candidate",
                candidate_id,
                source_total,
                candidate_allocated_by_district[(district_id, candidate_id)],
            )
        )
    for (poll_id, candidate_id), source_total in sorted(
        candidate_source_by_poll.items()
    ):
        validation.append(
            _validation_row(
                config.election_id,
                "source_poll",
                poll_id,
                "candidate",
                candidate_id,
                source_total,
                candidate_allocated_by_poll[(poll_id, candidate_id)],
            )
        )

    no_geometry_audit = []
    for poll in no_geometry:
        poll_id = poll["poll_id"]
        source_votes = number(poll["number_of_votes"]) or 0.0
        allocated_votes = allocated_totals_by_poll[(poll_id, "total_votes")]
        party_failures = 0
        for field in party_fields:
            source_value = number(poll.get(field))
            if source_value is not None and abs(
                allocated_totals_by_poll[(poll_id, f"party:{field}")]
                - source_value
            ) > TOLERANCE:
                party_failures += 1
        candidate_failures = 0
        for candidate_id, source_value in candidate_bridge.get(poll_id, ()):
            if abs(
                candidate_allocated_by_poll[(poll_id, candidate_id)] - source_value
            ) > TOLERANCE:
                candidate_failures += 1
        no_geometry_audit.append(
            {
                "election_id": config.election_id,
                "poll_id": poll_id,
                "electoral_district_number": poll["_district_id"],
                "vote_type": poll["vote_type"],
                "source_total_votes": source_votes,
                "allocated_total_votes": allocated_votes,
                "difference": allocated_votes - source_votes,
                "allocation_weight_sum": (
                    allocated_votes / source_votes if source_votes else 1.0
                ),
                "party_preservation_failures": party_failures,
                "candidate_preservation_failures": candidate_failures,
                "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
                "allocation_method": "district_no_geometry_population_weighted",
                "fully_allocated": (
                    abs(allocated_votes - source_votes) <= TOLERANCE
                    and party_failures == 0
                    and candidate_failures == 0
                ),
            }
        )

    audit_rows.extend(
        [
            {
                "election_id": config.election_id,
                "metric": "input_poll_rows",
                "value": len(polls),
            },
            {
                "election_id": config.election_id,
                "metric": "mapped_vote_rows",
                "value": len(mapped),
            },
            {
                "election_id": config.election_id,
                "metric": "no_geometry_vote_rows",
                "value": len(no_geometry),
            },
            {
                "election_id": config.election_id,
                "metric": "missing_votes_excluded_rows",
                "value": missing_votes_count,
            },
            {
                "election_id": config.election_id,
                "metric": "votes_exceed_electors_rows",
                "value": votes_exceed_electors_count,
            },
            {
                "election_id": config.election_id,
                "metric": "invalid_poll_geometries_repaired",
                "value": invalid_geometry_repaired,
            },
            {
                "election_id": config.election_id,
                "metric": "invalid_district_geometries_repaired",
                "value": invalid_districts,
            },
            {
                "election_id": config.election_id,
                "metric": "poll_area_fallback_rows",
                "value": len(
                    {
                        row["poll_id"]
                        for row in poll_crosswalk
                        if row["fallback_area_weight_used"]
                    }
                ),
            },
            {
                "election_id": config.election_id,
                "metric": "excluded_or_unallocated_rows",
                "value": len(exclusions),
            },
        ]
    )

    final_prefix = OUTPUT_ROOT / config.election_id
    crosswalk_prefix = CROSSWALK_ROOT / config.election_id
    allocation_prefix = ALLOCATION_AUDIT_ROOT / config.election_id
    validation_prefix = VALIDATION_ROOT / config.election_id
    context_prefix = CONTEXT_AUDIT_ROOT / config.election_id
    write_csv(
        crosswalk_prefix.with_name(
            crosswalk_prefix.name + "_poll_to_ct_crosswalk.csv"
        ),
        poll_crosswalk,
    )
    write_csv(
        crosswalk_prefix.with_name(
            crosswalk_prefix.name + "_district_to_ct_crosswalk.csv"
        ),
        district_crosswalk,
    )
    write_csv(
        final_prefix.with_name(final_prefix.name + "_ct_estimated_results.csv"),
        ct_output,
    )
    write_csv(
        final_prefix.with_name(
            final_prefix.name + "_ct_candidate_estimated_votes.csv"
        ),
        candidate_output,
    )
    write_csv(
        allocation_prefix.with_name(
            allocation_prefix.name + "_excluded_unallocated.csv"
        ),
        exclusions,
        fieldnames=[
            "election_id",
            "poll_id",
            "electoral_district_number",
            "vote_type",
            "number_of_votes",
            "number_of_electors",
            "exclusion_reason",
            "missing_votes_excluded_flag",
        ],
    )
    write_csv(
        validation_prefix.with_name(
            validation_prefix.name + "_validation.csv"
        ),
        validation,
    )
    write_csv(
        allocation_prefix.with_name(
            allocation_prefix.name + "_no_geometry_allocation_audit.csv"
        ),
        no_geometry_audit,
    )
    write_csv(
        allocation_prefix.with_name(allocation_prefix.name + "_audit.csv"),
        audit_rows,
    )

    failed_primary = [
        row
        for row in validation
        if row["measure_type"] in {"total_votes", "party", "candidate"}
        and not row["within_tolerance"]
    ]
    census_citizen_18plus = sum(
        ct.citizen_canadian_18over or 0.0 for ct in cts
    )
    official_row_turnout = (
        source_totals["total_votes"] / source_totals["electors"]
        if source_totals["electors"] > 0
        else None
    )
    citizen_18plus_participation = (
        source_totals["total_votes"] / census_citizen_18plus
        if census_citizen_18plus > 0
        else None
    )
    official_difference = (
        abs(official_row_turnout - config.published_turnout_rate)
        if official_row_turnout is not None
        else None
    )
    census_difference = (
        abs(citizen_18plus_participation - config.published_turnout_rate)
        if citizen_18plus_participation is not None
        else None
    )
    turnout_comparison = {
        "election_id": config.election_id,
        "official_total_votes": source_totals["total_votes"],
        "official_available_electors": source_totals["electors"],
        "official_row_turnout_rate": official_row_turnout,
        "published_reference_turnout_rate": config.published_turnout_rate,
        "published_turnout_source_note": config.published_turnout_source_note,
        "ct_citizen_canadian_18over_denominator": census_citizen_18plus,
        "ct_suppressed_denominator_count": sum(
            ct.citizen_canadian_18over is None for ct in cts
        ),
        "interpolated_citizen_18plus_participation_rate": (
            citizen_18plus_participation
        ),
        "official_row_absolute_difference": official_difference,
        "citizen_18plus_absolute_difference": census_difference,
        "citizen_18plus_rate_closer_to_published_than_official_row_rate": (
            census_difference <= official_difference
            if census_difference is not None and official_difference is not None
            else False
        ),
        "interpretation": (
            "Diagnostic only: Canadian citizens aged 18+ is a Census eligibility "
            "proxy, not the official registered-elector denominator."
        ),
    }
    write_csv(
        context_prefix.with_name(
            context_prefix.name + "_turnout_comparison.csv"
        ),
        [turnout_comparison],
    )
    summary = {
        "election_id": config.election_id,
        "working_crs": f"EPSG:{WORKING_EPSG}",
        "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
        "target_ct_count": len(cts),
        "poll_crosswalk_rows": len(poll_crosswalk),
        "district_crosswalk_rows": len(district_crosswalk),
        "ct_result_rows": len(ct_output),
        "candidate_result_rows": len(candidate_output),
        "excluded_or_unallocated_rows": len(exclusions),
        "vote_bearing_no_geometry_rows": len(no_geometry),
        "fully_allocated_no_geometry_rows": sum(
            row["fully_allocated"] for row in no_geometry_audit
        ),
        "primary_validation_failures": len(failed_primary),
        "all_primary_vote_validations_pass": not failed_primary,
        "official_row_turnout_rate": official_row_turnout,
        "interpolated_citizen_18plus_participation_rate": (
            citizen_18plus_participation
        ),
        "citizen_18plus_rate_closer_to_published_than_official_row_rate": (
            turnout_comparison[
                "citizen_18plus_rate_closer_to_published_than_official_row_rate"
            ]
        ),
    }
    write_json(
        validation_prefix.with_name(validation_prefix.name + "_summary.json"),
        summary,
    )
    return {
        "summary": summary,
        "audit": audit_rows,
        "validation": validation,
        "exclusions": exclusions,
        "no_geometry_audit": no_geometry_audit,
        "turnout_comparison": turnout_comparison,
    }


def _track_allocated(
    poll,
    weight,
    party_fields,
    allocated_totals,
    allocated_totals_by_district,
    allocated_totals_by_poll,
):
    district_id = poll["_district_id"]
    measures = {
        "total_votes": number(poll["number_of_votes"]),
        "electors": number(poll["number_of_electors"]),
        "valid_candidate_votes": number(poll["poll_total_candidate_votes"]),
    }
    for field in party_fields:
        measures[f"party:{field}"] = number(poll.get(field))
    for measure_id, value in measures.items():
        if value is None:
            continue
        allocated = value * weight
        allocated_totals[measure_id] += allocated
        allocated_totals_by_district[(district_id, measure_id)] += allocated
        allocated_totals_by_poll[(poll["poll_id"], measure_id)] += allocated
