<script>
	// Grouped horizontal bars: this cluster vs. the Toronto-wide value, one row per variable.
	// Candidate for the Mobile Middle section ("stacked bar chart or radar chart" in the
	// outline — a true radar is a bigger lift for an SVG-from-scratch build, so this bar
	// version is the placeholder) and for Working Suburbanites ("multiple bar chart... or
	// dumbbell chart" — see DumbbellChart.svelte for the other option).

	import { scaleLinear, max } from "d3";

	export let rows = []; // [{ label, clusterValue, torontoValue, format? }]
	export let color = "#3d53fb";

	const barHeight = 12;
	const rowHeight = 46;
	const margin = { top: 4, bottom: 4, left: 16, right: 48 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	$: height = rows.length * rowHeight + margin.top + margin.bottom;
	$: scale = scaleLinear()
		.domain([0, max(rows, (d) => Math.max(d.clusterValue, d.torontoValue)) || 1])
		.range([0, innerWidth])
		.nice();
	$: fmt = (d, v) => (d.format ? d.format(v) : v);
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			{#each rows as row, i}
				{@const y = i * rowHeight}
				<text class="row-title" x="0" y={y + 10}>{row.label}</text>

				<rect x="0" y={y + 14} width={scale(row.torontoValue)} height={barHeight} fill="#ccc" />
				<text class="value" x={scale(row.torontoValue) + 6} y={y + 14 + barHeight - 2}>
					Toronto: {fmt(row, row.torontoValue)}
				</text>

				<rect x="0" y={y + 14 + barHeight + 3} width={scale(row.clusterValue)} height={barHeight} fill={color} />
				<text class="value" x={scale(row.clusterValue) + 6} y={y + 14 + 2 * barHeight + 1}>
					This group: {fmt(row, row.clusterValue)}
				</text>
			{/each}
		</g>
	</svg>
</div>

<style>
	.row-title {
		font-size: 13px;
		fill: rgb(56, 56, 56);
		font-family: "Source Serif Pro", serif;
	}
	.value {
		font-size: 11px;
		fill: #333;
	}
</style>
