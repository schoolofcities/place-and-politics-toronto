<script>
	// Scatter plot over all 585 tracts, with the current cluster's dots highlighted. Built
	// for Civic Professionals' "income vs. education, this group's dots highlighted", but
	// xKey/yKey are generic so it can be reused for any pair of tract-level variables.

	import { scaleLinear, extent } from "d3";

	export let values = []; // ct_values.json records
	export let xKey;
	export let yKey;
	export let xLabel = "";
	export let yLabel = "";
	export let xFormat = (v) => v; // tick value -> display string, e.g. "$40k" or "20%"
	export let yFormat = (v) => v;
	export let clusterId;
	export let color = "#3d53fb";

	const FADE_COLOR = "#d8d8d8";
	const margin = { top: 10, bottom: 44, left: 56, right: 16 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	$: height = 360 - margin.top - margin.bottom;

	$: xScale = scaleLinear().domain(extent(values, (d) => d[xKey])).range([0, innerWidth]).nice();
	$: yScale = scaleLinear().domain(extent(values, (d) => d[yKey])).range([height, 0]).nice();
	$: xTicks = xScale.ticks(5);
	$: yTicks = yScale.ticks(5);
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={divWidth} height={height + margin.top + margin.bottom}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			<line x1="0" x2={innerWidth} y1={height} y2={height} class="axis" />
			<line x1="0" x2="0" y1="0" y2={height} class="axis" />

			{#each xTicks as t}
				<line class="tick" x1={xScale(t)} x2={xScale(t)} y1={height} y2={height + 5} />
				<text class="tick-label" x={xScale(t)} y={height + 17} text-anchor="middle">{xFormat(t)}</text>
			{/each}
			{#each yTicks as t}
				<line class="tick" x1="-5" x2="0" y1={yScale(t)} y2={yScale(t)} />
				<text class="tick-label" x="-9" y={yScale(t) + 3} text-anchor="end">{yFormat(t)}</text>
			{/each}

			<text class="axis-label" x={innerWidth / 2} y={height + 36} text-anchor="middle">{xLabel}</text>
			<text class="axis-label" x={-height / 2} y="-40" transform="rotate(-90)" text-anchor="middle">{yLabel}</text>

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
	.tick {
		stroke: #999;
		stroke-width: 1px;
	}
	.tick-label {
		font-size: 10px;
		fill: rgb(56, 56, 56);
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	.axis-label {
		font-size: 12px;
		fill: rgb(56, 56, 56);
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>
