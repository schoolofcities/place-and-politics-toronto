<script>
	// Small multiples: how strongly five neighbourhood measures went with each winning candidate's
	// vote share, mayoral elections 1997 to 2026 (absolute correlation, so a dot's height is
	// strength, not direction). Panels are stacked on one shared axis, the elections evenly spaced (not by
	// year), with a dot at each, a dashed line joining the dots and a faint fill under it. Each election's winner is named under its year on every panel,
	// at a 45° angle on narrow screens, where the names would run into each other side by side.
	// Data: ../data/winner_correlations.json (analysis/election_2026/03_neighbourhood_types_page_data.ipynb, Section 6).
	import { scaleLinear, scalePoint } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { winnerCorrelations } from './data.js';

	const { elections, variables } = winnerCorrelations;
	const years = elections.map((e) => e.year);

	let width = $state(560);
	const small = $derived(width < 420);
	const LEFT = 30; // room for the correlation labels on each panel
	const RIGHT = 8;
	const NAMES_H = 4; // space above the first panel
	const TITLE_H = 26; // a panel's title, and the space under it
	const PLOT_H = 62;
	const angled = $derived(width < 540); // too narrow for the winners' names side by side
	const AXIS_LAB = $derived(angled ? 64 : 33); // the years under each panel, and each election's winner under its year (angled: more room)
	const GAP = $derived(angled ? 8 : 22); // between the panels (the angled names already leave room)
	const BLOCK = $derived(TITLE_H + PLOT_H + AXIS_LAB + GAP);
	const height = $derived(NAMES_H + variables.length * BLOCK - GAP);

	// the elections evenly spaced, with room at each end for the first and last labels
	const x = $derived(scalePoint().domain(years).range([LEFT, width - RIGHT]).padding(0.5));
	const y = scaleLinear().domain([0, 1]).range([PLOT_H, 0]);

	// the dashed line through the dots, and the fill between it and 0
	const line = (v) => v.rows.map((r, i) => `${i ? 'L' : 'M'}${x(r.year).toFixed(1)},${y(r.abs).toFixed(1)}`).join('');
	const area = (v) => `${line(v)}L${x(v.rows.at(-1).year).toFixed(1)},${y(0)}L${x(v.rows[0].year).toFixed(1)},${y(0)}Z`;

	const GRID = [0, 0.5, 1];
	const gridText = (g) => (g === 0 ? '0' : g === 1 ? '1.0' : '0.5');

	// the dot under the pointer, and where to show its value
	let hovered = $state(null);
	const winnerOf = Object.fromEntries(elections.map((e) => [e.year, e.winner]));
	const signed = (r) => `${r < 0 ? '−' : ''}${Math.abs(r).toFixed(2)}`;

	const summary = variables
		.map((v) => `${v.label}: ` + v.rows.map((r) => `${r.year} ${r.abs.toFixed(2)}`).join(', '))
		.join('. ');
</script>

<figure>
	<FigureTitle title="Absolute correlations between neighbourhood traits and the winner's vote, 1997–2026" />

	<div class="chart" bind:clientWidth={width}>
		<svg {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Five small charts of the absolute correlation between a neighbourhood measure and the winning candidate's vote share in each mayoral election from 1997 to 2026, the elections evenly spaced. {summary}.">
			{#each variables as v, i (v.key)}
				{@const top = NAMES_H + i * BLOCK}
				{@const py = top + TITLE_H}
				<text class="row-title" x="0" y={top + 12}>{v.label}</text>

				<!-- horizontal guides, within the panel only -->
				{#each GRID as g (g)}
					<line class="grid" class:base={g === 0} x1={LEFT} x2={width - RIGHT} y1={py + y(g)} y2={py + y(g)} />
					<text class="tick" x={LEFT - 6} y={py + y(g)} dy="0.35em">{gridText(g)}</text>
				{/each}

				<g transform="translate(0,{py})">
					<!-- a faint fill under the dashed line joining the elections, then a dot per election -->
					<path class="area" d={area(v)} />
					<path class="link" d={line(v)} />
					{#each v.rows as r (r.year)}
						<circle class="pt" class:on={hovered?.key === v.key && hovered?.year === r.year} cx={x(r.year)} cy={y(r.abs)} r="4.1" />
						<!-- a wider, invisible target, so the dot is easy to hover -->
						<circle
							class="hit"
							cx={x(r.year)}
							cy={y(r.abs)}
							r="11"
							role="presentation"
							onpointerenter={() => (hovered = { key: v.key, label: v.label, year: r.year, r: r.r, abs: r.abs, cx: x(r.year), cy: py + y(r.abs) })}
							onpointerleave={() => (hovered = null)}
						/>
					{/each}
				</g>

				<!-- the years under every panel, each with its election's winner under it -->
				{#each elections as e (e.year)}
					<text class="tick year" x={x(e.year)} y={py + PLOT_H + 15} style:font-size={small ? '10px' : null}>{small ? `’${String(e.year).slice(2)}` : e.year}</text>
					{#if angled}
						<!-- angled up to the right, ending at its year: neighbouring names run parallel and clear each other -->
						{@const wx = x(e.year)}
						{@const wy = py + PLOT_H + 26}
						<text class="winner angled" x={wx} y={wy} transform="rotate(-45 {wx} {wy})">{e.winner}</text>
					{:else}
						<text class="winner" x={x(e.year)} y={py + PLOT_H + 28}>{e.winner}</text>
					{/if}
				{/each}
			{/each}
		</svg>

		{#if hovered}
			<div class="tip" style:left="{Math.min(Math.max(hovered.cx, 80), width - 80)}px" style:top="{hovered.cy - 12}px">
				<b>{hovered.year}, {winnerOf[hovered.year]}</b><br />
				{hovered.label}: {hovered.abs.toFixed(2)}<br />
				<span class="dir">{hovered.r < 0 ? 'Negative' : 'Positive'} (r = {signed(hovered.r)})</span>
			</div>
		{/if}
	</div>

	<figcaption class="note">
		Absolute Pearson correlations across census tracts, unweighted, between the winner's share of election-day votes and each
		measure, using the census nearest each election. They show strength, not direction. Apart from Tory in 2014 (negative for
		car commuting and distance), four measures are positive for the conservative mayors and negative for Miller and Chow; the share
		of households that rent runs the other way. Tracts, not voters.
	</figcaption>
</figure>

<style>
	/* as wide as the paragraphs (the page's .graphic wrapper sets that width) */
	figure {
		margin: 0;
	}
	/* positioned, for the hover label */
	.chart {
		position: relative;
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
		font-family: OpenSans, sans-serif;
		font-size: 10px;
		fill: var(--brandGray80);
		text-anchor: middle;
	}
	/* angled names end at their year */
	.winner.angled {
		text-anchor: end;
	}
	.row-title {
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		fill: var(--brandGray90);
	}
	/* horizontal guides in light grey, the 0 line darker */
	.grid {
		stroke: #e6e6e6;
		stroke-width: 1;
	}
	.grid.base {
		stroke: var(--brandGray60);
	}
	.tick {
		font-size: 11px;
		fill: var(--brandGray60);
		text-anchor: end;
	}
	.tick.year {
		font-size: 10px;
		text-anchor: middle;
	}
	.hit {
		fill: transparent;
		cursor: default;
	}
	.pt.on {
		stroke: var(--brandGray90);
		stroke-width: 1.5;
	}
	/* the value of the dot under the pointer, above it */
	.tip {
		position: absolute;
		transform: translate(-50%, -100%);
		pointer-events: none;
		background: #fff;
		border: 1px solid #8a8a8a;
		padding: 6px 9px;
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		line-height: 1.45;
		color: var(--brandGray90);
		white-space: nowrap;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
		z-index: 2;
	}
	.tip b {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}
	.tip .dir {
		color: var(--brandGray60);
	}
	.pt {
		fill: var(--brandDarkBlue);
		stroke: var(--brandLightBlue);
		stroke-width: 1;
	}
	/* a faint fill under the dashed line joining the dots */
	.area {
		fill: var(--brandLightBlue);
		fill-opacity: 0.25;
	}
	.link {
		fill: none;
		stroke: var(--brandDarkBlue);
		stroke-width: 1;
		stroke-dasharray: 3 3;
	}
	.note {
		margin: 14px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
