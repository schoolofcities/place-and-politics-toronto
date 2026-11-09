// Colours shared by the page's graphics, the same as the 2026 local-landslides page's: Chow purple
// and Bradford green, toned down to sit with the softer palettes elsewhere in the series.
// The *_TEXT colours are the darkest step of each ramp, for headings (about 5:1 against the page).
export const CHOW = '#a678b8';
export const BRADFORD = '#70a669';
export const CHOW_TEXT = '#87569c';
export const BRADFORD_TEXT = '#4e854e';

// Old Toronto and the suburbs, in the same two blues as the local-landslides post's "Where each
// progressive candidate's votes came from" (suburbs the darker one).
export const OLD_TORONTO = '#5b97c4';
export const SUBURBS = '#1f5f8b';

// "Growing the pie": the four kinds of tract, by who led the Chow vs. main-opponent contest in 2023 and 2026.
// Used by the map and the arrow chart, so a colour means the same thing in both.
export const GROUP_COLOURS = {
	held: '#6f3f8c', // Chow led both times: a deep Chow purple
	flipped: '#b9b2e6', // flipped to Chow: a pale blue-purple
	trailing: BRADFORD, // her opponent led both times
	other: '#cfcfcf' // anything else (6 tracts)
};
