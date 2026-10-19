<script>
	// The opening graphic: census-tract turnout, with a compact toggle between the mean of the
	// three elections and each election on its own. All four views use the same fixed classes
	// (see TURNOUT_BREAKS in ../config.js), so flipping between them is a like-for-like comparison.

	import TractMap from './TractMap.svelte';
	import FigureTitle from './FigureTitle.svelte';
	import MapLegend from './MapLegend.svelte';
	import { tracts } from '../data.js';
	import { TURNOUT_VIEWS, TURNOUT_BREAKS, TURNOUT_COLOURS, NA_COLOUR, HATCH_COLOUR } from '../config.js';
	import { fmtTurnout, fmtPct } from '../format.js';

	export let initialView = 'mean';

	let viewKey = initialView;
	$: view = TURNOUT_VIEWS.find((v) => v.key === viewKey);
</script>

<figure class="turnout-map">
	<FigureTitle title="Voter turnout in Toronto, by census tract" subtitle={view.subtitle} />

	<div class="controls">
		<div class="seg" role="group" aria-label="Turnout measure shown on the map">
			{#each TURNOUT_VIEWS as v}
				<button type="button" aria-pressed={v.key === viewKey} on:click={() => (viewKey = v.key)}>
					{v.label}
				</button>
			{/each}
		</div>
	</div>

	<MapLegend
		colors={TURNOUT_COLOURS}
		breaks={TURNOUT_BREAKS}
		format={(v) => fmtPct(v)}
		naColor={NA_COLOUR}
		hatchColor={HATCH_COLOUR}
		title="Turnout: votes cast as a share of citizens aged 18+"
		label="Turnout colour scale, from under 35 percent in the palest blue to 80 percent and over in the darkest blue"
	/>

	<TractMap
		{tracts}
		valueKey={view.field}
		breaks={TURNOUT_BREAKS}
		colors={TURNOUT_COLOURS}
		label={`Map of turnout by census tract in Toronto: ${view.label}. Hover or tap a tract for its turnout in each election.`}
		let:props
	>
		<div class="ct">Census tract {props.name}</div>
		{#if props.mean_turnout == null}
			<div class="row"><span class="k">No reliable turnout estimate</span></div>
		{:else}
			<div class="row big"><span class="k">{view.label}</span><span class="v">{fmtTurnout(props[view.field], 1)}</span></div>
			{#each TURNOUT_VIEWS.filter((v) => v.key !== viewKey) as v}
				<div class="row dim"><span class="k">{v.label}</span><span class="v">{fmtTurnout(props[v.field], 1)}</span></div>
			{/each}
		{/if}
	</TractMap>

	<figcaption class="map-note">
			Turnout is votes cast divided by Canadian citizens aged 18+ in each 2021 census tract. Poll results were apportioned to tracts, so a few small tracts come out above 100%.
	</figcaption>
</figure>

<style>
	.turnout-map {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	.controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 6px 14px;
		margin-bottom: 10px;
	}

	/* the site's segmented toggle (as on the social-geography page); each button keeps its own
	   border and overlaps its neighbours by 1px, so it still reads as one control when the
	   buttons wrap onto a second row on a phone */
	.seg {
		display: flex;
		flex-wrap: wrap;
		padding: 0 1px 1px 0;
	}
	.seg button {
		font-family: OpenSans, sans-serif;
		font-size: 14px;
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
	.seg button[aria-pressed='true'] {
		background: var(--brandDarkBlue);
		border-color: var(--brandDarkBlue);
		color: white;
		position: relative;
	}
	.seg button:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: 1px;
		position: relative;
	}

	:global(.turnout-map .legend) {
		margin-bottom: 8px;
	}
	.map-note {
		margin: 6px 0 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}

	@media (max-width: 600px) {
		/* two by two, rather than one button spilling onto its own line */
		.seg {
			display: grid;
			grid-template-columns: 1fr 1fr;
			width: 100%;
			box-sizing: border-box;
		}
		.seg button {
			font-size: 13px;
			padding: 7px 6px;
		}
	}
</style>
