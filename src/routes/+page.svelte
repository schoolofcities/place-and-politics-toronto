<script>

    import './styles.css';
	import logo from './assets/top-logo.svg';
	import p1 from './assets/p1.png';
	import p2 from './assets/p2.png';
	import p3 from './assets/p3.png';
	import p4 from './assets/p4.png';

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

    <title>Place and Politics in Toronto</title>
    <meta name="description" content="Place and Politics in Toronto">
    <meta name="author" content="Zack Taylor & Jeff Allen">

    <meta property="og:title" content="Place and Politics in Toronto" />
    <meta name="og:description" content="Mapping the 2022 Toronto Election" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/" />
    <meta property="og:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/sveltekit/src/routes/assets/web-card-1.png" />
    <meta property="og:locale" content="en_CA">

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="https://schoolofcities.github.io/place-and-politics-toronto/" />
    <meta name="twitter:creator" content="@JeffAllenMaps" />
    <meta name="twitter:title" content="Place and Politics in Toronto" />
    <meta name="twitter:description" content="Mapping the 2022 Toronto Election" />
    <meta name="twitter:image" content="https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/sveltekit/src/routes/assets/web-card-1.png" />

</svelte:head>



<main>

	<!-- <UnderConstruction/> -->

	<div id="homebar">

		<div id="content">
		
			<div id="logo">
				<a href="https://www.schoolofcities.utoronto.ca/"><img src={logo} alt="School of Cities"></a>
			</div>

		</div>
	
	</div>
	
	
	<div class="title">

		<div id="mini-line"></div>

		<h1>Place & Politics in Toronto</h1>

		<h3>A blog series mapping City of Toronto
			election results 
			<!-- by <a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a> -->
			<br><br>
			<a href="https://zacktaylor.com/">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a>
		</h3><br>


		<div id="mini-line"></div>


	</div>


	<div class="text">

		<a href="./place-and-politics-toronto/the-geography-of-the-vote-poll-by-poll">
			<div class="item">
				<div class="number" style="background-image: url({p1});">
				</div>
				<div id="part">
					<p>
					
						<span class="date">Part 1 - November 2, 2022</span><br>
					
						<u>The geography of the vote, poll by poll</u>
					
					
					</p>
				</div>
			</div>
		</a>

		<a href="./place-and-politics-toronto/torontos-two-rights">
			<div class="item">
				<div class="number" style="background-image: url({p2});">
				</div>
				<div id="part">
					<p>
						<span class="date">Part 2 - November 25, 2022</span><br>
						<u>Toronto's Two Rights</u>
					</p>
				</div>
			</div>
		</a>

		<a href="./place-and-politics-toronto/the-electoral-geography-of-progressivism">
			<div class="item">
				<div class="number" style="background-image: url({p3});">
				</div>
				<div id="part">
					<p>
						<span class="date">Part 3 - November 30, 2022</span><br>
						<u>The Electoral Geography of Progressivism in Toronto</u>
					</p>
				</div>
			</div>
		</a>

	</div>
	
	<br><br>
	<div id="mini-line"></div>

	

</main>



<style>

	main {
		width: 100%;
		max-width: 100%;
	}

	#homebar {
		padding: 0px;
		margin: 0px;
		width: 100%;
		height: 50px;
		border-bottom: solid 1px;
		text-align: center;
		border-bottom: 1px solid rgb(126, 126, 126);
		box-shadow: 0 2px 0 0 rgba(224, 224, 224, 0.268);
	}

	#logo:hover {
		opacity: 0.5;
	}

	.title {
		margin-bottom: 50px;
		margin-top: 50px;
		max-width: 500px;
	}
	.title h3 {
		font-size: 17px;
	}

	.text {
		max-width: 485px;
	}

	.item {
		padding: 0px;
		margin: 0px;
		overflow: hidden;
		border-right: solid 8px rgb(232, 232, 232);
		margin-bottom: 20px;
		opacity: 0.95;
	}
	.item p {
		padding: 0px;
		margin: 0px;
	}
	.item:hover {
		border-right: solid 8px black;
		background-color: #fcfcfc;
		opacity: 1;
	}
	
	.number {
		width: 55px;
		height: 55px;
		margin-right: 10px;
		border: solid 1px #4b4b4b;
		border-radius: 28px;
		float: left;
	}

	@media (max-width:527px) {
		.number {
			display: none;
		}
	}

	#part {
		padding-left: 0px;
		padding-right: 0px;
		/* border: solid 1px #4a5fff; */
		color: black;
		float: left; 
	}

	.date {
		color:rgb(126, 126, 126)
	}

	
</style>
