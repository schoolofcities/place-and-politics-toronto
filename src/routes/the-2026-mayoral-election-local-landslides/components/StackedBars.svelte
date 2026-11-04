<script>
	// 100% stacked columns with a percentage label in each segment, used for the polls-by-margin
	// and where-the-votes-came-from charts. `columns` are { key, label, sublabel, segments:
	// [{ key, value }] } with segments listed bottom to top; `colours` maps segment keys to fills
	// and `darkKeys` lists the segments dark enough to need white labels.
	import { scaleBand, scaleLinear } from 'd3';

	// label: for screen readers. ramp: an ordered scale (e.g. margin bands), so the legend is drawn
	// like the poll map's, one bar of joined steps with their labels above; otherwise swatches
	// boldKeys: segments whose labels are bold
	// legendTitle: a heading above the legend, as on the small-multiple maps
	let { columns, colours, darkKeys = [], boldKeys = [], yLabel = '', label = '', ramp = false, legendTitle = '' } = $props();

	let width = $state(760);
	const height = $derived(width < 520 ? 330 : 400);
	// room on the left for the tick labels, and for the axis title when there is one
	const M = $derived({ top: 8, right: 4, bottom: 44, left: width < 520 || !yLabel ? 36 : 58 });

	// little outer padding, so the first bar sits close to the axis labels
	const x = $derived(scaleBand().domain(columns.map((c) => c.key)).range([M.left, width - M.right]).paddingInner(0.22).paddingOuter(0.04));
	const barW = $derived(0.85 * x.bandwidth()); // bars a bit narrower than their band, centred in it
	const y = $derived(scaleLinear().domain([0, 1]).range([height - M.bottom, M.top]));

	const stacked = $derived(
		columns.map((c) => {
			let base = 0;
			return {
				...c,
				segments: c.segments.map((s) => {
					const seg = { ...s, y0: base, y1: base + s.value };
					base += s.value;
					return seg;
				})
			};
		})
	);

	const pct = (v) => `${Math.round(100 * v)}%`;
	const small = $derived(width < 520);
</script>

{#if legendTitle}<p class="legend-title">{legendTitle}</p>{/if}
{#if ramp}
	<div class="ramp-legend">
		<!-- breakpoints at the edges between steps: each band's lower bound ("10–20%" -> 10) -->
		<div class="breaks" style:--steps={Object.keys(colours).length}>
			{#each Object.keys(colours) as key, i (key)}
				<span class="break" style:left="{(100 * i) / Object.keys(colours).length}%">{parseFloat(key)}</span>
			{/each}
		</div>
		<div class="steps">
			{#each Object.entries(colours) as [key, fill] (key)}<span class="step" style:background={fill}></span>{/each}
		</div>
	</div>
{:else}
	<div class="legend">
		{#each Object.entries(colours) as [key, fill] (key)}
			<span class="item"><span class="swatch" style:background={fill}></span>{key}</span>
		{/each}
	</div>
{/if}

<div class="chart" bind:clientWidth={width}>
	<svg {width} {height} role="img" aria-label={label || yLabel}>
		{#each [0, 0.25, 0.5, 0.75, 1] as t (t)}
			<line class="grid" x1={M.left} x2={width - M.right} y1={y(t)} y2={y(t)} />
			<text class="tick" x={M.left - 6} y={y(t)} dy="0.32em" text-anchor="end">{pct(t)}</text>
		{/each}
		{#if yLabel && !small}
			<text class="axis-label" transform="translate(14,{(M.top + height - M.bottom) / 2}) rotate(-90)" text-anchor="middle">{yLabel}</text>
		{/if}

		{#each stacked as c (c.key)}
			<g>
				{#each c.segments as s (s.key)}
					<rect
						x={x(c.key) + (x.bandwidth() - barW) / 2}
						width={barW}
						y={y(s.y1)}
						height={Math.max(0, y(s.y0) - y(s.y1))}
						fill={colours[s.key]}
						stroke="#fff"
						stroke-width="1"
					/>
					{#if y(s.y0) - y(s.y1) >= 13 && barW >= 24}
						<text
							class="seg-label"
							class:light={darkKeys.includes(s.key)}
							class:bold={boldKeys.includes(s.key)}
							x={x(c.key) + x.bandwidth() / 2}
							y={(y(s.y0) + y(s.y1)) / 2}
							dy="0.35em"
							text-anchor="middle">{pct(s.value)}</text
						>
					{/if}
				{/each}
				<text class="col-label" x={x(c.key) + x.bandwidth() / 2} y={height - M.bottom + 16} text-anchor="middle">{c.label}</text>
				<text class="col-sub" x={x(c.key) + x.bandwidth() / 2} y={height - M.bottom + 31} text-anchor="middle">{c.sublabel}</text>
			</g>
		{/each}
	</svg>
</div>

<style>
	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px 18px;
		margin: 0 0 10px;
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		color: var(--brandGray80);
	}
	.item {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.swatch {
		width: 14px;
		height: 14px;
		display: inline-block;
	}
	/* as the small-multiple maps' legend heading */
	.legend-title {
		margin: 0 0 4px;
		text-align: center;
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		color: var(--brandGray70);
	}
	/* as the poll map's legend: breakpoints above a row of joined 40px steps */
	.ramp-legend {
		--step: 40px;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		margin: 0 0 12px;
		font-family: OpenSans, sans-serif;
		color: var(--brandGray70);
	}
	.steps {
		display: flex;
	}
	.step {
		width: var(--step);
		height: 12px;
	}
	/* each breakpoint centred on the edge between two steps */
	.breaks {
		position: relative;
		width: calc(var(--steps) * var(--step));
		height: 14px;
	}
	.break {
		position: absolute;
		bottom: 0;
		transform: translateX(-50%);
		font-size: 12px;
		line-height: 1;
	}
	.chart {
		width: 100%;
	}
	svg {
		display: block;
		font-family: OpenSans, sans-serif;
		overflow: visible;
	}
	.grid {
		stroke: #ececec;
	}
	.tick,
	.col-sub {
		fill: var(--brandGray60);
		font-size: 11px;
	}
	.axis-label {
		fill: var(--brandGray70);
		font-size: 12px;
	}
	.col-label {
		fill: var(--brandGray80);
		font-size: 12px;
	}
	.seg-label {
		fill: var(--brandGray90);
		font-size: 11px;
		pointer-events: none;
	}
	.seg-label.light {
		fill: #fff;
	}
	.seg-label.bold {
		font-family: OpenSansBold, sans-serif;
	}
	@media (max-width: 520px) {
		.col-label {
			font-size: 10px;
		}
		.tick,
		.col-sub,
		.seg-label {
			font-size: 9.5px;
		}
	}
</style>
