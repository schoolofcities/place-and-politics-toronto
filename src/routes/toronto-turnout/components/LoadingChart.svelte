<script>
	// What the first component is made of, as two ranked lists side by side: the 10
	// characteristics most strongly tied to its higher-turnout side and the 10 most strongly tied
	// to its lower-turnout side (largest positive and largest negative loadings on component 1,
	// from the VIP > 1 set in the data). Each row has a small inline bar and its value; both
	// lists share one scale, so bars compare across them. Stacks into one column on phones.
	//
	// Wording: a "loading" is how strongly a variable moves with the component 1 score, and that
	// score moves with turnout, so the chart calls it the strength of association with turnout.

	import FigureTitle from './FigureTitle.svelte';
	import { ingredientRows, meta } from '../data.js';
	import { COMPONENT_LOW_COLOUR, COMPONENT_HIGH_COLOUR } from '../config.js';
	import { fmtLoading, fmtPct } from '../format.js';

	const PER_SIDE = 10;
	const byLoading = [...ingredientRows].sort((a, b) => b.loading - a.loading);
	const highRows = byLoading.filter((d) => d.loading > 0).slice(0, PER_SIDE); // strongest first
	const lowRows = byLoading
		.filter((d) => d.loading < 0)
		.slice(-PER_SIDE)
		.reverse(); // strongest (most negative) first
	// one scale for both lists: the longest bar is the strongest loading on either side
	const maxAbs = Math.max(...[...highRows, ...lowRows].map((d) => Math.abs(d.loading)));

	const lists = [
		{ key: 'high', heading: 'Where turnout tends to be higher', color: COMPONENT_HIGH_COLOUR, rows: highRows },
		{ key: 'low', heading: 'Where turnout tends to be lower', color: COMPONENT_LOW_COLOUR, rows: lowRows }
	];

	const c1 = meta.component_1;
</script>

<figure class="loading-chart">
	<FigureTitle title="Neighbourhood characteristics ranked by their association with turnout" />

	<div class="lists">
		{#each lists as list (list.key)}
			<section class="list" aria-labelledby="loading-{list.key}">
				<h4 class="list-head" id="loading-{list.key}" style:color={list.color}>{list.heading}</h4>
				<ol>
					{#each list.rows as d, i (d.variable)}
						<li>
							<span class="rank">{i + 1}</span>
							<span class="name">{d.label}</span>
							<span class="bar-cell" aria-hidden="true">
								<span class="bar" style:width="{(Math.abs(d.loading) / maxAbs) * 100}%" style:background={list.color}></span>
							</span>
							<span class="val">{fmtLoading(d.loading)}</span>
						</li>
					{/each}
				</ol>
			</section>
		{/each}
	</div>

	<figcaption class="note">
		Each statistic shows how strongly a neighbourhood characteristic is tied to the main pattern behind Toronto's turnout differences (the map above), as a unitless score where 0 means no association; both lists share one scale. Shown are the {PER_SIDE} most strongly tied to each side from 70 characteristics that matter most to the Partial Least Squares model. For reference, tracts on the higher-turnout side of the pattern average {fmtPct(c1.mean_turnout_score_above_0)} turnout, and those on the lower side {fmtPct(c1.mean_turnout_score_below_0)}. These are associations between places, not evidence that any one characteristic changes whether people vote.
	</figcaption>
</figure>

<style>
	.loading-chart {
		margin: 0;
		font-family: OpenSans, sans-serif;
		color: var(--brandGray90);
	}

	.lists {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 28px;
		margin-top: 18px; /* room below the chart's title */
	}
	.list-head {
		margin: 0 0 6px;
		padding-bottom: 4px;
		border-bottom: 1px solid var(--brandGray);
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
		font-size: 13px;
		line-height: 1.3;
		text-align: center;
	}
	ol {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	/* rank | name | bar | value */
	li {
		display: grid;
		grid-template-columns: 16px minmax(0, 1fr) 70px 38px;
		align-items: center;
		gap: 8px;
		padding: 3px 0;
		border-bottom: 1px solid #f2f2f2;
		font-size: 12px;
		line-height: 1.3;
	}
	.rank {
		color: var(--brandGray60);
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
	.name {
		color: var(--brandGray90);
	}
	.bar-cell {
		display: block;
		height: 8px;
		background: #f2f2f2;
	}
	.bar {
		display: block;
		height: 100%;
	}
	.val {
		text-align: right;
		font-variant-numeric: tabular-nums;
		color: var(--brandGray70);
	}

	.note {
		margin: 20px 0 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}

	/* phones: the two lists one above the other */
	@media (max-width: 600px) {
		.lists {
			grid-template-columns: minmax(0, 1fr);
			gap: 18px;
		}
	}
</style>
