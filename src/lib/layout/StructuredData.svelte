<script>
	// schema.org structured data (JSON-LD) for search engines and AI crawlers:
	// an Article for a post (pass its slug), or the series itself on the home page.
	// Titles, dates and web cards come from $lib/posts.js; the description is the page's own.
	// Also adds the page's canonical link, so every variant of its URL counts as one page.
	import { posts } from '$lib/posts.js';

	let { slug = null, description } = $props();

	const SITE = 'https://schoolofcities.github.io/place-and-politics-toronto';
	const CARDS = 'https://raw.githubusercontent.com/schoolofcities/place-and-politics-toronto/main/src/assets';
	const SERIES = 'Place & Politics in Toronto';

	const authors = [
		{ '@type': 'Person', name: 'Zack Taylor', url: 'https://zacktaylorwestern.wordpress.com/' },
		{ '@type': 'Person', name: 'Jeff Allen', url: 'https://jamaps.github.io/' },
	];
	const publisher = {
		'@type': 'Organization',
		name: 'School of Cities, University of Toronto',
		url: 'https://www.schoolofcities.utoronto.ca/',
	};

	const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
		'August', 'September', 'October', 'November', 'December'];
	// "November 2, 2022" -> "2022-11-02"
	function isoDate(date) {
		const [, month, day, year] = date.match(/(\w+) (\d+), (\d+)/);
		return `${year}-${String(MONTHS.indexOf(month) + 1).padStart(2, '0')}-${day.padStart(2, '0')}`;
	}

	const article = (post) => ({
		'@type': 'Article',
		headline: post.title,
		url: `${SITE}/${post.slug}`,
		datePublished: isoDate(post.date),
		position: post.part,
	});

	const post = slug ? posts.find((p) => p.slug === slug) : null;
	const canonical = post ? `${SITE}/${post.slug}` : `${SITE}/`;

	const data = post
		? {
			'@context': 'https://schema.org',
			...article(post),
			description,
			image: `${CARDS}/web-card-${post.part}.png`,
			inLanguage: 'en-CA',
			author: authors,
			publisher,
			isPartOf: { '@type': 'CreativeWorkSeries', name: SERIES, url: `${SITE}/` },
		}
		: {
			'@context': 'https://schema.org',
			'@type': 'CreativeWorkSeries',
			name: SERIES,
			url: `${SITE}/`,
			description,
			inLanguage: 'en-CA',
			author: authors,
			publisher,
			hasPart: posts.map(article),
		};

	// escaped so nothing in the data can close the script tag early
	const json = JSON.stringify(data).replace(/</g, '\\u003c');
	const tag = `<script type="application/ld+json">${json}<` + '/script>';
</script>

<svelte:head>
	<link rel="canonical" href={canonical} />
	{@html tag}
</svelte:head>
