<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import Bar from "../lib/Bar2023.svelte";	
	import Turnout from "../lib/Turnout.svelte";
	import Map from "../lib/Map2023.svelte";	
    import WebCard from "../assets/web-card-1.png";
	import '../styles.css';

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
	<meta
		name="viewport"
		content="width=device-width, initial-scale=1, minimum-scale=1"
	/>
	<link href='https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.css' rel='stylesheet' />

    <title>Place and Politics in Toronto</title>
    <meta name="description" content="Place and Politics in Toronto">
    <meta name="author" content="Zack Taylor & Jeff Allen">

    <meta property="og:title" content="Place and Politics in Toronto" />
    <meta name="og:description" content="Mapping the 2023 Toronto Mayoral By-Election" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/the-geography-of-the-vote-poll-by-poll" />
    <meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/routes/assets/web-card-5.png" />
    <meta property="og:locale" content="en_CA">

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="https://schoolofcities.github.io/place-and-politics-toronto/the-geography-of-the-vote-poll-by-poll" />
    <meta name="twitter:creator" content="@JeffAllenMaps" />
    <meta name="twitter:title" content="Place and Politics in Toronto" />
    <meta name="twitter:description" content="Mapping the 2023 Toronto Mayoral By-Election" />
    <meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/routes/assets/web-card-5.png" />

</svelte:head>



<Top/>

<main>

	<UnderConstruction/>
	
	<div class="title">

		<h4>Place & Politics in Toronto - Part 5</h4>

		<div id="mini-line"></div>

		<h1>Mapping the 2023 Mayoral By-Election</h1>
		<h3><a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> <br><br> July 11, 2023</h3>

		<div id="mini-line"></div>

	</div>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
		<p>
			The winner, <span style="background-color: #c27dcf">Olivia Chow</span> had <span style="background-color: #c27dcf">269,372 votes</span> and <span style="background-color: #c27dcf">37.17% </span> of votes cast.
			The runner up, <span style="background-color: #c5de75">Ana Bailão</span>, ended election night with <span style="background-color: #c5de75">32.46% </span> and <span style="background-color: #c5de75">235,175 votes</span>.
			Third-place candidate <span style="background-color: #bec2d4">Mark Saunders</span> finished with <span style="background-color: #bec2d4">8.58%</span> and <span style="background-color: #bec2d4">62,167 votes</span>.
		</p>

		<div class="bar">
			<Bar/>
		</div>
	</div>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
		<div class="turnout">
			<Turnout/>
		</div>
	</div>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "chow"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "bailao"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "saunders"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "furey"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "matlow"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "hunter"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "brown"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>

	<Map candidate = "bradford"/>

	<div class="text">
		<p>
			Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
		</p>
	</div>



	<div id="mini-line"></div>

	<div class="info">
		<h3>Data Sources:</h3>
		<p>
			Official <a href="https://open.toronto.ca/dataset/elections-official-by-election-results/">election results</a> and the <a href="https://www.toronto.ca/city-government/elections/city-elections/voting-places/">voting subdivsions</a> (poll catchment areas) were downloaded from the City of Toronto. The code and data used to build this page and its graphics are on <a href="https://github.com/schoolofcities/place-and-politics-toronto">GitHub</a>.
			<br><br>
		</p>
	</div>

</main>
