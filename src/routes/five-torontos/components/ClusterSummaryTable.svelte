<script>
	// Full results for one cluster's section, each row comparing this cluster's value directly
	// to Toronto's, behind a show/hide toggle: either the election results (a 2×2 square of
	// small tables: each election's vote shares, then turnout) or the census characteristics
	// (one table). Tables stack on narrow screens. Styled after the social-geography page's correlation tables (12px Open
	// Sans rows, bold headings over a light rule, small tabular numbers). Variable lists,
	// election-row labels and value formatting live in ./clusterVariables.js.

	import { slide } from "svelte/transition";
	import {
		SOCIOECONOMIC_KEYS,
		SOCIOECONOMIC_LABEL_OVERRIDES,
		ELECTIONS,
		formatSocioeconomicValue,
		formatVotingValue,
	} from "./clusterVariables.js";

	export let cluster; // this section's cluster record (clusters_summary.json entry)
	export let torontoElections; // clustersMetadata.toronto_benchmark.elections
	export let variableLabels; // clustersMetadata.variable_labels
	export let clusters = []; // all five cluster records, to mark this cluster's census values that are the highest/lowest of the five
	// "elections": the election tables (under the section's voting chart). "census": the census
	// table (at the end of the section).
	export let part = "elections";

	// show/hide state; a unique id ties the toggle to the panel it controls
	let open = false;
	const panelId = `${part}-${Math.random().toString(36).slice(2, 9)}`;
	const TOGGLE_MS = 280;
	const TOGGLE_LABELS = {
		elections: { show: "Show all election results used in the cluster analysis", hide: "Hide election results" },
		census: { show: "Show more census characteristics related to the cluster", hide: "Hide census characteristics" },
	};

	// the cluster's name split at its first space, for the two-line column heading
	$: nameSplit = cluster.label.indexOf(" ");
	$: nameLines =
		nameSplit === -1 ? [cluster.label, ""] : [cluster.label.slice(0, nameSplit), cluster.label.slice(nameSplit + 1)];

	$: censusRows = SOCIOECONOMIC_KEYS.map((key) => {
		const value = cluster.demographics[key];
		// Toronto's own value is this cluster's value minus its stored difference from Toronto
		const toronto = value - cluster.demographics_vs_toronto[key].diff_vs_toronto;
		const shown = formatSocioeconomicValue(key, value);
		// "high"/"low" when this cluster's value is the highest/lowest of all five, compared as
		// displayed (so a tie at e.g. "48%" marks each cluster that shows it)
		const allShown = clusters.map((c) => formatSocioeconomicValue(key, c.demographics[key]));
		const allRaw = clusters.map((c) => c.demographics[key]);
		const highShown = allShown[allRaw.indexOf(Math.max(...allRaw))];
		const lowShown = allShown[allRaw.indexOf(Math.min(...allRaw))];
		return {
			key,
			label: SOCIOECONOMIC_LABEL_OVERRIDES[key] ?? variableLabels[key] ?? key,
			value: shown,
			toronto: formatSocioeconomicValue(key, toronto),
			rank: clusters.length ? (shown === highShown ? "high" : shown === lowShown ? "low" : null) : null,
		};
	});

	$: electionTables = ELECTIONS.map((election) => ({
		key: election.key,
		heading: election.heading,
		rows: election.fields.map(({ field, label }) => ({
			key: `${election.key}.${field}`,
			label,
			value: formatVotingValue(cluster.elections[election.key][field]),
			toronto: formatVotingValue(torontoElections[election.key][field]),
			// raw percents for the row's bar (cluster) and tick (Toronto), on a 0–100% scale
			valuePct: cluster.elections[election.key][field],
			torontoPct: torontoElections[election.key][field],
		})),
	}));

	// one row per election: the cluster's turnout vs Toronto's
	$: turnoutTable = {
		key: "turnout",
		heading: "Voter\nturnout",
		rows: ELECTIONS.map((election) => ({
			key: `${election.key}.turnout`,
			label: election.heading.replace("\n", " "),
			value: formatVotingValue(cluster.elections[election.key].turnout),
			toronto: formatVotingValue(torontoElections[election.key].turnout),
			valuePct: cluster.elections[election.key].turnout,
			torontoPct: torontoElections[election.key].turnout,
		})),
	};
</script>

<!-- `bars`: add a column with a small bar per row (the cluster's value, in its colour) and a
	 tick at Toronto's value, both on a 0–100% scale. Decorative: the numbers carry the data. -->
{#snippet summaryTable(heading, rows, bars = false)}
	<!-- scrolls sideways inside its box when it doesn't fit (phones), with edge shadows -->
	<div class="scroll">
		<table>
			<thead>
				<tr>
					<th scope="col" class="heading">{heading}</th>
					<!-- the name always on two lines (split at its first space), matching the two-line
						 election titles and keeping the column narrow -->
					<th scope="col" class="num">{nameLines[0]}<br />{nameLines[1]}</th>
					<th scope="col" class="num">Toronto</th>
					{#if bars}
						<th scope="col" class="bar-cell" aria-hidden="true"></th>
					{/if}
				</tr>
			</thead>
			<tbody>
				{#each rows as row (row.key)}
					<tr>
						<th scope="row" class="row-label">{row.label}</th>
						<td class="num">
							{#if row.rank}
								<span class="rank rank-{row.rank}">{row.value}</span>
							{:else}
								{row.value}
							{/if}
						</td>
						<td class="num">{row.toronto}</td>
						{#if bars}
							<td class="bar-cell" aria-hidden="true">
								<div class="bar-track">
									<div class="bar" style:width="{row.valuePct}%" style:background={cluster.color}></div>
									<div class="tick" style:left="{row.torontoPct}%"></div>
								</div>
							</td>
						{/if}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/snippet}

<!-- a button + Svelte `slide` (rather than a native <details>, which snaps open) so the tables
	 ease open and closed; aria-expanded tells screen readers whether they're showing -->
<div class="toggle-section {part}-toggle" class:open>
	<button
		type="button"
		class="toggle"
		aria-expanded={open}
		aria-controls={panelId}
		on:click={() => (open = !open)}
	>
		<span class="arrow" aria-hidden="true">▸</span>
		<span class="when-closed">{TOGGLE_LABELS[part].show}</span>
		<span class="when-open">{TOGGLE_LABELS[part].hide}</span>
	</button>
	{#if open}
		<div class="panel" id={panelId} transition:slide={{ duration: TOGGLE_MS }}>
			{#if part === "elections"}
				<div class="summary-box elections">
					{#each [...electionTables, turnoutTable] as t (t.key)}
						{@render summaryTable(t.heading, t.rows, true)}
					{/each}
				</div>
			{:else}
				<div class="summary-box census">
					{@render summaryTable("Census characteristics (2021)", censusRows)}
					<p class="rank-note">
						<span class="rank rank-high">Blue</span>: highest of the five clusters.
						<span class="rank rank-low">Red</span>: lowest of the five clusters.
					</p>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	/* Each box shrinks to fit its tables, inside a light grey border. */
	.summary-box {
		display: grid;
		gap: 30px;
		box-sizing: border-box;
		width: fit-content;
		margin: 20px auto 0;
		padding: 12px 16px;
		border: 1px solid var(--brandGray);
		font-family: OpenSans, sans-serif;
		color: var(--brandGray90);
	}
	/* Four tables in a 2×2 square (the three elections' vote shares, then turnout), left-aligned
	   under the toggle; one column on phones. Each table fills its column, so tables in a
	   column share one width and their bars line up. */
	.elections {
		grid-template-columns: repeat(2, max-content);
		align-items: start;
		gap: 16px 30px;
		margin: 0;
	}
	.elections table {
		width: 100%;
	}
	.elections tbody th.row-label,
	.elections thead th.num {
		white-space: nowrap;
	}
	.census {
		max-width: 100%;
		margin: 0;
	}
	.census table {
		width: 360px; /* a fixed width, rather than shrink-to-fit */
		max-width: 100%;
	}

	/* show/hide toggle, styled like the social-geography page's buttons */
	/* sized and padded like the global `.text` column (694px max, 25px side padding), so the
	   button and the table line up with the left edge of the paragraphs */
	.toggle-section {
		max-width: 694px;
		width: calc(100% - 50px);
		padding: 0 25px;
		margin: 20px auto 0;
	}
	/* the census toggle sits close to the strip plot above it */
	.census-toggle {
		margin-top: 8px;
	}
	.toggle {
		display: inline-grid;
		grid-template-columns: auto auto; /* arrow, then the label */
		text-align: left;
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		color: var(--brandGray90);
		background: white;
		border: 1px solid #c8c8c8;
		padding: 5px 10px;
		cursor: pointer;
	}
	.toggle:hover {
		border-color: #9ba1a8;
	}
	/* one arrow that turns to point down when open, timed with the table's slide */
	/* The arrow and labels are centred vertically in the button. (Stretched to the full row
	   height, the arrow rotated about the middle of that tall box, landing low and to the side
	   when a long hidden label wrapped onto two lines on phones.) */
	.arrow {
		grid-area: 1 / 1;
		align-self: center;
		margin-right: 5px;
		line-height: 1;
		transform-origin: 50% 50%;
		transition: transform 280ms ease;
	}
	.open .arrow {
		transform: rotate(90deg);
	}
	/* both labels share one grid cell and the inactive one is only made invisible, so the button
	   keeps the longer label's width whether open or closed */
	.toggle > span:not(.arrow) {
		grid-area: 1 / 2;
		align-self: center;
	}
	.toggle-section .when-open,
	.toggle-section.open .when-closed {
		visibility: hidden;
	}
	.toggle-section.open .when-open {
		visibility: visible;
	}
	/* the gap above the table is padding on the sliding panel (not a margin on the box inside
	   it), so it's part of the height the slide animates rather than a jump at the end */
	.panel {
		padding-top: 12px;
	}

	table {
		border-collapse: collapse;
		font-size: 12px;
		line-height: 1.35;
	}
	th {
		font-weight: normal;
		text-align: left;
	}

	/* header row: the table's heading, the cluster's name and Toronto, over a light rule. Regular
	   weight (not bold), so the tables don't outweigh the voting chart above them. */
	thead th {
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		line-height: 1.2;
		color: var(--brandBlack);
		padding: 0 2px 3px;
		vertical-align: bottom;
		border-bottom: 1px solid var(--brandGray);
	}
	/* honour the line break written into each election's heading */
	thead th.heading {
		white-space: pre-line;
	}
	/* the census table has room, so its cluster name stays on one line */
	.census thead th {
		white-space: nowrap;
	}
	/* a little air between the rule and the first row */
	tbody tr:first-child > * {
		padding-top: 4px;
	}

	td,
	tbody th.row-label {
		padding: 1px 2px;
	}
	/* minimum gap between a label and its first number */
	tbody th.row-label {
		padding-right: 10px;
	}
	/* body rows a step lighter than the black headings */
	tbody {
		color: var(--brandGray80);
	}
	/* census values that are the highest (blue) or lowest (red) of all five clusters: bold, in
	   a box outlined in the brand blue or red (also used for the swatches in the note below) */
	.rank {
		display: inline-block;
		padding: 0 4px;
		border: 1.5px solid;
		border-radius: 3px;
		font-family: OpenSansBold, sans-serif;
		color: var(--brandBlack);
	}
	/* the bold value in the same colour as its box. The brand red is a touch light for small
	   text (4.2:1 on white), so the text uses a slightly darker shade of it (4.6:1). */
	.rank-high {
		border-color: var(--brandMedBlue);
		color: var(--brandMedBlue);
	}
	.rank-low {
		border-color: var(--brandRed);
		color: #D83925;
	}
	.rank-note {
		margin: 8px 0 0;
		font-size: 12px;
		color: var(--brandGray70);
	}
	.rank-note .rank {
		font-size: 11px;
		line-height: 1.2;
	}

	/* per-row bar: cluster value as a filled bar on a light track, Toronto as a dark tick */
	.bar-cell {
		width: 60px;
		padding-left: 10px;
		vertical-align: middle;
	}
	.bar-track {
		position: relative;
		width: 60px;
		height: 8px;
		background: #f2f2f2;
	}
	.bar {
		height: 100%;
	}
	.tick {
		position: absolute;
		top: -2px;
		bottom: -2px;
		width: 2px;
		margin-left: -1px;
		background: var(--brandGray80);
	}

	/* centred headings over centred values, as in the social-geography page's tables, so a
	   two-line cluster name sits squarely over its numbers */
	.num {
		text-align: center;
		padding-left: 6px;
		padding-right: 6px;
		font-size: 12px;
		font-variant-numeric: tabular-nums;
	}
	thead th.num {
		font-size: 12px;
	}

	/* Each table scrolls sideways inside its box when it's wider than the space (phones), rather
	   than pushing the page wider. Scroll shadows, as in ClusterComparisonTables.svelte: a soft
	   shadow on an edge wherever there's more table to scroll to (page-coloured "covers" scroll
	   with the content and hide each shadow once that end is reached). */
	.scroll {
		min-width: 0;
		max-width: 100%;
		overflow-x: auto;
		background:
			linear-gradient(to right, #fffefd 30%, rgba(255, 254, 253, 0)) left center / 40px 100% no-repeat local,
			linear-gradient(to left, #fffefd 30%, rgba(255, 254, 253, 0)) right center / 40px 100% no-repeat local,
			radial-gradient(farthest-side at 0 50%, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0)) left center / 14px 100% no-repeat scroll,
			radial-gradient(farthest-side at 100% 50%, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0)) right center / 14px 100% no-repeat scroll;
	}

	@media (max-width: 640px) {
		/* less side padding on phones, so the tables get more of the screen */
		.toggle-section {
			width: calc(100% - 20px);
			padding: 0 10px;
		}
		.summary-box {
			width: auto;
			max-width: none;
			margin-left: 0;
			margin-right: 0;
			padding: 10px;
		}
		.census {
			margin-left: 0;
			margin-right: 0;
		}
		.elections {
			grid-template-columns: minmax(0, 1fr);
			gap: 16px;
		}
		/* the boxes can shrink to the screen; their tables then scroll inside them */
		.summary-box,
		.census {
			min-width: 0;
			max-width: 100%;
			box-sizing: border-box;
		}
		table {
			width: 100%;
		}
		.census table {
			width: 100%;
			max-width: none;
		}
	}
</style>
