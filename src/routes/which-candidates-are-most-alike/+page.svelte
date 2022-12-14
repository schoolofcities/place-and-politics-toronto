<script>

	import Top from "../lib/TopSofC.svelte";
	import '../styles.css';
	import candidateLinks from "../data/candidate_links.json"
	import candidateInfo from "../data/candidate_info.json";
	import ctWithResults from "../data/ctWithResults.geo.json";

	import UnderConstruction from "../lib/UnderConstruction.svelte";

	import MapMiniCor from "../lib/MapMiniCor.svelte";
	import CorList from "../lib/CorList.svelte";
	import Select from 'svelte-select';

	import { onMount } from 'svelte'
 	import { Runtime, Inspector } from '@observablehq/runtime'
 	import notebook from '@jamaps/force-directed-graph'

	import {candidateStore} from "../lib/stores/stores.js";
	
	console.log($candidateStore)

	// let candidate = "Tory 2022";

	// let animationRef

	// onMount(() => {
	// 	const runtime = new Runtime()
	// 	runtime.module(notebook, name => {
	// 		if (name === "chart") {
	// 			return new Inspector(animationRef)
	// 		}
	// 	})
	// })
    
	let toggled = false;
	let	candidates = candidateLinks.nodes.map(obj => obj.id);
	
	function candidateSelect(e) {
		$candidateStore = e.detail.value;
		toggled = !toggled;
	}

	$: candidateText = candidateInfo[$candidateStore].text;
	
	$: candidateTitle = candidateInfo[$candidateStore].fullname;

	$: candidateResult = candidateInfo[$candidateStore].won + " the " + candidateInfo[$candidateStore].year + " election with <span id='percent'>" + candidateInfo[$candidateStore].voteshare + "%</span> of the vote citywide";

	$: imageLink = 'candidate-photos/' +  candidateInfo[$candidateStore].image + '.png';

	let barChartWidth;

	$: barWidth = candidateInfo[$candidateStore].voteshare * barChartWidth / 100

</script>



<svelte:head>

	<link
		href="https://fonts.googleapis.com/css2?family=Bitter&family=Playfair+Display&display=swap"
		rel="stylesheet"
	/>
	<link
		href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&family=Source+Serif+Pro&display=swap"
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

		<h4>Place & Politics in Toronto - Part 4</h4>

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
		<!-- <p>
			The chart below initially links those candidates who are most similar (correlation coefficient 0.75 and greater). We can see strong similarity between candidates shown in our previous post on the right (e.g. the Ford brothers, Tory's two recent elections) and on the left (e.g. Penalosa, Keesemat, Chow, and Gomberg).
		</p>
		<p>	
			The slider allows for filtering different correlation values. For example, moving it all the to the left side will show those who are least alike.
		</p> -->

	</div>

	<!-- <div id="iframe-cor">
		<iframe width="100%" height="553" frameBorder="0"
		src="https://observablehq.com/embed/19651c303241ff66?cells=viewof+thresholds%2Cch"></iframe>
	</div> -->

	<!-- <div>
		<div bind:this={animationRef}></div>
	</div>

	<iframe width="100%" height="380" frameborder="0"
  src="https://observablehq.com/embed/@jamaps/canadas-population-by-longitude?cells=b1"></iframe> -->

	<div class="text">

		<p>
			Below, you can select and focus on mayoral candidate from a specific election year. Once selected, it will display a map of their electoral support across the city, as well as a list of candidates from other elections ranked by their similarity.
		</p>
		
	</div>

	<div id="mini-line"></div>


	<div class="select">
		<Select 
			items={candidates} 
			value={$candidateStore}
			isSearchable={false}
			isClearable={false}
			on:select={candidateSelect}
		>
		</Select>
	</div>

	<div class="candidate-info">

		<div id="wrapper-info">

			<div class="candidate-text">

				<div class="candidate-title">
					{candidateTitle}
				</div>

				<div class="candidate-body-web">
					{candidateInfo[$candidateStore].won} the <span id="yearText">{candidateInfo[$candidateStore].year}</span> election with <span id="votePercent">{candidateInfo[$candidateStore].voteshare}%</span> of the vote citywide.
				</div>

				<div id="barChart" bind:offsetWidth={barChartWidth}>
					<svg width={barWidth} height=20>
						<rect class="barPercent" width={barWidth} height="10" x="0" y="0"></rect>
					</svg>
				</div>
				
				<div class="candidate-body-web">
					{candidateText}
				</div>
			</div>

			<img class="face" src={imageLink} alt={candidateInfo[$candidateStore].fullname} width="183" height="183">
			
		</div>

		<!-- <div class="candidate-body-mobile">
			{candidateText}
		</div> -->

	</div>

	
	<div class="text">

		<div class="plotGrid">
			
			<div class="mapCorSmall">
				{#key toggled}
					<MapMiniCor candidate = {$candidateStore} tracts={ctWithResults} />
				{/key}
			</div>

			<div class="corplot">
				{#key toggled}
					<CorList candidate = {$candidateStore}/>
				{/key}
			</div>
		</div>

	</div>

	<div id="mini-line"></div>

	<!-- <CorList candidate = {candidate}/> -->

	<div class="info">
		<h3>Data Sources:</h3>
		<p>
			This post uses the same historical neighbourhood-scale (census tract) election results as previous posts in this series. The correlation coefficients were computed in R.
		</p>
		<p>
		
		</p>
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

	.candidate-info {
		margin: 0 auto;
		max-width: 670px;
		padding-left: 0px;
		padding-right: 25px;
		padding-bottom: 15px;
		padding-top: 50px;
	}

	#barChart {
		background-color: #deebf7;
		height: 10px;
		margin-top: 10px;
		/* margin-left: 25px; */
		width: calc(100%);
		z-index: -999;
	}

	.barPercent {
        fill: #9ecae1;
    }



	#wrapper-info {
		padding-top: 20px;
		overflow: hidden;
		padding-left: 1px;
	}

	.face {
		padding-right: 30px;
		overflow: hidden;
		float: right;
	}

	@media (max-width: 709px) {
		.face {
			float: left;
			padding-left: 25px;
		}
	}

	.candidate-text {
		float:left;
		font-family: "Source Serif Pro", serif;
		font-size: 15px;
		padding-left: 25px;
		padding-right: 25px;
		padding-bottom: 20px;
		max-width: 400px;
		min-width: 200px;
		line-height: 160%;
    	text-align: left;
	}

	#votePercent {
		text-decoration: none;
		color: black;
		/* text-decoration-color: */
		border-bottom: 2px solid #9ecae1;	
	}

	#yearText {
		font-weight: 900;
	}

	.candidate-title {
		border-bottom: 1px solid #dedede;
		font-family: 'Roboto', sans-serif;
		font-weight: 900;
	}

	.candidate-body-web {
		padding-top: 10px;
	}
	/* .candidate-body-mobile {
		display: none;
		font-family: "Source Serif Pro", serif;
		font-size: 15px;
		padding-left: 0px;
		line-height: 160%;
    	text-align: left;
	}

	@media (max-width: 500px) {
		.candidate-body-mobile {
			display:inherit;
			padding-top: 20px;
			font-size: 15px;
			line-height: 160%;
		}
		.candidate-body-web {
			display: none;
		}
	} */

	.plotGrid {
		margin: auto;
		/* overflow: hidden; */
		padding-bottom: 42px;
		max-width: 660px;
		width: 100%;
		/* display: grid; */
		gap: 4px 2px;
		/* grid-template-columns: repeat(2, 1fr); */
	}

	.mapCorSmall {
		/* background-color: #3d53fb; */
		/* z-index: -10; */
		float: left;
		/* margin: auto; */
		/* padding: -10px; */
		padding-right: 10px;
		max-width: 420px;
		width: 420px;
		margin: 0 auto;
		/* border: solid 1px #f4f4f4; */
	}

	.corplot {
		/* background-color: #3d53fb; */
		/* z-index: -10; */
		overflow: hidden;
		padding: -10px;
		max-width: 220px;
		width: 220px;
		/* margin: 0 auto; */
		/* border: solid 1px #f4f4f4; */
	}


	.select {
		margin:0 auto;
		/* float: left; */
		margin-top: 30px;
		margin-bottom: -20px;
		z-index: 999;
		width: 200px;
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
