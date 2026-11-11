<script>
	// The page's lead graphic: small multiples of census tracts, each candidate's 2026 vote share beside
	// six neighbourhood traits, so the patterns can be compared at a glance. Each map is shaded in fourths
	// of tracts (so every map uses its whole colour range), with the boundaries between the six former municipalities drawn on.
	// Two columns on every screen: Chow's and Bradford's maps side by side, each with its own scale above it,
	// then the traits' scale, then the six trait maps, the three that go with each candidate running down
	// under their map (heroMaps.maps lists Chow and his three traits, then Bradford and his).
	// Data: ../data/hero_maps.json (analysis/election_2026/03_neighbourhood_types_page_data.ipynb, Section 7); the tract
	// and municipality shapes are ../data/new_votes_tracts.geojson and new_votes_municipalities.geojson, and the
	// boundaries between the municipalities and between the wards ../data/municipality_lines.geojson and
	// ward_lines.geojson (../data/prep_boundary_lines.py). A toggle by the traits' scale picks which, or none.
	//
	// Drawn in the browser only: eight copies of 585 tracts would bloat the prerendered HTML.
	import { onMount } from 'svelte';
	import { geoMercator, geoPath, scaleThreshold } from 'd3';
	import { heroMaps, newVotesTracts, newVotesMunicipalities, municipalityLines, wardLines } from './data.js';
	import { HERO_RAMPS } from './config.js';

	const W = 300;
	const NO_DATA = '#d4d4d4';

	// one colour function per map
	const maps = heroMaps.maps.map((m) => {
		const step = scaleThreshold().domain(m.breaks).range(HERO_RAMPS[m.ramp]);
		return { ...m, colour: (v) => (v == null ? NO_DATA : step(v)) };
	});

	// the candidates' scales sit over their own maps; the traits' one, shared by the other six, above those
	const CANDIDATE_SCALES = { chow: "Chow's vote share", bradford: "Bradford's vote share" };
	const candidates = maps.filter((m) => CANDIDATE_SCALES[m.key]);
	const traits = maps.filter((m) => !CANDIDATE_SCALES[m.key]); // Chow's three, then Bradford's

	let paths = $state.raw([]); // one path per tract, in the order of heroMaps.tracts
	let areas = $state.raw([]); // the six former municipalities, for the city's edge
	// the boundary lines over the tracts, each drawn once: the six former municipalities', the wards', or none
	const BOUNDARIES = [
		{ key: 'former', label: 'Former municipalities' },
		{ key: 'wards', label: 'Wards' },
		{ key: 'none', label: 'None' }
	];
	let boundaries = $state('former');
	let boundaryPaths = $state.raw({ former: '', wards: '', none: '' });
	const lines = $derived(boundaryPaths[boundaries]);
	let H = $state(156); // the shape of the city, so the cells keep their size before the maps draw

	onMount(() => {
		const fc = newVotesTracts;
		// fitted to the former municipalities, not the tracts: their outline (the city's edge) reaches a
		// little past the tracts at the lakeshore, and would be clipped at the bottom otherwise
		const frame = newVotesMunicipalities;
		const [[, y0], [, y1]] = geoPath(geoMercator().angle(-17).fitWidth(W - 4, frame)).bounds(frame);
		H = Math.ceil(y1 - y0) + 4;
		const projection = geoMercator().angle(-17).fitExtent([[2, 2], [W - 2, H - 2]], frame);
		const draw = geoPath(projection).digits(1);
		paths = fc.features.map((f) => draw(f));
		areas = newVotesMunicipalities.features.map((f) => draw(f));
		boundaryPaths = { former: draw(municipalityLines), wards: draw(wardLines), none: '' };
	});
</script>

<figure aria-label="Maps of Toronto's census tracts: Chow's and Bradford's 2026 vote share beside six neighbourhood traits">
	<!-- one small map, with its name and, for a candidate, their scale -->
	{#snippet cell(m)}
		<div class="cell">
			<p class="name">{m.label}</p>
			{#if CANDIDATE_SCALES[m.key]}
				<div class="scale cell-scale" aria-hidden="true">
					<div class="bar">
						<span>Lower</span>
						<span class="steps">{#each HERO_RAMPS[m.key] as c (c)}<span class="step" style:background={c}></span>{/each}</span>
						<span>Higher</span>
					</div>
				</div>
			{/if}
			<svg
				class="small-map"
				viewBox="0 0 {W} {H}"
				style:aspect-ratio="{W} / {H}"
				role="img"
				aria-label="{m.label}, by census tract, shaded in fourths of tracts from lower (lightest) to higher (darkest)"
			>
				<!-- the city's edge, as on the local-landslides maps: a wide outline of the former municipalities, then
					 their fill on top, hiding the lines between them and showing through the lightest tracts -->
				{#each areas as d, j (j)}<path class="city-edge" {d} />{/each}
				{#each areas as d, j (j)}<path class="city-fill" {d} />{/each}
				{#each paths as d, j (j)}<path class="tract" {d} fill={m.colour(m.values[j])} />{/each}
				<!-- the chosen boundaries (former municipalities or wards), over the tracts: a grey line on a white casing -->
				{#if lines}
					<path class="municipality-casing" d={lines} />
					<path class="municipality" d={lines} />
				{/if}
			</svg>
		</div>
	{/snippet}

	<!-- Chow's and Bradford's maps side by side, each with its own scale -->
	<div class="grid">
		{#each candidates as m (m.key)}{@render cell(m)}{/each}
	</div>

	<!-- the traits' scale, shared by the six trait maps, above them (lower to higher), and beside it the
		 choice of boundary lines for all eight maps -->
	<div class="legend">
		<div class="scale" aria-hidden="true">
			<p class="legend-title">Neighbourhood characteristics (quartiles)</p>
			<div class="bar">
				<span>Lower</span>
				<span class="steps">{#each HERO_RAMPS.traits as c (c)}<span class="step" style:background={c}></span>{/each}</span>
				<span>Higher</span>
			</div>
		</div>
		<!-- the label to the left of its buttons, on one line -->
		<div class="scale boundary-control">
			<p class="legend-title" id="boundary-toggle-title">Boundaries</p>
			<div class="toggle" role="group" aria-labelledby="boundary-toggle-title">
				{#each BOUNDARIES as b (b.key)}
					<button type="button" aria-pressed={boundaries === b.key} onclick={() => (boundaries = b.key)}>
						<span class="lbl" data-text={b.label}>{b.label}</span>
					</button>
				{/each}
			</div>
		</div>
	</div>

	<!-- the six traits, two columns of three: Chow's three under his map, Bradford's under his -->
	<div class="grid traits">
		{#each traits as m (m.key)}{@render cell(m)}{/each}
	</div>

	<figcaption class="note">
		Census tracts (2021 boundaries) are shaded in four equal groups (quartiles), from the lowest values (lightest) to the highest
		(darkest). Vote shares are shares of valid 2026 election-day votes, apportioned from polls to tracts; advance and mail-in
		votes are not included. Neighbourhood characteristics are from the 2021 Census of Population.
	</figcaption>
</figure>

<style>
	figure {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	/* the scales, small: a heading, then Lower, the four steps and Higher. The traits' one sits between the
	   candidates' maps and the six trait maps */
	/* in the maps' two columns: the traits' scale centred over the left, the boundary toggle (its middle
	   button, Wards) centred over the right */
	.legend {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		justify-items: center;
		align-items: end;
		gap: 10px 12px;
		margin: 40px 0 39px;
		color: var(--brandGray70);
	}
	.scale {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
	}
	/* the boundary toggle, as the toggle on the local-landslides poll map: white buttons with a light grey
	   border, the chosen one bold at full strength, the others faded; small, to sit with the scale */
	.toggle {
		display: inline-flex;
		gap: 6px;
	}
	.boundary-control {
		flex-direction: row;
		align-items: center;
		gap: 8px;
	}
	/* phones: no room beside the buttons, so the label goes back above them */
	@media (max-width: 520px) {
		.boundary-control {
			flex-direction: column;
			gap: 2px;
		}
	}
	.toggle button {
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.2;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		margin: 0;
		padding: 3px 7px;
		cursor: pointer;
		white-space: nowrap; /* "Former municipalities" stays on one line */
	}
	.toggle button:hover {
		border-color: #9ba1a8;
	}
	.toggle button[aria-pressed='false'] {
		opacity: 0.65;
	}
	.toggle button[aria-pressed='false']:hover {
		opacity: 0.9;
	}
	.toggle button[aria-pressed='true'] {
		opacity: 0.9;
		font-family: OpenSansBold, sans-serif;
		color: var(--brandBlack);
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
	/* a thin mid-grey outline round the steps, so the lightest one doesn't vanish into the page */
	.steps {
		display: flex;
		outline: 1px solid var(--brandGray50);
	}
	.step {
		width: 16px;
		height: 8px;
	}
	/* two columns on every screen; the trait maps fill down each column, Chow's three then Bradford's */
	.grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 18px 12px;
	}
	.grid.traits {
		grid-template-rows: repeat(3, auto);
		grid-auto-flow: column;
	}
	/* a candidate's scale, between its map's name and the map */
	.cell-scale {
		margin: 0 0 4px;
	}
	/* narrow screens: no room side by side, so the traits' scale sits over the boundary toggle, each on its own line */
	@media (max-width: 700px) {
		.legend {
			grid-template-columns: 1fr;
			gap: 14px;
			margin: 26px 0 28px;
		}
	}
	@media (max-width: 520px) {
		/* names can wrap in the narrow columns: room for two lines, so the maps in a row stay level */
		.name {
			min-height: 2.6em;
		}
	}
	.cell {
		min-width: 0;
	}
	/* the map's name, in the installed bold, bottom-aligned so one- and two-line names sit alike */
	.name {
		margin: 0 0 2px;
		display: flex;
		align-items: flex-end;
		justify-content: center;
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		line-height: 1.3;
		text-align: center;
		text-wrap: balance;
		color: var(--brandGray90);
	}
	/* as wide as the body text's paragraphs, though the maps are wider */
	.note {
		max-width: 694px;
		margin: 21px auto 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
	.small-map {
		display: block;
		width: 100%;
		height: auto;
	}
	/* the shoreline and the city's other edges, darker than the boundaries inside it */
	.city-edge {
		fill: none;
		stroke: var(--brandGray70);
		stroke-width: 2;
		stroke-linejoin: round;
	}
	/* shows where the city's boundary takes in water (the harbour, around the islands); lighter than
	   the no-data grey (#d4d4d4) so the two don't read as the same */
	.city-fill {
		fill: #e4e4e4;
		stroke: #e4e4e4;
		stroke-width: 0.5;
	}
	.tract {
		stroke: #fff;
		stroke-width: 0.25;
	}
	/* the former municipalities' boundaries: a 1px grey line over a 3px white casing, both in screen pixels
	   whatever the map's size, so they stand out from the tracts */
	.municipality-casing {
		fill: none;
		stroke: #fff;
		stroke-width: 3;
		vector-effect: non-scaling-stroke;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.municipality {
		fill: none;
		stroke: var(--brandGray60);
		stroke-width: 1;
		vector-effect: non-scaling-stroke;
		stroke-linejoin: round;
		pointer-events: none;
	}

</style>
