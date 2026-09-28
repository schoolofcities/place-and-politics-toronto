<script>

	import { onMount } from 'svelte';
	import { replaceState } from '$app/navigation';
	import 'maplibre-gl/dist/maplibre-gl.css';
	import Top from "$lib/layout/TopSofC.svelte";
	import { startMapper } from './mapper.js';

	let root;
	let failed = null;

	onMount(() => {
		let stop = null;
		let unmounted = false;
		startMapper(root, { replaceHash: (hash) => replaceState(hash, {}) })
			.then((fn) => { if (unmounted) fn(); else stop = fn; })
			.catch((err) => { console.error(err); failed = err.message; });
		return () => { unmounted = true; stop?.(); };
	});

</script>

<svelte:head>

	<meta
		name="viewport"
		content="width=device-width, initial-scale=1, minimum-scale=1"
	/>

	<title>Social geography and the mayoral vote</title>
	<meta name="description" content="Side-by-side maps of Toronto census-tract social geography and mayoral election results, with the correlations between them.">
	<meta name="author" content="Zack Taylor & Jeff Allen">

	<meta property="og:title" content="Social geography and the mayoral vote" />
	<meta name="og:description" content="Side-by-side maps of Toronto census-tract social geography and mayoral election results" />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://schoolofcities.github.io/place-and-politics-toronto/social-geography-and-the-mayoral-vote" />
	<meta property="og:locale" content="en_CA">

</svelte:head>

<Top/>

<main>

	<div class="title">

		<h4>Place & Politics in Toronto</h4>

		<div id="mini-line"></div>

		<h1>Social geography and the mayoral vote</h1>
		<h3><a href="https://politicalscience.uwo.ca/people/faculty/full-time_faculty/zack_taylor.html">Zack Taylor</a> & <a href="https://jamaps.github.io/">Jeff Allen</a></h3>

		<div id="mini-line"></div>

	</div>

	<div class="text">
		<p>
			Since amalgamation in 1997, Toronto has held nine mayoral elections. In earlier posts in this series we mapped where candidates found their support. This page puts those results side by side with the city's social geography: housing, income, commuting, education, occupation. Pick a census variable on the left and a candidate on the right, then hover over a tract to see its values on both maps.
		</p>
	</div>

	<div class="mapper" bind:this={root}>

		<div class="panels">

			<section class="panel" aria-labelledby="census-heading">
				<div class="panel-head">
					<h2 id="census-heading">Social geography</h2>
					<div class="controls">
						<label class="field field-wide">
							<span>Variable</span>
							<select id="census-var"></select>
						</label>
						<label class="field" id="census-year-field">
							<span>Census year</span>
							<select id="census-year"></select>
						</label>
					</div>
					<p class="note" id="census-note"></p>
					<div class="legend" id="legend-census"></div>
				</div>
				<div class="map-wrap">
					<div class="map" id="map-census"></div>
					<div class="readout" id="readout-census" hidden></div>
				</div>
			</section>

			<section class="panel" aria-labelledby="election-heading">
				<div class="panel-head">
					<h2 id="election-heading">Mayoral election results</h2>
					<div class="controls">
						<label class="field field-wide">
							<span>Candidate</span>
							<select id="election-cand"></select>
						</label>
						<label class="field">
							<span>Election year</span>
							<select id="election-year"></select>
						</label>
						<div class="radios cand-scope" role="radiogroup" aria-label="Which candidates to list">
							<label class="check"><input type="radio" name="cand-scope-1" value="1"> All candidates</label>
							<label class="check"><input type="radio" name="cand-scope-1" value="0" checked> Only those with over 2% of the vote</label>
						</div>
					</div>
					<p class="note" id="election-note"></p>
					<div class="legend" id="legend-election"></div>
				</div>
				<div class="map-wrap">
					<div class="map" id="map-election"></div>
					<div class="readout" id="readout-election" hidden></div>
				</div>
			</section>

			<div class="loading" id="loading" class:error={failed}>
				{failed ? `Could not load the maps: ${failed}` : 'Loading data…'}
			</div>

		</div>

		<div class="text">
			<p>
				Below, the two maps are combined into one, and each census tract is plotted by its vote share and the characteristic you picked. A word of caution: these are correlations between places, not people. If a candidate did well in tracts with many renters, it does not mean that renters voted for that candidate. And many characteristics are correlated with one another. Tracts with more renters also tend to have more apartments, lower incomes, and more transit commuters, so a correlation of any one of them with vote share may really reflect the others, or something else entirely. Overall, these patterns show where a candidate's support was concentrated, explaining why takes more than a correlation.
			</p>
		</div>

		<!-- bivariate map and scatter: the map as wide as each map above, the scatter half that -->
		<div class="pair-section">

		<!-- the same choices as the dropdowns at the top (kept in sync by mapper.js) -->
		<div class="pair-controls">
			<div class="controls">
				<label class="field field-wide">
					<span>Variable</span>
					<select id="census-var-2"></select>
				</label>
				<label class="field" id="census-year-field-2">
					<span>Census year</span>
					<select id="census-year-2"></select>
				</label>
			</div>
			<div class="controls">
				<label class="field field-wide">
					<span>Candidate</span>
					<select id="election-cand-2"></select>
				</label>
				<label class="field">
					<span>Election year</span>
					<select id="election-year-2"></select>
				</label>
				<div class="radios cand-scope" role="radiogroup" aria-label="Which candidates to list">
					<label class="check"><input type="radio" name="cand-scope-2" value="1"> All candidates</label>
					<label class="check"><input type="radio" name="cand-scope-2" value="0" checked> Only those with over 2% of the vote</label>
				</div>
			</div>
		</div>

		<!-- one legend for the bivariate map and the scatter plot beside it -->
		<div class="legend legend-bi" id="legend-bi"></div>

		<div class="pair">
			<div class="map-wrap">
				<div class="map" id="map-bi"></div>
				<div class="readout" id="readout-bi" hidden></div>
			</div>
			<div class="scatter-col">
				<p class="note" id="scatter-stat"></p>
				<div class="scatter-wrap" id="scatter-big"></div>
				<p class="scatter-foot">
					r = Pearson correlation across census tracts, with the least-squares trend line. Tracts are not people: a correlation here describes places, not voters.
				</p>
			</div>
		</div>

		</div>

		<div class="text">
			<p>
				Even so, some patterns stand out. A handful of characteristics, such as housing type, income, how people commute, and distance from downtown, tend to line up with support for many candidates, and these patterns have been remarkably consistent since amalgamation. The two tables below rank and compare across a slate of categories. The first shows how every census variable relates to the selected candidate's vote share; the second compares the candidate's map with every other candidate's since 1997. Click any row to update the maps above.
			</p>
		</div>

		<section class="corr" id="corr" aria-label="Correlations between vote share, census variables and other candidates">
			<div class="corr-block corr-rank">
				<h3 id="corr-rank-title"></h3>
				<!-- copies of the top dropdowns (kept in sync by mapper.js) -->
				<div class="controls corr-controls">
					<div class="cand-col">
						<label class="field">
							<span>Candidate</span>
							<select id="election-cand-3"></select>
						</label>
						<div class="radios cand-scope" role="radiogroup" aria-label="Which candidates to list">
							<label class="check"><input type="radio" name="cand-scope-3" value="1"> All candidates</label>
							<label class="check"><input type="radio" name="cand-scope-3" value="0" checked> Only those with over 2% of the vote</label>
						</div>
					</div>
					<label class="field">
						<span>Census year</span>
						<select id="census-year-3"></select>
					</label>
					<div class="field">
						<span>Sort</span>
						<div class="seg" id="corr-sort" role="group" aria-label="Sort the table">
							<button type="button" data-sort="group" aria-pressed="true">By category</button>
							<button type="button" data-sort="r" aria-pressed="false">High to low</button>
						</div>
					</div>
				</div>
				<p class="corr-key">
					Pearson <i>r</i> across census tracts: <span class="swatch-pos">blue</span> where the vote share is higher in tracts with more of that characteristic, <span class="swatch-neg">red</span> where it's lower. Faded values aren't statistically significant (p ≥ 0.05).
				</p>
				<div id="corr-table" class="corr-table"></div>
			</div>
			<div class="corr-block corr-votes">
				<h3 id="corr-cand-title"></h3>
				<!-- a copy of the top candidate dropdown (kept in sync by mapper.js) -->
				<div class="controls corr-controls">
					<div class="cand-col">
						<label class="field">
							<span>Candidate</span>
							<select id="election-cand-4"></select>
						</label>
						<div class="radios cand-scope" role="radiogroup" aria-label="Which candidates to list">
							<label class="check"><input type="radio" name="cand-scope-4" value="1"> All candidates</label>
							<label class="check"><input type="radio" name="cand-scope-4" value="0" checked> Only those with over 2% of the vote</label>
						</div>
					</div>
					<div class="field">
						<span>Sort</span>
						<div class="seg" id="cand-sort" role="group" aria-label="Sort the table">
							<button type="button" data-sort="year" aria-pressed="true">By election</button>
							<button type="button" data-sort="r" aria-pressed="false">High to low</button>
						</div>
					</div>
				</div>
				<p class="corr-key">
					Pearson <i>r</i> between the two candidates' vote shares across census tracts: <span class="swatch-pos">blue</span> where their support was strong in the same neighbourhoods, <span class="swatch-neg">red</span> where one was strong where the other was weak. Faded values aren't statistically significant (p ≥ 0.05).
				</p>
				<div id="cand-table" class="corr-table"></div>
			</div>
		</section>

	</div>

	<div class="info">
		<p class="info-title"><strong>Data and methods</strong></p>
		<p>
			All data are for Toronto's 585 census tracts, on 2021 boundaries. Census characteristics and election results were each apportioned from their original geographies to these tracts, so that every census and every election since amalgamation can be compared on the same map. Correlations are Pearson coefficients across tracts, calculated in the browser for whatever is selected; values with p ≥ 0.05 are shown faded. This page is adapted from the <a href="https://github.com/zacktayloruwo/toronto-elections-mapper">Toronto elections mapper</a> built by Zack Taylor.
		</p>
		<ul>
			<li><strong><em>Census:</em></strong> Statistics Canada censuses, 1996 to 2021, apportioned to 2021 census tracts using the <a href="https://doi.org/10.1111/cag.12467">Canadian Longitudinal Census Tract Database</a> (Allen and Taylor, 2018). Income, density and access measures are shown as standard deviations from the average tract.</li>
			<li><strong><em>Proximity:</em></strong> Statistics Canada's Proximity Measures Database (2023), measured once and applied to every census year.</li>
			<li><strong><em>Elections:</em></strong> poll-level mayoral results, 1997 to 2023. Only election-day votes are included, as advance votes can't be placed in a neighbourhood. Polls were split into dissemination blocks by population and summed to 2021 census tracts.</li>
			<li><strong><em>Boundaries:</em></strong> census tracts from Statistics Canada; wards, former municipalities and neighbourhoods from the City of Toronto. Ward lines match the selected election (25 wards from 2018, 44 wards from 2000 to 2014, none for 1997). Basemap © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors.</li>
		</ul>
	</div>

</main>

<style>

	.info-title { font-size: 17px; }
	.info ul { margin: 0; padding-left: 18px; }
	.info li { margin-bottom: 8px; }

	/* a little more room between the body text and the charts around it */
	main > .text, .mapper > .text { margin-top: 20px; margin-bottom: 20px; }

	.mapper {
		--ink: var(--brandGray90);
		--muted: var(--brandGray60);
		--line: var(--brandGray);
		--accent: var(--brandDarkBlue);
		--focus: var(--linkHover);
		font-family: OpenSans, sans-serif;
		color: var(--ink);
		margin: 10px auto 0 auto;
		width: 100%;
	}

	.mapper :global(strong) {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
	}

	.panels {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 16px;
	}

	/* each panel's header and map share rows with the other panel's, so the two
	   maps line up even when one header wraps onto more lines */
	.panel {
		display: grid;
		grid-row: span 2;
		grid-template-rows: subgrid;
		grid-template-columns: minmax(0, 1fr);
		row-gap: 0;
		min-width: 0;
		border-top: 1px solid grey;
		border-bottom: 1px solid grey;
	}

	.panel-head {
		padding: 10px 2px 8px;
	}

	h2 {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
		font-size: 16px;
		color: var(--brandGray90);
		margin: 0 0 8px;
	}

	.controls {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 12px;
		align-items: flex-end;
	}

	.field { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
	/* `hidden` is set from mapper.js, so these rules must be global or Svelte drops them as unused */
	.mapper :global(.field[hidden]) { display: none; }
	.field-wide { flex: 1 1 240px; }
	.field > span { font-family: OpenSansBold, sans-serif; font-size: 12px; color: var(--muted); }

	select {
		font-family: OpenSans, sans-serif;
		font-size: 14px;
		color: var(--ink);
		background: white;
		border: 1px solid #c8c8c8;
		border-radius: 0px;
		padding: 5px 8px;
		max-width: 100%;
	}

	select:hover { border-color: #9ba1a8; }

	select:focus-visible, input:focus-visible {
		outline: 2px solid var(--focus);
		outline-offset: 1px;
	}

	.note {
		margin: 8px 0 0;
		font-size: 13px;
		line-height: 1.45;
		color: var(--brandGray80);
		min-height: 1.2em;
	}

	.note :global(strong) { color: black; font-size: 14px; }

	/* the rotated city is wide and short, so the map is too */
	/* a grid item with an aspect ratio sizes its width from its height unless told to fill the column */
	.map-wrap { position: relative; width: 100%; aspect-ratio: 1.59; min-height: 320px; border: 1px solid #dcdcdc; box-sizing: border-box; }
	.map { position: absolute; inset: 0; }

	.readout {
		position: absolute;
		background: rgba(255, 255, 255, 0.94);
		border: 1px solid var(--line);
		padding: 8px 10px;
		font-size: 12px;
		z-index: 2;
	}

	.legend { margin-top: 8px; font-size: 12px; }
	.legend :global(.legend-sub) { color: var(--muted); font-size: 11px; margin-bottom: 3px; }
	.legend :global(.legend-row) { display: flex; align-items: flex-start; gap: 14px; }
	.legend :global(.legend-scale) { width: min(280px, 70%); }
	/* one bar of equal-width classes; each break is labelled once, under the boundary it marks */
	.legend :global(.legend-bar) { display: flex; height: 12px; border: 1px solid rgba(0, 0, 0, 0.15); }
	.legend :global(.legend-bar span) { flex: 1; }
	.legend :global(.legend-ticks) { position: relative; height: 18px; font-size: 11px; font-variant-numeric: tabular-nums; }
	.legend :global(.legend-ticks span) { position: absolute; top: 2px; transform: translateX(-50%); white-space: nowrap; }
	.legend :global(.legend-na) { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--muted); }
	.legend :global(.swatch-na) { width: 12px; height: 10px; border: 1px solid rgba(0, 0, 0, 0.15); background: repeating-linear-gradient(45deg, #e4e4df 0 3px, #f3f3ef 3px 6px); }

	.readout { right: 10px; bottom: 10px; min-width: 160px; max-width: 250px; pointer-events: none; }
	.readout :global(.ct) { color: var(--muted); font-size: 11px; }
	.readout :global(.val-row) { display: flex; align-items: baseline; gap: 8px; }
	.readout :global(.val) { font-family: OpenSansBold, sans-serif; font-size: 17px; font-variant-numeric: tabular-nums; }
	.readout :global(.pair-row) { display: flex; gap: 16px; margin-top: 2px; }
	.readout :global(.val-md) { font-family: OpenSansBold, sans-serif; font-size: 14px; font-variant-numeric: tabular-nums; }
	.readout :global(.aside) { color: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
	.readout :global(.detail) { color: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
	.readout :global(.place) { color: var(--muted); font-size: 11px; }
	.readout :global(.place:empty) { display: none; }

	.loading {
		position: absolute;
		inset: 0;
		display: grid;
		place-items: center;
		background: rgba(255, 254, 253, 0.85);
		font-size: 15px;
		color: var(--muted);
		z-index: 10;
	}
	.mapper :global(.loading[hidden]) { display: none; }
	.loading.error { color: var(--brandRed); }

	/* bivariate map key: 3 x 3 swatches, low-low at bottom left */
	/* the dropdowns start together at the top; the candidate radios take their own line below */
	.pair-controls .controls { align-items: flex-start; }
	.pair-controls .cand-scope { flex-basis: 100%; }
	.pair-controls { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; border-top: 1px solid grey; padding: 12px 2px 0; }
	.legend-bi { display: flex; align-items: center; gap: 16px; padding: 12px 2px 12px; margin-top: 0; }
	.legend-bi :global(.bi-key) { display: block; overflow: visible; flex: none; }
	.legend-bi :global(.bi-text) { margin: 0; font-size: 13px; line-height: 1.5; color: var(--brandGray80); max-width: 560px; }
	.legend-bi :global(.bi-text strong) { color: black; }
	/* Sized from the page width W: each map above is (W - 16px) / 2 wide, so this
	   section is that plus a gap plus a scatter half as wide, centred */
	.pair-section { width: calc(0.75 * (100% - 16px) + 20px); margin: 0 auto; }
	.pair { display: grid; grid-template-columns: minmax(0, 2fr) minmax(0, 1fr); gap: 20px; align-items: start; }
	.scatter-col .note { margin: 0 0 6px; text-align: center; }
	.scatter-foot { margin: 6px 0 0; font-size: 11px; line-height: 1.45; color: var(--muted); }
	.legend-bi :global(.bi-cell) { stroke: white; stroke-width: 1; }
	.legend-bi :global(.bi-lab) { font-family: OpenSansBold, sans-serif; font-size: 11px; fill: var(--brandGray80); }

	/* large scatter, the same size as the map beside it */
	.scatter-wrap { width: 100%; aspect-ratio: 1; }
	.scatter-wrap :global(svg) { display: block; }
	.scatter-wrap :global(svg text) { font-family: OpenSans, sans-serif; font-size: 12px; fill: var(--ink); }
	.scatter-wrap :global(svg text.ax) { fill: var(--brandGray70); font-size: 11px; }
	.scatter-wrap :global(svg text.axlab) { fill: var(--brandGray80); font-size: 12px; font-family: OpenSansBold, sans-serif; }
	.scatter-wrap :global(svg text.stat) { font-size: 15px; font-family: OpenSansBold, sans-serif; font-variant-numeric: tabular-nums; }
	.scatter-wrap :global(svg .axis) { stroke: var(--line); }
	.scatter-wrap :global(svg .pt) { fill: black; fill-opacity: 0.6; }
	.scatter-wrap :global(svg .band) { opacity: 0.65; }
	/* labels drawn over the coloured bands get a white halo */
	.scatter-wrap :global(svg text.stat), .scatter-wrap :global(svg text.ax) { paint-order: stroke; stroke: rgba(255, 255, 255, 0.85); stroke-width: 3px; stroke-linejoin: round; }
	.scatter-wrap :global(svg .pt.hl) { fill: #F1C500; fill-opacity: 1; stroke: black; stroke-width: 1.2; }
	.scatter-wrap :global(svg .fit) { stroke: black; stroke-width: 2; }

	/* correlations, below the maps */

	.corr {
		display: flex;
		flex-wrap: wrap;
		gap: 20px;
		padding: 16px 2px 14px;
		border-top: 1px solid grey;
		border-bottom: 1px solid grey;
	}

	/* section titles, matching the map panels' headings */
	.corr-block h3 {
		font-family: OpenSansBold, sans-serif;
		font-weight: normal;
		margin: 0 0 8px;
		font-size: 16px;
		line-height: 1.35;
		color: var(--brandGray90);
	}

	/* the four blocks share the width in fixed ratios; the charts are drawn to fit.
	   The flex-basis values decide when a block wraps to a new row instead of being squeezed. */
	/* the full table takes its own row; the candidate bars sit below it */
	.corr-rank { flex: 1 1 100%; }
	.corr-controls { margin-bottom: 10px; align-items: flex-start; }
	/* the candidate dropdown with its radio buttons underneath */
	.cand-col { display: flex; flex-direction: column; gap: 6px; }
	.cand-col .radios { padding-bottom: 0; }
	/* the "which candidates" choice: small radio buttons */
	.radios { display: flex; flex-wrap: wrap; align-items: center; gap: 2px 14px; padding-bottom: 6px; }
	.check { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--muted); cursor: pointer; }
	.check input { accent-color: var(--accent); margin: 0; }

	/* two-button toggle, styled like the dropdowns */
	.seg { display: flex; }
	.seg button { font-family: OpenSans, sans-serif; font-size: 14px; color: var(--ink); background: white; border: 1px solid #c8c8c8; padding: 5px 10px; cursor: pointer; }
	.seg button + button { border-left: none; }
	.seg button:hover { border-color: #9ba1a8; }
	.seg button[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: white; }
	.corr-table > :global(.ct-row) { break-inside: avoid; }
	.corr-table :global(.ct-cat) { display: block; font-size: 10px; color: var(--muted); line-height: 1.2; }
	.corr-key { margin: 0 0 17px; padding-bottom: 10px; border-bottom: 1px solid #efefef; font-size: 12px; line-height: 1.45; color: var(--brandGray80); max-width: 760px; }
	/* the table's own colours at r = +0.8 and -0.8 (d3 interpolateRdBu) */
	.corr-key .swatch-pos, .corr-key .swatch-neg { color: white; font-family: OpenSansBold, sans-serif; padding: 0 4px; }
	.corr-key .swatch-pos { background: rgb(34, 101, 163); }
	.corr-key .swatch-neg { background: rgb(172, 32, 47); }
	.corr-table { column-width: 250px; column-gap: 28px; }
	.corr-table :global(.ct-group) { break-inside: avoid; margin-bottom: 14px; }
	.corr-table :global(.ct-group-name) { font-family: OpenSansBold, sans-serif; font-size: 12px; color: var(--brandGray90); border-bottom: 1px solid var(--line); padding-bottom: 2px; margin-bottom: 3px; }
	.corr-table :global(.ct-row) { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 1px 2px; font-size: 12px; cursor: pointer; }
	.corr-table :global(.ct-row:hover) { background: rgba(30, 55, 101, 0.07); }
	.corr-table :global(.ct-row.sel) { background: rgba(241, 197, 0, 0.25); }
	.corr-table :global(.ct-row.sel .ct-label) { font-family: OpenSansBold, sans-serif; }
	.corr-table :global(.ct-label) { color: var(--brandGray90); }
	.corr-table :global(.ct-r) { flex: none; width: 46px; text-align: center; font-size: 11px; font-variant-numeric: tabular-nums; padding: 1px 0; }
	.corr-table :global(.ct-r.ns) { opacity: 0.3; }
	.corr-votes { flex: 1 1 100%; border-top: 1px solid var(--line); padding-top: 16px; }
	.corr :global(.corr-stat) { margin: 2px 0 0; font-size: 12px; color: var(--muted); }

	/* map controls */

	/* "whole city" button: corner brackets, matching the zoom buttons' weight */
	.mapper :global(.maplibregl-ctrl button.ctrl-fit .maplibregl-ctrl-icon) {
		background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='none' stroke='%23333' stroke-width='1.8' stroke-linecap='round'%3E%3Cpath d='M4 8V4h4M16 8V4h-4M4 12v4h4M16 12v4h-4'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: center;
	}

	@media (max-width: 900px) {
		.panels, .pair, .pair-controls { grid-template-columns: minmax(0, 1fr); }
		.pair-section { width: 100%; }
		.map-wrap { aspect-ratio: 4 / 3; }
		.corr-block + .corr-block { border-left: none; padding-left: 0; }
	}

</style>
