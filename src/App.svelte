<script>

	import Top from "./lib/TopSofC.svelte";
	import UnderConstruction from "./lib/UnderConstruction.svelte";
	
	import Map from "./lib/Map.svelte";

	let coloursDiv = ["#DC4633", "#ee9d78", "#f2dfce", "#7eb4b3", "#007fa3"];
	
	
	
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
	<link href='https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.css' rel='stylesheet' />
</svelte:head>





<Top/>

<main>
	
	<div class="title">

		<div id="mini-line"></div>

		<h1>Mapping Toronto's 2022 Mayoral Election</h1>
		
		<h3>Subtitle</h3>
		<br>
		<h3>Authors, Date</h3>

		<div id="mini-line"></div>

	</div>

	

	<div class="text">
		<p>
		Some intro text here
		</p>
		
	</div>

	
	<Map/>


	<div class="text">
		<p>
		Some more text here
		</p>
		
	</div>

	<div id="mini-line"></div>

	<div class="info">
		<h3>Data Sources & More Information</h3>
		<p>
		etc etc etc
		</p>
			
		
	</div>


</main>


<style>
	@font-face {
		font-family: TradeGothicBold;
		src: url("./assets/Trade Gothic LT Bold.ttf");
	}
	:root {
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
			Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	:global(body) {
		padding: 0px;
		margin: 0px;
		background-color: #fffefd;
	}

	main {
		margin: 0 auto;
		width: 100%;
		min-width: 320px;
		max-width: 1200px;
		position: relative;
	}

	.title {
		margin: auto;
		max-width: 600px;
		width: calc(100% - 50px);
		padding-left: 25px;
		padding-right: 25px;
		margin-top: 100px;
		text-align: center;
		font-family: "Source Serif Pro", serif;
	}
	.title h1 {
		font-weight: normal;
		font-size: 40px;
	}
	.title h3 {
		font-weight: normal;
		font-size: 18px;
	}

	#mini-line {
		margin: auto;
		width: 220px;
		height: 1px;
		background-color: black;
	}

	.text {
		font-family: "Source Serif Pro", serif;
		font-size: 16px;
		margin: auto;
		max-width: 594px;
		width: calc(100% - 50px);
		padding: 25px;
		line-height: 160%;
		text-align: left;
	}
	a {
		text-decoration: none;
		color: #007fa3;
	}

	#bold {
		color: #ed1b00;
		font-weight: bold;	
	}



	.info {
		font-family: "Source Serif Pro", serif;
		font-size: 14px;
		margin: auto;
		max-width: 494px;
		width: calc(100% - 50px);
		padding: 25px;
		line-height: 160%;
		text-align: left;
	}
	
</style>
