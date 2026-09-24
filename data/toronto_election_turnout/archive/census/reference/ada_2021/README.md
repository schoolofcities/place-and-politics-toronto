# Toronto 2021 ADA Reference Files

These files were provided as reference inputs for exploring census variables:

- `toronto_ada_2021_profile.csv`
- `toronto_ada_2021_boundaries.gpkg`

The CSV is long-form profile data with:

- `GEO_NAME`
- `CHARACTERISTIC_ID`
- `CHARACTERISTIC_NAME`
- `CHARACTERISTIC_CODE`
- `C1_COUNT_TOTAL`
- `C10_RATE_TOTAL`

Observed structure:

- 279 ADA geographies.
- 161 characteristics per ADA.
- 44,919 rows total.
- The profile includes `citizen_canadian_18over`, which corresponds well to the interpolation algorithm's preferred `citizens_above_18` weighting concept.

The GeoPackage has:

- Layer: `toronto-ada`
- 279 ADA polygons.
- CRS: EPSG:3347, NAD83 / Statistics Canada Lambert.
- Fields: `ADAUID`, `DGUID`, `LANDAREA`, `PRUID`.

These ADA files are useful for checking which census variables exist and for coarse sensitivity checks. They are not the preferred ancillary population layer for poll-to-census-tract interpolation because the algorithm calls for a geography smaller than polls and census tracts where possible. For the main workflow, use DA-level geometry and DA-level population attributes.
