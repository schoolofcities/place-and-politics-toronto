<script>
	// Generic 1-N variable strip plot: each row is one variable's axis, every one of the
	// 585 census tracts gets a dot on it, and the current cluster's tracts are highlighted
	// in its colour against the rest of the city in grey. Passing 2 variables gives the
	// "double strip plot" in the Progressive Core section; 3 gives the "triple strip plot"
	// in the Settled Conservatives section — same component either way.

	import { scaleLinear, extent } from "d3";

	export let values = []; // ct_values.json records (or a pre-filtered subset)
	export let variables = []; // [{ key, label, format?, domain?, tickStep? }] — domain: [min, max] to fix the axis range and drop out-of-range dots; tickStep: fixed spacing between tick labels (both optional, and only meaningful together)
	export let clusterId;
	export let color = "#3d53fb";

	const FADE_COLOR = "#d8d8d8";
	const DOT_R = 2.5;
	const JITTER_SPACING = 6; // px between successive dots stacked at ~the same x
	const MAX_JITTER = 12; // cap how far dots spread from the line, so they never reach the tick labels
	const rowHeight = 80;
	const margin = { top: 24, bottom: 22, left: 16, right: 16 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	$: height = variables.length * rowHeight + margin.top + margin.bottom;

	// "% variables" (pct_* keys) always run the full 0–100 range with ticks every 20 — the
	// range is fixed rather than data-driven so the axis reads the same across sections. A
	// variable can also fix its own range explicitly via `domain` (e.g. average age, 30–60)
	// rather than stretching to whatever outliers happen to be in the data; anything outside
	// that range is dropped from the plot entirely rather than drawn off past the axis end.
	// With neither, fall back to d3's own "nice" ticks off the actual data extent.
	const isPercent = (key) => key.startsWith("pct_");
	$: scales = variables.map((v) =>
		isPercent(v.key)
			? scaleLinear().domain([0, 100]).range([0, innerWidth])
			: v.domain
			? scaleLinear().domain(v.domain).range([0, innerWidth])
			: scaleLinear().domain(extent(values, (d) => d[v.key])).range([0, innerWidth]).nice()
	);
	$: ticks = variables.map((v, i) => {
		if (isPercent(v.key)) return [0, 20, 40, 60, 80, 100];
		if (v.domain && v.tickStep) {
			const [min, max] = v.domain;
			const out = [];
			for (let t = min; t <= max; t += v.tickStep) out.push(t);
			return out;
		}
		return scales[i].ticks(5);
	});
	$: valuesFor = variables.map((v) =>
		v.domain ? values.filter((d) => d[v.key] >= v.domain[0] && d[v.key] <= v.domain[1]) : values
	);

	// Rather than every dot sitting dead-on the axis line, spread dots that land at (nearly)
	// the same x a little above/below it — not a true collision-avoiding beeswarm, just enough
	// vertical stagger that a dense cluster of tracts at one value reads as "many dots here"
	// rather than a single dot silently standing in for all of them.
	function jitterOffsets(xs) {
		const seen = new Map(); // rounded x -> how many dots already placed there
		return xs.map((x) => {
			const key = Math.round(x);
			const count = seen.get(key) ?? 0;
			seen.set(key, count + 1);
			if (count === 0) return 0;
			const magnitude = Math.min(Math.ceil(count / 2) * JITTER_SPACING, MAX_JITTER);
			return count % 2 === 1 ? -magnitude : magnitude;
		});
	}

	// Jitter background + foreground dots together (per row) so a highlighted tract doesn't
	// land exactly on top of an already-placed city-wide dot at the same value.
	$: rows = variables.map((v, i) => {
		const scale = scales[i];
		const rowValues = valuesFor[i];
		const bg = rowValues.filter((d) => d.cluster_id !== clusterId);
		const fg = rowValues.filter((d) => d.cluster_id === clusterId);
		const bgX = bg.map((d) => scale(d[v.key]));
		const fgX = fg.map((d) => scale(d[v.key]));
		const offsets = jitterOffsets([...bgX, ...fgX]);
		return {
			bg: bg.map((d, j) => ({ cx: bgX[j], cy: offsets[j] })),
			fg: fg.map((d, j) => ({ cx: fgX[j], cy: offsets[bgX.length + j] })),
		};
	});
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			{#each variables as v, i}
				{@const y = i * rowHeight}
				{@const scale = scales[i]}
				<text class="row-title" x="0" y={y - 6}>{v.label}</text>
				<line class="axis" x1="0" x2={innerWidth} y1={y + 20} y2={y + 20} />

				<!-- background: every tract in the city -->
				{#each rows[i].bg as p}
					<circle cx={p.cx} cy={y + 20 + p.cy} r={DOT_R} fill={FADE_COLOR} />
				{/each}
				<!-- foreground: this cluster's tracts -->
				{#each rows[i].fg as p}
					<circle cx={p.cx} cy={y + 20 + p.cy} r={DOT_R + 1} fill={color} fill-opacity="0.85" />
				{/each}

				<!-- ticks drawn after the dots (and well clear of the jitter band) so a dense
					 cluster of dots never sits on top of a tick label -->
				{#each ticks[i] as t}
					<line class="tick" x1={scale(t)} x2={scale(t)} y1={y + 17} y2={y + 23} />
					<text class="tick-label" x={scale(t)} y={y + 48}>{t}</text>
				{/each}
			{/each}
		</g>
	</svg>
</div>

<style>
	.row-title {
		font-size: 13px;
		fill: black;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	.axis {
		stroke: black;
		stroke-width: 1px;
	}
	.tick {
		stroke: black;
		stroke-width: 1px;
	}
	.tick-label {
		font-size: 10px;
		fill: black;
		text-anchor: middle;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>
