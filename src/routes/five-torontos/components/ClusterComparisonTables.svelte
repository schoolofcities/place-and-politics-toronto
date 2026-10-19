<script>
	// Two summary tables comparing all five clusters side by side, plus Toronto overall: one for
	// election results (each election's vote shares, then turnout), one for census
	// characteristics, with each row's highest cluster value bold and outlined in that cluster's colour. Same variables, labels and formatting as each section's own tables (see
	// ./ClusterSummaryTable.svelte and ./clusterVariables.js), and the same compact styling.
	// On narrow screens each table scrolls sideways rather than squeezing seven columns.

	import {
		SOCIOECONOMIC_KEYS,
		SOCIOECONOMIC_LABEL_OVERRIDES,
		ELECTIONS,
		formatSocioeconomicValue,
		formatVotingValue,
	} from "./clusterVariables.js";
	import { CLUSTER_OUTLINE_COLORS } from "./clusterColors.js";

	export let clusters; // all five cluster records, in display order (with this page's colours)
	export let torontoElections; // clustersMetadata.toronto_benchmark.elections
	export let variableLabels; // clustersMetadata.variable_labels

	// each cluster's name split at its first space, for the two-line column headings
	const nameLines = (label) => {
		const i = label.indexOf(" ");
		return i === -1 ? [label, ""] : [label.slice(0, i), label.slice(i + 1)];
	};

	// A row's formatted values plus which are its highest. Compared on the values as displayed,
	// so two clusters that both show e.g. "48%" are both marked. In percentage rows, small
	// highest values are marked less, since differences that small aren't worth drawing the eye
	// to: under 5%, not at all; 5% and up, bold and outlined. Non-percentage rows are always bold and outlined.
	const BOLD_MIN_PCT = 5;
	const OUTLINE_MIN_PCT = 5;
	function withMax(raw, format, isPercent = true) {
		const values = raw.map(format);
		const max = Math.max(...raw);
		const top = values[raw.indexOf(max)];
		const bold = !isPercent || max >= BOLD_MIN_PCT;
		const outline = !isPercent || max >= OUTLINE_MIN_PCT;
		return { values, isMax: values.map((v) => bold && v === top), outline };
	}

	// Toronto's census values: any cluster's value minus its stored difference from Toronto
	$: torontoCensus = Object.fromEntries(
		SOCIOECONOMIC_KEYS.map((key) => [
			key,
			clusters[0].demographics[key] - clusters[0].demographics_vs_toronto[key].diff_vs_toronto,
		])
	);

	$: electionGroups = [
		...ELECTIONS.map((election) => ({
			heading: election.heading.replace("\n", " "),
			rows: election.fields.map(({ field, label }) => ({
				key: `${election.key}.${field}`,
				label,
				...withMax(clusters.map((c) => c.elections[election.key][field]), formatVotingValue),
				toronto: formatVotingValue(torontoElections[election.key][field]),
			})),
		})),
		{
			heading: "Voter turnout",
			rows: ELECTIONS.map((election) => ({
				key: `${election.key}.turnout`,
				label: election.heading.replace("\n", " "),
				...withMax(clusters.map((c) => c.elections[election.key].turnout), formatVotingValue),
				toronto: formatVotingValue(torontoElections[election.key].turnout),
			})),
		},
	];

	$: censusGroups = [
		{
			heading: "Census characteristics (2021)",
			rows: SOCIOECONOMIC_KEYS.map((key) => ({
				key,
				label: SOCIOECONOMIC_LABEL_OVERRIDES[key] ?? variableLabels[key] ?? key,
				...withMax(
					clusters.map((c) => c.demographics[key]),
					(v) => formatSocioeconomicValue(key, v),
					key.startsWith("pct_")
				),
				toronto: formatSocioeconomicValue(key, torontoCensus[key]),
			})),
		},
	];

	$: tables = [
		{
			key: "elections",
			title: "Election results used to define the clusters",
			caption: "Election results by cluster",
			groups: electionGroups,
		},
		{
			key: "census",
			title: "Census characteristics, used only to describe the clusters",
			caption: "Census characteristics by cluster",
			groups: censusGroups,
		},
	];
</script>

<div class="comparison">
	{#each tables as table (table.key)}
		<div class="table-block">
			<h3 class="table-title">{table.title}</h3>
			<p class="scroll-hint" aria-hidden="true">Scroll to see all clusters →</p>
			<div class="scroll">
				<table>
					<caption class="visually-hidden">{table.caption}, compared to the City of Toronto</caption>
					<thead>
						<tr>
							<th scope="col" class="row-label"><span class="visually-hidden">Variable</span></th>
							{#each clusters as c (c.cluster_id)}
								{@const [first, second] = nameLines(c.label)}
								<th scope="col" class="num">
									<span class="dot" style:background={c.color}></span>{first}<br />{second}
								</th>
							{/each}
							<th scope="col" class="num toronto">City of<br />Toronto</th>
						</tr>
					</thead>
					{#each table.groups as group (group.heading)}
						<tbody>
							<tr class="group-row">
								<th scope="colgroup" colspan={clusters.length + 2}>{group.heading}</th>
							</tr>
							{#each group.rows as row (row.key)}
								<tr>
									<th scope="row" class="row-label">{row.label}</th>
									{#each row.values as v, i (clusters[i].cluster_id)}
										<td class="num">
											{#if row.isMax[i]}
												<!-- outlined in the cluster's (contrast-safe) outline colour, unless the row's
													 highest is a small percentage (see withMax) -->
												<span
													class="max"
													style:border-color={row.outline
														? (CLUSTER_OUTLINE_COLORS[clusters[i].slug] ?? clusters[i].color)
														: "transparent"}>{v}</span
												>
											{:else}
												{v}
											{/if}
										</td>
									{/each}
									<td class="num toronto">{row.toronto}</td>
								</tr>
							{/each}
						</tbody>
					{/each}
				</table>
			</div>
		</div>
	{/each}
</div>

<style>
	/* a single column that can shrink below the tables' width (grid items default to at least
	   their content's width, which would push the page wider instead of letting .scroll scroll) */
	.comparison {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 36px;
		max-width: 850px;
		width: calc(100% - 20px);
		margin: 0 auto;
		font-family: OpenSans, sans-serif;
	}
	.table-block {
		min-width: 0;
		padding-top: 15px;
	}
	/* only on screens narrow enough that the table (620px minimum) has to scroll */
	.scroll-hint {
		display: none;
		margin: -4px 0 6px;
		font-size: 12px;
		color: var(--brandGray70);
	}
	@media (max-width: 680px) {
		.scroll-hint {
			display: block;
		}
	}
	.table-title {
		margin: 0 0 10px;
		font-family: OpenSans, sans-serif;
		font-weight: normal;
		font-size: 14px;
		color: var(--brandBlack);
	}
	/* seven columns don't fit a phone: scroll sideways instead of squeezing */
	/* Scroll shadows: a soft shadow on an edge wherever there's more table to scroll to. The two
	   page-coloured "covers" scroll with the content (`local`) and hide each shadow (fixed to the
	   box, `scroll`) once that end is reached. CSS only, so nothing shows when the table fits. */
	.scroll {
		max-width: 100%;
		overflow-x: auto;
		background:
			linear-gradient(to right, #fffefd 30%, rgba(255, 254, 253, 0)) left center / 40px 100% no-repeat local,
			linear-gradient(to left, #fffefd 30%, rgba(255, 254, 253, 0)) right center / 40px 100% no-repeat local,
			radial-gradient(farthest-side at 0 50%, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0)) left center / 14px 100% no-repeat scroll,
			radial-gradient(farthest-side at 100% 50%, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0)) right center / 14px 100% no-repeat scroll;
	}
	/* fixed layout: the label column takes its set width, the six data columns share the rest
	   equally */
	table {
		width: 100%;
		min-width: 620px;
		table-layout: fixed;
		border-collapse: collapse;
		font-size: 12px;
		line-height: 1.35;
		color: var(--brandGray80);
	}
	th {
		font-weight: normal;
		text-align: left;
	}

	thead th {
		font-size: 12px;
		line-height: 1.2;
		color: var(--brandBlack);
		padding: 0 6px 4px;
		vertical-align: bottom;
		border-bottom: 1px solid var(--brandGray);
	}
	/* a circle in each cluster's colour above its name (same outline as the map legend's
	   swatches); Toronto's column has none */
	.dot {
		display: block;
		box-sizing: border-box;
		width: 11px;
		height: 11px;
		margin: 0 auto 4px;
		border-radius: 50%;
		border: 1px solid var(--brandGray70);
		box-shadow: inset 0 0 0 1px white;
	}

	/* group name: bold over a light rule */
	.group-row th {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandGray90);
		padding: 14px 2px 2px;
		border-bottom: 1px solid var(--brandGray);
	}
	.group-row + tr > * {
		padding-top: 4px;
	}

	td,
	tbody th.row-label {
		padding: 1px 6px;
	}
	/* very faint rules between rows (3% grey) */
	tbody tr:not(.group-row) > * {
		border-bottom: 1px solid #f7f7f7;
	}
	thead th.row-label {
		width: 28%;
	}
	tbody th.row-label {
		padding-left: 2px;
		padding-right: 12px;
		white-space: nowrap;
	}
	.num {
		text-align: center;
		font-size: 12px;
		font-variant-numeric: tabular-nums;
	}
	thead th.num {
		font-size: 12px;
	}
	/* the highest of the five clusters in each row: bold, in a box outlined in that cluster's
	   colour (its darker outline shade for saffron, rose and aqua, so the box has enough
	   contrast against white; see ./clusterColors.js) */
	.max {
		display: inline-block;
		padding: 0 4px;
		border: 1.5px solid;
		border-radius: 3px;
		font-family: OpenSansBold, sans-serif;
		color: var(--brandBlack);
	}
	/* Toronto's column set slightly apart, as the reference the clusters are compared to */
	.toronto {
		border-left: 1px solid var(--brandGray);
	}

	.visually-hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip: rect(0 0 0 0);
		white-space: nowrap;
	}
</style>
