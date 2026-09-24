# Blocks 1-5 Methodology Report

The master table is one row per 2021 Census Tract in the 585-CT interpolation universe.

Blocks 1-3 come from the Task 1 Statistics Canada CT Census master.
Block 4 comes from the existing population-weighted CT election interpolation outputs.
Block 5 combines Census, TTS 2022, and Toronto Open Data raw files collected in Task 2.

Accessibility variables use Euclidean CT-centroid distance because a routable pedestrian/transit network was not collected in Task 2. A 1200 metre threshold is included as a transparent 15-minute walking proxy, assuming roughly 80 metres per minute.

TTS variables are area-weighted from TTS zones to CT polygons. No CT/TTS population crosswalk exists in the repository, so this is preferred over unweighted assignment but should be treated as an approximation.
GDAL reported non-fatal topology warnings for a small number of TTS zone intersections, indicating invalid source geometries. The pipeline skips failed/zero-area intersections implicitly and records the TTS outputs as approximate.

All point and geometry transforms use traditional GIS axis order for EPSG coordinate systems to preserve longitude-latitude interpretation of Toronto Open Data coordinates.

311 requests are aggregated from official 2023, 2024, and 2025 annual files by municipal ward. Because the raw annual files do not include coordinates, ward totals are allocated to CTs by CT-ward intersection-area share using the existing municipal ward-to-CT crosswalk from the interpolation pipeline. The resulting CT count is divided by Census population_total and multiplied by 1000.

Social housing is measured with the 2021 Census Profile characteristic `% of tenant households in subsidized housing`, converted from percent to a 0-1 share. The denominator is tenant households, not all households or occupied dwellings.
