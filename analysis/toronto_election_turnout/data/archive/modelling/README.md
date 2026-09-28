# CT Modelling Data

`processed/toronto_ct_modelling_curated.csv` is the recommended analysis-ready one-row-per-CT modelling table. It contains only the selected modelling variables and outcomes.

`processed/toronto_ct_modelling_master.csv` is the verbose provenance table with raw counts, source status fields, and StatCan characteristic IDs. Use it for auditing, not as the default modelling input.

The CT universe follows the 585 CTs used by the interpolation outputs. Use `ct_id` as the join key.
