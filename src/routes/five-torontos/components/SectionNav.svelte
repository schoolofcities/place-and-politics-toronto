<script>
	// "On this page" menu for the five-torontos story: a list of the page's sections that
	// highlights the one being read (scrollspy) and jumps to a section on click. Fixed at the top
	// left: just below the site header, then near the top of the screen once that scrolls away. Wide screens: the list itself, in the empty left margin
	// beside the 850px content. Narrower screens: a small "Sections" button that opens the list.

	import { onMount } from "svelte";

	export let items = []; // [{ id, label, color? }] in page order; `id` is the section element's id

	let activeId = items[0]?.id;
	let open = false; // narrow-screen menu

	// Sits just below the site header (which scrolls away with the page), then follows it up as
	// the page scrolls, settling near the top of the screen once the header is gone.
	const TOP_START = 70; // px: below the 50px header
	const TOP_MIN = 8; // px: once scrolled past the header
	let scrollY = 0;
	$: top = Math.max(TOP_MIN, TOP_START - scrollY);

	onMount(() => {
		// a section counts as "current" once it crosses a band a little above the middle of the screen
		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting) activeId = entry.target.id;
				}
			},
			{ rootMargin: "-35% 0px -60% 0px" }
		);
		const els = items.map((item) => document.getElementById(item.id)).filter(Boolean);
		els.forEach((el) => observer.observe(el));
		return () => observer.disconnect();
	});

	function jump(event, id) {
		const el = document.getElementById(id);
		if (!el) return;
		event.preventDefault();
		const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
		el.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
		history.replaceState(null, "", `#${id}`);
		activeId = id;
		open = false;
	}
</script>

<svelte:window bind:scrollY />

<nav class="section-nav" class:open aria-label="Sections on this page" style:top="{top}px">
	<button
		type="button"
		class="nav-toggle"
		aria-expanded={open}
		aria-controls="section-nav-list"
		on:click={() => (open = !open)}
	>
		Sections
	</button>
	<ol id="section-nav-list">
		{#each items as item (item.id)}
			<li>
				<a
					href={`#${item.id}`}
					class:active={item.id === activeId}
					aria-current={item.id === activeId ? "location" : undefined}
					on:click={(e) => jump(e, item.id)}
				>
					{#if item.color}
						<span class="dot" style:background={item.color}></span>
					{/if}
					{item.label}
				</a>
			</li>
		{/each}
	</ol>
</nav>

<style>
	.section-nav {
		position: fixed;
		z-index: 20;
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		line-height: 1.3;
	}
	ol {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	li + li {
		margin-top: 2px;
	}
	a {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 3px 8px;
		border-left: 2px solid transparent;
		color: var(--brandGray70);
		text-decoration: none;
	}
	a:hover {
		color: var(--brandBlack);
		text-decoration: none;
	}
	/* the section being read */
	a.active {
		border-left-color: var(--brandGray80);
		color: var(--brandBlack);
		font-family: OpenSansBold, sans-serif;
	}
	.dot {
		flex: none;
		box-sizing: border-box;
		width: 9px;
		height: 9px;
		border-radius: 50%;
		border: 1px solid var(--brandGray70);
		box-shadow: inset 0 0 0 1px white;
	}

	/* top left; its `top` is set inline, following the site header up as the page scrolls */
	.section-nav {
		left: 16px;
	}

	/* Wide screens: the list in the left margin; no toggle button. Only from 1240px, where the
	   margin beside the 850px content is wide enough for it. */
	@media (min-width: 1240px) {
		.section-nav {
			width: 180px;
		}
		.nav-toggle {
			display: none;
		}
	}

	/* Narrower screens: a small button; the list opens below it */
	@media (max-width: 1239px) {
		.section-nav {
			left: 12px;
		}
		.nav-toggle {
			font-family: OpenSans, sans-serif;
			font-size: 13px;
			color: var(--brandGray90);
			background: white;
			border: 1px solid #c8c8c8;
			padding: 5px 10px;
			cursor: pointer;
			box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
		}
		.nav-toggle:hover {
			border-color: #9ba1a8;
		}
		ol {
			display: none;
			position: absolute;
			left: 0;
			top: calc(100% + 6px);
			width: 210px;
			padding: 6px 0;
			background: white;
			border: 1px solid #c8c8c8;
			box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
		}
		.open ol {
			display: block;
		}
	}
</style>
