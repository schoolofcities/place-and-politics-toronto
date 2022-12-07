<script>

	import Top from "../lib/TopSofC.svelte";
	import '../styles.css';

	import candidateLinks from "../data/candidate_links.json"
	import ctWithResults from "../data/ctWithResults.geo.json";

	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import MapMiniCor from "../lib/MapMiniCor.svelte";
	import CorList from "../lib/CorList.svelte";
	
	import Select from 'svelte-select';

	import { onMount } from 'svelte'
 	import { Runtime, Inspector } from '@observablehq/runtime'
 	import notebook from '@jamaps/force-directed-graph'
	

	import * as d3 from "d3"

	// let animationRef

	// onMount(() => {
	// 	const runtime = new Runtime()
	// 	runtime.module(notebook, name => {
	// 		if (name === "chart") {
	// 			return new Inspector(animationRef)
	// 		}
	// 	})
	// })
    
	let toggled = false
	let	candidates = candidateLinks.nodes.map(obj => obj.id);
	let candidate = "Tory 2022"
	function candidateSelect(e) {
		candidate = e.detail.value;
		toggled = !toggled;
	}

	

</script>





<svelte:head>

	<link
		href="https://fonts.googleapis.com/css2?family=Bitter&family=Playfair+Display&display=swap"
		rel="stylesheet"
	/>
	<link
		href="https://fonts.googleapis.com/css2?family=Roboto&family=Source+Serif+Pro&display=swap"
		rel="stylesheet"
	/>
	<meta
		name="viewport"
		content="width=device-width, initial-scale=1, minimum-scale=1"
	/>

    

</svelte:head>



<Top/>

<main>

	<!-- <UnderConstruction/> -->
	
	<div class="title">

		<h4>Place & Politics in Toronto - Part 3</h4>

		<div id="mini-line"></div>

		<h1>Correlation testing</h1>
		<h3><a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> December 12, 2022</h3>

		<div id="mini-line"></div>

	</div>



	<div class="text">
		<p>
			In our two previous posts we used maps to show that there is remarkable continuity in the geography of support for different types of candidates across the 25 years and eight elections since Toronto’s 1997 amalgamation. Support for progressive and conservative candidates is geographically concentrated. These patterns suggest that we can think more systematically about the relationships between candidates’ support bases across time.
		</p>
		<p>
			In this post we will visualize which mayoral candidates are most alike and most unalike based on their geographic distribution of support.
		</p>

		<!-- <div id="chart">
			<iframe width="100%" height="500" frameborder="0"
		src="https://observablehq.com/embed/@d3/force-directed-lattice?cells=chart"></iframe>
		</div> -->
	</div>

	<!-- <div>
		<div bind:this={animationRef}></div>
	</div>

	<iframe width="100%" height="380" frameborder="0"
  src="https://observablehq.com/embed/@jamaps/canadas-population-by-longitude?cells=b1"></iframe> -->

  	<div id="mini-line"></div>
	<div class="text">
		<p>
		Below you can select a mayoral candidate from a specific election year, and it will display a map of electoral support for the candidate, as well as a list of candidates from other elections ranked by their similarity.
		</p>
		<div class="select">
			<Select 
					items={candidates} 
					value={candidate}
					isSearchable={false}
					isClearable={false}
					on:select={candidateSelect}
				>
			</Select>
		</div>
	
	</div>

	
	<div class="text">

	<div class="mapGrid">
		
		<div class="mapSmall">
			
			{#key toggled}
				<MapMiniCor candidate = {candidate} tracts={ctWithResults} />
			{/key}
		</div>

		<div class="mapSmall">
			<CorList candidate = {candidate}/>
		</div>
	</div>

	<div id="mini-line"></div>

	<div class="info">
		<h3>Data Sources:</h3>
		<p>
			All the maps in this post use a dataset of historical neighbourhood-scale election results that we created with sociologists Daniel Silver of the University of Toronto and Jan Doering of McGill University. We hand-digitized the 1997 and 2000 election results and poll maps, which exist only in paper form, and accessed the 2003 through 2022 election results from the City’s open data site. We then apportioned the results to a common geography, 2021 census tracts, which represent neighbourhood areas of about 4,000 to 7,000 residents. To help orient you, we've overlaid the ward boundaries used since 2018 for reference, even though the city was divided into wards differently in previous years.
		</p>
	</div>

</div>

	

	


</main>


<style>

	.select {
		/* margin:0 auto; */
		z-index: 999999;
		width: 150px;
		font-family: 'Roboto', sans-serif;
		font-size: 14px;
		opacity: 0.95;
		border-right: 2px solid #08519c;
		--padding: 0px 0px 0px 7px;
		--border: 1px solid #c8c8c8;
		--borderRadius: 0px;
		--height: 28px;
		--borderFocusColor: #08519c;
		--itemColor: black;
		--itemHoverBG: #f6cfc3;
		--itemIsActiveBG: #08519c;
		--listBorderRadius: 0px;
		--itemFirstBorderRadius: 0px;
		--itemPadding: 0px 0px 0px 10px;
		--itemMargin: 0px;
		--inputColor: white;
		--borderHoverColor: #9ba1a8;
		--indicatorWidth: 20px;
		--indicatorTop: 4px;
		--indicatorColor: #08519c;
		--indicatorRight: 3px;
	}


</style>
