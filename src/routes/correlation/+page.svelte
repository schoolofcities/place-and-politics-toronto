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

		<h1>Which Candidates Are Most Alike?</h1>
		<h3><a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> December 12, 2022</h3>

		<div id="mini-line"></div>

	</div>



	<div class="text">
		<p>
			In our two previous posts we used maps to show that there is remarkable continuity in the geography of support for different types of candidates across the 25 years and eight elections since Toronto’s 1997 amalgamation. Support for progressive and conservative candidates is geographically concentrated. These patterns suggest that we can think more systematically about the relationships between candidates’ support bases across time.
		</p>
		<p>
			In this post we visualize which mayoral candidates are most alike and most unalike based on their geographic distribution of support. We do this by computing the correlation between all mayoral candidates who have received at least 5% of the vote in elections from 1997 to 2022. Specifically, we compute Pearson correlation coefficients between all candidates. These values range between -1.0 (strongest possible negative correlation) and 1.0 (strongest possible positive correlation).
		</p>
		<p>
			The chart below initially links those candidates who are most similar (correlation coefficient 0.75 and greater). We can see strong similarity between candidates shown in our previous post on the right (e.g. the Ford brothers, Tory's two recent elections) and on the left (e.g. Penalosa, Keesemat, Chow, and Gomberg).
		</p>
		<p>	
			The slider allows for filtering different correlation values. For example, moving it all the to the left side will show those who are least alike.
		</p>

	</div>

	<div id="iframe-cor">
		<iframe width="100%" height="553" frameBorder="0"
		src="https://observablehq.com/embed/19651c303241ff66?cells=viewof+thresholds%2Cch"></iframe>
	</div>

	

	<!-- <div>
		<div bind:this={animationRef}></div>
	</div>

	<iframe width="100%" height="380" frameborder="0"
  src="https://observablehq.com/embed/@jamaps/canadas-population-by-longitude?cells=b1"></iframe> -->

	<div class="text">
		<p>
		The above chart shows overall linkages, but it's a bit difficult to drill into specific candidates. Below, you can select and focus on mayoral candidate from a specific election year. Once selected, it will display a map of their electoral support across the city, as well as a list of candidates from other elections ranked by their similarity.
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
			This post uses the same historical neighbourhood-scale (census tract) election results as previous posts in this series. The correlation coefficients were computed in R.
		</p>
		<p>
		
		</p>
	</div>

</div>

	
</main>

<style>

	#iframe-cor {
		padding: 0px;
		margin: 0px;
		width: 550px;
		margin: 0 auto;
		height: 450px;
		overflow-y: hidden;
	}

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
