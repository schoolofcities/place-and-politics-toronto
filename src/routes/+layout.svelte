<script>
	import '$assets/global-styles.css';
	import Footer from '$lib/layout/Footer.svelte';

	let { children } = $props();
</script>

{@render children()}

<Footer />
