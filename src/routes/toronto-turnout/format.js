// Number formatting for the turnout page. Values are stored the way the analysis
// exports them: shares as 0-1, income in dollars, distance in km.

const nf = (digits) =>
	new Intl.NumberFormat('en-CA', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const nf0 = nf(0);
const nf1 = nf(1);
const nf2 = nf(2);
const nf3 = nf(3);

const MINUS = '−';
const signed = (v, text) => (v < 0 ? `${MINUS}${text.replace('-', '')}` : text);

export const fmtPct = (v, digits = 0) => (v == null ? 'No data' : `${nf(digits).format(v * 100)}%`);

// Turnout is estimated from polls apportioned to tracts, so a few small tracts come out above
// 100%; those are shown as "100%+" rather than as an impossible exact figure.
export const fmtTurnout = (v, digits = 0) =>
	v == null ? 'No data' : v > 1 ? '100%+' : fmtPct(v, digits);

export const fmtCurrency = (v, compact = false) =>
	v == null
		? 'No data'
		: compact
			? `$${nf0.format(Math.round(v / 1000))}k`
			: `$${nf0.format(Math.round(v))}`;

export const fmtKm = (v, digits = 1) => (v == null ? 'No data' : `${nf(digits).format(v)} km`);

export const fmtScore = (v, digits = 1) =>
	v == null ? 'No data' : signed(v, `${v > 0 ? '+' : ''}${nf(digits).format(v)}`);

export const fmtLoading = (v) => signed(v, `${v > 0 ? '+' : ''}${nf2.format(v)}`);

export const fmtR = (r) => signed(r, `${r > 0 ? '+' : ''}${nf2.format(r)}`);

export const fmtNumber1 = (v) => nf1.format(v);

/**
 * Formatter set for one explorer variable, from its `format`:
 * "percent" (0-1 share), "currency" (CAD), "km", "density" (people per km2),
 * "number1" / "number2" (plain numbers) or "index" (0-1 proximity index).
 * `axis` is for tick labels (compact), `value` for tooltips and readouts (full).
 */
export function variableFormat(format) {
	switch (format) {
		case 'currency':
			return { axis: (v) => fmtCurrency(v, true), value: (v) => fmtCurrency(v) };
		case 'km':
			return { axis: (v) => `${nf0.format(v)} km`, value: (v) => fmtKm(v) };
		case 'density':
			return {
				axis: (v) => (v >= 1000 ? `${nf1.format(v / 1000)}k` : nf0.format(v)),
				value: (v) => (v == null ? 'No data' : `${nf0.format(v)} per km²`)
			};
		case 'number1':
			return { axis: (v) => nf1.format(v), value: (v) => (v == null ? 'No data' : nf2.format(v)) };
		case 'number2':
			return { axis: (v) => nf1.format(v), value: (v) => (v == null ? 'No data' : nf2.format(v)) };
		case 'index':
			return { axis: (v) => nf2.format(v), value: (v) => (v == null ? 'No data' : nf3.format(v)) };
		default:
			return { axis: (v) => fmtPct(v, 0), value: (v) => fmtPct(v, 1) };
	}
}

/** A correlation's p-value, as on the social-geography page: "p < 0.001" or "p = 0.034". */
export const fmtP = (p) => (p < 0.001 ? 'p < 0.001' : `p = ${p.toFixed(3)}`);
