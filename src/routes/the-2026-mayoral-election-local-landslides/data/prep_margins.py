"""Build margins_by_election_bands.csv for the polls-by-winning-margin chart.

Re-bands Zack Taylor's per-poll margins (source/margins_by_election_polls.csv, from
plot_margins_by_election.R) into 10-point bands, the same as the poll map's. Bands are
right-open, as in his script (cut at 0, 10, 20, 30), so a margin of 9.9 points is in 0-10% and
an exact tie is in the first band. Polls with no votes are already left out of the source.

usage: python prep_margins.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
BANDS = ["0–10%", "10–20%", "20–30%", "30%+"]

polls = pd.read_csv(HERE / "source/margins_by_election_polls.csv")
polls["band"] = pd.cut(polls.margin, [0, 10, 20, 30, float("inf")], right=False, labels=BANDS)
assert polls.band.notna().all()

counts = polls.groupby(["election", "band"], observed=False).size().rename("n").reset_index()
counts["polls"] = counts.groupby("election").n.transform("sum")
counts["share"] = counts.n / counts.polls
counts.to_csv(HERE / "margins_by_election_bands.csv", index=False)

print(counts.assign(pct=(100 * counts.share).round(1)).pivot(index="election", columns="band", values="pct"))
