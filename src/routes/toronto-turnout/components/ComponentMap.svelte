<script>
	// Census-tract scores on PLS Component 1, the model's main axis of neighbourhood
	// difference. Diverging scale centred on zero, so the two ends are immediately
	// distinguishable from each other and from the (blue, sequential) turnout map.

	import TractMap from './TractMap.svelte';
	import MapLegend from './MapLegend.svelte';
	import { tracts, city, meta, boundaries } from '../data.js';
	import {
		COMPONENT_BREAKS,
		COMPONENT_COLOURS,
		COMPONENT_SIDES,
		COMPONENT_LOW_COLOUR,
		COMPONENT_HIGH_COLOUR,
		NA_COLOUR,
		HATCH_COLOUR
	} from '../config.js';
	import { fmtScore, fmtTurnout, fmtR } from '../format.js';

	const r = meta.component_1.turnout_corr;
</script>

<figure class="component-map">
	<MapLegend
		colors={COMPONENT_COLOURS}
		breaks={COMPONENT_BREAKS}
		format={(v) => fmtScore(v, 0)}
		naColor={NA_COLOUR}
		hatchColor={HATCH_COLOUR}
		title="Component 1 score (0 = the citywide average)"
		leftLabel={COMPONENT_SIDES.low.label}
		rightLabel={COMPONENT_SIDES.high.label}
		maxWidth="100%"
		leftColor={COMPONENT_LOW_COLOUR}
		rightColor={COMPONENT_HIGH_COLOUR}
		label={`Component 1 score scale, from ${COMPONENT_SIDES.low.long} at the low end in red to ${COMPONENT_SIDES.high.long} at the high end in blue`}
	/>

	<TractMap
		{tracts}
		{city}
		valueKey="component_1"
		boundaries={boundaries.municipal}
		breaks={COMPONENT_BREAKS}
		colors={COMPONENT_COLOURS}
		label="Map of Component 1 scores by census tract in Toronto. Hover or tap a tract for its score and mean turnout."
		let:props
	>
		<div class="ct">Census tract {props.name}</div>
		{#if props.component_1 == null}
			<div class="row"><span class="k">No reliable score</span></div>
		{:else}
			<div class="row big"><span class="k">Component 1</span><span class="v">{fmtScore(props.component_1, 1)}</span></div>
			<div class="row"><span class="k">Mean turnout</span><span class="v">{fmtTurnout(props.mean_turnout, 1)}</span></div>
		{/if}
	</TractMap>

	<figcaption class="map-note">
		Component 1 is the main pattern a statistical model found when relating 70 neighbourhood characteristics to turnout. Across tracts, higher scores go with higher mean turnout (r = {fmtR(r)}), which describes places, not individual voters. Dark lines show city ward boundaries. Side labels are provisional. Basemap © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors.
	</figcaption>
</figure>

<style>
	.component-map {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	:global(.component-map .legend) {
		margin-bottom: 8px;
	}
	.map-note {
		margin: 6px 0 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
	.map-note a {
		color: inherit;
	}
</style>
