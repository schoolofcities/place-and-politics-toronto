<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import MapMini from "../lib/MapMini.svelte";
    import WebCard from "../assets/web-card-2.png";
	import '../styles.css';
	import ctWithResults from "../data/ctWithResults.geo.json";

	var coloursLeft = ["#defde0", "#a6e7bb", "#73d398", "#3cbd73", "#00a64b"];

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
    <meta name="og:description" content="The Electoral Geography of Progressivism in Toronto" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/torontos-two-rights" />
    <meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/sveltekit/src/routes/assets/web-card-3.png" />
    <meta property="og:locale" content="en_CA">

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="https://schoolofcities.github.io/place-and-politics-toronto/torontos-two-rights" />
    <meta name="twitter:creator" content="@JeffAllenMaps" />
    <meta name="twitter:title" content="Place and Politics in Toronto" />
    <meta name="twitter:description" content="The Electoral Geography of Progressivism in Toronto" />
    <meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/sveltekit/src/routes/assets/web-card-3.png" />

</svelte:head>



<Top/>

<main>

	<!-- <UnderConstruction/> -->
	
	<div class="title">

		<h4>Place & Politics in Toronto - Part 3</h4>

		<div id="mini-line"></div>

		<h1>The Electoral Geography of Progressivism in Toronto</h1>
		<h3><a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> November 30, 2022</h3>

		<div id="mini-line"></div>

	</div>



	<div class="text">
		<p>
			<a href="./torontos-two-rights">Last time</a>  we mapped neighbourhood support for candidates generally understood to be politically conservative: John Tory in 2003, 2014, 2018, and 2022, Jane Pitfield in 2006, Rob Ford in 2010, and Doug Ford in 2014. We found that while right-leaning candidates do better in the postwar suburban neighbourhoods, the pattern isn’t uniform. There appear to be two kinds of right-leaning neighbourhood: those that always always favour the conservative candidate, and those that, when given a choice, defect. We will explore why this happens in a future post. In this post, we will look at the electoral geography of progressive candidates, with a particular focus on Tooker Gomberg in 2000, Olivia Chow in 2014, Jennifer Keesmaat in 2018, and Gil Peñalosa in 2022. We then examine the exception to this pattern: left-leaning centrist David Miller’s victories in 2003 and 2006, and also George Smitherman’s failed 2010 campaign.
		</p>

		
	</div>

	<div class="text">
		<h2>
			Seaton Village: Progressive Epicentre</h2>
		<p>
			The plucky campaign of the late environmental activist Tooker Gomberg in 2000 is now a forgotten footnote of Toronto political history. Incumbent mayor Mel Lastman cruised to victory with 80% of the vote citywide. Gomberg received 8%, followed by trans activist Enza “Supermodel” Anderson with 2%. It is easy to dismiss Gomberg as a gadfly. He had been a serial candidate in multiple cities, having run for office in Edmonton (once successfully) and Montréal. He attracted attention, however, for being endorsed by urbanist luminary Jane Jacobs, and for promoting causes that later became mainstream: expanding the city’s authority over local issues and growing the anemic cycling network. Goomberg’s campaign matters because he was a precursor of things to come.
		</p>
		<p>
			Fast-forward 14 years to Olivia Chow’s campaign in 2014. As widow of NDP leader Jack Layton, a former school board trustee, Metro Toronto, and City of Toronto councillor from 1985 to 2005, and a federal MP from 2005 to 2014, she had broad name recognition across the city. Her personal story as an immigrant from Hong Kong resonated with many people who had faced similar challenges. She positioned herself as the anti-Rob Ford with the slogan “New Mayor, Better City,” promoting suburban transit expansion, expanded childcare, and using municipal hiring and contracts to create employment opportunities for disadvantaged communities. Her platform was pitched to the whole city, and perhaps especially to immigrant communities in the inner suburbs. Yet her map looks a like a supercharged version of Gomberg’s. Both candidates received their strongest support in a handful of neighbourhoods just west of the downtown core.
		</p>
	</div>

	<div class="mapGrid">
		<div class="mapSmall">
			<MapMini candidate = {"pctgomberg2000"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pctchow2014"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
	</div>
	
	<div class="text">
		<p>
			Four years after that, former chief city planner Jennifer Keesmaat’s platform also emphasized suburban rapid transit expansion, but her economic planks focused more on affordability than marginalization and inclusion. Her proposal to dismantle the eastern portion of the Gardiner Expressway likely did not endear her to suburban car commuters. In the end, she received an almost identical citywide vote share to Chow’s, and almost 40,000 fewer votes. Her strongest support came from the same west-downtown neighburhoods.
		</p>
		<p>
			As discussed in our first post, internationally recognized urbanist Gil Peñalosa’s 2022 campaign was rooted squarely in urbanist values: improving the quality of public amenities, expanding transit, and encouraging walking and cycling. Like Keesmaat, he opposed Mayor Tory’s reconstruction of the Gardiner Expressway. On election day, he received only 18% of the vote citywide and less than half the number of votes received by Keesmaat four years earlier. Again, he did best on a small portion of the city – a cluster of neighbourhoods on the west flank of the core.
		</p>
	</div>

	<div class="mapGrid">
		<div class="mapSmall">
			<MapMini candidate = {"pctkeesmaat2018"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pctpenalosa_gil2022"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
	</div>

	<div class="text">
		<p>
			From Chow to Keesmaat to Peñalosa, we see a consistent pattern over the past three elections: candidates of the left have drawn most of their support from a narrow section of the city: the western core area whose epicentre is the Seaton Village neighbourhood located north of Bloor, east of Christie, and west of Bathurst, and to a lesser extent the Riverdale and Leslieville neighbourhoods east of the Don River. The candidates’ citywide performance has varied mostly in the degree to which they have picked up generalized support elsewhere in the city. Aside from York University, there are no other hot spots of support.
		</p>
	</div>

	<div class="text">
		<h2>
			The Miller Exception?</h2>
		<p>
			Let’s now turn to David Miller’s two mayoral wins in 2003 and 2006. Like Chow, Miller had served on Metro Council and, after amalgamation, City Council. He had previously run provincially for the NDP in 1996. During the 2000-2003 term, he led the charge against corruption as the MFP computer leasing scandal was exposed and investigated. Having served on the TTC’s board, he had been a vocal advocate for transit expansion, and had taken special interest in the work of the Royal Commission on the Toronto Waterfront, arguing that the city was allowing its public realm to decay. All of these themes found their way into his platform.
		</p>
		<p>
			Transit, parks and other public amenities, environmentalism… all of this sounds like the stuff of Keesmaat’s and Peñalosa’s platforms, yet he eked out a win in a crowded, five-way race with 43% of the vote, six points ahead of his opponent John Tory and 20 points more than Chow in 2014 or Keesmaat in 2018. What made the difference?
		</p>
	</div>
	
	<div class="mapGrid">
		<div class="mapSmall">
			<MapMini candidate = {"pctmiller2003"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pctmiller2006"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
	</div>

	<div class="text">
		<p>
			Part of it may have been his deployment of a simple unifying metaphor: the broom. Miller’s 2003 campaign literature highlighted a straightforward message: “clean waterfront, clean air and streets, clean government.” Rob Ford’s 2010 “respect for taxpayers” slogan is the only other example in Toronto’s post-amalgamation history of simple and powerful message that effectively communicated the essence of the candidates offer.
		</p>
		<p>
			While clearly hewing to a certain kind of class-based progressivism (“For David Miller, every day is Labour Day” trumpeted one of his brochures), Miller’s message was calibrated for broad appeal. While many suburbanites likely cared little about his opposition to Island Airport expansion and support for waterfront redevelopment, they could get behind message of clean, honest, and open government after the controversies and malaise of Mel Lastman’s second term. While John Tory campaigned from the right as “a man of action” who would keep taxes low, cut budgets, and put more cops on the street, Miller offered a more hopeful vision of how the still newly-amalgamated city could be made to work better.
		</p>
		<p>
			Like the other progressives, Miller did best in Seaton Village and other west-central neighbourhoods, Riverdale. Unlike them, he also did very well in North Toronto and respectably in central Etobicoke and the Scarborough lakeshore – the same neighbourhoods where John Tory had his highest level of support in 2014. And, of course, he had levels of diffuse support across the rest of the city that exceeded those received by Chow, Keesmaat, and Peñalosa.
		</p>
		<p>
			Three years later, Miller won the 2006 election with 57% support citywide, 25 points ahead of his conservative rival Jane Pitfield. He did well everywhere in the city, and especially in same neighbourhoods that favoured his progressive successors. What is notable in the geography of his support, however, is where he lost the most support: neighbourhoods in North Toronto, central Etobicoke, and lakefront Scarborough. While sympathetic to Miller in 2003, many of these neighbourhoods supported Rob Ford in 2010 and have since become the most reliable pockets of support for John Tory since 2014.
		</p>
	</div>

	<div class="text">
		<h2>
			Smitherman: Anybody-but-Ford</h2>
		<p>
			What about Rob Ford’s opponent in 2010, George Smitherman? With a strong political base in Toronto’s Gay Village, he had risen from working for the pre-amalgamation City of Toronto’s last mayor, Barbara Hall, to provincial MPP, to cabinet minister and deputy premier in Dalton McGuinty’s provincial Liberal government. He campaigned primarily on his political experience. His platform and campaign lacked definition. Indeed, his and Ford’s articulated policy positions differed more in their tone than their substance: cut waste at City Hall, speed up commute times, make the city safer, and improve the business climate. Rather than inheriting Miller’s coalition and policy legacies, Smitherman, like Ford, ran against them. Indeed, his campaign literature positioned Smitherman as a force for change, one that would “Make you proud to say you’re from Toronto. Again.”
		</p>
	</div>

	<div class="mapGrid">
		<div class="mapSmall">
			<MapMini candidate = {"pctsmitherman2010"} tracts={ctWithResults} colours = {coloursLeft} />
		</div>
		<div class="mapSmall">
			<MapMini candidate = {"pctford2010"} tracts={ctWithResults} colours = {coloursRight} />
		</div>
	</div>

	<div class="text">
	
		<p>
			As Rob Ford’s insurgent campaign performed increasingly well in the polls through the summer of 2010, Smitherman became the “anybody-but-Ford” candidate, and most other “serious” candidates dropped out to support him. (The exception was councillor and Miller-era deputy mayor Joe Pantalone. While Smitherman and Pantalone combined received about 2,000 votes more than Ford, it is doubtful that all of Pantalone’s votes would have flowed to Smitherman had he dropped out of the race.) Smitherman’s support map is therefore the mirror image of Rob Ford’s. Neighbourhoods that tend to support progressive candidates did not support Smitherman because he was, or campaigned as, a progressive. They supported him because he wasn’t Rob Ford.
		</p>
	</div>


	<div class="text">
		<h2>
			Next Time: Explaining Toronto’s Entrenched Electoral Geography</h2>
		<p>
			In this post and the previous one, we have explored persistent divisions in Toronto’s electoral geography. Some neighbourhoods have consistently supported particular kinds of candidates across the 25 years and eight elections since amalgamation, while others have proven fickle. The strongest support for progressive candidates is reliably in west-central neighbourhoods, Riverdale, and Leslieville. The strongest support for conservative candidates is in the postwar suburbs of Etobicoke, Scarbrough, and North York. In between, in parts of North Toronto, lakefront Scarborough, and central Etobicoke, are neighbourhoods that have been receptive both types of candidate in different elections. In our next post, we will explore reasons for this pattern of electoral support.
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
