import csv
import json
import math
from pathlib import Path

# Pearson correlations between every pair of candidates' CT vote shares, for the Part 4 tool.
# Reads the candidates (and their CT columns) from candidate_info.csv and the vote shares from
# ctWithResults.geo.json; writes candidate_correlations.csv, which convert.py turns into JSON.
# Only CTs with values for every candidate are used (same as R's cor(use = "complete.obs")).

HERE = Path(__file__).resolve().parent
OUT = HERE.parent

with open(HERE / "candidate_info.csv") as csvfile:
    candidates = [(row["main"], row["ctid"]) for row in csv.DictReader(csvfile)]

with open(OUT / "ctWithResults.geo.json") as f:
    tracts = [feature["properties"] for feature in json.load(f)["features"]]

tracts = [t for t in tracts if all(t.get(ctid) is not None for _, ctid in candidates)]
print(len(tracts), "CTs with complete data")

columns = {name: [t[ctid] for t in tracts] for name, ctid in candidates}


def pearson(x, y):
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


names = [name for name, _ in candidates]

with open(HERE / "candidate_correlations.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["x"] + names)
    for a in names:
        # the diagonal is written as exactly 1, which convert.py relies on
        writer.writerow([a] + [1 if a == b else float("%.15g" % pearson(columns[a], columns[b])) for b in names])
