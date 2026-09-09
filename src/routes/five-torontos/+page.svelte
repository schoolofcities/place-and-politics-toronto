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
	<meta property="og:title" content="Place and Politics in Toronto" />
	<meta name="og:description" content="Clustering Toronto's neighbourhoods into five political groups" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/five-torontos" />
</svelte:head>

<!-- Page is still in development — comment out this one line to unlock it for launch. -->
<PasswordGate />

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto</h4>
		<div id="mini-line"></div>
		<h1>The Five Toronto's</h1>
		<h3>Aniket Kali <br />September 2026</h3>
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
			elsewhere, residents move between parties or sit elections out altogether.
		</p>
		<p>
			Those differences matter beyond who wins an election. The people who participate most
			have a greater opportunity to make their priorities visible, while governments make
			decisions about the transit people rely on, the homes they can afford, the services
			available in their neighbourhoods, and how public money is spent. Using voting patterns
			from Toronto's three most recent elections, we find five broad political geographies –
			five different Torontos with different relationships to the city, shaped by where
			people live, the opportunities available to them, and whether they believe politics can
			make their lives better.
		</p>
	</div>

	<section class="intro-map">
		<ClusterMap tracts={ctClusters} activeClusterId={rotatingClusterId} legend={allClustersLegend} />
	</section>

	<div class="text">
		<p>
			The five groups below run broadly from Toronto's most consistently progressive
			neighbourhoods toward its more conservative ones. But they are not simply five steps
			along a left-right spectrum. Some are distinguished by ideology, others by mobility,
			civic participation, homeownership, or – perhaps most importantly – by opting out of
			politics altogether. The names are shorthand for those defining characteristics, rather
			than labels for the individual people who live there.
		</p>
	</div>

	{#each clusters as cluster, i}
		{@const config = SECTION_CONFIG[cluster.slug]}
		{@const clusterId = cluster.cluster_id}
		{@const color = cluster.color}
		<section class="cluster-section">
			<h2>Section {i + 1}: {cluster.label}</h2>

			<ClusterMap tracts={ctClusters} activeClusterId={clusterId} legend={legendFor(cluster)} />

			<ClusterSummaryTable
				socioeconomic={socioeconomicFor(cluster)}
				voting={votingRowsFor(cluster, config.votingSpecs)}
			/>

			<div class="text">
				{#if cluster.slug === "progressive-core"}
					<p>
						Rooted in the twin hearts of Toronto's West End and East End, this is one of
						the most left-leaning segments across the city, and perhaps even the country.
						Residents vote for the NDP at much higher rates, even in historically bad years
						for the party, while showing little interest in conservatives across all levels
						of government. Olivia Chow – a former NDP MP and the clearest progressive
						candidate in the formally non-partisan 2023 mayoral race – performed
						particularly strongly here. Equally, this crowd finds itself drawn to politics
						more than others, with turnout consistently higher than across the city as a
						whole.
					</p>
					<p>
						The makeup of this segment is distinguished by its higher presence of renters,
						dense urban living, and university degrees. The progressivism of these residents
						is strikingly in line with a
						<a href="https://wid.world/news-article/changing-political-cleavages-in-21-western-democracies/">growing trend across many Western democracies</a>:
						moving away from its former immigrant and working-class base, it is increasingly
						more educated yet
						<a href="https://fortune.com/2024/03/16/homeowners-red-renters-blue-broken-housing-market-polarized-political-culture/">economically downward</a>
						residents who identify most strongly with progressivism –
						<a href="https://www.mattpolacko.com/_files/ugd/2876d8_177a7fd90b264b8d9cf1d2973c75b727.pdf">including in</a>
						<a href="https://thetyee.ca/Culture/2021/06/15/Thomas-Piketty-New-Data-Tells-About-Canadian-Left/">Canada</a>. Still,
						these areas have a long history of immigrant-led cleaners' and garment unions,
						socialist and social-democratic politics, and urban reform movements culminating
						in the fight against the Spadina Expressway. The people have changed, but some
						of that political culture has persisted beyond its earlier inhabitants.
					</p>
				{:else if cluster.slug === "mobile-middle"}
					<p>
						If the Progressive Core is a story of political inheritance holding firm, then
						the Mobile Middle is about an oft-shifting edge around it. Politically, both
						share similar qualities, albeit less pronounced: more votes for progressive
						candidates and parties, fewer votes for conservatives, and much less of the deep
						NDP attachment found closer to the core. What most defines this group, though,
						is turnover and flexibility. It is the youngest of the five, has the smallest
						household sizes, the highest share facing heavy shelter costs, and by far the
						largest recent-migrant share – whether those newcomers arrived from elsewhere in
						the city, the country, or beyond.
					</p>
					<p>
						That mobility makes more sense when looking at the places this group comprises.
						It is a mix of newer condos and rental towers alongside older urban
						neighbourhoods sitting within reach of the denser core. That attracts young
						professionals looking for more attainable but nearby homes, recent arrivals
						establishing themselves in Toronto, and tenants who may not yet be as rooted in
						their neighbourhood. The result is an urban group whose politics resemble those
						of the Progressive Core, but without the same depth of political inheritance or
						attachment.
					</p>
				{:else if cluster.slug === "civic-professionals"}
					<p>
						It is in neighbourhoods like The Beaches, Leaside, and Midtown where residents
						turn out in numbers far higher than the average Torontonian. This is not
						terribly surprising when looking at the numbers: these are amongst the city's
						most educated, highest-income, and whitest areas. Politics is a space these
						residents already have access to, with high participation suggesting faith in
						a system they broadly believe to be working. The political form of that faith
						is usually liberal rather than left-wing: stronger support for Liberal
						parties, higher support for the reform-minded Josh Matlow in 2023, and an
						openness to change – but preferably when pursued cautiously.
					</p>
					<div class="inline-graphic">
						<ScatterHighlight values={ctValues} {...config.scatter} {clusterId} {color} />
					</div>
					<p>
						Several of these neighbourhoods trace their political history to the edges of
						Old Toronto – the much smaller city that existed before amalgamation in 1998.
						During Toronto's period of urban reform and renewal
						<a href="https://www.theglobeandmail.com/canada/toronto/article-yonge-and-eglinton-ground-zero-in-torontos-battle-to-reconcile-high/">in the 1970s</a>,
						residents across Midtown formed ratepayers associations to push back against
						large developments, advocate for environmental protection, and favour
						community planning over unchecked corporate growth. Their champion in the
						1970s was Mayor
						<a href="https://thecanadianencyclopedia.ca/en/article/david-crombie">David Crombie</a>,
						himself a Progressive Conservative, reflecting an openness
						<a href="https://activehistory.ca/blog/2020/10/13/did-you-hear-the-one-about-the-cardinal-the-rabbi-and-the-minister-spiritual-leaders-and-big-social-problems-in-1970s-toronto/">beyond partisanship</a>
						to reform and change. Still, there were limits to that reformism: when
						Crombie's successor John Sewell pushed further on police accountability and
						acceptance of Toronto's queer community, it was
						<a href="https://www.tvo.org/article/how-homophobia-tainted-the-1980-toronto-municipal-election">seen as contentious</a>
						and
						<a href="https://activehistory.ca/blog/2015/12/10/how-did-1970s-reform-change-toronto/">beyond the bounds</a>
						of the community planning and housing reforms many residents had supported.
					</p>
				{:else if cluster.slug === "settled-conservatives"}
					<p>
						Spanning much of Toronto's established inner suburbs, the Settled Conservatives
						are a product of the region's postwar promise: detached housing, homeownership,
						and automobile access. Today, they remain the oldest and most homeowner-heavy of
						the five groups, while driving more and taking transit less than anyone else.
						Politically, they form the city's clearest conservative constituency: giving
						substantially more support to the Ontario PCs and federal Conservatives,
						overwhelmingly rejecting the NDP, and favouring the more centrist Ana Bailão over
						Olivia Chow in the formally non-partisan 2023 mayoral race. Unlike the
						lower-turnout Working Suburbanites around them, however, these are established
						communities whose residents continue to participate at roughly the city average.
					</p>
					<p>
						Their politics have roots in the way Metropolitan Toronto grew after the Second
						World War. While Old Toronto developed around denser neighbourhoods, transit,
						and increasingly collective ideas about what municipal government could provide,
						former suburbs like Etobicoke, North York, and Scarborough grew around
						<a href="https://www.thestar.com/news/gta/toronto-s-political-divide-is-real-but-it-can-change-especially-in-the-suburbs/article_a903777f-15aa-54d3-a000-dc726b9e3a38.html">private homes, cars, and a leaner conception of local government</a>
						focused more heavily on property, roads, and basic services. Political geographer
						Zack Taylor argues that this urban-suburban divide
						<a href="https://www.utsc.utoronto.ca/geography/professor-taylor-discusses-ford-nation">long predates Rob Ford's conservatism</a>:
						Ford simply gave particularly clear expression to a political tradition already
						embedded in Toronto's geography. Even decades after amalgamation brought these
						different visions into the same city government, this group remains the clearest
						political descendant of a postwar suburban Toronto built around the house and
						the car.
					</p>
				{:else if cluster.slug === "working-suburbanites"}
					<p>
						It is easy to look at the maps and numbers and conclude that much of the inner
						suburbs is made up of working-class conservatives, but the data complicates
						that story. More than anything, what marks out this group is abstention:
						residents turn out at significantly lower rates than other Torontonians,
						despite making up the city's largest group – nearly one million people. This
						segment has the lowest income and university attainment, the highest
						racialized share, some of the largest households, and the longest commutes.
						Nearly four in five residents are racialized, while turnout falls below every
						other group across the municipal, provincial, and federal elections. The
						politics of those who do vote are also less straightforward than the Settled
						Conservatives beside them: stronger Conservative support provincially, a clear
						Liberal advantage federally, and considerably weaker attachment to the NDP.
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
						It is true that residents who do vote here have
						<a href="https://schoolofcities.github.io/gta-immigration/political-shifts">shifted noticeably toward conservative parties and politicians</a>
						over recent decades, but that likely corresponds in part to disillusionment
						with
						<a href="https://schoolofcities.github.io/gta-immigration/rightward-minorities">an incomplete multiculturalism</a>
						in Canada that has failed to deliver beyond slogans and headlines. Hard work
						does not necessarily yield good pay and stability, while these parts of the
						city suffer from underinvestment, poorer access to services, long journeys
						across Toronto, and subpar transit. More than simple political disinterest,
						the group's low participation points toward an unequal political incorporation
						of different parts of Toronto, building on a legacy that has been
						<a href="https://www.thestar.com/news/gta/we-are-fighting-a-big-machine-gentrification-is-pulling-apart-toronto-s-communities-how-do/article_98d623ff-56a0-5fff-a73e-3964086febfc.html">pushing working-class immigrants</a>
						farther from the city's core. The result is not Toronto's most conservative
						population so much as the one most weakly connected to the political system
						around it.
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
				Our analysis works at the census tract level across Toronto's 585 tracts. For each
				tract, we combine census demographic data with results from three elections: the
				2023 mayoral race, the 2025 Ontario provincial election, and the 2025 federal
				election. We used publicly available election results, supplemented by a cleaned
				dataset provided by Zack Taylor, and applied areal interpolation to estimate
				tract-level results from voting polls whose boundaries do not line up neatly with
				census tracts.
			</p>
			<p>
				We grouped tracts into five clusters using their voting patterns and turnout, not
				their demographics. For each election, we considered both how a tract voted
				compared with Toronto overall and how it differed from its own ward or riding, with
				these blocks weighted equally. We then used principal component analysis (PCA) to
				condense these related measures into a smaller set of patterns, before applying
				k-means clustering to group similar tracts. Five groups provided a useful balance
				between capturing meaningful differences and keeping the results interpretable.
				Demographic and socioeconomic characteristics were joined afterward and did not
				determine the clusters.
			</p>
			<p>
				Each group is described using the same broad set of demographic measures –
				including income, renting, racialization, recent migration, education, and
				commuting – alongside actual vote shares and turnout. These are shown relative to
				the Toronto average where useful, making it easier to see what most distinguishes
				one group from another. The group names are descriptive shorthand for those
				patterns rather than labels for every person living within them.
			</p>
			<p>
				This is tract-level analysis describing the political and demographic character of
				places, not the behaviour of individual voters. The five groups are also a
				simplification of more continuous and overlapping variation across Toronto, rather
				than a claim that the city divides neatly into exactly five types. Some census
				tracts sit close to the boundaries between groups, while considerable variation
				remains within each one.
			</p>
		</div>
	</section>
</main>

<style>
	.intro-map,
	.cluster-section,
	.methods-section {
		margin: 0 auto 50px;
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
		margin-top: 24px;
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
			width: 280px;
			max-width: 45%;
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
