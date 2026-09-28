<script>
	import logo from '$assets/top-logo.svg';
	import logoFull from '$assets/top-logo-full.svg';

	let width;

	let barWidth = 246;
	$: if (width < 500) {
		barWidth = 246
	} else {
		barWidth = 361
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
	/* scrolls away with the page rather than staying fixed at the top */
	#bar {
		position: relative;
		overflow: hidden;
		height: 50px;
		background-color: #fffefd;
		margin-bottom: 0px;
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
		line-height: 18.5px;
	}

	a {
		color: black;
	}
	a:hover {
		opacity: 0.5;
	}

	img {
		color: blue;
		height: 45px;
		width: auto;
		margin-top: 2px;
	}
	img:hover {
		opacity: 0.5;
		cursor: pointer;
	}
</style>
