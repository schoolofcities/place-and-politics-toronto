<script>
	// Census-tract scores on PLS Component 1, the model's main axis of neighbourhood
	// difference. Diverging scale centred on zero, so the two ends are immediately
	// distinguishable from each other and from the (blue, sequential) turnout map.

	import TractMap from './TractMap.svelte';
	import FigureTitle from './FigureTitle.svelte';
	import MapLegend from './MapLegend.svelte';
	import { tracts, meta } from '../data.js';
	import {
		COMPONENT_BREAKS,
		COMPONENT_COLOURS,
		COMPONENT_SIDES,
		NA_COLOUR,
		HATCH_COLOUR
	} from '../config.js';
	import { fmtScore, fmtTurnout, fmtR } from '../format.js';
	import { onMount } from 'svelte';
	import { legendClassWidth } from './legendScale.js';

	// "Tap" on touch-only screens, "Hover over" otherwise (set once in the browser)
	let touchOnly = false;
	let mounted = false;
	onMount(() => {
		touchOnly = window.matchMedia('(hover: none)').matches;
		mounted = true;
	});

	// same width per colour class as the first turnout map's legend (7 classes here vs 5 there);
	// full width until that's been measured
	$: legendWidth = $legendClassWidth ? `${$legendClassWidth * COMPONENT_COLOURS.length}px` : '100%';

	const r = meta.component_1.turnout_corr;
</script>

<figure class="component-map">
	<FigureTitle title="The neighbourhood pattern behind turnout" subtitle="Census tracts scored on the mix of characteristics most closely tied to voting" />

	<MapLegend
		colors={COMPONENT_COLOURS}
		breaks={COMPONENT_BREAKS}
		format={(v) => fmtScore(v, 0)}
		showNoData={false}
		endsAbove
		endCells={2.5}
		centerLabel="Average tract"
		centerTick="0"
		leftLabel={COMPONENT_SIDES.low.label}
		rightLabel={COMPONENT_SIDES.high.label}
		maxWidth={legendWidth}
		label={`First component score scale, from ${COMPONENT_SIDES.low.long} at the low end in red to ${COMPONENT_SIDES.high.long} at the high end in blue`}
	/>

	<!-- under the legend, as on the first map: "No data" at its left edge, the hint at its right -->
	<div class="legend-extra" style:width={$legendClassWidth ? legendWidth : null}>
		<span class="extra-na"><span class="swatch-na" style:--na={NA_COLOUR} style:--hatch={HATCH_COLOUR}></span>No data</span>
		{#if mounted}<span aria-hidden="true">{touchOnly ? 'Tap' : 'Hover over'} a tract for values</span>{/if}
	</div>

	<TractMap
		{tracts}
		valueKey="component_1"
		breaks={COMPONENT_BREAKS}
		colors={COMPONENT_COLOURS}
		label="Map of first component scores by census tract in Toronto. Hover or tap a tract for its score and mean turnout."
		showHint={false}
		let:props
	>
		<div class="ct">Census tract {props.name}</div>
		{#if props.component_1 == null}
			<div class="row"><span class="k">No reliable score</span></div>
		{:else}
			<div class="row big"><span class="k">First component</span><span class="v">{fmtScore(props.component_1, 1)}</span></div>
			<div class="row"><span class="k">Mean turnout</span><span class="v">{fmtTurnout(props.mean_turnout, 1)}</span></div>
		{/if}
	</TractMap>

	<figcaption class="map-note">
		Colours show each tract's score on the first component, the main pattern found by Partial Least Squares (PLS) regression when relating 70 neighbourhood characteristics to turnout; 0 is the average tract. Across tracts, higher scores go with higher mean turnout (r = {fmtR(r)}), which describes places, not individual voters.
	</figcaption>
</figure>

<style>
	.component-map {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	:global(.component-map .legend) {
		margin-top: 20px; /* more room below the subtitle */
		margin-bottom: 8px;
	}
	/* legend centred (MapLegend is shared, so only on this map) */
	:global(.component-map .legend-title) {
		text-align: center;
	}
	:global(.component-map .legend-row) {
		justify-content: center;
	}

	/* same row as under the first map's legend */
	.legend-extra {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		max-width: 100%;
		align-items: center;
		gap: 4px 16px;
		margin: 0 auto -5px;
		font-size: 12px;
		color: var(--brandGray70);
	}
	.extra-na {
		display: inline-flex;
		align-items: center;
		gap: 5px;
	}
	.swatch-na {
		width: 12px;
		height: 10px;
		border: 1px solid rgba(0, 0, 0, 0.15);
		background: repeating-linear-gradient(45deg, var(--hatch) 0 1.5px, var(--na) 1.5px 4px);
	}
	/* the body text's width: sized and padded like the global `.text` column (694px max, 25px
	   side padding), so its edges line up with the paragraphs */
	.map-note {
		max-width: 694px;
		width: calc(100% - 50px);
		padding: 0 25px;
		margin: 6px auto 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
