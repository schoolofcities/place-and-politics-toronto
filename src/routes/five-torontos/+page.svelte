<script>
	// ── FIRST-DRAFT OUTLINE ──────────────────────────────────────────────────────────
	// This route is a scaffold, not a finished story: it wires the real data
	// (src/data/clustering_neighbourhoods/*, produced by
	// analysis/clustering_neighbourhoods/process_ct_to_cluster.ipynb) into a page shaped
	// like the outline below, using placeholder copy and first-pass chart components.
	// Everything here — copy, chart choice, layout, colours — is expected to change once
	// there's a final design to build to.
	//
	//   Intro: "there are 5 political groups in Toronto" + rotating map of all 5
	//   One section per cluster: header -> map -> summary tables -> body copy -> graphic
	//     Section 1: Progressive Core       — double strip plot
	//     Section 2: Mobile Middle          — grouped-bar comparison
	//     Section 3: Civic Professionals    — income-vs-education scatter
	//     Section 4: Settled Conservatives  — triple strip plot
	//     Section 5: Working Suburbanites   — normalized triangle (visible minority / income / education)
	//   (display order per an earlier edit: Settled Conservatives 4th, Working Suburbanites 5th)

	import { onMount, onDestroy } from "svelte";
	import Top from "$lib/TopSofC.svelte";
	import "../styles.css";

	import ClusterMap from "$lib/ClusterMap.svelte";
	import ClusterSummaryTable from "$lib/ClusterSummaryTable.svelte";
	import StripPlot from "$lib/StripPlot.svelte";
	import ClusterCompareBars from "$lib/ClusterCompareBars.svelte";
	import ScatterHighlight from "$lib/ScatterHighlight.svelte";
	import TernaryProfilePlot from "$lib/profiles/TernaryProfilePlot.svelte";
	// A radar/triangle alternative to the ternary above — kept here, commented out, in case it
	// gets swapped back in later (see the commented markup near the bottom of the template).
	// import RadarTriangle from "$lib/profiles/RadarTriangle.svelte";

	import clustersSummary from "$data/clustering_neighbourhoods/clusters_summary.json";
	import clustersMetadata from "$data/clustering_neighbourhoods/clusters_metadata.json";
	import ctClusters from "$data/clustering_neighbourhoods/ct_clusters.geo.json";
	import ctValues from "$data/clustering_neighbourhoods/ct_values.json";

	// clusters_summary.json is already sorted progressive -> conservative (display_order 1-5),
	// but sort defensively rather than assume the file's row order never changes.
	const clusters = [...clustersSummary].sort((a, b) => a.display_order - b.display_order);

	const pct = (v) => `${v.toFixed(0)}%`;

	// Fixed socioeconomic vars shown in every section (per the outline). `delta` is the
	// cluster's percentage-point difference from the Toronto-wide figure, already computed
	// in clusters_summary.json — shown in green/red beside the value (see
	// $lib/ClusterSummaryTable.svelte).
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

	// Per-section config: which 5 voting rows to show (per the story brief), and which
	// first-draft graphic to render. `graphic` is deliberately just a switch key — swap the
	// component or props per section without restructuring the page once the final chart
	// choices are made.
	const SECTION_CONFIG = {
		"progressive-core": {
			votingSpecs: [
				{ label: "Municipal: Chow", election: "mayor_2023", field: "chow" },
				{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
				{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
				{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
				{ label: "Federal: NDP", election: "federal_2025", field: "ndp" },
			],
			graphic: "strip",
			stripVars: [
				{ key: "pct_renter", label: "% renter" },
				{ key: "pct_commute_car", label: "% commute by car" },
			],
		},
		"mobile-middle": {
			votingSpecs: [
				{ label: "Municipal: Chow", election: "mayor_2023", field: "chow" },
				{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
				{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
				{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
				{ label: "Federal: Liberal", election: "federal_2025", field: "liberal" },
			],
			// No graphic for this section (the grouped-bar comparison was removed on request).
			graphic: null,
		},
		"civic-professionals": {
			votingSpecs: [
				{ label: "Municipal: Matlow", election: "mayor_2023", field: "matlow" },
				{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
				{ label: "Provincial: Liberal", election: "provincial_2025", field: "liberal" },
				{ label: "Federal: Liberal", election: "federal_2025", field: "liberal" },
				{ label: "Federal turnout", election: "federal_2025", field: "turnout" },
			],
			graphic: "scatter",
			scatter: {
				xKey: "income_median",
				yKey: "pct_bachelor_or_higher",
				xLabel: "Median income ($)",
				yLabel: "Bachelor's degree+ (%)",
				xFormat: (v) => `$${Math.round(v / 1000)}k`,
				yFormat: (v) => `${v.toFixed(0)}%`,
			},
		},
		"settled-conservatives": {
			votingSpecs: [
				{ label: "Municipal: Bailão", election: "mayor_2023", field: "bailao" },
				{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
				{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
				{ label: "Federal: Conservative", election: "federal_2025", field: "conservative" },
				{ label: "Federal: Liberal", election: "federal_2025", field: "liberal" },
			],
			graphic: "strip",
			stripVars: [
				{ key: "pct_renter", label: "% renter (lower = more homeowners)" },
				{ key: "avg_age", label: "Average age", domain: [30, 60], tickStep: 5 },
				{ key: "pct_commute_car", label: "% commute by car" },
			],
		},
		"working-suburbanites": {
			votingSpecs: [
				{ label: "Municipal: Others", election: "mayor_2023", field: "other" },
				{ label: "Municipal turnout", election: "mayor_2023", field: "turnout" },
				{ label: "Provincial: NDP", election: "provincial_2025", field: "ndp" },
				{ label: "Provincial: PC", election: "provincial_2025", field: "pc" },
				{ label: "Federal: Conservative", election: "federal_2025", field: "conservative" },
			],
			graphic: "ternary",
			// [bottom-left, bottom-right, top] — see $lib/profiles/TernaryProfilePlot.svelte.
			ternary: {
				vars: [
					{ key: "pct_visible_minority", label: "% Visible Minority" },
					{ key: "income_median", label: "Median income" },
					{ key: "pct_bachelor_or_higher", label: "% Bachelor's degree+" },
				],
			},
		},
	};

	// Toronto-wide benchmark row, used by the bar/dumbbell comparison charts.
	const torontoBenchmark = {};
	for (const rec of clustersSummary) {
		for (const [k, v] of Object.entries(rec.demographics_vs_toronto)) {
			torontoBenchmark[k] = v.value - v.diff_vs_toronto; // back out the Toronto value once
		}
		break;
	}
	function compareRows(cluster, vars) {
		return vars.map((v) => ({
			label: v.label,
			clusterValue: cluster.demographics[v.key] ?? ctValues.find((d) => d.cluster_id === cluster.cluster_id)?.[v.key],
			torontoValue: torontoBenchmark[v.key],
			format: v.format,
		}));
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
	// map, or just the one group for a section map — see $lib/ClusterMap.svelte.
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
		<section class="cluster-section">
			<h2>Section {i + 1}: {cluster.label}</h2>

			<ClusterMap tracts={ctClusters} activeClusterId={cluster.cluster_id} legend={legendFor(cluster)} />

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
							<ScatterHighlight
								values={ctValues}
								xKey={config.scatter.xKey}
								yKey={config.scatter.yKey}
								xLabel={config.scatter.xLabel}
								yLabel={config.scatter.yLabel}
								xFormat={config.scatter.xFormat}
								yFormat={config.scatter.yFormat}
								clusterId={cluster.cluster_id}
								color={cluster.color}
							/>
						{:else if config.graphic === "ternary"}
							<TernaryProfilePlot
								values={ctValues}
								vars={config.ternary.vars}
								clusterId={cluster.cluster_id}
								color={cluster.color}
							/>
							<!-- Alternative graphic for this section — a radar/triangle hybrid instead of
								 the normalized ternary above. Sized to fit this same half-page float-wrap
								 layout; swap it in by uncommenting this and commenting out the
								 TernaryProfilePlot above (and its import at the top of the script).
							<RadarTriangle {clusters} activeClusterId={cluster.cluster_id} />
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

				{#if config.graphic}
					<div class="graphic">
						{#if config.graphic === "strip"}
							<StripPlot
								values={ctValues}
								variables={config.stripVars}
								clusterId={cluster.cluster_id}
								color={cluster.color}
							/>
						{:else if config.graphic === "bars"}
							<ClusterCompareBars rows={compareRows(cluster, config.compareVars)} color={cluster.color} />
						{/if}
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
