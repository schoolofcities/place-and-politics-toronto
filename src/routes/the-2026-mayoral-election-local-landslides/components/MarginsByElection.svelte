<script>
	// Share of polls in each election by the winner's margin over the runner-up
	// (plot_margins_by_election.R).
	import FigureTitle from './FigureTitle.svelte';
	import StackedBars from './StackedBars.svelte';
	import { marginColumns } from './data.js';
	import { BAND_COLOURS } from './config.js';
</script>

<figure>
	<FigureTitle title="Polls by winning margin, Toronto mayoral elections" />
	<div class="fit">
		<StackedBars columns={marginColumns} colours={BAND_COLOURS} darkKeys={['20–30%', '30%+']} boldKeys={['20–30%', '30%+']} label="Share of polls by winning margin"
			ramp
			legendTitle="Share of polls, by the winner's margin over the runner-up (percentage points of the poll's votes)"
		/>
	</div>
	<figcaption class="note">
		Every poll reported in the results counts once, including advance, mail-in and long-term care polls, whatever its
		size. Polls with no votes are left out. 2023 was a by-election.
	</figcaption>
</figure>

<style>
	figure {
		margin: 0;
	}
	/* the chart and its note as wide as the body text's paragraphs (.text's 694px content box) */
	.fit {
		max-width: 694px;
		margin: 0 auto;
	}
	.note {
		max-width: 694px;
		margin: 14px auto 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
