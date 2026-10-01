<script>
	// Two-column summary (socioeconomic / voting) for one cluster's section. Unlike most
	// components on this page, this one is NOT "dumb" — it owns the expand/scroll and
	// comparison-target state itself, since those are inherently stateful UI behaviours that
	// need to recompute every row live. The page just hands it the raw cluster records and
	// metadata; see ./clusterVariables.js for the full variable catalogs and formatting rules.
	//
	// Each column defaults to a curated 5 rows. A half-height "+" row underneath lets a reader
	// expand it into a scrollable window (still 5 rows tall) over every variable we have —
	// curated rows keep their normal styling wherever they land in that scroll; everything
	// else gets a slightly lighter background so the curated 5 stay visually distinct even
	// while browsing the rest. The two columns expand/scroll fully independently. Every label
	// (see ./clusterVariables.js) is a short, single-line abbreviation, and it's the SAME text
	// whether a variable is showing curated or discovered while browsing — labels never change
	// between the two views, and row height never depends on which variable landed in a row.
	//
	// A single "Compare to" bar underneath both columns (not per-column — one comparison
	// target makes sense for the whole section) swaps every row's delta from "vs. Toronto" to
	// "vs. this other cluster" and recolours the delta to that cluster's own colour. It affects
	// whichever rows are currently visible, curated or expanded alike.

	import {
		CURATED_SOCIOECONOMIC_KEYS,
		ALL_SOCIOECONOMIC_KEYS,
		ALL_VOTING_SPECS,
		socioeconomicLabel,
		votingVarKey,
		votingVarLabel,
		votingSpecsEqual,
		formatSocioeconomicValue,
		formatSocioeconomicDelta,
		formatVotingValue,
		formatVotingDelta,
	} from "./clusterVariables.js";

	export let title = "";
	export let cluster; // this section's cluster record (clusters_summary.json entry)
	export let clusters; // all 5 cluster records, for comparison targets + their colours
	export let torontoElections; // clustersMetadata.toronto_benchmark.elections
	export let votingSpecs; // this section's curated voting rows: [{ election, field }]

	const WINDOW = 5;

	// Each instance gets a unique id prefix (rather than a static string) so the heading/table
	// aria-labelledby pairing below stays valid even with 5 of these on one page (one per
	// cluster section) — duplicate ids are invalid HTML and break the association for AT users.
	let uid = `cst-${Math.random().toString(36).slice(2, 9)}`;

	let socioExpanded = false;
	let votingExpanded = false;
	let socioScroll = 0; // index into ALL_SOCIOECONOMIC_KEYS
	let votingScroll = 0; // index into ALL_VOTING_SPECS

	// "toronto", or another cluster's cluster_id. Local to this section's table — switching it
	// here never affects any other section, and it always starts back at Toronto.
	let compareTarget = "toronto";

	$: otherClusters = clusters.filter((c) => c.cluster_id !== cluster.cluster_id);
	$: compareCluster = compareTarget === "toronto" ? null : clusters.find((c) => c.cluster_id === compareTarget);
	$: compareColor = compareCluster ? compareCluster.color : "#666";

	// `compareCluster` is passed in explicitly (rather than closed over) and referenced directly
	// in each call site's `$:` statement below — Svelte's reactivity only re-runs a `$:` block
	// when the variables *textually present in it* change, so a plain closure over a reactive
	// variable wouldn't reliably recompute these rows when the comparison target changes (the
	// same gotcha documented in TernaryProfilePlot.svelte/RadarTriangle.svelte).
	function socioRow(key, compareCluster) {
		const value = cluster.demographics[key];
		const delta = compareCluster
			? value - compareCluster.demographics[key]
			: cluster.demographics_vs_toronto[key].diff_vs_toronto;
		return {
			key,
			label: socioeconomicLabel(key),
			value: formatSocioeconomicValue(key, value),
			delta: formatSocioeconomicDelta(key, delta),
			curated: CURATED_SOCIOECONOMIC_KEYS.includes(key),
		};
	}

	function votingRow(spec, compareCluster) {
		const value = cluster.elections[spec.election][spec.field];
		const compareValue = compareCluster
			? compareCluster.elections[spec.election][spec.field]
			: torontoElections[spec.election][spec.field];
		return {
			key: votingVarKey(spec),
			label: votingVarLabel(spec),
			value: formatVotingValue(value),
			delta: formatVotingDelta(value - compareValue),
			curated: votingSpecs.some((s) => votingSpecsEqual(s, spec)),
		};
	}

	$: socioScrollMax = ALL_SOCIOECONOMIC_KEYS.length - WINDOW;
	$: votingScrollMax = ALL_VOTING_SPECS.length - WINDOW;

	$: socioRowsCollapsed = CURATED_SOCIOECONOMIC_KEYS.map((key) => socioRow(key, compareCluster));
	$: socioRowsExpanded = ALL_SOCIOECONOMIC_KEYS.slice(socioScroll, socioScroll + WINDOW).map((key) =>
		socioRow(key, compareCluster)
	);
	$: votingRowsCollapsed = votingSpecs.map((s) => votingRow(s, compareCluster));
	$: votingRowsExpanded = ALL_VOTING_SPECS.slice(votingScroll, votingScroll + WINDOW).map((spec) =>
		votingRow(spec, compareCluster)
	);

	function scroll(which, dir) {
		if (which === "socio") socioScroll = Math.min(Math.max(socioScroll + dir, 0), socioScrollMax);
		else votingScroll = Math.min(Math.max(votingScroll + dir, 0), votingScrollMax);
	}

	$: columns = [
		{
			key: "socio",
			heading: "Socioeconomic",
			rows: socioExpanded ? socioRowsExpanded : socioRowsCollapsed,
			expanded: socioExpanded,
			atTop: socioScroll <= 0,
			atBottom: socioScroll >= socioScrollMax,
			toggle: () => (socioExpanded = !socioExpanded),
			up: () => scroll("socio", -1),
			down: () => scroll("socio", 1),
		},
		{
			key: "voting",
			heading: "Voting",
			rows: votingExpanded ? votingRowsExpanded : votingRowsCollapsed,
			expanded: votingExpanded,
			atTop: votingScroll <= 0,
			atBottom: votingScroll >= votingScrollMax,
			toggle: () => (votingExpanded = !votingExpanded),
			up: () => scroll("voting", -1),
			down: () => scroll("voting", 1),
		},
	];
</script>

<div class="summary-tables">
	{#if title}
		<h3>{title}</h3>
	{/if}

	<div class="table-grid">
		{#each columns as col, i (col.key)}
			{@const headingId = `${uid}-${i}`}
			<div class="table-block">
				<h3 id={headingId}>{col.heading}</h3>
				<table aria-labelledby={headingId}>
					<tbody>
						{#if col.expanded}
							<tr class="control-row">
								<td colspan="2">
									<button
										class="scroll-btn"
										on:click={col.up}
										disabled={col.atTop}
										aria-label={`Scroll up through ${col.heading.toLowerCase()} variables`}
									>
										&#9650;
									</button>
								</td>
							</tr>
						{/if}

						{#each col.rows as row (row.key)}
							<tr class:muted={col.expanded && !row.curated}>
								<td class="row-label">{row.label}</td>
								<td class="row-value">
									{row.value}
									<span class="delta" style:color={compareColor}>({row.delta})</span>
								</td>
							</tr>
						{/each}

						{#if col.expanded}
							<tr class="control-row">
								<td colspan="2">
									<button
										class="scroll-btn"
										on:click={col.down}
										disabled={col.atBottom}
										aria-label={`Scroll down through ${col.heading.toLowerCase()} variables`}
									>
										&#9660;
									</button>
								</td>
							</tr>
							<tr class="control-row">
								<td colspan="2">
									<button
										class="toggle-btn"
										on:click={col.toggle}
										aria-label={`Show only the top 5 ${col.heading.toLowerCase()} variables`}
									>
										&minus;
									</button>
								</td>
							</tr>
						{:else}
							<tr class="control-row">
								<td colspan="2">
									<button
										class="toggle-btn"
										on:click={col.toggle}
										aria-label={`Show all ${col.heading.toLowerCase()} variables`}
									>
										+
									</button>
								</td>
							</tr>
						{/if}
					</tbody>
				</table>
			</div>
		{/each}
	</div>

	<div class="compare-bar">
		<span class="compare-label">Compare to</span>
		<button class="compare-option" class:active={compareTarget === "toronto"} on:click={() => (compareTarget = "toronto")}>
			Toronto
		</button>
		{#each otherClusters as c (c.cluster_id)}
			<button
				class="compare-option"
				class:active={compareTarget === c.cluster_id}
				style:--option-color={c.color}
				on:click={() => (compareTarget = c.cluster_id)}
			>
				{c.label}
			</button>
		{/each}
	</div>
</div>

<style>
	.summary-tables {
		font-family: "Source Serif Pro", serif;
		margin: 20px auto 0;
		max-width: 600px;
	}
	.table-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20px;
	}
	.table-block h3 {
		margin: 0 0 4px;
		font-size: 14px;
		font-weight: normal;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #666;
	}
	/* Each row reads like the map legend's rectangles — a bordered off-white bar per row —
	   rather than one big background block behind the whole table. Same sans-serif as the
	   map legend labels (see ./ClusterMap.svelte) rather than the serif used for body
	   copy, so the numbers read as data rather than prose. */
	table {
		width: 100%;
		table-layout: fixed;
		border-collapse: separate;
		border-spacing: 0 4px;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
		font-size: 15px;
	}
	td {
		padding: 4px 10px;
		background: #faf8f2;
		border-top: 1px solid black;
		border-bottom: 1px solid black;
		overflow: hidden;
	}
	.row-label {
		width: 58%;
		border-left: 1px solid black;
		/* Labels are chosen short enough to fit in one line (see ./clusterVariables.js); this is
		   a safety net so a row's height can never vary by which variable landed in it. */
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.row-value {
		width: 42%;
		border-right: 1px solid black;
		text-align: right;
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
		letter-spacing: 0.02em; /* a touch of the "blocky" feel the numbers should carry */
	}
	.delta {
		font-variant-numeric: tabular-nums;
	}

	/* Rows visible only because a column is expanded (not part of the curated 5) recede into a
	   slightly lighter background instead of the curated rows' off-white, so the reader can
	   always tell which 5 are "the point" even while scrolling through everything else. */
	tr.muted td {
		background: #fdfcf9;
		border-color: #ccc;
		color: #888;
	}

	/* Control rows (expand/collapse/scroll) are deliberately half the height of a data row —
	   they're chrome for browsing, not data themselves. */
	.control-row td {
		padding: 1px 10px;
		border-left: 1px solid black;
		border-right: 1px solid black;
	}
	.scroll-btn,
	.toggle-btn {
		display: block;
		width: 100%;
		height: 13px;
		line-height: 13px;
		padding: 0;
		border: none;
		background: transparent;
		font-family: inherit;
		font-size: 9px;
		color: #666;
		cursor: pointer;
	}
	.toggle-btn {
		font-size: 12px;
		font-weight: 600;
	}
	.scroll-btn:hover:not(:disabled),
	.toggle-btn:hover {
		color: black;
	}
	.scroll-btn:disabled {
		color: #ddd;
		cursor: default;
	}

	/* All 5 names together are wider than the 600px table column above, so this bar is let out
	   of that column — centred on the same axis via the position/left/transform trick below —
	   up to the width of the page's own text column (850px, see +page.svelte's `.cluster-section`),
	   which comfortably fits every section's longest combination on an actual desktop viewport.
	   `width: max-content` capped by that `max-width` is what gives the responsive behaviour:
	   sized to fit its content with no scroll or compression on desktop, but once the viewport
	   itself can't offer that width (mobile), the cap shrinks and flex-wrap takes over, wrapping
	   to extra lines instead of overflowing or scrolling. */
	.compare-bar {
		position: relative;
		left: 50%;
		transform: translateX(-50%);
		width: max-content;
		max-width: min(850px, calc(100vw - 40px));
		margin-top: 14px;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 6px 8px;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	.compare-label {
		flex: none;
		font-size: 12px;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #666;
		margin-right: 2px;
	}
	.compare-option {
		flex: none;
		white-space: nowrap;
		font-family: inherit;
		font-size: 12px;
		padding: 3px 9px;
		border: 1px solid black;
		border-radius: 999px;
		background: #faf8f2;
		color: black;
		cursor: pointer;
	}
	.compare-option.active {
		background: var(--option-color, black);
		border-color: var(--option-color, black);
		color: white;
	}
	.compare-option:hover:not(.active) {
		background: #efece2;
	}

	/* Below this, two squeezed columns would leave too little room for the row-label column to
	   hold even these abbreviated labels without truncating — stack to one full-width column
	   instead, which has far more room per table than a squeezed 2-column layout would. */
	@media (max-width: 640px) {
		.table-grid {
			grid-template-columns: 1fr;
			gap: 14px;
		}
		table {
			font-size: 13px;
		}
		.row-label,
		.row-value {
			padding: 4px 6px;
		}
		.control-row td {
			padding: 1px 6px;
		}
	}
</style>
