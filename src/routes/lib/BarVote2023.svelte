<script>

    const margin = { top: 1, bottom: 1, left: 1, right: 1 };
	const height = 200;
    let divWidth;

    let results = [
        {
            "name": "Chow",
            "votes": 269372,
            "mail": 14273,
            "colour": "#83009c"
        },
        {
            "name": "Bailão",
            "votes": 235175,
            "mail": 3222,
            "colour": "#68983b"
        },
        {
            "name": "Saunders",
            "votes": 62167,
            "mail": 2993,
            "colour": "#1f2e69"
        }, 
        {
            "name": "Furey",
            "votes": 35899,
            "mail": 1172,
            "colour": "#117c83"
        }, 
        {
            "name": "Matlow",
            "votes": 35572,
            "mail": 2957,
            "colour": "#00a182"
        }, 
        {
            "name": "Hunter",
            "votes": 21229,
            "mail": 1313,
            "colour": "#00689f"
        }, 
        {
            "name": "Brown",
            "votes": 18831,
            "mail": 667,
            "colour": "#b94141"
        }, 
        {
            "name": "Bradford",
            "votes": 9254,
            "mail": 794,
            "colour": "#00567b"
        }, 
        {
            "name": "Other",
            "votes": 37139,
            "mail": 726,
            "colour": "grey"
        }
    ]

    $: results.forEach(object => {
        object.width = divWidth * object.votes / 100000 - 100;
    });

</script>



<div id="container" class="svg-container" bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height} class="svg-content">
		<g transform={`translate(${margin.left},${margin.top})`}>
            {#each results as r, i}
                <rect x="80" y={17 + i * 20} width={(divWidth - 150) * r.votes / 300000} height="8"
                style="fill:{r.colour}"/>

                <text class="label" x="70" y={25 + i * 20} text-anchor="end">{r.name}</text>

                <text class="label" x={85 + (divWidth - 150) * r.votes / 300000} y={25 + i * 20}>{r.votes.toLocaleString("en-US")}</text>
            {/each}

            <text class="label" x="80" y="{10}">Total Votes For Mayor</text>

            <!-- <text class="label" x="0" y="0" transform="rotate(270,63,51)">Candidate</text> -->
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
