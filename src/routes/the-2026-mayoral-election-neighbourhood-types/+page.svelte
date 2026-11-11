<script>
	// Graphics live in ./components; colours in ./components/config.js. Their data are JSON/GeoJSON files in ./data,
	// built by analysis/election_2026/03_neighbourhood_types_page_data.ipynb (the analysis behind the story is in
	// 02_chow_coalition_expansion.ipynb).

	import Top from "$lib/layout/TopSofC.svelte";
	import StructuredData from "$lib/layout/StructuredData.svelte";

	import NeighbourhoodMaps from "./components/NeighbourhoodMaps.svelte";
	import CorrelationsOverview from "./components/CorrelationsOverview.svelte";
	import NewVotesMap from "./components/NewVotesMap.svelte";
	import ChowTopFifthStrips from "./components/ChowTopFifthStrips.svelte";
	import ChineseShares from "./components/ChineseShares.svelte";
	import ReligionShares from "./components/ReligionShares.svelte";
	import CorrelationsOverTime from "./components/CorrelationsOverTime.svelte";

	const TITLE = "The 2026 mayoral election: What kinds of neighbourhoods voted for whom? | Place & Politics in Toronto";
	const CARD = "https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/assets/web-card-10.png";
	const DESCRIPTION =
		"What kinds of neighbourhoods voted for whom in the 2026 Toronto mayoral election: the demographics of Olivia Chow's coalition, how she grew it, and what has and has not changed over time.";
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />

	<title>{TITLE}</title>
	<meta name="description" content={DESCRIPTION} />
	<meta name="author" content="Zack Taylor, Aniket Kali, Jeff Allen" />

	<meta property="og:title" content={TITLE} />
	<meta property="og:site_name" content="Place & Politics in Toronto" />
	<meta property="og:description" content={DESCRIPTION} />
	<meta property="og:type" content="article" />
	<meta property="article:published_time" content="2026-11-10" />
	<meta property="article:author" content="https://zacktaylorwestern.wordpress.com/" />
	<meta property="article:author" content="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" />
	<meta property="article:author" content="https://jamaps.github.io/" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/the-2026-mayoral-election-neighbourhood-types" />
	<meta property="og:locale" content="en_CA" />

	<meta property="og:image" content={CARD} />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://www.schoolofcities.utoronto.ca/" />
	<meta name="twitter:title" content={TITLE} />
	<meta name="twitter:description" content={DESCRIPTION} />
	<meta name="twitter:image" content={CARD} />
</svelte:head>

<StructuredData slug="the-2026-mayoral-election-neighbourhood-types" description={DESCRIPTION} />

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto - Part 10</h4>
		<div id="mini-line"></div>
		<h1>The 2026 mayoral election: What kinds of neighbourhoods voted for whom?</h1>
		<h3>
			<a href="https://zacktaylorwestern.wordpress.com/" target="_blank" rel="noopener noreferrer">Zack Taylor</a>,
			<a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" target="_blank" rel="noopener noreferrer">Aniket Kali</a>, and
			<a href="https://jamaps.github.io/" target="_blank" rel="noopener noreferrer">Jeff Allen</a>
			<br><br> <span class="date">November 10, 2026</span>
		</h3>
		<div id="mini-line"></div>
	</div>

	<!-- Introduction: the lead maps, then the first three paragraphs and the ranked lists -->
	<section class="story-section" aria-label="Introduction">
		<div class="graphic hero">
			<NeighbourhoodMaps />
		</div>
		<div class="text">
			<p>
				Chow and Bradford appealed to different kinds of voters. The
				<a href="https://www.thestar.com/news/gta/why-olivia-chow-and-brad-bradford-supporters-see-toronto-as-two-different-cities/article_18a06e44-86a6-4015-b444-e65f0fbe6f73.html" target="_blank" rel="noopener noreferrer"><em>Star</em>’s Vote Compass project</a>
				found that people who favoured one or the other candidate seemed to live in “different cities”, with Chow supporters
				being most concerned about housing and transit, while Bradford’s reported property tax rates and crime and policing as
				their most important issues. As our
				<a href="https://schoolofcities.github.io/place-and-politics-toronto/social-geography-and-the-mayoral-vote#cvar=jwmdauto_pct&cyear=2021&eyear=2026&ecand=chow_olivia&eall=0" target="_blank" rel="noopener noreferrer">social geography correlation tool</a>
				shows, this variation is reflected in their geographic bases of support. Each candidate tended to receive support from
				different types of neighbourhoods – reflecting
				<a href="https://schoolofcities.github.io/place-and-politics-toronto/five-torontos" target="_blank" rel="noopener noreferrer">deeper patterns</a>
				across the city.
			</p>
			<p>
				Transportation behaviour gives a strong hint about what separates neighbourhoods that support Chow and Bradford.
				Commuting by bicycle or walking, and neighbourhood walkability are among the strongest correlates of neighbourhood
				support for Chow. By contrast, commuting by car is Bradford’s strongest.
			</p>
			<p>
				Chow’s neighbourhoods are also disproportionately home to younger, “creative class” types – people who work in arts
				and culture occupations, are unmarried or living common-law, and rent. Bradford’s neighbourhoods are where
				“homevoters” live: people who are married, live in single-detached houses, and have higher household incomes. This may
				be interpreted as something of a class divide. Bradford’s geographic coalition supports a narrative of pocketbook
				voting: people voting for low taxes and protection of property and property values. The characteristics of Chow’s
				coalition are consistent with the prioritization of preserving and expanding collective amenities.
			</p>
		</div>
		<div class="graphic">
			<CorrelationsOverview />
		</div>
	</section>

	<!-- Growing the pie -->
	<section class="story-section titled" aria-labelledby="growing-heading">
		<div class="text">
			<h2 id="growing-heading">Growing the pie</h2>
			<p>
				In the
				<a href="https://schoolofcities.github.io/place-and-politics-toronto/the-2026-mayoral-election-local-landslides" target="_blank" rel="noopener noreferrer">previous post</a>
				we noted that Chow won with a “core-plus” strategy – building a coalition of neighbourhoods from the centre outwards
				toward the periphery. This was not only the result of a greater number of votes from higher turnout, but also a
				substantial increase in the percentage of votes for her as well.
			</p>
			<p>
				Where did all of these new votes come from? Half of them came from census tracts that she won in 2023 largely in Old
				Toronto, East York, and northern Scarborough. But a substantial number also came from parts of the city that she
				flipped, largely in the rest of Scarborough and along the Weston Road corridor. Moreover, even places that Bailão won
				in 2023 which stuck with Bradford in 2026, she increased her share of the vote from 21.7% to 39.3%.
			</p>
		</div>
		<div class="graphic">
			<NewVotesMap />
		</div>
		<div class="text">
			<p>
				Who exactly are these new supporters? For the most part, they resemble the same kinds of voters that Chow won in 2023:
				transit and bicycle riders, renters, young people, and lower income residents. Across the city, her increase in vote
				share was tied to neighbourhoods with a higher proportion of renters, and this is especially prevalent in Scarborough.
				In one sense, this isn’t very surprising – Chow has pursued numerous pro-renter policies including a
				<a href="https://www.cbc.ca/news/canada/toronto/toronto-renoviction-bylaw-1.7607168" target="_blank" rel="noopener noreferrer">renoviction bylaw</a>,
				<a href="https://www.cbc.ca/news/canada/toronto/city-approves-rentsafeto-changes-1.7181345" target="_blank" rel="noopener noreferrer">increased support to RentSafeTO</a>,
				and
				<a href="https://www.cbc.ca/news/canada/toronto/olivia-chow-bad-landlord-task-force-9.7358529" target="_blank" rel="noopener noreferrer">remedial action at 500 Dawes Road</a>.
				But in another sense, it reflects the growth of half of the city as a political constituency in its own right,
				overcoming its historical association with low turnout.
			</p>
			<p>
				At the same time, some of her weakest gains were in neighbourhoods with a high proportion of visible minority
				residents. Conversely, this is where Bradford began to make inroads, adhering to a broader trend of an
				<a href="https://schoolofcities.github.io/gta-immigration/rightward-minorities" target="_blank" rel="noopener noreferrer">openness to right-wing politics</a>
				from visible minorities, or
				<a href="https://schoolofcities.github.io/place-and-politics-toronto/toronto-turnout" target="_blank" rel="noopener noreferrer">plain abstention</a>,
				which School of Cities research has previously highlighted.
			</p>
		</div>
		<div class="graphic">
			<ChowTopFifthStrips />
		</div>
	</section>

	<!-- Identity voting -->
	<section class="story-section titled" aria-labelledby="identity-heading">
		<div class="text">
			<h2 id="identity-heading">Identity voting?</h2>
			<p>
				Toronto is a highly ethnically diverse city, and so we might expect to see ethnic affinity voting for Chow. In 2023,
				and again in 2026, pundits suggested that as a Chinese woman, Chow would potentially attract support from the city’s
				large Asian community. In fact we find this to be correct, if weakly. Neighbourhood vote shares for Chow are weakly
				correlated with neighbourhood Chinese population share in 2014 and 2026, regardless of location. In 2023 there was a
				stronger correlation in suburban areas, but a weaker one in 2026. Without individual-level evidence from surveys we
				cannot definitively explain this pattern. Nevertheless, we may conclude that Chinese ethnic affinity voting likely
				occurs, but it is a marginal factor, and was more present in 2023 than in 2026 or 2014.
			</p>
		</div>
		<div class="graphic">
			<ChineseShares />
		</div>
		<div class="text">
			<p>
				In the context of the polarized debate on Israel and Palestine, the media reported
				<a href="https://nationalpost.com/news/canada/after-re-election-olivia-chow-needs-to-show-up-in-order-to-gain-jewish-communitys-trust/" target="_blank" rel="noopener noreferrer">criticism from the Jewish community</a>
				that Chow was insufficiently supportive of them, while others have
				<a href="https://www.cbc.ca/news/canada/toronto/toronto-palestinian-flag-raising-9.6981640" target="_blank" rel="noopener noreferrer">pushed back</a>
				on that criticism as relying on anti-Palestinian tropes.
				<a href="https://x.com/BradMBradford/status/2097718635104006517" target="_blank" rel="noopener noreferrer">Bradford called her out</a>
				for not showing up to a Walk for Israel and a debate on antisemitism, but also
				<a href="https://www.thestar.com/news/gta/brad-bradford-s-campaign-drops-an-event-co-host-over-islam-comments/article_8935bb5e-5d86-42d6-b5d1-46d4a2d90e44.html" target="_blank" rel="noopener noreferrer">came under criticism</a>
				for courting Islamophobes.
			</p>
			<p>
				Do we see any evidence of Jewish neighbourhoods disproportionately supporting Bradford or Muslim neighbourhoods
				disproportionately supporting Chow? Again, we have weak evidence that this is the case. As the proportion of the
				neighbourhood population that is Jewish increases, that neighbourhood was more likely to support Bradford over Chow.
				The corresponding trend for neighbourhoods by Muslim population is much weaker.
			</p>
		</div>
		<div class="graphic">
			<ReligionShares group="Jewish" />
		</div>
		<div class="graphic">
			<ReligionShares group="Muslim" />
		</div>
	</section>

	<!-- Plus ça change… -->
	<section class="story-section titled" aria-labelledby="change-heading">
		<div class="text">
			<h2 id="change-heading">Plus ça change…</h2>
			<p>
				In the end, the geography of the 2026 election, along with the limited polling data reported in the media, suggests
				that the contest hinged on divergent neighbourhood interests rather than on other potential divides, including
				ethno-racial group conflict. The 2026 election is not unique. With the three-way 2014 election being the principal
				exception to the trend, we find that transportation behaviour and housing type and tenure, which are in turn related
				to distance from City Hall, are powerful positive or negative correlates of support for winning mayoral candidates
				across time. Toronto politics is to a large degree a politics of mobility and location – where people live, the
				nature of their relationship to housing, and how they move through the city.
			</p>
		</div>
		<div class="graphic">
			<CorrelationsOverTime />
		</div>
	</section>

	<div class="info" id="data-and-methods">
		<p class="info-title"><strong>Data and methods</strong></p>
		<p>
			All data are for Toronto’s 585 census tracts, on 2021 boundaries. Official <a href="https://open.toronto.ca/dataset/election-results-official/" target="_blank" rel="noopener noreferrer">election results</a>
			and the <a href="https://www.toronto.ca/city-government/elections/city-elections/voting-places/" target="_blank" rel="noopener noreferrer">voting subdivisions</a>
			(poll catchment areas) were downloaded from the City of Toronto, and election results and census characteristics were each apportioned to these tracts.
			Everything here describes neighbourhoods, not how individual voters, or any group of people, voted. The code and data used to build this page and its
			graphics are on <a href="https://github.com/schoolofcities/place-and-politics-toronto" target="_blank" rel="noopener noreferrer">GitHub</a>.
		</p>
		<ul>
			<li><strong><em>Elections:</em></strong> poll-level mayoral results, 1997 to 2026, split into dissemination blocks by population and summed to 2021 census tracts. Only election-day votes are included, as advance and mail-in votes can’t be placed in a neighbourhood. The map and the votes Chow added use the polls that can be mapped, about 78% of valid votes in 2023 and 76% in 2026, so the 2023 baseline is not the official result, in which Chow led Ana Bailão 37.2% to 32.5%.</li>
			<li><strong><em>Census:</em></strong> Statistics Canada’s 2021 Census of Population, including median age. The chart of the winners’ vote over time uses the census nearest each election, 1996 to 2021; data from 1996 to 2016 were apportioned to 2021 census tracts using the <a href="https://doi.org/10.1111/cag.12467" target="_blank" rel="noopener noreferrer">Canadian Longitudinal Census Tract Database</a> (Allen and Taylor, 2018).</li>
			<li><strong><em>Correlations:</em></strong> Pearson coefficients across tracts, unweighted, between a candidate’s share of valid election-day votes and a tract characteristic.</li>
			<li><strong><em>Boundaries:</em></strong> census tracts from Statistics Canada and former municipalities from the City of Toronto, as in other posts in this series.</li>
		</ul>
	</div>
</main>

<style>
	.story-section {
		margin: 0 auto 40px;
		width: 100%;
	}
	/* space above each titled section, in place of a rule */
	.story-section.titled {
		padding-top: 10px;
	}

	/* graphics are exactly as wide as the paragraphs: the .text column's content box (694px, or the page width less 50px), so their edges line up with the text */
	.graphic {
		margin: 14px auto 8px;
		max-width: 694px;
		width: calc(100% - 50px);
	}
	/* the lead graphic: close under the title block, with the introduction following */
	.graphic.hero {
		margin-top: 8px;
		margin-bottom: 8px;
	}

	.info-title {
		font-size: 17px;
	}
	.info ul {
		margin: 0;
		padding-left: 18px;
	}
	.info li {
		margin-bottom: 8px;
	}

	@media (max-width: 600px) {
		.story-section {
			margin-bottom: 32px;
		}
		.story-section.titled {
			padding-top: 6px;
		}
		.graphic {
			margin: 12px auto 6px;
		}
	}
</style>
