// The five clusters' colours on this page, keyed by cluster slug. These override the colours
// stored in the data files (clusters_summary.json's `color`, ct_clusters.geo.json's
// `cluster_color`), which still carry the original palette.
//
// A deliberately non-partisan palette: no NDP orange, Liberal red, Conservative blue or Green
// green, since each cluster combines voting across three levels of government. Checked with a
// categorical palette validator (light mode, all pairs): even lightness and chroma, every pair
// distinct with normal vision (worst: violet/plum, ΔE 18.9). Rose/aqua is the closest pair under
// deuteranopia (ΔE 7.9), acceptable because every map is also labelled (legend or section heading).
export const CLUSTER_COLORS = {
	"progressive-core": "#EDA100", // saffron
	"soft-left-belt": "#D98CB3", // dusty rose
	"civic-liberals": "#1BAF7A", // aqua
	"suburban-conservatives": "#6250D6", // violet
	"low-turnout-suburbanites": "#8E2C6E", // plum (darkest, on the largest cluster)
};

// Outline for a single highlighted cluster on the maps, where it sits against white. WCAG 1.4.11
// asks for 3:1 contrast between a graphic and what's beside it; saffron, rose and aqua fall short
// against white (about 2.1–2.7:1 as drawn), so their outline is a darker shade of the same hue
// (about 3.5:1 as drawn). Violet and plum already pass, so they keep their own colour.
export const CLUSTER_OUTLINE_COLORS = {
	"progressive-core": "#AD7600",
	"soft-left-belt": "#C95C93",
	"civic-liberals": "#179468",
	"suburban-conservatives": "#6250D6",
	"low-turnout-suburbanites": "#8E2C6E",
};
