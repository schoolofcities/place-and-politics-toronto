# Release Metadata Dictionary

This folder makes the final release self-describing and auditable. It contains
no analytical observations; its files describe datasets, variables, QA, source
lineage, and release integrity.

## `dataset_catalog.csv`

One row per analysis-ready dataset. Fields record the dataset name, row grain,
primary key, purpose, and relative CSV/GeoJSON paths. Use this as the
machine-readable version of the top-level folder guide.

## `variable_dictionary.csv`

One row per distinct released variable (358 rows). `datasets` lists every table
containing the variable. `variable_group`, `description`, `units`, `numerator`,
`denominator`, and `source` define meaning and provenance;
`maximum_missing_count` and `data_types` summarize its released representation.
This is the authoritative column-level dictionary when a subfolder README
describes a family rather than enumerating every variable.

## `qa_summary.csv`

One row per analysis-ready dataset. It records rows, columns, duplicate primary
keys, missing `ct_id` values, unique CT count, and pass/fail status. Candidate
results use their composite key; CT-wide tables use `ct_id`.

## `source_manifest.csv`

One row per upstream source artifact consumed by the final release. Fields are
the repository-relative `source_file`, SHA-256 checksum, and byte size. Use it
to verify source lineage or detect an upstream artifact change.

## `release_manifest.json`

Release-level metadata plus one checksum/size record for every delivered file.
It records the canonical CT count, join key, geometry CRS, build script, and a
`files` array containing relative paths, SHA-256 checksums, and byte sizes. The
manifest does not checksum itself.

## Integrity Workflow

Use `dataset_catalog.csv` to locate a table, `variable_dictionary.csv` to
interpret its fields, `qa_summary.csv` to confirm structural checks, and the
two manifests to verify exact source and release files. Checksums establish file
identity; they do not by themselves establish substantive validity.
