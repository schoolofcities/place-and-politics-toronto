<script>
	// Generic 1-N variable strip plot: each row is one variable's axis, every one of the
	// 585 census tracts gets a dot on it, and the current cluster's tracts are highlighted
	// in its colour against the rest of the city in grey, with dotted lines at the citywide
	// and cluster medians. Passing 2 variables gives the "double strip plot" (Progressive Core,
	// Soft-Left Belt sections); 3 gives the "triple strip plot" (Suburban Conservatives and
	// Low-turnout Suburbanites) — same component either way.

	import { scaleLinear, extent, median } from "d3";

	export let values = []; // ct_values.json records (or a pre-filtered subset)
	export let variables = []; // [{ key, label, domain?, tickStep?, format? }] — domain: [min, max] fixes the axis range and drops out-of-range dots; tickStep: fixed spacing between tick labels (both optional, and only meaningful together); format: (value) => string, applied to tick labels and the median label alike (defaults to the raw number for ticks, one decimal place for the median)
	export let clusterId;
	export let clusterLabel = ""; // e.g. "Progressive Core", for its median label
	export let color = "#3d53fb";

	$: ariaLabel = `Strip plot${variables.length > 1 ? "s" : ""} showing ${variables
		.map((v) => v.label)
		.join(" and ")} across Toronto's 585 census tracts, with this cluster's tracts highlighted`;

	const FADE_COLOR = "#c4c4c4";
	const DOT_R = 2.5;
	const JITTER_SPACING = 6; // px between successive dots stacked at ~the same x
	const MAX_JITTER = 12; // cap how far dots spread from the line, so they never reach the tick labels
	const rowHeight = 159; // includes the gap between rows
	const ROW_BOTTOM = 80; // how far a row's content reaches below its top (to the Toronto median label)
	const margin = { top: 57, bottom: 4, left: 16, right: 16 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	// ends just below the last row's content, rather than leaving a full row's height (which
	// includes the between-row gap) below it
	$: height = margin.top + (variables.length - 1) * rowHeight + ROW_BOTTOM + margin.bottom;

	// "% variables" (pct_* keys) always run the full 0–100 range with ticks every 20, so the
	// axis reads the same across sections. A variable can also fix its own range explicitly
	// via `domain` (e.g. average age, 30–60) instead of stretching to whatever outliers are in
	// the data — anything outside that range is dropped from the plot rather than drawn past
	// the axis end. With neither, fall back to d3's own "nice" ticks off the real data extent.
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

	// Citywide median for each row -- always computed over every tract the row actually plots
	// (valuesFor), not just this section's cluster, so it reads as a fixed reference line.
	$: medians = variables.map((v, i) => median(valuesFor[i], (d) => d[v.key]));
	// This cluster's median for each row, over its own plotted tracts.
	$: clusterMedians = variables.map((v, i) =>
		median(valuesFor[i].filter((d) => d.cluster_id === clusterId), (d) => d[v.key])
	);
	// % variables get a "%" on their tick and median labels
	$: tickFormat = variables.map((v) => v.format ?? (isPercent(v.key) ? (t) => `${t}%` : (t) => t));
	$: medianFormat = variables.map(
		(v) => v.format ?? (isPercent(v.key) ? (t) => `${t.toFixed(1)}%` : (t) => t.toFixed(1))
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
	<svg width={divWidth} {height} role="img" aria-label={ariaLabel}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			{#each variables as v, i}
				{@const y = i * rowHeight}
				{@const scale = scales[i]}
				<text class="row-title" x="0" y={y - 39}>{v.label}</text>
				<line class="axis" x1="0" x2={innerWidth} y1={y + 20} y2={y + 20} />

				<!-- ticks drawn first, behind the dots; their labels sit below the jitter band,
					 well clear of the dots -->
				{#each ticks[i] as t}
					<line class="tick" x1={scale(t)} x2={scale(t)} y1={y + 17} y2={y + 23} />
					<text class="tick-label" x={scale(t)} y={y + 48}>{tickFormat[i](t)}</text>
				{/each}

				<!-- medians: dotted reference lines (Toronto in grey, this cluster in its colour),
					 longer than the tick marks, each labelled just above its top end, between the row
					 title and the line. The lines themselves are drawn after the dots, on top, each over a
					 white casing so it stands out against them (see below). -->
				{@const medX = scales[i](medians[i])}
				{@const cMedX = scales[i](clusterMedians[i])}
				<!-- both centred on their lines, each over two lines (name, then "median: value"):
					 the cluster's label above the strip, Toronto's below it (under the tick numbers) -->
				<text class="median-label" text-anchor="middle">
					<tspan x={medX} y={y + 63}>City of Toronto</tspan>
					<tspan x={medX} y={y + 76}>median: {medianFormat[i](medians[i])}</tspan>
				</text>
				<text class="median-label cluster-median-label" text-anchor="middle">
					<tspan x={cMedX} y={y - 23}>{clusterLabel}</tspan>
					<tspan x={cMedX} y={y - 10}>median: {medianFormat[i](clusterMedians[i])}</tspan>
				</text>

				<!-- background: every tract in the city -->
				{#each rows[i].bg as p}
					<circle cx={p.cx} cy={y + 20 + p.cy} r={DOT_R} fill={FADE_COLOR} />
				{/each}
				<!-- foreground: this cluster's tracts -->
				{#each rows[i].fg as p}
					<circle cx={p.cx} cy={y + 20 + p.cy} r={DOT_R + 1} fill={color} fill-opacity="0.85" />
				{/each}

				<!-- median lines on top of the dots: a solid white casing, then the dashed line -->
				<!-- Toronto's line runs down toward its label below; the cluster's up toward its label above -->
				<line class="median-casing" x1={medX} x2={medX} y1={y + 2} y2={y + 52} />
				<line class="median-casing" x1={cMedX} x2={cMedX} y1={y - 7} y2={y + 34} />
				<line class="median" x1={medX} x2={medX} y1={y + 2} y2={y + 52} />
				<line class="median" x1={cMedX} x2={cMedX} y1={y - 7} y2={y + 34} style:stroke={color} />
			{/each}
		</g>
	</svg>
</div>

<style>
	.row-title {
		font-size: 13px;
		fill: black;
		font-family: OpenSansBold, sans-serif;
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
		font-size: 11px;
		fill: black;
		text-anchor: middle;
		font-family: OpenSans, sans-serif;
	}
	.median-casing {
		stroke: white;
		stroke-width: 4.5px;
	}
	.median {
		stroke: var(--brandGray70);
		stroke-width: 1.5px;
		stroke-dasharray: 3, 2;
	}
	.median-label {
		font-size: 11px;
		fill: var(--brandGray70);
		font-family: OpenSans, sans-serif;
	}
	.cluster-median-label {
		fill: black;
	}

</style>
