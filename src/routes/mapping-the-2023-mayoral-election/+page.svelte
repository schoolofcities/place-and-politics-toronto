<script>

	import Top from "../lib/TopSofC.svelte";
	import UnderConstruction from "../lib/UnderConstruction.svelte";
	import Bar from "../lib/Bar2023.svelte";
	import BarVote from "../lib/BarVote2023.svelte";	
	import Turnout from "../lib/Turnout.svelte";
	import Map from "../lib/Map2023.svelte";	
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
			The June 26, 2023, election followed a short but eventful campaign. Turnout was considerably higher than in last fall’s general election. A total of 722,877 ballots were cast, 30.1% more than the 551,890 cast in 2022. This was the fourth-highest number of votes cast in the nine mayoral elections held since amalgamation in 1997, and only 32,616 less than were cast in the 2018 election.

		</p>
		<div class="turnout">
			<Turnout/>
		</div>
	</div>

	<div class="text">
		<p>
			Although Olivia Chow polled in first place throughout the campaign period, a large number of top-tier candidates jockeyed to break through the noise to become the clear alternative, or even to jump into first place. Not since 2003 have so many “serious” candidates run for mayor in an open race. Running against the well-known New Democrat Olivia Chow were two sitting members of council, Brad Bradford (Beaches-East York) and Josh Matlow (Toronto-St. Paul’s). (We’ll set aside Councillor Anthony Peruzza, who won only a few hundred votes in the end.) This being a by-election, councillors could keep their ward seats while running for mayor. Former councillor Ana Bailão ultimately received an endorsement from disgraced ex-mayor John Tory. Fresh from defeat as the Progressive Conservative candidate in Don Valley West in the 2022 provincial election, former police chief Mark Saunders was Premier Doug Ford’s preferred candidate. Rounding out the list were Mitzie Hunter, MPP for Scarborough-Guildwood and former provincial Liberal cabinet minister; Toronto Sun columnist Anthony Furey; and Chloe Brown, who came in a surprise (if distant) third place in last fall’s mayoral general election. 
		</p>
		<p>
			That so many major candidates remained the race to the end is testament to the degree to which they possessed distinct support bases and fundraising networks – which, we show below, is reflected in the different geographies of electoral support. In the end, fully 69.6% of votes cast went to the top two finishers – Chow (37.2%) and Bailão (32.5%) while the rest competed for scraps.
		</p>
		<!-- <p>
			The winner, <span style="background-color: #c27dcf">Olivia Chow</span> had <span style="background-color: #c27dcf">269,372 votes</span> and <span style="background-color: #c27dcf">37.17% </span> of votes cast.
			The runner up, <span style="background-color: #c5de75">Ana Bailão</span>, ended election night with <span style="background-color: #c5de75">32.46% </span> and <span style="background-color: #c5de75">235,175 votes</span>.
			Third-place candidate <span style="background-color: #bec2d4">Mark Saunders</span> finished with <span style="background-color: #bec2d4">8.58%</span> and <span style="background-color: #bec2d4">62,167 votes</span>.
		</p> -->

		<div class="bar-vote-total">
			<BarVote/>
		</div>

	</div>

	<div class="text">
		<h2>Unpacking the Bailão surge</h2>
		<p>
			Unlike in previous mayoral elections, considerable movement occurred between the June 8–13 advance voting period and the June 26 election day. Chow performed far better in advance (46.6%) and mail-in (50.8%) voting than she did on election day (34.3%). Bailão, by contrast, surged on election day, likely due to Tory’s endorsement on July 21. Although Bailão beat Chow in terms of ballots cast on election day, Chow’s advance and mail-in votes put her over the top when all votes were counted.
		</p>
	</div>


	<div class="text">
		<h2>Chow versus Bailão, mapped</h2>
		<p>
			Mapping election day votes by poll, we find that Olivia Chow did best in the core: neighbourhoods within the seven wards that roughly correspond to the pre-amalgamation City of Toronto and Boroughs of York and East York south of St. Clair Avenue. This is not simply an of City of Toronto-versus-the-rest story. She also received diffuse support in the postwar suburbs of Scarborough, North Etobicoke, and east flank of North York, with concentrations of support in rental apartment clusters, most visibility in Thorncliffe Park. In sum, she received X% of her election day votes in polls corresponding to the former City of Toronto, and Y% from polls located in the former suburban municipalities. The neighbourhoods where she did the least well are among the wealthiest in the city; the neighbourhoods where she did best are not only downtown hipster enclaves, but also those containing high numbers of immigrants. 

		</p>
	</div>

	<Map candidate = "chow"/>

	<div class="text">
		<p>
			Bailao’s map is more or less the inverse of Chow’s. She did best in the well-off neighbourhoods of central Etobicoke, Scarborough south of Kingston Road, Rosedale, North Toronto, the Bridle Path, Don Mills, and Willowdale. She may also have benefitted from support from southern European immigrant voters – predominantly Portuguese and Italians – in her former ward of Davenport and to the northwest in York and Weston. 
		</p>
	</div>

	<Map candidate = "bailao"/>

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