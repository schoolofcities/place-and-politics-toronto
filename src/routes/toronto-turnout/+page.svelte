<script>
	//
	//   Structure (article copy is still to be written -- each prose block is a one-line placeholder).
	//   Only sections 3 and 5 carry a visible subheading; the others are labelled for screen readers only.
	//     1. Introduction                           — intro, then the turnout map (4-way toggle)
	//     2. Map the turnout geography              — prose only
	//     3. What sits underneath the turnout map?  — Component 1 map, then its ingredient chart
	//     4. What might make participation easier?  — prose only
	//     5. Explore the ingredients                — variable vs. mean-turnout explorer
	//     6. Methods and limitations                — shell for the future methods write-up
	//
	// Graphics live in ./components; palettes, breaks and labels in ./config.js; data shaping in
	// ./data.js. All data comes from analysis/toronto_election_turnout/09_final_synthesis.ipynb.

	import Top from "$lib/layout/TopSofC.svelte";
	import PasswordGate from "$lib/layout/PasswordGate.svelte";

	import TurnoutMap from "./components/TurnoutMap.svelte";
	import ComponentMap from "./components/ComponentMap.svelte";
	import LoadingChart from "./components/LoadingChart.svelte";
	import VariableExplorer from "./components/VariableExplorer.svelte";
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />

	<!-- TODO: finalize title/description/social image once the story's copy is set. -->
	<title>One city, uneven participation | Place &amp; Politics in Toronto</title>
	<meta name="description" content="Examining differences in turnout across recent elections in Toronto" />
	<meta name="author" content="School of Cities" />
	<link rel="canonical" href="https://schoolofcities.github.io/place-and-politics-toronto/toronto-turnout" />
	<meta property="og:title" content="One city, uneven participation | Place &amp; Politics in Toronto" />
	<meta property="og:description" content="Examining differences in turnout across recent elections in Toronto" />
	<meta property="og:type" content="article" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/toronto-turnout" />
	<meta property="og:locale" content="en_CA" />
</svelte:head>

<!-- Page is still in development — comment out this one line to unlock it for launch. -->
<PasswordGate />

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto - Part 8</h4>
		<div id="mini-line"></div>
		<h1>One city, uneven participation</h1>
		<p class="subtitle">Examining differences in turnout across recent elections in Toronto</p>
		<h3><a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/">Aniket Kali</a> <br />October 2026</h3>
		<div id="mini-line"></div>
	</div>

	<!-- 1. Introduction + main turnout map -->
	<section class="story-section" aria-label="One city, uneven participation">
		<div class="text">
			<p>[Introduction text goes here.]</p>
		</div>
		<div class="graphic">
			<TurnoutMap />
		</div>
	</section>

	<!-- 2. Turnout geography -->
	<section class="story-section" aria-label="Map the turnout geography">
		<div class="text">
			<p>[Text on the geography of turnout goes here.]</p>
		</div>
	</section>

	<!-- 3. What sits underneath -->
	<section class="story-section" aria-labelledby="underneath-heading">
		<h2 id="underneath-heading">What sits underneath the turnout map?</h2>
		<div class="text">
			<p>[Text introducing the model and Component 1 goes here.]</p>
		</div>
		<div class="graphic">
			<ComponentMap />
		</div>
		<div class="text">
			<p>[Text on what Component 1 is made of goes here.]</p>
		</div>
		<div class="graphic graphic-narrow">
			<LoadingChart />
		</div>
		<div class="text">
			<p>[Text noting that other latent social geographies (Components 2 to 4) exist goes here.]</p>
			<p>[Text noting that the main component persists across the municipal, provincial and federal models goes here.]</p>
		</div>
	</section>

	<!-- 4. What might make participation easier? -->
	<section class="story-section" aria-label="What might make participation easier?">
		<div class="text">
			<p>[Discussion of time constraints, commutes, caregiving, polling access, shift work, transit and voting hours goes here.]</p>
		</div>
	</section>

	<!-- 5. Explorer -->
	<section class="story-section" aria-labelledby="explore-heading">
		<h2 id="explore-heading">Explore the ingredients</h2>
		<div class="text">
			<p>[Text introducing the explorer goes here.]</p>
		</div>
		<div class="graphic graphic-wide">
			<VariableExplorer />
		</div>
	</section>

	<!-- 6. Methods and limitations -->
	<section class="story-section methods-section" aria-label="Methods and limitations">
		<div class="text">
			<p>[Methods and limitations text goes here.]</p>
			<p class="methods-link">
				Full methods: [link to the detailed methods write-up goes here]. In the meantime, the reproducible analysis notebooks are on
				<a href="https://github.com/schoolofcities/place-and-politics-toronto/tree/main/analysis/toronto_election_turnout">GitHub</a>.
			</p>
		</div>
	</section>

	<div id="mini-line"></div>

	<div class="info">
		<p>[Acknowledgements go here.]</p>
	</div>
</main>

<style>
	.title .subtitle {
		font-weight: normal;
		font-size: 20px;
		line-height: 1.35;
		margin: 14px 0 18px;
	}

	.story-section {
		margin: 0 auto 28px;
		width: 100%;
	}
	.story-section h2 {
		font-family: "Source Serif Pro", serif;
		font-weight: normal;
		text-align: center;
		margin: 0 auto 16px;
		max-width: 694px;
		padding: 0 25px;
		box-sizing: border-box;
	}

	/* graphics sit wider than the text column, like the maps on the other stories */
	.graphic {
		margin: 20px auto;
		max-width: 850px;
		width: calc(100% - 20px);
	}
	.graphic-narrow {
		max-width: 680px;
	}
	.graphic-wide {
		max-width: 1000px;
	}

	.methods-link {
		font-size: 15px;
	}

	@media (max-width: 600px) {
		.story-section {
			margin-bottom: 24px;
		}
		.story-section h2 {
			font-size: 24px;
		}
		.graphic {
			margin: 16px auto;
		}
	}
</style>
