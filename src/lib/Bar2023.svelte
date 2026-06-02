<script>

	const votePercent = {
        "Chow": 37.17,
        "Bailao": 32.46,
        "Other": 30.37
    }

	const margin = { top: 1, bottom: 1, left: 1, right: 1 };
	let divWidth;
	const height = 90;

	$: innerWidth = divWidth - margin.left - margin.right;

	$: boxes = [
		[0, votePercent["Chow"] / 100 * innerWidth], 
		[votePercent["Chow"] / 100 * innerWidth,
        votePercent["Bailao"] / 100 * innerWidth],
        [(votePercent["Chow"] / 100 + votePercent["Bailao"] / 100 )  * innerWidth, votePercent["Other"] / 100 * innerWidth]
	];

</script>



<div id="container" class="svg-container" bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height} class="svg-content">
		<g transform={`translate(${margin.left},${margin.top})`}>
			<rect x={boxes[0][0]} y="10" width={boxes[0][1]} height="20"
			style="fill:#c27dcf;stroke:white;stroke-width:1;" />
			<rect x={boxes[1][0]} y="10" width={boxes[1][1]} height="20"
			style="fill:#94b956;stroke:white;stroke-width:1;" />
			<rect x={boxes[2][0]} y="10" width={boxes[2][1]} height="20"
			style="fill:#bec2d4;stroke:white;stroke-width:1;" />
		</g>
	</svg>
</div>



<style>

	#container {
			padding-left: 0px;
			width: 100%;
		}

</style>
