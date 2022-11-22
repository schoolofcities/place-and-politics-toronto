<script>

import tracts from "../data/ctWithResults.geo.json"
import { geoPath, geoMercator, scaleThreshold } from "d3";

console.log(tracts);

// export var colours;
export var candidate;

let colours = ["#deebfd", "#a7c9ff", "#77a5ff", "#507fff", "#3d53fb"]

const candidates = {
	"pcttory_john2022": {
		"breaks": [0.4, 0.5, 0.6, 0.7],
		"name": "John Tory",
		"year": "2022"
	},
	"pcttory2018": {
		"breaks": [0.4, 0.5, 0.6, 0.7],
		"name": "John Tory",
		"year": "2018"
	}
}



let divWidth = 350;
$: innerWidth = divWidth;
$: height = 225;

$: projection = geoMercator()
	.center([-78.15 - 0.0023*innerWidth + 0.000001125*innerWidth**2, 43.54 + 0.00045*innerWidth - 2.5e-7*innerWidth**2])
	.scale([82000 * innerWidth / 800])
	.angle([-17]);
$: path = geoPath(projection);

var color = scaleThreshold()
	.domain(candidates[candidate]["breaks"])
	.range(colours);

tracts.features.map((item) => {
	item.properties[candidate]
		? (item.properties.color = color(item.properties[candidate]))
		: (item.properties.color = "white");
});

</script>




<div class="container" id={candidate} bind:offsetWidth={divWidth}>
	<svg width={innerWidth} {height}>

		<text id="year-label" x="5" y="22">{candidates[candidate].name} {candidates[candidate].year}</text>

		{#each tracts.features as data}
			<path id="ct" d={path(data)} fill={data.properties.color} />
		{/each}

		
	</svg>
</div>

<style>
	.container {
		max-width: 350px;
		width: 100%;
		/* background-color: aqua; */
		border: solid 1px #f6f6f6;;
	}

	#fm-back {
		stroke: rgb(0, 0, 0);
		stroke-width: 5px;
		opacity: 0.08;
		fill-opacity: 0;
	}
	#ct {
		stroke: rgb(237, 237, 237);
		stroke-width: 1px;
	}
	#fm {
		stroke: rgb(36, 36, 36);
		stroke-width: 1 px;
		fill-opacity: 0;
	}

	#year-label {
		font-size: 14px;
		fill: rgb(103, 103, 103);
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>