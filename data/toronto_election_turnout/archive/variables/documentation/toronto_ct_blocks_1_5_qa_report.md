# Blocks 1-5 Modelling Variables QA Report

Generated: 2026-07-09

- Rows: 585
- Unique CT ids: 585
- Duplicate CT ids: 0
- Variables: 90
- Invalid share/margin/fragmentation values outside [0,1]: 1

## Notable Issues

- `block3_citizen_adult_share` retains the Task 1 documented CT `5350047.03` value slightly above 1 due to mixed 25% sample and 100% denominator sources.
- `block5_requests_311_per_1000` is populated as an area-weighted ward-to-CT allocation estimate because 311 raw files have ward/FSA fields but no point coordinates.
- `block5_social_housing_share` is populated from Census Profile characteristic 1491, `% of tenant households in subsidized housing`, converted to a 0-1 share.
- Committee of Adjustment since-2017 current file was unavailable from official endpoints; development variable uses the official Development Applications file only.
- GDAL reported non-fatal topology warnings for some TTS zone overlays; TTS shares were still produced for all 585 CTs and should be treated as approximate area-weighted values.
- Highest 311 per-capita estimate is CT `5350001.00` with `44907.657` requests per 1,000 residents; this reflects area-weighted ward allocation over a low-population CT and should be reviewed before modelling.

## Invalid Share Details

- 5350047.03 block3_citizen_adult_share=1.011299435
