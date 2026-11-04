<script>
	// The where-the-votes-came-from data as one stacked bar per progressive candidate: their
	// election-day votes in the former City of Toronto, then in the suburbs, both as shares of all
	// election-day votes (plot_core_suburb_shares.R), so the bar's length is their whole
	// election-day share. The former City of Toronto comes first, from zero, then the suburbs.
	import { scaleLinear } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { coreSuburbColumns, WIN_YEARS, CITYWIDE_SHARE } from './data.js';
	import { PART_COLOURS } from './config.js';

	// the suburbs, the part that decides the race, in the darker blue; the former City of Toronto in the lighter
	const CORE = PART_COLOURS.Suburbs;
	const SUBURBS = PART_COLOURS['City of Toronto'];

	const rows = coreSuburbColumns.map((c) => {
		const core = c.segments.find((s) => s.key === 'City of Toronto').value;
		const suburbs = c.segments.find((s) => s.key === 'Suburbs').value;
		return { key: c.key, name: c.label, year: c.sublabel, won: WIN_YEARS.includes(c.key), citywide: CITYWIDE_SHARE[c.key], core, suburbs };
	});

	let width = $state(694);
	const small = $derived(width < 520);
	// labels as on the back-to-back chart: name and year, then the result from RESULT_X
	const RESULT_X = $derived(small ? 108 : 132);
	const NAME_W = $derived(RESULT_X + (small ? 80 : 92));
	const ROW = 37; // bar plus 15px between rows
	const BAR = 22;
	const height = rows.length * ROW;
	const x = $derived(scaleLinear().domain([0, 0.6]).range([NAME_W, width - 12]));
	const TICKS = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6];

	const pct = (v) => `${Math.round(100 * v)}%`;
</script>

<figure>
	<FigureTitle title="Where each progressive candidate's votes came from" />

	<div class="legend">
		<span class="item"><span class="swatch" style:background={CORE}></span>Former City of Toronto</span>
		<span class="item"><span class="swatch" style:background={SUBURBS}></span>Suburbs</span>
	</div>

	<div class="chart" bind:clientWidth={width}>
		<svg {width} height={height + 16} role="img" aria-label="Each progressive candidate's election-day votes in the suburbs and in the former City of Toronto">
			<!-- a light gridline and label every 10%, behind the bars -->
			{#each TICKS as t (t)}
				<line class="grid" x1={x(t)} x2={x(t)} y1="0" y2={height} />
				<text class="tick" x={x(t)} y={height + 12}>{pct(t)}</text>
			{/each}
			{#each rows as r, i (r.key)}
				<g transform="translate(0,{i * ROW})">
					<text class="name" class:won={r.won} x="0" y={ROW / 2} dy="0.35em"><tspan class="last">{r.name}</tspan> {r.year}</text>
					<line class="divider" x1={RESULT_X - 7} x2={RESULT_X - 7} y1={(ROW - 14) / 2} y2={(ROW + 14) / 2} />
					<g class="ballot" class:won={r.won} transform="translate({RESULT_X},{(ROW - 12) / 2}) scale(1.1)">
						<rect x="0.5" y="0.5" width="10" height="10" />
						{#if r.won}
							<path d="M2.6 5.8 L4.7 7.9 L8.8 3.4" />
						{:else}
							<path d="M3.1 3.1 L7.9 7.9 M7.9 3.1 L3.1 7.9" />
						{/if}
					</g>
					<text class="result" class:won={r.won} x={RESULT_X + 17} y={ROW / 2} dy="0.35em">{r.won ? 'Won' : 'Lost'} <tspan class="citywide">{pct(r.citywide)}</tspan></text>

					<!-- the former City of Toronto from zero, then the suburbs -->
					<rect x={x(0)} y={(ROW - BAR) / 2} width={x(r.core) - x(0)} height={BAR} fill={CORE} />
					<rect x={x(r.core)} y={(ROW - BAR) / 2} width={x(r.core + r.suburbs) - x(r.core)} height={BAR} fill={SUBURBS} />
					<!-- a 1px white line where the core ends and the suburbs begin -->
					<line class="split" x1={x(r.core)} x2={x(r.core)} y1={(ROW - BAR) / 2} y2={(ROW + BAR) / 2} />
					{#if x(r.core) - x(0) >= 28}
						<text class="val" x={(x(0) + x(r.core)) / 2} y={ROW / 2} dy="0.35em">{pct(r.core)}</text>
					{/if}
					{#if x(r.core + r.suburbs) - x(r.core) >= 28}
						<text class="val" x={(x(r.core) + x(r.core + r.suburbs)) / 2} y={ROW / 2} dy="0.35em">{pct(r.suburbs)}</text>
					{/if}
				</g>
			{/each}
		</svg>
	</div>

	<figcaption class="note">
		Suburbs are everywhere outside the former City of Toronto: East York, Etobicoke, North York, Scarborough and York.
		Bars only include votes cast on election day, as shares of all election-day votes. The share after each result is
		the candidate's official citywide result.
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
	/* names and years: black for a winner, a step lighter for a loser */
	.name {
		font-size: 14px;
		fill: var(--brandGray70);
	}
	.name.won {
		fill: var(--brandBlack);
	}
	.last {
		font-family: OpenSansItalic, sans-serif;
	}
	.divider {
		stroke: var(--brandGray);
		stroke-width: 1;
	}
	.ballot rect {
		fill: #fff;
		stroke: var(--brandGray60);
		stroke-width: 1;
	}
	.ballot path {
		fill: none;
		stroke: var(--brandGray60);
		stroke-width: 1.6;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.ballot.won rect,
	.ballot.won path {
		stroke: var(--brandGray90);
	}
	.result {
		font-size: 13px;
		fill: var(--brandGray60);
	}
	.result.won {
		font-family: OpenSansBold, sans-serif;
		fill: var(--brandGray90);
	}
	.citywide {
		font-family: OpenSans, sans-serif;
	}
	.val {
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		fill: #fff;
		text-anchor: middle;
		pointer-events: none;
	}
	.grid {
		stroke: #e6e6e6;
		stroke-width: 1;
	}
	.split {
		stroke: #fff;
		stroke-width: 1;
	}
	.tick {
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
			font-size: 12px;
		}
		.result {
			font-size: 11px;
		}
		.val {
			font-size: 10px;
		}
	}
</style>
