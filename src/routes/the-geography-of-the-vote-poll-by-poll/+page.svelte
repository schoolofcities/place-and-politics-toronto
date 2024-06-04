<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import Bar from "../lib/Bar.svelte";	
	import Turnout from "../lib/Turnout.svelte";
	import Map from "../lib/Map.svelte";	
    import WebCard from "../assets/web-card-1.png";
	import '../styles.css';

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

    <title>Place and Politics in Toronto</title>
    <meta name="description" content="Mapping the 2022 Toronto Election.">
    <meta name="author" content="Zack Taylor & Jeff Allen">

    <meta property="og:title" content="Place and Politics in Toronto" />
    <meta name="og:description" content="Mapping the 2022 Toronto Election" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/the-geography-of-the-vote-poll-by-poll" />
    <meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/routes/assets/web-card-1.png" />
    <meta property="og:locale" content="en_CA">

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="https://schoolofcities.github.io/place-and-politics-toronto/the-geography-of-the-vote-poll-by-poll" />
    <meta name="twitter:creator" content="@JeffAllenMaps" />
    <meta name="twitter:title" content="Place and Politics in Toronto" />
    <meta name="twitter:description" content="Mapping the 2022 Toronto Election" />
    <meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/routes/assets/web-card-1.png" />

</svelte:head>



<Top/>

<main>

	<!-- <UnderConstruction/> -->
	
	<div class="title">

		<h4>Place & Politics in Toronto - Part 1</h4>

		<div id="mini-line"></div>

		<h1>The geography of the vote, poll by poll</h1>
		<h3><a href="https://politicalscience.uwo.ca/people/faculty/full-time_faculty/zack_taylor.html">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> November 2, 2022</h3>

		<div id="mini-line"></div>

	</div>

	<div class="text">
		<p>
			It was, as most Torontonians expected, a <span style="background-color: #a7c9ff">John Tory</span> landslide in the October 24, 2022 election. Tory steamrolled over his opponents with <span style="background-color: #a7c9ff">342,158 votes</span> and <span style="background-color: #a7c9ff">62.0%</span> of votes cast. The runner up, <span style="background-color: #b3e5b2">Gil Peñalosa</span>, ended election night far behind, with <span style="background-color: #b3e5b2">17.8%</span> and <span style="background-color: #b3e5b2">98,525 votes</span>. Insurgent third-place candidate <span style="background-color: #f0b7b6">Chloe Brown</span> finished with <span style="background-color: #f0b7b6">6.3%</span> and <span style="background-color: #f0b7b6">34,821 votes</span>.
		</p>

		<div class="bar">
			<Bar/>
		</div>
	</div>

	<div class="text">
		<p>
			Voter turnout in 2022 was a record low. Fewer people cast votes for mayor than in any election since amalgamation in 1997, even though the city has added over 400,000 new residents between 1997 and 2022.
		</p>
		<div class="turnout">
			<Turnout/>
		</div>
	</div>

	<div class="text">
		<p>
			The lopsided citywide results tell us a great deal about the nature of political competition in Toronto, not least the power of incumbency advantage and the extent to which voters appear to be unenthused by the options on the ballot paper. 
		</p>
		<p>
			Perhaps more interesting is the geography of the vote - which candidates did better or worse in different parts of the city. This blog series on Place and Politics in Toronto will explore the geography of the vote and what it means for Torontonians. In this first post, we begin by mapping the geography of candidate support.
		</p>
		<p>
			We’ve created our maps from the poll-by-poll results, which Elections Toronto makes available several days after the election. In 2022, citizens could cast ballots at one of 1,460 poll locations on election day, each of which has a corresponding area that range in size from single apartment buildings to areas covering several city blocks. These offer much more geographic detail than ward-level results that are made available on election night. 
		</p>
		<p>	
			One caveat of mapping results by polls is that these vote counts do not include those cast at ward or citywide advance polls. (About 24% of vote were cast prior to election day. About 26% of Tory voters cast their votes in advance, versus 24% for Peñalosa. Only 8.3% of Brown’s votes were cast in advance; her support materialized on October 24.)
		</p>
		<p>
			We invite you to zoom in on the maps to see how your polling area voted. 
		</p>
	</div>

	<Map candidate = "tory"/>

	<div class="text">
		<p>
			While John Tory did well in almost all parts of the city, he did best in the City’s geographic centre - the neighbourhoods located north of the core along the Yonge subway line, from Rosedale and Forest Hill to Hog’s Hollow and the Bridle Path - and also in central Etobicoke and parts of Scarborough. 
		</p>
	</div>

	<Map candidate = "penalosa"/>

	<div class="text">
		<p>
			Peñalosa generally did best where Tory did worst: in core neighbourhoods, especially west of downtown and around the University of Toronto. He also had the greatest share of votes in the poll that covered York University at the City’s northern border as well as the poll that encompasses the Toronto Islands.
		</p>
	</div>

	<Map candidate = "brown"/>

	<div class="text">
		<p>
			Brown’s support was similar to Peñalosa’s, with more support in older downtown neighbourhoods and less in Toronto’s wealthy inner-suburbs. Different to Peñalosa however, Brown received a greater share of her votes in parts of Scarborough and Etobicoke.
		</p>
	</div>

	<Map candidate = "margin"/>

	<div class="text">
		<p>
			At the level of individual polls, the election was competitive only in core neighbourhoods. In almost every other part of the City the winner won by a wide margin.
		</p>
	</div>

	<Map candidate = "race"/>

	<div class="text">
		<p>
			Looking beyond the voter margin to see which candidates placed first and second, we see that in most parts of the City it was a race between Tory and Peñalosa. In the central Davenport, Parkdale-High Park, and University-Rosedale wards, Peñalosa edged Tory; in most other parts of the city, Peñalosa came second to Tory. In northwest Etobicoke and northeast Scarbough, however, we see that Peñalosa slipped to third place, behind Brown. 
		</p>
		<p>
			What do these patterns mean? In the next post in our series on Place and Politics in Toronto we’ll explore how these patterns are related to Toronto’s social and economic geography.
		</p>
	</div>

	

	<div id="mini-line"></div>

	<div class="info">
		<h3>Data Sources:</h3>
		<p>
			Official <a href="https://open.toronto.ca/dataset/election-results-official/">election results</a> and the <a href="https://www.toronto.ca/city-government/elections/city-elections/voting-places/">voting subdivsions</a> (poll catchment areas) were downloaded from the City of Toronto. The code and data used to build this page and its graphics are on <a href="https://github.com/schoolofcities/place-and-politics-toronto">GitHub</a>.
			<br><br>
		</p>
	</div>

</main>
