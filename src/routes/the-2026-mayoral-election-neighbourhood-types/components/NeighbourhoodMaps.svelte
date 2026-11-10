<script>
	// The page's lead graphic: small multiples of census tracts, each candidate's 2026 vote share beside
	// six neighbourhood traits, so the patterns can be compared at a glance. Each map is shaded in fourths
	// of tracts (so every map uses its whole colour range), with Old Toronto outlined and named on the first map.
	// Laid out like the small-multiple maps on the local-landslides page, and as wide as they are.
	// Data: ../data/hero_maps.json (analysis/election_2026/03_neighbourhood_types_page_data.ipynb, Section 7); the tract
	// and municipality shapes are ../data/new_votes_tracts.geojson and new_votes_municipalities.geojson.
	//
	// Drawn in the browser only: eight copies of 585 tracts would bloat the prerendered HTML.
	import { onMount } from 'svelte';
	import { geoMercator, geoPath, scaleThreshold } from 'd3';
	import { heroMaps, newVotesTracts, newVotesMunicipalities } from './data.js';
	import { HERO_RAMPS } from './config.js';

	const W = 300;
	const NO_DATA = '#d4d4d4';

	// one colour function per map
	const maps = heroMaps.maps.map((m) => {
		const step = scaleThreshold().domain(m.breaks).range(HERO_RAMPS[m.ramp]);
		return { ...m, colour: (v) => (v == null ? NO_DATA : step(v)) };
	});

	// the three colour scales, each explained once above the maps
	const legend = [
		{ key: 'chow', label: "Chow's vote share" },
		{ key: 'bradford', label: "Bradford's vote share" },
		{ key: 'traits', label: 'Neighbourhood traits' }
	];

	let paths = $state.raw([]); // one path per tract, in the order of heroMaps.tracts
	let areas = $state.raw([]); // the six former municipalities, for the city's edge
	let oldCity = $state('');
	let callout = $state(null); // where to name Old Toronto on the first map
	let H = $state(156); // the shape of the city, so the cells keep their size before the maps draw
	let cellWidth = $state(200);
	const scale = $derived(W / cellWidth); // svg units per screen pixel, so the callout's text is the same size at any width

	onMount(() => {
		const fc = newVotesTracts;
		const [[, y0], [, y1]] = geoPath(geoMercator().angle(-17).fitWidth(W - 4, fc)).bounds(fc);
		H = Math.ceil(y1 - y0) + 4;
		const projection = geoMercator().angle(-17).fitExtent([[2, 2], [W - 2, H - 2]], fc);
		const draw = geoPath(projection).digits(1);
		paths = fc.features.map((f) => draw(f));
		areas = newVotesMunicipalities.features.map((f) => draw(f));
		const old = newVotesMunicipalities.features.find((f) => f.properties.name === 'Old Toronto');
		oldCity = draw(old);
		const [[ox0, oy0], [ox1, oy1]] = draw.bounds(old);
		callout = { x1: ox1, y1: oy1, cx: (ox0 + ox1) / 2 };
	});
</script>

<figure aria-label="Maps of Toronto's census tracts: Chow's and Bradford's 2026 vote share beside six neighbourhood traits">
	<div class="grid">
		{#each maps as m, i (m.key)}
			<div class="cell">
				<p class="name">{m.label}</p>
				<svg
					class="small-map"
					viewBox="0 0 {W} {H}"
					style:aspect-ratio="{W} / {H}"
					role="img"
					aria-label="{m.label}, by census tract, shaded in fourths of tracts from lower (lightest) to higher (darkest)"
					bind:clientWidth={cellWidth}
				>
					<!-- the city's edge, as on the local-landslides maps: a wide outline of the former municipalities, then
						 their fill on top, hiding the lines between them and showing through the lightest tracts -->
					{#each areas as d, j (j)}<path class="city-edge" {d} />{/each}
					{#each areas as d, j (j)}<path class="city-fill" {d} />{/each}
					{#each paths as d, j (j)}<path class="tract" {d} fill={m.colour(m.values[j])} />{/each}
					{#if oldCity}<path class="old-city" d={oldCity} />{/if}
					<!-- on the first map only: name the outline -->
					{#if i === 0 && callout}
						{@const fs = 11 * scale}
						{@const tx = W - 4}
						{@const ty = H - 7}
						<!-- the name sits in the lake, bottom right, with an arrow to the outline's lakeshore corner -->
						<defs>
							<marker id="old-toronto-head" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
								<path d="M0,1 L9,5 L0,9 Z" fill="#191919" />
							</marker>
						</defs>
						<g class="callout" style:font-size="{fs}px">
							<path class="arrow" marker-end="url(#old-toronto-head)" d="M{tx - 5.6 * fs - 5},{ty - 0.3 * fs} Q{callout.x1 + 6 * scale},{ty - 0.3 * fs} {callout.x1 - 1 * scale},{callout.y1 - 26 * scale}" />
							<text x={tx} y={ty}>Old Toronto</text>
						</g>
					{/if}
				</svg>
			</div>
		{/each}
	</div>


	<!-- the three colour scales, one compact row under the maps: each runs from lower to higher -->
	<div class="legend" aria-hidden="true">
		{#each legend as l (l.key)}
			<div class="scale">
				<p class="legend-title">{l.label}</p>
				<div class="bar">
					<span>Lower</span>
					<span class="steps">{#each HERO_RAMPS[l.key] as c (c)}<span class="step" style:background={c}></span>{/each}</span>
					<span>Higher</span>
				</div>
			</div>
		{/each}
	</div>
</figure>

<style>
	figure {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	/* the three scales, small and in one row under the maps: a heading, then Lower, the four steps and Higher */
	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px 22px;
		margin: 12px 0 0;
		color: var(--brandGray70);
	}
	.scale {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}
	.legend-title {
		margin: 0;
		font-size: 11px;
		line-height: 1.2;
		color: var(--brandGray70);
	}
	.bar {
		display: flex;
		align-items: center;
		gap: 5px;
		font-size: 11px;
		line-height: 1;
	}
	.steps {
		display: flex;
	}
	.step {
		width: 16px;
		height: 8px;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 16px 10px;
	}
	@media (max-width: 520px) {
		.grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
		.legend {
			gap: 6px 18px;
			margin-top: 10px;
		}
	}
	.cell {
		min-width: 0;
	}
	/* the map's name: regular weight, as the names over the local-landslides maps, bottom-aligned so one- and two-line names sit alike */
	.name {
		margin: 0 0 2px;
		min-height: 2.6em;
		display: flex;
		align-items: flex-end;
		justify-content: center;
		font-size: 12px;
		line-height: 1.3;
		text-align: center;
		text-wrap: balance;
		color: var(--brandGray90);
	}
	.small-map {
		display: block;
		width: 100%;
		height: auto;
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
		pointer-events: none;
	}
	.callout text {
		font-family: OpenSans, sans-serif;
		fill: var(--brandGray90);
		text-anchor: end;
	}
	.callout .arrow {
		fill: none;
		stroke: var(--brandGray90);
		stroke-width: 0.8;
	}

</style>
