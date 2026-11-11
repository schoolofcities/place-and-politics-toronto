<script>
	// The ten neighbourhood characteristics most strongly correlated with each candidate's 2026
	// vote share, as two ranked lists side by side, in the style of the turnout post's "ranked by
	// their association with turnout" chart: rank, name, a dot on a small inline scale and the value.
	// A dot rather than a bar, since a correlation is a position on a scale, not an amount. Both lists
	// share one scale, so the dots compare across them. Stacks into one column on phones.
	// Data: ../data/correlations_top.json, built by analysis/election_2026/03_neighbourhood_types_page_data.ipynb
	// from Zack Taylor's correlates_2026.csv (data/tor_elections_2023_2026).
	import FigureTitle from './FigureTitle.svelte';
	import { correlationLists, correlationMeta } from './data.js';

	// one scale for both lists: a correlation's whole positive range, 0 (no relationship) to 1 (a perfect one)
	const maxR = 1;
	const fmt = (r) => r.toFixed(2);
</script>

<figure class="ranked">
	<FigureTitle
		title="Neighbourhood characteristics most correlated with each candidate's vote"
		subtitle="Top ten correlations across census tracts with 2026 election-day vote share"
	/>

	<div class="lists">
		{#each correlationLists as list (list.key)}
			<section class="list" aria-labelledby="corr-{list.key}">
				<h4 class="list-head" id="corr-{list.key}" style:color={list.text}>Correlation with {list.name}'s vote share</h4>
				<ol>
					{#each list.rows as d, i (d.id)}
						<li>
							<span class="rank">{i + 1}</span>
							<span class="name">{d.label}</span>
							<span class="dot-cell" aria-hidden="true">
								<span class="stem" style:width="{(d.r / maxR) * 100}%" style:border-color={list.colour}></span>
								<span class="dot" style:left="{(d.r / maxR) * 100}%" style:background={list.colour}></span>
							</span>
							<span class="val">{fmt(d.r)}</span>
						</li>
					{/each}
				</ol>
			</section>
		{/each}
	</div>

	<figcaption class="note">
		Each number is a correlation across the city's {correlationMeta.tracts} census tracts, not a share of the vote: 1 means a
		characteristic rises and falls exactly with the candidate's vote share, and 0 means no relationship. Both lists share one
		scale, from 0 at the left of each line to 1 at the right. Shown are the ten highest of {correlationMeta.pool} characteristics
		(2021 census variables and distance from City Hall). Tracts count equally, whatever their size. Vote share is the share of
		valid election-day votes; advance and mail-in votes are not included. These are associations between places, not evidence
		about how any group of people voted.
	</figcaption>
</figure>

<style>
	.ranked {
		margin: 0;
		font-family: OpenSans, sans-serif;
		color: var(--brandGray90);
	}

	.lists {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 28px;
		margin: 18px 0 0; /* room below the chart's title */
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
	/* rank | name and what it is measured as | dot on its scale | value */
	li {
		display: grid;
		grid-template-columns: 16px minmax(0, 1fr) 90px 34px;
		align-items: center;
		gap: 8px;
		padding: 4px 0;
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
	/* a thin guide line for the scale (0 at the left), and the dot on it */
	.dot-cell {
		position: relative;
		display: block;
		height: 10px;
		margin: 0 5px; /* so a dot at either end stays inside the cell */
	}
	.dot-cell::before {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		top: 50%;
		border-top: 1px solid #dcdcdc;
	}
	/* the line from 0 up to the dot, in the candidate's colour, over the grey */
	.stem {
		position: absolute;
		left: 0;
		top: 50%;
		border-top: 1px solid;
		transform: translateY(-50%);
	}
	.dot {
		position: absolute;
		top: 50%;
		width: 9px;
		height: 9px;
		border-radius: 50%;
		transform: translate(-50%, -50%);
	}
	.val {
		text-align: right;
		font-variant-numeric: tabular-nums;
		color: var(--brandGray70);
	}

	.note {
		margin: 14px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}

	/* phones: the two lists one above the other */
	@media (max-width: 600px) {
		.lists {
			grid-template-columns: minmax(0, 1fr);
			gap: 22px;
		}
	}
</style>
