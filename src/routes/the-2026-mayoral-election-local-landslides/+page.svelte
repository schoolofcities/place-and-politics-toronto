<script>
	// Graphics live in ./components; colours in ./components/config.js. Chart data are the CSVs in
	// ./data, exported by Zack Taylor's R scripts; the poll map's data is built by ./data/prep_polls.py,
	// the tract small multiples' by ./data/prep_tracts.py, and the change map's vote counts by ./data/prep_change.py.

	import Top from "$lib/layout/TopSofC.svelte";
	import PasswordGate from "$lib/layout/PasswordGate.svelte"; // remove, with <PasswordGate /> below, at launch

	import MarginsByElection from "./components/MarginsByElection.svelte";
	import PollMap from "./components/PollMap.svelte";
	import CoreSuburbStacked from "./components/CoreSuburbStacked.svelte";
	import ProgressiveMaps from "./components/ProgressiveMaps.svelte";
	import MunicipalityBars from "./components/MunicipalityBars.svelte";
	import ChangeMap from "./components/ChangeMap.svelte";

	const TITLE = "The 2026 mayoral election: Local landslides | Place & Politics in Toronto";
	const DESCRIPTION =
		"Mapping the 2026 Toronto mayoral election poll by poll: Olivia Chow's local landslides, her core-plus coalition, and the role of Scarborough.";
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />

	<title>{TITLE}</title>
	<meta name="description" content={DESCRIPTION} />
	<meta name="author" content="Zack Taylor, Jeff Allen, Aniket Kali" />

	<meta property="og:title" content={TITLE} />
	<meta property="og:site_name" content="Place & Politics in Toronto" />
	<meta property="og:description" content={DESCRIPTION} />
	<meta property="og:type" content="article" />
	<meta property="article:published_time" content="2026-11-04" />
	<meta property="article:author" content="https://zacktaylorwestern.wordpress.com/" />
	<meta property="article:author" content="https://jamaps.github.io/" />
	<meta property="article:author" content="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/the-2026-mayoral-election-local-landslides" />
	<meta property="og:locale" content="en_CA" />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://www.schoolofcities.utoronto.ca/" />
	<meta name="twitter:title" content={TITLE} />
	<meta name="twitter:description" content={DESCRIPTION} />
</svelte:head>

<PasswordGate />

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto - Part 9</h4>
		<div id="mini-line"></div>
		<h1>The 2026 mayoral election: Local landslides</h1>
		<h3>
			<a href="https://zacktaylorwestern.wordpress.com/" target="_blank" rel="noopener noreferrer">Zack Taylor</a>,
			<a href="https://jamaps.github.io/" target="_blank" rel="noopener noreferrer">Jeff Allen</a>, and
			<a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" target="_blank" rel="noopener noreferrer">Aniket Kali</a>
			<br><br> <span class="date">November 4, 2026</span>
		</h3>
		<div id="mini-line"></div>
	</div>

	<section class="story-section" aria-label="The 2026 mayoral election: Local landslides">
		<div class="text">
			<p>
				In the end it wasn’t even close. Despite polls showing a tightening of the race, incumbent mayor Olivia Chow
				trounced Brad Bradford 54.2% to 41.1%. After Chris Alexander dropped out of the race, no credible third candidate
				remained in the race – the top two together received more than 95% of votes cast. Unlike in 2023, when Chow won
				the election despite coming behind Ana Bailão in the election-day vote tally, Chow performed strongly in both.
			</p>
		</div>
		<div class="graphic graphic-map">
			<PollMap />
		</div>
	</section>

	<section class="story-section titled" aria-labelledby="landslides-heading">
		<div class="text">
			<h2 id="landslides-heading">A geography of local landslides</h2>
			<p>
				Chow won by a wide margin in most parts of the city. In fact, 58% of polls (including ward-level advance and
				mail-in polls) were decided by a 20 percentage point margin or more. As in previous elections, where candidates
				did well, they generally did very well. It was, as is typically true in Toronto mayoral elections, a geography of
				local landslides.
			</p>
		</div>
		<div class="graphic">
			<MarginsByElection />
		</div>
		<div class="text">
			<p>
				Chow largely replicated the map of election-day support in 2023, but with higher percentages. She beat Bradford
				handily in core neighbourhoods, racking up margins of 20 percentage points or more south of St. Clair within the
				former City of Toronto, York and East York. As past progressive candidates discovered – see Keesmaat in 2018 and
				Peñalosa in 2022, and indeed Chow herself in 2014 – winning these neighbourhoods alone would not have been enough.
				Chow was pushed over the top by racking up strong support specific neighbourhoods outside the core. In Etobicoke
				and York, she did well along the Weston Road corridor and in the apartment neighbourhoods in the northwest corner
				of the city, as well as south of the Queensway in Mimico, New Toronto, and Long Branch. In North York, she racked
				up a vote surplus in York University and Jane and Finch, and also in the Don Mills corridor above and below the
				401.
			</p>
		</div>
		<div class="graphic graphic-maps">
			<ProgressiveMaps />
		</div>
	</section>

	<section class="story-section titled" aria-labelledby="core-heading">
		<div class="text">
			<h2 id="core-heading">Core, suburbs, and the Scarborough factor</h2>
			<p>
				Chow mounted an effective “core-plus” strategy – running up votes in her “home base” in the city’s core while
				picking up votes wherever she could in the city’s inner and outer suburbs. About 44% of votes she received were
				cast in the former City of Toronto. This is the only way that progressive mayoral candidates have won since
				amalgamation. David Miller did it in 2003 and 2006, and Chow in 2023. All other progressive candidates have
				failed. Chow’s capture of suburban votes in 2026 rivals only Miller’s in 2006, another two-way race.
			</p>
		</div>
		<!-- hidden for now, not deleted
		<div class="graphic">
			<CoreSuburbStacked />
		</div>
		-->
		<!-- exploratory: change in Chow's share by tract, to be merged, replaced or removed -->
		<div class="graphic graphic-map">
			<ChangeMap />
		</div>
		<div class="text">
			<p>
				<a href="https://www.thestar.com/opinion/the-war-for-scarborough-why-the-east-end-is-shaping-up-as-a-key-battleground/article_2ab20aac-25ec-4ffa-8d96-d0cc6a86885b.html" target="_blank" rel="noopener noreferrer">Matt Elliot wrote in the <em>Toronto Star</em></a>
				that her path to victory ran through Scarborough, and she did very well there. She won 81% of election-day polls
				and 92% of advance polls in the former borough, achieving a 53% vote share. Indeed, Scarborough is the only outer
				suburban municipality she won. Bradford eked out narrow majorities in Etobicoke and North York only. Could she
				have won without a strong showing in Scarborough? Yes. Imagine if Bradford and Chow’s vote shares had been
				swapped, and Bradford had taken Scarborough by 53% to Chow’s 40%. Chow still would have won the citywide vote 52%
				to 44%. She had enough votes everywhere else.
			</p>
			<p>
				In the next post we’ll look in more detail about what <em>types</em> of neighbourhoods supported each major
				candidate.
			</p>
		</div>
		<div class="graphic">
			<MunicipalityBars />
		</div>
	</section>

	<div class="info">
		<p class="info-title"><strong>Data Sources</strong></p>
		<p>
			Official <a href="https://open.toronto.ca/dataset/election-results-official/" target="_blank" rel="noopener noreferrer">election results</a>
			and the <a href="https://www.toronto.ca/city-government/elections/city-elections/voting-places/" target="_blank" rel="noopener noreferrer">voting subdivisions</a>
			(poll catchment areas) were downloaded from the City of Toronto. The code and data used to build this page and its
			graphics are on <a href="https://github.com/schoolofcities/place-and-politics-toronto" target="_blank" rel="noopener noreferrer">GitHub</a>.
		</p>
		<p>
			The census tract maps and the chart of where each progressive candidate's votes came from are based on the
			historical election results used in other posts in this series, apportioned to 2021 census tracts.
		</p>
	</div>
</main>

<style>
	.story-section {
		margin: 0 auto 60px;
		width: 100%;
	}
	/* space above each titled section, in place of a rule */
	.story-section.titled {
		padding-top: 20px;
	}
	/* section headings sit in the text column with the browser's h2 style, as on the 2023 post */

	/* graphics sit wider than the text column, like the maps on the other stories */
	.graphic {
		margin: 20px auto;
		max-width: 850px;
		width: calc(100% - 20px);
	}
	/* the poll map, about a fifth wider than the other graphics allow */
	.graphic-map {
		max-width: 1200px;
	}
	/* the small-multiple maps, five across */
	.graphic-maps {
		max-width: 1100px;
	}

	.info-title {
		font-size: 17px;
	}

	@media (max-width: 600px) {
		.story-section {
			margin-bottom: 48px;
		}
		.story-section.titled {
			padding-top: 12px;
		}
		.graphic {
			margin: 16px auto;
		}
	}
</style>
