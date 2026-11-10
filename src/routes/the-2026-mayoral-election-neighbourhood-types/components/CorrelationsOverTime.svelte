<script>
	// Small multiples: how strongly five neighbourhood measures went with each winning candidate's
	// vote share, mayoral elections 1997 to 2026 (absolute correlation, so a line's height is
	// strength, not direction). Panels are stacked on one shared time axis, so the line moves
	// by years, not by election; the background tint marks conservative and progressive mayors,
	// each from the year they were elected to the year the next was (Miller's and Chow's are the progressive ones). Styled like the page's strip plots.
	// Data: ../data/winner_correlations.json (analysis/election_2026/03_neighbourhood_types_page_data.ipynb, Section 6).
	import { scaleLinear } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { winnerCorrelations } from './data.js';
	import { CHOW } from './config.js';

	const { elections, variables } = winnerCorrelations;
	const years = elections.map((e) => e.year);

	const LINE = '#333';
	const PROGRESSIVE = CHOW; // tinted at low opacity
	const CONSERVATIVE = '#7d8fa3'; // tinted at low opacity

	let width = $state(560);
	const small = $derived(width < 420);
	const LEFT = 30; // room for the correlation labels on the first panel
	const RIGHT = 8;
	const NAMES_H = 32; // mayors' names above the first panel
	const TITLE_H = 26; // a panel's title, and the space under it
	const PLOT_H = 68;
	const GAP = 12;
	const BLOCK = TITLE_H + PLOT_H + GAP;
	const AXIS_H = 38;
	const height = NAMES_H + variables.length * BLOCK - GAP + AXIS_H;

	const X0 = 1997;
	const X1 = 2027;
	const x = $derived(scaleLinear().domain([X0, X1]).range([LEFT, width - RIGHT]));
	const y = scaleLinear().domain([0, 1]).range([PLOT_H, 0]);

	// each mayor's span of the axis: from the year they were first elected to the year the next mayor was
	const winners = [];
	elections.forEach((e) => {
		const last = winners[winners.length - 1];
		if (!last || last.name !== e.winner) winners.push({ name: e.winner, side: e.side, start: e.year, end: X1 });
	});
	winners.forEach((w, i) => {
		if (i > 0) winners[i - 1].end = w.start;
	});

	const path = $derived((v) =>
		v.rows.map((r, i) => `${i ? 'L' : 'M'}${x(r.year).toFixed(1)},${y(r.abs).toFixed(1)}`).join('')
	);
	const GRID = [0, 0.5, 1];
	const gridText = (g) => (g === 0 ? '0' : g === 1 ? '1.0' : '0.5');
	// 2022 and 2023 are a year apart, so 2022's label drops to a second line
	const lowered = new Set([2022]);

	const summary = variables
		.map((v) => `${v.label}: ` + v.rows.map((r) => `${r.year} ${r.abs.toFixed(2)}`).join(', '))
		.join('. ');
</script>

<figure>
	<FigureTitle title="Absolute correlations between neighbourhood traits and the winner's vote, 1997–2026" />

	<div class="legend">
		<span class="item"><span class="swatch" style:background={CONSERVATIVE} style:opacity="0.22"></span>Conservative mayor</span>
		<span class="item"><span class="swatch" style:background={PROGRESSIVE} style:opacity="0.3"></span>Progressive mayor</span>
	</div>

	<div class="chart" bind:clientWidth={width}>
		<svg {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Five small line charts of the absolute correlation between a neighbourhood measure and the winning candidate's vote share in each mayoral election from 1997 to 2026. {summary}.">
			<!-- the mayors, named above the first panel, centred on their years in office -->
			{#each winners as w (w.start)}
				<text class="winner" x={(x(w.start) + x(w.end)) / 2} y={NAMES_H - 7}>{w.name}</text>
			{/each}

			{#each variables as v, i (v.key)}
				{@const top = NAMES_H + i * BLOCK}
				{@const py = top + TITLE_H}
				<text class="row-title" x="0" y={top + 12}>{v.label}</text>

				<!-- tint behind the panel: conservative or progressive winner -->
				{#each winners as w (w.start)}
					<rect x={x(w.start)} y={py} width={x(w.end) - x(w.start)} height={PLOT_H} fill={w.side === 'Progressive' ? PROGRESSIVE : CONSERVATIVE} fill-opacity={w.side === 'Progressive' ? 0.22 : 0.13} />
				{/each}

				<!-- horizontal guides, and vertical markers at each election, within the panel only -->
				{#each GRID as g (g)}
					<line class="grid" class:base={g === 0} x1={LEFT} x2={width - RIGHT} y1={py + y(g)} y2={py + y(g)} />
					{#if i === 0}<text class="tick" x={LEFT - 6} y={py + y(g)} dy="0.35em">{gridText(g)}</text>{/if}
				{/each}
				{#each years as yr (yr)}
					<line class="mark" x1={x(yr)} x2={x(yr)} y1={py} y2={py + PLOT_H} />
				{/each}

				<g transform="translate(0,{py})">
					<path class="series" d={path(v)} />
				</g>
			{/each}

			<!-- shared time axis under the last panel -->
			{#each years as yr (yr)}
				{@const ty = NAMES_H + variables.length * BLOCK - GAP + (lowered.has(yr) ? 24 : 12)}
				<text class="tick year" x={x(yr)} y={ty} style:font-size={small ? '10px' : null}>{yr}</text>
			{/each}
		</svg>
	</div>

	<figcaption class="note">
		Absolute Pearson correlations across census tracts, unweighted, between the winner's share of election-day votes and each measure, using the census nearest each election. They show
		strength, not direction. Except for Tory in 2014 (negative for auto commuting and distance), all five measures are positive for the conservative mayors and negative for Miller and Chow.
		Tracts, not voters.
	</figcaption>
</figure>

<style>
	figure {
		max-width: 560px;
		margin: 0 auto;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px 18px;
		margin: 0 0 8px;
		font-family: OpenSans, sans-serif;
		font-size: 12px;
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
	.chart {
		width: 100%;
	}
	svg {
		display: block;
		max-width: 100%;
		height: auto;
		overflow: visible;
		font-family: OpenSans, sans-serif;
	}
	.winner {
		font-family: OpenSansBold, sans-serif;
		font-size: 11px;
		fill: var(--brandGray80);
		text-anchor: middle;
	}
	.row-title {
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		fill: var(--brandGray90);
	}
	.grid {
		stroke: #dcdcdc;
		stroke-width: 1;
	}
	.grid.base {
		stroke: var(--brandGray60);
	}
	.mark {
		stroke: #fff;
		stroke-opacity: 0.7;
		stroke-width: 1;
	}
	.tick {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: end;
	}
	.tick.year {
		text-anchor: middle;
	}
	.series {
		fill: none;
		stroke: #333;
		stroke-width: 2;
		stroke-linejoin: round;
		stroke-linecap: round;
	}
	.note {
		margin: 12px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
