# 2021 Census Inputs for Poll-to-CT Interpolation

This folder stores census geography and reference inputs for population-weighted interpolation from election polling divisions to 2021 census tracts.

The `source_downloads` folder also contains
`statcan_2021_age_single_year_98100023-eng.zip`, the official Statistics Canada
table `98-10-0023-01`. It supports an exact calculation of all-person
population aged 18+ from published single-year age counts.

It also contains `statcan_2021_ct_age_single_year_98100024-eng.zip`, official
table `98-10-0024-01`, used for the corresponding CT-level calculation and
suppression audit.

It also contains annual Statistics Canada estimate tables used only for
temporal diagnostics in the interpolation audit:

- `statcan_annual_csd_population_17100155-eng.zip`
  - Table `17-10-0155-01`, Toronto CSD total population estimates.
- `statcan_annual_cd_age_17100152-eng.zip`
  - Table `17-10-0152-01`, Toronto CD age estimates.

These annual tables do not publish Canadian citizens aged 18 and over at DA,
CT, Toronto CSD, or Toronto CD geography. They are therefore not used to
replace or scale the production `citizen_canadian_18over` denominator.

## Stored Files

### Official Statistics Canada Geometry

All official geometry files use NAD83 / Statistics Canada Lambert, EPSG:3347.

- `statcan_2021_toronto_csd.gpkg`
  - Layer: `toronto_csd_2021`
  - One feature: Toronto census subdivision, `CSDUID = 3520005`.

- `statcan_2021_ct_toronto_clipped.gpkg`
  - Layer: `census_tracts_2021_toronto`
  - 622 census tract features clipped to the Toronto CSD boundary.

- `statcan_2021_da_toronto_clipped.gpkg`
  - Layer: `dissemination_areas_2021_toronto`
  - 3,807 dissemination area features clipped to the Toronto CSD boundary.
  - For Census Profile extraction, use the 3,743 DA records whose `DAUID`
    starts with `3520`, which is the Toronto CD/CSD geography prefix.

### Official Statistics Canada Census Profile Attributes

Extracted Toronto-only Census Profile outputs are stored in:

`data/toronto_election_turnout/census/processed/profile_2021/`

- `statcan_2021_da_citizens_18plus.csv`
  - 3,743 Toronto DA rows.
  - Characteristic: `1525`, `Canadian citizens aged 18 and over`.
  - Total count: 1,869,930.
  - Missing/suppressed rows: 16.

- `statcan_2021_ct_citizens_18plus.csv`
  - 622 CT rows intersecting the Toronto clipping boundary.
  - Characteristic: `1525`, `Canadian citizens aged 18 and over`.
  - The 585 CTs linked to Toronto DAs total 1,870,085.
  - The all-row sum of 1,999,260 is not a Toronto city total.
  - Missing/suppressed rows: 2.

- `statcan_2021_citizens_18plus_extraction_metadata.json`
  - Source URLs, extraction timestamp, counts, totals, and notes.

The DA total closely matches the official Toronto CSD row in the same Census
Profile source: 1,870,055 Canadian citizens aged 18 and over. The 125-person
difference is consistent with rounding/suppression in small-area 25% sample
estimates. The Toronto-linked CT sum is within 30 people of the city value.
The DA table should remain the primary ancillary-weight input
for poll-to-CT interpolation.

### Source Downloads

`source_downloads/` contains the raw GeoJSON pulled from the official Statistics Canada ArcGIS REST service before clipping:

- `statcan_2021_toronto_csd_3520005.geojson`
- `statcan_2021_ct_toronto_bbox.geojson`
- `statcan_2021_da_toronto_bbox.geojson`

The CT and DA source files are bounding-box pulls around Toronto, so they include some records outside the city before clipping. The clipped GeoPackages should be used for Toronto analysis.

The large official Census Profile source zips used for the attribute extract are
not stored in Git. They can be re-downloaded with
`analysis/toronto_election_turnout/census/scripts/extract_statcan_census_profile_citizens_18plus.py`.
The source downloads are:

- DA, Ontario-only comprehensive CSV with confidence intervals:
  `https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=006CI_Ontario`
- CT, CMA/CA/CT comprehensive CSV with confidence intervals:
  `https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=007CI`

## Official Source URLs

- Statistics Canada 2021 cartographic boundary service:
  `https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer`
- CSD layer:
  `https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/9`
- CT layer:
  `https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/11`
- DA layer:
  `https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Cartographic_boundary_files/MapServer/12`
- Census Profile download page for DA/CT attributes:
  `https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm`
- Annual CSD total population estimates, table 17-10-0155-01:
  `https://www150.statcan.gc.ca/n1/en/tbl/csv/17100155-eng.zip`
- Annual CD age estimates, table 17-10-0152-01:
  `https://www150.statcan.gc.ca/n1/en/tbl/csv/17100152-eng.zip`

## Attribute Data Status

The geometry files contain identifiers and land area only. The preferred
DA-level ancillary attribute has now been extracted from the official Census
Profile source.

The interpolation algorithm needs one ancillary weight at DA level. Preferred hierarchy:

1. Canadian citizens aged 18 and over / citizens above 18.
2. Voting-age population.
3. Adult population.
4. Total population.
5. Dwelling count.

The attached ADA reference profile has `citizen_canadian_18over`, but ADA geography is coarser than DA and is not the preferred ancillary layer.

Do not treat ADA data as a replacement for DA data unless explicitly running a lower-resolution sensitivity test.
