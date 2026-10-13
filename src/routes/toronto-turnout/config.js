// Presentation settings for the /toronto-turnout story: palettes, class breaks and the
// provisional reader-facing labels. Everything data-derived (field mapping, model figures,
// loadings) comes from $data/toronto-turnout, written by
// analysis/toronto_election_turnout/09_final_synthesis.ipynb (section 10).

import { piecewise, interpolateRgb, quantize, color } from 'd3';

// ---- Turnout (sequential) ---------------------------------------------------------
// The four views share one set of fixed classes so switching between them is a like-for-like
// comparison: federal turnout is visibly higher than municipal, rather than each map being
// stretched to its own range. Palette: the site's blue "vote" ramp (see
// routes/social-geography-and-the-mayoral-vote/mapper.js), sampled at 7 classes.
const VOTE_COLOURS = ['#e8ebf5', '#b9c3e3', '#8698cc', '#4f64ad', '#1e3765'];
export const TURNOUT_BREAKS = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8];
export const TURNOUT_COLOURS = quantize(piecewise(interpolateRgb, VOTE_COLOURS), TURNOUT_BREAKS.length + 1);

export const TURNOUT_VIEWS = [
	{ key: 'mean', field: 'mean_turnout', label: 'Mean turnout', short: 'Mean', note: 'Average of the three election rates' },
	{ key: 'municipal', field: 'municipal_turnout', label: '2023 mayoral', short: '2023 mayoral', note: '2023 mayoral by-election' },
	{ key: 'provincial', field: 'provincial_turnout', label: '2025 provincial', short: '2025 provincial', note: '2025 Ontario general election' },
	{ key: 'federal', field: 'federal_turnout', label: '2025 federal', short: '2025 federal', note: '2025 federal general election' }
];

// ---- Component 1 (diverging, centred on zero) --------------------------------------
// Rust against teal: the site's colour-blind-safe pair from the bivariate map in
// routes/social-geography-and-the-mayoral-vote/mapper.js, with a pale neutral at zero.
// Deliberately a different hue family from the blue turnout ramp.
const RUST = '#c8643c';
const TEAL = '#2f8a9e';
const NEUTRAL = '#f1efea';
export const COMPONENT_BREAKS = [-6, -3, -1, 1, 3, 6];
export const COMPONENT_COLOURS = quantize(
	piecewise(interpolateRgb, [
		color(RUST).darker(0.7).formatHex(),
		RUST,
		NEUTRAL,
		TEAL,
		color(TEAL).darker(0.7).formatHex()
	]),
	COMPONENT_BREAKS.length + 1
);
export const COMPONENT_LOW_COLOUR = RUST;
export const COMPONENT_HIGH_COLOUR = TEAL;

// Provisional interface labels for the two ends of Component 1, from the loadings in
// 09_final_synthesis.ipynb (section 4). Editorial wording can change here in one place.
export const COMPONENT_SIDES = {
	low: {
		label: 'More working class, immigrant-heavy, commuters',
		long: 'more working-class, immigrant-heavy, commuter neighbourhoods'
	},
	high: {
		label: 'More professional, central, flexible workers',
		long: 'more professional, central neighbourhoods with flexible workers'
	}
};

// ---- Explorer predictors (single-hue sequential, like the site's census maps) ------
export const CENSUS_COLOURS = ['#e6f2ef', '#b3dbd2', '#6fbcae', '#2e8f80', '#0d534d'];

// ---- Shared ------------------------------------------------------------------------
export const NA_COLOUR = '#e6e6e1';
export const HOVER_COLOUR = '#F1C500'; // --brandYellow
