<script>
	// Normalized triangle plot for Working Suburbanites: NOT a true ternary, since the 3
	// variables (visible minority %, income, bachelor's+ %) don't sum to anything meaningful
	// on their own. Each is min-max normalized across all 585 tracts to [0, 1], then the 3
	// normalized values are rescaled to proportions a, b, c with a,b,c >= 0 and a+b+c = 1 —
	// that's what places every dot inside the triangle (a barycentric combination of the 3
	// vertices always lands in their convex hull as long as the weights are non-negative and
	// sum to 1). Every tract gets a dot; the active cluster's tracts are coloured, the rest of
	// the city is grey.

	import { extent } from "d3";

	export let values = []; // ct_values.json records
	export let vars = []; // exactly 3: [{ key, label }, { key, label }, { key, label }] — bottom-left, bottom-right, top
	export let clusterId;
	export let color = "#3d53fb";

	const FADE_COLOR = "#d8d8d8";
	const MIN_SIDE = 110; // small enough that the triangle + margins still fit a narrow container
	const LABEL_OFFSET = 16; // how far outside the triangle edge the slanted labels sit

	// Margins only need to hold the label overhang beyond the triangle's own bounding box
	// (worst case ~20px, at MIN_SIDE — shrinking toward 0 as the triangle grows).
	const margin = { top: 22, bottom: 30, left: 26, right: 26 };

	// No upper cap on `side`: like ScatterHighlight, this fills however much width its
	// container (the float-graphic half of the section) actually gives it. Only floored at
	// MIN_SIDE so a narrow container doesn't force the triangle + margins to overflow it.
	let divWidth = 380;
	$: side = Math.max(MIN_SIDE, divWidth - margin.left - margin.right);
	$: triHeight = (side * Math.sqrt(3)) / 2;
	$: totalWidth = side + margin.left + margin.right;
	$: totalHeight = triHeight + margin.top + margin.bottom;

	$: A = { x: 0, y: triHeight };
	$: B = { x: side, y: triHeight };
	$: C = { x: side / 2, y: 0 };
	$: centroid = { x: side / 2, y: (2 * triHeight) / 3 };

	$: ranges = vars.map((v) => extent(values, (d) => d[v.key]));

	// Every dot's (x, y) is computed in one reactive statement that references A/B/C and
	// `ranges` directly, rather than via a helper function that merely closes over them —
	// Svelte only re-runs a `$:` block when the variables *textually present in it* change, so
	// a plain closure wouldn't reliably recompute dots when a resize changes A/B/C via `side`.
	$: points = values.map((d) => {
		const n = ranges.map(([min, max], i) => (max === min ? 0.5 : (d[vars[i].key] - min) / (max - min)));
		const sum = n[0] + n[1] + n[2];
		const [pa, pb, pc] = sum > 0 ? [n[0] / sum, n[1] / sum, n[2] / sum] : [1 / 3, 1 / 3, 1 / 3];
		return { tract: d, x: pa * A.x + pb * B.x + pc * C.x, y: pa * A.y + pb * B.y + pc * C.y };
	});
	$: bgPoints = points.filter((p) => p.tract.cluster_id !== clusterId);
	$: fgPoints = points.filter((p) => p.tract.cluster_id === clusterId);

	// 3 slanted labels per side of the triangle, running parallel to that side: e.g. the left
	// side (bottom-left corner up to the top corner) is labeled with vars[0] — the variable
	// name at the middle, "higher" shifted toward the bottom-left corner, "lower" shifted
	// toward the top corner. Each vertex's variable "owns" the edge connecting it to the
	// *previous* vertex in the A→B→C→A cycle, so each of the 3 variables gets exactly one
	// edge, and each of the 3 edges gets exactly one label set:
	//   edge C→A ("left"):   vars[0], higher at A, lower at C
	//   edge A→B ("bottom"): vars[1], higher at B, lower at A
	//   edge B→C ("right"):  vars[2], higher at C, lower at B
	function outward(p, dist) {
		const dx = p.x - centroid.x;
		const dy = p.y - centroid.y;
		const len = Math.hypot(dx, dy) || 1;
		return { x: p.x + (dx / len) * dist, y: p.y + (dy / len) * dist };
	}
	function along(p1, p2, t) {
		return { x: p1.x + (p2.x - p1.x) * t, y: p1.y + (p2.y - p1.y) * t };
	}
	// A label's rotation follows its edge's own angle (so it reads as "slanted" along that
	// side), normalized to stay within ±90° so the text is never upside down. That
	// normalization also flips which physical direction the rendered arrow glyphs point in —
	// an unrotated "→" ends up pointing toward `higherVertex` on the bottom edge but toward
	// `lowerVertex` on both slanted side edges — so the whole "← lower"/"higher →" template
	// (arrow character AND which side of the word it's on) swaps together whenever the angle
	// had to be normalized, not just the arrow character alone.
	function edgeLabel(lowerVertex, higherVertex, label) {
		let angle = (Math.atan2(higherVertex.y - lowerVertex.y, higherVertex.x - lowerVertex.x) * 180) / Math.PI;
		let flipped = false;
		if (angle > 90) {
			angle -= 180;
			flipped = true;
		} else if (angle < -90) {
			angle += 180;
			flipped = true;
		}
		const parts = [
			{ t: 0.22, text: flipped ? "lower →" : "← lower", tag: true },
			{ t: 0.5, text: label, tag: false },
			{ t: 0.78, text: flipped ? "← higher" : "higher →", tag: true },
		];
		return parts.map(({ t, text, tag }) => {
			const pos = outward(along(lowerVertex, higherVertex, t), LABEL_OFFSET);
			return { x: pos.x, y: pos.y, angle, text, tag };
		});
	}

	$: edgeLabels = [
		...edgeLabel(C, A, vars[0]?.label), // left edge
		...edgeLabel(A, B, vars[1]?.label), // bottom edge
		...edgeLabel(B, C, vars[2]?.label), // right edge
	];
</script>

<div bind:offsetWidth={divWidth}>
	<svg width={totalWidth} height={totalHeight}>
		<g transform={`translate(${margin.left},${margin.top})`}>
			<path class="tri" d={`M${A.x},${A.y} L${B.x},${B.y} L${C.x},${C.y} Z`} />

			{#each bgPoints as p}
				<circle cx={p.x} cy={p.y} r="2.5" fill={FADE_COLOR} />
			{/each}
			{#each fgPoints as p}
				<circle cx={p.x} cy={p.y} r="3.5" fill={color} fill-opacity="0.85" />
			{/each}

			{#each edgeLabels as l}
				<text
					class="side-label"
					class:tag={l.tag}
					x={l.x}
					y={l.y}
					text-anchor="middle"
					transform={`rotate(${l.angle} ${l.x} ${l.y})`}
				>
					{l.text}
				</text>
			{/each}
		</g>
	</svg>
</div>

<style>
	.tri {
		fill: #faf8f2;
		stroke: black;
		stroke-width: 1px;
	}
	.side-label {
		font-size: 11px;
		font-weight: 600;
		fill: black;
		font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
			Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
	}
	/* the "← lower" / "higher →" tags read as secondary to the variable name itself */
	.side-label.tag {
		font-size: 9.5px;
		font-weight: 400;
	}
</style>
