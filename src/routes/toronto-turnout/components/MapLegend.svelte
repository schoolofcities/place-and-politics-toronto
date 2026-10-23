<script>
	// Legend for a classed choropleth: one bar of equal-width classes, with each break
	// labelled once under the boundary it marks (same pattern as the mapper's legend in
	// routes/social-geography-and-the-mayoral-vote). Optional captions sit under the two
	// ends of the bar, used for the diverging Component 1 scale.

	export let colors = [];
	export let breaks = []; // colors.length - 1 break values
	export let format = (v) => v;
	export let title = '';
	export let leftLabel = '';
	export let rightLabel = '';
	export let showNoData = true;
	export let naColor = '#e6e6e1';
	export let hatchColor = '#c4c4bc';
	export let label = ''; // accessible description of the whole legend
	export let endCells = 0; // >0: cap each end caption at this many colour cells' width (it wraps onto more lines)
	export let centerLabel = ''; // a label at the bar's midpoint, above it (with endsAbove), e.g. "The average tract"
	export let centerTick = ''; // an extra tick number at the bar's midpoint, e.g. "0"
	export let endsAbove = false; // end captions above the bar (default: below the tick numbers)
	export let maxWidth = '420px'; // any CSS width
</script>

<div
	class="legend"
	role="img"
	aria-label={label || title}
	style:--legend-max={maxWidth}
	style:--end-max={endCells ? `${(endCells / colors.length) * 100}%` : null}
>
	{#if title}<div class="legend-title">{title}</div>{/if}
	<div class="legend-row">
		<div class="legend-scale">
			{#if (leftLabel || rightLabel) && endsAbove}
				<div class="legend-ends above">
					<span class="end end-left">
						{leftLabel}
					</span>
					{#if centerLabel}<span class="center-label">{centerLabel}</span>{/if}
					<span class="end end-right">
						{rightLabel}
					</span>
				</div>
			{/if}
			<div class="legend-bar">
				{#each colors as c}
					<span style:background={c}></span>
				{/each}
			</div>
			<div class="legend-ticks">
				{#each breaks as b, i}
					<span style:left="{((i + 1) / colors.length) * 100}%">{format(b)}</span>
				{/each}
				{#if centerTick}<span style:left="50%">{centerTick}</span>{/if}
			</div>
			{#if (leftLabel || rightLabel) && !endsAbove}
				<div class="legend-ends">
					<span class="end end-left">
						{leftLabel}
					</span>
					<span class="end end-right">
						{rightLabel}
					</span>
				</div>
			{/if}
		</div>
		{#if showNoData}
			<div class="legend-na"><span class="swatch-na" style:--na={naColor} style:--hatch={hatchColor}></span>No data</div>
		{/if}
	</div>
</div>

<style>
	.legend {
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		color: var(--brandGray90);
	}
	/* title and tick numbers: same size and darkness */
	.legend-title {
		color: var(--brandGray90);
		font-size: 13px;
		margin-bottom: 3px;
	}
	.legend-row {
		display: flex;
		align-items: flex-start;
		flex-wrap: wrap;
		gap: 6px 18px;
	}
	.legend-scale {
		width: min(var(--legend-max), 100%);
		flex: 0 1 var(--legend-max);
	}
	.legend-bar {
		display: flex;
		height: 12px;
		border: 1px solid rgba(0, 0, 0, 0.15);
	}
	.legend-bar span {
		flex: 1;
	}
	.legend-ticks {
		position: relative;
		height: 20px;
		font-size: 13px;
		color: var(--brandGray90);
		font-variant-numeric: tabular-nums;
	}
	.legend-ticks span {
		position: absolute;
		top: 2px;
		transform: translateX(-50%);
		white-space: nowrap;
	}
	.legend-ends {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		margin-top: 2px;
		font-family: OpenSansItalic, sans-serif; /* italic, not bold */
		font-size: 12px;
		line-height: 1.3;
		color: var(--brandBlack);
	}
	.legend-ends.above {
		position: relative;
		margin: 0 0 4px;
	}
	/* midpoint label, centred over the bar between the two end captions, with a short tick
	   down to the bar's centre */
	.center-label {
		position: absolute;
		left: 50%;
		bottom: 0;
		transform: translateX(-50%);
		padding-bottom: 6px;
		white-space: nowrap;
		font-family: OpenSansItalic, sans-serif;
		color: var(--brandBlack); /* italic and black, like the end captions */
	}
	.center-label::after {
		content: '';
		position: absolute;
		left: 50%;
		bottom: 0;
		height: 5px;
		border-left: 1px solid var(--brandGray80);
	}
	.end {
		display: inline-flex;
		align-items: baseline;
		gap: 5px;
		max-width: var(--end-max, 50%);
	}
	.end-right {
		text-align: right;
		justify-content: flex-end;
	}
	.legend-na {
		display: flex;
		align-items: center;
		gap: 5px;
		font-size: 11px;
		color: var(--brandGray60);
		margin-top: 1px;
	}
	.swatch-na {
		width: 12px;
		height: 10px;
		border: 1px solid rgba(0, 0, 0, 0.15);
		/* the same diagonal hatching the map draws over tracts with no data */
		background: repeating-linear-gradient(45deg, var(--hatch) 0 1.5px, var(--na) 1.5px 4px);
	}
	/* phones: the captions above the bar (and its midpoint label) 2px smaller, to fit the narrow bar */
	@media (max-width: 600px) {
		.legend-ends {
			font-size: 10px;
		}
	}
</style>
