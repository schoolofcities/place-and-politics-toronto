<script>
	import logo from '../assets/top-logo.svg';
	import logoFull from '../assets/top-logo-full.svg';

	let width;

	let barWidth = 262;
	$: if (width < 500) {
		barWidth = 262
	} else {
		barWidth = 383
	}

</script>

<div id="bar" bind:clientWidth={width}>

	<div id="content" style="width: {barWidth}px">
	
		<div id="logo">
			{#if width < 500}
				<a href="https://www.schoolofcities.utoronto.ca/"><img src={logo} alt="School of Cities"></a>
			{:else}
				<a href="https://www.schoolofcities.utoronto.ca/"><img src={logoFull} alt="School of Cities"></a>
			{/if}
		</div>

		<div id="pp">
			<a href="./"><p>Place & Politics <br>in Toronto</p></a>
		</div>

	</div>

</div>

<style>
	#bar {
		position: fixed;
		overflow: hidden;
   		top: 0px;
		height: 50px;
		background-color: #fffefd;
		margin-bottom: 20px;
		border-bottom: 1px solid rgb(126, 126, 126);
		width: 100%;
		min-width: 200px;
		padding-left: 0px;
		padding-right: 0px;
		/* text-align: center; */
		z-index: 9999;
		opacity: 0.98;
		box-shadow: 0 2px 0 0 rgba(224, 224, 224, 0.268);
	}

	#content {
		margin: auto;
		/* max-width: 400px; */
		background-color: aquamarine;
	}

	#logo {
		float: left;
	}

	#pp {
		margin-top: -8px;
		float: right;
		font-family: "Source Serif Pro", serif;
		text-decoration: underline;
		color: black;
		font-size: 15px;
	}

	a {
		color: black;
	}
	a:hover {
		opacity: 0.5;
	}

	img {
		color: blue;
		height: 50px;
		width: auto;
	}
	img:hover {
		opacity: 0.5;
		cursor: pointer;
	}
</style>
