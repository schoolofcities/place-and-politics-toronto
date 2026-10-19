<script>
	//
	//   Intro: "there are 5 political groups in Toronto" + rotating map of all 5
	//   One section per cluster: header -> map -> summary tables -> body copy -> graphic
	//     Section 1: Progressive Core          — double strip plot
	//     Section 2: Soft-Left Belt            — double strip plot (income / education)
	//     Section 3: Civic Liberals            — (no graphic)
	//     Section 4: Suburban Conservatives    — triple strip plot
	//     Section 5: Low-turnout Suburbanites  — triple strip plot (visible minority / income / education)
	//
	// Per-section voting rows + graphic choice live in ./sections.js —
	// edit that file for section content, this one for page structure/layout.

	import { onMount, onDestroy } from "svelte";
	import Top from "$lib/layout/TopSofC.svelte";
	import PasswordGate from "$lib/layout/PasswordGate.svelte";

	import ClusterMap from "./components/ClusterMap.svelte";
	import ClusterSummaryTable from "./components/ClusterSummaryTable.svelte";
	import VotingDumbbell from "./components/VotingDumbbell.svelte";
	import ClusterComparisonTables from "./components/ClusterComparisonTables.svelte";
	import SectionNav from "./components/SectionNav.svelte";
	import StripPlot from "./components/StripPlot.svelte";

	import { SECTION_CONFIG } from "./sections.js";
	import { CLUSTER_COLORS } from "./components/clusterColors.js";
	import clustersSummary from "./data/clusters_summary.json";
	import clustersMetadata from "./data/clusters_metadata.json";
	import clusterAreas from "./data/clusters_dissolved.geo.json"; // census tracts dissolved by cluster
	import ctClusters from "./data/ct_clusters.geo.json"; // tract outlines, drawn under the clusters
	import ctValues from "./data/ct_values.json";

	// clusters_summary.json is already sorted progressive -> conservative (display_order 1-5),
	// but sort defensively rather than assume the file's row order never changes.
	// Each cluster's colour is replaced with this page's palette (see ./components/clusterColors.js).
	const clusters = [...clustersSummary]
		.sort((a, b) => a.display_order - b.display_order)
		.map((c) => ({ ...c, color: CLUSTER_COLORS[c.slug] ?? c.color }));

	// Each section's summary table compares the cluster's voting (vote-weighted, from
	// elections.*) to these Toronto-wide vote-weighted figures; see
	// ./components/ClusterSummaryTable.svelte.
	const torontoElections = clustersMetadata.toronto_benchmark.elections;

	// ── Rotating "all 5 groups" intro map ─────────────────────────────────────────────
	let rotatingIndex = 0;
	let rotateTimer;
	$: rotatingClusterId = clusters[rotatingIndex]?.cluster_id ?? null;
	onMount(() => {
		rotateTimer = setInterval(() => {
			rotatingIndex = (rotatingIndex + 1) % clusters.length;
		}, 2500);
	});
	onDestroy(() => clearInterval(rotateTimer));

	// Bottom-right map legend rows: all 5 groups (+ population share) for the rotating intro
	// map, or just the one group for a section map — see ./components/ClusterMap.svelte.
	// "On this page" menu: the page's eight sections, each cluster with its colour dot
	const navItems = [
		{ id: "introduction", label: "Introduction" },
		...clusters.map((c) => ({ id: c.slug, label: c.label, color: c.color })),
		{ id: "comparing-the-clusters", label: "Comparing the clusters" },
		{ id: "data-and-methods", label: "Data and methods" },
	];

	const allClustersLegend = clusters.map((c) => ({
		cluster_id: c.cluster_id,
		label: c.label,
		color: c.color,
		pct: c.population_share * 100,
	}));
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />

	<!-- TODO: finalize title/description/social image once the story's copy is set. -->
	<title>Place and Politics in Toronto</title>
	<meta name="description" content="Clustering Toronto's neighbourhoods into five political groups" />
	<meta name="author" content="School of Cities" />
	<link rel="canonical" href="https://schoolofcities.github.io/place-and-politics-toronto/five-torontos" />
	<meta property="og:title" content="Place and Politics in Toronto" />
	<meta property="og:description" content="Clustering Toronto's neighbourhoods into five political groups" />
	<meta property="og:type" content="article" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/five-torontos" />
	<meta property="og:locale" content="en_CA" />
</svelte:head>

<!-- Page is still in development — comment out this one line to unlock it for launch. -->
<PasswordGate />

<Top />

<main>
	<SectionNav items={navItems} />

	<div class="title" id="introduction">
		<h4>Place & Politics in Toronto - Part 7</h4>
		<div id="mini-line"></div>
		<h1>The Five Torontos</h1>
		<p class="subtitle">Clustering neighbourhoods based on voting patterns</p>
		<h3><a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" target="_blank" rel="noopener noreferrer">Aniket Kali</a> <br><br> October 2026</h3>
		<div id="mini-line"></div>
	</div>

	<div class="text">
		<p>
			People's experiences of Toronto can vary dramatically from one neighbourhood to the
			next. Areas separated by just a few subway stops can differ sharply in income, housing,
			access to transit and services, and even life expectancy –
			<a href="https://thelocal.to/life-expectancy-varies-by-almost-12-years-across-toronto-neighbourhoods/" target="_blank" rel="noopener noreferrer">which varies by almost 12 years</a>
			across the city. Those divides carry over into politics. Some parts of Toronto vote
			consistently, turn out in large numbers, and show a clear political orientation;
			elsewhere, voting is more divided or participation is much lower.
		</p>
		<p>
			Those differences matter beyond who wins an election. Neighbourhoods with similar
			numbers of eligible voters can contribute very different numbers of votes, while
			governments make decisions about the transit people rely on, the homes they can
			afford, the services available nearby, and how public money is spent. Using voting and
			turnout patterns from Toronto's three most recent elections, we identify five broad
			political geographies – five different Torontos that participate and vote in distinct
			ways. Census data is then used to describe the kinds of places those clusters
			represent; it does not determine which cluster a neighbourhood belongs to.
		</p>
	</div>

	<section class="intro-map">
		<p class="map-title">Five Torontos</p>
		<p class="map-subtitle">Census tracts clustered by voting in the 2023 mayoral and 2025 provincial and federal elections</p>
		<ClusterMap
			areas={clusterAreas}
			tracts={ctClusters}
			activeClusterId={rotatingClusterId}
			legend={allClustersLegend}
			label="Map of Toronto rotating through each of the five political clusters, showing which census tracts belong to the currently highlighted group"
		/>
	</section>

	<div class="text intro-end">
		<p>
			The five clusters run broadly from Toronto's most consistently progressive
			neighbourhoods toward its more conservative ones, but they are not simply five stops
			along a left-right line. Participation matters separately from partisan preference, and
			similar voting patterns sometimes appear in neighbourhoods with very different
			histories, housing, and demographics. What emerges is not a map of five kinds of
			voters, but five recurring combinations of politics and place.
		</p>
	</div>

	{#each clusters as cluster, i}
		{@const config = SECTION_CONFIG[cluster.slug]}
		{@const clusterId = cluster.cluster_id}
		{@const color = cluster.color}
		{#snippet stripAndCensus()}
			<!-- Strip plot (every section but Civic Liberals), then the census table.
				 Rendered after the section's text, except in Progressive Core, where it sits
				 before the closing paragraph (see below). -->
			{#if config.graphic === "strip"}
				<div class="graphic">
					<StripPlot values={ctValues} variables={config.stripVars} {clusterId} clusterLabel={cluster.label} {color} />
				</div>
			{/if}

			<!-- census characteristics: supporting detail, collapsed until a reader opens it -->
			<ClusterSummaryTable
				part="census"
				{cluster}
				{clusters}
				{torontoElections}
				variableLabels={clustersMetadata.variable_labels}
			/>
		{/snippet}
		<section class="cluster-section" id={cluster.slug} class:last-cluster={i === clusters.length - 1}>
			<h2>{cluster.label}</h2>
			<p class="map-subtitle">
				{cluster.n_tracts} of {clustersMetadata.n_tracts} census tracts, {(cluster.population_share * 100).toFixed(1)}% of population (2021 Census)
			</p>

			<!-- map, then a chart of the section's selected voting measures, then the full
				 election results behind a show/hide toggle -->
			<div class="map-results">
				<ClusterMap
					areas={clusterAreas}
					tracts={ctClusters}
					activeClusterId={clusterId}
					label={`Map of Toronto highlighting the census tracts belonging to the ${cluster.label} cluster`}
				/>
				<VotingDumbbell
					{cluster}
					{torontoElections}
					variableLabels={clustersMetadata.variable_labels}
					specs={config.votingSpecs}
				/>
				<ClusterSummaryTable
					{cluster}
					{torontoElections}
					variableLabels={clustersMetadata.variable_labels}
				/>
			</div>

			<div class="text">
				{#if cluster.slug === "progressive-core"}
					<p>
						Rooted in the twin hearts of Toronto's West End and East End, this is the city's
						clearest concentration of progressive voting. These neighbourhoods give the NDP
						much higher shares than Toronto overall, even in historically difficult elections
						for the party, while giving considerably less support to Conservatives across
						levels of government. Olivia Chow – a former NDP MP and city councillor – also
						performed particularly strongly here in the formally non-partisan 2023 mayoral
						race. Participation is high too: turnout sits above the city average across all
						three elections.
					</p>
					<p>
						The geography is as recognizable as the politics. This is Toronto's densest
						cluster, with the highest renter share, the lowest reliance on cars for
						commuting, and relatively high university attainment. Much of it is made up of
						older, established central-city neighbourhoods rather than the newer high-rise
						districts that appear more prominently in the Soft-Left Belt. That combination
						of educated, renter-heavy urban neighbourhoods and progressive voting is
						consistent with a
						<a href="https://wid.world/news-article/changing-political-cleavages-in-21-western-democracies/" target="_blank" rel="noopener noreferrer">broader shift documented across many Western democracies</a>,
						including
						<a href="https://www.mattpolacko.com/_files/ugd/2876d8_177a7fd90b264b8d9cf1d2973c75b727.pdf" target="_blank" rel="noopener noreferrer">research</a>
						<a href="https://thetyee.ca/Culture/2021/06/15/Thomas-Piketty-New-Data-Tells-About-Canadian-Left/" target="_blank" rel="noopener noreferrer">on Canada</a>,
						in which the electoral base of the left has increasingly moved toward highly
						educated and
						<a href="https://fortune.com/2024/03/16/homeowners-red-renters-blue-broken-housing-market-polarized-political-culture/" target="_blank" rel="noopener noreferrer">economically downward</a>
						urban voters.
					</p>
				{:else if cluster.slug === "soft-left-belt"}
					<p>
						If the Progressive Core is Toronto's most concentrated geography of progressive
						voting, the Soft-Left Belt is what that politics looks like once it spreads into
						a more varied urban landscape. It stretches through newer condo districts and
						rental-heavy parts of the central city, established neighbourhoods farther west
						and east, and pockets of Scarborough. These places do not share one built form
						or one history. What they share is electoral: high participation, broadly
						progressive voting, and a greater willingness to support Liberal or moderate
						alternatives than in the Core.
					</p>
					<p>
						That difference is visible across elections. Chow and the provincial NDP both
						outperform their Toronto-wide results here, but by much smaller margins than in
						the Progressive Core; Josh Matlow also performs best in this cluster. At the same
						time, the Soft-Left Belt has the highest university attainment and approximate
						income of the five clusters, while also having the highest shelter-cost burden,
						the largest recent-migrant share, and relatively high renting. That combination
						fits parts of Toronto's changing central-city geography, where growth has
						increasingly taken the form of
						<a href="https://www.toronto.ca/city-government/data-research-maps/research-reports/planning-development/housing-occupancy-trends/" target="_blank" rel="noopener noreferrer">mid- and high-rise apartments</a>
						and a large rented-condominium market; in 2021,
						<a href="https://www150.statcan.gc.ca/n1/daily-quotidien/220921/mc-b003-eng.htm" target="_blank" rel="noopener noreferrer">more than half of downtown condominiums were rented</a>.
					</p>
					<p>
						The result is a political belt rather than a single neighbourhood type. Some
						parts are products of recent condo growth; others are older and more
						established. They converge not because they look the same, but because they
						arrive at a similar political balance: left of Toronto overall, highly
						participatory, but less consistently aligned with the progressive left than the
						neighbourhoods at the city's core.
					</p>
				{:else if cluster.slug === "civic-liberals"}
					<p>
						The Civic Liberals are even harder to pin to one part of Toronto. They appear in
						parts of Midtown and Leaside, stretches of the Yonge corridor through
						Willowdale, pieces of The Beaches, Etobicoke-Lakeshore, and Scarborough along
						the lake. What connects them is not geography so much as political style:
						turnout is high, Liberal support is strong, and there is much less warmth toward
						the NDP and other progressive candidates.
					</p>
					<p>
						That pattern is clearest provincially, where the Liberals receive just over half
						the vote and the NDP falls to only 8 per cent. Ana Bailão also leads Olivia Chow
						in the mayoral race, while federally the Liberals remain ahead but Conservatives
						perform considerably better than in either of the first two clusters. These
						neighbourhoods are generally relatively affluent and highly educated, but the
						sharper dividing line is political: compared with the Soft-Left Belt, they are
						much more willing to move toward centrist and centre-right alternatives.
					</p>
					<p>
						There is some historical precedent for that kind of Toronto politics. The city's
						<a href="https://schoolofcities.github.io/neighbourhood-income-toronto-2020/" target="_blank" rel="noopener noreferrer">changing geography of wealth</a>
						runs through parts of this cluster, especially along the Yonge corridor, where
						incomes have
						<a href="https://www.utoronto.ca/news/gap-between-rich-and-poor-widening-says-u-t-david-hulchanski" target="_blank" rel="noopener noreferrer">risen sharply over time</a>.
						Toronto has long contained prosperous, high-participation districts that sit
						outside both the city's strongest progressive neighbourhoods and its most
						conservative suburbs. The Civic Liberals are a modern version of that middle
						ground: scattered across the map, but tied together by a politics that is
						engaged, Liberal-leaning, and notably less progressive than the clusters to
						their left.
					</p>
				{:else if cluster.slug === "suburban-conservatives"}
					<p>
						Spanning much of Toronto's established inner suburbs, the Suburban Conservatives
						overlap strongly with neighbourhoods built during the region's
						<a href="https://www.toronto.ca/explore-enjoy/history-art-culture/online-exhibits/web-exhibits/web-exhibits-community-neighbourhoods/your-home-our-city/your-home-our-city-suburban-growth/" target="_blank" rel="noopener noreferrer">postwar suburban expansion</a>:
						lower-density housing, high rates of homeownership, and greater automobile use.
						Today, they are the oldest and least renter-heavy of the five clusters, while
						driving more and taking transit less than anyone else. Their electoral pattern
						is just as clear: these neighbourhoods give the highest shares to the Ontario
						PCs and federal Conservatives, the lowest or near-lowest shares to the NDP, and
						favoured Ana Bailão over Olivia Chow in 2023. The federal Liberals still
						narrowly lead the Conservatives here, but this is where conservative parties and
						candidates perform most strongly overall.
					</p>
					<p>
						That pattern echoes a much older divide between Toronto's core and its postwar
						suburbs.
						<a href="https://www.toronto.ca/explore-enjoy/history-art-culture/online-exhibits/web-exhibits/web-exhibits-community-neighbourhoods/etobicoke-a-modern-suburb/" target="_blank" rel="noopener noreferrer">Etobicoke</a>,
						<a href="https://www.toronto.ca/explore-enjoy/history-art-culture/online-exhibits/web-exhibits/web-exhibits-community-neighbourhoods/progress-economy-heart-celebrating-100-years-of-north-york/progress-economy-heart-living-in-north-york/" target="_blank" rel="noopener noreferrer">North York</a>,
						and
						<a href="https://www.toronto.ca/explore-enjoy/history-art-culture/online-exhibits/web-exhibits/web-exhibits-local-government/albert-campbells-dream-a-new-scarborough-civic-centre/scarborough-before-the-civic-centre/" target="_blank" rel="noopener noreferrer">Scarborough</a>
						all grew rapidly through the postwar period before amalgamation in 1998, much of
						it around private homes and automobile travel. Political geographer Zack Taylor
						has documented an enduring city-suburb divide in Toronto voting that
						<a href="https://www.thestar.com/news/gta/toronto-s-political-divide-is-real-but-it-can-change-especially-in-the-suburbs/article_a903777f-15aa-54d3-a000-dc726b9e3a38.html" target="_blank" rel="noopener noreferrer">predates Rob Ford's conservatism</a>;
						in 2010, for example, the former Metropolitan Toronto suburbs voted heavily for
						Ford while the old City of Toronto went strongly for George Smitherman.
					</p>
					<p>
						But today's suburban politics no longer follow that older divide neatly. Much of
						Scarborough, despite sharing the same postwar and car-oriented built form, falls
						instead into the Low-turnout Suburbanites. The Suburban Conservatives are older,
						less renter-heavy, less racially diverse, and higher-income than those
						neighbouring suburban areas. The result is a geography that still closely
						resembles Toronto's older conservative suburban divide, but also shows how much
						the suburbs themselves have changed since they were first built.
					</p>
				{:else if cluster.slug === "low-turnout-suburbanites"}
					<p>
						It is easy to look at Toronto's electoral maps and treat much of the inner
						suburbs as one conservative bloc, but this cluster complicates that picture.
						More than anything else, what distinguishes these neighbourhoods is low
						participation. Turnout is lower than in every other cluster across the
						municipal, provincial, and federal elections, even though Low-turnout
						Suburbanites are Toronto's largest group, containing almost one-third of the
						city's population. These neighbourhoods also have the lowest approximate income
						and university attainment, the highest racialized share, some of the largest
						households, and the longest commutes.
					</p>
					<p>
						Their voting is more unsettled than that of the Suburban Conservatives beside
						them. Ontario PC support is relatively high, but Chow leads the mayoral vote and
						the federal Liberals receive a clear majority. Previous School of Cities work has
						documented a longer-term rise in Conservative support in
						<a href="https://schoolofcities.github.io/gta-immigration/political-shifts" target="_blank" rel="noopener noreferrer">immigrant- and minority-heavy GTA ridings</a>,
						particularly at the provincial level, pointing toward
						<a href="https://schoolofcities.github.io/gta-immigration/rightward-minorities" target="_blank" rel="noopener noreferrer">disillusionment with an incomplete multiculturalism</a>.
						What emerges here is not a simple march to the right, but a more unsettled
						politics in which different parties can succeed at different levels of
						government.
					</p>
					<p>
						That political complexity sits on top of a broader geography of inequality.
						Research on Toronto's inner suburbs has
						<a href="https://www.utsc.utoronto.ca/sociology/getting-heart-issues-matter-inner-suburbs" target="_blank" rel="noopener noreferrer">documented</a>
						lower incomes, weaker access to mass transit and city services, and longstanding
						underinvestment compared with more affluent parts of the city.
						<a href="https://www.thestar.com/news/gta/we-are-fighting-a-big-machine-gentrification-is-pulling-apart-toronto-s-communities-how-do/article_98d623ff-56a0-5fff-a73e-3964086febfc.html" target="_blank" rel="noopener noreferrer">Other reporting</a>
						has traced how rising housing costs and gentrification have pushed lower-income
						and immigrant households outward from parts of the core, while surveys through
						the
						<a href="https://community-voices.report/wp-content/uploads/2022/02/Feb-15-Community-Voices.pdf" target="_blank" rel="noopener noreferrer">Community Voices project</a>
						found that residents placed particular importance on reliable transportation,
						neighbourhood services, affordable housing, and safety. That makes the group's
						consistently low turnout important in its own right: many of the neighbourhoods
						facing some of Toronto's largest material and service disparities are also
						contributing fewer votes relative to their adult-citizen populations.
					</p>
				{/if}
			</div>

			<!-- Progressive Core: the strip plot and census table sit between its census-focused
				 paragraph and its closing paragraph on history -->
			{#if cluster.slug === "progressive-core"}
				{@render stripAndCensus()}
				<div class="text after-graphics">
					<p>
						But this is not simply a recent realignment. Many of these same areas were
						centres of
						<a href="https://www.yiddishbookcenter.org/language-literature-culture/wexler-oral-history-project-films-features-news/features/jewish-5" target="_blank" rel="noopener noreferrer">immigrant labour organization</a>,
						left-wing politics, and later neighbourhood-based urban reform, including
						<a href="https://activehistory.ca/blog/2015/12/10/how-did-1970s-reform-change-toronto/" target="_blank" rel="noopener noreferrer">the fight against the Spadina Expressway</a>.
						Toronto's reform movement was politically heterogeneous, but many of its fights
						over expressways, redevelopment, neighbourhood preservation, and local planning
						took place in and around the old urban core. Research on Toronto's political
						geography finds that neighbourhood-level patterns
						<a href="https://academic.daniels.utoronto.ca/urbangenome/2018/09/22/political-order-of-the-city/" target="_blank" rel="noopener noreferrer">can persist across elections</a>,
						even as the people living within them change. The electorate has shifted, but
						the
						<a href="https://schoolofcities.github.io/place-and-politics-toronto/the-electoral-geography-of-progressivism" target="_blank" rel="noopener noreferrer">geography of progressive voting</a>
						has proved remarkably durable.
					</p>
				</div>
			{/if}

			{#if cluster.slug !== "progressive-core"}
				{@render stripAndCensus()}
			{/if}
		</section>
	{/each}

	<!-- all five clusters side by side, before the methods -->
	<section class="comparison-section" id="comparing-the-clusters">
		<h2>Comparing the five clusters</h2>
		<ClusterComparisonTables
			{clusters}
			{torontoElections}
			variableLabels={clustersMetadata.variable_labels}
		/>
	</section>

	<div class="info" id="data-and-methods">
		<p class="info-title"><strong>Data and methods</strong></p>
		<p>
			This project was originally inspired in part by the <em>San Francisco Chronicle's</em>
			<a href="https://www.sfchronicle.com/projects/2026/california-political-groups/" target="_blank" rel="noopener noreferrer">California political groups project</a>,
			which used clustering to identify recurring political geographies rather than
			beginning from conventional partisan or demographic categories.
		</p>
		<p>
			We analyzed all 585 Toronto census tracts using results from three
			recent elections: the 2023 mayoral race, the 2025 Ontario election, and the 2025
			federal election. Because voting polls and census tracts do not share the same
			boundaries, poll-level votes were first interpolated to census tracts using the
			distribution of Canadian citizens aged 18 and over. Turnout is measured as votes cast
			relative to that adult-citizen population, while party and candidate support is
			calculated from valid votes cast.
		</p>
		<p>
			We grouped neighbourhoods using their voting and turnout alone – not their
			demographics. For each election, we considered both how a tract differed from
			Toronto overall and how it differed from its own ward or riding, giving those
			citywide and local perspectives equal weight. We also balanced the three elections so
			that no single electoral contest dominated. We then used
			principal component analysis (PCA) to condense overlapping electoral
			measures and k-means clustering to group tracts with similar political
			profiles.
		</p>
		<p>
			We tested several alternative approaches and solutions ranging from three to seven
			clusters. Under the final model, five groups produced the strongest silhouette score,
			although the difference between three, four, and five was small. Looking at the actual
			memberships helped distinguish the alternatives. At four clusters, the Progressive Core
			and Soft-Left Belt remain largely intact, while Civic Liberals largely lose their
			standalone cluster and are distributed among neighbouring groups. At six and seven,
			the existing political geographies begin to fragment while statistical separation
			becomes clearly weaker. Five therefore provides a useful balance between retaining
			substantively distinct electoral patterns and avoiding unnecessary subdivision. It
			should still be understood as one useful simplification of Toronto's continuous
			political geography, rather than evidence that exactly five natural political types
			exist.
		</p>
		<p>
			After creating the clusters, we joined the 2021 Census data on age, income, housing,
			migration, racialization, education, commuting, and other characteristics to understand
			the places within them. These demographics did not determine the groups
			and should not be read as explaining how any individual voted. The names –
			Progressive Core, Soft-Left Belt, Civic Liberals, Suburban Conservatives, and
			Low-turnout Suburbanites – are similarly descriptive shorthand applied after
			the analysis.
		</p>
		<p>
			For full details on the data, interpolation, model selection, sensitivity tests,
			aggregation, and limitations, see our complete
			<a href="https://github.com/schoolofcities/place-and-politics-toronto/tree/main/analysis/clustering_neighbourhoods" target="_blank" rel="noopener noreferrer">Data and Methods</a>
			and the reproducible analysis notebooks:
			<a href="https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/clustering_neighbourhoods/02_model_exploration.ipynb" target="_blank" rel="noopener noreferrer">model exploration</a>,
			<a href="https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/clustering_neighbourhoods/03_cluster_interpretation.ipynb" target="_blank" rel="noopener noreferrer">cluster interpretation</a>,
			and
			<a href="https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/clustering_neighbourhoods/04_process_ct_to_cluster.ipynb" target="_blank" rel="noopener noreferrer">final data processing</a>.
		</p>
	</div>

	<div id="mini-line"></div>

	<div class="info">
		<p>
			Thanks to Jeff Allen and Zack Taylor for reviewing the methods, research, and text
			behind this piece, and to Felicity Heyworth for reviewing the text.
		</p>
	</div>
</main>

<style>
	.title .subtitle {
		font-weight: normal;
		font-size: 20px;
		line-height: 1.35;
		margin: 14px 0 18px;
	}

	.intro-map,
	.cluster-section {
		margin: 0 auto 40px;
		max-width: 850px;
		width: calc(100% - 20px);
	}
	/* a light rule above each cluster section, and below the last, to separate the sections */
	.cluster-section {
		border-top: 1px solid #d9d9d9; /* 15% grey */
		padding-top: 66px;
		margin-bottom: 90px;
	}
	/* map, voting chart and election-results toggle */
	.map-results {
		margin-top: 12px;
		margin-bottom: 30px;
	}

	/* the all-groups comparison tables, between the last cluster section and the methods */
	.comparison-section {
		margin: 0 auto 60px;
	}
	/* (more specific than the shared heading rule further down, which sets margin-bottom: 0) */
	section.comparison-section h2 {
		margin-bottom: 20px;
	}

	/* more room between the census toggle and Progressive Core's closing paragraph below it */
	.after-graphics {
		margin-top: 40px;
	}

	/* the same space above the first section's rule as above the others (the global `.text`
	   block already has 10px bottom padding, plus this = ~90px) */
	.intro-end {
		margin-bottom: 80px;
	}
	.cluster-section.last-cluster {
		border-bottom: 1px solid #d9d9d9;
		padding-bottom: 90px;
	}
	/* styled to match the intro map's `.map-title` */
	.cluster-section h2,
	.comparison-section h2 {
		font-family: "Source Serif Pro", serif;
		font-size: 20px;
		font-weight: bold;
		text-align: center;
		margin-bottom: 0;
	}
	.graphic {
		margin-top: 20px;
	}

	/* title + subtitle above the intro map, so it still makes sense on its own (e.g. screenshotted) */
	.map-title {
		font-family: "Source Serif Pro", serif;
		font-size: 20px;
		font-weight: bold;
		text-align: center;
		margin: 24px 0 0;
	}
	.map-subtitle {
		font-family: OpenSans, sans-serif;
		font-size: 14px;
		color: #555;
		text-align: center;
		/* pulled into the map's empty top margin (the svg pads and centres Toronto's
		   rotated outline, leaving blank space above it); kept above the svg in stacking */
		position: relative;
		z-index: 1;
		margin: 4px 0 -20px;
	}

	.info-title {
		font-size: 17px;
	}

	@media (max-width: 600px) {
		.intro-map {
			margin-bottom: 36px;
		}
		.cluster-section {
			margin-bottom: 86px;
		}
		.graphic {
			margin-top: 18px;
		}
	}
</style>
