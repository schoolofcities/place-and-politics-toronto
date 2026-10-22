<script>
	// Title and subtitle above a graphic, so it still makes sense on its own (e.g. screenshotted).
	// Same look as the intro map's `.map-title` / `.map-subtitle` on the five-torontos page.
	export let title = '';
	export let subtitle = '';
</script>

<div class="figure-title">
	<p class="title-text">{title}</p>
	{#if subtitle}<p class="subtitle-text">{subtitle}</p>{/if}
</div>

<style>
	.figure-title {
		margin: 0 0 12px;
		text-align: center;
	}
	.title-text {
		font-family: 'Source Serif Pro', serif;
		font-size: 20px;
		font-weight: bold;
		line-height: 1.3;
		margin: 24px 0 0;
	}
	.subtitle-text {
		font-family: OpenSans, sans-serif;
		font-size: 14px;
		line-height: 1.4;
		color: var(--brandGray90);
		margin: 9px 0 0;
	}
</style>
