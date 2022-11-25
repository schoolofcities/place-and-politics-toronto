<script>

import { geoPath, geoMercator, scaleThreshold } from "d3";
import Wards from "../data/wards.geo.json";

// export var colours;
export let candidate;
export let tracts;

console.log(Wards);

const ct = tracts.features;

let colours = ["#deebfd", "#a7c9ff", "#77a5ff", "#507fff", "#3d53fb"]

const candidates = {
	"pcttory_john2022": {
		"breaks": [0.4, 0.5, 0.6, 0.7],
		"name": "John Tory",
		"year": "2022",
		"citywide": "62%"
	},
	"pcttory2018": {
		"breaks": [0.4, 0.5, 0.6, 0.7],
		"name": "John Tory",
		"year": "2018",
		"citywide": "63%"
	},
	"pcttory2014": {
		"breaks": [0.2, 0.3, 0.4, 0.5],
		"name": "John Tory",
		"year": "2014",
		"citywide": "40%"
	},
	"pcttory2003": {
		"breaks": [0.2, 0.3, 0.4, 0.5],
		"name": "John Tory",
		"year": "2003",
		"citywide": "38%"
	}, 
	"pctpitfield2006": {
		"breaks": [0.2, 0.3, 0.4, 0.5],
		"name": "Jane Pitfield",
		"year": "2006",
		"citywide": "30%"
	}
}

let divWidth = 420;
$: innerWidth = divWidth;
$: height = innerWidth / 1.75;

$: console.log(innerWidth)

$: projection = geoMercator()
	.center([-78.15 - 0.00239*innerWidth + 0.000001125*innerWidth**2, 43.54 + 0.00045*innerWidth - 2.5e-7*innerWidth**2])
	.scale([82000 * innerWidth / 800])
	.angle([-17]);
$: path = geoPath(projection);

var color = scaleThreshold()
	.domain(candidates[candidate]["breaks"])
	.range(colours);

ct.map((item) => {
	item.properties[candidate]
		? (item.properties["color_" + candidate]  = color(item.properties[candidate]))
		: (item.properties["color_" + candidate] = "white");
});

</script>



<div id={candidate} bind:offsetWidth={divWidth}>
	<svg width={innerWidth} {height} id={candidate}>

		<text class="label" x="9" y="22">{candidates[candidate].name + " " + candidates[candidate].year + " (" + candidates[candidate].citywide + " of the vote citywide)"}</text>

		{#each ct as data}
			<path class="ct" id={candidate} d={path(data)} fill={data.properties["color_" + candidate]} />
		{/each}

		{#each Wards.features as data}
			<path class="wardwhite" d={path(data)} />
		{/each}

		{#each Wards.features as data}
			<path class="ward" d={path(data)} />
		{/each}

		<text class="label" x="320" y="185">% of</text>
		<text class="label" x="320" y="200">vote</text>
		<text class="label" x="373" y="170">{candidates[candidate]["breaks"][3]*100 + "%"}</text>
		<text class="label" x="373" y="185">{candidates[candidate]["breaks"][2]*100 + "%"}</text>
		<text class="label" x="373" y="200">{candidates[candidate]["breaks"][1]*100 + "%"}</text>
		<text class="label" x="373" y="215">{candidates[candidate]["breaks"][0]*100 + "%"}</text>
		
		<rect class="box" width="20" height = "15" x="350" y="150" style="fill:{colours[4]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="350" y="165" style="fill:{colours[3]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="350" y="180" style="fill:{colours[2]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="350" y="195" style="fill:{colours[1]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="350" y="210" style="fill:{colours[0]}; stroke: white;"></rect>

	</svg>
</div>



<style>

	#fm-back {
		stroke: rgb(0, 0, 0);
		stroke-width: 5px;
		opacity: 0.08;
		fill-opacity: 0;
	}
	.ct {
		stroke: rgb(237, 237, 237);
		stroke-width: 1px;
	}
	.ward {
		stroke: black;
		stroke-width: 1px;
		fill: none;
	}
	.wardwhite {
		stroke: white;
		stroke-width: 0px;
		fill: none;
	}

	#fm {
		stroke: rgb(36, 36, 36);
		stroke-width: 1 px;
		fill-opacity: 0;
	}

	.label {
		font-size: 13px;
		fill: rgb(56, 56, 56);
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>