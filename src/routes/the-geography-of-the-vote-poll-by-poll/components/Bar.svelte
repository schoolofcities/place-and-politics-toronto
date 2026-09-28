<script>

	const votePercent = {
        "Tory": 62,
        "Penalosa": 17.9,
        "Brown": 6.3,
        "Other": 13.8
    }

	const margin = { top: 1, bottom: 1, left: 1, right: 1 };
	let divWidth;
	const height = 90;

	$: innerWidth = divWidth - margin.left - margin.right;

	$: boxes = [
		[0, votePercent["Tory"] / 100 * innerWidth], 
		[votePercent["Tory"] / 100 * innerWidth,
        votePercent["Penalosa"] / 100 * innerWidth],
		[(votePercent["Tory"] / 100 + votePercent["Penalosa"] / 100) * innerWidth, votePercent["Brown"] / 100 * innerWidth],
        [(votePercent["Tory"] / 100 + votePercent["Penalosa"] / 100 + votePercent["Brown"] / 100)  * innerWidth, votePercent["Other"] / 100 * innerWidth]
	];

</script>



<div id="container" class="svg-container" bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height} class="svg-content">
		<g transform={`translate(${margin.left},${margin.top})`}>
			<rect x={boxes[0][0]} y="10" width={boxes[0][1]} height="20"
			style="fill:#77a5ff;stroke:white;stroke-width:1;" />
			<rect x={boxes[1][0]} y="10" width={boxes[1][1]} height="20"
			style="fill:#8acc84;stroke:white;stroke-width:1;" />
			<rect x={boxes[2][0]} y="10" width={boxes[2][1]} height="20"
			style="fill:#e1908e;stroke:white;stroke-width:1;" />
            <rect x={boxes[3][0]} y="10" width={boxes[3][1]} height="20"
			style="fill:#cccccc;stroke:white;stroke-width:1;" />
		</g>
	</svg>
</div>



<style>

	#container {
			padding-left: 0px;
			width: 100%;
		}

</style>
