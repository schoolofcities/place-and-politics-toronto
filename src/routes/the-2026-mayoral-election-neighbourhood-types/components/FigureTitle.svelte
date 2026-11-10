<script>
	// Title and subtitle above a graphic, so it still makes sense on its own (e.g. screenshotted).
	// Same look as FigureTitle on the 2026 local-landslides page.
	// size: the title's font size in px, for a graphic smaller than the rest (default 18).
	// children: the title as markup (e.g. a word underlined), in place of the plain `title`
	let { title = '', subtitle = '', size = 18, children } = $props();
</script>

<div class="figure-title">
	<p class="title-text" style:font-size="{size}px">{#if children}{@render children()}{:else}{title}{/if}</p>
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
