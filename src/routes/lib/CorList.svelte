<script>

    import candidateCor from "../data/candidate_links.json"

    import {interpolateRdBu} from "d3";

    export let candidate;

    import {candidateStore} from "../lib/stores/stores.js";

    var links = candidateCor.links;

    $: test = links.filter(d => d.source === $candidateStore || d.target === $candidateStore)

    $: test.map((item) => {
		item.source === $candidateStore
			? (item["compare"] = item.target)
			: (item["compare"] = item.source);
	});

    $: data = test.map(d => ({ 
        compare: d["compare"],
        value: d.value,
        colour: interpolateRdBu((d.value + 1) / 2)
    }));

    $: data.sort((a, b) => {
        return b.value - a.value;
    });

    function candidateSelect(c) {
        console.log(c);
        $candidateStore = c;
    }

</script>



<svg width=200 height=400>
   
    <text class="label" x="10" y="10">
        Candidates ranked from most 
    </text>
    <text class="label" x="10" y="25">
        to least similar
    </text>

    {#each data as c, i}
        <rect class="box" width="50" height="17" x="10" y={33 + i * 18} style="fill:{c.colour};"></rect>
	{/each}

    {#each data as c, i}
        <rect class="box" width="130" height="17" x="61" y={33 + i * 18} style="fill:{c.colour};"></rect>
	{/each}

    {#each data as c, i}
        <text class="label" x="67" y={47 + i * 18}>{c.compare}</text>
	{/each}

    {#each data as c, i}
        {#if c.value >= 0}
            <text class="label" x="24" y={47 + i * 18}>{c.value.toFixed(2)}</text>
        {:else}
            <text class="label" x="20.5" y={47 + i * 18}>{c.value.toFixed(2)}</text>
        {/if}
	{/each}

    {#each data as c, i}
        <rect class="select" width="181" height="17" x="10" y={33 + i * 18} on:click|once={candidateSelect(c.compare)}></rect>
	{/each}

    <rect class="bg" width="183" height="361" x="9" y="32"></rect>

</svg>



<style>

    .box {
        stroke: #ffffff;
        opacity: 0.33
    }

    .bg {
        fill: none;
        stroke: #cecece;
    }

    .select {
        fill: #ffffff45;
        stroke: black;
        opacity: 0;
    }
    .select:hover {
        cursor: pointer;
        opacity: 1;
    }

	.label {
		font-size: 13px;
		fill: #383838;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}

</style>
