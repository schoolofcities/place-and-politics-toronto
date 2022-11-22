<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import Bar from "../lib/Bar.svelte";
	import MapMini from "../lib/MapMini.svelte"
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
    <meta name="description" content="Place and Politics in Toronto">
    <meta name="author" content="Zack Taylor & Jeff Allen">

    <meta property="og:title" content="Place and Politics in Toronto" />
    <meta name="og:description" content="Mapping the 2022 Toronto Election" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/" />
    <meta property="og:image" content={WebCard} />
    <meta property="og:locale" content="en_CA">

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="https://schoolofcities.github.io/" />
    <meta name="twitter:creator" content="@JeffAllenMaps" />
    <meta name="twitter:title" content="Place and Politics in Toronto" />
    <meta name="twitter:description" content="Mapping the 2022 Toronto Election" />
    <meta name="twitter:image" content={WebCard} />

</svelte:head>



<Top/>

<main>

	<!-- <UnderConstruction/> -->
	
	<div class="title">

		<h4>Place & Politics in Toronto - Part 2</h4>

		<div id="mini-line"></div>

		<h1>Toronto's Two Rights</h1>
		<h3><a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> November 26, 2022</h3>

		<div id="mini-line"></div>

	</div>

	<div class="text">
		<p>
			In our <a href="./the-geography-of-the-vote-poll-by-poll">last post</a> we mapped the vote share percentages for the 2022 mayoral candidates by neighbourhood. We found that, in the 2022 election anyway, some neighbourhoods in the city’s core wards were more likely to support Gil Peñalosa than John Tory, while neighbourhoods in wards outside the core more more likely to support John Tory. In fact, the more distant you are from the core, the more likely that Chloe Brown, who received 6.3% support citywide, beat Peñalosa for second place. It would appear that many core voters want something different, politically, than most suburban voters. In future posts we will explore what may be driving this pattern. First, however, we will look back at the geography of past elections to see where particular candidates did best.
		</p>
		<p>
			To do this, we use a dataset of historical neighbourhood-scale election results we created with sociologists Daniel Silver of the University of Toronto and Jan Doering of McGill University. We hand-digitized the 1997 and 2000 election results and poll maps, which exist only in paper form, and accessed the 2003 through 2022 election results from the City’s open data site. We then apportioned the results to a common geography, 2021 census tracts, which represent neighbourhood areas of about 4,000 residents. To help orient you, we overlay the ward boundaries used since 2018 for reference, even though the city was divided into wards differently in previous years.
		</p>
		<p>
			In this post, we will look at the geography of support for candidates often thought of as being on the centre-right or right: John Tory, Jane Pitfield, and the Ford brothers. In the next post we'll look at candidates often thought of as on the left.
		</p>

		
	</div>

	<div class="text">
		<h2>Finding Toryland</h2>
		<p>
			Let’s begin by comparing John Tory’s geography of support in the four elections in which he ran for mayor: 2003, 2014, 2018, and 2022.
		</p>
		
	</div>

	<MapMini candidate = "pcttory_john2022"/>

	<MapMini candidate = "pcttory2018"/>

	


	<div id="mini-line"></div>

	<div class="info">
		<h3>Data Sources:</h3>
		<p>
			Official <a href="https://open.toronto.ca/dataset/election-results-official/">election results</a> and the <a href="https://www.toronto.ca/city-government/elections/city-elections/voting-places/">voting subdivsions</a> (poll catchment areas) were downloaded from the City of Toronto. The code and data used to build this page and its graphics are on <a href="https://github.com/schoolofcities/place-and-politics-toronto">GitHub</a>.
			<br><br>
		</p>
	</div>

</main>
