<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import MapMini from "../lib/MapMini.svelte";
	import '../styles.css';

	import { onMount } from 'svelte'
 	import { Runtime, Inspector } from '@observablehq/runtime'
 	import notebook from '@jamaps/force-directed-graph'
	

	import * as d3 from "d3"

	var coloursLeft = ["#defde0", "#a6e7bb", "#73d398", "#3cbd73", "#00a64b"];

	var coloursRight = ["#deebfd", "#a7c9ff", "#77a5ff", "#507fff", "#3d53fb"];

	let animationRef

	onMount(() => {
		const runtime = new Runtime()
		runtime.module(notebook, name => {
			if (name === "chart") {
				return new Inspector(animationRef)
			}
		})
	})


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
		<p>
			Beep boop.
		</p>
	</div>

	<div>
		<div bind:this={animationRef}></div>
	</div>

	<iframe width="100%" height="380" frameborder="0"
  src="https://observablehq.com/embed/@jamaps/canadas-population-by-longitude?cells=b1"></iframe>



	
</main>


<style>


</style>
