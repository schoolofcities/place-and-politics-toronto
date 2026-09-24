# CT Census Variables QA Report

Generated: 2026-07-09

## Coverage

- Master CT rows: 622
- Unique `ct_id` values: 622
- Duplicate `ct_id` values: 0
- Interpolation CT ids found across election outputs: 585
- Interpolation CT ids missing from master: 0
- Master CTs outside interpolation universe: 37

## Integrity

- Share fields checked: 24
- Invalid share values outside [0, 1]: 1
- Negative count/total values: 0
- Population total mismatches between profile and age cube greater than 5 persons: 7
- Maximum absolute profile-vs-age population difference: 10.0

## Notes

- The master retains 622 CTs from the existing Toronto CT geometry file.
- `contains_toronto_da=true` and `in_interpolation_universe=true` identify the 585 CTs used by the interpolation pipeline.
- Two interpolation-universe CTs have suppressed or unavailable citizen-adult denominators in the existing Census profile products.
- Small profile-vs-age population differences are expected from published table rounding.
- Citizen-adult share can exceed 1 in rare cases because the numerator is a 25% sample citizenship estimate and the denominator is a 100% age-table count.

Invalid shares:

- 5350047.03 citizen_adult_share=1.011299435
