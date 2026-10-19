<script>
	// Diverging bar chart of what Component 1 is made of: every variable that matters to the model
	// overall (VIP > 1), ranked from the strongest association with higher turnout (top) to the
	// strongest association with lower turnout (bottom). Bars run left (negative loading) or right
	// (positive loading) from a zero line; each label sits on the empty half opposite its bar, next
	// to the zero line, so names stay readable at phone width without a label column.
	// Built in HTML/CSS rather than SVG so long labels wrap naturally.
	//
	// Wording: a "loading" is how strongly a variable moves with the Component 1 score, and that score
	// moves with turnout, so the chart calls it the strength of association with turnout.

	import FigureTitle from './FigureTitle.svelte';
	import { ingredientRows, ingredientMeta, meta } from '../data.js';
	import { COMPONENT_LOW_COLOUR, COMPONENT_HIGH_COLOUR } from '../config.js';
	import { fmtLoading, fmtPct } from '../format.js';

	const AXIS_MAX = 0.25; // each half of the chart spans 0 to this loading
	const TICKS = [-0.2, -0.1, 0, 0.1, 0.2];

	const rows = ingredientRows.map((d) => ({ ...d, side: d.loading >= 0 ? 'high' : 'low' }));
	const c1 = meta.component_1;

	let figure;
	let active = null; // the row whose details are open
	let tipStyle = '';

	function open(row, event) {
		active = row.variable;
		const rowBox = event.currentTarget.getBoundingClientRect();
		const top = rowBox.bottom - figure.getBoundingClientRect().top + 4; // just under the row
		// keep the box inside the figure: centred, clamped to both edges
		const width = Math.min(260, figure.clientWidth - 8);
		const left = Math.max(0, Math.min(figure.clientWidth - width, figure.clientWidth / 2 - width / 2));
		tipStyle = `top:${top}px; left:${left}px; width:${width}px`;
	}
	function close(row) {
		if (active === row.variable) active = null;
	}
	function toggle(row, event) {
		// a tap on touch screens, where there is no hover
		if (active === row.variable) active = null;
		else open(row, event);
	}
	const describe = (d) =>
		`${d.label}: association strength with ${d.loading >= 0 ? 'higher' : 'lower'} turnout ${fmtLoading(d.loading)}, on a unitless scale where 0 is no association`;

	$: activeRow = rows.find((d) => d.variable === active);
</script>

<figure class="loading-chart" bind:this={figure}>
	<FigureTitle title="What Component 1 is made of" subtitle="Neighbourhood characteristics ranked by their association with turnout" />

	<div class="heads" aria-hidden="true">
		<div class="head head-low"><i style:background={COMPONENT_LOW_COLOUR}></i>Associated with lower turnout</div>
		<div class="head head-high">Associated with higher turnout<i style:background={COMPONENT_HIGH_COLOUR}></i></div>
	</div>

	<ul class="rows" aria-label="Neighbourhood characteristics ranked by their association with turnout">
		<!-- faint guide lines at each axis tick; the zero line is the heavier one -->
		{#each TICKS as t}
			<li class="gridline" class:zero={t === 0} style:left="{50 + (t / AXIS_MAX) * 50}%" aria-hidden="true"></li>
		{/each}
		{#each rows as d (d.variable)}
			<li class="item">
				<button
					type="button"
					class="row {d.side}"
					class:active={active === d.variable}
					aria-label={describe(d)}
					aria-describedby={active === d.variable ? 'loading-tip' : undefined}
					on:mouseenter={(e) => open(d, e)}
					on:mouseleave={() => close(d)}
					on:focus={(e) => open(d, e)}
					on:blur={() => close(d)}
					on:click={(e) => toggle(d, e)}
					on:keydown={(e) => e.key === 'Escape' && (active = null)}
				>
					<span class="half left">
						{#if d.side === 'low'}
							<span class="bar" style:width="{(Math.abs(d.loading) / AXIS_MAX) * 100}%" style:background={COMPONENT_LOW_COLOUR}></span>
						{:else}
							<span class="label">{d.label}</span>
						{/if}
					</span>
					<span class="half right">
						{#if d.side === 'high'}
							<span class="bar" style:width="{(Math.abs(d.loading) / AXIS_MAX) * 100}%" style:background={COMPONENT_HIGH_COLOUR}></span>
						{:else}
							<span class="label">{d.label}</span>
						{/if}
					</span>
				</button>
			</li>
		{/each}
	</ul>

	<div class="axis" aria-hidden="true">
		{#each TICKS as t}
			<span style:left="{50 + (t / AXIS_MAX) * 50}%">{t === 0 ? '0' : fmtLoading(t)}</span>
		{/each}
	</div>
	<div class="axis-title" aria-hidden="true">
		<b>Association strength</b>
		<span>a unitless score: 0 means no link, and the longer the bar, the stronger the link</span>
	</div>

	{#if activeRow}
		<div class="tip" id="loading-tip" role="tooltip" style={tipStyle}>
			<div class="tip-name">{activeRow.plain_name}</div>
			<div class="tip-row"><span>Association strength</span><b>{fmtLoading(activeRow.loading)}</b></div>
			<div class="tip-unit">Unitless score; 0 = no association with turnout</div>
		</div>
	{/if}

	<figcaption class="note">
		Each bar shows how strongly a neighbourhood characteristic is tied to the main pattern behind Toronto's turnout differences (the map above), as a unitless score where 0 means no association. Bars pointing right are characteristics more common where turnout tends to be higher; bars pointing left, where it tends to be lower. Shown are the {rows.length} of {ingredientMeta.nModelVariables} characteristics that matter most to the Partial Least Squares model. For reference, tracts on the higher-turnout side of the pattern average {fmtPct(c1.mean_turnout_score_above_0)} turnout, and those on the lower side {fmtPct(c1.mean_turnout_score_below_0)}. These are associations between places, not evidence that any one characteristic changes whether people vote.
	</figcaption>
</figure>

<style>
	.loading-chart {
		position: relative;
		margin: 0;
		font-family: OpenSans, sans-serif;
		color: var(--brandGray90);
	}

	/* the two headings sit over their halves of the chart */
	.heads {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 8px;
		margin-bottom: 8px;
	}
	.head {
		display: flex;
		align-items: center;
		gap: 6px;
		min-width: 0;
		padding: 0 6px;
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		line-height: 1.25;
	}
	.head-low {
		justify-content: flex-start;
	}
	.head-high {
		justify-content: flex-end;
		text-align: right;
	}
	.head i {
		width: 10px;
		height: 10px;
		flex: none;
	}

	.rows {
		position: relative;
		list-style: none;
		margin: 0;
		padding: 0;
	}
	/* guide lines behind the bars: faint at each tick, dark at zero */
	.gridline {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 1px;
		background: rgba(0, 0, 0, 0.1);
		pointer-events: none;
	}
	.gridline.zero {
		background: var(--brandGray90);
		z-index: 1;
	}
	/* each row is a button, so it is reachable and openable from the keyboard */
	.row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		align-items: center;
		width: 100%;
		min-height: 26px;
		margin: 0;
		padding: 0;
		border: 0;
		background: none;
		font: inherit;
		color: inherit;
		text-align: inherit;
		cursor: default;
		position: relative;
	}
	.row:hover,
	.row.active {
		background: rgba(30, 55, 101, 0.07);
	}
	.row:focus-visible {
		outline: 2px solid var(--linkHover);
		outline-offset: -2px;
	}

	.half {
		display: flex;
		align-items: center;
		gap: 5px;
		min-width: 0;
		padding: 2px 0;
	}
	.half.left {
		justify-content: flex-end;
		padding-right: 1px;
	}
	.half.right {
		justify-content: flex-start;
		padding-left: 1px;
	}
	.bar {
		display: block;
		height: 16px;
		flex: none;
	}
	.label {
		font-size: 12.5px;
		line-height: 1.25;
		padding: 0 7px;
	}
	.half.left .label {
		text-align: right;
	}

	.axis {
		position: relative;
		height: 16px;
		margin-top: 2px;
		font-size: 10.5px;
		font-variant-numeric: tabular-nums;
		color: var(--brandGray60);
	}
	.axis span {
		position: absolute;
		transform: translateX(-50%);
		white-space: nowrap;
	}
	.axis-title {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1px;
		text-align: center;
		font-size: 11px;
		line-height: 1.35;
		color: var(--brandGray60);
	}
	.axis-title b {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
		font-size: 12px;
		color: var(--brandGray80);
	}

	.tip {
		position: absolute;
		z-index: 5;
		box-sizing: border-box;
		background: rgba(255, 255, 255, 0.97);
		border: 1px solid var(--brandGray);
		padding: 8px 10px;
		font-size: 12px;
		pointer-events: none;
	}
	.tip-name {
		font-family: OpenSansBold, sans-serif;
		margin-bottom: 3px;
	}
	.tip-row {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		font-variant-numeric: tabular-nums;
	}
	.tip-unit {
		margin-top: 3px;
		font-size: 11px;
		color: var(--brandGray60);
	}
	.tip-row span {
		color: var(--brandGray70);
	}
	.tip-row b {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}

	.note {
		margin: 10px 0 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}

	@media (max-width: 600px) {
		.label {
			font-size: 12px;
			padding: 0 5px;
		}
		.head {
			font-size: 12px;
		}
	}
</style>
