<script>
	// The change in Olivia Chow's share of election-day votes between 2023 and 2026
	// in each census tract, relative to the citywide change (her share rose almost everywhere, so
	// the absolute change only shows where she did better; relative to the city shows where she did
	// better or worse than the city as a whole). Drawn like the poll map beside it: shaded tracts, with a toggle to
	// bubbles sized by votes cast (each tract's shape morphs into a circle whose area is
	// proportional to its 2026 votes, nudged apart by a force layout so none overlap).
	//
	// Shares are the last two of tracts_progressive.json's per-candidate shares (Chow 2023, Chow
	// 2026); votes are from tracts_votes.json (../data/prep_change.py); the boundaries drawn are the
	// six former municipalities' (the series' former_municipalities.geo.json). Drawn in the browser only, as the other maps are.
	import { onMount } from 'svelte';
	import { geoMercator, geoPath, geoArea, greatest, sum, forceSimulation, forceX, forceY, forceCollide, scaleThreshold, range, transition, easeCubicInOut, interpolateNumber } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { shapeToCircle } from './morph.js';
	import tractData from '../data/tracts_progressive.json';
	import tractVotes from '../data/tracts_votes.json';
	import { coreSuburbColumns } from './data.js';
	import municipalities from '../data/former_municipalities.geo.json'; // the city's extent and the old City of Toronto

	const W = 1000;
	const H = 640;
	const DURATION = 900;

	// Chow's citywide share of election-day votes in a year: the former City of Toronto's and the
	// suburbs' parts, as on the stacked chart. The change between the two is the benchmark.
	const cityShare = (year) =>
		coreSuburbColumns.find((c) => c.key === year).segments
			.filter((seg) => seg.key !== 'Votes for Other Candidates')
			.reduce((total, seg) => total + seg.value, 0);
	const CITY_CHANGE = cityShare('2026') - cityShare('2023');

	// a tract's change minus the citywide change, in percentage points: a bipolar ramp, orange where
	// she gained less than the city did, white about level, purple where she gained more. The steps
	// are under −10, −10 to −5, −5 to −2, within 2 of level, then 2 to 5, 5 to 10 and 10 or more.
	const BREAKS = [-0.1, -0.05, -0.02, 0.02, 0.05, 0.1];
	const TICKS = ['−10', '−5', '−2', '+2', '+5', '+10']; // legend labels, at the edges between steps
	const RAMP = ['#c4651a', '#e5955a', '#f4cfae', '#f6f4f3', '#d4bde0', '#a678b8', '#6f4584'];
	const NO_DATA = '#d4d4d4';
	// the pop-up's paired bars: her share in 2023 (lighter) above her share in 2026 (darker)
	const SHARE_2023 = '#c9a6d5';
	const SHARE_2026 = '#a678b8';
	const MUNI_NAMES = { Toronto: 'Former City of Toronto' }; // the others are named as they are
	const bin = scaleThreshold().domain(BREAKS).range(range(BREAKS.length + 1));
	const fill = (p) => (p.relative == null ? NO_DATA : RAMP[bin(p.relative)]);

	// raw: hundreds of shapes that never change after mount, so no deep reactivity
	let nodes = $state.raw([]);
	let muniPaths = $state.raw([]); // the six former municipalities' outlines
	let muniLabels = $state.raw([]); // their names, at the label points in the municipalities file
	let view = $state('shapes');
	let width = $state(800);
	let hovered = $state(null);
	let k = $state(0); // bubble radius per √vote, in map units
	let viewBox = $state({ x: 0, y: 0, w: W, h: H }); // cropped to the city once drawn
	// a municipality's name split into lines as ward names are on the poll map: after each hyphen, or
	// at the last space if it's longer than 13 characters (so the former City of Toronto takes two)
	function labelLines(name) {
		const parts = name.split(/(?<=[-–—])/);
		if (parts.length > 1) return parts;
		const sp = name.lastIndexOf(' ');
		if (name.length > 13 && sp !== -1) return [name.slice(0, sp), name.slice(sp + 1)];
		return [name];
	}
	const LABEL_SIZE = 11; // px on screen, as on the poll map
	const LABEL_LEADING = 12;
	const LABEL_MIN_WIDTH = 560; // the narrowest map at which the six names fit
	const radius = (v) => k * Math.sqrt(v);
	let pathEls = [];
	let morphs = null;
	let progress = 0; // 0 = tracts, 1 = bubbles

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
		const tracts = rewind(structuredClone(tractData.tracts));
		const munis = rewind(structuredClone(municipalities));
		const projection = geoMercator().angle(-17).fitExtent([[10, 10], [W - 10, H - 10]], munis);
		const path = geoPath(projection);

		// bubbles: area proportional to votes, sized to cover about 40% of the city, then pushed apart
		const totals = tractVotes.map((v) => v[1]);
		const land = sum(tracts.features, (f) => path.area(f));
		k = Math.sqrt((0.4 * land) / (Math.PI * sum(totals)));

		const built = tracts.features.map((f, i) => {
			const [before, after] = f.properties.s.slice(-2); // Chow 2023, Chow 2026
			const ok = before != null && after != null;
			const [, , muni, ward, wardName] = tractVotes[i];
			const change = ok ? after - before : null;
			const p = { before, after, change, relative: ok ? change - CITY_CHANGE : null, total: totals[i], muni, ward, wardName };
			// the morph uses one ring: the outer ring of the largest piece
			const g = f.geometry;
			const outer = g.type === 'Polygon' ? g.coordinates[0] : greatest(g.coordinates, (c) => geoArea({ type: 'Polygon', coordinates: c }))[0];
			const [x, y] = path.centroid(f);
			return { p, d: path(f), ring: outer.map((pt) => projection(pt)), x0: x, y0: y, x, y, r: radius(p.total), fill: fill(p) };
		});

		forceSimulation(built)
			.force('x', forceX((d) => d.x0).strength(0.25))
			.force('y', forceY((d) => d.y0).strength(0.25))
			.force('collide', forceCollide((d) => d.r + 0.4).iterations(3))
			.stop()
			.tick(400);

		nodes = built;
		muniPaths = munis.features.map((f) => path(f));
		muniLabels = munis.features.map((f) => {
			const { name, label_lon, label_lat } = f.properties;
			const shown = name === 'Old Toronto' ? 'Former City of Toronto' : name;
			const [x, y] = projection([label_lon, label_lat]);
			return { name: shown, lines: labelLines(shown), x, y };
		});

		// the rotated city doesn't fill the frame, so crop to it (bubbles stay close to their tracts)
		const PAD = 8;
		const [[x0, y0], [x1, y1]] = path.bounds(munis);
		viewBox = { x: x0 - PAD, y: y0 - PAD, w: x1 - x0 + 2 * PAD, h: y1 - y0 + 2 * PAD };
	});

	function setView(next) {
		if (next === view) return;
		view = next;
		hovered = null;
		morphs ??= nodes.map((n) => shapeToCircle(n.ring, n.x, n.y, Math.max(n.r, 0.1)));
		const from = progress;
		const to = next === 'bubbles' ? 1 : 0;
		const ease = interpolateNumber(from, to);
		transition('morph-change')
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
	const signed = (v) => `${v < 0 ? '−' : '+'}${Math.abs(100 * v).toFixed(1)}`;
	const scale = $derived(width / viewBox.w);
	const sizeKey = [500, 1500, 3000];
</script>

<figure>
	<FigureTitle title="Where Chow did relatively better in 2026 than in 2023" />

	<div class="controls">
		<div class="toggle" role="group" aria-label="Map view">
			{#each [['shapes', 'Census tracts'], ['bubbles', 'Bubbles sized by votes']] as [key, label] (key)}
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
	<!-- above the map: the title is too long to sit over the lake without covering tracts -->
	<div class="legend">
		<div class="ramps">
			<p class="legend-title">Percentage point difference in Chow’s performance relative to the citywide average in 2026 versus 2023</p>
			<div class="ramp labels">
				<!-- breakpoints at the edges between steps -->
				<span class="breaks" style:--steps={RAMP.length}>
					{#each TICKS as t, i (t)}<span class="break" style:left="{(100 * (i + 1)) / RAMP.length}%">{t}</span>{/each}
				</span>
			</div>
			<div class="ramp">
				{#each RAMP as c, i (i)}<span class="step" style:background={c}></span>{/each}
			</div>
			<div class="ends"><span>Worse</span><span>Better</span></div>
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

		<svg class="map-svg" viewBox="{viewBox.x} {viewBox.y} {viewBox.w} {viewBox.h}" role="img" aria-label="Map of the change in Olivia Chow's share of the vote in each census tract">
			<g class="ghosts">
				{#each nodes as n, i (i)}<path d={n.d} />{/each}
			</g>
			<g class="polls">
				{#each nodes as n, i (i)}
					<path
						bind:this={pathEls[i]}
						d={n.d}
						fill={n.fill}
						role="presentation"
						onpointermove={(e) => showTip(e, n)}
						onpointerleave={() => (hovered = null)}
					/>
				{/each}
			</g>
			<!-- the former municipalities' boundaries, black on a white casing as the ward lines are on the
				 poll map, to set the core against the suburbs; the casings go first so no line is covered -->
			<g class="munis">
				{#each muniPaths as d, i (i)}<path class="casing" {d} />{/each}
				{#each muniPaths as d, i (i)}<path class="line" {d} />{/each}
				<!-- names with a white halo, set as the ward names are on the poll map: sized in screen pixels,
					 so divided by the map's scale -->
				{#if width >= LABEL_MIN_WIDTH}
					{#each muniLabels as l (l.name)}
						{@const lead = LABEL_LEADING / scale}
						<text class="muni-label" x={l.x} y={l.y - ((l.lines.length - 1) * lead) / 2} style:font-size="{LABEL_SIZE / scale}px" style:stroke-width="{3 / scale}px">
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
			<div class="tip" style:left="{Math.min(hovered.x + 14, width - 250)}px" style:top="{hovered.y + 14}px">
				<span class="tip-bold">{MUNI_NAMES[p.muni] ?? p.muni}, Ward {p.ward} ({p.wardName})</span>
				{#if p.change == null}
					<br />No data
				{:else}
					<!-- paired bars on the same 0 to 100% scale, unlabelled: her 2023 share above her 2026 share -->
					<div class="pair" aria-hidden="true">
						<div class="track"><span style:width="{100 * p.before}%" style:background={SHARE_2023}></span></div>
						<div class="track"><span style:width="{100 * p.after}%" style:background={SHARE_2026}></span></div>
					</div>
					<div class="stack-key">
						<span><i style:background={SHARE_2023}></i>2023: {pct(p.before)}</span>
						<span><i style:background={SHARE_2026}></i>2026: {pct(p.after)}</span>
					</div>
					{p.total.toLocaleString('en-CA')} votes cast in 2026<br />
					<span class="tip-bold">{signed(p.change)} percentage points</span><br />
					{#if Math.abs(p.relative) < 0.0005}Level with the citywide gain{:else}{p.relative > 0 ? 'Above' : 'Below'} the citywide gain by {(100 * Math.abs(p.relative)).toFixed(1)} points{/if}
				{/if}
			</div>
		{/if}
	</div>

	<figcaption class="note">
		Election-day votes only, apportioned from polls to 2021 census tracts. Advance and mail-in votes are not included.
		In the bubble view each circle's area is proportional to the votes cast in that tract in 2026, and circles are
		nudged apart so none overlap, so a bubble sits near its tract rather than exactly on it. Chow's share rose in every
		tract, so tracts are coloured by how her gain compares with the citywide gain of {(100 * CITY_CHANGE).toFixed(1)} points (her
		election-day share rose from {pct(cityShare('2023'))} to {pct(cityShare('2026'))}): purple where it was larger, orange where it was smaller. The pop-up
		shows the tract's actual gain. The black lines are the boundaries of the former municipalities: the former City of Toronto, East York, York, Etobicoke, North York and Scarborough.
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
		flex-direction: column;
		align-items: center;
		gap: 10px;
		margin-bottom: 4px;
		font-size: 13px;
		color: var(--brandGray70);
	}
	.ramps {
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.legend-title {
		text-align: center;
		max-width: 460px;
		margin: 0 0 6px;
		line-height: 1.35;
		color: var(--brandGray90);
	}
	.ramp {
		display: flex;
		align-items: center;
		gap: 0;
		margin-bottom: 3px;
	}
	.legend {
		--step: 32px;
	}
	/* under the ramp's ends: which way is more and which less */
	.ends {
		width: calc(7 * var(--step));
		display: flex;
		justify-content: space-between;
		margin-top: 2px;
		font-size: 11px;
		color: var(--brandGray60);
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
	.munis path {
		fill: none;
		pointer-events: none;
		stroke-linejoin: round;
	}
	.munis .casing {
		stroke: #fff;
		stroke-width: 3;
	}
	.munis .line {
		stroke: #000;
		stroke-width: 1;
	}
	/* as .ward-label on the poll map (size and halo width are set inline, per scale) */
	.muni-label {
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
	.munis {
		transition: opacity 0.9s;
	}
	.bubbles .ghosts,
	.bubbles .munis {
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
		width: 220px;
		z-index: 2;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
		color: var(--brandGray90);
	}
	/* the installed bold face, not a browser-synthesized weight of OpenSans */
	.tip-bold {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}
	/* the pop-up's paired bars and their key: each bar 10px tall as on the poll map, on a grey 0 to 100% track */
	.pair {
		display: flex;
		flex-direction: column;
		gap: 3px;
		margin: 6px 0 4px;
	}
	.track {
		height: 10px;
		background: #eee;
	}
	.track span {
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
			--step: 30px;
		}
	}
</style>
