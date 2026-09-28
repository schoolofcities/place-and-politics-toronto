<script>
	import { base } from '$app/paths';
	import { page } from '$app/state';
	import { posts } from '$lib/posts.js';
	import logoFull from '$assets/top-logo-full.svg';

	// the home page already lists the posts, so it has no footer
	const isHome = $derived(page.route.id === '/');

	// the post being read is shown, but not linked
	const isCurrent = (slug) => page.url.pathname.replace(/\/$/, '').endsWith(`/${slug}`);
</script>

{#if !isHome}
<footer>
	<div class="inner">
		<p class="series"><a href="{base}/">Place & Politics in Toronto</a></p>
		<ol>
			{#each posts as post}
				<li>
					<span class="thumb" style="background-image: url({post.image});"></span>
					<span class="post">
						<span class="date">Part {post.part} · {post.date}</span>
						{#if isCurrent(post.slug)}
							<span class="current">{post.title}</span>
						{:else}
							<a href="{base}/{post.slug}">{post.title}</a>
						{/if}
					</span>
				</li>
			{/each}
		</ol>
	</div>
	<!-- the logo gets its own row, below a full-width line -->
	<div class="logo-row">
		<a class="logo" href="https://www.schoolofcities.utoronto.ca/"><img src={logoFull} alt="University of Toronto, School of Cities"></a>
	</div>
</footer>
{/if}

<style>
	footer {
		margin-top: 60px;
		border-top: 1px solid grey;
		background-color: #fffefd;
		font-family: "Source Serif Pro", serif;
	}

	/* only as wide as the list, so the footer sits in the middle of the page */
	.inner {
		width: fit-content;
		max-width: calc(100% - 50px);
		margin: 0 auto;
		padding: 25px 25px 20px;
	}

	.logo-row {
		border-top: 1px solid grey;
		padding: 46px 25px 60px;
		text-align: center;
	}

	.series {
		font-size: 17px;
		margin: 0 0 12px;
	}

	.series a {
		text-decoration: none;
	}

	ol {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	li {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 12px;
		font-size: 15px;
		line-height: 1.4;
	}

	/* the round thumbnails from the home page, a size down */
	.thumb {
		flex: none;
		width: 40px;
		height: 40px;
		border: solid 1px #4b4b4b;
		border-radius: 50%;
		background-size: cover;
		background-position: center;
	}

	.date {
		display: block;
		font-family: OpenSans, sans-serif;
		font-size: 12px;
		color: var(--brandGray60);
	}

	.logo {
		display: inline-block;
	}

	.logo img {
		display: block;
		height: 40px;
		width: auto;
	}

	.logo:hover img {
		opacity: 0.6;
	}

	.current {
		color: var(--brandGray60);
	}
</style>
