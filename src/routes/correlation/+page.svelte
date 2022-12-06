<script>

	import Top from "../lib/TopSofC.svelte";
	import '../styles.css';

	import candidateLinks from "../data/candidate_links.json"
	import ctWithResults from "../data/ctWithResults.geo.json";

	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import MapMini from "../lib/MapMini.svelte";
	
	import Select from 'svelte-select';

	import { onMount } from 'svelte'
 	import { Runtime, Inspector } from '@observablehq/runtime'
 	import notebook from '@jamaps/force-directed-graph'
	

	import * as d3 from "d3"

	var colours = ["#deebfd", "#a7c9ff", "#77a5ff", "#507fff", "#3d53fb"];

	let animationRef

	onMount(() => {
		const runtime = new Runtime()
		runtime.module(notebook, name => {
			if (name === "chart") {
				return new Inspector(animationRef)
			}
		})
	})
    
	let	candidates = candidateLinks.nodes.map(obj => obj.id);
	let candidate = "Tory 2022"
	function candidateSelect(e) {
		candidate = e.detail.value;
	}
	$: console.log(candidate);

	

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
			Beep boop.
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
		Beep boop.
		</p>
	</div>

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

	<div class="mapSmall">
		<MapMini candidate = {"pctpitfield2006"} tracts={ctWithResults} colours = {colours}/>
	</div>

	
</main>


<style>

.select {
		z-index: 99;
		width: 150px;
		font-family: 'Roboto', sans-serif;
		font-size: 14px;
		opacity: 0.95;
		border-right: 2px solid #0D534D;
		--padding: 0px 0px 0px 7px;
		--border: 1px solid #c8c8c8;
		--borderRadius: 0px;
		--height: 28px;
		--borderFocusColor: #0D534D;
		--itemColor: black;
		--itemHoverBG: #F1C500;
		--itemIsActiveBG: #0D534D;
		--listBorderRadius: 0px;
		--itemFirstBorderRadius: 0px;
		--itemPadding: 0px 0px 0px 10px;
		--itemMargin: 0px;
		--inputColor: white;
		--borderHoverColor: #0D534D;
		--indicatorWidth: 20px;
		--indicatorTop: 4px;
		--indicatorColor: #0D534D;
		--indicatorRight: 3px;
	}


</style>
