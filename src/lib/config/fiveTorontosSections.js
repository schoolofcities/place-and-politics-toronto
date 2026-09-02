// Per-section config for the /five-torontos story: which 5 voting rows to show (per the
// story brief) and which graphic to render, keyed by cluster slug (clusters_summary.json).
// This is the one place to edit if a section's voting rows or graphic need to change —
// nothing here depends on the page's own logic, so it's safe to tweak without touching
// +page.svelte. `graphic` is a plain switch key; `graphic: null` means no graphic at all
// (see the template in +page.svelte for how each value maps to a component).
export const SECTION_CONFIG = {
	"progressive-core": {
		votingSpecs: [
			{ label: "Municipal: Chow", election: "mayor_2023", field: "chow" },
			{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
			{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
			{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
			{ label: "Federal: NDP", election: "federal_2025", field: "ndp" },
		],
		graphic: "strip",
		stripVars: [
			{ key: "pct_renter", label: "% renter" },
			{ key: "pct_commute_car", label: "% commute by car" },
		],
	},
	"mobile-middle": {
		votingSpecs: [
			{ label: "Municipal: Chow", election: "mayor_2023", field: "chow" },
			{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
			{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
			{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
			{ label: "Federal: Liberal", election: "federal_2025", field: "liberal" },
		],
		graphic: null, // no graphic for this section
	},
	"civic-professionals": {
		votingSpecs: [
			{ label: "Municipal: Matlow", election: "mayor_2023", field: "matlow" },
			{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
			{ label: "Provincial: Liberal", election: "provincial_2025", field: "liberal" },
			{ label: "Federal: Liberal", election: "federal_2025", field: "liberal" },
			{ label: "Federal turnout", election: "federal_2025", field: "turnout" },
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
	"settled-conservatives": {
		votingSpecs: [
			{ label: "Municipal: Bailão", election: "mayor_2023", field: "bailao" },
			{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
			{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
			{ label: "Federal: Conservative", election: "federal_2025", field: "conservative" },
			{ label: "Federal: Liberal", election: "federal_2025", field: "liberal" },
		],
		graphic: "strip",
		stripVars: [
			{ key: "pct_renter", label: "% renter (lower = more homeowners)" },
			{ key: "avg_age", label: "Average age", domain: [30, 60], tickStep: 5 },
			{ key: "pct_commute_car", label: "% commute by car" },
		],
	},
	"working-suburbanites": {
		votingSpecs: [
			{ label: "Municipal: Others", election: "mayor_2023", field: "other" },
			{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
			{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
			{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
			{ label: "Federal: Conservative", election: "federal_2025", field: "conservative" },
		],
		graphic: "ternary",
		// [bottom-left, bottom-right, top] — see $lib/charts/TernaryProfilePlot.svelte.
		ternaryVars: [
			{ key: "pct_visible_minority", label: "% Visible Minority" },
			{ key: "income_median", label: "Median income" },
			{ key: "pct_bachelor_or_higher", label: "% Bachelor's degree+" },
		],
	},
};
