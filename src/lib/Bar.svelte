<script>

	let city = "toronto"

	const cities = {

		"toronto": {
			"Tory": 62,
			"Penalosa": 17.9,
			"Brown": 6.3,
            "Other": 13.8
		}
	}

	const margin = { top: 1, bottom: 1, left: 1, right: 1 };
	let divWidth;
	const height = 90;

	$: innerWidth = divWidth - margin.left - margin.right;

	$: boxes = [
		[0, cities[city]["Tory"] / 100 * innerWidth], 
		[cities[city]["Tory"] / 100 * innerWidth,
        cities[city]["Penalosa"] / 100 * innerWidth],
		[(cities[city]["Tory"] / 100 + cities[city]["Penalosa"] / 100) * innerWidth, cities[city]["Brown"] / 100 * innerWidth],
        [(cities[city]["Tory"] / 100 + cities[city]["Penalosa"] / 100 + cities[city]["Brown"] / 100)  * innerWidth, cities[city]["Other"] / 100 * innerWidth]
	];

    $: console.log(boxes);

</script>

<div id="container" class="svg-container" bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height} class="svg-content">
		<g transform={`translate(${margin.left},${margin.top})`}>
			<rect x={boxes[0][0]} y="0" width={boxes[0][1]} height="20"
			style="fill:#507fff;stroke:white;stroke-width:1;" />
			<rect x={boxes[1][0]} y="0" width={boxes[1][1]} height="20"
			style="fill:#00A189;stroke:white;stroke-width:1;" />
			<rect x={boxes[2][0]} y="0" width={boxes[2][1]} height="20"
			style="fill:#6FC7EA;stroke:white;stroke-width:1;" />
            <rect x={boxes[3][0]} y="0" width={boxes[3][1]} height="20"
			style="fill:#6FC7EA;stroke:white;stroke-width:1;" />
		</g>
	</svg>
</div>


<style>

	#container {
			padding-left: 0px;
			width: 100%;
		}

</style>