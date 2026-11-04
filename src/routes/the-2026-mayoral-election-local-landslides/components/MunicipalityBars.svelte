<script>
	// 2026 election-day vote share for Chow, Bradford and everyone else in each former
	// municipality (plot_shares_by_municipality.R), as one 100% horizontal bar each. Bars are
	// as tall as the votes cast there, so each segment's area is proportional to its votes, and
	// stacked almost touching, like a treemap. Names on the left, vote totals on the right.
	import { scaleLinear, max, sum } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { municipalityGroups, CANDIDATES } from './data.js';
	import { CHOW, BRADFORD, OTHERS } from './config.js';

	const colours = { Chow: CHOW, Bradford: BRADFORD, 'All others': OTHERS };

	const MAX_BAR = 115; // px, the former City of Toronto's bar on phones
	const GAP = 2; // px between bars
	const LABEL_SIZE = 12; // px, shrunk to fit the thinnest bars (East York's)

	let width = $state(694);
	const small = $derived(width < 520);
	const LABEL_W = $derived(small ? 84 : 98); // municipality names, as wide as "Scarborough"
	// the data's name -> the label, one line each (the former City of Toronto's on two)
	const NAMES = { 'City of Toronto': ['Former City', 'of Toronto'] };
	const lines = (key) => NAMES[key] ?? [key];
	const TOTAL_W = $derived(small ? 74 : 92); // vote totals, right of the bars
	const x = $derived(scaleLinear().domain([0, 1]).range([LABEL_W, width - TOTAL_W]));

	// bar heights, in px per vote: on wider screens the bars together (gaps included) are as tall
	// as they are wide, a square; on phones that would be too thin, so the tallest is MAX_BAR
	const maxTotal = max(municipalityGroups, (g) => g.total);
	const sumTotal = sum(municipalityGroups, (g) => g.total);
	const gaps = (municipalityGroups.length - 1) * GAP;
	const perVote = $derived(small ? MAX_BAR / maxTotal : (width - TOTAL_W - LABEL_W - gaps) / sumTotal);

	const rows = $derived.by(() => {
		let y = 0;
		return municipalityGroups.map((g) => {
			const h = perVote * g.total;
			let base = 0;
			const row = {
				key: g.key,
				total: g.total,
				y,
				h,
				size: Math.min(LABEL_SIZE, h - 2),
				segments: g.bars.map((b) => {
					const s = { ...b, x0: base, x1: base + b.value };
					base += b.value;
					return s;
				})
			};
			y += h + GAP;
			return row;
		});
	});
	const height = $derived(rows.at(-1).y + rows.at(-1).h);

	const pct = (v) => `${Math.round(100 * v)}%`;
</script>

<figure>
	<FigureTitle title="Votes by former municipality, 2026 Toronto mayoral election" />

	<div class="legend">
		{#each CANDIDATES as c (c)}
			<span class="item"><span class="swatch" style:background={colours[c]}></span>{c}</span>
		{/each}
	</div>

	<div class="chart" bind:clientWidth={width}>
		<svg {width} height={height + 16} role="img" aria-label="Vote share by former municipality">
			{#each rows as r (r.key)}
				<g transform="translate(0,{r.y})">
					<text class="name" x={LABEL_W - 8} y={r.h / 2}>
						{#each lines(r.key) as line, j (j)}
							<tspan x={LABEL_W - 8} dy={j === 0 ? `${0.35 - 0.6 * (lines(r.key).length - 1)}em` : '1.2em'}>{line}</tspan>
						{/each}
					</text>
					<text class="votes" x={width - TOTAL_W + 8} y={r.h / 2} dy="0.35em">{r.total.toLocaleString('en-CA')} votes</text>
					{#each r.segments as s (s.key)}
						{@const w = x(s.x1) - x(s.x0)}
						<rect x={x(s.x0)} width={Math.max(0, w)} height={r.h} fill={colours[s.key]} />
						<!-- labels for Chow and Bradford only; "all others" is left unlabelled -->
						{#if w >= 24 && s.key !== 'All others'}
							<text class="val" x={x(s.x0) + w / 2} y={r.h / 2} dy="0.35em" style:font-size="{r.size}px">{pct(s.value)}</text>
						{/if}
					{/each}
				</g>
			{/each}
			<!-- the 50% line: who has a majority -->
			<line class="half" x1={x(0.5)} x2={x(0.5)} y1="0" y2={height} />
			<text class="half-label" x={x(0.5)} y={height + 12}>50%</text>
		</svg>
	</div>

	<figcaption class="note">
		Advance and mail-in votes are not included because they are reported by ward. Each voting subdivision is assigned whole to the former municipality
		holding most of its area.
	</figcaption>
</figure>

<style>
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
	}
	/* as wide as the body text's paragraphs (.text's 694px content box) */
	.chart {
		width: 100%;
		max-width: 694px;
		margin: 0 auto;
	}
	svg {
		display: block;
		font-family: OpenSans, sans-serif;
		overflow: visible;
	}
	rect {
		stroke: #fff;
		stroke-width: 1;
	}
	.name {
		font-size: 13px;
		fill: var(--brandGray90);
		text-anchor: end;
	}
	.votes {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: start;
	}
	.val {
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		fill: #fff;
		text-anchor: middle;
		pointer-events: none;
	}
	.half {
		stroke: var(--brandGray90);
		stroke-width: 1;
		stroke-dasharray: 3 3;
	}
	.half-label {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: middle;
	}
	.note {
		max-width: 694px;
		margin: 14px auto 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
	@media (max-width: 520px) {
		.name {
			font-size: 11px;
		}
		.votes,
		.val {
			font-size: 10px;
		}
	}
</style>
