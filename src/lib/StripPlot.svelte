<script>
	// Generic 1-N variable strip plot: each row is one variable's axis, every one of the
	// 585 census tracts gets a dot on it, and the current cluster's tracts are highlighted
	// in its colour against the rest of the city in grey. Passing 2 variables gives the
	// "double strip plot" in the Progressive Core section; 3 gives the "triple strip plot"
	// in the Settled Conservatives section — same component either way.

	import { scaleLinear, extent } from "d3";

	export let values = []; // ct_values.json records (or a pre-filtered subset)
	export let variables = []; // [{ key, label, format? }] — format: (v) => string, optional
	export let clusterId;
	export let color = "#3d53fb";

	const FADE_COLOR = "#d8d8d8";
	const rowHeight = 70;
	const margin = { top: 24, bottom: 10, left: 16, right: 16 };

	let divWidth = 600;
	$: innerWidth = divWidth - margin.left - margin.right;
	$: height = variables.length * rowHeight + margin.top + margin.bottom;

	$: scales = variables.map((v) =>
		scaleLinear().domain(extent(values, (d) => d[v.key])).range([0, innerWidth]).nice()
	);
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			{#each variables as v, i}
				{@const y = i * rowHeight}
				{@const scale = scales[i]}
				<text class="row-title" x="0" y={y - 6}>{v.label}</text>
				<line class="axis" x1="0" x2={innerWidth} y1={y + 20} y2={y + 20} />

				<!-- background: every tract in the city -->
				{#each values.filter((d) => d.cluster_id !== clusterId) as d}
					<circle cx={scale(d[v.key])} cy={y + 20} r="2.5" fill={FADE_COLOR} />
				{/each}
				<!-- foreground: this cluster's tracts -->
				{#each values.filter((d) => d.cluster_id === clusterId) as d}
					<circle cx={scale(d[v.key])} cy={y + 20} r="3.5" fill={color} fill-opacity="0.85" />
				{/each}
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
	.axis {
		stroke: #bbb;
		stroke-width: 1px;
	}
</style>
