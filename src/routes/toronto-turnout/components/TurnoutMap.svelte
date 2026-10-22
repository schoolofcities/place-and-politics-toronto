<script>
	// The opening graphic: census-tract turnout, with a compact toggle between the mean of the
	// three elections and each election on its own. All four views use the same fixed classes
	// (see TURNOUT_BREAKS in ../config.js), so flipping between them is a like-for-like comparison.

	import TractMap from './TractMap.svelte';
	import FigureTitle from './FigureTitle.svelte';
	import MapLegend from './MapLegend.svelte';
	import { tracts } from '../data.js';
	import { onMount } from 'svelte';
	import { legendClassWidth } from './legendScale.js';
	import { TURNOUT_VIEWS, TURNOUT_BREAKS, TURNOUT_COLOURS, NA_COLOUR, HATCH_COLOUR } from '../config.js';
	import { fmtTurnout, fmtPct } from '../format.js';

	export let initialView = 'mean';

	let viewKey = initialView;
	// the legend's width: fixed at about what the button row measured with its earlier, shorter
	// labels (the longer labels made the row, and a legend matched to it, much wider)
	const LEGEND_WIDTH = 440;
	// share the width of one legend class, so the post's other legends can match it
	legendClassWidth.set(LEGEND_WIDTH / TURNOUT_COLOURS.length);

	// "Tap" on touch-only screens, "Hover over" otherwise (set once in the browser)
	let touchOnly = false;
	let mounted = false;
	onMount(() => {
		touchOnly = window.matchMedia('(hover: none)').matches;
		mounted = true;
	});
	$: view = TURNOUT_VIEWS.find((v) => v.key === viewKey);
</script>

<figure class="turnout-map">
	<!-- no subtitle: the buttons below already say which election (or the mean) is shown -->
	<FigureTitle title="Voter turnout in Toronto" />

	<div class="controls">
		<div class="seg" role="group" aria-label="Turnout measure shown on the map">
			{#each TURNOUT_VIEWS as v}
				<button type="button" aria-pressed={v.key === viewKey} on:click={() => (viewKey = v.key)}>
					<span class="lbl" data-text={v.label}>{v.label}</span>
				</button>
			{/each}
		</div>
	</div>

	<MapLegend
		colors={TURNOUT_COLOURS}
		breaks={TURNOUT_BREAKS}
		format={(v) => fmtPct(v)}
		showNoData={false}
		maxWidth="{LEGEND_WIDTH}px"
		title="Votes cast as a share of citizens aged 18+ per census tract (2021)"
		label="Turnout colour scale, from under 35 percent in the palest blue to 80 percent and over in the darkest blue"
	/>

	<!-- under the legend: the "No data" key, and the hover/tap hint (shown here rather than over the map) -->
	<div class="legend-extra" style:width="{LEGEND_WIDTH}px">
		<span class="extra-na"><span class="swatch-na" style:--na={NA_COLOUR} style:--hatch={HATCH_COLOUR}></span>No data</span>
		{#if mounted}<span aria-hidden="true">{touchOnly ? 'Tap' : 'Hover over'} a tract for values</span>{/if}
	</div>

	<TractMap
		{tracts}
		valueKey={view.field}
		breaks={TURNOUT_BREAKS}
		colors={TURNOUT_COLOURS}
		label={`Map of turnout by census tract in Toronto: ${view.short}. Hover or tap a tract for its turnout in each election.`}
		showHint={false}
		let:props
	>
		<!-- compact: everything at one small size, all four measures in button order, the one
			 shown on the map in bold -->
		<div class="compact-readout">
			<div class="ct"><span>Census tract</span><span>{props.name}</span></div>
			{#if props.mean_turnout == null}
				<div class="row"><span class="k">No reliable turnout estimate</span></div>
			{:else}
				{#each TURNOUT_VIEWS as v}
					<div class="row" class:sel={v.key === viewKey}>
						<span class="k">{v.short}</span><span class="v">{fmtTurnout(props[v.field], 1)}</span>
					</div>
				{/each}
			{/if}
		</div>
	</TractMap>

</figure>

<style>
	.turnout-map {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		align-items: center;
		gap: 6px 14px;
		margin-top: 18px; /* more room below the title */
		margin-bottom: 20px; /* and before the legend */
	}

	/* segmented toggle: white buttons with a light grey border, 13px; the chosen one bold at full
	   strength, the others faded (as with the maps' reference-layer buttons). Each button keeps its
	   own border and overlaps its neighbours by 1px, so it still reads as one control when the
	   buttons wrap onto a second row on a phone */
	/* two by two on every screen: two equal columns, as wide as the longest label needs */
	.seg {
		display: grid;
		grid-template-columns: 1fr 1fr;
		width: max-content;
		max-width: 100%;
		box-sizing: border-box;
		padding: 0 1px 1px 0;
	}
	.seg button {
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		margin: 0 -1px -1px 0;
		padding: 5px 10px;
		cursor: pointer;
	}
	.seg button:hover {
		border-color: #9ba1a8;
		position: relative;
	}
	/* chosen: white, bold, full strength; the others: regular weight at 50% opacity */
	.seg button[aria-pressed='false'] {
		opacity: 0.5;
	}
	/* an unchosen button brightens on hover */
	.seg button[aria-pressed='false']:hover {
		opacity: 0.99;
	}
	.seg button[aria-pressed='true'] {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandBlack);
		position: relative;
	}
	/* each label reserves its bold width (an invisible bold copy), so a button doesn't change
	   size when chosen, and the legend sized to this row doesn't shift */
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
	.seg button:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: 1px;
		position: relative;
	}

	:global(.turnout-map .legend) {
		margin-bottom: 8px;
	}
	/* centred under the title and buttons (MapLegend is shared, so only on this map) */
	:global(.turnout-map .legend-title) {
		text-align: center;
	}
	:global(.turnout-map .legend-row) {
		justify-content: center;
	}
	/* the legend's width (same as the buttons'): "No data" at its left edge, the hint at its right */
	/* compact hover readout (see the markup): one 11px size throughout, regular weight except
	   the row for the measure on the map */
	:global(.turnout-map .readout) {
		min-width: 0;
		padding: 5px 8px;
	}
	:global(.turnout-map .compact-readout),
	:global(.turnout-map .compact-readout .ct),
	:global(.turnout-map .compact-readout .row .k),
	:global(.turnout-map .compact-readout .row .v) {
		font-size: 11px;
		line-height: 1.4;
		font-family: OpenSans, sans-serif;
		color: var(--brandGray70);
	}
	/* the census tract line in italics (the site's Open Sans italic face), its id right-aligned
	   like the values below */
	:global(.turnout-map .compact-readout .ct) {
		font-family: OpenSansItalic, sans-serif;
		display: flex;
		justify-content: space-between;
		gap: 10px;
		font-variant-numeric: tabular-nums;
		/* a faint rule under it, separating it from the values */
		padding-bottom: 2px;
		margin-bottom: 2px;
		border-bottom: 1px solid var(--brandGray);
	}
	:global(.turnout-map .compact-readout .row.sel .k),
	:global(.turnout-map .compact-readout .row.sel .v) {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandBlack);
	}
	.legend-extra {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		max-width: 100%;
		align-items: center;
		gap: 4px 16px;
		margin: 0 auto -5px; /* centred; pulled 15px closer to the map below */
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
		/* the same diagonal hatching the map draws over tracts with no data */
		background: repeating-linear-gradient(45deg, var(--hatch) 0 1.5px, var(--na) 1.5px 4px);
	}

	@media (max-width: 600px) {
		/* still two by two, now the full width */
		.seg {
			width: 100%;
		}
		.seg button {
			font-size: 13px;
			padding: 7px 6px;
		}
	}
</style>
