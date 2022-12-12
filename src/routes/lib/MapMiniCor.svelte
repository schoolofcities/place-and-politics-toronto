<script context="module">
	export const router = true
</script>


<script>

	import { geoPath, geoMercator, scaleThreshold } from "d3";
	import Wards from "../data/wards.geo.json";
	import candidateInfo from "../data/candidate_info.json";

	// export var colours;
	export let candidate;
	export let tracts;

	let colours = ['#fff','#deebf7','#c6dbef','#9ecae1','#6baed6','#4292c6','#2171b5','#08519c','#08306b','#021530']
	
	// ['#fcfcf7','#fff7bc','#fee391','#fec44f','#fe9929','#ec7014','#cc4c02','#8c2d04', "#521a02", "#1f0a01"];
	
	// ['#fff','#efedf5','#dadaeb','#bcbddc','#9e9ac8','#807dba','#6a51a3','#4a1486',"#350c63", "#17032e"]
	
	
	
	// ["#fff2b6", "#ece6af", "#d8daa8", "#c1cda1", "#a7bf99", "#88af91", "#609f89", "#008c80"];

	var breaks = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9];

	$: candidateVar = candidateInfo[candidate].ctid;

	let divWidth = 420;
	$: innerWidth = divWidth;
	$: height = 10 + innerWidth / 1.55;

	$: projection = geoMercator()
		.center([-78.155 - 0.00239*innerWidth + 0.000001125*innerWidth**2, 43.54 + 0.00045*innerWidth - 2.5e-7*innerWidth**2])
		.scale([82000 * innerWidth / 800])
		.angle([-17]);
	$: path = geoPath(projection); 


	var ct = tracts.features;

	var color = scaleThreshold()
		.domain(breaks)
		.range(colours);

	$: ct.map((item) => {
		item.properties[candidateVar]
			? (item.properties["colour"] = color(item.properties[candidateVar]))
			: (item.properties["colour"] = "white");
	});

</script>



<div bind:offsetWidth={divWidth}>


	<svg width={innerWidth} {height} id="back">

		

		<text class="label" x="12" y="22">{"Map of electoral support for " + candidateInfo[candidate].fullname + " in " + candidateInfo[candidate].year}</text>

		{#each ct as data}
			<path class="ct" d={path(data)} fill={data.properties["colour"]} />
		{/each}

		{#each Wards.features as data}
			<path class="wardwhite" d={path(data)} />
		{/each}

		{#each Wards.features as data}
			<path class="ward" d={path(data)} />
		{/each}

		<text class="label" x="25" y="245">% of the vote by CT</text>

		<text class="label" x="215" y="275">{"100%"}</text>
		<text class="label" x="175" y="275">{breaks[7]*100 + "%"}</text>
		<text class="label" x="135" y="275">{breaks[5]*100 + "%"}</text>
		<text class="label" x="95" y="275">{breaks[3]*100 + "%"}</text>
		<text class="label" x="55" y="275">{breaks[1]*100 + "%"}</text>
		<text class="label" x="20" y="275">{"0%"}</text>

		<rect class="box" width="202" height = "12" x="24" y="249" style="fill:black; stroke: none;"></rect>

		<rect class="box" width="20" height = "10" x="205" y="250" style="fill:{colours[9]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="185" y="250" style="fill:{colours[8]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="165" y="250" style="fill:{colours[7]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="145" y="250" style="fill:{colours[6]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="125" y="250" style="fill:{colours[5]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="105" y="250" style="fill:{colours[4]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="85" y="250" style="fill:{colours[3]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="65" y="250" style="fill:{colours[2]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="45" y="250" style="fill:{colours[1]}; stroke: white;"></rect>
		<rect class="box" width="20" height = "10" x="25" y="250" style="fill:{colours[0]}; stroke: white;"></rect>
		
	</svg>
</div>



<style>

	img {
		opacity: 0.9;
	}

	#back {
		z-index: 0;
		/* background-color: grey; */
	}

	.ct {
		stroke: rgb(237, 237, 237);
		stroke-width: 1px;
		opacity: 0.9;
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

	.label {
		font-size: 13px;
		fill: rgb(56, 56, 56);
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>
