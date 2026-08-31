<script>
	// Dumbbell chart: a line + two dots (Toronto-wide vs. this cluster) per variable.
	// Alternate to ClusterCompareBars.svelte for the Working Suburbanites section
	// ("multiple bar chart? Or dumbbell chart" in the outline) — same input shape as
	// ClusterCompareBars so the page can swap between them without touching the data prep.

	import { scaleLinear, extent } from "d3";

	export let rows = []; // [{ label, clusterValue, torontoValue, format? }]
	export let color = "#3d53fb";
	export let torontoColor = "#999";

	const rowHeight = 40;
	const margin = { top: 10, bottom: 10, left: 16, right: 60 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	$: height = rows.length * rowHeight + margin.top + margin.bottom;
	$: scale = scaleLinear()
		.domain(extent(rows.flatMap((d) => [d.clusterValue, d.torontoValue])))
		.range([0, innerWidth])
		.nice();
	$: fmt = (d, v) => (d.format ? d.format(v) : v);
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			{#each rows as row, i}
				{@const y = i * rowHeight + rowHeight / 2}
				<text class="row-title" x="0" y={y - 10}>{row.label}</text>
				<line
					x1={scale(row.torontoValue)}
					x2={scale(row.clusterValue)}
					y1={y}
					y2={y}
					stroke="#ccc"
					stroke-width="2"
				/>
				<circle cx={scale(row.torontoValue)} cy={y} r="5" fill={torontoColor} />
				<circle cx={scale(row.clusterValue)} cy={y} r="6" fill={color} />
				<text class="value" x={innerWidth + 8} y={y + 4}>
					{fmt(row, row.clusterValue)} vs. {fmt(row, row.torontoValue)}
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
