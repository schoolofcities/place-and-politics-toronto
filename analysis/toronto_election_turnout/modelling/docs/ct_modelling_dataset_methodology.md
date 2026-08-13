# CT Modelling Dataset Methodology

Rows: 585 CTs, matching the interpolation target universe.

The primary dependent variable for Model E is
`mean_participation_citizen_18plus`, the mean of municipal, provincial,
and federal CT participation rates calculated with
`citizen_canadian_18over` as the denominator.

Official elector turnout fields are retained separately as
`*_turnout_electors`. These are not forced to match Census population
variables.

Blocks 1-3 are extracted from the official Statistics Canada 2021 CT
Census Profile and the official 2021 CT single-year age table. Block 4
competitiveness variables are computed from the existing CT interpolated
candidate/party vote outputs. Block 5 variables are populated where a
Census Profile variable is directly available, and non-Census service
variables are listed in the missing-variable checklist for future
official Open Toronto acquisition.

Competitiveness formulas:

- share = candidate or party votes / total valid candidate or party votes
- top-two margin = top share - second share
- effective number = 1 / sum(share_i^2)
- fragmentation = 1 - sum(share_i^2)

Downloaded official Census Profile source:

- https://www12-2021.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=007
