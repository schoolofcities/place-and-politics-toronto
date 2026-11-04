// Chart data, as exported by Zack Taylor's R scripts (tor_elections_2023_2026/output/plots); the
// margin bands are re-cut from his per-poll margins by ../data/prep_margins.py.
import { csvParse } from 'd3';
import marginsCsv from '../data/margins_by_election_bands.csv?raw';
import coreSuburbCsv from '../data/core_suburb_shares.csv?raw';
import municipalityCsv from '../data/shares_2026_by_municipality.csv?raw';

const groupBy = (rows, key) => {
	const out = new Map();
	for (const r of rows) {
		if (!out.has(r[key])) out.set(r[key], []);
		out.get(r[key]).push(r);
	}
	return out;
};

// one column per election: share of polls in each margin band, the widest margins at the bottom
export const MARGIN_BANDS = ['0–10%', '10–20%', '20–30%', '30%+'];
export const marginColumns = [...groupBy(csvParse(marginsCsv), 'election')].map(([election, rows]) => ({
	key: election,
	label: election,
	sublabel: `${(+rows[0].polls).toLocaleString('en-CA')} polls`,
	segments: [...MARGIN_BANDS].reverse().map((band) => ({ key: band, value: +rows.find((r) => r.band === band).share }))
}));

// one column per progressive candidate: their votes in the core, in the suburbs, and everyone else's
export const PARTS = ['City of Toronto', 'Suburbs', 'Votes for Other Candidates'];
export const WIN_YEARS = ['2003', '2006', '2023', '2026']; // the elections the progressive candidate won
// each one's official citywide share of all votes (advance and mail-in included), by year,
// from the series' src/data/candidate_info.json
export const CITYWIDE_SHARE = {
	1997: 0.4638, 2000: 0.0846, 2003: 0.4326, 2006: 0.5697, 2010: 0.3561,
	2014: 0.2315, 2018: 0.2359, 2022: 0.1785, 2023: 0.3717, 2026: 0.5416
};
export const coreSuburbColumns = [...groupBy(csvParse(coreSuburbCsv), 'year')].map(([year, rows]) => ({
	key: year,
	label: rows[0].candidate,
	sublabel: year,
	segments: PARTS.map((part) => ({ key: part, value: +rows.find((r) => r.part === part).share }))
}));

// 2026 vote share in each former municipality, in the draft's order
export const MUNICIPALITIES = ['City of Toronto', 'East York', 'York', 'Scarborough', 'Etobicoke', 'North York'];
export const CANDIDATES = ['Chow', 'Bradford', 'All others'];
const municipalityRows = csvParse(municipalityCsv);
export const municipalityGroups = MUNICIPALITIES.map((m) => ({
	key: m,
	total: +municipalityRows.find((r) => r.municipality === m).total, // election-day votes cast
	bars: CANDIDATES.map((c) => ({ key: c, value: +municipalityRows.find((r) => r.municipality === m && r.cand === c).share }))
}));
