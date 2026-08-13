# Non-Census Raw Dataset Collection QA

Generated: 2026-07-09

## Scope

Raw acquisition only. No variables were derived, no observations were aggregated, and no spatial joins were performed.

## Summary

- Inventory records: 46
- Downloaded files in this run: 0
- Existing files reused: 45
- Local raw file records present: 45
- Missing or failed records: 1
- CSV files readable: 10
- ZIP files readable: 5

## Task 1 Census QA Summary Carried Forward

- CT Census master rows: 622.
- Interpolation-universe CT rows: 585.
- Duplicate CT ids: 0.
- Interpolation CT ids missing from Census master: 0.
- Invalid Census share values documented: 1 (`citizen_adult_share` for CT `5350047.03`).

## Known Limitations

- Toronto CKAN package metadata often reports `License not specified`; the inventory notes the Toronto Open Data licence context.
- The Toronto Open Data `parks` and shelter location packages are marked as legacy/current-as-published in metadata; future processing should assess whether newer park/shelter alternatives are needed.
- Federal 2025 polling-place coordinates remain unavailable in the existing election/accessibility raw data.
- TTS files were collected from the supervisor-recommended School of Cities GitHub repository; no TTS indicator was computed.

## Missing/Failed Records

- Committee of Adjustment Applications / committee-of-adjustments-applications-since-2017.csv: failed Collected current since-2017 file and 2023 closed applications file. No filtering or aggregation. Download error: <HTTPError 500: 'Internal Server Error'>
