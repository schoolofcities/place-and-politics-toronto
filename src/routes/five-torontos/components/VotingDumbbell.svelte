<script>
	// Dumbbell chart summarizing a cluster's voting: one row per selected measure (each
	// section's `votingSpecs`, from ../sections.js), with the cluster's value (filled dot, in its
	// colour) and Toronto's (hollow dot) on a shared 0–100% axis, joined by a line showing the
	// gap, each dot labelled with its value. The full results are in ClusterSummaryTable.svelte's election tables. Styled after
	// the social-geography page (Open Sans, grey secondary text, light rules).

	export let cluster; // this section's cluster record (clusters_summary.json entry)
	export let torontoElections; // clustersMetadata.toronto_benchmark.elections
	export let variableLabels; // clustersMetadata.variable_labels
	export let specs; // [{ election, field }], in display order

	// an (election, field) spec's key in clusters_metadata.json's `variable_labels`
	const LABEL_PREFIX = { mayor_2023: "mun", provincial_2025: "prov", federal_2025: "fed" };
	const TICKS = [0, 25, 50, 75, 100];

	$: rows = specs.map(({ election, field }) => {
		const key = `${LABEL_PREFIX[election]}_${field}`;
		const value = cluster.elections[election][field];
		const toronto = torontoElections[election][field];
		return {
			key,
			label: variableLabels[key] ?? key,
			value,
			toronto,
			lo: Math.min(value, toronto),
			hi: Math.max(value, toronto),
			// each dot's % label goes on its outer side, away from the other dot, so they never collide
			clusterRight: value >= toronto,
		};
	});
</script>

<figure class="dumbbell">
	<figcaption class="key">
		<span class="key-item"><span class="dot cluster-dot" style:background={cluster.color}></span>{cluster.label}</span>
		<span class="key-item"><span class="dot toronto-dot"></span>City of Toronto average</span>
	</figcaption>

	<div class="chart">
		<!-- axis labels -->
		<div class="axis" aria-hidden="true">
			{#each TICKS as t}
				<span class="axis-label" style:left="{t}%">{t}%</span>
			{/each}
		</div>

		{#each rows as row (row.key)}
			<div class="label">{row.label}</div>
			<div class="track" aria-hidden="true">
				{#each TICKS as t}
					<span class="grid-line" style:left="{t}%"></span>
				{/each}
				<span class="gap-line" style:left="{row.lo}%" style:width="{row.hi - row.lo}%"></span>
				<span class="dot toronto-dot" style:left="{row.toronto}%"></span>
				<span class="dot cluster-dot" style:left="{row.value}%" style:background={cluster.color}></span>
				<span class="dot-label toronto-label" class:right={!row.clusterRight} style:left="{row.toronto}%">
					{row.toronto.toFixed(0)}%
				</span>
				<span class="dot-label cluster-label" class:right={row.clusterRight} style:left="{row.value}%">
					{row.value.toFixed(0)}%
				</span>
			</div>
		{/each}
	</div>
</figure>

<style>
	/* 50px below the map's boundary buttons, which hang 14px below the map (see ClusterMap.svelte) */
	.dumbbell {
		max-width: 694px;
		width: calc(100% - 50px);
		margin: 64px auto 0;
		padding: 0 25px;
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		color: var(--brandGray90);
	}

	.key {
		display: flex;
		gap: 16px;
		margin-bottom: 6px;
		font-size: 12px;
		color: var(--brandBlack);
	}
	.key-item {
		display: inline-flex;
		align-items: center;
		gap: 5px;
	}
	.key .dot {
		position: static;
		transform: none;
	}

	/* label | track; the axis labels sit over the track column. The wider gap leaves room for a
	   value label left of a dot near 0%. */
	.chart {
		display: grid;
		grid-template-columns: max-content minmax(0, 1fr);
		column-gap: 28px;
		row-gap: 7px;
		align-items: center;
	}
	.axis {
		grid-column: 2;
		position: relative;
		height: 14px;
		/* same inset as the tracks below, so labels sit over their grid lines; a little extra
		   room underneath before the first row */
		margin: 0 6px 3px;
	}
	.axis-label {
		position: absolute;
		transform: translateX(-50%);
		font-size: 11px;
		color: var(--brandGray70);
		font-variant-numeric: tabular-nums;
	}

	.label {
		grid-column: 1;
		font-size: 13px;
		white-space: nowrap;
		color: var(--brandBlack);
	}
	.track {
		position: relative;
		height: 14px;
		/* room so a dot at 0% or 100% doesn't spill past the column */
		margin: 0 6px;
	}
	.grid-line {
		position: absolute;
		top: 0;
		bottom: 0;
		width: 1px;
		background: #ececec;
	}
	.gap-line {
		position: absolute;
		top: 50%;
		height: 2px;
		margin-top: -1px;
		background: #c8c8c8;
	}

	.dot {
		display: inline-block;
		box-sizing: border-box;
		width: 13px;
		height: 13px;
		border-radius: 50%;
		position: absolute;
		top: 50%;
		transform: translate(-50%, -50%);
	}
	/* same outline treatment as the map legend's swatches */
	.cluster-dot {
		border: 1px solid var(--brandGray70);
		box-shadow: inset 0 0 0 1px white;
	}
	.toronto-dot {
		background: white;
		border: 2px solid #606060; /* between --brandGray60 and --brandGray70 */
	}

	/* value labels beside the dots: left of the dot by default, right with `.right` */
	.dot-label {
		position: absolute;
		top: 50%;
		transform: translate(calc(-100% - 10px), -50%);
		font-size: 12px;
		line-height: 1;
		white-space: nowrap;
		font-variant-numeric: tabular-nums;
	}
	.dot-label.right {
		transform: translate(10px, -50%);
	}
	.cluster-label {
		font-family: OpenSansBold, sans-serif;
		color: var(--brandGray90);
	}
	.toronto-label {
		color: var(--brandGray70);
	}

	@media (max-width: 600px) {
		/* there the buttons sit in the flow below the map instead, so 50px from them */
		.dumbbell {
			margin-top: 50px;
		}
		.label {
			white-space: normal;
			max-width: 110px;
		}
	}
</style>
