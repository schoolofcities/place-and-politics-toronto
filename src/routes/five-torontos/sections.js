// Per-section config for the /five-torontos story: which 5 voting rows to show (per the
// story brief) and which graphic to render, keyed by cluster slug (clusters_summary.json).
// This is the one place to edit if a section's voting rows or graphic need to change —
// nothing here depends on the page's own logic, so it's safe to tweak without touching
// +page.svelte. `graphic` is a plain switch key; `graphic: null` means no graphic at all
// (see the template in +page.svelte for how each value maps to a component). Voting specs are
// just an (election, field) pair — their display label is the shared, single-line abbreviation
// in ClusterSummaryTable.svelte's VOTING_LABELS, not defined per section.
export const SECTION_CONFIG = {
	"progressive-core": {
		votingSpecs: [
			{ election: "mayor_2023", field: "chow" },
			{ election: "mayor_2023", field: "turnout" },
			{ election: "provincial_2025", field: "ndp" },
			{ election: "provincial_2025", field: "pc" },
			{ election: "federal_2025", field: "ndp" },
		],
		graphic: "strip",
		stripVars: [
			{ key: "pct_renter", label: "% renter" },
			{ key: "pct_commute_car", label: "% commute by car" },
		],
	},
	"soft-left-belt": {
		votingSpecs: [
			{ election: "mayor_2023", field: "chow" },
			{ election: "mayor_2023", field: "turnout" },
			{ election: "provincial_2025", field: "ndp" },
			{ election: "provincial_2025", field: "pc" },
			{ election: "federal_2025", field: "liberal" },
		],
		graphic: null, // no graphic for this section
	},
	"civic-liberals": {
		votingSpecs: [
			{ election: "mayor_2023", field: "matlow" },
			{ election: "mayor_2023", field: "turnout" },
			{ election: "provincial_2025", field: "liberal" },
			{ election: "federal_2025", field: "liberal" },
			{ election: "federal_2025", field: "turnout" },
		],
		graphic: "scatter",
		scatter: {
			xKey: "income_median",
			yKey: "pct_bachelor_or_higher",
			xLabel: "Median income ($)",
			yLabel: "Bachelor's degree+ (%)",
			xFormat: (v) => `$${Math.round(v / 1000)}k`,
			yFormat: (v) => `${v.toFixed(0)}%`,
		},
	},
	"suburban-conservatives": {
		votingSpecs: [
			{ election: "mayor_2023", field: "bailao" },
			{ election: "provincial_2025", field: "pc" },
			{ election: "provincial_2025", field: "ndp" },
			{ election: "federal_2025", field: "conservative" },
			{ election: "federal_2025", field: "liberal" },
		],
		graphic: "strip",
		stripVars: [
			{ key: "pct_renter", label: "% renter (lower = more homeowners)" },
			{ key: "avg_age", label: "Average age", domain: [30, 60], tickStep: 5 },
			{ key: "pct_commute_car", label: "% commute by car" },
		],
	},
	"low-turnout-suburbanites": {
		votingSpecs: [
			{ election: "mayor_2023", field: "other" },
			{ election: "mayor_2023", field: "turnout" },
			{ election: "provincial_2025", field: "ndp" },
			{ election: "provincial_2025", field: "pc" },
			{ election: "federal_2025", field: "conservative" },
		],
		graphic: "strip",
		stripVars: [
			{ key: "pct_visible_minority", label: "% visible minority" },
			{ key: "income_median", label: "Median income", domain: [20000, 90000], tickStep: 20000, format: (v) => `$${Math.round(v / 1000)}k` },
			{ key: "pct_bachelor_or_higher", label: "% bachelor's degree+" },
		],
	},
};
