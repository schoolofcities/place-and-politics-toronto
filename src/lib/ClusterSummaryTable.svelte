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
	   rather than one big background block behind the whole table. */
	table {
		width: 100%;
		border-collapse: separate;
		border-spacing: 0 4px;
		font-size: 15px;
	}
	td {
		padding: 4px 10px;
		background: #faf8f2;
		border-top: 1px solid black;
		border-bottom: 1px solid black;
	}
	.row-label {
		border-left: 1px solid black;
	}
	.row-value {
		border-right: 1px solid black;
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	@media (max-width: 480px) {
		.table-grid {
			grid-template-columns: 1fr;
			gap: 14px;
		}
		table {
			font-size: 14px;
		}
	}
</style>
