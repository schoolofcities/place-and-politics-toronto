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

	// TODO: replace with real per-section copy — placeholder text so the layout (map ->
	// summary tables -> body copy -> graphic) can be reviewed before final copy exists.
	const LOREM_IPSUM =
		"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor " +
		"incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud " +
		"exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.";
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

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto</h4>
		<div id="mini-line"></div>
		<h1>The Five Toronto's</h1>
		<!-- TODO: replace with the real author name(s) and publish date. -->
		<h3>[Author Name] <br />[Month Day, Year]</h3>
		<div id="mini-line"></div>
	</div>

	<div class="text">
		<p>There are five political groups in Toronto, each a cluster of census tracts that tend to vote alike across the 2023 mayoral, 2025 provincial, and 2025 federal elections.</p>
		<!-- TODO: replace with final intro copy. -->
	</div>

	<section class="intro-map">
		<ClusterMap tracts={ctClusters} activeClusterId={rotatingClusterId} legend={allClustersLegend} />
	</section>

	<div class="text">
		<p>{LOREM_IPSUM}</p>
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

			{#if config.graphic === "scatter" || config.graphic === "ternary"}
				<!-- Smaller, left-aligned graphic with the body copy wrapping around its right
					 side on desktop — the graphic has to come before the text in the markup for
					 the float-wrap to work, so these two graphics skip the shared text-then-graphic
					 order below. -->
				<div class="float-wrap">
					<div class="float-graphic">
						{#if config.graphic === "scatter"}
							<ScatterHighlight values={ctValues} {...config.scatter} {clusterId} {color} />
						{:else if config.graphic === "ternary"}
							<TernaryProfilePlot values={ctValues} vars={config.ternaryVars} {clusterId} {color} />
							<!-- Alternative graphic for this section — a radar/triangle hybrid instead of
								 the normalized ternary above. Sized to fit this same half-page float-wrap
								 layout; swap it in by uncommenting this and commenting out the
								 TernaryProfilePlot above (and its import at the top of the script).
							<RadarTriangle {clusters} activeClusterId={clusterId} />
							-->
						{/if}
					</div>
					<div class="text float-text">
						<p>{LOREM_IPSUM}</p>
					</div>
				</div>
			{:else}
				<div class="text">
					<p>{LOREM_IPSUM}</p>
				</div>
				{#if config.graphic === "strip"}
					<div class="graphic">
						<StripPlot values={ctValues} variables={config.stripVars} {clusterId} {color} />
					</div>
				{/if}
			{/if}
		</section>
	{/each}

	<div class="text">
		<p>
			<em
				>These are tract-level political profiles, not individual voter types — a
				label like "{clusters[0]?.label}" describes the aggregate voting pattern of a
				group of census tracts, not any one person living there.</em
			>
		</p>
		<!-- TODO: closing section / methods link, and add a card for this story on the homepage (src/routes/+page.svelte). -->
	</div>
</main>

<style>
	.intro-map,
	.cluster-section {
		margin: 0 auto 50px;
		max-width: 850px;
		width: calc(100% - 20px);
	}
	.cluster-section h2 {
		font-family: "Source Serif Pro", serif;
		text-align: center;
		margin-bottom: 16px;
	}
	.graphic {
		margin-top: 24px;
	}

	/* Smaller, left-aligned graphic (Civic Professionals' scatter, Working Suburbanites'
	   ternary plot) with the body copy wrapping around its right side — a plain CSS float,
	   so the graphic must precede the text in the markup (see the template above) for the
	   wrap to happen. */
	.float-wrap {
		margin-top: 24px;
	}
	.float-wrap::after {
		content: "";
		display: table;
		clear: both;
	}
	.float-graphic {
		float: left;
		width: 50%;
		box-sizing: border-box;
		padding-right: 20px;
	}
	.float-text {
		/* override .text's own centering/max-width so it fills the space beside the float
		   instead of trying to center itself across the whole row */
		margin: 0;
		max-width: none;
		width: auto;
		padding: 0;
	}

	@media (max-width: 600px) {
		.intro-map,
		.cluster-section {
			margin-bottom: 36px;
		}
		.graphic {
			margin-top: 18px;
		}
		.float-graphic {
			float: none;
			width: 100%;
			padding-right: 0;
			margin-bottom: 16px;
		}
		.float-text {
			padding: 0 25px;
		}
	}
</style>
