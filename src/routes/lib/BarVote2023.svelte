<script>

    export let voteType;

    const margin = { top: 1, bottom: 1, left: 1, right: 1 };
	const height = 200;
    let divWidth;

    let maxVote = 280000;

    let results = [
        {
            "name": "Chow",
            "total": 269372,
            "mail": 14273,
            "advance": 60441,
            "electionday": 193698,
            "colour": "#83009c"
        },
        {
            "name": "Bailão",
            "total": 235175,
            "mail": 3222,
            "advance": 19212,
            "electionday": 212177,
            "colour": "#68983b"
        },
        {
            "name": "Saunders",
            "total": 62167,
            "mail": 2993,
            "advance": 15378,
            "electionday": 43558,
            "colour": "#1f2e69"
        }, 
        {
            "name": "Furey",
            "total": 35899,
            "mail": 1172,
            "advance": 8203,
            "electionday": 26468,
            "colour": "#117c83"
        }, 
        {
            "name": "Matlow",
            "total": 35572,
            "mail": 2957,
            "advance": 9524,
            "electionday": 22978,
            "colour": "#00a182"
        }, 
        {
            "name": "Hunter",
            "total": 21229,
            "mail": 1313,
            "advance": 5497,
            "electionday": 14348,
            "colour": "#00689f"
        }, 
        {
            "name": "Brown",
            "total": 18831,
            "mail": 667,
            "advance": 2581,
            "electionday": 15563,
            "colour": "#b94141"
        }, 
        {
            "name": "Bradford",
            "total": 9254,
            "mail": 794,
            "advance": 2394,
            "electionday": 6019,
            "colour": "#00567b"
        }, 
        {
            "name": "Other",
            "total": 37139,
            "mail": 726,
            "advance": 6418,
            "electionday": 29458,
            "colour": "grey"
        }
    ]

    let torontoTotal = results.reduce((sum, result) => sum + result[voteType], 0);

</script>



<div id="container" class="svg-container" bind:offsetWidth={divWidth}>
	<svg width={divWidth} {height} class="svg-content">
		<g transform={`translate(${margin.left},${margin.top})`}>

            <!-- <text class="label" x="80" y="{10}">Total Votes</text> -->

            {#each results as r, i}
                <rect x="110" y={17 + i * 20} width={(divWidth - 150) * r["total"] / maxVote} height="8"
                style="fill:  #E3E3E3"/>

                <rect x="110" y={17 + i * 20} width={(divWidth - 150) * r[voteType] / maxVote} height="8"
                style="fill:{r.colour}"/>

                <text class="label" x="100" y={25 + i * 20} text-anchor="end">
                    {r.name} 
                    ({(Math.round(10 * 100 * r[voteType] / torontoTotal) / 10).toFixed(1)}%)
                </text>

                <text class="label" x={113 + (divWidth - 150) * r[voteType] / maxVote} y={25 + i * 20}>{r[voteType].toLocaleString("en-US")}</text>
            {/each}

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
		fill: rgb(20, 20, 20);
	} 

</style>
