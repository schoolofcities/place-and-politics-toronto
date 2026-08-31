<script>
	// Generic two-table summary (socioeconomic / voting) for one cluster's section.
	// Deliberately dumb: the page passes in already-resolved {label, value} rows so this
	// component doesn't need to know about clusters_summary.json's shape. Swap for
	// richer styling (vs.-Toronto deltas, sparklines, etc.) once the final design lands.

	export let title = "";
	export let socioeconomic = []; // [{ label, value }]
	export let voting = []; // [{ label, value }]
</script>

<div class="summary-tables">
	{#if title}
		<h4>{title}</h4>
	{/if}

	<div class="table-grid">
		<div class="table-block">
			<h5>Socioeconomic</h5>
			<table>
				<tbody>
					{#each socioeconomic as row}
						<tr>
							<td class="row-label">{row.label}</td>
							<td class="row-value">{row.value}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="table-block">
			<h5>Voting</h5>
			<table>
				<tbody>
					{#each voting as row}
						<tr>
							<td class="row-label">{row.label}</td>
							<td class="row-value">{row.value}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

<style>
	.summary-tables {
		font-family: "Source Serif Pro", serif;
		margin: auto;
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
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 15px;
	}
	td {
		padding: 4px 0;
		border-bottom: 1px solid #eee;
	}
	.row-value {
		text-align: right;
		font-variant-numeric: tabular-nums;
	}
</style>
