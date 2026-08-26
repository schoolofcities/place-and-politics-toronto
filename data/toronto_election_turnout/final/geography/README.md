# Geography Data Dictionary

This folder supplies the canonical 585-CT join base. Use it to attach geometry
or basic population context to any other final dataset.

## Files and Formats

- `toronto_ct_2021_geography.csv` is the authoritative nonspatial table.
- `toronto_ct_2021_geography.geojson` contains the same properties plus CT
  polygon or multipolygon geometry in EPSG:4326.

Both files have one record per analytical 2021 Toronto CT. The primary key is
`ct_id`; it is complete and unique across all 585 records.

## Columns

| Column | Meaning |
| --- | --- |
| `ct_id` | Canonical CT join key, stored as text |
| `ctuid` | Statistics Canada Census Tract UID |
| `dguid` | Statistics Canada dissemination geography UID |
| `geo_name` | CT geographic name/label |
| `census_year` | Census reference year, 2021 |
| `land_area_km2` | CT land area in square kilometres |
| `population_total` | Total census population |
| `population_18plus` | Estimated population aged 18+ |
| `citizen_canadian_18plus_count` | Estimated Canadian-citizen population aged 18+ used by participation outcomes |

## Usage Notes

Treat all identifier columns as text. For a CSV that already has one row per
CT, join one-to-one on `ct_id`. For candidate results, join many-to-one from
candidate rows to this table. The geometry is intended for visualization and
spatial joins; analytical variables remain authoritative in their CSV files.
