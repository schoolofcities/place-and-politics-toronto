<script>
	// Choropleth of Toronto's 585 census tracts on the site's MapLibre basemap, rotated like
	// the other maps. Generic: the parent says which tract property to colour (`valueKey`)
	// and with which classes; this component owns the camera, hover/tap behaviour and the
	// readout box, whose contents the parent supplies through the default slot:
	//
	//   <TractMap ... let:props> ...markup for one tract's properties... </TractMap>
	//
	// Hover (or tap) a tract to open the readout; `activeId` lets a sibling chart highlight
	// a tract on the map, and a `hover` event reports the tract under the pointer back.

	import { onMount, createEventDispatcher } from 'svelte';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import maplibregl, { createBaseMapStyle } from '$lib/maps/maplibre.js';
	import { BEARING, MAX_BOUNDS, outlinePoints, rotatedFit } from '$lib/maps/tractCamera.js';
	import { NA_COLOUR, HATCH_COLOUR, HOVER_COLOUR } from '../config.js';

	export let tracts; // FeatureCollection, features carry a `ct` property
	export let city; // FeatureCollection: the city outline
	export let valueKey; // tract property that decides the fill
	export let breaks = []; // class boundaries, ascending
	export let colors = []; // breaks.length + 1 colours
	export let boundaries = null; // FeatureCollection of ward / riding lines drawn over the tracts
	export let fillOpacity = 0.92; // high enough that neighbouring classes stay distinct
	export let activeId = null; // tract highlighted from outside (e.g. a hovered scatter dot)
	export let label = 'Map of Toronto census tracts';

	const dispatch = createEventDispatcher();

	const FIT_PADDING = 12;
	const EMPTY = { type: 'FeatureCollection', features: [] };
	const OUTSIDE_FADE = 0.8; // white veil over everything outside the city
	const WATER_COLOUR = '#d6d5d1'; // a little darker than the site basemap's, as on the mapper
	// Street kinds drawn faintly under the tract colours (Shortbread `streets` layer)
	const STREET_KINDS = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'living_street'];

	let container;
	let map;
	let ready = false;
	let hovered = null; // ct id under the pointer
	let hoveredProps = null;
	let touchOnly = false;

	// step(value) -> class colour; tracts without a number get the "no data" colour
	function fillExpression(key, stops, palette) {
		const value = ['get', key];
		const step = ['step', value, palette[0]];
		stops.forEach((b, i) => step.push(b, palette[i + 1]));
		return ['case', ['==', ['typeof', value], 'number'], step, NA_COLOUR];
	}

	// The site's blue-on-white basemap, with a slightly darker water colour
	function baseStyle() {
		const style = createBaseMapStyle();
		for (const layer of style.layers) {
			if (layer.id === 'water' || layer.id === 'ocean') layer.paint['fill-color'] = WATER_COLOUR;
		}
		return style;
	}

	// A big box with the city cut out of it: filled white, it fades the world outside Toronto
	function outsideMask(outline) {
		const box = [[-81, 42.5], [-77.5, 42.5], [-77.5, 45], [-81, 45], [-81, 42.5]];
		const holes = outline.features.flatMap((f) =>
			f.geometry.type === 'Polygon' ? [f.geometry.coordinates[0]] : f.geometry.coordinates.map((poly) => poly[0])
		);
		return { type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [box, ...holes] } };
	}

	// Diagonal hatching for tracts with no data: unmistakable next to any palette colour, and the
	// same look as the legend's "no data" swatch. Drawn as a small RGBA tile (2x pixel ratio).
	function hatchImage() {
		const size = 10;
		const [bg, stripe] = [NA_COLOUR, HATCH_COLOUR].map((c) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16)));
		const data = new Uint8Array(size * size * 4);
		for (let y = 0; y < size; y++) {
			for (let x = 0; x < size; x++) {
				const [r, g, b] = (x - y + size) % size < 4 ? stripe : bg;
				data.set([r, g, b, 255], (y * size + x) * 4);
			}
		}
		return { width: size, height: size, data };
	}

	let shown = null; // tract currently outlined
	function outline(id) {
		if (shown !== null) map.setFeatureState({ source: 'tracts', id: shown }, { hover: false });
		if (id != null) map.setFeatureState({ source: 'tracts', id }, { hover: true });
		shown = id;
	}

	function setHovered(props) {
		const ct = props?.ct ?? null;
		if (ct === hovered) return;
		hovered = ct;
		hoveredProps = props ?? null;
		dispatch('hover', ct);
	}

	$: if (ready) {
		map.setPaintProperty('fill', 'fill-color', fillExpression(valueKey, breaks, colors));
		map.setFilter('nodata', ['!=', ['typeof', ['get', valueKey]], 'number']);
	}
	$: if (ready) map.getSource('boundaries').setData(boundaries ?? EMPTY);
	$: if (ready) map.setPaintProperty('fill', 'fill-opacity', fillOpacity);
	$: if (ready) outline(hovered ?? activeId);

	onMount(() => {
		touchOnly = window.matchMedia('(hover: none)').matches;

		const points = outlinePoints(tracts);
		map = new maplibregl.Map({
			container,
			style: baseStyle(),
			bounds: [[-79.64, 43.58], [-79.11, 43.86]],
			fitBoundsOptions: { padding: FIT_PADDING, bearing: BEARING },
			bearing: BEARING,
			maxBounds: MAX_BOUNDS,
			dragRotate: false,
			pitchWithRotate: false,
			touchPitch: false,
			attributionControl: false // credited in the note under the map instead
		});
		// A fixed view of the whole city: no zooming or panning, so the map never captures the
		// page's scroll gestures. Hover and tap still work.
		map.scrollZoom.disable();
		map.boxZoom.disable();
		map.doubleClickZoom.disable();
		map.touchZoomRotate.disable();
		map.dragPan.disable();
		map.keyboard.disable();

		// The whole city, fitted once rotated, refitted on resize.
		const cityCamera = () => {
			const el = map.getContainer();
			return el.clientWidth && el.clientHeight ? rotatedFit(points, el.clientWidth, el.clientHeight, FIT_PADDING) : null;
		};
		const fit = () => {
			const cam = cityCamera();
			if (cam) map.jumpTo({ center: cam.center, zoom: cam.zoom, bearing: BEARING });
		};
		let queued = false;
		map.on('resize', () => {
			if (queued) return;
			queued = true;
			requestAnimationFrame(() => {
				queued = false;
				fit();
			});
		});

		map.on('load', () => {
			fit();
			map.addSource('tracts', { type: 'geojson', data: tracts, promoteId: 'ct' });
			map.addSource('city', { type: 'geojson', data: city });
			map.addSource('outside', { type: 'geojson', data: outsideMask(city) });
			map.addSource('boundaries', { type: 'geojson', data: boundaries ?? EMPTY });
			map.addImage('nodata-hatch', hatchImage(), { pixelRatio: 2 });

			map.addLayer({
				id: 'fill',
				type: 'fill',
				source: 'tracts',
				paint: { 'fill-color': fillExpression(valueKey, breaks, colors), 'fill-opacity': fillOpacity }
			});
			map.addLayer({
				id: 'nodata',
				type: 'fill',
				source: 'tracts',
				filter: ['!=', ['typeof', ['get', valueKey]], 'number'],
				paint: { 'fill-pattern': 'nodata-hatch' }
			});
			// thin mid-grey streets from the basemap tiles, under the tract colours
			map.addLayer(
				{
					id: 'streets',
					type: 'line',
					source: 'osm',
					'source-layer': 'streets',
					filter: ['in', ['get', 'kind'], ['literal', STREET_KINDS]],
					layout: { 'line-cap': 'round', 'line-join': 'round' },
					paint: {
						'line-color': '#6e6e6e',
						'line-width': [
							'interpolate', ['linear'], ['zoom'],
							10, ['match', ['get', 'kind'], ['motorway', 'trunk'], 0.8, ['primary', 'secondary'], 0.5, 0.25],
							15, ['match', ['get', 'kind'], ['motorway', 'trunk'], 2.4, ['primary', 'secondary'], 1.6, 0.9]
						]
					}
				},
				'fill'
			);
			map.addLayer({ id: 'outside', type: 'fill', source: 'outside', paint: { 'fill-color': '#ffffff', 'fill-opacity': OUTSIDE_FADE } });
			map.addLayer({ id: 'outline', type: 'line', source: 'tracts', paint: { 'line-color': '#ffffff', 'line-width': 0.5, 'line-opacity': 0.9 } });
			// ward / riding lines: dark over a white casing, as on the social-geography maps
			map.addLayer({ id: 'boundaries-white', type: 'line', source: 'boundaries', paint: { 'line-color': '#ffffff', 'line-width': 2.5, 'line-opacity': 0.85 } });
			map.addLayer({ id: 'boundaries-black', type: 'line', source: 'boundaries', paint: { 'line-color': '#000000', 'line-width': 0.9 } });
			map.addLayer({ id: 'city-white', type: 'line', source: 'city', paint: { 'line-color': '#ffffff', 'line-width': 4.5 } });
			map.addLayer({ id: 'city-black', type: 'line', source: 'city', paint: { 'line-color': '#000000', 'line-width': 1.5 } });
			const on = ['boolean', ['feature-state', 'hover'], false];
			map.addLayer({ id: 'hover-casing', type: 'line', source: 'tracts', paint: { 'line-color': '#000000', 'line-width': ['case', on, 5, 0] } });
			map.addLayer({ id: 'hover', type: 'line', source: 'tracts', paint: { 'line-color': HOVER_COLOUR, 'line-width': ['case', on, 3, 0] } });

			ready = true;
		});

		// Mouse: hover. Touch: tap (a tap on empty map closes the readout).
		const propsAt = (point) => map.queryRenderedFeatures(point, { layers: ['fill'] })[0]?.properties ?? null;
		map.on('mousemove', 'fill', (e) => {
			map.getCanvas().style.cursor = 'crosshair'; // the target pointer used on the site's other maps
			setHovered(e.features[0].properties);
		});
		map.on('mouseleave', 'fill', () => {
			map.getCanvas().style.cursor = '';
			setHovered(null);
		});
		map.on('click', (e) => setHovered(propsAt(e.point)));

		return () => map.remove();
	});
</script>

<div class="map-wrap">
	<div class="map" bind:this={container} role="group" aria-label={label}></div>
	{#if hoveredProps}
		<div class="readout" aria-live="polite"><slot props={hoveredProps} /></div>
	{:else}
		<div class="hint" aria-hidden="true">{touchOnly ? 'Tap' : 'Hover over'} a tract for values</div>
	{/if}
</div>

<style>
	/* the rotated city is wide and short, so the map is too */
	.map-wrap {
		position: relative;
		width: 100%;
		aspect-ratio: 1.59;
		min-height: 320px;
		border: 1px solid #dcdcdc;
		box-sizing: border-box;
	}
	.map {
		position: absolute;
		inset: 0;
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
		bottom: 8px;
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

	@media (max-width: 900px) {
		.map-wrap {
			aspect-ratio: 4 / 3;
		}
	}
</style>
