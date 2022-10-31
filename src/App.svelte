<script>

	import Top from "./lib/TopSofC.svelte";
	import UnderConstruction from "./lib/UnderConstruction.svelte";
	
	import Bar from "./lib/Bar.svelte";	
	import Map from "./lib/Map.svelte";	
	
	
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

	<UnderConstruction/>
	
	<div class="title">

		<div id="mini-line"></div>

		<h1>The geography of the vote, poll by poll</h1>
		<h3>Zack Taylor and Jeff Allen</h3>

		<div id="mini-line"></div>

	</div>

	

	<div class="text">
		<p>
			It was, as most Torontonians expected, a John Tory landslide in the October 24, 2022 election. Tory steamrolled over his opponents with 342,158 votes and 62% of votes cast. The runner up, Gil Penalosa, ended election night far behind, with 17.8% and 98,525 votes. Insurgent third-place candidate Chloe-Marie Brown finished with 6.3% and 34,821 votes.
		</p>

		<div class="bar">
			<Bar/>
		</div>
	</div>

	

	<div class="text">
		<p>
			Fewer people cast votes for mayor than in any election since amalgamation in 1997, even though the city has added over 400,000 new residents since then. 
		</p>
	</div>

	<div class="text">
		<p>
			The lopsided citywide results tell us a great deal about the nature of political competition in Toronto, not least the power of incumbency advantage and the extent to which voters appear to be unenthused by the options on the ballot paper. 
		</p>
		<p>
			Perhaps more interesting is the geography of the vote - which candidates did better or worse in different parts of the city. This blog series on Place and Politics in Toronto will explore the geography of the vote and what it means for Torontonians. In this first post, we begin by mapping the geography of candidate support.
		</p>
		<p>
			Results for the 25 wards are available on election night. We've created our maps from the poll-by-poll results, which Elections Toronto makes available several days after the election. In 2022, citizens could cast ballots at one of 1,460 locations on election day. The vote counts mapped do not include those cast at advance polls, which cannot be geographically located. (About 24% of vote were cast prior to election day. About 26% of Tory voters cast their votes in advance, versus 24% for Penalosa. Only 8.3% of Brown's votes were cast in advance; her support materialized on October 24.)

		</p>
	</div>

	
	<Map candidate = "tory"/>


	<div class="text">
		<p>
			While John Tory did well in almost all parts of the city, he did best in the City's geographic centre - the neighbourhoods located north of the core along the Yonge subway line, from Rosedale and Forest Hill to Hog's Hollow and the Bridle Path - and also in central Etobicoke and parts of Scarborough. 

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
		font-size: 17px;
		margin: auto;
		max-width: 694px;
		width: calc(100% - 50px);
		padding: 25px;
		line-height: 160%;
		text-align: left;
	}

	.bar {
		text-align: center;
		height: 25px;
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
