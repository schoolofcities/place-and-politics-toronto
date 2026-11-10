// Chart data, pre-computed by analysis/election_2026/03_neighbourhood_types_page_data.ipynb into
// ../data (one file per graphic), so the page only draws.
import correlations from '../data/correlations_top.json';
import chinese from '../data/chinese_correlation.json';
import religion from '../data/religion_correlation.json';
import groupShares from '../data/group_vote_shares.json';
import newVotesGroups from '../data/new_votes_groups.json';
import stripsData from '../data/chow_top_fifth_strips.json';
import winnerData from '../data/winner_correlations.json';
import heroMapsData from '../data/hero_maps.json';
import newVotesGeo from '../data/new_votes_tracts.geojson?raw';
import newVotesMuniGeo from '../data/new_votes_municipalities.geojson?raw';
import muniLinesGeo from '../data/municipality_lines.geojson?raw';
import wardLinesGeo from '../data/ward_lines.geojson?raw';
import { CHOW, BRADFORD, CHOW_TEXT, BRADFORD_TEXT, GROUP_COLOURS } from './config.js';

// the ten strongest positive correlations with each candidate's 2026 vote share, strongest first
export const correlationMeta = correlations.meta;
export const correlationLists = [
	{ key: 'chow', name: correlations.chow.name, rows: correlations.chow.rows, colour: CHOW, text: CHOW_TEXT },
	{ key: 'bradford', name: correlations.bradford.name, rows: correlations.bradford.rows, colour: BRADFORD, text: BRADFORD_TEXT }
];

// Chow's vote share against the Chinese visible-minority share of residents (2021 census): a
// row each for Old Toronto and the suburbs, a value per election (quoted in ChineseShares.svelte's note).
// The file's all-tract values are left out: pooled, the two areas' different levels of support for
// Chow cancel out the pattern within each, so they read as a contradiction.
export const chineseYears = [...new Set(chinese.rows.map((r) => r.election))];
export const chineseRows = ['Old Toronto', 'Suburbs'].map((area) => ({
	area,
	values: chineseYears.map((y) => chinese.rows.find((r) => r.area === area && r.election === y).r)
}));

// Chow's and Bradford's 2026 vote share against the Jewish and Muslim shares of residents (2021
// census): a row per group, a value per candidate (quoted in ReligionShares.svelte's note).
export const religionMeta = religion.meta;
export const religionShares = religion.shares;
export const religionCandidates = [
	{ key: 'chow', name: 'Chow' },
	{ key: 'bradford', name: 'Bradford' }
];
export const religionRows = ['Jewish', 'Muslim'].map((rel) => ({
	group: rel,
	values: religionCandidates.map((c) => religion.rows.find((r) => r.religion === rel && r.role === c.key).r)
}));

// Candidates' vote shares in tracts where a group is more than 20% of residents, against all other
// tracts (../data/prep_group_vote_shares.py): ReligionShares.svelte and ChineseShares.svelte.
export const groupThreshold = groupShares.meta.threshold;
export const religionShareRows = groupShares.religion;
export const chineseShareRows = groupShares.chinese;

// ---- Growing the pie: map and arrow chart ------------------------------------------------
// Tracts grouped by who led the Chow vs. main-opponent contest in 2023 and in 2026.
export const newVotes = newVotesGroups;
export const newVotesTracts = JSON.parse(newVotesGeo);
// the six former municipalities: outlines, and a label point each
export const newVotesMunicipalities = JSON.parse(newVotesMuniGeo);
// the boundaries between them, and between the 25 wards, each drawn once (../data/prep_boundary_lines.py)
export const municipalityLines = JSON.parse(muniLinesGeo);
export const wardLines = JSON.parse(wardLinesGeo);
export const groupOrder = ['held', 'flipped', 'trailing', 'other'];
export const groupByKey = Object.fromEntries(newVotesGroups.groups.map((g) => [g.key, { ...g, colour: GROUP_COLOURS[g.key] }]));

// ---- Strip plots: the top fifth of tracts by Chow's 2026 vote share (ChowTopFifthStrips.svelte) ----
export const strips = stripsData;

// ---- Correlations with the winner's vote share over time (CorrelationsOverTime.svelte) ----
export const winnerCorrelations = winnerData;

// ---- Small-multiple maps at the top: the vote and the traits that track it (NeighbourhoodMaps.svelte) ----
export const heroMaps = heroMapsData;
