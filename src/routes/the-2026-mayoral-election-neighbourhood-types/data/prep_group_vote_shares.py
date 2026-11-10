"""Build group_vote_shares.json: candidates' vote shares in tracts where a group is more than THRESHOLD of
residents, compared with all other tracts (components/ReligionShares.svelte and ChineseShares.svelte).

    religion  Chow's and Bradford's 2026 shares in tracts over THRESHOLD Jewish, and over THRESHOLD Muslim
    chinese   Chow's share in tracts over THRESHOLD Chinese (visible minority), in 2014, 2023 and 2026,
              within Old Toronto and within the suburbs

Shares pool the tracts' votes (each tract's share weighted by its election-day votes cast), so they are
the share of all election-day votes cast in those tracts. Census shares are from the 2021 census.

Sources: the tract shares and votes cast in data/election_results/2026-results-clean/tor_electoral_ct2021_pct.dta
(Zack Taylor's), and, saved as source/group_shares_2021.csv, the 2021 Jewish, Muslim and Chinese shares
from the social-geography page's census.parquet. Given that file's path, the CSV is first re-extracted
(this needs pyarrow or duckdb to read it).

usage: python prep_group_vote_shares.py [/path/to/census.parquet]
"""

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
THRESHOLD = 20  # percent of residents
CSV = HERE / "source" / "group_shares_2021.csv"
DTA = REPO / "data/election_results/2026-results-clean/tor_electoral_ct2021_pct.dta"
TRACTS = REPO / "src/routes/social-geography-and-the-mayoral-vote/data/tracts.geojson"
CHOW = {2014: "pctchow2014", 2023: "pctchow_olivia2023", 2026: "pctchow_olivia2026"}

if len(sys.argv) > 1:
    import duckdb
    CSV.parent.mkdir(exist_ok=True)
    duckdb.sql(f"copy (select ct, rlgnjewi_pct, rlgnmusl_pct, vminvisichin_pct from '{sys.argv[1]}' where year = 2021) to '{CSV}' (header)")

shares = pd.read_csv(CSV, dtype={"ct": str}).set_index("ct") * 100
elec = pd.read_stata(DTA).assign(ct=lambda d: d.ctuid2021.astype(str)).set_index("ct")
old = {f["properties"]["ct"]: f["properties"]["oldcity"] == "Toronto" for f in json.load(open(TRACTS))["features"]}
d = shares.join(elec, how="inner")
d["area"] = ["Old Toronto" if old.get(ct) else "Suburbs" for ct in d.index]


def pooled(sub, col, year):
    v = sub[f"voted{year}"]
    return round(float(100 * (sub[col] * v).sum() / v.sum()), 1)


def compare(sub, mask, cols, year):
    """the shares in the tracts over the threshold and in all the others, with tract and vote counts"""
    out = {}
    for name, part in (("over", sub[mask]), ("other", sub[~mask])):
        out[name] = {"tracts": len(part), "votes": int(part[f"voted{year}"].sum()),
                     **{k: pooled(part, c, year) for k, c in cols.items()}}
    return out


religion = []
r26 = d.dropna(subset=["rlgnjewi_pct", "rlgnmusl_pct", "pctchow_olivia2026", "pctbradford_brad2026"])
for group, col in (("Jewish", "rlgnjewi_pct"), ("Muslim", "rlgnmusl_pct")):
    religion.append({"group": group, **compare(r26, r26[col] > THRESHOLD, {"chow": "pctchow_olivia2026", "bradford": "pctbradford_brad2026"}, 2026)})

chinese = []
for year, col in CHOW.items():
    c = d.dropna(subset=["vminvisichin_pct", col])
    for area in ("Old Toronto", "Suburbs"):
        a = c[c.area == area]
        chinese.append({"year": year, "area": area, **compare(a, a.vminvisichin_pct > THRESHOLD, {"chow": col}, year)})

out = {"meta": {"threshold": THRESHOLD, "census_year": 2021,
                "measure": "Each candidate's share of election-day votes cast in the tracts where the group is more than the threshold of residents, and in all other tracts (votes pooled)",
                "built_by": "src/routes/the-2026-mayoral-election-neighbourhood-types/data/prep_group_vote_shares.py"},
       "religion": religion, "chinese": chinese}
json.dump(out, open(HERE / "group_vote_shares.json", "w"), ensure_ascii=False, indent=1)
for r in religion:
    print(r["group"], r["over"], "| other", r["other"])
for r in chinese:
    print(r["year"], r["area"], r["over"], "| other", r["other"])
