<script>
	// "Explore the ingredients": pick one neighbourhood characteristic and see how it lines up
	// with mean turnout across Toronto's census tracts -- a scatterplot with its trend line and
	// Pearson correlation, linked to a small map of the same characteristic. Hovering a dot
	// outlines its tract on the map, and hovering the map marks its dot on the scatterplot.
	// Exploratory only: it shows association between places, not cause.

	import ExplorerScatter from './ExplorerScatter.svelte';
	import TractMap from './TractMap.svelte';
	import FigureTitle from './FigureTitle.svelte';
	import MapLegend from './MapLegend.svelte';
	import { tracts, meta, tractRows, explorerVariables, explorerGroups } from '../data.js';
	import { CENSUS_COLOURS, NA_COLOUR, HATCH_COLOUR } from '../config.js';
	import { variableFormat, fmtR, fmtTurnout } from '../format.js';
	import { linearFit, quantileBreaks, spread } from '../stats.js';

	export let initialField = 'block1_bachelors_or_higher_25_64_share';

	let field = initialField;
	let activeId = null; // tract highlighted on both the scatterplot and the map

	$: variable = explorerVariables.find((v) => v.field === field);
	$: fmt = variableFormat(variable.format);
	$: pairs = tractRows.filter((d) => d[field] != null && d.mean_turnout != null);
	$: fit = linearFit(pairs.map((d) => [d[field], d.mean_turnout]));

	// map classes: quintiles of the selected variable, as on the site's other census maps
	$: breaks = quantileBreaks(pairs.map((d) => d[field]), 5);
	$: colors = spread(CENSUS_COLOURS, breaks.length + 1);

	const nNoData = Object.keys(meta.no_data_tracts).length;
	$: statText = fit ? `r = ${fmtR(fit.r)} · ${fit.n} tracts` : 'Not enough data';
	$: announce = fit
		? `Showing ${variable.label} against mean turnout: correlation ${fmtR(fit.r)} across ${fit.n} tracts`
		: '';
</script>

<div class="explorer">
	<FigureTitle title="Neighbourhood characteristics and turnout" subtitle="Pick a characteristic to map it by census tract and compare it with mean turnout" />

	<div class="controls">
		<label class="field">
			<span>Neighbourhood characteristic</span>
			<select bind:value={field}>
				{#each explorerGroups as group}
					<optgroup label={group.label}>
						{#each group.variables as v}
							<option value={v.field}>{v.label}</option>
						{/each}
					</optgroup>
				{/each}
			</select>
		</label>
	</div>

	<!-- the map is the larger panel, the scatterplot the smaller, as on the social-geography page -->
	<div class="pair">
		<div class="map-col">
			<MapLegend
				{colors}
				{breaks}
				format={fmt.axis}
				naColor={NA_COLOUR}
				hatchColor={HATCH_COLOUR}
				title="{variable.label}, by fifths of tracts"
				label="Map colour scale for {variable.label}, in fifths of tracts, from lowest in pale green to highest in dark green"
			/>
			<TractMap
				{tracts}
				valueKey={field}
				{breaks}
				{colors}
				{activeId}
				on:hover={(e) => (activeId = e.detail)}
				label="Map of {variable.label} by census tract in Toronto. Hover or tap a tract to see it on the scatterplot."
				let:props
			>
				<div class="ct">Census tract {props.name}</div>
				<div class="row big"><span class="k">{variable.label}</span><span class="v">{fmt.value(props[field])}</span></div>
				<div class="row"><span class="k">Mean turnout</span><span class="v">{fmtTurnout(props.mean_turnout, 1)}</span></div>
			</TractMap>
		</div>

		<div class="scatter-col">
			<p class="stat" aria-hidden="true"><strong>{statText}</strong></p>
			<ExplorerScatter
				rows={tractRows}
				xField={field}
				xLabel={variable.label}
				xAxisFormat={fmt.axis}
				xValueFormat={fmt.value}
				xFromZero={variable.format === 'percent' || variable.format === 'km' || variable.format === 'density'}
				{fit}
				bind:activeId
			/>
		</div>
	</div>

	<p class="sr-only" aria-live="polite">{announce}</p>

	<p class="foot">
		r = Pearson correlation across census tracts, with the least-squares trend line. Tracts are not people: a correlation here describes places, not voters, and many of these characteristics move together. {nNoData} tracts with no reliable data at all are left out, and so is any tract missing the selected characteristic (hatched on the map).
	</p>
</div>

<style>
	.explorer {
		font-family: OpenSans, sans-serif;
		color: var(--brandGray90);
	}
	.controls {
		margin-bottom: 12px;
	}
	.field {
		display: flex;
		flex-direction: column;
		gap: 2px;
		min-width: 0;
		width: min(380px, 100%);
	}
	.field > span {
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		color: var(--brandGray60);
	}
	select {
		font-family: OpenSans, sans-serif;
		font-size: 14px;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		border-radius: 0;
		padding: 6px 8px;
		max-width: 100%;
	}
	select:hover {
		border-color: #9ba1a8;
	}
	select:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: 1px;
	}
	.stat {
		margin: 0 0 6px;
		font-size: 14px;
		text-align: center;
		font-variant-numeric: tabular-nums;
	}
	.stat strong {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
		font-size: 16px;
	}

	.pair {
		display: grid;
		grid-template-columns: minmax(0, 2fr) minmax(0, 1fr);
		gap: 20px 24px;
		align-items: start;
	}
	:global(.explorer .legend) {
		margin-bottom: 8px;
	}
	.foot {
		margin: 10px 0 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0 0 0 0);
		white-space: nowrap;
		border: 0;
	}

	@media (max-width: 800px) {
		.pair {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
