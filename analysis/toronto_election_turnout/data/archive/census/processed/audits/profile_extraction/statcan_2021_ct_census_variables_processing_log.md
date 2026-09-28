# CT Census Variables Processing Log

Generated: 2026-07-09

## Source Files

- `data/toronto_election_turnout/census/raw/source_downloads/statcan_2021_ct_profile.zip`
- `data/toronto_election_turnout/census/raw/source_downloads/statcan_2021_ct_age_single_year_98100024-eng.zip`
- `data/toronto_election_turnout/census/processed/ct/statcan_2021_toronto_ct.geojson`
- `data/toronto_election_turnout/census/processed/ct/statcan_2021_ct_profile.csv`

No new datasets were downloaded. Existing official Statistics Canada source files were reused.

## Outputs

- `data/toronto_election_turnout/census/processed/ct/statcan_2021_ct_census_variables_master.csv`
- `data/toronto_election_turnout/census/processed/metadata/statcan_2021_ct_census_variables_dictionary.csv`
- `data/toronto_election_turnout/census/processed/audits/profile_extraction/statcan_2021_ct_census_variables_missing_report.csv`
- `data/toronto_election_turnout/census/processed/audits/profile_extraction/statcan_2021_ct_census_variables_qa_report.md`

## Row Counts

- Master rows: 622
- Interpolation-universe rows: 585

## Processing Summary

- Extracted selected official Census Profile characteristics by `DGUID`.
- Summed single-year ages for 5-17, 18-34, and 35-64 age bands.
- Used the official 65+ age aggregate from Table 98-10-0024-01.
- Preserved raw counts and official rates, then added 0-1 derived shares.
- Updated the project-level variable registry for collected Census variables.
