<script>
	// Scatterplot of one tract-level predictor (x) against mean turnout (y), one dot per
	// census tract, with the least-squares trend line. Hovering (or tapping) picks the nearest
	// dot; the chart is also a keyboard control: focus it, then Left/Right step through the
	// tracts in order of the x variable. `activeId` is two-way so a map can highlight the same
	// tract. Dot positions are computed in script and drawn as plain SVG, as on the other charts.

	import { createEventDispatcher } from 'svelte';
	import { scaleLinear, extent } from 'd3';
	import { fmtTurnout, fmtPct } from '../format.js';

	export let rows = []; // tract records
	export let xField;
	export let xLabel = '';
	export let xAxisFormat = (v) => v;
	export let xValueFormat = (v) => v;
	export let xFromZero = false; // start the x axis at 0 (shares) rather than at the data minimum
	export let fit = null; // { r, slope, intercept }
	export let activeId = null;

	const dispatch = createEventDispatcher();
	const Y_FIELD = 'mean_turnout';
	const margin = { top: 10, right: 24, bottom: 46, left: 50 };
	const HIT_RADIUS = 14;

	let boxWidth = 480;
	$: width = Math.max(260, boxWidth);
	$: height = Math.round(Math.min(480, Math.max(300, width * 0.95)));
	$: innerW = width - margin.left - margin.right;
	$: innerH = height - margin.top - margin.bottom;

	$: points = rows.filter((d) => d[xField] != null && d[Y_FIELD] != null);
	$: xExtent = extent(points, (d) => d[xField]);
	$: xScale = scaleLinear()
		.domain([xFromZero ? 0 : xExtent[0], xExtent[1]])
		.range([0, innerW])
		.nice();
	$: yScale = scaleLinear()
		.domain(extent(points, (d) => d[Y_FIELD]))
		.range([innerH, 0])
		.nice();
	$: xTicks = xScale.ticks(width < 420 ? 4 : 6);
	$: yTicks = yScale.ticks(5);
	$: dots = points.map((d) => ({ ct: d.ct, name: d.name, x: xScale(d[xField]), y: yScale(d[Y_FIELD]), xv: d[xField], yv: d[Y_FIELD] }));
	$: byX = [...dots].sort((a, b) => a.xv - b.xv);
	$: active = dots.find((d) => d.ct === activeId) ?? null;

	// the trend line, drawn across the data only (not out to the axis ends)
	$: line = fit
		? {
				x1: xScale(xExtent[0]),
				y1: yScale(fit.intercept + fit.slope * xExtent[0]),
				x2: xScale(xExtent[1]),
				y2: yScale(fit.intercept + fit.slope * xExtent[1])
			}
		: null;

	function nearest(event) {
		const box = event.currentTarget.getBoundingClientRect();
		const px = event.clientX - box.left - margin.left;
		const py = event.clientY - box.top - margin.top;
		let best = null;
		let bestD = HIT_RADIUS * HIT_RADIUS;
		for (const d of dots) {
			const dd = (d.x - px) ** 2 + (d.y - py) ** 2;
			if (dd < bestD) {
				best = d;
				bestD = dd;
			}
		}
		return best;
	}
	function pick(id) {
		if (id === activeId) return;
		activeId = id;
		dispatch('select', id);
	}
	function onPointer(event) {
		pick(nearest(event)?.ct ?? null);
	}

	function onKey(event) {
		const step = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1, PageUp: 10, PageDown: -10 }[event.key];
		if (event.key === 'Escape') return pick(null);
		if (event.key === 'Home' || event.key === 'End') {
			event.preventDefault();
			return pick(byX[event.key === 'Home' ? 0 : byX.length - 1]?.ct ?? null);
		}
		if (!step) return;
		event.preventDefault();
		const i = byX.findIndex((d) => d.ct === activeId);
		const next = i < 0 ? Math.floor(byX.length / 2) : Math.max(0, Math.min(byX.length - 1, i + step));
		pick(byX[next]?.ct ?? null);
	}

	// right-hand dots flip the tooltip to the left of the dot
	$: tipSide = active && active.x > innerW * 0.55 ? 'left' : 'right';
	$: description = `Scatter plot of mean turnout against ${xLabel} for ${points.length} census tracts${fit ? `, correlation ${fit.r.toFixed(2)}` : ''}. Use the left and right arrow keys to move between tracts.`;
</script>

<div class="scatter" bind:clientWidth={boxWidth}>
	<!-- svelte-ignore a11y-no-noninteractive-tabindex -->
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<svg
		{width}
		{height}
		role="group"
		tabindex="0"
		aria-roledescription="scatter plot"
		aria-label={description}
		on:pointermove={onPointer}
		on:pointerdown={onPointer}
		on:pointerleave={(e) => e.pointerType === 'mouse' && pick(null)}
		on:keydown={onKey}
		on:blur={() => pick(null)}
	>
		<g transform="translate({margin.left},{margin.top})">
			<!-- light horizontal grid -->
			{#each yTicks as t}
				<line class="grid" x1="0" x2={innerW} y1={yScale(t)} y2={yScale(t)} />
			{/each}
			<line class="axis" x1="0" x2={innerW} y1={innerH} y2={innerH} />
			<line class="axis" x1="0" x2="0" y1="0" y2={innerH} />

			{#each xTicks as t}
				<line class="axis" x1={xScale(t)} x2={xScale(t)} y1={innerH} y2={innerH + 4} />
				<text class="tick" x={xScale(t)} y={innerH + 17} text-anchor="middle">{xAxisFormat(t)}</text>
			{/each}
			{#each yTicks as t}
				<text class="tick" x="-7" y={yScale(t) + 3.5} text-anchor="end">{fmtPct(t)}</text>
			{/each}

			<text class="axis-label" x={innerW / 2} y={innerH + 38} text-anchor="middle">{xLabel}</text>
			<text class="axis-label" x={-innerH / 2} y="-38" transform="rotate(-90)" text-anchor="middle">Mean turnout</text>

			{#each dots as d (d.ct)}
				<circle class="pt" cx={d.x} cy={d.y} r="2.6" />
			{/each}
			{#if line}<line class="fit" {...line} />{/if}
			{#if active}
				<circle class="pt hl" cx={active.x} cy={active.y} r="5.5" />
			{/if}
		</g>
	</svg>

	{#if active}
		<div
			class="tip {tipSide}"
			style="left:{margin.left + active.x}px; top:{margin.top + active.y}px"
			aria-hidden="true"
		>
			<div class="ct">Census tract {active.name}</div>
			<div class="row"><span>{xLabel}</span><b>{xValueFormat(active.xv)}</b></div>
			<div class="row"><span>Mean turnout</span><b>{fmtTurnout(active.yv, 1)}</b></div>
		</div>
	{/if}

	<p class="sr-only" aria-live="polite">
		{active ? `Census tract ${active.name}: ${xLabel} ${xValueFormat(active.xv)}, mean turnout ${fmtTurnout(active.yv, 1)}` : ''}
	</p>
</div>

<style>
	.scatter {
		position: relative;
		width: 100%;
		font-family: OpenSans, sans-serif;
	}
	svg {
		display: block;
		touch-action: pan-y; /* a vertical swipe still scrolls the page */
	}
	svg:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: 2px;
	}
	.axis {
		stroke: var(--brandGray);
		stroke-width: 1;
	}
	.grid {
		stroke: #efefec;
		stroke-width: 1;
	}
	.tick {
		font-size: 11px;
		fill: var(--brandGray70);
	}
	.axis-label {
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		fill: var(--brandGray80);
	}
	.pt {
		fill: black;
		fill-opacity: 0.55;
	}
	.pt.hl {
		fill: var(--brandYellow);
		fill-opacity: 1;
		stroke: black;
		stroke-width: 1.2;
	}
	.fit {
		stroke: black;
		stroke-width: 2;
	}

	.tip {
		position: absolute;
		z-index: 3;
		pointer-events: none;
		min-width: 150px;
		max-width: 230px;
		background: rgba(255, 255, 255, 0.95);
		border: 1px solid var(--brandGray);
		padding: 6px 9px;
		font-size: 12px;
		color: var(--brandGray90);
		transform: translate(12px, -50%);
	}
	.tip.left {
		transform: translate(calc(-100% - 12px), -50%);
	}
	.tip .ct {
		color: var(--brandGray60);
		font-size: 11px;
	}
	.tip .row {
		display: flex;
		justify-content: space-between;
		gap: 10px;
		font-variant-numeric: tabular-nums;
	}
	.tip .row span {
		color: var(--brandGray70);
	}
	.tip .row b {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}

	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0 0 0 0);
		white-space: nowrap;
		border: 0;
	}
</style>
