<script>

    const margin = { top: 1, bottom: 1, left: 1, right: 1 };
	const height = 180;
    let divWidth;

    let results = [
        {
            "year": "2022",
            "votes": 551890
        },
        {
            "year": "2018",
            "votes": 755493
        }, 
        {
            "year": "2014",
            "votes": 981054
        }, 
        {
            "year": "2010",
            "votes": 813984
        }, 
        {
            "year": "2006",
            "votes": 584484
        }, 
        {
            "year": "2003",
            "votes": 692085
        }, 
        {
            "year": "2000",
            "votes": 627309
        }, 
        {
            "year": "1997",
            "votes": 695799
        }
    ]

    $: results.forEach(object => {
        object.width = divWidth * object.votes / 1000000 - 100;
    });

</script>



<div id="container" class="svg-container" bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height} class="svg-content">
		<g transform={`translate(${margin.left},${margin.top})`}>
            {#each results as { votes }, i}
                <rect x="55" y={5 + i * 20} width={(divWidth - 150) * votes / 1000000} height="2"
                style="fill:#1D1D1D;"/>
            {/each}

            {#each results as { year }, i}
                <text class="label" x="20" y={10 + i * 20}>{year}</text>
            {/each}

            {#each results as { votes }, i}
                <text class="label" x={60 + (divWidth - 150) * votes / 1000000} y={10 + i * 20}>{votes.toLocaleString("en-US")}</text>
            {/each}

            <text class="label" x="60" y="170">Total Votes For Mayor</text>

            <text class="label" x="0" y="0" transform="rotate(270,63,51)">Election Year</text>
		</g>
	</svg>
</div>



<style>

	#container {
			padding-left: 0px;
			width: 100%;
		}

    .label {
        font-family: "Roboto", sans-serif;
		font-size: 13px;
		fill: rgb(66, 66, 66);
	} 

</style>
