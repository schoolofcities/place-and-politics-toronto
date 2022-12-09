<script>

    import candidateCor from "../data/candidate_links.json"

    import {interpolateRdBu} from "d3";

    export let candidate;

    var links = candidateCor.links;

    $: test = links.filter(d => d.source === candidate || d.target === candidate)

    $: test.map((item) => {
		item.source === candidate
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

</script>


<svg width=300 height=400>

    <text class="label" x="10" y="22">Candidates ranked by similarity</text>

    

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

	.label {
		font-size: 13px;
		fill: #383838;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
</style>
