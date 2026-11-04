// Morph a polygon into a circle and back, for the poll map's bubble view.
//
// Both shapes are resampled to the same number of points: the polygon's outer ring evenly along
// its perimeter, the circle at even angles, wound the same way and starting at the angle of the
// ring's first point, so each point slides roughly straight to its partner. (This is the idea
// behind flubber's toCircle, without adding a dependency.)

const STEP = 3; // px between resampled points
const MIN_POINTS = 24;
const MAX_POINTS = 160;

function perimeter(ring) {
	let p = 0;
	for (let i = 1; i < ring.length; i++) p += Math.hypot(ring[i][0] - ring[i - 1][0], ring[i][1] - ring[i - 1][1]);
	return p;
}

// n points evenly spaced along a closed ring (first point repeated at the end)
function resample(ring, n) {
	const total = perimeter(ring);
	const out = [];
	let seg = 1;
	let walked = 0; // distance to the start of the current segment
	for (let k = 0; k < n; k++) {
		const target = (k / n) * total;
		while (seg < ring.length - 1) {
			const len = Math.hypot(ring[seg][0] - ring[seg - 1][0], ring[seg][1] - ring[seg - 1][1]);
			if (walked + len >= target) break;
			walked += len;
			seg++;
		}
		const [x0, y0] = ring[seg - 1];
		const [x1, y1] = ring[seg];
		const len = Math.hypot(x1 - x0, y1 - y0) || 1;
		const t = Math.min(1, (target - walked) / len);
		out.push([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t]);
	}
	return out;
}

// > 0 when the ring runs clockwise on screen (y down)
function signedArea(ring) {
	let a = 0;
	for (let i = 1; i < ring.length; i++) a += ring[i - 1][0] * ring[i][1] - ring[i][0] * ring[i - 1][1];
	return a / 2;
}

const toPath = (pts) => 'M' + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('L') + 'Z';

// ring: the shape's outer ring in screen coordinates, closed. Returns t => path string,
// the shape at t = 0 and the circle (cx, cy, r) at t = 1.
export function shapeToCircle(ring, cx, cy, r) {
	const n = Math.max(MIN_POINTS, Math.min(MAX_POINTS, Math.ceil(Math.max(perimeter(ring), 2 * Math.PI * r) / STEP)));
	const from = resample(ring, n);
	const dir = signedArea(ring) >= 0 ? 1 : -1;
	const start = Math.atan2(from[0][1] - cy, from[0][0] - cx);
	const to = from.map((_, i) => {
		const a = start + (dir * 2 * Math.PI * i) / n;
		return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
	});
	return (t) => toPath(from.map((p, i) => [p[0] + (to[i][0] - p[0]) * t, p[1] + (to[i][1] - p[1]) * t]));
}
