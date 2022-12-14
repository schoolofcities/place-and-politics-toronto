<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import MapMini from "../lib/MapMini.svelte";
    import WebCard from "../assets/web-card-2.png";
	import '../styles.css';
	import ctWithResults from "../data/ctWithResults.geo.json";

	var coloursRight = ["#deebfd", "#a7c9ff", "#77a5ff", "#507fff", "#3d53fb"];

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

    <title>Place and Politics in Toronto</title>
    <meta name="description" content="Place and Politics in Toronto">
    <meta name="author" content="Zack Taylor & Jeff Allen">

	<meta property="og:title" content="Place and Politics in Toronto" />
    <meta name="og:description" content="Mapping Toryland and Ford Nation" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/torontos-two-rights" />
    <meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/routes/assets/web-card-2.png" />
    <meta property="og:locale" content="en_CA">

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="https://schoolofcities.github.io/place-and-politics-toronto/torontos-two-rights" />
    <meta name="twitter:creator" content="@JeffAllenMaps" />
    <meta name="twitter:title" content="Place and Politics in Toronto" />
    <meta name="twitter:description" content="Mapping Toryland and Ford Nation" />
    <meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/routes/assets/web-card-2.png" />

</svelte:head>



<Top/>

<main>

	<!-- <UnderConstruction/> -->
	
	<div class="title">

		<h4>Place & Politics in Toronto - Part 2</h4>

		<div id="mini-line"></div>

		<h1>Toronto's Two Rights</h1>
		<h3><a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> November 25, 2022</h3>

		<div id="mini-line"></div>

	</div>



	<div class="text">
		<p>
			In our <a href="./the-geography-of-the-vote-poll-by-poll">last post</a> we mapped the vote share percentages for the 2022 mayoral candidates by neighbourhood. We found that, in the 2022 election anyway, some neighbourhoods in the city’s core wards were more likely to support Gil Peñalosa than John Tory, while neighbourhoods in wards outside the core were more likely to support John Tory. In fact, the more distant you are from the core, the more likely that Chloe Brown, who received 6.3% support citywide, beat Peñalosa for second place. It would appear that many core voters want something different, politically, than most suburban voters. In future posts we will explore what may be driving this pattern. First, however, we will look back at the geography of past elections to see where particular candidates did best.
		</p>
		<p>
			In this post, we look at the geography of support for candidates often thought of as being on the centre-right or right: John Tory, Jane Pitfield, and the Ford brothers. In the next post we'll look at candidates often thought of as on the left.
		</p>

		
	</div>

	<div class="text">
		<h2>Finding Toryland</h2>
		<p>
			Let’s begin by comparing John Tory’s geography of support in the four elections in which he ran for mayor.
		</p>
	</div>



	<div class="mapGrid">
		<div class="mapSmall">
			<MapMini candidate = {"pcttory2003"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pcttory2014"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pcttory2018"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pcttory_john2022"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>
	</div>
	
	<div class="text">
		<p>
			Each election featured quite different circumstances, of course. In 2003, Tory campaigned from the right in a crowded, five-way race, and ultimately lost to David Miller. In 2014, he campaigned (successfully) as a pragmatic centrist against conservative populist Doug Ford on the one side, and Olivia Chow, the progressive former city councillor and NDP MP, on the other. In 2018 and 2022, he was an entrenched incumbent facing candidates with professional urban planning experience and established reputations as urbanists.
		</p>
		<p>
			Yet across four elections and 19 years, Tory support was strongest and weakest in the same places. He was strongest in the Forest Hill, Rosedale, and points north along the Yonge corridor, as well as in central Etobicoke and lakeshore Scarborough. He was persistently weakest in the west-central downtown wards and Toronto Island. For Tory, the difference between losing and winning (and between merely winning and winning big) was picking up neighbourhoods in the city’s northwest and northeast: in York, north Etobicoke, and Scarborough.
		</p>
		<p>
			Tory’s map bears strong similarities to other candidates in other elections. Let’s look at support for Jane Pitfield in 2006. Pitfield had represented Leaside on city council since winning a byelection in 1999. Running on the slogan “Always think like a taxpayer,” she called for a property tax freeze and a crackdown on crime. Much like Tory three years earlier, she did best in the inner suburban neighbourhoods north of downtown, central Etobicoke, and Scarborough south of Kingston Road.
		</p>
	</div>

		<div class="mapSmall">
			<MapMini candidate = {"pctpitfield2006"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>

	<div class="text">
		<h2>Ford Nation</h2>
		<p>
			Now let’s turn to the geography of Ford Nation. In 2010, Rob Ford’s support was strongest outside the core, racking up overwhelming support in his home turf of northwest Etobicoke and receiving majority support in neighbourhoods across the rest of Etobicoke, Scarborough, much of North York, and parts of York and East York. His brother Doug’s map is more starkly divided. Where Rob did well, Doug did also; where Rob performed less well, Doug performed much worse. Indeed, we see that Doug Ford lost ground everywhere in the former City of Toronto and especially in North Toronto. He also did less well than his brother in south Etobicoke, central North York, and the Scarborough lakeshore neighbourhoods.
		</p>
	</div>


	<div class="mapGrid">
		<div class="mapSmall">
			<MapMini candidate = {"pctford2010"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pctford2014"} tracts={ctWithResults} colours = {coloursRight}/>
		</div>
	</div>

	<div class="text">
		<p>
			While Rob Ford’s map looks like a less extreme version of Tory’s 2018 and 2022 maps, Doug Ford’s map looks different. It is not surprising that, outside the City of Toronto, Ford and Tory’s maps are mirror images of each other in 2014. After all, they were running against each other. But Doug Ford also did relatively poorly in areas where Jane Pitfield and, earlier, Mel Lastman, did well.
		</p>
		<p>
			This suggests that conservative candidates all tend to do poorly in the city core, some of them do better in some parts of the inner-ring suburbs than in others. There appear to be two types of right-leaning neighbourhoods in Toronto. Some candidates unify them - Tory in 2018 and 2022, Ford in 2010 - while others, like Tory in 2003, Pitfield in 2006, and Doug Ford and John Tory in 2014, appeal to one but not the other.
		</p>
		<p>
			We’ll return to this in a future post. Next time, we will examine the geography of candidates commonly thought of as being on the left.
		</p>
	</div>


	<div id="mini-line"></div>



	<div class="info">
		<h3>Data Sources:</h3>
		<p>
			All the maps in this post use a dataset of historical neighbourhood-scale election results that we created with sociologists Daniel Silver of the University of Toronto and Jan Doering of McGill University. We hand-digitized the 1997 and 2000 election results and poll maps, which exist only in paper form, and accessed the 2003 through 2022 election results from the City’s open data site. We then apportioned the results to a common geography, 2021 census tracts, which represent neighbourhood areas of about 4,000 to 7,000 residents. To help orient you, we've overlaid the ward boundaries used since 2018 for reference, even though the city was divided into wards differently in previous years.
		</p>
	</div>

</main>
