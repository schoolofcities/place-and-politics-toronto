// Chart data, pre-computed by analysis/election_2026/03_neighbourhood_types_page_data.ipynb into
// ../data (one file per graphic), so the page only draws.
import correlations from '../data/correlations_top.json';
import chinese from '../data/chinese_correlation.json';
import religion from '../data/religion_correlation.json';
import newVotesGroups from '../data/new_votes_groups.json';
import stripsData from '../data/chow_top_fifth_strips.json';
import winnerData from '../data/winner_correlations.json';
import newVotesGeo from '../data/new_votes_tracts.geojson?raw';
import newVotesMuniGeo from '../data/new_votes_municipalities.geojson?raw';
import { CHOW, BRADFORD, CHOW_TEXT, BRADFORD_TEXT, OLD_TORONTO, SUBURBS, GROUP_COLOURS } from './config.js';

// the ten strongest positive correlations with each candidate's 2026 vote share, strongest first
export const correlationMeta = correlations.meta;
export const correlationLists = [
	{ key: 'chow', name: correlations.chow.name, rows: correlations.chow.rows, colour: CHOW, text: CHOW_TEXT },
	{ key: 'bradford', name: correlations.bradford.name, rows: correlations.bradford.rows, colour: BRADFORD, text: BRADFORD_TEXT }
];

// ---- Dot-and-interval charts (CorrelationIntervals.svelte) --------------------------------
// Each chart is { legend, panels }: a panel has an optional heading and blocks (one per election),
// a block has rows (the series to compare), a row has r and its 95% interval.

// Chow's vote share against the Chinese visible-minority share of residents (2021 census), by
// election: Old Toronto and the suburbs.
export const chineseMeta = chinese.meta;
export const CHINESE_AREAS = ['Old Toronto', 'Suburbs'];
export const chineseLegend = [
	{ key: 'Old Toronto', label: 'Old Toronto', colour: OLD_TORONTO },
	{ key: 'Suburbs', label: 'Suburbs', colour: SUBURBS }
];
const chineseElections = [...new Set(chinese.rows.map((r) => r.election))];
export const chinesePanels = [
	{
		blocks: chineseElections.map((election) => ({
			label: String(election),
			rows: CHINESE_AREAS.map((area) => ({ key: area, ...chinese.rows.find((r) => r.election === election && r.area === area) }))
		}))
	}
];
export const chineseCitywide = chineseElections.map((e) => chinese.citywide.find((r) => r.election === e).r);
export const chineseTracts = Object.fromEntries(CHINESE_AREAS.map((a) => [a, chinese.rows.find((r) => r.area === a).n]));

// Chow's and Bradford's 2026 vote share against the Jewish and Muslim shares of residents (2021
// census): one block per religion, a row per candidate.
export const religionMeta = religion.meta;
export const religionShares = religion.shares;
export const religionLegend = [
	{ key: 'chow', label: 'Chow', colour: CHOW },
	{ key: 'bradford', label: 'Bradford', colour: BRADFORD }
];
export const religionPanels = [
	{
		blocks: ['Jewish', 'Muslim'].map((rel) => ({
			label: rel,
			rows: ['chow', 'bradford'].map((role) => ({ key: role, ...religion.rows.find((r) => r.religion === rel && r.role === role) }))
		}))
	}
];

// ---- Growing the pie: map and arrow chart ------------------------------------------------
// Tracts grouped by who led the Chow vs. main-opponent contest in 2023 and in 2026.
export const newVotes = newVotesGroups;
export const newVotesTracts = JSON.parse(newVotesGeo);
// the six former municipalities: outlines, and a label point each
export const newVotesMunicipalities = JSON.parse(newVotesMuniGeo);
export const groupOrder = ['held', 'flipped', 'trailing', 'other'];
export const groupByKey = Object.fromEntries(newVotesGroups.groups.map((g) => [g.key, { ...g, colour: GROUP_COLOURS[g.key] }]));

// ---- Strip plots: the top fifth of tracts by Chow's 2026 vote share (ChowTopFifthStrips.svelte) ----
export const strips = stripsData;

// ---- Correlations with the winner's vote share over time (CorrelationsOverTime.svelte) ----
export const winnerCorrelations = winnerData;
