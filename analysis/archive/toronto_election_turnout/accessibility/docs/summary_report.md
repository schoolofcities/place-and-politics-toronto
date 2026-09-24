# Polling Station Accessibility Audit Summary

## Main Finding

Municipal 2023 polling-station coordinates were found and recorded for
all mapped municipal polling-subdivision rows. Provincial 2025 and
Federal 2025 remain unresolved as complete distance-analysis datasets.
Provincial 2025 has a partial official-source path through Elections
Ontario proposed voting-location CSV exports, Open Toronto Address
Points, and exact official-return label recoveries. These sources still
do not cover every mapped 2025 polling row. Federal 2025 still lacks a
bulk official source tying mapped poll divisions to polling-place coordinates.

## Election-Level Readiness

| Election | Rows | Mapped rows | Candidate location labels | Distance-model-ready rows | Area/turnout Pearson | Area/turnout Spearman |
|---|---:|---:|---:|---:|---:|---:|
| municipal_2023_mayor | 1545 | 1445 | 1445 | 1351 | -0.1701 | -0.2833 |
| provincial_2025 | 1532 | 1388 | 1338 | 1180 | -0.2091 | -0.4256 |
| federal_2025 | 5069 | 4273 | 0 | 0 | -0.0684 | -0.2138 |

## Interpretation

- Municipal 2023 is ready for an exploratory distance-vs-turnout pass.
  The official Open Toronto `Elections Voting Locations` point table
  has 1,445 records for 2023 and matches all 1,445 mapped municipal
  polling-subdivision rows by ward/subdivision code.
- Provincial 2025 has the strongest starting point because the raw official
  return includes `VotingPlaceAddressOrLocation`. Elections Ontario
  proposed voting-location exports provide names and addresses for many
  Toronto locations, and Open Toronto Address Points can geocode those
  addresses. Where proposed-location matching fails, exact Open Toronto
  place-name or civic-address matches to official-return labels are used.
  Fuzzy proposed-location candidates remain review leads only.
- Federal 2025 is the weakest starting point: the processed ordinary poll
  label is usually not a polling-place address, so an additional official
  or archived source is needed.
- Poll area can be computed now and is included as a possible accessibility
  proxy. It should not be treated as a substitute for polling-station
  distance because large polling areas may reflect land-use/geography,
  apartment density, institutional voting, or district design choices.

## Possible Covariates Worth Adding Later

- density or apartment share
- age composition
- income or deprivation measures
- transit access
- car ownership, if available
- advance/mail/special voting availability
- riding or ward fixed effects

## Next Step

Proceed with municipal and partial provincial exploratory analysis.
For federal analysis, locate an official polling-place coordinate table
or a defensible address source before estimating distances.
