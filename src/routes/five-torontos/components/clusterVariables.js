// Canonical catalogs of every socioeconomic/voting variable we have cluster-level data for,
// plus their value/delta formatting rules. ClusterSummaryTable.svelte shows a curated 5 per
// column by default (CURATED_SOCIOECONOMIC_KEYS below for socioeconomic; each section's own
// `votingSpecs`, from ../sections.js, for voting) and falls back to these full catalogs only
// once a reader expands a column to scroll through everything else.
//
// Every label below is a short, single-line abbreviation — deliberately the SAME text whether
// a variable is showing in the curated 5 or discovered later while browsing the full catalog,
// and short enough to never wrap in the table's narrow label column (which would otherwise
// make a row's height depend on which variable happened to land in it).

// Same 5 for every section (unlike voting, which sections.js tailors per cluster).
export const CURATED_SOCIOECONOMIC_KEYS = [
	"pct_renter",
	"pct_visible_minority",
	"pct_migrant_5yr",
	"pct_bachelor_or_higher",
	"pct_commute_car",
];

// Every demographic variable clusters_summary.json carries, in the order it's already computed
// (see `DEMO_VARS` in analysis/clustering_neighbourhoods/04_process_ct_to_cluster.ipynb).
export const ALL_SOCIOECONOMIC_KEYS = [
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

const SOCIOECONOMIC_LABELS = {
	population_density: "Pop. density",
	pct_age_65_over: "Age 65+",
	avg_age: "Avg. age",
	avg_household_size: "Household size",
	income_median_approx: "Median income",
	pct_renter: "Renters",
	pct_shelter_burdened_30plus: "Cost-burdened",
	pct_canadian_citizen: "Citizens",
	pct_visible_minority: "Visible minority",
	pct_migrant_5yr: "Moved <5 yrs",
	pct_bachelor_or_higher: "Bachelor's+",
	pct_commute_car: "Commute: car",
	pct_commute_transit: "Commute: transit",
	pct_commute_60plus_min: "Commute 60+min",
};

export function socioeconomicLabel(key) {
	return SOCIOECONOMIC_LABELS[key] ?? key;
}

// Every (election, field) pair with an actual vote-weighted value, excluding each election's
// "other" minor-party/candidate catch-all — not a meaningful single variable to compare
// cluster-to-cluster. 15 total: turnout + every named candidate/party on each ballot.
export const ALL_VOTING_SPECS = [
	{ election: "mayor_2023", field: "turnout" },
	{ election: "mayor_2023", field: "chow" },
	{ election: "mayor_2023", field: "bailao" },
	{ election: "mayor_2023", field: "saunders" },
	{ election: "mayor_2023", field: "matlow" },
	{ election: "provincial_2025", field: "turnout" },
	{ election: "provincial_2025", field: "pc" },
	{ election: "provincial_2025", field: "ndp" },
	{ election: "provincial_2025", field: "liberal" },
	{ election: "provincial_2025", field: "green" },
	{ election: "federal_2025", field: "turnout" },
	{ election: "federal_2025", field: "liberal" },
	{ election: "federal_2025", field: "conservative" },
	{ election: "federal_2025", field: "ndp" },
	{ election: "federal_2025", field: "green" },
];

// Abbreviated "Mun./Prov./Fed." prefixes so a candidate surname never has to share a line with
// the full "Municipal"/"Provincial"/"Federal" word. Covers each election's "other" catch-all
// too, since a couple of sections' curated 5 reference it even though it's excluded above from
// the full browsable catalog (not a meaningful variable to compare cluster-to-cluster on its own).
const VOTING_LABELS = {
	"mayor_2023.turnout": "Mun. turnout",
	"mayor_2023.chow": "Mun: Chow",
	"mayor_2023.bailao": "Mun: Bailão",
	"mayor_2023.saunders": "Mun: Saunders",
	"mayor_2023.matlow": "Mun: Matlow",
	"mayor_2023.other": "Mun: Others",
	"provincial_2025.turnout": "Prov. turnout",
	"provincial_2025.pc": "Prov: PC",
	"provincial_2025.ndp": "Prov: NDP",
	"provincial_2025.liberal": "Prov: Liberal",
	"provincial_2025.green": "Prov: Green",
	"provincial_2025.other": "Prov: Others",
	"federal_2025.turnout": "Fed. turnout",
	"federal_2025.liberal": "Fed: Liberal",
	"federal_2025.conservative": "Fed: Conservative",
	"federal_2025.ndp": "Fed: NDP",
	"federal_2025.green": "Fed: Green",
	"federal_2025.other": "Fed: Others",
};

export function votingVarKey({ election, field }) {
	return `${election}.${field}`;
}

export function votingVarLabel(spec) {
	return VOTING_LABELS[votingVarKey(spec)] ?? spec.field;
}

export function votingSpecsEqual(a, b) {
	return a.election === b.election && a.field === b.field;
}

// ── Value/delta formatting ────────────────────────────────────────────────────────
// Percentages (the overwhelming majority of variables, and every voting one) format as
// "pts" deltas; the 4 non-percentage socioeconomic variables each get their own unit.
const DOLLAR_KEYS = new Set(["income_median_approx"]);
const PLAIN_FORMATS = {
	avg_age: { digits: 0, suffix: " yrs" },
	avg_household_size: { digits: 1, suffix: "" },
	population_density: { digits: 0, suffix: "/km²", thousands: true },
};

export function formatSocioeconomicValue(key, value) {
	if (key.startsWith("pct_")) return `${value.toFixed(0)}%`;
	if (DOLLAR_KEYS.has(key)) return `$${Math.round(value / 1000)}k`;
	const plain = PLAIN_FORMATS[key];
	if (plain) {
		const n = Number(value.toFixed(plain.digits));
		return `${plain.thousands ? n.toLocaleString() : n}${plain.suffix}`;
	}
	return `${value}`;
}

export function formatSocioeconomicDelta(key, delta) {
	const sign = delta > 0 ? "+" : delta < 0 ? "−" : "";
	const abs = Math.abs(delta);
	if (key.startsWith("pct_")) {
		const rounded = Math.round(abs);
		return rounded === 0 ? "0 pts" : `${sign}${rounded} pts`;
	}
	if (DOLLAR_KEYS.has(key)) {
		const rounded = Math.round(abs / 1000);
		return rounded === 0 ? "$0k" : `${sign}$${rounded}k`;
	}
	const plain = PLAIN_FORMATS[key];
	if (plain) {
		const n = Number(abs.toFixed(plain.digits));
		// Drop the unit suffix in the delta itself (just the signed number) when it's a
		// thousands-formatted value like density — the row's own value/label already carries
		// the unit, and repeating a "/km²"-style suffix here is what was overflowing the
		// column's width.
		const text = plain.thousands ? n.toLocaleString() : `${n}${plain.suffix}`;
		return n === 0 ? text : `${sign}${text}`;
	}
	return `${sign}${abs}`;
}

export function formatVotingValue(value) {
	return `${value.toFixed(0)}%`;
}

export function formatVotingDelta(delta) {
	const rounded = Math.round(delta);
	return rounded === 0 ? "0 pts" : `${rounded > 0 ? "+" : "−"}${Math.abs(rounded)} pts`;
}
