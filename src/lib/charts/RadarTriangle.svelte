<script>
	// Alternative to TernaryProfilePlot.svelte for Working Suburbanites: a triangle-as-radar
	// hybrid, 3 spokes from a shared centre, one per cluster-summary record (not per tract).
	// Each spoke is scaled on its OWN absolute terms rather than a percentile rank among the
	// 5 clusters: visible minority % runs its natural 0–100 range, bachelor's+ % runs 0–60 (no
	// cluster is anywhere near 100% on this one, so a 0–100 axis would waste most of its
	// length), and median income runs the actual (niced) range across the 5 clusters. All 5
	// clusters draw as outlines only, in their own colour — no fill — so overlapping shapes
	// stay legible; the active cluster gets a noticeably thicker outline and draws on top.
	// Currently unused (see the commented-out import/markup in +page.svelte) — kept as a ready
	// swap-in alternative to the ternary plot.

	import { scaleLinear, extent } from "d3";

	export let clusters = []; // all 5 cluster summary records
	export let activeClusterId;

	const AXES = [
		{ label: "Visible minority", angle: -90, get: (c) => c.demographics.pct_visible_minority, domain: [0, 100], format: (v) => `${v.toFixed(0)}%` },
		{ label: "Bachelor's degree+", angle: 30, get: (c) => c.demographics.pct_bachelor_or_higher, domain: [0, 60], format: (v) => `${v.toFixed(0)}%` },
		{ label: "Median income", angle: 150, get: null, domain: null, format: (v) => `$${Math.round(v / 1000)}k` },
	];

	// Income doesn't have a natural 0–100 scale like the two % variables, so its axis runs the
	// actual (niced) range across the 5 clusters instead of a fixed ceiling.
	$: incomeDomain = scaleLinear()
		.domain(extent(clusters, (c) => c.demographics.income_median_approx))
		.nice()
		.domain();
	$: axes = AXES.map((ax, i) =>
		i === 2 ? { ...ax, get: (c) => c.demographics.income_median_approx, domain: incomeDomain } : ax
	);

	const MARGIN = 78; // room outside the spokes for the tick value + the axis name beyond it
	const MAX_R = 110;
	const MIN_R = 55;

	// Sized off the measured container width (like the other charts on this page) rather than
	// a fixed pixel size, so it never overflows a narrower box than expected.
	let divWidth = 380;
	$: R = Math.max(MIN_R, Math.min((divWidth - MARGIN * 2) / 2, MAX_R));
	$: SIZE = R * 2 + MARGIN * 2;
	$: cx = SIZE / 2;
	$: cy = SIZE / 2 + 6;
	const toRad = (deg) => (deg * Math.PI) / 180;

	function fracFor(axis, cluster) {
		const [min, max] = axis.domain;
		return max === min ? 0.5 : (axis.get(cluster) - min) / (max - min);
	}
	// Takes R/cx/cy as explicit arguments (rather than closing over them) so every reactive
	// call site passes the *current* R/cx/cy directly in its own `$:` statement — see the note
	// in TernaryProfilePlot.svelte for why a closure over reactive vars isn't reliable here.
	function pointFor(R, cx, cy, angle, frac) {
		const r = R * frac;
		const a = toRad(angle);
		return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) };
	}
	function polygonPoints(pts) {
		return pts.map((p) => `${p.x},${p.y}`).join(" ");
	}

	// Tick value sits just past the spoke's tip; the axis name sits further out again — both
	// placed along the spoke's own radial direction so they never overlap on a diagonal spoke.
	$: axisEnds = axes.map((ax) => pointFor(R, cx, cy, ax.angle, 1));
	$: tickPositions = axes.map((ax) => pointFor(R, cx, cy, ax.angle, 1.16));
	$: labelPositions = axes.map((ax) => pointFor(R, cx, cy, ax.angle, 1.65));
	$: polygons = clusters.map((c) => ({
		cluster: c,
		points: axes.map((ax) => pointFor(R, cx, cy, ax.angle, fracFor(ax, c))),
	}));
	$: activePolygon = polygons.find((p) => p.cluster.cluster_id === activeClusterId);
	$: otherPolygons = polygons.filter((p) => p.cluster.cluster_id !== activeClusterId);
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={SIZE} height={SIZE}>
		{#each axes as ax, i}
			{@const end = axisEnds[i]}
			{@const tick = tickPositions[i]}
			{@const labelPos = labelPositions[i]}
			<!-- Anchor each label so it grows back INWARD, toward the centre, rather than further
				 out past the spoke tip, so it can't overhang the SVG's own edge. -->
			{@const anchor = Math.abs(end.x - cx) < 4 ? "middle" : end.x > cx ? "end" : "start"}
			<line class="spoke" x1={cx} y1={cy} x2={end.x} y2={end.y} />
			<text class="axis-tick" x={tick.x} y={tick.y} text-anchor={anchor}>{ax.format(ax.domain[1])}</text>
			<text class="axis-label" x={labelPos.x} y={labelPos.y} text-anchor={anchor}>{ax.label}</text>
		{/each}

		{#each otherPolygons as p}
			<polygon class="cluster-shape" points={polygonPoints(p.points)} stroke={p.cluster.color} />
		{/each}
		{#if activePolygon}
			<polygon class="cluster-shape active" points={polygonPoints(activePolygon.points)} stroke={activePolygon.cluster.color} />
		{/if}
	</svg>
</div>

<style>
	.spoke {
		stroke: #bbb;
		stroke-width: 1px;
	}
	.axis-label {
		font-size: 11px;
		fill: black;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	.axis-tick {
		font-size: 9px;
		fill: black;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	.cluster-shape {
		fill: none;
		stroke-width: 1.5px;
	}
	.cluster-shape.active {
		stroke-width: 3.5px;
	}
</style>
