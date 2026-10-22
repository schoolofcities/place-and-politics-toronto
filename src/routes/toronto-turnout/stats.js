// Small statistics helpers for the explorer scatterplot.

/**
 * Pearson correlation (with its two-sided p-value) and least-squares line over [x, y] pairs.
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
	const r = sxy / Math.sqrt(sxx * syy);
	// two-sided p-value for r (t-test with n - 2 degrees of freedom), as on the
	// social-geography page (routes/social-geography-and-the-mayoral-vote/mapper.js)
	const df = n - 2;
	const t2 = (r * r * df) / Math.max(1e-12, 1 - r * r);
	const p = ibeta(df / 2, 0.5, df / (df + t2));
	return { n, r, p, slope, intercept: my - slope * mx };
}

// regularized incomplete beta function, for the p-value above (Numerical Recipes)
function betacf(a, b, x) {
	const tiny = 1e-30;
	const qab = a + b;
	const qap = a + 1;
	const qam = a - 1;
	let c = 1;
	let d = 1 - (qab * x) / qap;
	if (Math.abs(d) < tiny) d = tiny;
	d = 1 / d;
	let h = d;
	for (let m = 1; m <= 200; m++) {
		const m2 = 2 * m;
		let aa = (m * (b - m) * x) / ((qam + m2) * (a + m2));
		d = 1 + aa * d;
		if (Math.abs(d) < tiny) d = tiny;
		c = 1 + aa / c;
		if (Math.abs(c) < tiny) c = tiny;
		d = 1 / d;
		h *= d * c;
		aa = (-(a + m) * (qab + m) * x) / ((a + m2) * (qap + m2));
		d = 1 + aa * d;
		if (Math.abs(d) < tiny) d = tiny;
		c = 1 + aa / c;
		if (Math.abs(c) < tiny) c = tiny;
		d = 1 / d;
		const del = d * c;
		h *= del;
		if (Math.abs(del - 1) < 3e-7) break;
	}
	return h;
}

function lgamma(z) {
	const g = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
	let y = z;
	let tmp = z + 5.5;
	tmp -= (z + 0.5) * Math.log(tmp);
	let ser = 1.000000000190015;
	for (let j = 0; j < 6; j++) ser += g[j] / ++y;
	return -tmp + Math.log((2.5066282746310005 * ser) / z);
}

function ibeta(a, b, x) {
	if (x <= 0) return 0;
	if (x >= 1) return 1;
	const front = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
	return x < (a + 1) / (a + b + 2) ? (front * betacf(a, b, x)) / a : 1 - (front * betacf(b, a, 1 - x)) / b;
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
