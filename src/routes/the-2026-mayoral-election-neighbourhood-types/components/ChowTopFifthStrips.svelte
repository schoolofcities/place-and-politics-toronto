<script>
	// Strip plots in the style of the five-torontos page, simplified: one row per neighbourhood
	// measure with a dot for every census tract; the fifth of tracts where Chow's 2026 vote share was
	// highest is picked out in her colour and the fifth where Bradford's was highest in his (drawn in a mixed, seeded order), with
	// dotted lines at the median of all tracts and of each top fifth. Only the first row names its
	// lines; the others show just the values. Data: ../data/chow_top_fifth_strips.json, built by
	// analysis/election_2026/03_neighbourhood_types_page_data.ipynb (Section 5).
	import { scaleLinear } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { strips } from './data.js';
	import { CHOW, BRADFORD, GROUP_COLOURS } from './config.js';

	const GREY = '#c4c4c4';
	const CHOW_LINE = GROUP_COLOURS.held; // deep purple
	const BRADFORD_LINE = '#3f7a3b'; // deep green
	const ALL_LINE = '#3a3a3a'; // charcoal, so the three never read alike
	const { meta, chow_top, bradford_top, variables } = strips;

	let width = $state(560);
	const small = $derived(width < 420);
	const MARGIN = 18;
	const ROW = 90; // title, median labels (on two levels if they would collide), strip, tick labels
	const AXIS_Y = 56; // the strip's line, from the top of its row
	const LINE_TOP = 30; // where the median lines start
	const LEVEL_UP = 27; // baselines of the median labels: an upper level, used only to avoid a collision, and the usual lower one
	const LEVEL_LOW = 40;
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
	const NAMES = { all: 'All tracts', chow: 'Chow', bradford: 'Bradford' };
	const CHAR_W = 6.4; // about the width of a character of the 11px bold labels

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

	// Where the two candidates' dots overlap, neither should always be on top: the highlighted dots are drawn in a random order.
	// The shuffle is seeded (per row), so the page renders the same on the server and in the browser and on every visit.
	function shuffled(items, seed) {
		let a = seed >>> 0;
		const rand = () => {
			a = (a + 0x6d2b79f5) >>> 0;
			let t = a;
			t = Math.imul(t ^ (t >>> 15), t | 1);
			t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
			return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
		};
		const out = [...items];
		for (let i = out.length - 1; i > 0; i--) {
			const j = Math.floor(rand() * (i + 1));
			[out[i], out[j]] = [out[j], out[i]];
		}
		return out;
	}

	// Labels for the three medians, left to right. The leftmost ends at its line and the rightmost starts at its line;
	// the middle one starts at its line too, unless that would run into the rightmost, and then it is centred on its line one level up.
	function placeLabels(items, named) {
		const sorted = [...items].sort((a, b) => a.x - b.x);
		const width = (it) => (named ? NAMES[it.key].length + 1 : 0) * CHAR_W + it.text.length * CHAR_W + 4;
		return sorted.map((it, i) => {
			const w = width(it);
			if (i === 0) return { ...it, anchor: 'end', lx: it.x - 4, ly: LEVEL_LOW };
			if (i === sorted.length - 1) return { ...it, anchor: 'start', lx: it.x + 4, ly: LEVEL_LOW };
			const clash = sorted[i + 1].x - it.x < w + 4;
			return clash ? { ...it, anchor: 'middle', lx: it.x, ly: LEVEL_UP } : { ...it, anchor: 'start', lx: it.x + 4, ly: LEVEL_LOW };
		});
	}

	const rows = $derived(
		variables.map((v, i) => {
			const x = scaleLinear().domain(v.domain).range([MARGIN, MARGIN + innerW]);
			const inRange = (a) => a != null && a >= v.domain[0] && a <= v.domain[1];
			const idx = v.values.map((a, k) => k).filter((k) => inRange(v.values[k]));
			const cx = idx.map((k) => x(v.values[k]));
			const dy = offsets(cx);
			const kind = (k) => (chow_top[k] === 1 ? 'chow' : bradford_top[k] === 1 ? 'bradford' : 'other');
			const dots = idx.map((k, j) => ({ cx: cx[j], dy: dy[j], kind: kind(k) }));
			const ticks = [];
			for (let t = v.domain[0]; t <= v.domain[1] + 1e-9; t += v.tick) ticks.push(t);
			const medians = [
				{ key: 'all', x: x(v.median_all), text: fmt[v.unit].value(v.median_all) },
				{ key: 'chow', x: x(v.median_chow), text: fmt[v.unit].value(v.median_chow) },
				{ key: 'bradford', x: x(v.median_bradford), text: fmt[v.unit].value(v.median_bradford) }
			];
			return {
				...v,
				x,
				ticks,
				medians,
				labels: placeLabels(medians, i === 0),
				// back-to-front: the other tracts first, then both top fifths over them, mixed at random
				dots: [...dots.filter((d) => d.kind === 'other'), ...shuffled(dots.filter((d) => d.kind !== 'other'), 1000 + i)]
			};
		})
	);

	const summary = variables
		.map((v) => `${v.label}: median ${fmt[v.unit].value(v.median_all)} across all tracts, ${fmt[v.unit].value(v.median_chow)} in Chow's top fifth and ${fmt[v.unit].value(v.median_bradford)} in Bradford's top fifth`)
		.join('; ');
	const outside = variables.filter((v) => v.outside > 0);
	const range = { income: 'incomes above $160,000 or below $40,000', age: 'median ages outside 30 to 60' };
	const dotFill = { chow: CHOW, bradford: BRADFORD, other: GREY };
	const lineColour = { all: ALL_LINE, chow: CHOW_LINE, bradford: BRADFORD_LINE };
</script>

<figure>
	<FigureTitle title="Neighbourhoods where each candidate did best" subtitle="Their top fifth of census tracts by 2026 vote share; dotted lines are medians" />

	<div class="legend">
		<span class="item"><span class="dot" style:background={CHOW}></span><span class="dash" style:border-color={CHOW_LINE}></span>Chow's top fifth</span>
		<span class="item"><span class="dot" style:background={BRADFORD}></span><span class="dash" style:border-color={BRADFORD_LINE}></span>Bradford's top fifth</span>
		<span class="item"><span class="dot" style:background={GREY}></span><span class="dash" style:border-color={ALL_LINE}></span>All tracts</span>
	</div>

	<div class="chart" bind:clientWidth={width}>
		<svg {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Strip plots of five neighbourhood measures across Toronto's census tracts, with each candidate's top fifth of tracts by 2026 vote share picked out. {summary}.">
			{#each rows as r, i (r.key)}
				{@const y0 = i * ROW}
				{@const ay = y0 + AXIS_Y}
				{@const lineEnd = ay + MAX_SPREAD + 3}
				<text class="row-title" x="0" y={y0 + 13}>{r.label}</text>

				<!-- ticks and their labels, below the dots -->
				<line class="axis" x1={MARGIN} x2={MARGIN + innerW} y1={ay} y2={ay} />
				{#each r.ticks as t (t)}
					<line class="tick" x1={r.x(t)} x2={r.x(t)} y1={ay - 3} y2={ay + 3} />
					<text class="tick-label" x={r.x(t)} y={ay + MAX_SPREAD + 17}>{fmt[r.unit].tick(t)}</text>
				{/each}

				{#each r.dots as d, j (j)}
					<circle cx={d.cx} cy={ay + d.dy} r={d.kind === 'other' ? R : R_TOP} fill={dotFill[d.kind]} fill-opacity={d.kind === 'other' ? 1 : 0.85} />
				{/each}

				<!-- the medians, dotted over a white casing -->
				{#each r.medians as m (m.key)}
					<line class="casing" x1={m.x} x2={m.x} y1={y0 + LINE_TOP} y2={lineEnd} />
				{/each}
				{#each r.medians as m (m.key)}
					<line class="median" class:strong={m.key !== 'all'} x1={m.x} x2={m.x} y1={y0 + LINE_TOP} y2={lineEnd} style:stroke={lineColour[m.key]} />
				{/each}

				<!-- each value in its line's colour; only the first row also names the line -->
				{#each r.labels as l (l.key)}
					<text class="median-label" x={l.lx} y={y0 + l.ly} text-anchor={l.anchor} style:fill={lineColour[l.key]}>
						{#if i === 0}<tspan class="nm">{NAMES[l.key]}</tspan><tspan dx="4">{l.text}</tspan>{:else}{l.text}{/if}
					</text>
				{/each}
			{/each}
		</svg>
	</div>

	<figcaption class="note">
		Each dot is one of the {meta.tracts} census tracts, using the 2021 census. Each top fifth is the {meta.top_tracts} tracts where the candidate won the highest share of valid 2026 election-day votes:
		Chow {meta.top_cut_pct}% or more (the tract median is {meta.city_median_chow_pct}%) and Bradford {meta.bradford_cut_pct}% or more ({meta.city_median_bradford_pct}%). Dotted lines are medians of tract values, unweighted.
		Not drawn: {outside.map((v) => `${v.outside} tracts with ${range[v.key]}`).join(' and ')}; they are in the medians. Advance and mail-in votes are excluded. These describe neighbourhoods, not how any group voted.
	</figcaption>
</figure>

<style>
	/* as wide as the paragraphs (the page's .graphic wrapper sets that width) */
	figure {
		margin: 0;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px 18px;
		margin: 0 0 10px;
		font-family: OpenSans, sans-serif;
		font-size: 13px;
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
	/* the median's dotted line, drawn heavy so its colour stands out */
	.dash {
		width: 0;
		height: 16px;
		border-left: 3px dotted;
		display: inline-block;
		margin-right: 1px;
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
		stroke-width: 1.5px;
		stroke-dasharray: 3 2;
	}
	.median.strong {
		stroke-width: 2px;
	}
	.median-label {
		font-size: 11px;
		font-family: OpenSansBold, sans-serif;
	}
	/* the line's name, lighter than its value */
	.nm {
		font-family: OpenSans, sans-serif;
	}
	.note {
		margin: 14px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
