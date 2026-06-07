# Zack Taylor CT Dataset Comparison

This note records the comparison between this project's polling-division turnout files and the Toronto election dataset provided by Zack Taylor as `tor_electoral_ct2021_pct.dta`.

## Status in This Repository

The checked repository already contains related 2021 census-tract election outputs used by the Place and Politics site, including:

- `src/data/ctWithResults2023.geo.json`
- `src/data/ctWithResults.geo.json`
- `src/data/ctWithResults.csv`

The specific Stata file `tor_electoral_ct2021_pct.dta` was not found in the repository. It is therefore referenced here as a Zack Taylor-provided dataset rather than treated as an original project source file.

The conversion script is stored at:

- `analysis/toronto_election_turnout/census/scripts/convert_zack_taylor_stata.py`

Run it with the source `.dta` path:

```bash
python analysis/toronto_election_turnout/census/scripts/convert_zack_taylor_stata.py /path/to/tor_electoral_ct2021_pct.dta
```

The script preserves all rows and columns in CSV form and writes sidecar metadata under `data/toronto_election_turnout/census/reference/zack_taylor_ct2021/`.

Conversion fidelity check:

- Stata source shape: 585 rows and 1,129 columns.
- CSV output shape: 585 rows and 1,129 columns.
- Column order matches the Stata source.
- No variable labels, value labels, or data label are present in the Stata file.
- The Stata timestamp is preserved in metadata.
- `ctuid2021` is a text identifier and should be read as string/text. The schema file records this because plain CSV readers may otherwise infer it as numeric.

## Method Difference

Zack's dataset is apportioned to 2021 census tracts. It is not the same geography as this project's polling-division and reporting-bucket files.

The provided description states that the census-tract file does not include advance-poll votes and should be read as election-day geographically apportionable votes. Point polls are assigned to their enclosing census tract. Voting-subdivision catchment-area votes are decomposed into dissemination blocks, weighted by block population, and summed to census tracts.

This project keeps official polling-division rows and special reporting buckets as published. It does not apportion votes to census tracts or assign no-geometry advance, mail-in, or special votes to ordinary polygons unless the source identifies a supported relationship.

## Municipal 2023 Comparison

The direct overlap is the 2023 Toronto mayoral by-election.

| Measure | Value |
|---|---:|
| This project, all official municipal reporting buckets | 724,638 |
| This project, ordinary election-day mapped rows | 564,267 |
| Zack Taylor CT dataset, `citytotal2023` | 561,428 |
| Difference between this project's ordinary election-day mapped rows and Zack CT city total | 2,839 |

The large difference between 724,638 and 561,428 is expected because Zack's CT dataset excludes advance, mail-in, and special reporting buckets, while this project retains them.

The remaining 2,839-vote difference is small, about 0.5 percent of this project's ordinary election-day mapped total. Based on the source descriptions and the proportional spread across candidate totals, the likely causes are non-apportioned or filtered election-day records in the CT workflow. This project does not force that difference into polling divisions because no official source identifies a supported subdivision-level allocation for it.

The Zack file's tract-level `voted2023` sum is 561,430, two votes above `citytotal2023`, which is consistent with a small apportionment or rounding artifact. Candidate-specific tract-level `a_*2023` sums may also differ slightly from citywide candidate totals, so citywide fields should be used for aggregate comparison.

## Official Municipal 2023 Source Reconciliation

Toronto's official row-level candidate and voter-statistics workbooks support 724,638 as the assignable row-level total used in this project.

There are, however, multiple public totals in circulation:

- Toronto's certification release and supplementary report state that 725,333 ballots were cast.
- The official candidate declaration and row-level workbooks sum to 724,638.
- The supplementary report's published method totals also sum to 724,638, not 725,333.
- The existing Place and Politics 2023 article text cites 722,877, which appears to be an older public-facing figure; the current chart data in the repository uses 724,638.

This project records the 695-ballot difference between 725,333 and 724,638, but does not assign those ballots to subdivisions because the published row-level sources do not identify where they belong.

## Trustworthy Sources

Official and institutional sources used for this reconciliation:

- City of Toronto, official by-election results open-data package: https://open.toronto.ca/dataset/elections-official-by-election-results/
- City of Toronto, official voting-subdivision geometry: https://open.toronto.ca/dataset/elections-subdivisions/
- City of Toronto, Clerk certification release for the 2023 mayoral by-election: https://www.toronto.ca/news/toronto-city-clerk-certifies-by-election-for-mayor-results-and-declares-olivia-chow-as-mayor-elect/
- City of Toronto, Declaration of Results for the 2023 Toronto By-Election for Mayor: https://www.toronto.ca/wp-content/uploads/2023/06/900e-Declaration-of-Results-for-the-2023-Toronto-By-Election-for-Mayor.pdf
- City of Toronto, 2023 Mayor By-Election Supplementary Report: https://www.toronto.ca/wp-content/uploads/2023/12/8bb4-Final-for-web-2023-Mayor-ByElection-Report.pdf
- Place and Politics in Toronto repository and article context: https://github.com/schoolofcities/place-and-politics-toronto and https://schoolofcities.github.io/place-and-politics-toronto/mapping-the-2023-mayoral-election

## Interpretation

These datasets are compatible but not interchangeable:

- Use this project's files when the analysis needs official polling-division/reporting-bucket turnout for municipal 2023, provincial 2025, or federal 2025.
- Use Zack's CT-apportioned file when the analysis needs historical municipal election results on a stable 2021 census-tract geography.
- Do not compare Zack's election-day-only CT total with this project's all-method municipal total without first filtering this project to `vote_type = election_day` and considering the remaining small apportionment/source-extract gap.
