<script>
	// "Explore the ingredients": pick one neighbourhood characteristic and see how it lines up
	// with mean turnout across Toronto's census tracts -- a scatterplot with its trend line and
	// Pearson correlation, linked to a small map of the same characteristic. Hovering a dot
	// outlines its tract on the map, and hovering the map marks its dot on the scatterplot.
	// Exploratory only: it shows association between places, not cause.

	import ExplorerScatter from './ExplorerScatter.svelte';
	import TractMap from './TractMap.svelte';
	import MapLegend from './MapLegend.svelte';
	import { tracts, meta, tractRows, explorerVariables, explorerGroups } from '../data.js';
	import { CENSUS_COLOURS, NA_COLOUR, HATCH_COLOUR } from '../config.js';
	import { variableFormat, fmtR, fmtP, fmtTurnout } from '../format.js';
	import { linearFit, quantileBreaks, spread } from '../stats.js';

	let field = 'block1_bachelors_or_higher_25_64_share';
	let activeId = null; // tract highlighted on both the scatterplot and the map
	// Line the details box's top up with the top of the map's first reference-layer button
	// ("Former municipalities"): that sits 107px above the map's bottom (the stack's 43px offset,
	// set below, plus three 20px buttons and two 2px gaps). Measured, since the map's height
	// changes with width; only when map and scatterplot sit side by side.
	const FIRST_BUTTON_FROM_BOTTOM = 43 + 3 * 20 + 2 * 2;
	let mapColH = 0;
	let scatterTopH = 0; // the stat line + scatterplot above the box
	let pageW = 1000;
	$: detailsTop = pageW > 800 ? Math.max(8, mapColH - FIRST_BUTTON_FROM_BOTTOM - scatterTopH) : 8;

	// the highlighted tract's record, for the one details box under the scatterplot
	$: activeRow = activeId == null ? null : tractRows.find((d) => d.ct === activeId) ?? null;

	$: variable = explorerVariables.find((v) => v.field === field);
	$: fmt = variableFormat(variable.format);
	$: pairs = tractRows.filter((d) => d[field] != null && d.mean_turnout != null);
	$: fit = linearFit(pairs.map((d) => [d[field], d.mean_turnout]));

	// map classes: quintiles of the selected variable, as on the site's other census maps
	$: breaks = quantileBreaks(pairs.map((d) => d[field]), 5);
	$: colors = spread(CENSUS_COLOURS, breaks.length + 1);

	const nNoData = Object.keys(meta.no_data_tracts).length;
	$: statR = fit ? `r = ${fmtR(fit.r)}` : '';
	// as on the social-geography page: r, p and the number of tracts, flagging non-significance
	$: statRest = fit ? ` · ${fmtP(fit.p)} · ${fit.n} tracts${fit.p < 0.05 ? '' : ' · not significant'}` : 'Not enough data';
	$: announce = fit
		? `Showing ${variable.label} against mean turnout: correlation ${fmtR(fit.r)}, ${fmtP(fit.p)}, across ${fit.n} tracts${fit.p < 0.05 ? '' : ', not significant'}`
		: '';
</script>

<svelte:window bind:innerWidth={pageW} />

<div class="explorer">
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
		<div class="map-col" bind:clientHeight={mapColH}>
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
				showReadout={false}
			/>
		</div>

		<div class="scatter-col">
			<div bind:clientHeight={scatterTopH}>
				<p class="stat" aria-hidden="true"><strong>{statR}</strong>{statRest}</p>
				<ExplorerScatter
					rows={tractRows}
					xField={field}
					xLabel={variable.label}
					xAxisFormat={fmt.axis}
					xValueFormat={fmt.value}
					xFromZero={variable.format === 'percent' || variable.format === 'km' || variable.format === 'density'}
					{fit}
					bind:activeId
					labelOutside={pageW > 800}
					maxHeight={pageW > 800 ? 480 : 400}
				/>
			</div>
			<!-- one details box for both charts, under the scatterplot: whichever tract is hovered
				 on the map or the scatterplot; nothing shown until one is -->
			{#if activeRow}
				<div class="tract-details" aria-hidden="true" style:margin-top="{detailsTop}px">
					<div class="d-ct">Census tract {activeRow.name}</div>
					<div class="d-row"><span>{variable.label}</span><b>{fmt.value(activeRow[field])}</b></div>
					<div class="d-row"><span>Mean turnout</span><b>{fmtTurnout(activeRow.mean_turnout, 1)}</b></div>
				</div>
			{/if}
		</div>
	</div>

	<p class="sr-only" aria-live="polite">{announce}</p>

	<p class="foot">
		r = Pearson correlation across census tracts, with the least-squares trend line. Tracts are not people: a correlation here describes places, not voters, and many of these characteristics move together. {nNoData} tracts with no reliable data at all are left out, and so is any tract missing the selected characteristic (hatched on the map).
	</p>
</div>

<style>
	/* this map's reference-layer buttons sit 16px lower than on the other maps (TractMap.svelte
	   puts them at bottom: 59px), on phones TractMap moves them below
	   the map, so this only applies above 600px */
	@media (min-width: 601px) {
		:global(.explorer .map-wrap .boundary-control) {
			bottom: 43px;
		}
	}
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
	/* as on the social-geography page: "r = …" bold black 14px, the rest 13px dark grey */
	.stat {
		margin: 0 0 6px;
		font-size: 13px;
		line-height: 1.45;
		color: var(--brandGray80);
		text-align: center;
		font-variant-numeric: tabular-nums;
	}
	.stat strong {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
		font-size: 14px;
		color: black;
	}

	/* the one details box, under the scatterplot. (Not called `.details`: that's a global brand
	   component in global-styles.css, with a rounded corner and large margins.) */
	.tract-details {
		box-sizing: border-box;
		padding: 6px 10px;
		border: 1px solid var(--brandGray);
		background: white;
		font-size: 12px;
		line-height: 1.4;
		font-variant-numeric: tabular-nums;
	}
	.d-ct {
		font-size: 11px;
		color: var(--brandGray60);
	}
	.d-row {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 10px;
	}
	.d-row span {
		color: var(--brandGray70);
	}
	.d-row b {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
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
	/* the body text's width: sized and padded like the global `.text` column (694px max, 25px
	   side padding), so its edges line up with the paragraphs */
	.foot {
		max-width: 694px;
		width: calc(100% - 50px);
		padding: 0 25px;
		margin: 10px auto 0;
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
		/* stacked under the map: the scatterplot (with its stat line and details box) at most
		   400px wide, centred; ExplorerScatter caps its height at 400px here too */
		.scatter-col {
			width: 100%;
			max-width: 400px;
			margin: 0 auto;
		}
	}
</style>
