<script>
	// The page's dot-and-interval chart, shared by the graphics that compare correlations: one
	// block per election, each with a row per series. A row is a solid square (the correlation)
	// on a fainter bar (its 95% confidence interval); the block is labelled in the left
	// margin (a year, or a group name), centred on its rows, and a legend of coloured markers names the series. Panels
	// (e.g. one per religion) stack under optional headings and share one axis. Everything about
	// how these charts look lives here, so they stay identical.
	//
	// Props: title; legend [{ key, label, colour }]; panels [{ heading?, blocks: [{ label, rows:
	// [{ key, r, low, high }] }] }]; children = the note under the chart.
	import { scaleLinear } from 'd3';
	import FigureTitle from './FigureTitle.svelte';

	let { title, legend, panels, children } = $props();

	const colour = Object.fromEntries(legend.map((l) => [l.key, l.colour]));

	let width = $state(520);
	const small = $derived(width < 420);
	// the block labels (years, or group names), left of the plot: wide enough for the longest
	const longest = Math.max(...panels.flatMap((p) => p.blocks.map((b) => b.label.length)));
	const LABEL_W = $derived(Math.max(small ? 40 : 46, longest * 8 + 12));
	const RIGHT = 14;
	const ROW = 21;
	const GAP = 11; // between blocks
	const HEAD = 22; // a panel's heading
	const BAND = 11; // height of the interval bar
	const SQ = 10; // side of the square

	// vertical layout, the same at any width
	let cursor = 0;
	const laid = panels.map((p, pi) => {
		if (pi > 0) cursor += 18; // between panels
		const top = cursor;
		if (p.heading) cursor += HEAD;
		const blocks = p.blocks.map((b, bi) => {
			if (bi > 0) cursor += GAP;
			const y = cursor;
			cursor += b.rows.length * ROW;
			return { ...b, y, h: b.rows.length * ROW };
		});
		return { ...p, top, blocks };
	});
	const plotH = cursor;
	const height = plotH + 34; // tick labels and the axis title

	const rows = panels.flatMap((p) => p.blocks.flatMap((b) => b.rows));
	const lo = Math.min(0, Math.floor(Math.min(...rows.map((r) => r.low)) * 10) / 10);
	const hi = Math.ceil(Math.max(...rows.map((r) => r.high)) * 20) / 20; // up to the next 0.05
	const x = $derived(scaleLinear().domain([lo, hi]).range([LABEL_W, width - RIGHT]));
	const TICKS = [];
	for (let t = lo; t <= hi + 1e-9; t += 0.1) TICKS.push(Math.round(t * 10) / 10);

	const f2 = (v) => v.toFixed(2).replace('-0.00', '0.00');
	const tickText = (t) => (t === 0 ? '0' : t.toFixed(1).replace('-', '−'));
	const seriesName = Object.fromEntries(legend.map((l) => [l.key, l.label]));
	const summary = panels
		.map((p) => (p.heading ? `${p.heading}: ` : '') + p.blocks.map((b) => `${b.label}: ` + b.rows.map((r) => `${seriesName[r.key]} ${f2(r.r)} (${f2(r.low)} to ${f2(r.high)})`).join('; ')).join('. '))
		.join('. ');
</script>

<figure>
	<FigureTitle {title} />

	<div class="legend">
		{#each legend as l (l.key)}
			<span class="item"><span class="swatch" style:background={l.colour}></span>{l.label}</span>
		{/each}
	</div>

	<div class="chart" bind:clientWidth={width}>
		<svg {width} {height} role="img" aria-label="{title}, with 95% confidence intervals. {summary}">
			<!-- gridlines every 0.1, the zero line darker, behind the marks -->
			{#each TICKS as t (t)}
				<line class="grid" class:zero={t === 0} x1={x(t)} x2={x(t)} y1="0" y2={plotH} />
				<text class="tick" x={x(t)} y={plotH + 14}>{tickText(t)}</text>
			{/each}
			<text class="axis-title" x={(x(lo) + x(hi)) / 2} y={plotH + 30}>Correlation (r), with 95% confidence interval</text>

			{#each laid as p, pi (pi)}
				{#if p.heading}<text class="heading" x="0" y={p.top + 14}>{p.heading}</text>{/if}
				{#each p.blocks as b (b.label)}
					<text class="year" x={x(lo) - 8} y={b.y + b.h / 2} dy="0.35em">{b.label}</text>
					{#each b.rows as r, j (r.key)}
						{@const y = b.y + j * ROW + ROW / 2}
						<rect class="band" x={x(r.low)} y={y - BAND / 2} width={x(r.high) - x(r.low)} height={BAND} fill={colour[r.key]} />
						<rect x={x(r.r) - SQ / 2} y={y - SQ / 2} width={SQ} height={SQ} fill={colour[r.key]} />
					{/each}
				{/each}
			{/each}
		</svg>
	</div>

	<figcaption class="note">{@render children?.()}</figcaption>
</figure>

<style>
	/* as wide as the paragraphs (the page's .graphic wrapper sets that width) */
	figure {
		margin: 0;
	}
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
		flex: none;
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
		stroke: #e6e6e6;
		stroke-width: 1;
	}
	.grid.zero {
		stroke: var(--brandGray60);
	}
	.tick {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: middle;
	}
	.axis-title {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: middle;
	}
	.heading {
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		fill: var(--brandGray90);
	}
	.year {
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		fill: var(--brandGray90);
		text-anchor: end;
	}
	/* the interval, a fainter bar behind the square */
	.band {
		opacity: 0.33;
	}
	.note {
		margin: 14px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
