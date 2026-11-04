// Colours shared by the page's graphics.

// Chow purple (after the 2023 post's) and Bradford green (after his campaign), both toned down
// to sit with the softer palettes elsewhere in the series. Bins are the winner's lead in
// points: under 10, 10 to under 20, 20 to under 30, 30 or more.
export const MARGIN_BINS = [0.1, 0.2, 0.3];
export const MARGIN_TICKS = [0, 10, 20, 30]; // legend labels, at the step edges (the last step is open)
export const CHOW_RAMP = ['#e9d6ee', '#c9a6d5', '#a678b8', '#87569c'];
export const BRADFORD_RAMP = ['#d9ebd4', '#a9d0a1', '#70a669', '#4e854e'];
export const TIE = '#9a9a9a';

export const CHOW = '#a678b8';
export const BRADFORD = '#70a669';
export const OTHERS = '#9b9892';

// polls by winning margin: not about either candidate, so a separate ramp, a pastel take on
// the site's brand pink
export const BAND_COLOURS = {
	'0–10%': '#f5e2ec',
	'10–20%': '#dea7c6',
	'20–30%': '#bd6f9b',
	'30%+': '#93436f'
};

// where each candidate's votes came from. The suburbs' blue is the lightest of its hue that
// clears WCAG's 3:1 for graphics against the page (3.1:1); as text it needs 4.5:1, so the
// "Suburbs" heading uses a darker shade (4.5:1)
export const PART_COLOURS = {
	'City of Toronto': '#1f5f8b',
	Suburbs: '#5b97c4',
	'Votes for Other Candidates': '#deddd8'
};
export const SUBURBS_TEXT = '#3a7bab';
