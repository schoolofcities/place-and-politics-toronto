<script>
	// Map of Toronto's census tracts by who led the Chow vs. main-opponent contest in 2023 and 2026,
	// with a small bar chart in the empty lake corner: the votes Chow added in each kind of tract.
	// Static: pre-simplified tracts (../data/new_votes_tracts.geojson) and group totals
	// (../data/new_votes_groups.json), built by analysis/election_2026/03_neighbourhood_types_page_data.ipynb, Section 4.
	import { geoMercator, geoPath, scaleLinear } from 'd3';
	import FigureTitle from './FigureTitle.svelte';
	import { newVotes, newVotesTracts, newVotesMunicipalities, groupByKey, groupOrder } from './data.js';
	import { GROUP_COLOURS } from './config.js';

	let width = $state(680);
	const small = $derived(width < 460);
	// rotated 17 degrees, like the site's other Toronto maps, so the lakeshore runs level
	const projection = $derived(geoMercator().angle(-17).fitWidth(width, newVotesTracts));
	const path = $derived(geoPath(projection).digits(1));
	const mapH = $derived(Math.ceil(path.bounds(newVotesTracts)[1][1]) + 1);
	const tracts = $derived(newVotesTracts.features.map((f) => ({ ct: f.properties.ct, g: f.properties.g, d: path(f) })));

	// the former municipalities' outlines (black on a white casing) and names (with a white halo), as on the
	// local-landslides change map; line widths scale with the map so it stays fine on a phone
	const munis = $derived(
		newVotesMunicipalities.features.map((f) => {
			const { name, label_lon, label_lat } = f.properties;
			const [x, y] = projection([label_lon, label_lat]);
			return { name, d: path(f), lines: labelLines(name), x, y };
		})
	);
	// a name split after each hyphen, or at the last space if longer than 13 characters
	function labelLines(name) {
		const parts = name.split(/(?<=[-–—])/);
		if (parts.length > 1) return parts;
		const sp = name.lastIndexOf(' ');
		if (name.length > 13 && sp !== -1) return [name.slice(0, sp), name.slice(sp + 1)];
		return [name];
	}
	const LABEL_SIZE = $derived(small ? 9.5 : 11);
	const LABEL_LEADING = $derived(small ? 10.5 : 12);
	const lineW = $derived(Math.max(0.6, width / 760));

	// the inset bars, left to right: opponent both times, flipped, Chow both times. Text is right-aligned, on the right.
	const BARS = ['trailing', 'flipped', 'held'].map((k) => groupByKey[k]);
	const city = newVotes.meta.citywide;
	const BAR_W = $derived(small ? 18 : 44);
	const GAP = $derived(small ? 4 : 8);
	// what each bar is, written under it where there is room (not on small screens)
	const BAR_LABELS = { trailing: ['Opponent', 'both times'], flipped: ['Flipped', 'to Chow'], held: ['Chow', 'both times'] };
	const LABEL_H = $derived(small ? 0 : 30);
	const AXIS_W = $derived(small ? 28 : 32); // y-axis labels, right of the bars
	const PLOT_W = $derived(BARS.length * BAR_W + (BARS.length - 1) * GAP);
	const IN_W = $derived(Math.max(PLOT_W + AXIS_W + 8, small ? 92 : 108));
	const IN_H = $derived(small ? 84 : 162);
	const PLOT_TOP = $derived(small ? 34 : 38); // under the two-line title
	// the inset sits in the map's empty lake corner, flush with the map's bottom edge; on small screens a little of it hangs below
	const EXTRA = $derived(small ? 36 : 30);
	const height = $derived(mapH + EXTRA);
	const IN_X = $derived(width - IN_W);
	const IN_Y = $derived(height - IN_H);
	const y = $derived(scaleLinear().domain([0, 112000]).range([IN_H - 2 - LABEL_H, PLOT_TOP]));
	const TICKS = [0, 50000, 100000];
	const tickText = (t) => (t === 0 ? '0' : `${t / 1000}K`);
	const gridX0 = $derived(IN_W - AXIS_W - PLOT_W - 4);
	const gridX1 = $derived(IN_W - AXIS_W);
	const barX = (i) => IN_W - AXIS_W - PLOT_W + i * (BAR_W + GAP);

	const counts = groupOrder.map((k) => `${groupByKey[k].tracts} ${groupByKey[k].label}`).join(', ');
	const added = BARS.map((b) => `${b.label}: ${b.added_votes.toLocaleString('en-CA')}`).join('; ');
</script>

<figure>
	<FigureTitle title="Who led each tract in 2023 and 2026" />

	<div class="legend">
		{#each groupOrder as k (k)}
			<span class="item"><span class="swatch" style:background={GROUP_COLOURS[k]}></span>{groupByKey[k].label}</span>
		{/each}
	</div>

	<div class="map" bind:clientWidth={width}>
		<svg {width} {height} viewBox="0 0 {width} {height}" role="img" aria-label="Map of Toronto's census tracts by who led, Chow or her main opponent, in 2023 and in 2026. Tracts: {counts}. Inset bars, Chow's added votes: {added}.">
			{#each tracts as t (t.ct)}
				<path d={t.d} fill={GROUP_COLOURS[t.g]} />
			{/each}
			<g class="munis">
				{#each munis as m (m.name)}<path class="casing" d={m.d} style:stroke-width="{3 * lineW}px" />{/each}
				{#each munis as m (m.name)}<path class="line" d={m.d} style:stroke-width="{lineW}px" />{/each}
				{#each munis as m (m.name)}
					<text class="muni-label" x={m.x} y={m.y - ((m.lines.length - 1) * LABEL_LEADING) / 2} style:font-size="{LABEL_SIZE}px">
						{#each m.lines as line, j (j)}<tspan x={m.x} dy={j === 0 ? '0.35em' : LABEL_LEADING}>{line}</tspan>{/each}
					</text>
				{/each}
			</g>

			<g transform="translate({IN_X},{IN_Y})">
				<text class="in-title" x={IN_W} y={small ? 10 : 11} style:font-size={small ? "10px" : null}>Votes Chow added</text>
				<text class="in-title" x={IN_W} y={small ? 22 : 24} style:font-size={small ? "10px" : null}>city-wide, by zone</text>
				{#each TICKS as t (t)}
					<line class="grid" class:zero={t === 0} x1={gridX0} x2={gridX1} y1={y(t)} y2={y(t)} />
					<text class="tick" x={IN_W} y={y(t)} dy="0.35em">{tickText(t)}</text>
				{/each}
				{#each BARS as b, i (b.key)}
					<rect x={barX(i)} y={y(b.added_votes)} width={BAR_W} height={y(0) - y(b.added_votes)} fill={GROUP_COLOURS[b.key]} />
					{#if !small}
						{#each BAR_LABELS[b.key] as line, j (j)}
							<text class="bar-label" x={barX(i) + BAR_W / 2} y={y(0) + 13 + j * 12}>{line}</text>
						{/each}
					{/if}
				{/each}
			</g>
		</svg>
	</div>

	<figcaption class="note">
		Census tracts by who led, Chow or her main opponent, in each election; black lines are the former municipalities. Other is two
		tracts Chow led in 2023 but not 2026, and four exact ties. The bars show the votes Chow added from 2023 to 2026 in each kind of
		tract: {city.added_votes.toLocaleString('en-CA')} in all, {groupByKey.other.added_votes.toLocaleString('en-CA')} of them in the other tracts. Votes cast rose
		{Math.round(city.valid_growth_pct)}%, so part of each gain is higher turnout. Mapped poll votes only (about 78% of valid votes
		in 2023 and 76% in 2026); advance and mail-in votes are excluded.
	</figcaption>
</figure>

<style>
	/* as wide as the paragraphs (the page's .graphic wrapper sets that width) */
	figure {
		margin: 0;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 6px 18px;
		margin: 0 0 10px;
		font-family: OpenSans, sans-serif;
		font-size: 13px;
		color: var(--brandGray80);
	}
	.item {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.swatch {
		width: 14px;
		height: 14px;
		display: inline-block;
		flex: none;
	}
	.map {
		width: 100%;
	}
	svg {
		display: block;
		max-width: 100%; /* the first, pre-measurement render scales down instead of overflowing */
		height: auto;
		overflow: visible;
		font-family: OpenSans, sans-serif;
	}
	/* a fine hairline between tracts, in the page colour (as on the local-landslides change map) */
	.map path {
		stroke: #fff;
		stroke-width: 0.25;
		stroke-linejoin: round;
	}
	.munis path {
		fill: none;
		pointer-events: none;
	}
	.munis .casing {
		stroke: #fff;
	}
	.munis .line {
		stroke: #000;
	}
	.muni-label {
		fill: var(--brandGray90);
		text-anchor: middle;
		paint-order: stroke;
		stroke: #fff;
		stroke-width: 3px;
		stroke-opacity: 0.84; /* the halo only; the text stays solid */
		stroke-linejoin: round;
		pointer-events: none;
	}
	.in-title {
		font-family: OpenSansBold, sans-serif;
		font-size: 11px;
		fill: var(--brandGray90);
		text-anchor: end;
	}
	.bar-label {
		font-size: 10px;
		fill: var(--brandGray80);
		text-anchor: middle;
	}
	.grid {
		stroke: #e6e6e6;
		stroke-width: 1;
	}
	.grid.zero {
		stroke: var(--brandGray60);
	}
	.tick {
		font-size: 10px;
		fill: var(--brandGray60);
		text-anchor: end;
	}
	.note {
		margin: 14px 0 0;
		font-family: OpenSans, sans-serif;
		font-size: 11px;
		line-height: 1.45;
		color: var(--brandGray60);
	}
</style>
