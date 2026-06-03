#!/usr/bin/env python3
"""Convert Zack Taylor-provided Toronto census-tract election data to CSV.

The source Stata file is not required to live in this repository. Pass the
input .dta path explicitly, and the script writes a full-column CSV plus a
small metadata text file for audit.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Toronto CT election Stata data to CSV."
    )
    parser.add_argument("input_dta", type=Path, help="Path to tor_electoral_ct2021_pct.dta")
    parser.add_argument("--output-csv", type=Path, default=None, help="Output CSV path")
    parser.add_argument("--metadata", type=Path, default=None, help="Output metadata text path")
    parser.add_argument("--schema-csv", type=Path, default=None, help="Output schema CSV path")
    parser.add_argument("--metadata-json", type=Path, default=None, help="Output metadata JSON path")
    args = parser.parse_args()

    if not args.input_dta.exists():
        raise FileNotFoundError(args.input_dta)

    repo_root = Path(__file__).resolve().parents[3]
    reference_dir = repo_root / "data" / "toronto_election_turnout" / "reference"
    reference_dir.mkdir(parents=True, exist_ok=True)

    output_csv = args.output_csv or reference_dir / "zack_taylor_tor_electoral_ct2021_pct.csv"
    metadata = args.metadata or reference_dir / "zack_taylor_tor_electoral_ct2021_pct_metadata.txt"
    schema_csv = args.schema_csv or reference_dir / "zack_taylor_tor_electoral_ct2021_pct_schema.csv"
    metadata_json = args.metadata_json or reference_dir / "zack_taylor_tor_electoral_ct2021_pct_metadata.json"

    reader = pd.io.stata.StataReader(args.input_dta)
    variable_labels = reader.variable_labels()
    value_labels = reader.value_labels()
    data_label = reader.data_label
    timestamp = reader.time_stamp
    df = pd.read_stata(args.input_dta, convert_categoricals=False)
    df.to_csv(output_csv, index=False, quoting=csv.QUOTE_NONNUMERIC, float_format="%.17g")

    schema_rows = []
    for column in df.columns:
        schema_rows.append(
            {
                "column": column,
                "pandas_dtype": str(df[column].dtype),
                "read_as": "string" if column == "ctuid2021" else str(df[column].dtype),
                "role": "2021 census tract identifier" if column == "ctuid2021" else "",
                "variable_label": variable_labels.get(column, ""),
            }
        )
    pd.DataFrame(schema_rows).to_csv(schema_csv, index=False)

    year_2023_cols = [c for c in df.columns if "2023" in c]
    lines = [
        "Source: Zack Taylor-provided Stata dataset tor_electoral_ct2021_pct.dta",
        "Description: Toronto election results between 1997 and 2023 apportioned to 2021 census tracts.",
        f"Rows: {len(df)}",
        f"Columns: {len(df.columns)}",
        f"Columns containing 2023: {len(year_2023_cols)}",
        f"Stata timestamp: {timestamp}",
        f"Stata data label: {data_label or '(blank)'}",
        f"Nonblank variable labels: {sum(bool(v) for v in variable_labels.values())}",
        f"Value label sets: {len(value_labels)}",
        "Identifier handling: read ctuid2021 as text/string, not numeric.",
    ]

    for column in ["citytotal2023", "voted2023"]:
        if column in df.columns:
            series = pd.to_numeric(df[column], errors="coerce")
            if column.startswith("city"):
                vals = [float(v) for v in series.dropna().unique()[:5]]
                lines.append(f"{column} unique values: {vals}")
            else:
                lines.append(f"{column} sum: {series.sum()}")

    metadata.write_text("\n".join(lines) + "\n", encoding="utf-8")
    metadata_json.write_text(
        json.dumps(
            {
                "source": "Zack Taylor-provided Stata dataset tor_electoral_ct2021_pct.dta",
                "description": "Toronto election results between 1997 and 2023 apportioned to 2021 census tracts.",
                "rows": len(df),
                "columns": len(df.columns),
                "columns_containing_2023": len(year_2023_cols),
                "stata_timestamp": str(timestamp),
                "stata_data_label": data_label,
                "nonblank_variable_labels": sum(bool(v) for v in variable_labels.values()),
                "value_label_sets": len(value_labels),
                "identifier_columns": ["ctuid2021"],
                "csv_read_notes": {
                    "ctuid2021": "Read as text/string to preserve the census tract identifier exactly."
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output_csv}")
    print(f"Wrote {metadata}")
    print(f"Wrote {schema_csv}")
    print(f"Wrote {metadata_json}")
    print(f"Rows={len(df)} Columns={len(df.columns)}")


if __name__ == "__main__":
    main()
