<script>
	// First-draft small multiple map for the "five-torontos" story.
	// Colours the 585 census tracts by Model 8F cluster, "spotlighting" one cluster at a
	// time (everything else fades to grey) — used both for the rotating "all 5 groups"
	// intro map and for each section's single-cluster map. Adapted from the projection/path
	// conventions in $lib/MapMini.svelte; swap for a full maplibre map (see $lib/Map.svelte)
	// later if the story needs zoom/pan/tooltips instead of a static small multiple.

	import { geoPath, geoMercator } from "d3";
	import Wards from "$data/wards.geo.json";

	export let tracts; // ct_clusters.geojson FeatureCollection ($data/clustering_neighbourhoods/ct_clusters.geojson)
	export let activeClusterId = null; // null = show every cluster in colour; a cluster_id = spotlight just that one
	export let label = "";

	const FADE_COLOR = "#e6e6e6";

	let divWidth = 420;
	$: innerWidth = divWidth;
	$: height = innerWidth / 1.75;

	// Same Toronto-centred projection used elsewhere on the site (MapMini.svelte) so every
	// map on the page lines up visually.
	$: projection = geoMercator()
		.center([-78.155 - 0.00239 * innerWidth + 0.000001125 * innerWidth ** 2, 43.54 + 0.00045 * innerWidth - 2.5e-7 * innerWidth ** 2])
		.scale([82000 * innerWidth / 800])
		.angle([-17]);
	$: path = geoPath(projection);

	$: features = tracts.features;
	$: fillFor = (props) =>
		activeClusterId === null || props.cluster_id === activeClusterId ? props.cluster_color : FADE_COLOR;
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={innerWidth} {height}>
		{#if label}
			<text class="label" x="12" y="22">{label}</text>
		{/if}

		{#each features as feature}
			<path class="ct" d={path(feature)} fill={fillFor(feature.properties)} />
		{/each}

		{#each Wards.features as feature}
			<path class="ward" d={path(feature)} />
		{/each}
	</svg>
</div>

<style>
	.ct {
		stroke: rgb(237, 237, 237);
		stroke-width: 1px;
		opacity: 0.9;
	}
	.ward {
		stroke: black;
		stroke-width: 1px;
		fill: none;
		opacity: 0.5;
	}
	.label {
		font-size: 13px;
		fill: rgb(56, 56, 56);
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>
