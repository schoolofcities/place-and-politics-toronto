<script context="module">
	export const router = true
</script>


<script>

import { geoPath, geoMercator, scaleThreshold, window } from "d3";
import Wards from "../data/wards2023adv.geo.json";

// export var colours;
export let variable


const variables = {
	"adv_chow_olivia": {
		"breaks": [20, 30, 40, 50],
		"colours": ["#f5f5f5", "#bcbcbc", "#8c8c8c", "#575757", "#2b2b2b"],
		"title": "Chow advance votes % by ward"
	},
	"chg_chow_olivia": {
		"breaks": [-15,-10,-5,5],
		"colours": ["#dc4633","#e17b6e","#e6b5ae","#ebebeb","#a8c1e4"],
		"title": "% change from early voting to election day"
	},
	"adv_bailao_ana": {
		"breaks": [20, 30, 40, 50],
        "colours": ["#f5f5f5", "#bcbcbc", "#8c8c8c", "#575757", "#2b2b2b"],
		"title": "Bailão advance votes % by ward"
	},
	"chg_bailao_ana": {
		"breaks": [-5,5,15,25],
		"colours": ["#e6b5ae","#ebebeb","#a8c1e4","#5a90dc","#1263d4"],
		"title": "% change from early voting to election day"
	}
}

let divWidth = 320;
$: innerWidth = divWidth;
$: height = innerWidth / 1.75;

$: projection = geoMercator()
	.center([-77.97 - 0.00239*innerWidth + 0.000001125*innerWidth**2, 43.53 + 0.00045*innerWidth - 2.5e-7*innerWidth**2])
	.scale([69000 * innerWidth / 800])
	.angle([-17]);
$: path = geoPath(projection);


let w = Wards.features;

var color = scaleThreshold()
	.domain(variables[variable]["breaks"])
	.range(variables[variable]["colours"]);

w.map((item) => {
	parseFloat(item.properties[variable])
		? (item.properties["color_" + variable]  = color(parseFloat(item.properties[variable])))
		: (item.properties["color_" + variable] = "white");
});

</script>




<div bind:offsetWidth={divWidth}>
	<svg width={innerWidth} {height} id={variable}>

		<text class="label" x="12" y="22">
			{variables[variable].title}
		</text>

		{#each w as data}
			<path class="w" d={path(data)} fill={data.properties["color_" + variable]} opacity=0.97 />
		{/each}

		{#each Wards.features as data}
			<path class="wardwhite" d={path(data)} />
		{/each}

		{#each Wards.features as data}
			<path class="ward" d={path(data)} />
		{/each}

		<!-- <text class="label" x="320" y="185">% of</text>
		<text class="label" x="320" y="200">vote</text> -->
		<text class="label" x="313" y="55">{variables[variable]["breaks"][3] + "%"}</text>
		<text class="label" x="313" y="70">{variables[variable]["breaks"][2] + "%"}</text>
		<text class="label" x="313" y="85">{variables[variable]["breaks"][1] + "%"}</text>
		<text class="label" x="313" y="100">{variables[variable]["breaks"][0] + "%"}</text>
		
		<rect class="box" width="20" height = "15" x="290" y="35" style="fill:{variables[variable].colours[4]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="290" y="50" style="fill:{variables[variable].colours[3]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="290" y="65" style="fill:{variables[variable].colours[2]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="290" y="80" style="fill:{variables[variable].colours[1]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "15" x="290" y="95" style="fill:{variables[variable].colours[0]}; stroke: white;"></rect>

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
		opacity: 0.9;
	}
	.ward {
		stroke: #e6e6e6;
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