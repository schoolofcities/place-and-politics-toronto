"""GDAL/OGR geometry loading and population-weight construction."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path

from osgeo import ogr, osr

from config import ANCILLARY_WEIGHT_FIELD, WORKING_EPSG
from io_utils import boolean, number


ogr.UseExceptions()


@dataclass
class AreaUnit:
    unit_id: str
    ct_id: str
    geometry: ogr.Geometry
    area: float
    citizen_weight: float
    citizen_suppressed: bool


@dataclass
class TargetCT:
    ct_id: str
    geometry: ogr.Geometry
    citizen_canadian_18over: float | None
    citizen_canadian_18over_status: str


class SpatialGrid:
    """Simple envelope grid to avoid full scans for every intersection."""

    def __init__(self, records, geometry_getter, cell_size=2000.0):
        self.records = records
        self.geometry_getter = geometry_getter
        self.cell_size = cell_size
        self.cells = defaultdict(set)
        for index, record in enumerate(records):
            for cell in self._cells_for(geometry_getter(record).GetEnvelope()):
                self.cells[cell].add(index)

    def _cells_for(self, envelope):
        min_x, max_x, min_y, max_y = envelope
        x0 = math.floor(min_x / self.cell_size)
        x1 = math.floor(max_x / self.cell_size)
        y0 = math.floor(min_y / self.cell_size)
        y1 = math.floor(max_y / self.cell_size)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                yield x, y

    def query(self, geometry):
        indexes = set()
        for cell in self._cells_for(geometry.GetEnvelope()):
            indexes.update(self.cells.get(cell, ()))
        return (self.records[index] for index in indexes)


def _transformer(source_epsg=4326, target_epsg=WORKING_EPSG):
    source = osr.SpatialReference()
    source.ImportFromEPSG(source_epsg)
    source.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    target = osr.SpatialReference()
    target.ImportFromEPSG(target_epsg)
    target.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return osr.CoordinateTransformation(source, target)


TRANSFORM_TO_WORKING = _transformer()


def _polygonal_parts(geometry):
    flat_type = ogr.GT_Flatten(geometry.GetGeometryType())
    if flat_type == ogr.wkbPolygon:
        return [geometry.Clone()]
    if flat_type == ogr.wkbMultiPolygon:
        return [geometry.GetGeometryRef(i).Clone() for i in range(geometry.GetGeometryCount())]
    if flat_type == ogr.wkbGeometryCollection:
        parts = []
        for i in range(geometry.GetGeometryCount()):
            parts.extend(_polygonal_parts(geometry.GetGeometryRef(i)))
        return parts
    return []


def make_valid_polygonal(geometry, transform=True) -> ogr.Geometry | None:
    if geometry is None or geometry.IsEmpty():
        return None
    geometry = geometry.Clone()
    if transform:
        geometry.Transform(TRANSFORM_TO_WORKING)
    if not geometry.IsValid():
        geometry = geometry.MakeValid()
    parts = _polygonal_parts(geometry)
    if not parts:
        return None
    output = ogr.Geometry(ogr.wkbMultiPolygon)
    for part in parts:
        if not part.IsEmpty() and part.GetArea() > 0:
            output.AddGeometry(part)
    return output if output.GetGeometryCount() else None


def geometry_from_json(text: str) -> ogr.Geometry | None:
    if not text or not text.strip():
        return None
    return make_valid_polygonal(ogr.CreateGeometryFromJson(text))


def _open_layer(path: Path):
    dataset = ogr.Open(str(path), 0)
    if dataset is None:
        raise RuntimeError(f"Could not open {path}")
    return dataset, dataset.GetLayer(0)


def load_census(ct_path: Path, da_path: Path):
    ct_dataset, ct_layer = _open_layer(ct_path)
    cts = []
    for feature in ct_layer:
        if not boolean(feature.GetField("contains_toronto_da")):
            continue
        geometry = make_valid_polygonal(feature.GetGeometryRef())
        if geometry is None:
            continue
        cts.append(
            TargetCT(
                str(feature.GetField("geo_id")),
                geometry,
                number(feature.GetField(ANCILLARY_WEIGHT_FIELD)),
                str(feature.GetField("value_status") or ""),
            )
        )

    da_dataset, da_layer = _open_layer(da_path)
    das = []
    suppressed_rows = []
    for feature in da_layer:
        geometry = make_valid_polygonal(feature.GetGeometryRef())
        if geometry is None:
            continue
        citizen_weight = number(feature.GetField(ANCILLARY_WEIGHT_FIELD))
        citizen_status = str(feature.GetField("value_status") or "")
        unit = AreaUnit(
            unit_id=str(feature.GetField("geo_id")),
            ct_id=str(feature.GetField("ct_id")),
            geometry=geometry,
            area=geometry.GetArea(),
            citizen_weight=citizen_weight or 0.0,
            citizen_suppressed=citizen_weight is None,
        )
        das.append(unit)
        if unit.citizen_suppressed:
            suppressed_rows.append(
                {
                    "da_id": unit.unit_id,
                    "ct_id": unit.ct_id,
                    "value_status": citizen_status,
                    "ancillary_weight_variable": ANCILLARY_WEIGHT_FIELD,
                    "ancillary_weight_status": "suppressed_treated_as_zero",
                }
            )

    del ct_layer, ct_dataset, da_layer, da_dataset
    return cts, das, suppressed_rows


def load_district_geometries(config, required_ids):
    dataset, layer = _open_layer(config.district_geojson)
    districts = {}
    invalid_before_repair = 0
    for feature in layer:
        district_id = config.normalize_district_id(
            feature.GetField(config.district_id_field)
        )
        if district_id not in required_ids:
            continue
        original = feature.GetGeometryRef()
        if original is not None and not original.IsValid():
            invalid_before_repair += 1
        geometry = make_valid_polygonal(original)
        if geometry is not None:
            districts[district_id] = geometry
    del layer, dataset
    return districts, invalid_before_repair


def intersect_area(left, right) -> tuple[ogr.Geometry | None, float]:
    if not left.Intersects(right):
        return None, 0.0
    piece = left.Intersection(right)
    if piece is None or piece.IsEmpty():
        return None, 0.0
    area = piece.GetArea()
    if area <= 0:
        return None, 0.0
    return piece, area


def build_population_weights(
    source_id: str,
    source_geometry: ogr.Geometry,
    ct_grid: SpatialGrid,
    da_grid: SpatialGrid,
    weight_variable: str,
    allow_area_fallback: bool = True,
):
    """Return normalized source-to-CT population weights and source diagnostics."""
    overlaps = []
    total_population_weight = 0.0
    total_ct_area = 0.0
    total_da_piece_area = 0.0
    suppressed_da_piece_area = 0.0
    suppressed_ids = set()

    for ct in ct_grid.query(source_geometry):
        ct_piece, ct_area = intersect_area(source_geometry, ct.geometry)
        if ct_piece is None:
            continue
        total_ct_area += ct_area
        population_weight = 0.0
        ct_suppressed_ids = set()
        ct_da_piece_area = 0.0
        ct_suppressed_area = 0.0
        for da in da_grid.query(ct_piece):
            if da.ct_id != ct.ct_id:
                continue
            da_piece, da_piece_area = intersect_area(ct_piece, da.geometry)
            if da_piece is None:
                continue
            ct_da_piece_area += da_piece_area
            if weight_variable == ANCILLARY_WEIGHT_FIELD:
                da_weight = da.citizen_weight
                da_suppressed = da.citizen_suppressed
            else:
                raise ValueError(f"Unsupported weight variable: {weight_variable}")
            allocated_weight = (
                da_weight * da_piece_area / da.area if da.area > 0 else 0.0
            )
            population_weight += allocated_weight
            if da_suppressed:
                ct_suppressed_ids.add(da.unit_id)
                ct_suppressed_area += da_piece_area
        total_population_weight += population_weight
        total_da_piece_area += ct_da_piece_area
        suppressed_da_piece_area += ct_suppressed_area
        suppressed_ids.update(ct_suppressed_ids)
        overlaps.append(
            {
                "source_id": source_id,
                "ct_id": ct.ct_id,
                "population_weight": population_weight,
                "intersection_area_m2": ct_area,
                "suppressed_da_count_ct_piece": len(ct_suppressed_ids),
            }
        )

    zero_population_weight = total_population_weight <= 0
    denominator = (
        total_ct_area
        if zero_population_weight and allow_area_fallback
        else total_population_weight
    )
    for row in overlaps:
        numerator = (
            row["intersection_area_m2"]
            if zero_population_weight and allow_area_fallback
            else row["population_weight"]
        )
        row["allocation_weight"] = numerator / denominator if denominator else 0.0

    suppressed_area_share = (
        suppressed_da_piece_area / total_da_piece_area
        if total_da_piece_area > 0
        else 0.0
    )
    diagnostics = {
        "zero_population_weight": zero_population_weight,
        "fallback_area_weight_used": (
            zero_population_weight and allow_area_fallback and bool(overlaps)
        ),
        "suppressed_da_count": len(suppressed_ids),
        "suppressed_da_area_share": suppressed_area_share,
        "excluded_weight_area_share": suppressed_area_share,
        "total_population_weight": total_population_weight,
        "ct_overlap_count": len(overlaps),
    }
    return overlaps, diagnostics
