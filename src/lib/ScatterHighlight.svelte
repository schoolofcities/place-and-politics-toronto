<script>
	// Scatter plot over all 585 tracts, with the current cluster's dots highlighted.
	// Built for Civic Professionals' "scatter plot of income vs. education, this group's
	// dots highlighted", but xKey/yKey are generic so it can be reused for any pair of
	// tract-level variables from ct_values.json.

	import { scaleLinear, extent } from "d3";

	export let values = []; // ct_values.json records
	export let xKey;
	export let yKey;
	export let xLabel = "";
	export let yLabel = "";
	export let clusterId;
	export let color = "#3d53fb";

	const FADE_COLOR = "#d8d8d8";
	const margin = { top: 10, bottom: 36, left: 48, right: 16 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	$: height = 360 - margin.top - margin.bottom;

	$: xScale = scaleLinear().domain(extent(values, (d) => d[xKey])).range([0, innerWidth]).nice();
	$: yScale = scaleLinear().domain(extent(values, (d) => d[yKey])).range([height, 0]).nice();
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={divWidth} height={height + margin.top + margin.bottom}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			<line x1="0" x2={innerWidth} y1={height} y2={height} class="axis" />
			<line x1="0" x2="0" y1="0" y2={height} class="axis" />
			<text class="axis-label" x={innerWidth / 2} y={height + 28} text-anchor="middle">{xLabel}</text>
			<text class="axis-label" x={-height / 2} y="-32" transform="rotate(-90)" text-anchor="middle">{yLabel}</text>

			{#each values.filter((d) => d.cluster_id !== clusterId) as d}
				<circle cx={xScale(d[xKey])} cy={yScale(d[yKey])} r="2.5" fill={FADE_COLOR} />
			{/each}
			{#each values.filter((d) => d.cluster_id === clusterId) as d}
				<circle cx={xScale(d[xKey])} cy={yScale(d[yKey])} r="3.5" fill={color} fill-opacity="0.85" />
			{/each}
		</g>
	</svg>
</div>

<style>
	.axis {
		stroke: #999;
		stroke-width: 1px;
	}
	.axis-label {
		font-size: 12px;
		fill: rgb(56, 56, 56);
		font-family: "Source Serif Pro", serif;
	}
</style>
