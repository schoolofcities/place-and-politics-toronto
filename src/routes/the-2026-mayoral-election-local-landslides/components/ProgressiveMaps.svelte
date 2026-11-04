<script>
	// Small multiples: each progressive candidate's election-day share by census tract, for the
	// ten candidates in the where-the-votes-came-from chart, with the former City of Toronto
	// outlined. One colour scale for all, so the maps compare. Five across on wide screens,
	// wrapping to three and then two.
	//
	// Drawn in the browser only: ten copies of 585 tracts would bloat the prerendered HTML.
	import { onMount } from 'svelte';
	import { geoMercator, geoPath, geoArea, scaleThreshold } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import data from '../data/tracts_progressive.json';
	// the five-torontos page's former municipalities: the city's edge and the old City of Toronto
	import municipalities from '../data/former_municipalities.geo.json';

	const W = 300;
	const H = 190;
	const BREAKS = [0.1, 0.25, 0.5];
	const TICKS = [0, ...BREAKS]; // legend labels, at the step edges (the last step is open)
	const COLOURS = ['#fbf8ee', '#fbe3a0', '#f5b94a', '#e0761f']; // white, yellow, orange
	const NO_DATA = '#d4d4d4';
	const threshold = scaleThreshold().domain(BREAKS).range(COLOURS);
	const colour = (v) => (v == null ? NO_DATA : threshold(v));

	let tracts = $state.raw([]); // { d, s: [share per candidate] }
	let areas = $state.raw([]); // the six former municipalities, for the city's edge
	let oldCity = $state('');

	// d3 wants rings wound clockwise; a shape wound the other way reads as "the whole globe minus it"
	function rewind(f) {
		if (geoArea(f) <= 2 * Math.PI) return f;
		const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
		for (const poly of polys) for (const ring of poly) ring.reverse();
		return f;
	}

	onMount(() => {
		const fc = structuredClone(data.tracts);
		fc.features.forEach(rewind);
		const munis = structuredClone(municipalities);
		munis.features.forEach(rewind);
		const projection = geoMercator().angle(-17).fitExtent([[2, 2], [W - 2, H - 2]], munis);
		const path = geoPath(projection);
		tracts = fc.features.map((f) => ({ d: path(f), s: f.properties.s }));
		areas = munis.features.map((f) => path(f));
		oldCity = path(munis.features.find((f) => f.properties.name === 'Old Toronto'));
	});
</script>

<figure>
	<FigureTitle
		title="Progressive candidates' vote share in Toronto mayoral elections"
	/>

	<p class="legend-title">% of votes by census tract</p>
	<div class="legend" aria-hidden="true">
		<div class="ramp">
			<div class="breaks" style:--steps={COLOURS.length}>
				{#each TICKS as t, i (t)}
					<span class="break" style:left="{(100 * i) / COLOURS.length}%">{Math.round(100 * t)}%</span>
				{/each}
			</div>
			<div class="steps">
				{#each COLOURS as c (c)}<span class="step" style:background={c}></span>{/each}
			</div>
		</div>
		<!-- set apart from the scale, off to its right -->
		<div class="no-data">
			<span class="no-data-label">No data</span>
			<span class="step no-data-swatch" style:background={NO_DATA}></span>
		</div>
	</div>

	<!-- the callout's arrowhead -->
	<svg class="defs" aria-hidden="true">
		<defs>
			<marker id="callout-head" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
				<path d="M0,1 L9,5 L0,9 Z" fill="#191919" />
			</marker>
		</defs>
	</svg>

	<div class="grid">
		{#each data.candidates as c, i (c.key)}
			<div class="cell">
				<p class="name">
					{c.label} <span class="year">{c.year}</span>
					<span class="result" class:won={c.won}>
						<!-- a ballot box: ticked for a win, crossed for a loss -->
						<svg class="ballot" viewBox="0 0 12 12" aria-hidden="true">
							<rect x="0.75" y="0.75" width="10.5" height="10.5" />
							{#if c.won}
								<path d="M2.8 6.2 L5 8.4 L9.3 3.6" />
							{:else}
								<path d="M3.3 3.3 L8.7 8.7 M8.7 3.3 L3.3 8.7" />
							{/if}
						</svg>{c.won ? 'Won' : 'Lost'}
					</span>
				</p>
				<svg class="small-map" viewBox="0 0 {W} {H}" role="img" aria-label="{c.label} {c.year}, vote share by census tract">
					<!-- the city's edge, as on the five-torontos maps: a wide outline of the former
						 municipalities, then their fill on top, hiding the lines between them -->
					{#each areas as d, j (j)}<path class="city-edge" {d} />{/each}
					{#each areas as d, j (j)}<path class="city-fill" {d} />{/each}
					{#each tracts as t, j (j)}<path class="tract" d={t.d} fill={colour(t.s[i])} />{/each}
					{#if oldCity}<path class="old-city" d={oldCity} />{/if}
					<!-- on the first map only: name the outline, from the lake to its eastern edge -->
					{#if oldCity && i === 0}
						<g class="callout">
							<path class="arrow" d="M212,158 Q180,158 148,138" marker-end="url(#callout-head)" />
							<text x="252" y="161">Former City</text>
							<text x="252" y="176">of Toronto</text>
						</g>
					{/if}
				</svg>
			</div>
		{/each}
	</div>

	<figcaption class="note">
		Percent of election-day votes in each 2021 census tract. Advance and mail-in votes are not included. Votes are
		apportioned from polls to tracts.
	</figcaption>
</figure>

<style>
	figure {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	/* the legend's heading, in its colour and size, just above it */
	.legend-title {
		margin: 0 0 4px;
		text-align: center;
		font-size: 13px;
		color: var(--brandGray70);
	}
	.legend {
		display: flex;
		justify-content: center;
		align-items: flex-end;
		gap: 18px;
		margin: 0 0 24px;
		font-size: 12px;
		color: var(--brandGray70);
	}
	.steps {
		display: flex;
	}
	.legend {
		--step: 64px;
	}
	.ramp,
	.no-data {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}
	.no-data-label {
		line-height: 1;
		height: 14px;
		display: flex;
		align-items: flex-end;
	}
	/* half a step wide (scoped under .no-data so it wins over .step's width) */
	.no-data .no-data-swatch {
		width: calc(var(--step) / 2);
	}
	.step {
		width: var(--step);
		height: 12px;
	}
	/* breakpoint labels, each centred on the edge between two steps */
	.breaks {
		position: relative;
		width: calc(var(--steps) * var(--step));
		height: 14px;
	}
	.break {
		position: absolute;
		bottom: 0;
		transform: translateX(-50%);
		line-height: 1;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(5, minmax(0, 1fr));
		gap: 14px 10px;
	}
	@media (max-width: 760px) {
		.grid {
			grid-template-columns: repeat(3, minmax(0, 1fr));
		}
	}
	@media (max-width: 480px) {
		.grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
		.legend {
			--step: 56px;
		}
	}
	/* the candidate's last name in the installed italic; the year and result set their own faces */
	.name {
		margin: 0 0 -6px;
		font-family: OpenSansItalic, sans-serif;
		font-size: 13px;
		text-align: center;
		color: var(--brandGray90);
	}
	.year {
		font-family: OpenSans, sans-serif;
		color: var(--brandBlack);
	}
	/* whether the candidate won: "Won" bold and dark, "Lost" plain and grey, after a thin rule */
	.result {
		margin-left: 4px;
		padding-left: 6px;
		border-left: 1px solid var(--brandGray);
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		color: var(--brandGray60);
	}
	.result.won {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandGray90);
	}
	.ballot {
		display: inline-block;
		width: 11px;
		height: 11px;
		margin-right: 4px;
		vertical-align: -1px;
	}
	.ballot rect {
		fill: #fff;
		stroke: currentColor;
		stroke-width: 1;
	}
	.ballot path {
		fill: none;
		stroke: currentColor;
		stroke-width: 1.6;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.small-map {
		display: block;
		width: 100%;
		height: auto;
		/* keeps the cell's shape before the maps draw */
		aspect-ratio: 300 / 190;
	}
	.city-edge {
		fill: none;
		stroke: var(--brandGray70);
		stroke-width: 2;
		stroke-linejoin: round;
	}
	.city-fill {
		fill: #eeeeee;
		stroke: #eeeeee;
		stroke-width: 0.5;
	}
	.tract {
		stroke: #fff;
		stroke-width: 0.25;
	}
	.old-city {
		fill: none;
		stroke: #000;
		stroke-width: 1;
		stroke-linejoin: round;
	}
	.defs {
		position: absolute;
		width: 0;
		height: 0;
	}
	.callout text {
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		fill: var(--brandGray90);
		text-anchor: middle;
	}
	.callout .arrow {
		fill: none;
		stroke: var(--brandGray90);
		stroke-width: 1;
	}
	.note {
		max-width: 694px;
		margin: 14px auto 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
