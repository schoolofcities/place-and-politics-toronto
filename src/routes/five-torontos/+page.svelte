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
	//     Section 5: Working Suburbanites   — dumbbell comparison
	//   (display order per an earlier edit: Settled Conservatives 4th, Working Suburbanites 5th)

	import { onMount, onDestroy } from "svelte";
	import Top from "$lib/TopSofC.svelte";
	import "../styles.css";

	import ClusterMap from "$lib/ClusterMap.svelte";
	import ClusterSummaryTable from "$lib/ClusterSummaryTable.svelte";
	import StripPlot from "$lib/StripPlot.svelte";
	import ClusterCompareBars from "$lib/ClusterCompareBars.svelte";
	import ScatterHighlight from "$lib/ScatterHighlight.svelte";
	import DumbbellChart from "$lib/DumbbellChart.svelte";

	import clustersSummary from "$data/clustering_neighbourhoods/clusters_summary.json";
	import clustersMetadata from "$data/clustering_neighbourhoods/clusters_metadata.json";
	import ctClusters from "$data/clustering_neighbourhoods/ct_clusters.geo.json";
	import ctValues from "$data/clustering_neighbourhoods/ct_values.json";

	// clusters_summary.json is already sorted progressive -> conservative (display_order 1-5),
	// but sort defensively rather than assume the file's row order never changes.
	const clusters = [...clustersSummary].sort((a, b) => a.display_order - b.display_order);

	const pct = (v) => `${v.toFixed(0)}%`;
	const dollars = (v) => `$${Math.round(v).toLocaleString()}`;

	// Fixed socioeconomic vars shown in every section (per the outline).
	const socioeconomicFor = (c) => [
		{ label: "Renters", value: pct(c.demographics.pct_renter) },
		{ label: "Visible minority", value: pct(c.demographics.pct_visible_minority) },
		{ label: "Migrated in last 5 years", value: pct(c.demographics.pct_migrant_5yr) },
		{ label: "Bachelor's degree+", value: pct(c.demographics.pct_bachelor_or_higher) },
		{ label: "Commute by car", value: pct(c.demographics.pct_commute_car) },
	];

	// Per-section config: which voting numbers to show, and which first-draft graphic to
	// render. `graphic` is deliberately just a switch key — swap the component or props
	// per section without restructuring the page once the final chart choices are made.
	const SECTION_CONFIG = {
		"progressive-core": {
			voting: (c) => [
				{ label: "Municipal: Chow", value: pct(c.elections.mayor_2023.chow) },
				{ label: "Provincial: NDP", value: pct(c.elections.provincial_2025.ndp) },
				{ label: "Federal: NDP", value: pct(c.elections.federal_2025.ndp) },
			],
			graphic: "strip",
			stripVars: [
				{ key: "pct_renter", label: "% renter" },
				{ key: "pct_commute_car", label: "% commute by car (lower here)" },
			],
		},
		"mobile-middle": {
			voting: (c) => [
				{ label: "Municipal: Chow", value: pct(c.elections.mayor_2023.chow) },
				{ label: "Provincial: NDP", value: pct(c.elections.provincial_2025.ndp) },
				{ label: "Federal: Liberal", value: pct(c.elections.federal_2025.liberal) },
			],
			graphic: "bars",
			// TODO: swap for a radar chart if that reads better than grouped bars once styled.
			compareVars: [
				{ key: "pct_migrant_5yr", label: "Migrated in last 5 years", format: pct },
				{ key: "pct_renter", label: "Renters", format: pct },
				{ key: "pct_bachelor_or_higher", label: "Bachelor's degree+", format: pct },
				{ key: "pct_commute_car", label: "Commute by car", format: pct },
			],
		},
		"civic-professionals": {
			voting: (c) => [
				{ label: "Municipal: Matlow", value: pct(c.elections.mayor_2023.matlow) },
				{ label: "Provincial: Liberal", value: pct(c.elections.provincial_2025.liberal) },
				{ label: "Municipal turnout", value: pct(c.elections.mayor_2023.turnout) },
			],
			graphic: "scatter",
			scatter: { xKey: "income_median", yKey: "pct_bachelor_or_higher", xLabel: "Median income ($)", yLabel: "Bachelor's degree+ (%)" },
		},
		"working-suburbanites": {
			voting: (c) => [
				{ label: "Municipal: Other candidates", value: pct(c.elections.mayor_2023.other) },
				{ label: "Provincial: PC", value: pct(c.elections.provincial_2025.pc) },
				{ label: "Municipal turnout", value: pct(c.elections.mayor_2023.turnout) },
			],
			graphic: "dumbbell",
			// TODO: try ClusterCompareBars instead — outline leaves the chart type open.
			compareVars: [
				{ key: "pct_visible_minority", label: "Visible minority", format: pct },
				{ key: "income_median", label: "Median income", format: dollars },
				{ key: "pct_bachelor_or_higher", label: "Bachelor's degree+", format: pct },
			],
		},
		"settled-conservatives": {
			voting: (c) => [
				{ label: "Municipal: Bailão", value: pct(c.elections.mayor_2023.bailao) },
				{ label: "Provincial: PC", value: pct(c.elections.provincial_2025.pc) },
				{ label: "Federal: Conservative", value: pct(c.elections.federal_2025.conservative) },
			],
			graphic: "strip",
			stripVars: [
				{ key: "pct_renter", label: "% renter (lower here = more homeowners)" },
				{ key: "avg_age", label: "Average age" },
				{ key: "pct_commute_car", label: "% commute by car" },
			],
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
				voting={config.voting(cluster)}
			/>

			<div class="text">
				<p>{LOREM_IPSUM}</p>
			</div>

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
				{:else if config.graphic === "dumbbell"}
					<DumbbellChart rows={compareRows(cluster, config.compareVars)} color={cluster.color} />
				{:else if config.graphic === "scatter"}
					<ScatterHighlight
						values={ctValues}
						xKey={config.scatter.xKey}
						yKey={config.scatter.yKey}
						xLabel={config.scatter.xLabel}
						yLabel={config.scatter.yLabel}
						clusterId={cluster.cluster_id}
						color={cluster.color}
					/>
				{/if}
			</div>
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

	@media (max-width: 600px) {
		.intro-map,
		.cluster-section {
			margin-bottom: 36px;
		}
		.graphic {
			margin-top: 18px;
		}
	}
</style>
