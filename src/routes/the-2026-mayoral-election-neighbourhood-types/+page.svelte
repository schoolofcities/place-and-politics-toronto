<script>
	// Outline only: placeholder text and placeholder graphics (./components), to be filled in one at a time.
	// Analysis behind the graphics: analysis/election_2026/02_chow_coalition_expansion.ipynb.
	//
	// TODO before publishing:
	//  - add this post to $lib/posts.js (needs src/assets/p10.png and web-card-10.png), then add
	//    <StructuredData slug="..." /> below. Until then it is left out, because StructuredData
	//    treats an unlisted slug as the home page (and would set the canonical link to the site root).
	//  - replace CARD with web-card-10.png.

	import Top from "$lib/layout/TopSofC.svelte";

	import CorrelationsOverview from "./components/CorrelationsOverview.svelte";
	import NewVotesMap from "./components/NewVotesMap.svelte";
	import ChowTopFifthStrips from "./components/ChowTopFifthStrips.svelte";
	import ChineseVisibleMinority from "./components/ChineseVisibleMinority.svelte";
	import JewishMuslimShares from "./components/JewishMuslimShares.svelte";
	import CorrelationsOverTime from "./components/CorrelationsOverTime.svelte";

	const TITLE = "The 2026 mayoral election: What kinds of neighbourhoods voted for whom? | Place & Politics in Toronto";
	const CARD = "https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/assets/web-card-9.png"; // placeholder
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

	<!-- Introduction -->
	<section class="story-section" aria-label="Introduction">
		<div class="text">
			<p>Introduction text goes here.</p>
		</div>
		<div class="graphic">
			<CorrelationsOverview />
		</div>
	</section>

	<!-- Growing the pie -->
	<section class="story-section titled" aria-labelledby="growing-heading">
		<div class="text">
			<h2 id="growing-heading">Growing the pie</h2>
			<p>Text goes here.</p>
		</div>
		<div class="graphic">
			<NewVotesMap />
		</div>
		<div class="text">
			<p>More text goes here.</p>
		</div>
		<div class="graphic">
			<ChowTopFifthStrips />
		</div>
	</section>

	<!-- Identity voting -->
	<section class="story-section titled" aria-labelledby="identity-heading">
		<div class="text">
			<h2 id="identity-heading">Identity voting?</h2>
			<p>Text goes here.</p>
		</div>
		<div class="graphic">
			<ChineseVisibleMinority />
		</div>
		<div class="text">
			<p>More text goes here.</p>
		</div>
		<div class="graphic">
			<JewishMuslimShares />
		</div>
	</section>

	<!-- Plus ça change… -->
	<section class="story-section titled" aria-labelledby="change-heading">
		<div class="text">
			<h2 id="change-heading">Plus ça change…</h2>
			<p>Concluding text goes here.</p>
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
		margin: 0 auto 60px;
		width: 100%;
	}
	/* space above each titled section, in place of a rule */
	.story-section.titled {
		padding-top: 20px;
	}

	/* graphics are exactly as wide as the paragraphs: the .text column's content box (694px, or the page width less 50px), so their edges line up with the text */
	.graphic {
		margin: 20px auto;
		max-width: 694px;
		width: calc(100% - 50px);
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
