<script>
	//
	//   Intro: "there are 5 political groups in Toronto" + rotating map of all 5
	//   One section per cluster: header -> map -> summary tables -> body copy -> graphic
	//     Section 1: Progressive Core       — double strip plot
	//     Section 2: Mobile Middle          — (no graphic)
	//     Section 3: Civic Professionals    — income-vs-education scatter
	//     Section 4: Settled Conservatives  — triple strip plot
	//     Section 5: Working Suburbanites   — normalized triangle (visible minority / income / education)
	//
	// Per-section voting rows + graphic choice live in $lib/config/fiveTorontosSections.js —
	// edit that file for section content, this one for page structure/layout.

	import { onMount, onDestroy } from "svelte";
	import Top from "$lib/layout/TopSofC.svelte";
	import PasswordGate from "$lib/layout/PasswordGate.svelte";
	import "../styles.css";

	import ClusterMap from "$lib/maps/ClusterMap.svelte";
	import ClusterSummaryTable from "$lib/tables/ClusterSummaryTable.svelte";
	import StripPlot from "$lib/charts/StripPlot.svelte";
	import ScatterHighlight from "$lib/charts/ScatterHighlight.svelte";
	import TernaryProfilePlot from "$lib/charts/TernaryProfilePlot.svelte";
	// An alternative to the ternary plot for Working Suburbanites — kept ready to swap in (see
	// the commented-out markup further down) without needing to rebuild it from scratch.
	// import RadarTriangle from "$lib/charts/RadarTriangle.svelte";

	import { SECTION_CONFIG } from "$lib/config/fiveTorontosSections.js";
	import clustersSummary from "$data/clustering_neighbourhoods/clusters_summary.json";
	import clustersMetadata from "$data/clustering_neighbourhoods/clusters_metadata.json";
	import ctClusters from "$data/clustering_neighbourhoods/ct_clusters.geo.json";
	import ctValues from "$data/clustering_neighbourhoods/ct_values.json";

	// clusters_summary.json is already sorted progressive -> conservative (display_order 1-5),
	// but sort defensively rather than assume the file's row order never changes.
	const clusters = [...clustersSummary].sort((a, b) => a.display_order - b.display_order);

	const pct = (v) => `${v.toFixed(0)}%`;

	// Fixed socioeconomic vars shown in every section. `delta` is the cluster's
	// percentage-point difference from the Toronto-wide figure, already computed in
	// clusters_summary.json — shown in green/red beside the value (see
	// $lib/tables/ClusterSummaryTable.svelte).
	const socioeconomicFor = (c) => [
		{ label: "Renters", value: pct(c.demographics.pct_renter), delta: c.demographics_vs_toronto.pct_renter.diff_vs_toronto },
		{ label: "Visible minority", value: pct(c.demographics.pct_visible_minority), delta: c.demographics_vs_toronto.pct_visible_minority.diff_vs_toronto },
		{ label: "Moved in last 5 years", value: pct(c.demographics.pct_migrant_5yr), delta: c.demographics_vs_toronto.pct_migrant_5yr.diff_vs_toronto },
		{ label: "Bachelor's degree+", value: pct(c.demographics.pct_bachelor_or_higher), delta: c.demographics_vs_toronto.pct_bachelor_or_higher.diff_vs_toronto },
		{ label: "Commute by car", value: pct(c.demographics.pct_commute_car), delta: c.demographics_vs_toronto.pct_commute_car.diff_vs_toronto },
	];

	// Voting rows: cluster's actual vote share/turnout (vote-weighted, from elections.*)
	// alongside its delta vs. the Toronto-wide vote-weighted figure in clusters_metadata.json.
	const torontoElections = clustersMetadata.toronto_benchmark.elections;
	function votingRowsFor(cluster, specs) {
		return specs.map(({ label, election, field }) => {
			const value = cluster.elections[election][field];
			const torontoValue = torontoElections[election][field];
			return { label, value: pct(value), delta: value - torontoValue };
		});
	}

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
	// map, or just the one group for a section map — see $lib/maps/ClusterMap.svelte.
	const allClustersLegend = clusters.map((c) => ({
		cluster_id: c.cluster_id,
		label: c.label,
		color: c.color,
		pct: c.population_share * 100,
	}));
	const legendFor = (cluster) => allClustersLegend.filter((r) => r.cluster_id === cluster.cluster_id);
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
	<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />

	<!-- TODO: finalize title/description/social image once the story's copy is set. -->
	<title>Place and Politics in Toronto</title>
	<meta name="description" content="Clustering Toronto's neighbourhoods into five political groups" />
	<meta name="author" content="School of Cities" />
	<link rel="canonical" href="https://schoolofcities.github.io/place-and-politics-toronto/five-torontos" />
	<meta property="og:title" content="Place and Politics in Toronto" />
	<meta name="og:description" content="Clustering Toronto's neighbourhoods into five political groups" />
	<meta property="og:type" content="article" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/five-torontos" />
	<meta property="og:locale" content="en_CA" />
</svelte:head>

<!-- Page is still in development — comment out this one line to unlock it for launch. -->
<PasswordGate />

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto - Part 6</h4>
		<div id="mini-line"></div>
		<h1>The Five Toronto's</h1>
		<h3><a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/">Aniket Kali</a> <br />October 2026</h3>
		<div id="mini-line"></div>
	</div>

	<div class="text">
		<p>
			Toronto may be one city on a map, but where you live can shape remarkably different
			experiences of it. Neighbourhoods separated by just a few subway stops can differ
			sharply in income, housing, access to transit and services, and even life expectancy –
			<a href="https://thelocal.to/life-expectancy-varies-by-almost-12-years-across-toronto-neighbourhoods/">which varies by almost 12 years</a>
			across the city. Those divides carry over into politics. Some parts of Toronto vote
			consistently, participate in large numbers, and share a clear political preference;
			elsewhere, voting is more divided or participation is much lower.
		</p>
		<p>
			Those differences matter beyond who wins an election. Areas with higher turnout
			contribute more votes relative to their eligible population, while governments make
			decisions about the transit people rely on, the homes they can afford, the services
			available in their neighbourhoods, and how public money is spent. Using voting patterns
			from Toronto's three most recent elections, we find five broad political geographies –
			five different Torontos shaped by different combinations of political participation,
			housing, income, migration, education, mobility, and the city's geography.
		</p>
	</div>

	<section class="intro-map">
		<ClusterMap
			tracts={ctClusters}
			activeClusterId={rotatingClusterId}
			legend={allClustersLegend}
			label="Map of Toronto rotating through each of the five political clusters, showing which census tracts belong to the currently highlighted group"
		/>
	</section>

	<div class="text">
		<p>
			The five groups below run broadly from Toronto's most consistently progressive
			neighbourhoods toward its more conservative ones. But they are not simply five steps
			along a left-right spectrum. Some are distinguished by their voting patterns, others by
			mobility, housing, socioeconomic characteristics, or – perhaps most importantly –
			consistently lower turnout. The names are shorthand for those tract-level patterns,
			rather than labels for the individual people who live there.
		</p>
	</div>

	{#each clusters as cluster, i}
		{@const config = SECTION_CONFIG[cluster.slug]}
		{@const clusterId = cluster.cluster_id}
		{@const color = cluster.color}
		<section class="cluster-section">
			<h2>Section {i + 1}: {cluster.label}</h2>

			<ClusterMap
				tracts={ctClusters}
				activeClusterId={clusterId}
				legend={legendFor(cluster)}
				label={`Map of Toronto highlighting the census tracts belonging to the ${cluster.label} cluster`}
			/>

			<ClusterSummaryTable
				socioeconomic={socioeconomicFor(cluster)}
				voting={votingRowsFor(cluster, config.votingSpecs)}
			/>

			<div class="text">
				{#if cluster.slug === "progressive-core"}
					<p>
						Rooted in the twin hearts of Toronto's West End and East End, this is one of
						the most consistently left-leaning parts of the city. These neighbourhoods vote
						for the NDP at much higher rates, even in historically bad years for the party,
						while giving considerably less support to Conservatives across levels of
						government. Olivia Chow – a former NDP MP and city councillor – also performed
						particularly strongly here in the formally non-partisan 2023 mayoral race.
						Participation is high as well: turnout sits consistently above the city average
						across all three elections.
					</p>
					<p>
						The makeup of this segment is distinguished by its higher presence of renters,
						dense urban living, and university degrees. That combination of educated,
						renter-heavy neighbourhoods and progressive voting is consistent with a
						<a href="https://wid.world/news-article/changing-political-cleavages-in-21-western-democracies/">broader shift documented across many Western democracies</a>,
						including
						<a href="https://www.mattpolacko.com/_files/ugd/2876d8_177a7fd90b264b8d9cf1d2973c75b727.pdf">research</a>
						<a href="https://thetyee.ca/Culture/2021/06/15/Thomas-Piketty-New-Data-Tells-About-Canadian-Left/">on Canada</a>,
						in which the electoral base of the left has increasingly moved toward highly
						educated and
						<a href="https://fortune.com/2024/03/16/homeowners-red-renters-blue-broken-housing-market-polarized-political-culture/">economically downward</a>
						urban voters.
					</p>
					<p>
						Toronto's geography also has deeper local roots. Many of these areas were
						centres of
						<a href="https://www.heritagetoronto.org/explore/reform-city/labour-reform/">immigrant labour organization</a>,
						left-wing politics, and later neighbourhood-based urban reform like
						<a href="https://www.thecanadianencyclopedia.ca/en/article/toronto-feature-spadina-expressway">the fight against the Spadina Expressway</a>.
						Research on Toronto's political geography finds that neighbourhood political
						patterns <a href="https://academic.daniels.utoronto.ca/urbangenome/2018/09/22/political-order-of-the-city/">can persist across elections</a> even as the people living within them
						change, with a longstanding progressive-core/suburban cleavage closely related
						to urban form and transportation. The people have changed, but some of that
						political culture has persisted beyond its earlier inhabitants.
					</p>
				{:else if cluster.slug === "mobile-middle"}
					<p>
						If the Progressive Core represents the city's strongest and most consistent
						concentration of progressive votes, the Mobile Middle forms a softer and more
						geographically scattered edge around it. It also gives more votes to progressive
						candidates and parties and fewer to Conservatives than Toronto overall, but the
						differences are less pronounced. What distinguishes the group demographically is
						mobility: it is the youngest of the five, has the smallest households, the
						highest shelter-cost burden, and the largest recent-migrant share.
					</p>
					<p>
						Its geography helps put those numbers in context. The group combines
						<a href="https://www.theglobeandmail.com/real-estate/article-toronto-rental-apartment-construction-condos-data/">newer condos and rental towers</a>
						with older urban neighbourhoods across the central city and nearby parts of
						Scarborough, rather than representing one historically continuous political
						region. Toronto's central areas have long had
						<a href="https://www.toronto.ca/wp-content/uploads/2017/08/8dbf-Living-in-Downtown-and-the-Centres.pdf">younger, smaller, and more mobile households</a>,
						while more recent housing growth has increasingly taken the form of
						<a href="https://www.toronto.ca/legdocs/mmis/2024/ph/bgrd/backgroundfile-247209.pdf">mid- and high-rise apartments</a>,
						including a large rented-condominium market. In 2021, nearly two-thirds of
						occupied dwellings in downtown Toronto were condominiums, and
						<a href="https://www.statcan.gc.ca/o1/en/plus/3237-condo-market-toronto-and-vancouver-home-investment-and-increasingly-rental-property">more than half of those condos were rented</a>.
						These areas share relatively high renting, education, and residential mobility,
						but not the same electoral intensity as the Progressive Core: turnout is much
						closer to the Toronto average, and NDP and Chow support are lower. It is
						therefore better understood as a present-day electoral similarity between
						neighbourhoods with quite different histories than as evidence of a shared
						political identity or attachment.
					</p>
				{:else if cluster.slug === "civic-professionals"}
					<p>
						It is in neighbourhoods like The Beaches, Leaside, and Midtown where
						participation is highest. These are also amongst the city's most educated and
						highest-income areas, with the lowest visible minority share of the five
						groups. Their voting patterns are distinctive as well: provincial Liberal
						support is highest here, the NDP performs poorly, and Josh Matlow received
						roughly twice his citywide mayoral vote share in 2023. Rather than indicating
						particular attitudes toward government, the data establish a simpler pattern:
						these are affluent, highly educated neighbourhoods where residents vote at
						unusually high rates and tend to favour Liberal and moderate-reform candidates
						over either the NDP or Conservatives.
					</p>
					<div class="inline-graphic">
						<ScatterHighlight values={ctValues} {...config.scatter} {clusterId} {color} />
					</div>
					<p>
						There is some historical precedent for that combination. Several of these
						neighbourhoods sit along the edges of Old Toronto and overlap with
						neighbourhoods active in the city's
						<a href="https://activehistory.ca/blog/2015/12/10/how-did-1970s-reform-change-toronto/">urban reform politics</a>
						of the 1960s and 1970s. Residents and ratepayer organizations mobilized around
						development, environmental protection, neighbourhood preservation, and greater
						public involvement in planning. Toronto's reform coalition itself crossed
						conventional partisan lines: Mayor
						<a href="https://thecanadianencyclopedia.ca/en/article/david-crombie">David Crombie</a>
						was a Progressive Conservative, while reform politicians also came from
						Liberal, NDP, and independent traditions. Historians describe the movement as
						<a href="https://www.thecanadianencyclopedia.ca/en/article/urban-reform">heterogeneous rather than uniformly left-wing</a>,
						united particularly around
						<a href="https://spacing.ca/toronto/2011/11/11/torontos-current-urban-planning-conflicts-rooted-in-the-past/">planning and neighbourhood issues</a>.
						Those precedents do not demonstrate continuity in individual attitudes, but
						they provide useful context for a contemporary geography that remains highly
						participatory, liberal-leaning, and less strongly aligned with the NDP than the
						Progressive Core.
					</p>
				{:else if cluster.slug === "settled-conservatives"}
					<p>
						Spanning much of Toronto's established inner suburbs, the Settled Conservatives
						are a product of the region's
						<a href="https://www.toronto.ca/explore-enjoy/history-art-culture/online-exhibits/web-exhibits/web-exhibits-community-neighbourhoods/your-home-our-city/your-home-our-city-suburban-growth/">postwar promise</a>:
						detached housing, homeownership, and greater automobile use. Today, they are the
						oldest and most homeowner-heavy of the five groups, while driving more and
						taking transit less than anyone else. Their electoral pattern is similarly
						clear. These neighbourhoods give the highest shares to the Ontario PCs and
						federal Conservatives, the lowest or near-lowest shares to the NDP, and favoured
						Ana Bailão over Olivia Chow in the 2023 mayoral election. Participation, unlike
						in the Working Suburbanites, remains close to the city average.
					</p>
					<p>
						That pattern fits a much longer political divide between Toronto's older core
						and its postwar suburbs. Suburbs like
						<a href="https://en.wikipedia.org/wiki/Etobicoke">Etobicoke</a>,
						<a href="https://en.wikipedia.org/wiki/North_York">North York</a>, and
						<a href="https://en.wikipedia.org/wiki/Scarborough,_Toronto">Scarborough</a>
						developed under different municipal governments focused more on
						<a href="https://www.thestar.com/news/gta/toronto-s-political-divide-is-real-but-it-can-change-especially-in-the-suburbs/article_a903777f-15aa-54d3-a000-dc726b9e3a38.html">private homes and cars</a>,
						before amalgamation in 1998. Political geographer Zack Taylor has documented an
						enduring city-suburb divide in Toronto voting that
						<a href="https://www.utsc.utoronto.ca/geography/professor-taylor-discusses-ford-nation">predates Rob Ford's conservatism</a>;
						in the 2010 mayoral election, for example, the former Metropolitan Toronto
						suburbs voted heavily for Ford while the old City of Toronto went strongly for
						George Smitherman. Related research finds that Toronto's broader
						progressive-core/conservative-suburban cleavage is closely associated with
						housing form and transportation patterns. The geography of the Settled
						Conservatives closely overlaps with that longer-running suburban political
						divide, even as the suburbs themselves have changed considerably since they
						were first built.
					</p>
				{:else if cluster.slug === "working-suburbanites"}
					<p>
						It is easy to look at the maps and conclude that much of the inner suburbs is
						simply made up of working-class conservatives, but the data complicates that
						story. More than anything, what distinguishes these neighbourhoods is low
						participation. Turnout is lower than in every other cluster across the
						municipal, provincial, and federal elections, even though this is Toronto's
						largest group at nearly one million people. These neighbourhoods also have the
						lowest approximate income and university attainment, the highest visible
						minority share, some of the largest households, and the longest commutes.
					</p>
					<div class="inline-graphic">
						<TernaryProfilePlot values={ctValues} vars={config.ternaryVars} {clusterId} {color} />
						<!-- Alternative graphic for this section — a radar/triangle hybrid instead of
							 the normalized ternary above. Sized to fit this same inline layout; swap it
							 in by uncommenting this and commenting out the TernaryProfilePlot above (and
							 its import at the top of the script).
						<RadarTriangle {clusters} activeClusterId={clusterId} />
						-->
					</div>
					<p>
						Their voting patterns are less straightforward than those of the Settled
						Conservatives beside them. Ontario PC support is relatively high, but the
						federal Liberals still receive a clear majority, while Chow leads the mayoral
						vote. Previous work has documented a longer-term rise in Conservative support
						in
						<a href="https://schoolofcities.github.io/gta-immigration/political-shifts">immigrant- and minority-heavy GTA ridings</a>,
						particularly at the provincial level, pointing toward
						<a href="https://schoolofcities.github.io/gta-immigration/rightward-minorities">disillusionment with an incomplete multiculturalism</a>.
					</p>
					<p>
						More broadly, these political differences overlap with a broader geography of
						inequality. Research on Toronto's inner suburbs has
						<a href="https://www.utsc.utoronto.ca/sociology/getting-heart-issues-matter-inner-suburbs">documented</a>
						lower incomes, weaker access to mass transit and city services, and
						longstanding underinvestment compared with more affluent parts of the city.
						<a href="https://www.thestar.com/news/gta/we-are-fighting-a-big-machine-gentrification-is-pulling-apart-toronto-s-communities-how-do/article_98d623ff-56a0-5fff-a73e-3964086febfc.html">Other reporting</a>
						has traced how rising housing costs and gentrification have displaced
						lower-income and immigrant households outward from parts of the core. Surveys
						conducted through the
						<a href="https://schoolofcities.utoronto.ca/research/community-voices-a-study-into-what-residents-value-in-torontos-inner-suburbs/">Community Voices project</a>
						also found that residents themselves placed particular importance on reliable
						transportation, neighbourhood services, affordable housing, and safety. That
						makes the group's consistently low turnout important in its own right: many of
						the neighbourhoods facing some of the city's largest material and service
						disparities are also contributing fewer votes relative to their adult-citizen
						populations.
					</p>
				{/if}
			</div>

			<!-- Progressive Core / Settled Conservatives get a full-width strip plot underneath
				 the body copy. Civic Professionals' scatter and Working Suburbanites' ternary
				 plot are instead placed inline, between that section's two paragraphs above
				 (see `.inline-graphic`), so the second paragraph wraps around them. -->
			{#if config.graphic === "strip"}
				<div class="graphic">
					<StripPlot values={ctValues} variables={config.stripVars} {clusterId} {color} />
				</div>
			{/if}
		</section>
	{/each}

	<section class="methods-section">
		<h2>Data &amp; Methods</h2>
		<div class="text">
			<p>
				We analyzed all 585 Toronto census tracts using results from three recent
				elections: the 2023 mayoral race, the 2025 Ontario election, and the 2025 federal
				election. Because voting polls and census tracts do not share the same boundaries,
				poll-level votes were first interpolated to census tracts. Turnout is measured
				using the number of adult citizens, while party and candidate support is calculated
				from valid votes cast.
			</p>
			<p>
				We grouped neighbourhoods using their voting and turnout alone – not their
				demographics. For each election, we considered both how a tract differed from
				Toronto overall and how it differed from its own ward or riding, giving those
				citywide and local perspectives equal weight. We also balanced the three elections
				so that no single race dominated. We then used principal component analysis (PCA)
				to condense overlapping electoral measures and k-means clustering to group tracts
				with similar political profiles.
			</p>
			<p>
				We tested several alternative approaches and between three and seven clusters.
				Five offered a useful balance: three produced slightly stronger statistical
				separation but merged political geographies that were substantively different,
				while six and seven produced clearly weaker groups. The final five should
				therefore be understood as a useful simplification of Toronto's continuous
				political geography, not five naturally fixed types.
			</p>
			<p>
				After creating the clusters, we joined 2021 Census data on age, income, housing,
				migration, racialization, education, commuting and other characteristics to
				understand the places within them. These demographics did not determine the
				groups and should not be read as explaining how any individual voted. The names –
				Progressive Core, Mobile Middle, Civic Professionals, Settled Conservatives and
				Working Suburbanites – are similarly descriptive shorthand applied after the
				analysis.
			</p>
			<p>
				For full details on the data, interpolation, model selection, sensitivity tests,
				aggregation and limitations, see our complete
				<a href="https://github.com/schoolofcities/place-and-politics-toronto/tree/main/analysis/clustering_neighbourhoods">Data and Methods</a>
				and the reproducible analysis notebooks:
				<a href="https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/clustering_neighbourhoods/02_model_exploration.ipynb">model exploration</a>,
				<a href="https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/clustering_neighbourhoods/03_cluster_interpretation.ipynb">cluster interpretation</a>,
				and
				<a href="https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/clustering_neighbourhoods/04_process_ct_to_cluster.ipynb">final data processing</a>.
			</p>
		</div>
	</section>

	<div id="mini-line"></div>

	<div class="info">
		<p>
			Thanks to Jeff Allen and Zack Taylor for reviewing the methods, research, and text
			behind this piece, and to Felicity Heyworth for reviewing the text.
		</p>
	</div>
</main>

<style>
	.intro-map,
	.cluster-section,
	.methods-section {
		margin: 0 auto 40px;
		max-width: 850px;
		width: calc(100% - 20px);
	}
	.cluster-section h2,
	.methods-section h2 {
		font-family: "Source Serif Pro", serif;
		text-align: center;
		margin-bottom: 16px;
	}
	.graphic {
		margin-top: 20px;
	}

	/* Contains the `.inline-graphic` float below so the section's own height (and anything
	   after it) accounts for it, rather than the float spilling past the end of the text. */
	.text::after {
		content: "";
		display: table;
		clear: both;
	}

	/* Civic Professionals' scatter plot and Working Suburbanites' ternary plot sit between
	   that section's two paragraphs, floated so the second paragraph wraps around them and
	   continues full-width once it reads past the bottom of the graphic — rather than a hard
	   break to a separate block below. Stacked full-width on mobile instead (see the media
	   query below): a narrow column doesn't leave enough room beside a floated graphic for
	   wrapped text to read well. */
	.inline-graphic {
		max-width: 380px;
		margin: 16px auto;
	}

	@media (min-width: 601px) {
		.inline-graphic {
			float: left;
			width: 320px;
			max-width: 50%;
			margin: 4px 24px 16px 0;
		}
	}

	@media (max-width: 600px) {
		.intro-map,
		.cluster-section,
		.methods-section {
			margin-bottom: 36px;
		}
		.graphic {
			margin-top: 18px;
		}
	}
</style>
