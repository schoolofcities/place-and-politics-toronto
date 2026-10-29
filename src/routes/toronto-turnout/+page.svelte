<script>
	// Graphics live in ./components; palettes, breaks and labels in ./config.js; data shaping in
	// ./data.js. All data comes from analysis/toronto_election_turnout/09_final_synthesis.ipynb.

	import Top from "$lib/layout/TopSofC.svelte";
	import StructuredData from "$lib/layout/StructuredData.svelte";

	import TurnoutMap from "./components/TurnoutMap.svelte";
	import ComponentMap from "./components/ComponentMap.svelte";
	import LoadingChart from "./components/LoadingChart.svelte";
	import VariableExplorer from "./components/VariableExplorer.svelte";

	// page metadata (the canonical link and JSON-LD come from <StructuredData>)
	const TITLE = "One city, uneven participation | Place & Politics in Toronto";
	const DESCRIPTION =
		"Mapping turnout across Toronto's 585 census tracts in the 2023 mayoral by-election and the 2025 provincial and federal elections, and the combination of neighbourhood characteristics most closely tied to it.";
	const CARD = "https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/assets/web-card-8.png";

	const METHODS = "https://github.com/schoolofcities/place-and-politics-toronto/blob/main/analysis/toronto_election_turnout";
</script>

<svelte:head>
	<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1" />

	<title>{TITLE}</title>
	<meta name="description" content={DESCRIPTION} />
	<meta name="author" content="Aniket Kali, Kaiwen Yang" />

	<meta property="og:title" content={TITLE} />
	<meta property="og:site_name" content="Place & Politics in Toronto" />
	<meta property="og:description" content={DESCRIPTION} />
	<meta property="og:type" content="article" />
	<meta property="article:published_time" content="2026-10-26" />
	<meta property="article:author" content="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" />
	<meta property="article:author" content="https://kaiwenyangut.github.io" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/toronto-turnout" />
	<meta property="og:image" content={CARD} />
	<meta property="og:locale" content="en_CA" />

	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="https://www.schoolofcities.utoronto.ca/" />
	<meta name="twitter:title" content={TITLE} />
	<meta name="twitter:description" content={DESCRIPTION} />
	<meta name="twitter:image" content={CARD} />
</svelte:head>

<StructuredData slug="toronto-turnout" description={DESCRIPTION} />

<Top />

<main>
	<div class="title">
		<h4>Place & Politics in Toronto - Part 8</h4>
		<div id="mini-line"></div>
		<h1>One city, uneven participation</h1>
		<h3><a href="https://www.linkedin.com/in/aniket-kali-8a8b9921b/" target="_blank" rel="noopener noreferrer">Aniket Kali</a> & <a href="https://kaiwenyangut.github.io" target="_blank" rel="noopener noreferrer">Kaiwen Yang</a> <br><br> <span class="date">October 26, 2026</span></h3>
		<div id="mini-line"></div>
	</div>

	<!-- Introduction + main turnout map -->
	<section class="story-section" aria-label="One city, uneven participation">
		<div class="text">
			<p>
				Political participation is not evenly distributed across the City of Toronto. Voters in some
				neighbourhoods come out in greater numbers, while turnout is lower in others.
			</p>
			<p>
				We mapped voter turnout in Toronto's 2023 mayoral by-election, 2025 provincial election, and
				2025 federal election. Turnout differs from election to election, but broad geographic
				patterns recur across all three.
			</p>
		</div>
		<div class="graphic">
			<TurnoutMap />
		</div>
	</section>

	<!-- What sits underneath the turnout map -->
	<section class="story-section titled" aria-labelledby="underneath-heading">
		<h2 id="underneath-heading">What sits underneath the turnout map?</h2>
		<div class="text">
			<p>
				Neighbourhood-level data cannot tell us why particular people chose to vote or not to vote.
				But we know neighbourhood characteristics also do not vary independently: education overlaps
				with occupation, housing with income, immigration with age and language, and so on – and
				many of these characteristics are
				<a href="https://schoolofcities.github.io/place-and-politics-toronto/social-geography-and-the-mayoral-vote" target="_blank" rel="noopener noreferrer">correlated to voting patterns</a>.
			</p>
			<p>
				To examine these relationships together, we used
				<a href="https://en.wikipedia.org/wiki/Partial_least_squares_regression" target="_blank" rel="noopener noreferrer">Partial Least Squares</a>
				(PLS) regression with 70 measures of neighbourhood population, housing, employment,
				transportation, and accessibility. In simple terms, PLS finds a small number of components
				that capture characteristics that tend to occur together and are also related to voter
				turnout. Each neighbourhood census tract receives a score on each component, showing where it
				lies relative to other tracts.
			</p>
			<p>
				The first component is much more closely associated with turnout than the others. Its
				higher-scoring side includes neighbourhoods with more university education, professional
				employment, working from home, higher employment rates, and tends to be more centrally
				located. Its lower-scoring side combines more trades, service and manufacturing work, long
				commutes, unemployment, larger and multigenerational households, lone-parent families, and
				larger immigrant and first-generation populations.
			</p>
		</div>
		<div class="graphic">
			<ComponentMap />
		</div>
		<div class="text">
			<p>
				The important finding is the <em>combination</em>, not any one characteristic. The data and
				the model cannot tell us, for example, that immigrants living in a lower-turnout tract are
				the residents who did not vote. Nor can immigrant share, occupation, household structure or
				any other individual measure be isolated from the component and treated as a cause of lower
				turnout.
			</p>
			<p>
				That distinction matters here. Our turnout denominator includes only Canadian citizens aged
				18 and older, so neighbourhoods are not assigned lower turnout simply because they contain
				more residents who are ineligible to vote. Immigrant and first-generation shares instead
				describe the wider neighbourhoods in which eligible voters live, alongside differences in
				employment, education, household structure, commuting and geography.
			</p>
			<p>
				The broader turnout literature also shows why these characteristics should be interpreted
				together.
				<a href="https://www.sciencedirect.com/science/article/pii/S0261379405000910" target="_blank" rel="noopener noreferrer">A major meta-analysis by Benny Geys</a>
				reviewed 83 aggregate-level studies of turnout, while a
				<a href="https://www.sciencedirect.com/science/article/pii/S0261379416300956" target="_blank" rel="noopener noreferrer">later update by João Cancela and Geys</a>
				expanded that evidence base to 185 studies and broadly confirmed the earlier findings. Both
				emphasize that turnout reflects a mix of socioeconomic, political and institutional
				conditions rather than a single demographic explanation.
			</p>
			<p>
				Existing Canadian research gives us additional reason to resist treating immigration or
				racialization as simple explanations for voter turnout. A
				<a href="https://onlinelibrary.wiley.com/doi/full/10.1111/imig.13150" target="_blank" rel="noopener noreferrer">2023 study by Stephen White</a>,
				using Canadian election studies spanning 45 years, found that an apparent relationship
				between immigrants' length of residence and turnout largely disappeared once the historical
				period in which different cohorts arrived was taken into account. Even seemingly
				straightforward demographic relationships can therefore reflect political socialization and
				historical context rather than fixed characteristics of a group.
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
				The component is therefore better understood as a wider social geography involving class,
				employment, settlement, household responsibilities, commuting, and location. Across the 582
				tracts with reliable data, its score correlates 0.72 with mean turnout, substantially more
				strongly than the other components identified by the model.
			</p>
			<p>
				This component is not peculiar to one election. When we repeat the analysis separately for
				municipal, provincial and federal turnout, essentially the same underlying components
				reappear. Neighbourhood characteristics predict municipal turnout more strongly, but the
				broad pattern remains very similar across all three levels.
			</p>
		</div>
		<div class="graphic graphic-narrow">
			<LoadingChart />
		</div>
		<div class="text">
			<p>
				The model also identifies other recognizable components of Toronto's geography: relatively
				settled family neighbourhoods versus younger and more mobile renter areas; housing need and
				apartment living versus higher-income family ownership; and a weaker housing and employment
				contrast. These components are all much less closely related to turnout than the first.
			</p>
		</div>
	</section>

	<!-- Making participation easier -->
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
				reasons related to the electoral process, and 23% cited everyday-life or health reasons.
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
				schedules, and caregiving are useful areas for further study. Our model does not directly
				measure most of these mechanisms, so they are better treated as plausible ways to make
				participation easier, not as effects demonstrated by this analysis.
			</p>
		</div>
	</section>

	<!-- Explorer -->
	<section class="story-section titled" aria-labelledby="explore-heading">
		<h2 id="explore-heading">Explore the ingredients</h2>
		<div class="text">
			<p>
				The component analysis summarizes how variables work together, but it is also useful to see
				how each relates to turnout on its own. The explorer below lets you select measures included
				in the model, including education, employment, age, housing, transportation, and access to
				services, and compare each with turnout.
			</p>
			<p>
				Remember, however, that these are relationships between characteristics of neighbourhoods,
				not individual people. A census tract is not a voter, a correlation does not establish
				behaviour or causation, and turnout is not the sum of political participation.
			</p>
		</div>
		<div class="graphic graphic-wide">
			<VariableExplorer />
		</div>
	</section>

	<!-- Data and methods, in the small .info style used on the other posts -->
	<div class="info" id="data-and-methods">
		<p class="info-title"><strong>Data and methods</strong></p>
		<p>
			This analysis combines results from Toronto's 2023 mayoral election, the 2025 Ontario
			provincial election, and the 2025 federal election with 2021 Census data, the 2022/23
			Transportation Tomorrow Survey, and Statistics Canada's
			<a href="https://www150.statcan.gc.ca/n1/pub/71-607-x/71-607-x2020011-eng.htm" target="_blank" rel="noopener noreferrer">2021 Proximity Measures Database</a>.
		</p>
		<p>
			Because each election uses different polling boundaries, we use population-weighted spatial
			interpolation to estimate results for Toronto's 585 census tracts (2021 boundaries). Turnout is
			measured as votes cast relative to the estimated number of Canadian citizens aged 18 and older
			in the tract, providing a consistent population-based measure across all three elections. Our
			main outcome variable in the model is average turnout across the three elections.
		</p>
		<p>
			We then use 70 neighbourhood measures covering demographics, household structure, education,
			income and employment, occupation, housing, immigration and citizenship, language,
			transportation, urban form and access to services. Because many overlap, we use Partial Least
			Squares regression (PLS) to identify combinations of characteristics that move together and
			are also related to turnout. Cross-validation selects four components, with most of the
			turnout relationship concentrated in the first.
		</p>
		<p>
			We test that result in several ways. The main component remains very similar when each
			election is modelled separately, when the predictor set is reduced, and when transportation
			and broader spatial-context variables are removed. We also compare PLS with Principal
			Component Regression, supervised PCA and Elastic Net, and use spatial cross-validation and
			bootstrap resampling to test whether the result is sensitive to geography or the observed
			sample.
		</p>
		<p>
			The main pattern remains stable across these checks, but the analysis is descriptive and
			predictive rather than causal. Election results are spatially estimated, the denominator comes
			from the 2021 Census, and neighbourhood-level relationships cannot identify individual
			behaviour. The components are continuous summaries of overlapping neighbourhood
			characteristics, not fixed types of people or places.
		</p>
		<p>
			A more detailed
			<a href="{METHODS}/DATA_AND_METHODS.md" target="_blank" rel="noopener noreferrer">technical write-up</a>
			describes the interpolation, variables, model selection, robustness checks and limitations in
			full, and the analysis notebooks document each step:
			<a href="{METHODS}/04_interpolate_votes_to_tracts.ipynb" target="_blank" rel="noopener noreferrer">vote interpolation</a>,
			<a href="{METHODS}/06_explore_and_curate_predictors.ipynb" target="_blank" rel="noopener noreferrer">predictor selection</a>,
			<a href="{METHODS}/07_fit_latent_pls_model.ipynb" target="_blank" rel="noopener noreferrer">PLS model</a>,
			<a href="{METHODS}/08_robustness_and_alternative_models.ipynb" target="_blank" rel="noopener noreferrer">robustness checks</a>,
			and
			<a href="{METHODS}/09_final_synthesis.ipynb" target="_blank" rel="noopener noreferrer">final synthesis</a>.
		</p>
	</div>

	<div id="mini-line"></div>

	<div class="info">
		<p>
			Thanks to Zack Taylor for reviewing the methods, research, and text behind this piece. Jeff
			Allen reviewed the text and helped design the graphics.
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
