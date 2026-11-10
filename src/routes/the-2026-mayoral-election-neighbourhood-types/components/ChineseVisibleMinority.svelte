<script>
	// Chow's vote share against the Chinese share of residents, 2014, 2023 and 2026, in Old
	// Toronto and the suburbs. Drawn by the shared CorrelationIntervals chart.
	// Data: ../data/chinese_correlation.json, built by analysis/election_2026/03_neighbourhood_types_page_data.ipynb
	// from Zack Taylor's chow_chinese_correlation_by_area.csv (data/tor_elections_2023_2026).
	import CorrelationIntervals from './CorrelationIntervals.svelte';
	import { chineseLegend, chinesePanels, chineseCitywide, chineseTracts } from './data.js';
</script>

<CorrelationIntervals title="Correlation between Chow neighbourhood vote share and % Chinese residents" legend={chineseLegend} panels={chinesePanels}>
	Pearson correlations across census tracts ({chineseTracts['Old Toronto']} in Old Toronto, {chineseTracts.Suburbs} in the suburbs), unweighted,
	between Chow's share of valid election-day votes and the Chinese (visible minority) share of residents, using the 2021 census for all three
	elections. Bars are 95% confidence intervals, probably too narrow because neighbouring tracts are alike. Across all tracts the correlations are
	{chineseCitywide.map((r) => r.toFixed(2)).join(', ')}. The suburbs are all tracts outside the former City of Toronto. Advance and mail-in votes
	are excluded. These describe places, not how any group voted.
</CorrelationIntervals>
