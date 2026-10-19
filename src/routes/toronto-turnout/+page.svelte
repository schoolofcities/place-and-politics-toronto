<script>
	//
	//   Structure (copy from "2026.09 Turnout in Toronto's Elections DRAFT"):
	//     1. Introduction                           — intro, then the turnout map (4-way toggle)
	//     2. What sits underneath the turnout map?  — Component 1 map, then its ingredient chart
	//     3. Making electoral participation easier  — prose only
	//     4. Explore the ingredients                — one characteristic vs. turnout: linked map + scatterplot
	//     5. Data and methods                       — small .info block, as on the other posts
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
		<h3><a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" target="_blank" rel="noopener noreferrer">Aniket Kali</a>, Kevin Yang <br><br> October 2026</h3>
		<div id="mini-line"></div>
	</div>

	<!-- 1. Introduction + main turnout map -->
	<section class="story-section" aria-label="One city, uneven participation">
		<div class="text">
			<p>
				Political participation is not evenly distributed across the City of Toronto. Voters in some
				neighbourhoods come out in greater numbers, while others tend to stay at home.
			</p>
			<p>
				Looking at the most recent mayoral election in 2023, provincial election in 2025, and federal
				election in 2025, we mapped all three to Toronto's 585 census tracts and calculated turnout
				against the estimated number of Canadian citizens aged 18 and older. Turnout differs from
				election to election, but broad patterns recur across the city's geography.
			</p>
		</div>
		<div class="graphic">
			<TurnoutMap />
		</div>
	</section>

	<!-- 2. What sits underneath -->
	<section class="story-section titled" aria-labelledby="underneath-heading">
		<h2 id="underneath-heading">What sits underneath the turnout map?</h2>
		<div class="text">
			<p>
				We cannot say exactly why particular people decided to vote or not to vote, especially from
				neighbourhood-level data. But we do know that neighbourhood characteristics do not vary
				independently: education overlaps with profession, housing with income, immigration with age
				and language, and so on.
			</p>
			<p>
				To examine these relationships together, we used Partial Least Squares (PLS) regression with
				70 measures of neighbourhood population, housing, employment, transportation and
				accessibility. In simple terms, PLS looks for combinations of characteristics that tend to
				occur together and are also related to turnout. Each census tract receives a score showing
				where it falls along these broader dimensions.
			</p>
			<p>
				One of these combinations, called the first component, is much more closely associated with
				turnout than the others. Its higher-scoring side, which is associated with higher turnout,
				includes neighbourhoods with more university education, professional employment, working from
				home and stronger employment, and which tend to be more centrally located. Its lower-scoring
				side combines more trades, service and manufacturing work, long commutes, unemployment, larger
				and multigenerational households, lone-parent families, and areas with larger immigrant and
				first-generation populations.
			</p>
		</div>
		<div class="graphic">
			<ComponentMap />
		</div>
		<div class="text">
			<p>
				The important finding is the <em>combination</em>, not any one of those characteristics. The
				model cannot tell us, for example, that immigrants living in a lower-turnout tract are the
				residents who did not vote. Nor can immigrant share, occupation, household structure or any
				other individual measure be pulled out of the component and treated as a cause of lower
				turnout.
			</p>
			<p>
				That distinction is especially important here. Our turnout denominator includes only Canadian
				citizens aged 18 and older, so neighbourhoods are not assigned lower turnout simply because
				they contain more residents who are ineligible to vote. Rather, immigrant and first-generation
				population shares are characteristics of the wider neighbourhoods in which eligible voters
				live, alongside differences in employment, education, household structure, commuting and
				geography.
			</p>
			<p>
				Existing Canadian research also gives us reason to resist treating immigration or
				racialization as simple explanations for electoral participation.
				<a href="https://onlinelibrary.wiley.com/doi/full/10.1111/imig.13150" target="_blank" rel="noopener noreferrer">A 2023 study by Stephen White</a>
				using Canadian election studies spanning 45 years found that an apparent relationship between
				immigrants' length of residence and turnout largely disappeared once the historical period in
				which different cohorts arrived was taken into account. In other words, even seemingly
				straightforward demographic relationships can reflect political socialization and historical
				context rather than fixed characteristics of a group.
			</p>
			<p>
				Likewise,
				<a href="https://www.cogitatiopress.com/politicsandgovernance/article/view/9377" target="_blank" rel="noopener noreferrer">recent Canadian research on racialized voters</a>
				finds differences in turnout between several racialized groups and white Canadians, but also
				finds that socioeconomic circumstances and political engagement explain part of those gaps,
				while a substantial portion remains unexplained. Other work by Statistics Canada
				<a href="https://www150.statcan.gc.ca/n1/daily-quotidien/220517/dq220517c-eng.htm" target="_blank" rel="noopener noreferrer">cautions us to note</a>
				that many racialized Canadians still participate in politics beyond the ballot box: by
				engaging with news, going to meetings or demonstrations, signing a petition, or wearing signs
				in support of a cause.
			</p>
			<p>
				In other words, turnout is only one way of looking at political participation by
				neighbourhood. The component is therefore better understood as a wider social geography
				involving class, employment, settlement, household responsibilities, commuting and location.
				Across the 582 tracts with reliable data, its score correlates 0.72 with mean turnout, substantially
				more strongly than the other components identified by the model.
			</p>
		</div>
		<div class="graphic graphic-narrow">
			<LoadingChart />
		</div>
		<div class="text">
			<p>
				The model also identifies other recognizable aspects of Toronto's geography: relatively
				settled family neighbourhoods versus younger and more mobile renter areas; housing need and
				apartment living versus higher-income family ownership; and a weaker housing and employment
				contrast. These components are all much less closely related to turnout than the first.
			</p>
			<p>
				Nor is the first component peculiar to one election. When we repeat the analysis separately
				for municipal, provincial and federal turnout, essentially the same underlying dimension
				reappears. Neighbourhood characteristics predict municipal turnout more strongly, but the
				broad pattern is very similar across all three levels.
			</p>
		</div>
	</section>

	<!-- 3. Making participation easier -->
	<section class="story-section titled" aria-labelledby="easier-heading">
		<h2 id="easier-heading">Making electoral participation easier</h2>
		<div class="text">
			<p>
				None of this tells us that a particular policy would increase turnout. It does suggest a
				different way of framing the problem: lower participation may reflect barriers that
				institutions can reduce, rather than a lack of interest within particular neighbourhoods.
			</p>
			<p>
				Time and convenience are part of that picture. In an
				<a href="https://www.elections.ca/content.aspx?dir=rec%2Feval%2Fpes2025%2Frve&amp;document=p1&amp;lang=e&amp;section=res" target="_blank" rel="noopener noreferrer">Elections Canada survey following the 2025 federal election</a>,
				34% of voters said they chose their voting method because the date and time worked with their
				schedule, while 28% cited having a nearby voting location. Among non-voters, 24% cited
				electoral-process reasons and 23% everyday-life or health reasons.
			</p>
			<p>
				Access matters too.
				<a href="https://www.cambridge.org/core/journals/canadian-journal-of-political-science-revue-canadienne-de-science-politique/article/i-came-i-saw-i-voted-distance-to-polling-locations-and-voter-turnout-in-ontario-canada/84EB73738B9DE67B869A013432566C02" target="_blank" rel="noopener noreferrer">Observational research using Ontario polling locations</a>
				found that greater distance or travel time to the polls was generally associated with lower
				turnout. And in the 2025 federal election,
				<a href="https://elections.ca/content.aspx?dir=rec%2Feval%2Fpes2025%2Fevt&amp;document=p7&amp;lang=e&amp;section=res" target="_blank" rel="noopener noreferrer">44.2% of ballots were cast through advance or other alternative voting methods</a>,
				showing how widely voters already use more flexible options.
			</p>
			<p>
				Taken together, polling-place location, advance voting, voting hours, transportation, work
				schedules and caregiving are useful areas for further study. Our model does not directly
				measure most of these mechanisms, so they are better treated as plausible ways to make
				participation easier, not as effects demonstrated by this analysis.
			</p>
		</div>
	</section>

	<!-- 4. Explorer -->
	<section class="story-section titled" aria-labelledby="explore-heading">
		<h2 id="explore-heading">Explore the ingredients</h2>
		<div class="text">
			<p>
				Our component analysis provides a useful summary of how different variables work together, but
				it can also be useful to see how each relates to turnout on its own. The explorer below lets
				you select from measures included in the model, including education, employment, age,
				housing, transportation and access to services, and compare each with turnout.
			</p>
			<p>
				Remember, however, that these are relationships between characteristics of neighbourhoods, not
				individual people. A census tract is not a voter, a correlation does not establish behaviour
				or causation, and turnout is not the sum of political participation.
			</p>
		</div>
		<div class="graphic graphic-wide">
			<VariableExplorer />
		</div>
	</section>

	<!-- 5. Data and methods, in the small .info style used on the other posts -->
	<div class="info" id="data-and-methods">
		<p class="info-title"><strong>Data and methods</strong></p>
		<p>This analysis combines electoral results from Toronto's 2023 mayoral election, the 2025
			Ontario provincial election, and the 2025 federal election with Census, Transportation
			Tomorrow Survey, and neighbourhood-accessibility data.</p>
		<p>Election results are originally reported using different polling geographies at each level of
			government. To compare them consistently, we use population-weighted spatial interpolation to
			estimate results for Toronto's 585 census tracts. Turnout is calculated as votes cast relative
			to the estimated number of Canadian citizens aged 18 and older in each census tract, which
			allows for a standardized comparison across all tracts and elections.</p>
		<p>We then assemble 70 neighbourhood measures covering age and household structure, education,
			income and employment, occupation, housing, immigration and citizenship, language,
			transportation, urban form and access to services. Many of these characteristics overlap
			substantially. We therefore use Partial Least Squares regression, which summarizes them into a
			smaller number of components chosen specifically for their relationship with turnout.
			Cross-validation selects a four-component model, although most of the turnout relationship is
			concentrated in the first component described above.</p>
		<p>We tested whether that result depends heavily on particular modelling choices. The main
			component remains very similar when municipal, provincial and federal turnout are modelled
			separately, when the predictor set is substantially reduced, and when transportation variables
			are removed. We also compare PLS with Principal Component Regression, supervised PCA and
			Elastic Net, and use spatial cross-validation and repeated bootstrap samples to test how well
			the findings hold when geography or the observed sample changes.</p>
		<p>These tests support the stability of the main pattern, but they do not turn it into a causal
			explanation. Election results are spatially estimated, the population denominator comes from
			the 2021 Census while the elections occurred between 2023 and 2025, and neighbourhood-level
			relationships cannot identify the behaviour of individual residents. The components themselves
			are continuous statistical summaries of overlapping characteristics, not fixed types of
			neighbourhood or people.</p>
		<p>A more detailed
			<a href="https://github.com/schoolofcities/place-and-politics-toronto/tree/main/analysis/toronto_election_turnout" target="_blank" rel="noopener noreferrer">technical write-up</a>
			describes the interpolation, variables, model selection, validation and sensitivity tests in
			full.</p>
	</div>

	<div id="mini-line"></div>

	<div class="info">
		<p>[Acknowledgements go here.]</p>
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
	/* centred serif 20px, as the section headings on five-torontos */
	.story-section h2 {
		font-family: "Source Serif Pro", serif;
		font-size: 20px;
		font-weight: bold;
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
