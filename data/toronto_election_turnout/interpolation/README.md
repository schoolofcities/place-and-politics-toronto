# Interpolation Data

Generated poll-to-census-tract interpolation products are stored in
`processed/`.

Rebuild them with:

```bash
cd analysis/toronto_election_turnout/interpolation
python3 run_interpolation.py
```

See the interpolation module README for methodology, assumptions, output
schemas, and quality flags.
