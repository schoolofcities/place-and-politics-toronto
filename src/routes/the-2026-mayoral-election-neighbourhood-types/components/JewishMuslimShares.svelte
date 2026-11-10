<script>
	// Chow's and Bradford's 2026 vote share against the Jewish and Muslim shares of residents.
	// Drawn by the shared CorrelationIntervals chart.
	// Data: ../data/religion_correlation.json, built by analysis/election_2026/03_neighbourhood_types_page_data.ipynb
	// from Zack Taylor's religion_correlations_2026.csv (data/tor_elections_2023_2026).
	import CorrelationIntervals from './CorrelationIntervals.svelte';
	import { religionLegend, religionPanels, religionMeta, religionShares } from './data.js';
	const pct = (v) => `${Math.round(v)}%`;
</script>

<CorrelationIntervals title="Correlation between 2026 candidate vote share and % Jewish and % Muslim residents." legend={religionLegend} panels={religionPanels}>
	Pearson correlations across {religionMeta.tracts} census tracts, unweighted, between each candidate's share of valid election-day votes and the
	Jewish or Muslim share of residents, using the 2021 census. Bars are 95% confidence intervals, probably too narrow because neighbouring tracts
	are alike. Both groups are concentrated in a few tracts: the median tract is {pct(religionShares.Jewish.median_pct)} Jewish and
	{pct(religionShares.Muslim.median_pct)} Muslim, and {religionShares.Jewish.tracts_over_20pct} tracts are over 20% Jewish and {religionShares.Muslim.tracts_over_20pct}
	over 20% Muslim. Advance and mail-in votes are excluded. These describe places, not how any group voted.
</CorrelationIntervals>
