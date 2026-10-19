<script>
	// Static choropleth of Toronto's 585 census tracts (SVG, rotated like the site's other maps),
	// in the style of the five-torontos maps: a two-layer grey background of the former
	// municipalities, white tract outlines, and a "Reference layers" control that adds former
	// municipality, ward / provincial riding or 2025 federal riding boundaries (with names).
	//
	// Generic: the parent says which tract property to colour (`valueKey`) and with which classes.
	// Tracts with no value get a diagonal hatch. Hover (or tap) a tract to open the readout, whose
	// contents the parent supplies through the default slot:
	//
	//   <TractMap ... let:props> ...markup for one tract's properties... </TractMap>
	//
	// `activeId` lets a sibling chart highlight a tract here, and a `hover` event reports the
	// tract under the pointer back.

	import { geoPath, geoMercator } from 'd3';
	import { onMount, createEventDispatcher } from 'svelte';
	// Reference layers are shared with the five-torontos story (Toronto only, digital boundary
	// files that extend into the lake; label_lon/label_lat is a point inside each area's land).
	import Wards from '../../five-torontos/data/wards.geo.json';
	import Feds2025 from '../../five-torontos/data/fed_2025.geo.json';
	import FormerMunicipalities from '../../five-torontos/data/former_municipalities.geo.json';
	import { NA_COLOUR, HATCH_COLOUR, HOVER_COLOUR } from '../config.js';

	export let tracts; // FeatureCollection, features carry a `ct` property
	export let valueKey; // tract property that decides the fill
	export let breaks = []; // class boundaries, ascending
	export let colors = []; // breaks.length + 1 colours
	export let activeId = null; // tract highlighted from outside (e.g. a hovered scatter dot)
	export let label = 'Map of Toronto census tracts';

	const dispatch = createEventDispatcher();
	// unique per map (several maps share the page): the hatch pattern's id and the control's label id
	const uid = `tract-map-${Math.random().toString(36).slice(2, 9)}`;

	// draw the map shapes only in the browser, so they aren't prerendered into the page HTML
	let mounted = false;
	let touchOnly = false;
	onMount(() => {
		mounted = true;
		touchOnly = window.matchMedia('(hover: none)').matches;
	});

	// which boundaries to draw over the tracts; each map has its own control (bottom left)
	const BOUNDARY_OPTIONS = [
		// the 25 wards are also the 2025 provincial ridings (Ontario's Toronto ridings share their boundaries)
		// labelMinWidth: the narrowest map (px) at which that layer's names don't overlap; narrower, lines only
		{ key: 'former', label: 'Former municipalities', layer: FormerMunicipalities, labelMinWidth: 400 },
		{ key: 'wards', label: '2023 wards and 2025 provincial ridings', layer: Wards, labelMinWidth: 800 },
		{ key: 'fed2025', label: '2025 federal ridings', layer: Feds2025, labelMinWidth: 820 }
	];
	// former municipalities shown by default; clicking the chosen option again turns boundaries off
	let boundaryKey = 'former';
	$: boundaryOption = BOUNDARY_OPTIONS.find((o) => o.key === boundaryKey) ?? null;
	$: boundaries = boundaryOption?.layer ?? null;

	// a boundary name split into lines: after each hyphen or dash (kept at the end of its line),
	// otherwise at its last space if longer than 13 characters; short names stay on one line
	function labelLines(name) {
		const parts = name.split(/(?<=[-–—])/);
		if (parts.length > 1) return parts;
		const sp = name.lastIndexOf(' ');
		if (name.length > 13 && sp !== -1) return [name.slice(0, sp), name.slice(sp + 1)];
		return [name];
	}

	const MAP_ANGLE = -17; // same tilt used elsewhere on the site so Toronto reads as level
	const PAD = 10;
	const PAD_BOTTOM = 20;

	let divWidth = 420;
	$: width = divWidth;
	$: height = width / (width < 600 ? 1.3 : 1.6); // a taller map on phones, where tracts are tapped

	// Fit the projection to the tracts on every resize so Toronto stays centred with even margins.
	$: projection = geoMercator()
		.angle(MAP_ANGLE)
		.fitExtent(
			[
				[PAD, PAD],
				[width - PAD, height - PAD_BOTTOM]
			],
			tracts
		);
	$: path = geoPath(projection);
	$: shapes = tracts.features.map((f) => ({ ct: f.properties.ct, props: f.properties, d: path(f) }));
	$: pathById = new Map(shapes.map((s) => [s.ct, s.d]));

	// step(value) -> class colour (a value on a break goes up a class); null when there is no number
	$: colorOf = (v) => {
		if (typeof v !== 'number') return null;
		let i = 0;
		while (i < breaks.length && v >= breaks[i]) i++;
		return colors[i];
	};

	let hovered = null; // ct id under the pointer
	let hoveredProps = null;
	function setHovered(props) {
		const ct = props?.ct ?? null;
		if (ct === hovered) return;
		hovered = ct;
		hoveredProps = props ?? null;
		dispatch('hover', ct);
	}
	$: highlightD = pathById.get(hovered ?? activeId) ?? null;

	// a tap anywhere that isn't a tract closes the readout
	function onSvgClick(event) {
		if (!event.target.classList?.contains('tract')) setHovered(null);
	}
</script>

<div class="map-wrap" bind:offsetWidth={divWidth}>
	<!-- the map is a pointer-hover/tap explorer; its tracts are not individually focusable (the values
		 are also reachable through the linked chart on the explorer, and the colour classes are in the legend) -->
	<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
	<svg {width} {height} role="group" aria-label={label} on:click={onSvgClick} on:keydown={() => {}}>
		{#if mounted}
			<defs>
				<!-- diagonal hatching for tracts with no data: unmistakable next to any palette colour -->
				<pattern id="{uid}-hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
					<rect width="5" height="5" fill={NA_COLOUR} />
					<line x1="0" y1="0" x2="0" y2="5" stroke={HATCH_COLOUR} stroke-width="2" />
				</pattern>
			</defs>

			<!-- background, behind everything, in two layers of the former municipalities (which
				 extend into the lake): first a 6px 20% grey outline, then on top the light grey fill
				 with a 1px outline of the same grey, leaving just a grey edge around the city -->
			{#each FormerMunicipalities.features as feature}
				<path class="background-edge" d={path(feature)} />
			{/each}
			{#each FormerMunicipalities.features as feature}
				<path class="background" d={path(feature)} />
			{/each}

			<!-- the tracts -->
			<g role="presentation" on:mouseleave={() => setHovered(null)}>
				{#each shapes as s (s.ct)}
					<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
					<path
						class="tract"
						d={s.d}
						fill={colorOf(s.props[valueKey]) ?? `url(#${uid}-hatch)`}
						on:mouseenter={() => setHovered(s.props)}
						on:click={() => setHovered(s.props)}
					/>
				{/each}
			</g>

			{#if boundaries}
				<!-- white casing drawn first, under the black boundary line, so the boundaries
					 stand out against the tract colours -->
				{#each boundaries.features as feature}
					<path class="ward-casing" d={path(feature)} />
				{/each}
				{#each boundaries.features as feature}
					<path class="ward" d={path(feature)} />
				{/each}
			{/if}

			<!-- the highlighted tract (hovered here, or hovered in a linked chart) -->
			{#if highlightD}
				<path class="highlight-casing" d={highlightD} />
				<path class="highlight" d={highlightD} stroke={HOVER_COLOUR} />
			{/if}

			{#if boundaries && width >= boundaryOption.labelMinWidth}
				<!-- names at the centre of each area's land, with a white halo so they read over colours and lines -->
				{#each boundaries.features as feature}
					{@const [cx, cy] = projection([feature.properties.label_lon, feature.properties.label_lat])}
					{@const lines = labelLines(feature.properties.name)}
					<text class="ward-label" x={cx} y={cy - ((lines.length - 1) * 11) / 2}>
						{#each lines as line, j}
							<tspan x={cx} dy={j === 0 ? '0.35em' : 11}>{line}</tspan>
						{/each}
					</text>
				{/each}
			{/if}
		{/if}
	</svg>

	<!-- reference-layer control, in the empty corner below the Etobicoke shoreline (below the map on narrow screens) -->
	{#if mounted}
		<div class="boundary-control" role="group" aria-labelledby="{uid}-layers">
			<p class="boundary-title" id="{uid}-layers">Reference layers</p>
			{#each BOUNDARY_OPTIONS as option (option.key)}
				<button
					type="button"
					class:on={boundaryKey === option.key}
					aria-pressed={boundaryKey === option.key}
					on:click={() => (boundaryKey = boundaryKey === option.key ? null : option.key)}
				>
					{option.label}
				</button>
			{/each}
		</div>
	{/if}

	{#if hoveredProps}
		<div class="readout" aria-live="polite"><slot props={hoveredProps} /></div>
	{:else if mounted}
		<div class="hint" aria-hidden="true">{touchOnly ? 'Tap' : 'Hover over'} a tract for values</div>
	{/if}
</div>

<style>
	.map-wrap {
		position: relative;
	}
	svg {
		display: block;
	}
	.background-edge {
		fill: none;
		stroke: #cccccc; /* 20% grey */
		stroke-width: 6px;
		stroke-linejoin: round;
	}
	.background {
		fill: #eeeeee;
		stroke: #eeeeee;
		stroke-width: 1px;
	}
	.tract {
		stroke: white;
		stroke-width: 0.6px;
		cursor: crosshair; /* the target pointer used on the site's other maps */
	}
	.ward-casing {
		stroke: white;
		stroke-width: 3px;
		fill: none;
		pointer-events: none;
	}
	.ward {
		stroke: black;
		stroke-width: 1px;
		fill: none;
		pointer-events: none;
	}
	.highlight-casing,
	.highlight {
		fill: none;
		pointer-events: none;
		stroke-linejoin: round;
	}
	.highlight-casing {
		stroke: black;
		stroke-width: 5px;
	}
	.highlight {
		stroke-width: 3px;
	}
	.ward-label {
		font-family: OpenSans, sans-serif;
		font-size: 10px;
		fill: var(--brandGray90);
		text-anchor: middle;
		paint-order: stroke;
		stroke: white;
		stroke-opacity: 0.84; /* the white halo only; the text stays solid */
		stroke-width: 3px;
		stroke-linejoin: round;
		pointer-events: none;
	}

	.readout,
	.hint {
		position: absolute;
		z-index: 2;
		font-family: OpenSans, sans-serif;
		pointer-events: none;
	}
	.readout {
		right: 10px;
		bottom: 10px;
		min-width: 160px;
		max-width: min(250px, calc(100% - 20px));
		background: rgba(255, 255, 255, 0.94);
		border: 1px solid var(--brandGray);
		padding: 8px 10px;
		font-size: 12px;
		color: var(--brandGray90);
	}
	.hint {
		left: 10px;
		top: 6px;
		font-size: 11px;
		color: var(--brandGray60);
		text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 3px #fff;
	}

	/* readout contents, shared by every map that uses this component */
	.readout :global(.ct) {
		color: var(--brandGray60);
		font-size: 11px;
	}
	.readout :global(.row) {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 10px;
		font-variant-numeric: tabular-nums;
	}
	.readout :global(.row .k) {
		color: var(--brandGray70);
	}
	.readout :global(.row .v) {
		font-family: OpenSansBold, sans-serif;
	}
	.readout :global(.row.big) {
		margin-top: 2px;
	}
	.readout :global(.row.big .v) {
		font-size: 17px;
	}
	.readout :global(.row.dim .k),
	.readout :global(.row.dim .v) {
		color: var(--brandGray60);
		font-family: OpenSans, sans-serif;
		font-size: 11px;
	}

	/* reference-layer control: white buttons stacked vertically, 2px apart (the chosen one at full
	   strength, the others faded), as on the five-torontos maps */
	.boundary-control {
		position: absolute;
		left: 10px;
		bottom: 4px;
		display: flex;
		flex-direction: column;
		align-items: stretch;
		gap: 2px;
	}
	/* 20px tall: 14px line + 2px padding top and bottom + 1px border top and bottom */
	.boundary-control button {
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 14px;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		padding: 2px 7px;
		text-align: left;
		cursor: pointer;
	}
	.boundary-title {
		margin: 0 0 1px;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 14px;
		color: var(--brandGray70);
	}
	.boundary-control button:hover {
		border-color: #9ba1a8;
	}
	.boundary-control button:not(.on) {
		opacity: 0.5;
	}
	.boundary-control button.on {
		color: var(--brandBlack);
	}
	.boundary-control button:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: 1px;
	}

	@media (max-width: 600px) {
		.boundary-control {
			position: static;
			width: max-content;
			margin: 8px auto 0;
		}
	}
</style>
