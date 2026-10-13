// Small statistics helpers for the explorer scatterplot.

/**
 * Pearson correlation and least-squares line over [x, y] pairs.
 * Returns null when there are too few pairs or no variation.
 */
export function linearFit(pairs) {
	const n = pairs.length;
	if (n < 5) return null;
	let sx = 0;
	let sy = 0;
	for (const [x, y] of pairs) {
		sx += x;
		sy += y;
	}
	const mx = sx / n;
	const my = sy / n;
	let sxy = 0;
	let sxx = 0;
	let syy = 0;
	for (const [x, y] of pairs) {
		const dx = x - mx;
		const dy = y - my;
		sxy += dx * dy;
		sxx += dx * dx;
		syy += dy * dy;
	}
	if (sxx === 0 || syy === 0) return null;
	const slope = sxy / sxx;
	return { n, r: sxy / Math.sqrt(sxx * syy), slope, intercept: my - slope * mx };
}

/** Breaks that split values into `n` groups of (as near as ties allow) equal size. */
export function quantileBreaks(values, n) {
	const v = values.filter((x) => x != null && Number.isFinite(x)).sort((a, b) => a - b);
	if (!v.length) return [];
	const breaks = [];
	for (let i = 1; i < n; i++) {
		const q = v[Math.min(v.length - 1, Math.floor((i * v.length) / n))];
		if (q > v[0] && (!breaks.length || q > breaks[breaks.length - 1])) breaks.push(q);
	}
	return breaks;
}

/** `k` colours spread evenly across a palette (for when ties leave fewer classes than the palette has). */
export function spread(palette, k) {
	if (k >= palette.length) return palette.slice();
	if (k === 1) return [palette[palette.length - 1]];
	return Array.from({ length: k }, (_, i) => palette[Math.round((i * (palette.length - 1)) / (k - 1))]);
}
