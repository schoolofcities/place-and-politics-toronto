# Zack Taylor CT Reference Data

This folder contains the Zack Taylor-provided Toronto census-tract election
dataset converted from Stata:

- `zack_taylor_tor_electoral_ct2021_pct.csv`
- `zack_taylor_tor_electoral_ct2021_pct_schema.csv`
- `zack_taylor_tor_electoral_ct2021_pct_metadata.json`
- `zack_taylor_tor_electoral_ct2021_pct_metadata.txt`

These files are a reference comparison for previously apportioned CT election
results. They are not inputs to the production poll/district-to-CT
interpolation.

Rebuild from the original Stata file with:

```bash
python3 analysis/toronto_election_turnout/census/scripts/convert_zack_taylor_stata.py /path/to/tor_electoral_ct2021_pct.dta
```
