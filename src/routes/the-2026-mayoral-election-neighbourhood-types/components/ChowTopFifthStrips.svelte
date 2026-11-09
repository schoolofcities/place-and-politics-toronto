<script>
	// Strip plots in the style of the five-torontos page, simplified: one row per neighbourhood
	// measure with a dot for every census tract, the fifth of tracts where Chow's 2026 vote share
	// was highest picked out in her colour, and dotted lines at the median of all tracts and of
	// that top fifth. Data: ../data/chow_top_fifth_strips.json, built by
	// analysis/election_2026/03_neighbourhood_types_page_data.ipynb (Section 5).
	import { scaleLinear } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { strips } from './data.js';
	import { CHOW, GROUP_COLOURS } from './config.js';

	const GREY = '#c4c4c4';
	const TOP_LINE = GROUP_COLOURS.held; // the top fifth's median: a deep purple
	const ALL_LINE = '#3a3a3a'; // all tracts' median: charcoal, so the two never read alike
	const { meta, top, variables } = strips;

	let width = $state(560);
	const small = $derived(width < 420);
	const MARGIN = 18;
	const ROW = 82; // title, median labels, strip, tick labels
	const AXIS_Y = 48; // the strip's line, from the top of its row
	const R = $derived(small ? 1.9 : 2.2);
	const R_TOP = $derived(small ? 2.6 : 3);
	const SPACING = $derived(small ? 3.9 : 4.4); // between dots that land at about the same x
	const MAX_SPREAD = 10;
	const height = variables.length * ROW + 4;

	const innerW = $derived(width - 2 * MARGIN);
	const fmt = {
		percent: { tick: (t) => `${t}%`, value: (v) => `${Math.round(v)}%` },
		dollars: { tick: (t) => `$${Math.round(t / 1000)}K`, value: (v) => `$${Math.round(v / 1000)}K` },
		years: { tick: (t) => `${t}`, value: (v) => v.toFixed(1) }
	};

	// stack dots that land at about the same x a little above and below the line, so a dense pile reads as many dots
	function offsets(xs) {
		const seen = new Map();
		return xs.map((x) => {
			const key = Math.round(x / 1.5);
			const n = seen.get(key) ?? 0;
			seen.set(key, n + 1);
			if (n === 0) return 0;
			const m = Math.min(Math.ceil(n / 2) * SPACING, MAX_SPREAD);
			return n % 2 === 1 ? -m : m;
		});
	}

	const rows = $derived(
		variables.map((v) => {
			const x = scaleLinear().domain(v.domain).range([MARGIN, MARGIN + innerW]);
			const inRange = (a) => a != null && a >= v.domain[0] && a <= v.domain[1];
			const idx = v.values.map((a, i) => i).filter((i) => inRange(v.values[i]));
			const cx = idx.map((i) => x(v.values[i]));
			const dy = offsets(cx);
			const dots = idx.map((i, j) => ({ cx: cx[j], dy: dy[j], top: top[i] === 1 }));
			const ticks = [];
			for (let t = v.domain[0]; t <= v.domain[1] + 1e-9; t += v.tick) ticks.push(t);
			const xa = x(v.median_all);
			const xt = x(v.median_top);
			// the two labels sit above their lines on opposite sides, so they never collide: the lower median's ends at its line, the higher one's starts at it
			const topIsLeft = xt < xa;
			return {
				...v,
				x,
				ticks,
				xa,
				xt,
				topIsLeft,
				// back-to-front: the other tracts first, then the top fifth over them
				dots: [...dots.filter((d) => !d.top), ...dots.filter((d) => d.top)]
			};
		})
	);

	const summary = variables.map((v) => `${v.label}: median ${fmt[v.unit].value(v.median_all)} across all tracts, ${fmt[v.unit].value(v.median_top)} in the top fifth`).join('; ');
	const outside = variables.filter((v) => v.outside > 0);
	const range = { income: 'incomes above $160,000 or below $40,000', age: 'median ages outside 30 to 60' };
</script>

<figure>
	<FigureTitle title="Neighbourhoods where Chow did best" subtitle="Her top fifth of census tracts by 2026 vote share, compared with all tracts" />

	<div class="legend">
		<span class="item"><span class="dot" style:background={CHOW}></span>Chow's top fifth of tracts</span>
		<span class="item"><span class="dot" style:background={GREY}></span>All other tracts</span>
		<span class="item"><span class="dash" style:border-color={TOP_LINE}></span>Median, top fifth</span>
		<span class="item"><span class="dash" style:border-color={ALL_LINE}></span>Median, all tracts</span>
	</div>

	<div class="chart" bind:clientWidth={width}>
		<svg {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Strip plots of five neighbourhood measures across Toronto's census tracts, with the tracts where Chow's 2026 vote share was highest picked out. {summary}.">
			{#each rows as r, i (r.key)}
				{@const y0 = i * ROW}
				{@const ay = y0 + AXIS_Y}
				<text class="row-title" x={MARGIN} y={y0 + 13}>{r.label}</text>

				<!-- ticks and their labels, below the dots -->
				<line class="axis" x1={MARGIN} x2={MARGIN + innerW} y1={ay} y2={ay} />
				{#each r.ticks as t (t)}
					<line class="tick" x1={r.x(t)} x2={r.x(t)} y1={ay - 3} y2={ay + 3} />
					<text class="tick-label" x={r.x(t)} y={ay + MAX_SPREAD + 17}>{fmt[r.unit].tick(t)}</text>
				{/each}

				{#each r.dots as d, j (j)}
					<circle cx={d.cx} cy={ay + d.dy} r={d.top ? R_TOP : R} fill={d.top ? CHOW : GREY} fill-opacity={d.top ? 0.85 : 1} />
				{/each}

				<!-- the medians, dotted over a white casing -->
				<line class="casing" x1={r.xa} x2={r.xa} y1={y0 + 22} y2={ay + MAX_SPREAD + 3} />
				<line class="casing" x1={r.xt} x2={r.xt} y1={y0 + 22} y2={ay + MAX_SPREAD + 3} />
				<line class="median" x1={r.xa} x2={r.xa} y1={y0 + 22} y2={ay + MAX_SPREAD + 3} />
				<line class="median top" x1={r.xt} x2={r.xt} y1={y0 + 22} y2={ay + MAX_SPREAD + 3} />
				<!-- each line is named where it sits, in its own colour -->
				<text class="median-label" x={r.xa + (r.topIsLeft ? 4 : -4)} y={y0 + 33} text-anchor={r.topIsLeft ? 'start' : 'end'}><tspan class="nm">All tracts</tspan><tspan dx="4">{fmt[r.unit].value(r.median_all)}</tspan></text>
				<text class="median-label top" x={r.xt + (r.topIsLeft ? -4 : 4)} y={y0 + 33} text-anchor={r.topIsLeft ? 'end' : 'start'}><tspan class="nm">Top fifth</tspan><tspan dx="4">{fmt[r.unit].value(r.median_top)}</tspan></text>
			{/each}
		</svg>
	</div>

	<figcaption class="note">
		Each dot is one of the {meta.tracts} census tracts, using the 2021 census; the top fifth are the {meta.top_tracts} tracts where Chow won {meta.top_cut_pct}% or more of valid 2026 election-day votes
		(the tract median is {meta.city_median_chow_pct}%). Dotted lines are medians of tract values, unweighted. Not drawn: {outside.map((v) => `${v.outside} tracts with ${range[v.key]}`).join(' and ')};
		they are in the medians. Advance and mail-in votes are excluded. These describe neighbourhoods, not how any group voted.
	</figcaption>
</figure>

<style>
	figure {
		max-width: 560px;
		margin: 0 auto;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px 16px;
		margin: 0 0 8px;
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		color: var(--brandGray80);
	}
	.item {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		display: inline-block;
	}
	.dash {
		width: 0;
		height: 14px;
		border-left: 2px dotted #3a3a3a;
		display: inline-block;
	}
	.chart {
		width: 100%;
	}
	svg {
		display: block;
		max-width: 100%;
		height: auto;
		overflow: visible;
		font-family: OpenSans, sans-serif;
	}
	.row-title {
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		fill: var(--brandGray90);
	}
	.axis,
	.tick {
		stroke: var(--brandGray60);
		stroke-width: 1px;
	}
	.tick-label {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: middle;
	}
	.casing {
		stroke: #fff;
		stroke-width: 4px;
	}
	.median {
		stroke: #3a3a3a;
		stroke-width: 1.5px;
		stroke-dasharray: 3 2;
	}
	.median.top {
		stroke: #6f3f8c;
		stroke-width: 2px;
	}
	.median-label {
		font-size: 11px;
		fill: #3a3a3a;
		font-family: OpenSansBold, sans-serif;
	}
	.median-label.top {
		fill: #6f3f8c;
	}
	/* the line's name, lighter than its value */
	.nm {
		font-family: OpenSans, sans-serif;
	}
	.note {
		margin: 12px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
