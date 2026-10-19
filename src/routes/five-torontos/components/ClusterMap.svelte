<script>
	// Small-multiple map for the "five-torontos" story: draws the five clusters (census tracts
	// dissolved by Model 8F cluster). When a cluster is active, it renders in its colour and every
	// other cluster is solid white. A control at the bottom left adds ward / provincial riding,
	// 2025 federal riding or former-municipality boundaries (with names) on top; former
	// municipalities by default. Used both for the rotating
	// "all 5 groups" intro map (activeClusterId cycles, with a "show all" toggle) and for
	// each section's single-cluster map (activeClusterId fixed, legend has just that one row).
	// Adapted from the projection/path conventions in $lib/maps/MapMini.svelte.

	import { geoPath, geoMercator } from "d3";
	import { onMount } from 'svelte';
	// boundary layers (Toronto only, digital boundary files: they extend into the lake rather than
	// following the shoreline; label_lon/label_lat is a point inside each area's land)
	import Wards from "../data/wards.geo.json";
	import Feds2025 from "../data/fed_2025.geo.json";
	import FormerMunicipalities from "../data/former_municipalities.geo.json";
	import { CLUSTER_COLORS, CLUSTER_OUTLINE_COLORS } from "./clusterColors.js"; // this page's palette, over the data file's colours

	// unique per map, for the tract layer's clip path (several maps share the page)
	const clipId = `cluster-clip-${Math.random().toString(36).slice(2, 9)}`;

	// draw the map shapes only in the browser, so they aren't prerendered into the page HTML
	let mounted = false;
	onMount(() => { mounted = true; });

	export let areas; // data/clusters_dissolved.geo.json FeatureCollection: one feature per cluster
	export let tracts; // data/ct_clusters.geo.json FeatureCollection: tract outlines, drawn underneath
	export let activeClusterId = null; // null = every cluster at full colour; a cluster_id = spotlight just that one
	export let legend = []; // [{ cluster_id, label, color, pct }] — 5 rows for the intro map, 1 for a section map
	export let label = "Map of Toronto's 585 census tracts, coloured by political cluster"; // accessible name for the map svg

	// which boundaries to draw over the clusters; each map has its own control (bottom left)
	const BOUNDARY_OPTIONS = [
		// the 25 wards are also the 2025 provincial ridings (Ontario's Toronto ridings share their boundaries)
		// labelMinWidth: the narrowest map (px) at which that layer's names don't overlap
		// (checked by laying out every label's box); narrower than that, lines only
		{ key: "former", label: "Former municipalities", layer: FormerMunicipalities, labelMinWidth: 400 },
		{ key: "wards", label: "2023 wards and 2025 provincial ridings", layer: Wards, labelMinWidth: 800 },
		{ key: "fed2025", label: "2025 federal ridings", layer: Feds2025, labelMinWidth: 820 },
	];
	// former municipalities shown by default; clicking the chosen option again turns boundaries off
	let boundaryKey = "former";
	$: boundaryOption = BOUNDARY_OPTIONS.find((o) => o.key === boundaryKey) ?? null;
	$: boundaries = boundaryOption?.layer ?? null;

	// a boundary name split into lines: after each hyphen or dash (kept at the end of its line),
	// e.g. "Taiaiako'n–Parkdale–High Park" on three lines (both layers' names use en dashes); otherwise at its last space if it's
	// longer than 13 characters (e.g. "Toronto Centre"); short names stay on one line
	function labelLines(name) {
		const parts = name.split(/(?<=[-–—])/);
		if (parts.length > 1) return parts;
		const sp = name.lastIndexOf(" ");
		if (name.length > 13 && sp !== -1) return [name.slice(0, sp), name.slice(sp + 1)];
		return [name];
	}

	const FULL_OPACITY = 1;
	const FADE_OPACITY = 0.1; // inactive legend swatches
	const LEGEND_TEXT_FADE_OPACITY = 0.45; // legend *text* needs to stay readable, so it fades less than the map fill
	const MAP_ANGLE = -17; // same tilt used elsewhere on the site so Toronto reads as level
	const PAD = 10;
	const PAD_BOTTOM = 20; // extra room so the legend doesn't sit flush on Toronto's edge

	// "Show all" only makes sense where the legend has more than one row (the rotating intro
	// map) — a section map's legend is always just its own single, already-active cluster.
	$: multiRow = legend.length > 1;
	let showAll = false;
	$: effectiveActiveId = showAll ? null : activeClusterId;

	// Legend grid rows are numbered explicitly rather than left to CSS grid auto-flow: row 1
	// holds the "% of population" header and (when present) the "show all" button; data rows follow.
	const firstDataRow = 2;

	let divWidth = 420;
	$: innerWidth = divWidth;
	$: height = innerWidth / 1.6;

	// Fit the projection to the clusters' actual bounds on every resize, rather than hand-tuned
	// center/scale constants, so Toronto stays centred with even margins at any width. The
	// angle is set before fitting so the fit accounts for the rotated bounding box.
	$: projection = geoMercator()
		.angle(MAP_ANGLE)
		.fitExtent(
			[
				[PAD, PAD],
				[innerWidth - PAD, height - PAD_BOTTOM],
			],
			areas
		);
	$: path = geoPath(projection);

	$: features = areas.features;
	// the active cluster (or every cluster, when none is active) in its colour; the rest white
	$: fillFor = (props) =>
		effectiveActiveId === null || props.cluster_id === effectiveActiveId
			? (CLUSTER_COLORS[props.cluster_slug] ?? props.cluster_color)
			: "white";
	// a single highlighted cluster (not "all at once") gets a darker outline in its own hue, so
	// its edge has enough contrast against the white around it (see ./clusterColors.js)
	$: outlineFor = (props) =>
		effectiveActiveId !== null && props.cluster_id === effectiveActiveId
			? CLUSTER_OUTLINE_COLORS[props.cluster_slug]
			: null;
</script>

<div class="map-wrap" bind:offsetWidth={divWidth}>
	<svg width={innerWidth} {height} role="img" aria-label={label}>
		{#if mounted}
			<!-- background, behind everything, in two layers of the former municipalities (which
				 extend into the lake): first a 6px 20% grey outline, then on top the light grey fill
				 with a 1px outline of the same grey. The fill hides the grey lines between the
				 municipalities, leaving just a grey edge around the outside of the city. -->
			{#each FormerMunicipalities.features as feature}
				<path class="background-edge" d={path(feature)} />
			{/each}
			{#each FormerMunicipalities.features as feature}
				<path class="background" d={path(feature)} />
			{/each}

			<!-- census tract outlines underneath; they show faintly through the cluster layer above.
				 Clipped to the clusters' shapes, so the outer half of the tracts' edge line (which
				 the cluster fill never covers) doesn't show as a dark line along the shoreline. -->
			<defs>
				<clipPath id={clipId}>
					{#each features as feature}
						<path d={path(feature)} />
					{/each}
				</clipPath>
			</defs>
			<g clip-path={`url(#${clipId})`}>
				{#each tracts.features as feature}
					<path class="tract" d={path(feature)} />
				{/each}
			</g>

			<g class="areas">
				{#each features as feature}
					<path
						class="area"
						class:inactive={effectiveActiveId !== null && feature.properties.cluster_id !== effectiveActiveId}
						d={path(feature)}
						fill={fillFor(feature.properties)}
						style:stroke={outlineFor(feature.properties)}
					/>
				{/each}
			</g>

			{#if boundaries}
				<!-- white casing drawn first, under the black boundary line, so the boundaries
					 stand out against the cluster colours -->
				{#each boundaries.features as feature}
					<path class="ward-casing" d={path(feature)} />
				{/each}
				{#each boundaries.features as feature}
					<path class="ward" d={path(feature)} />
				{/each}

				<!-- names at the centre of each area's land (nudged apart where two would overlap),
					 with a white halo so they read over colours and lines -->
				{#if innerWidth >= boundaryOption.labelMinWidth}
					{#each boundaries.features as feature}
						{@const [cx, cy] = projection([feature.properties.label_lon, feature.properties.label_lat])}
						{@const lines = labelLines(feature.properties.name)}
						<text class="ward-label" x={cx} y={cy - ((lines.length - 1) * 11) / 2}>
							{#each lines as line, j}
								<tspan x={cx} dy={j === 0 ? "0.35em" : 11}>{line}</tspan>
							{/each}
						</text>
					{/each}
				{/if}
			{/if}
		{/if}
	</svg>

	<!-- boundary control, in the empty corner below the Etobicoke shoreline (below the map on
		 narrow screens) -->
	{#if mounted}
		<div class="boundary-control" role="group" aria-labelledby={`${clipId}-layers`}>
			<p class="boundary-title" id={`${clipId}-layers`}>Reference layers</p>
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

	{#if legend.length}
		<div class="legend-box">
			<div class="legend-spacer" style:grid-row="1" style:grid-column="1"></div>

			{#if multiRow}
				<!-- Sits above the group labels, sharing row 1 with the "% of population" header. -->
				<button
					type="button"
					class="show-all-btn"
					class:on={showAll}
					style:grid-row="1"
					style:grid-column="2"
					aria-pressed={showAll}
					on:click={() => (showAll = !showAll)}
				>
					Show all
				</button>
			{:else}
				<div class="legend-spacer" style:grid-row="1" style:grid-column="2"></div>
			{/if}

			<div class="legend-header" style:grid-row="1" style:grid-column="3">% of<br />population</div>

			{#each legend as row, i (row.cluster_id)}
				{@const active = !multiRow || effectiveActiveId === null || row.cluster_id === effectiveActiveId}
				{@const r = firstDataRow + i}
				{@const textOpacity = active ? 1 : LEGEND_TEXT_FADE_OPACITY}
				<span
					class="legend-swatch"
					style:grid-row={r}
					style:grid-column="1"
					style:background={row.color}
					style:opacity={active ? FULL_OPACITY : FADE_OPACITY}
				></span>
				<span class="legend-rect" style:grid-row={r} style:grid-column="2" style:opacity={textOpacity}>
					{row.label}
				</span>
				<span class="legend-pop" style:grid-row={r} style:grid-column="3" style:opacity={textOpacity}>
					{row.pct.toFixed(1)}%
				</span>
			{/each}
		</div>
	{/if}
</div>

<style>
	.map-wrap {
		position: relative;
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
		fill: none;
		stroke: black;
		stroke-width: 1px;
	}
	/* 94% opaque, so the tract outlines underneath show through faintly */
	.areas {
		opacity: 0.94;
	}
	.area {
		stroke: rgb(237, 237, 237);
		stroke-width: 1px;
	}
	/* clusters that aren't highlighted: plain white, with a white outline */
	.area.inactive {
		stroke: white;
		stroke-width: 1px;
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
	.ward-casing {
		stroke: white;
		stroke-width: 3px;
		fill: none;
	}
	.ward {
		stroke: black;
		stroke-width: 1px;
		fill: none;
	}

	/* Legend styled after the social-geography page's map controls and legends: Open Sans,
	   near-black ink with grey secondary text, small swatches with a faint outline, and no
	   boxed cells. A light backing keeps it readable where it overlaps tracts. */
	.legend-box {
		position: absolute;
		right: 10px;
		bottom: 8px;
		display: grid;
		grid-template-columns: auto auto auto;
		gap: 4px 8px;
		align-items: center;
		padding: 8px 10px;
		background: rgba(255, 255, 255, 0.85);
		font-family: OpenSans, sans-serif;
		color: var(--brandBlack);
	}
	.legend-header {
		font-size: 11px;
		line-height: 1.2;
		text-align: right;
		color: var(--brandGray70);
		/* Row 1 can be taller than this header's own text when it also holds the "show all"
		   button (the rotating intro map's multi-row legend) — align to the row's bottom edge
		   so the header sits the same distance from the data row below it either way, rather
		   than floating higher whenever row 1 grows past the text's natural height. */
		align-self: end;
	}
	/* dark grey outline with a white ring inside it, like the ward lines' white casing */
	.legend-swatch {
		width: 20px;
		height: 20px;
		border: 1px solid var(--brandGray70);
		box-shadow: inset 0 0 0 1px white;
		box-sizing: border-box;
	}
	/* each label and value sits in its own light box */
	.legend-rect,
	.legend-pop {
		display: flex;
		align-items: center;
		height: 20px;
		box-sizing: border-box;
		border: 1px solid var(--brandGray);
		background: white;
		font-size: 12px;
		white-space: nowrap;
		margin: 0;
	}
	.legend-rect {
		padding: 0 8px;
		justify-content: flex-start;
	}
	.legend-pop {
		padding: 0 6px;
		justify-content: flex-end;
		font-variant-numeric: tabular-nums;
	}
	/* same as the social-geography page's two-button toggle */
	.show-all-btn {
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		padding: 3px 8px;
		cursor: pointer;
		justify-self: start;
		/* bottom of row 1, level with the two-line "% of population" header beside it */
		align-self: end;
		opacity: 1; /* always fully visible, unlike the fading map/legend rows */
	}
	.show-all-btn:hover {
		border-color: #9ba1a8;
	}
	.show-all-btn.on {
		background: var(--brandGray80);
		border-color: var(--brandGray80);
		color: white;
	}

	/* boundary control: three white buttons stacked vertically, 2px apart (the chosen one at full
	   strength, the others faded) */
	/* Left edge lined up with the body text's: the global `.text` column (content up to 694px,
	   25px side padding) is centred in the same section the map fills, so its content starts
	   half the leftover width in from the map's edge. */
	.boundary-control {
		position: absolute;
		left: calc((100% - min(694px, 100% - 50px)) / 2);
		bottom: -14px; /* reaches 14px below the map's box */
		/* stacked: one button per row, all the width of the widest */
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
		cursor: pointer;
	}
	.boundary-control button {
		text-align: left;
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
	/* the chosen option at full strength, the others faded (no dark fill) */
	.boundary-control button:not(.on) {
		opacity: 0.5;
	}
	.boundary-control button.on {
		color: var(--brandBlack);
	}

	@media (max-width: 600px) {
		.boundary-control {
			position: static;
			width: max-content;
			margin: 8px auto 0;
		}
		.legend-box {
			position: static;
			margin: 8px auto 0;
			width: max-content;
		}
	}
</style>
