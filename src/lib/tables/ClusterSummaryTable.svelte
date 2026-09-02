<script>
	// Two-column summary (socioeconomic / voting) for one cluster's section. Deliberately
	// dumb: the page passes in already-resolved rows so this component doesn't need to know
	// about clusters_summary.json's shape. Each row is { label, value, delta? } — `delta`
	// (percentage points vs. the Toronto-wide figure) is optional; when present it's shown
	// beside the value, green if the cluster is above the city average, red if below.

	export let title = "";
	export let socioeconomic = []; // [{ label, value, delta? }]
	export let voting = []; // [{ label, value, delta? }]

	$: tables = [
		{ heading: "Socioeconomic", rows: socioeconomic },
		{ heading: "Voting", rows: voting },
	];

	function deltaText(delta) {
		const rounded = Math.round(delta);
		const arrow = rounded >= 0 ? "▲" : "▼";
		return `(${arrow}${Math.abs(rounded)}%)`;
	}
</script>

<div class="summary-tables">
	{#if title}
		<h4>{title}</h4>
	{/if}

	<div class="table-grid">
		{#each tables as { heading, rows }}
			<div class="table-block">
				<h5>{heading}</h5>
				<table>
					<tbody>
						{#each rows as row}
							<tr>
								<td class="row-label">{row.label}</td>
								<td class="row-value">
									{row.value}
									{#if row.delta !== undefined && row.delta !== null}
										<span class="delta" class:positive={row.delta >= 0} class:negative={row.delta < 0}>
											{deltaText(row.delta)}
										</span>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
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
	.table-block h5 {
		margin-bottom: 4px;
		font-size: 14px;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #666;
	}
	/* Each row reads like the map legend's rectangles — a bordered off-white bar per row —
	   rather than one big background block behind the whole table. Same sans-serif as the
	   map legend labels (see $lib/maps/ClusterMap.svelte) rather than the serif used for body
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
	.delta.positive {
		color: #1a7d3a;
	}
	.delta.negative {
		color: #c0392b;
	}

	@media (max-width: 480px) {
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
	}
</style>
