<script>
	// Title and subtitle above a graphic, so it still makes sense on its own (e.g. screenshotted).
	// Same look as FigureTitle on the 2026 local-landslides page.
	let { title = '', subtitle = '' } = $props();
</script>

<div class="figure-title">
	<p class="title-text">{title}</p>
	{#if subtitle}<p class="subtitle-text">{subtitle}</p>{/if}
</div>

<style>
	/* as wide as the graphic's own column */
	.figure-title {
		margin: 0 auto 12px;
		text-align: center;
	}
	.title-text {
		font-family: 'Source Serif Pro', serif;
		font-size: 18px;
		font-weight: bold;
		line-height: 1.3;
		margin: 24px 0 0;
		text-wrap: balance; /* a title that has to wrap breaks into even lines, with no stranded last word; one that fits is unchanged */
	}
	.subtitle-text {
		font-family: OpenSans, sans-serif;
		font-size: 14px;
		line-height: 1.4;
		color: var(--brandGray90);
		margin: 9px 0 0;
		text-wrap: balance;
	}
</style>
