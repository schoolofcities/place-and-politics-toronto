// Presentation settings for the /toronto-turnout story: palettes, class breaks and the
// provisional reader-facing labels. Everything data-derived (field mapping, model figures,
// loadings) comes from $data/toronto-turnout, written by
// analysis/toronto_election_turnout/09_final_synthesis.ipynb (section 10).

import { piecewise, interpolateRgb, quantize, schemeRdYlBu } from 'd3';

// ---- Turnout (sequential) ---------------------------------------------------------
// The four views share one set of fixed classes so switching between them is a like-for-like
// comparison: federal turnout is visibly higher than municipal, rather than each map being
// stretched to its own range. Five classes, on a ramp through the site's brand blues (pale tint ->
// --brandLightBlue -> --brandMedBlue -> --brandDarkBlue) so neighbouring classes differ in both
// lightness and hue and stay distinguishable on the map.
const TURNOUT_RAMP = ['#e3ebf5', '#6FC7EA', '#007FA3', '#1E3765'];
export const TURNOUT_BREAKS = [0.35, 0.5, 0.65, 0.8];
export const TURNOUT_COLOURS = quantize(piecewise(interpolateRgb, TURNOUT_RAMP), TURNOUT_BREAKS.length + 1);

// label: the map's buttons; short: the hover readout (and the map's screen-reader name)
export const TURNOUT_VIEWS = [
	{ key: 'mean', field: 'mean_turnout', label: 'Mean voter turnout', short: 'Mean turnout', subtitle: 'Average of the 2023 mayoral, 2025 provincial and 2025 federal election rates' },
	{ key: 'municipal', field: 'municipal_turnout', label: '2023 mayoral election turnout', short: '2023 mayoral', subtitle: '2023 mayoral by-election' },
	{ key: 'provincial', field: 'provincial_turnout', label: '2025 provincial election turnout', short: '2025 provincial', subtitle: '2025 Ontario general election' },
	{ key: 'federal', field: 'federal_turnout', label: '2025 federal election turnout', short: '2025 federal', subtitle: '2025 federal general election' }
];

// ---- Component 1 (diverging, centred on zero) --------------------------------------
// ColorBrewer's red -> yellow -> blue, 7 classes: a pale-yellow middle that cannot be mistaken
// for the hatched "no data" fill, and ends that are clearly different from the blue sequential
// turnout ramp. Low scores are red, high scores blue.
export const COMPONENT_BREAKS = [-6, -3, -1, 1, 3, 6];
export const COMPONENT_COLOURS = schemeRdYlBu[COMPONENT_BREAKS.length + 1];
export const COMPONENT_LOW_COLOUR = COMPONENT_COLOURS[0];
export const COMPONENT_HIGH_COLOUR = COMPONENT_COLOURS[COMPONENT_COLOURS.length - 1];

// Provisional interface labels for the two ends of Component 1, from the loadings in
// 09_final_synthesis.ipynb (section 4). Editorial wording can change here in one place.
export const COMPONENT_SIDES = {
	// wording follows the paragraph describing the two sides in +page.svelte
	low: {
		label: 'More trades and service jobs, long commutes, immigrant families',
		long: 'neighbourhoods with more trades and service jobs, long commutes and immigrant families'
	},
	high: {
		label: 'More degrees and professional jobs, working from home',
		long: 'neighbourhoods with more university degrees, professional jobs and working from home'
	}
};

// ---- Explorer predictors (single-hue sequential, like the site's census maps) ------
export const CENSUS_COLOURS = ['#e6f2ef', '#b3dbd2', '#6fbcae', '#2e8f80', '#0d534d'];

// ---- Shared ------------------------------------------------------------------------
export const NA_COLOUR = '#e6e6e1'; // under the hatching; also the legend's "no data" base
export const HATCH_COLOUR = '#c4c4bc'; // the hatch stripes on tracts with no data
export const HOVER_COLOUR = '#F1C500'; // --brandYellow
