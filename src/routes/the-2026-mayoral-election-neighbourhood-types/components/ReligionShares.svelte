<script>
	// Chow's and Bradford's 2026 vote share in tracts where more than 20% of residents are of one group
	// (group: 'Jewish' or 'Muslim'), against all other tracts: one 100% bar per set of tracts (Chow,
	// Bradford, all other candidates), in the style of the local-landslides page's municipality bars.
	// Data: ../data/group_vote_shares.json (../data/prep_group_vote_shares.py); the correlations are in the note.
	import FigureTitle from './FigureTitle.svelte';
	import { religionShareRows, groupThreshold, religionRows } from './data.js';
	import { HERO_RAMPS } from './config.js';

	// the candidates' darkest map colours, so the white labels read
	let { group } = $props();

	const CHOW = HERO_RAMPS.chow.at(-1);
	const BRADFORD = HERO_RAMPS.bradford.at(-1);
	const OTHERS = '#c9c9c9';

	const g = religionShareRows.find((x) => x.group === group);
	const rows = [
		{ key: 'over', label: `More than ${groupThreshold}% ${group}`, ...g.over },
		{ key: 'other', label: 'All other tracts', ...g.other }
	];
	const segments = (r) => [
		{ key: 'chow', v: r.chow, fill: CHOW },
		{ key: 'bradford', v: r.bradford, fill: BRADFORD },
		{ key: 'others', v: 100 - r.chow - r.bradford, fill: OTHERS }
	];
	const r = (cand) => religionRows.find((x) => x.group === group).values[cand === 'chow' ? 0 : 1].toFixed(2).replace('-', '−');
</script>

<figure>
	<FigureTitle>Chow's and Bradford's vote share in neighbourhoods with more <u>{group}</u> residents</FigureTitle>

	<div class="legend">
		<span class="item"><span class="swatch" style:background={CHOW}></span>Chow</span>
		<span class="item"><span class="swatch" style:background={BRADFORD}></span>Bradford</span>
		<span class="item"><span class="swatch" style:background={OTHERS}></span>All others</span>
	</div>

	<div class="block">
		{#each rows as row (row.key)}
				<div class="row" class:muted={row.key === 'other'}>
					<span class="label">{row.label}<span class="count">{row.tracts} tracts</span></span>
					<span class="bar">
						{#each segments(row) as s (s.key)}
							<span class="seg" style:width="{s.v}%" style:background={s.fill}>
								{#if s.key !== 'others'}{Math.round(s.v)}%{/if}
							</span>
						{/each}
					</span>
				</div>
		{/each}
	</div>

	<figcaption class="note">
		Share of election-day votes in the census tracts where more than {groupThreshold}% of residents are {group} (2021 census) and in all
		other tracts. Across all tracts, the correlation with the {group} share of residents is {r('chow')} for Chow and {r('bradford')} for
		Bradford. Advance and mail-in votes are excluded. These describe places, not how any group voted.
	</figcaption>
</figure>

<style>
	figure {
		margin: 0;
		font-family: OpenSans, sans-serif;
	}
	.legend {
		display: flex;
		justify-content: center;
		gap: 6px 18px;
		margin: 0 0 12px;
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
	/* label | bar */
	.row {
		display: grid;
		grid-template-columns: 160px minmax(0, 1fr);
		align-items: center;
		gap: 10px;
		margin-bottom: 3px;
	}
	.label {
		display: flex;
		flex-direction: column;
		font-size: 13px;
		line-height: 1.2;
		color: var(--brandGray90);
		text-align: right;
	}
	.count {
		font-size: 11px;
		color: var(--brandGray60);
	}
	.bar {
		display: flex;
		height: 26px;
	}
	.seg {
		display: flex;
		align-items: center;
		justify-content: center;
		font-family: OpenSansBold, sans-serif;
		font-size: 12px;
		color: #fff;
		border-right: 1px solid #fff;
		overflow: hidden;
	}
	.seg:last-child {
		border-right: none;
	}
	/* the comparison rows, all other tracts, in lighter bars */
	.row.muted .bar {
		opacity: 0.6;
	}
	.note {
		max-width: 694px;
		margin: 14px auto 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
	@media (max-width: 520px) {
		.row {
			grid-template-columns: 112px minmax(0, 1fr);
		}
		.label {
			font-size: 12px;
		}
	}
</style>
