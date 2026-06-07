# Official Totals Audit

This audit compares the built datasets with row-level official source files. It does not force aggregate totals onto mapped polygons. Rows that official sources report without ordinary polling-division geometry are retained as no-geometry reporting buckets.

## Current Built Totals

Rows whose `vote_in_other_division` points to another division are excluded from aggregate totals to avoid double-counting electors that were already added to their target row.

`number_of_votes` is the turnout numerator where the official source supports it: ballots cast / number voted, not only valid candidate votes. Valid candidate votes are lower when rejected, unmarked, or declined ballots are reported separately.

| Dataset | Built votes | Built electors | Built turnout | Notes |
|---|---:|---:|---:|---|
| Municipal 2023 | 724,638 | 1,947,242 | 37.21% | Matches Toronto voter-statistics workbook row totals. |
| Provincial 2025 | 890,829 | 2,090,960 | 42.60% | Matches Elections Ontario official return rows for the selected Toronto ridings. |
| Federal 2025 | 1,318,564 | 2,028,280 | 65.01% | Matches Elections Canada Format 2 rows for the selected Toronto ridings, including advance and special-voting-rules group rows. |

## Valid Votes Versus Ballots Cast

| Dataset | Official valid candidate votes | Other ballots | Official ballots cast / number voted | Dataset `number_of_votes` |
|---|---:|---:|---:|---:|
| Provincial 2025 | 884,229 | 6,600 rejected, unmarked, or declined | 890,829 | 890,829 |
| Federal 2025 | 1,308,423 | 10,141 rejected | 1,318,564 | 1,318,564 |

The provincial screenshot figure of 881,787 does not match the Elections Ontario official return rows for the 25 selected Toronto provincial ridings. The official accepted-ballot total from the row-level source is 884,229; the turnout numerator is 890,829 when rejected, unmarked, and declined ballots are included.

The federal screenshot figure of about 1.45 million does not match Elections Canada official totals for the 24 selected Toronto federal ridings. The official Elections Canada total ballots cast for those ridings is 1,318,564. Reaching about 1.45 million would require a broader riding universe than the 24 Toronto federal ridings currently in this project.

### Municipal 2023 Turnout Reconciliation

The municipal dataset intentionally uses the final revised voters' list from Toronto's official voter-statistics workbook:

| Municipal measure | Value |
|---|---:|
| Initial `Total Electors` in the voter-statistics workbook | 1,888,082 |
| Additions to voters' list | 69,959 |
| Deletions from voters' list | 10,799 |
| Final `Total Eligible Electors` | 1,947,242 |
| `Number Voted` | 724,638 |
| Declined ballots | 299 |
| Dataset calculation: `Number Voted / Total Eligible Electors` | 37.21% |
| Workbook readme turnout definition: `(Number Voted + Declined Ballots) / Total Eligible Electors` | 37.23% |

The often-cited 38.5% municipal turnout figure uses an earlier denominator of about 1.88 million electors. It is not the turnout produced by Toronto's final revised list. Toronto's December 2023 supplementary report confirms that 1,947,242 eligible electors were on the final list and describes turnout as 37%.

The same supplementary report states that 725,333 ballots were cast, but its published vote-method breakdown totals 724,638: 28,143 mail-in, 129,745 advance, and 566,750 election-day ballots. The official poll-by-poll mayor workbook and voter-statistics workbook also both total 724,638. The unexplained 695-ballot difference is documented here but is not assigned to polling subdivisions because the published row-level sources do not identify those ballots by subdivision.

The Zack Taylor-provided census-tract dataset `tor_electoral_ct2021_pct.dta` reports `citytotal2023` as 561,428 and is election-day-only. This is not comparable to the all-method municipal total of 724,638. Compared with this project's ordinary election-day mapped rows, 564,267, the remaining difference is 2,839 votes. See `zack_taylor_ct_comparison.md` for details and official/institutional source links.

## Voting-Method Buckets

| Dataset | `vote_type` | Rows counted | Votes | Electors | No-geometry rows |
|---|---|---:|---:|---:|---:|
| Municipal 2023 | `election_day` | 1,445 | 564,267 | 1,939,801 | 0 |
| Municipal 2023 | `advance` | 50 | 129,648 | 0 | 50 |
| Municipal 2023 | `mail_in` | 25 | 28,117 | 0 | 25 |
| Municipal 2023 | `special` | 25 | 2,606 | 7,441 | 25 |
| Provincial 2025 | `election_day` | 1,389 | 692,459 | 2,090,882 | 3 |
| Provincial 2025 | `advance` | 127 | 198,370 | 78 | 127 |
| Federal 2025 | `election_day` | 4,276 | 769,958 | 2,009,652 | 3 |
| Federal 2025 | `advance` | 363 | 463,817 | 0 | 363 |
| Federal 2025 | `special` | 48 | 84,789 | 18,628 | 48 |

## Why Totals Differ From Polygon-Only Maps

The ordinary mapped polygons do not include every official voting method. Advance, mail-in, and special-voting-rules rows often have valid votes but no ordinary polling-division geometry. Those rows should count in election totals but should not be assigned to a polygon unless the source identifies a specific geographic division.

Municipal turnout now uses Toronto's voter-statistics row-level electors, not the geometry file's `VOTER_COUNT` field. The geometry file remains the polygon source only.

Federal now builds from Elections Canada Format 2. That source confirms ordinary federal poll names are generally `Toronto`, provides explicit combined/void flags, and records `0` electors for advance and some special-voting-rules reporting buckets. Those zero-elector reporting buckets are retained for vote totals but treated as having no supported turnout denominator.

Federal special-voting-rules rows (`SVR Group 1/RÉS Groupe 1` and `SVR Group 2/RÉS Groupe 2`) are retained as `special` no-geometry rows. This closes the vote-count gap against Elections Canada without attaching those votes to ordinary polygons.
