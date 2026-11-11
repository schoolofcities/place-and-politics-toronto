<script>
	// Chow's vote share in tracts where more than 20% of residents are Chinese, against all other tracts,
	// within Old Toronto and within the suburbs, in 2014, 2023 and 2026: a pair of dots per row on one scale,
	// green for all other tracts and red for the more Chinese ones, so each row's gap is the difference.
	// Data: ../data/group_vote_shares.json (../data/prep_group_vote_shares.py); the correlations are in the note.
	import FigureTitle from './FigureTitle.svelte';
	import { chineseShareRows, groupThreshold, chineseYears, chineseRows } from './data.js';

	const OVER = 'var(--brandRed)'; // tracts over the threshold
	const OTHER = 'var(--brandMedGreen)'; // all other tracts
	const MAX = 80; // the scale, 0 to 80%

	const years = [...new Set(chineseShareRows.map((r) => r.year))];
	const pos = (v) => `${(v / MAX) * 100}%`;
	const fmtR = (area, year) => chineseRows.find((r) => r.area === area).values[chineseYears.indexOf(year)].toFixed(2);
</script>

<figure>
	<FigureTitle title="Chow's vote share in neighbourhoods with more Chinese residents" />

	<div class="legend">
		<span class="item"><span class="dot" style:background={OVER}></span>More than {groupThreshold}% Chinese</span>
		<span class="item"><span class="dot" style:background={OTHER}></span>All other tracts</span>
	</div>

	{#each years as y (y)}
		<div class="block">
			<p class="year">{y}</p>
			{#each chineseShareRows.filter((r) => r.year === y) as row (row.area)}
				{@const lo = Math.min(row.over.chow, row.other.chow)}
				{@const hi = Math.max(row.over.chow, row.other.chow)}
				{@const overHigher = row.over.chow >= row.other.chow}
				<div class="row">
					<span class="label">{row.area}</span>
					<span class="track">
						<span class="link" style:left={pos(lo)} style:width="{((hi - lo) / MAX) * 100}%"></span>
						<span class="pt" style:left={pos(row.other.chow)} style:background={OTHER}></span>
						<span class="pt" style:left={pos(row.over.chow)} style:background={OVER}></span>
						<!-- each value beside its dot, on the outer side, whichever is higher -->
						<span class="val other" class:before={overHigher} style:left={pos(row.other.chow)}>{Math.round(row.other.chow)}%</span>
						<span class="val over" class:before={!overHigher} style:left={pos(row.over.chow)}>{Math.round(row.over.chow)}%</span>
					</span>
				</div>
			{/each}
		</div>
	{/each}

	<figcaption class="note">
		Chow's share of election-day votes in the census tracts where more than {groupThreshold}% of residents are Chinese (visible
		minority, 2021 census) and in all other tracts, in Old Toronto and in the suburbs (everywhere outside the former City of
		Toronto). Only {chineseShareRows.find((r) => r.area === 'Old Toronto').over.tracts} Old Toronto tracts are over {groupThreshold}% Chinese. The correlations with the Chinese share of
		residents in 2014, 2023 and 2026 are {years.map((y) => fmtR('Old Toronto', y)).join(', ')} in Old Toronto and {years.map((y) => fmtR('Suburbs', y)).join(', ')} in the
		suburbs. Advance and mail-in votes are excluded. These describe places, not how any group voted.
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
		margin: 0 0 8px;
		font-size: 13px;
		color: var(--brandGray80);
	}
	.item {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.dot {
		width: 11px;
		height: 11px;
		border-radius: 50%;
		display: inline-block;
	}
	.block {
		margin-top: 8px;
	}
	.year {
		margin: 0 0 2px;
		font-family: OpenSansBold, sans-serif;
		font-size: 13px;
		color: var(--brandGray90);
	}
	/* label | the scale, 0 to 80% */
	.row {
		display: grid;
		grid-template-columns: 96px minmax(0, 1fr);
		align-items: center;
		gap: 10px;
		height: 30px;
	}
	.label {
		font-size: 13px;
		color: var(--brandGray80);
		text-align: right;
	}
	.track {
		position: relative;
		height: 100%;
		border-left: 1px solid var(--brandGray);
	}
	.track::before {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		top: 50%;
		border-top: 1px solid #ececec;
	}
	.link {
		position: absolute;
		top: 50%;
		border-top: 2px solid var(--brandGray);
		transform: translateY(-50%);
	}
	.pt {
		position: absolute;
		top: 50%;
		width: 11px;
		height: 11px;
		border-radius: 50%;
		transform: translate(-50%, -50%);
	}
	/* the values, each beside its dot, on the outer side */
	.val {
		position: absolute;
		top: 50%;
		font-size: 12px;
		line-height: 1;
		transform: translateY(-50%);
		white-space: nowrap;
		margin-left: 10px;
	}
	.val.before {
		margin-left: -10px;
		translate: -100% 0;
	}
	.val.other {
		color: var(--brandGray60);
	}
	.val.over {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandGray90);
	}
	.note {
		max-width: 694px;
		margin: 14px auto 0;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
