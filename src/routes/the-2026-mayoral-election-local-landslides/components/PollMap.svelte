<script>
	// Winner and margin in each 2026 voting subdivision, with a toggle between the poll areas and
	// bubbles sized by votes cast. Many polls are a single apartment building and barely show as
	// an area, so in the bubble view each poll's shape morphs into a circle whose area is
	// proportional to its votes, nudged apart by a force layout so none overlap.
	//
	// Drawn in the browser only: 1,356 shapes would bloat the prerendered HTML.
	import { onMount } from 'svelte';
	import { geoMercator, geoPath, geoArea, greatest, sum, scaleThreshold, range, transition, easeCubicInOut, interpolateNumber } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { shapeToCircle } from './morph.js';
	import { settleBubbles } from './bubbleLayout.js';
	import { MARGIN_BINS, MARGIN_TICKS, CHOW_RAMP, BRADFORD_RAMP, TIE, CHOW, BRADFORD, OTHERS } from './config.js';
	import data from '../data/polls_2026.json';

	const W = 1000;
	const H = 640;
	const DURATION = 900;

	const bin = scaleThreshold().domain(MARGIN_BINS).range(range(MARGIN_BINS.length + 1));
	function fill(p) {
		if (p.c === p.b) return TIE;
		return (p.c > p.b ? CHOW_RAMP : BRADFORD_RAMP)[bin(Math.abs(p.margin))];
	}

	// raw: thousands of points that never change after mount, so no deep reactivity
	let nodes = $state.raw([]);
	let wardPaths = $state.raw([]);
	let wardLabels = $state.raw([]);
	let view = $state('shapes');
	let width = $state(800);
	let hovered = $state(null);
	let k = $state(0); // bubble radius per √vote, in map units
	let viewBox = $state({ x: 0, y: 0, w: W, h: H }); // cropped to the city once drawn
	const radius = (v) => k * Math.sqrt(v);
	let pathEls = [];
	let morphs = null;
	let layout = null; // the bubble layout, settling in the background
	let progress = 0; // 0 = poll areas, 1 = bubbles

	// a ward name split into lines, as on the five-torontos maps: after each hyphen (kept at the
	// end of its line); otherwise at its last space if it's longer than 13 characters
	function labelLines(name) {
		const parts = name.split(/(?<=[-–—])/);
		if (parts.length > 1) return parts;
		const sp = name.lastIndexOf(' ');
		if (name.length > 13 && sp !== -1) return [name.slice(0, sp), name.slice(sp + 1)];
		return [name];
	}
	const LABEL_SIZE = 11; // px on screen, a pixel larger than on the five-torontos maps
	const LABEL_LEADING = 12;
	const LABEL_MIN_WIDTH = 800; // the narrowest map at which the names don't overlap

	// d3 wants rings wound clockwise; a shape wound the other way reads as "the whole globe minus it"
	function rewind(fc) {
		for (const f of fc.features) {
			if (geoArea(f) <= 2 * Math.PI) continue;
			const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
			for (const poly of polys) for (const ring of poly) ring.reverse();
		}
		return fc;
	}

	onMount(() => {
		const polls = rewind(structuredClone(data.polls));
		const wards = rewind(structuredClone(data.wards));
		const projection = geoMercator().angle(-17).fitExtent([[10, 10], [W - 10, H - 10]], wards);
		const path = geoPath(projection);

		// bubbles: area proportional to votes, sized to cover about 40% of the city, then pushed apart
		const totals = polls.features.map((f) => f.properties.c + f.properties.b + f.properties.o);
		const land = sum(polls.features, (f) => path.area(f));
		k = Math.sqrt((0.4 * land) / (Math.PI * sum(totals)));

		const built = polls.features.map((f, i) => {
			const p = { ...f.properties, total: totals[i] };
			p.margin = p.total ? (p.c - p.b) / p.total : 0; // + Chow ahead, − Bradford ahead
			// the morph uses one ring: the outer ring of the largest piece
			const g = f.geometry;
			const outer = g.type === 'Polygon' ? g.coordinates[0] : greatest(g.coordinates, (c) => geoArea({ type: 'Polygon', coordinates: c }))[0];
			const [x, y] = path.centroid(f);
			return { p, d: path(f), ring: outer.map((pt) => projection(pt)), x0: x, y0: y, x, y, r: radius(p.total), fill: fill(p) };
		});

		// settled in the background; setView() finishes it if the bubbles are asked for first
		layout = settleBubbles(built);

		nodes = built;
		wardPaths = wards.features.map((f) => path(f));
		wardLabels = wards.features.map((f) => {
			const [x, y] = path.centroid(f);
			return { name: f.properties.name, lines: labelLines(f.properties.name), x, y };
		});

		// the rotated city doesn't fill the frame, so crop to it (bubbles stay close to their polls)
		const PAD = 8;
		const [[x0, y0], [x1, y1]] = path.bounds(wards);
		viewBox = { x: x0 - PAD, y: y0 - PAD, w: x1 - x0 + 2 * PAD, h: y1 - y0 + 2 * PAD };

		return () => layout?.cancel();
	});

	function setView(next) {
		if (next === view) return;
		view = next;
		hovered = null;
		layout?.finish();
		morphs ??= nodes.map((n) => shapeToCircle(n.ring, n.x, n.y, Math.max(n.r, 0.1)));
		const from = progress;
		const to = next === 'bubbles' ? 1 : 0;
		const ease = interpolateNumber(from, to);
		transition('morph')
			.duration(DURATION * Math.abs(to - from))
			.ease(easeCubicInOut)
			.tween('morph', () => (t) => {
				progress = ease(t);
				for (let i = 0; i < nodes.length; i++) pathEls[i]?.setAttribute('d', morphs[i](progress));
			})
			.on('end', () => {
				// back on the map, swap in the exact shapes (with holes and every piece)
				if (to === 0) for (let i = 0; i < nodes.length; i++) pathEls[i]?.setAttribute('d', nodes[i].d);
			});
	}

	function showTip(event, n) {
		const box = event.currentTarget.ownerSVGElement.parentNode.getBoundingClientRect();
		hovered = { p: n.p, x: event.clientX - box.left, y: event.clientY - box.top };
	}

	const pct = (v) => `${(100 * v).toFixed(1)}%`;
	const scale = $derived(width / viewBox.w);
	const sizeKey = [100, 500, 1500];
</script>

<figure>
	<!-- the subtitle is the legend's title, over the lake -->
	<FigureTitle title="Votes and winning margin by poll, 2026 Toronto mayoral election" />

	<div class="controls">
		<div class="toggle" role="group" aria-label="Map view">
			{#each [['shapes', 'Poll areas'], ['bubbles', 'Bubbles sized by votes']] as [key, label] (key)}
				<button type="button" aria-pressed={view === key} onclick={() => setView(key)}>
					<svg class="icon" viewBox="0 0 14 14" aria-hidden="true">
						{#if key === 'shapes'}
							<path d="M4 2.5 L10 2.5 L13 11.5 L1 11.5 Z" />
						{:else}
							<circle cx="7" cy="7" r="5.5" />
						{/if}
					</svg>
					<span class="lbl" data-text={label}>{label}</span>
				</button>
			{/each}
		</div>
	</div>

	<div class="map" class:bubbles={view === 'bubbles'} bind:clientWidth={width}>
	<!-- over Lake Ontario, bottom right, on wider screens; above the map on phones -->
	<div class="legend">
		<div class="ramps">
			<p class="legend-title">Percentage points between the winner and the runner-up in each voting subdivision</p>
			<div class="ramp labels">
				<span class="ramp-name"></span>
				<!-- breakpoints at the edges between steps -->
				<span class="breaks" style:--steps={CHOW_RAMP.length}>
					{#each MARGIN_TICKS as t, i (t)}<span class="break" style:left="{(100 * i) / CHOW_RAMP.length}%">{t}</span>{/each}
				</span>
			</div>
			{#each [['Chow', CHOW_RAMP], ['Bradford', BRADFORD_RAMP]] as [name, ramp] (name)}
				<div class="ramp">
					<span class="ramp-name">{name}</span>
					{#each ramp as c, i (i)}<span class="step" style:background={c}></span>{/each}
				</div>
			{/each}
		</div>
		<div class="sizes" class:shown={view === 'bubbles'} aria-hidden={view !== 'bubbles'}>
			<span class="sizes-title">Votes cast</span>
			{#each sizeKey as v (v)}
				{@const r = Math.max(1, radius(v) * scale)}
				<span class="size">
					<svg width={2 * r + 2} height={2 * r + 2}><circle cx={r + 1} cy={r + 1} {r} /></svg>
					{v.toLocaleString('en-CA')}
				</span>
			{/each}
		</div>
	</div>

		<svg class="map-svg" viewBox="{viewBox.x} {viewBox.y} {viewBox.w} {viewBox.h}" role="img" aria-label="Map of the winner and margin in each poll">
			<g class="ghosts">
				{#each nodes as n, i (i)}<path d={n.d} />{/each}
			</g>
			<g class="polls">
				{#each nodes as n, i (i)}
					<path
						bind:this={pathEls[i]}
						d={n.d}
						fill={n.fill}
						onpointermove={(e) => showTip(e, n)}
						onpointerleave={() => (hovered = null)}
					/>
				{/each}
			</g>
			<!-- black ward lines on a white casing, as on the series' other maps -->
			<g class="wards">
				{#each wardPaths as d, i (i)}<path class="casing" {d} />{/each}
				{#each wardPaths as d, i (i)}<path class="line" {d} />{/each}
				<!-- names at each ward's centre with a white halo, as on the five-torontos maps; sized in
					 screen pixels, so divided by the map's scale -->
				{#if width >= LABEL_MIN_WIDTH}
					{#each wardLabels as l (l.name)}
						{@const lead = LABEL_LEADING / scale}
						<text class="ward-label" x={l.x} y={l.y - ((l.lines.length - 1) * lead) / 2} style:font-size="{LABEL_SIZE / scale}px" style:stroke-width="{3 / scale}px">
							{#each l.lines as line, j (j)}
								<tspan x={l.x} dy={j === 0 ? '0.35em' : lead}>{line}</tspan>
							{/each}
						</text>
					{/each}
				{/if}
			</g>
		</svg>

		{#if hovered}
			{@const p = hovered.p}
			<div class="tip" style:left="{Math.min(hovered.x + 14, width - 230)}px" style:top="{hovered.y + 14}px">
				<span class="tip-bold">Ward {p.w}, subdivision {p.s}</span>
				{#if p.total}
					<div class="stack" aria-hidden="true">
						<span style:width="{(100 * p.c) / p.total}%" style:background={CHOW}></span>
						<span style:width="{(100 * p.b) / p.total}%" style:background={BRADFORD}></span>
						<span style:width="{(100 * p.o) / p.total}%" style:background={OTHERS}></span>
					</div>
					<div class="stack-key">
						<span><i style:background={CHOW}></i>Chow {pct(p.c / p.total)}</span>
						<span><i style:background={BRADFORD}></i>Bradford {pct(p.b / p.total)}</span>
					</div>
				{/if}
				{p.total.toLocaleString('en-CA')} votes cast<br />
				<span class="tip-bold">{p.c === p.b ? 'Tied' : `${p.c > p.b ? 'Chow' : 'Bradford'} by ${(100 * Math.abs(p.margin)).toFixed(1)} pts`}</span>
			</div>
		{/if}
	</div>

	<figcaption class="note">
		Election-day votes only. Advance and mail-in votes are reported for each ward as a whole and can't be mapped. In the
		bubble view each circle's area is proportional to the votes cast at that poll, and circles are nudged apart so none
		overlap, so a bubble sits near its poll rather than exactly on it.
	</figcaption>
</figure>

<style>
	figure {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	.controls {
		display: flex;
		justify-content: center;
		margin: 19px 0 12px;
	}
	/* segmented toggle as on the toronto-turnout map: white buttons with a light grey border,
	   13px; the chosen one bold at full strength, the other faded. Neighbours overlap by 1px so
	   the borders don't double up */
	.toggle {
		display: inline-flex;
		gap: 10px;
	}
	.toggle button {
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		margin: 0;
		padding: 5px 10px;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	/* a little poll shape or circle before each label */
	.icon {
		width: 13px;
		height: 13px;
		flex: none;
	}
	.icon path,
	.icon circle {
		fill: var(--brandGray);
		stroke: var(--brandGray80);
		stroke-width: 1;
		stroke-linejoin: round;
	}
	.toggle button:hover {
		border-color: #9ba1a8;
		position: relative;
	}
	.toggle button[aria-pressed='false'] {
		opacity: 0.75;
	}
	.toggle button[aria-pressed='false']:hover {
		opacity: 0.99;
	}
	.toggle button[aria-pressed='true'] {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandBlack);
		position: relative;
	}
	/* each label reserves its bold width, so a button doesn't change size when chosen */
	.lbl {
		display: inline-flex;
		flex-direction: column;
		align-items: center;
	}
	.lbl::after {
		content: attr(data-text);
		height: 0;
		overflow: hidden;
		visibility: hidden;
		font-family: OpenSansBold, sans-serif;
	}
	.toggle button:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: 1px;
		position: relative;
	}

	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: flex-end;
		gap: 10px 36px;
		margin-bottom: 8px;
		font-size: 13px;
		color: var(--brandGray70);
	}
	/* as wide as the ramps (name column plus four steps) */
	.legend-title {
		max-width: 222px;
		margin: 0 0 6px;
		line-height: 1.35;
		color: var(--brandGray90);
	}
	@media (min-width: 700px) {
		.legend {
			position: absolute;
			right: 2%;
			bottom: 9%;
			flex-direction: column;
			align-items: flex-start;
			gap: 12px;
			margin: 0;
			z-index: 1;
		}
	}
	.ramp {
		display: flex;
		align-items: center;
		gap: 0;
		margin-bottom: 3px;
	}
	.ramp-name {
		width: 62px;
	}
	.legend {
		--step: 40px;
	}
	.step {
		width: var(--step);
		height: 12px;
	}
	/* breakpoint labels, each centred on the edge between two steps */
	.breaks {
		position: relative;
		display: block;
		width: calc(var(--steps) * var(--step));
		height: 16px;
	}
	.break {
		position: absolute;
		bottom: 0;
		transform: translateX(-50%);
		font-size: 12px;
		line-height: 1;
	}
	.sizes {
		display: flex;
		align-items: flex-end;
		gap: 14px;
		opacity: 0;
		transition: opacity 0.9s;
	}
	.sizes.shown {
		opacity: 1;
	}
	.sizes-title {
		margin-right: -4px;
	}
	.size {
		display: inline-flex;
		align-items: flex-end;
		gap: 4px;
	}
	.size circle {
		fill: none;
		stroke: var(--brandGray60);
	}

	.map {
		position: relative;
	}
	.map-svg {
		display: block;
		width: 100%;
		height: auto;
		overflow: visible; /* bubbles at the city's edge can be pushed just past the crop */
	}
	.ghosts path {
		fill: #ececec;
		stroke: #fff;
		stroke-width: 0.3;
		pointer-events: none;
	}
	.polls path {
		stroke: #fff;
		stroke-width: 0.3;
		fill-opacity: 0.9;
	}
	.polls path:hover {
		stroke: var(--brandGray90);
		stroke-width: 1.2;
	}
	.wards path {
		fill: none;
		pointer-events: none;
		stroke-linejoin: round;
	}
	.wards .casing {
		stroke: #fff;
		stroke-width: 3;
	}
	.wards .line {
		stroke: #000;
		stroke-width: 1;
	}
	/* as .ward-label on the five-torontos maps (size and halo width are set inline, per scale) */
	.ward-label {
		font-family: OpenSans, sans-serif;
		fill: var(--brandGray90);
		text-anchor: middle;
		paint-order: stroke;
		stroke: white;
		stroke-opacity: 0.84; /* the white halo only; the text stays solid */
		stroke-linejoin: round;
		pointer-events: none;
	}
	.ghosts,
	.wards {
		transition: opacity 0.9s;
	}
	.bubbles .ghosts,
	.bubbles .wards {
		opacity: 0;
	}

	.tip {
		position: absolute;
		pointer-events: none;
		background: #fff;
		border: 1px solid #8a8a8a;
		padding: 8px 10px;
		font-size: 12px;
		line-height: 1.5;
		width: 200px;
		z-index: 2;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
		color: var(--brandGray90);
	}
	/* the installed bold face, not a browser-synthesized weight of OpenSans */
	.tip-bold {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}
	.stack {
		display: flex;
		height: 10px;
		margin: 6px 0 4px;
		background: #eee;
	}
	.stack span {
		display: block;
		height: 100%;
	}
	.stack-key {
		display: flex;
		flex-wrap: wrap;
		gap: 0 10px;
		margin-bottom: 4px;
		font-size: 11px;
	}
	.stack-key span {
		display: inline-flex;
		align-items: center;
		gap: 4px;
	}
	.stack-key i {
		display: inline-block;
		width: 8px;
		height: 8px;
	}

	/* as wide as the body text's paragraphs (.text's 694px content box), not the map */
	.note {
		max-width: 694px;
		margin: 14px auto 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}

	@media (max-width: 520px) {
		.legend {
			--step: 34px;
		}
		.ramp-name {
			width: 56px;
		}
	}
</style>
