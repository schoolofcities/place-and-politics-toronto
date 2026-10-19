// Every variable ClusterSummaryTable.svelte shows, grouped as its table groups them, plus their
// value formatting. Socioeconomic row labels come from clusters_metadata.json's
// `variable_labels`; election rows use the short labels below, since each election's group
// heading already names the election.

// Every demographic variable clusters_summary.json carries, in the order it's already computed
// (see `DEMO_VARS` in analysis/clustering_neighbourhoods/04_process_ct_to_cluster.ipynb).
export const SOCIOECONOMIC_KEYS = [
	"population_density",
	"pct_age_65_over",
	"avg_age",
	"avg_household_size",
	"income_median_approx",
	"pct_renter",
	"pct_shelter_burdened_30plus",
	"pct_canadian_citizen",
	"pct_visible_minority",
	"pct_migrant_5yr",
	"pct_bachelor_or_higher",
	"pct_commute_car",
	"pct_commute_transit",
	"pct_commute_60plus_min",
];

// Labels used instead of clusters_metadata.json's `variable_labels` for these keys.
export const SOCIOECONOMIC_LABEL_OVERRIDES = {
	pct_visible_minority: "Visible minority", // the census's own term
};

// Every election and every vote-share field with a vote-weighted value: each named
// candidate/party and each election's "other" catch-all. Municipal -> provincial -> federal.
// Each election's turnout (field "turnout") goes in a separate turnout table instead.
export const ELECTIONS = [
	{
		key: "mayor_2023",
		heading: "2023 mayoral\nby-election", // \n = line break in the table heading
		fields: [
			{ field: "chow", label: "Olivia Chow" },
			{ field: "bailao", label: "Ana Bailão" },
			{ field: "saunders", label: "Mark Saunders" },
			{ field: "matlow", label: "Josh Matlow" },
			{ field: "other", label: "Other candidates" },
		],
	},
	{
		key: "provincial_2025",
		heading: "2025 provincial\nelection",
		fields: [
			{ field: "pc", label: "PC" },
			{ field: "ndp", label: "NDP" },
			{ field: "liberal", label: "Liberal" },
			{ field: "green", label: "Green" },
			{ field: "other", label: "Other parties" },
		],
	},
	{
		key: "federal_2025",
		heading: "2025 federal\nelection",
		fields: [
			{ field: "liberal", label: "Liberal" },
			{ field: "conservative", label: "Conservative" },
			{ field: "ndp", label: "NDP" },
			{ field: "green", label: "Green" },
			{ field: "other", label: "Other parties" },
		],
	},
];

// ── Value formatting ──────────────────────────────────────────────────────────────
// Percentages (the overwhelming majority of variables, and every voting one) format as whole
// percents; the 4 non-percentage socioeconomic variables each get their own unit. Density has
// no suffix because its label already says "(per km²)".
const DOLLAR_KEYS = new Set(["income_median_approx"]);
const PLAIN_FORMATS = {
	avg_age: { digits: 0, suffix: "" },
	avg_household_size: { digits: 1, suffix: "" },
	population_density: { digits: 0, suffix: "", thousands: true },
};

export function formatSocioeconomicValue(key, value) {
	if (key.startsWith("pct_")) return `${value.toFixed(0)}%`;
	if (DOLLAR_KEYS.has(key)) return `$${Math.round(value / 1000)}k`;
	const plain = PLAIN_FORMATS[key];
	if (plain) {
		// toFixed keeps a trailing zero (household size "2.0", not "2")
		const text = plain.thousands ? Number(value.toFixed(plain.digits)).toLocaleString() : value.toFixed(plain.digits);
		return `${text}${plain.suffix}`;
	}
	return `${value}`;
}

export function formatVotingValue(value) {
	return `${value.toFixed(0)}%`;
}
