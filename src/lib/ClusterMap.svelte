<script>
	// First-draft small multiple map for the "five-torontos" story.
	// Colours the 585 census tracts by Model 8F cluster; when active, that cluster's tracts
	// render at full colour and every other cluster fades — in its own colour, not grey, so
	// the rest of the city stays legibly "in the background" rather than disappearing. Used
	// both for the rotating "all 5 groups" intro map (activeClusterId cycles, and a "show
	// all" toggle overrides it) and for each section's single-cluster map (activeClusterId
	// fixed, legend has just the one row, always shown plain/full). Adapted from the
	// projection/path conventions in $lib/MapMini.svelte; swap for a full maplibre map
	// (see $lib/Map.svelte) later if the story needs zoom/pan/tooltips instead of a static
	// small multiple.

	import { geoPath, geoMercator } from "d3";
	import Wards from "$data/wards.geo.json";

	export let tracts; // ct_clusters.geo.json FeatureCollection ($data/clustering_neighbourhoods/ct_clusters.geo.json)
	export let activeClusterId = null; // null = every cluster at full colour; a cluster_id = spotlight just that one
	export let legend = []; // [{ cluster_id, label, color, pct }] — 5 rows for the intro map, 1 for a section map

	const FULL_OPACITY = 1;
	const FADE_OPACITY = 0.1; // faint, but still visible so the rest of the city stays legible
	const LEGEND_TEXT_FADE_OPACITY = 0.45; // lighter fade for legend *text* (needs to stay readable, unlike the map fill)
	const MAP_ANGLE = -17; // same tilt used elsewhere on the site (see $lib/MapMini.svelte) so Toronto reads as level
	const PAD = 10;
	const PAD_BOTTOM = 20; // a little extra room at the bottom so the legend doesn't sit flush on Toronto's edge

	// "Show all" only makes sense where the legend has more than one row (the rotating intro
	// map) — a section map's legend is always just its own single, already-active cluster.
	$: multiRow = legend.length > 1;
	let showAll = false;
	$: effectiveActiveId = showAll ? null : activeClusterId;

	// Explicit row numbers for the legend grid: row 1 is the "% Pop." header, sharing that row
	// with the "show all" button (when there is one); data rows start right after. Assigned
	// explicitly rather than left to grid auto-flow, since mixing auto-placed and
	// explicitly-columned items in the same grid is easy to get wrong across rows.
	const firstDataRow = 2;

	let divWidth = 420;
	$: innerWidth = divWidth;
	$: height = innerWidth / 1.6;

	// Fit the projection to the tracts' actual bounds each time the box size changes, rather
	// than hand-tuned center/scale constants — this keeps Toronto centred with even margins
	// instead of clipping the south/east edges at some widths. The angle is set before fitting
	// so the fit accounts for the rotated bounding box.
	$: projection = geoMercator()
		.angle(MAP_ANGLE)
		.fitExtent(
			[
				[PAD, PAD],
				[innerWidth - PAD, height - PAD_BOTTOM],
			],
			tracts
		);
	$: path = geoPath(projection);

	$: features = tracts.features;
	$: opacityFor = (props) =>
		effectiveActiveId === null || props.cluster_id === effectiveActiveId ? FULL_OPACITY : FADE_OPACITY;
</script>

<div class="map-wrap" bind:offsetWidth={divWidth}>
	<svg width={innerWidth} {height}>
		{#each features as feature}
			<path class="ct" d={path(feature)} fill={feature.properties.cluster_color} fill-opacity={opacityFor(feature.properties)} />
		{/each}

		{#each Wards.features as feature}
			<path class="ward" d={path(feature)} />
		{/each}
	</svg>

	{#if legend.length}
		<div class="legend-box">
			<div class="legend-spacer" style="grid-row:1; grid-column:1;"></div>

			{#if multiRow}
				<!-- Same size/position as a data row's label rectangle below — just stacked above them,
					at the same width and with the same grid gap between it and "Progressive Core" — and
					sharing its row with the "% Pop." header. -->
				<button
					type="button"
					class="legend-rect show-all-btn"
					class:on={showAll}
					style="grid-row:1; grid-column:2;"
					on:click={() => (showAll = !showAll)}
				>
					Show all
				</button>
			{:else}
				<div class="legend-spacer" style="grid-row:1; grid-column:2;"></div>
			{/if}

			<div class="legend-header" style="grid-row:1; grid-column:3;">% Pop.</div>

			{#each legend as row, i (row.cluster_id)}
				{@const active = !multiRow || effectiveActiveId === null || row.cluster_id === effectiveActiveId}
				{@const r = firstDataRow + i}
				<span
					class="legend-swatch"
					style="grid-row:{r}; grid-column:1; background: {row.color}; opacity: {active ? FULL_OPACITY : FADE_OPACITY};"
				></span>
				<span class="legend-rect" style="grid-row:{r}; grid-column:2; opacity: {active ? 1 : LEGEND_TEXT_FADE_OPACITY};">
					{row.label}
				</span>
				<span class="legend-pop" style="grid-row:{r}; grid-column:3; opacity: {active ? 1 : LEGEND_TEXT_FADE_OPACITY};">
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
	.ct {
		stroke: rgb(237, 237, 237);
		stroke-width: 1px;
	}
	.ward {
		stroke: black;
		stroke-width: 1px;
		fill: none;
		opacity: 0.5;
	}

	.legend-box {
		position: absolute;
		right: 10px;
		bottom: 8px;
		display: grid;
		grid-template-columns: auto auto auto;
		gap: 4px 5px;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	.legend-header {
		font-size: 10px;
		text-align: center;
		color: #333;
	}
	.legend-swatch {
		width: 20px;
		height: 20px;
		border: 1px solid black;
		box-sizing: border-box;
	}
	.legend-rect,
	.legend-pop {
		display: flex;
		align-items: center;
		height: 20px;
		box-sizing: border-box;
		border: 1px solid black;
		background: #faf8f2;
		color: black;
		font-size: 13px;
		font-weight: 400;
		white-space: nowrap;
		margin: 0;
	}
	.legend-rect {
		padding: 0 10px;
		justify-content: flex-start;
		text-align: left;
	}
	.legend-pop {
		padding: 0 8px;
		justify-content: center;
		text-align: center;
	}
	.show-all-btn {
		font-family: inherit;
		cursor: pointer;
		justify-content: center;
		letter-spacing: 0.03em;
		opacity: 1; /* always fully visible, unlike the fading map/legend rows */
	}
	.show-all-btn.on {
		background: black;
		color: white;
	}

	@media (max-width: 600px) {
		.legend-box {
			position: static;
			margin: 8px auto 0;
			width: max-content;
		}
		.legend-rect,
		.legend-pop {
			font-size: 12px;
		}
	}
</style>
