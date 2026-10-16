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
	export let leftColor = null; // small swatch dot beside each end caption
	export let rightColor = null;
	export let showNoData = true;
	export let naColor = '#e6e6e1';
	export let hatchColor = '#c4c4bc';
	export let label = ''; // accessible description of the whole legend
	export let maxWidth = '420px'; // any CSS width; the diverging scale uses '100%' so its two captions have room
</script>

<div class="legend" role="img" aria-label={label || title} style:--legend-max={maxWidth}>
	{#if title}<div class="legend-title">{title}</div>{/if}
	<div class="legend-row">
		<div class="legend-scale">
			<div class="legend-bar">
				{#each colors as c}
					<span style:background={c}></span>
				{/each}
			</div>
			<div class="legend-ticks">
				{#each breaks as b, i}
					<span style:left="{((i + 1) / colors.length) * 100}%">{format(b)}</span>
				{/each}
			</div>
			{#if leftLabel || rightLabel}
				<div class="legend-ends">
					<span class="end end-left">
						{#if leftColor}<i style:background={leftColor}></i>{/if}{leftLabel}
					</span>
					<span class="end end-right">
						{rightLabel}{#if rightColor}<i style:background={rightColor}></i>{/if}
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
	.legend-title {
		color: var(--brandGray60);
		font-size: 11px;
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
		height: 18px;
		font-size: 11px;
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
		font-family: OpenSansBold, sans-serif;
		font-size: 11.5px;
		line-height: 1.3;
		color: var(--brandGray80);
	}
	.end {
		display: inline-flex;
		align-items: baseline;
		gap: 5px;
		max-width: 50%;
	}
	.end-right {
		text-align: right;
		justify-content: flex-end;
	}
	.end i {
		flex: none;
		width: 9px;
		height: 9px;
		border: 1px solid rgba(0, 0, 0, 0.2);
		transform: translateY(0.5px);
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
</style>
