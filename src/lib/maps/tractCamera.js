// Camera helpers for the site's rotated Toronto maps (MapLibre). The same rotation
// (bearing -17.1°) is used by the other maps so the city reads as level.
//
// MapLibre's own fitBounds fits the north-up bounding box, which leaves wide margins once
// the map is rotated, so the camera is instead fitted to the city's actual outline.
// Ported from the camera maths in routes/social-geography-and-the-mayoral-vote/mapper.js.

export const BEARING = -17.1;

// How far the map can be panned: the site maps' box around Toronto, made 10% larger
const PAN_BOX = [
	[-79.6772, 43.44], // SW
	[-79.04763, 44.03074] // NE
];
const PAN_MARGIN = 0.05;
export const MAX_BOUNDS = (([[w, s], [e, n]]) => {
	const dx = (e - w) * PAN_MARGIN;
	const dy = (n - s) * PAN_MARGIN;
	return [
		[w - dx, s - dy],
		[e + dx, n + dy]
	];
})(PAN_BOX);

// Web Mercator coordinates at zoom 0
const WORLD = 512;
const mercX = (lng) => ((lng + 180) / 360) * WORLD;
const mercY = (lat) =>
	((180 - (180 / Math.PI) * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360))) / 360) * WORLD;
const mercLng = (x) => (x / WORLD) * 360 - 180;
const mercLat = (y) =>
	(360 / Math.PI) * Math.atan(Math.exp(((180 - (y / WORLD) * 360) * Math.PI) / 180)) - 90;

/** All vertices of a FeatureCollection, as Web Mercator points. */
export function outlinePoints(collection) {
	const pts = [];
	const walk = (c) => (typeof c[0] === 'number' ? pts.push([mercX(c[0]), mercY(c[1])]) : c.forEach(walk));
	collection.features.forEach((f) => walk(f.geometry.coordinates));
	return pts;
}

/**
 * Centre and zoom that fit `points` into a width x height viewport once rotated by BEARING.
 * Of the spare height, `topShare` goes above the city rather than half, so the city sits
 * slightly high and leaves room under it.
 */
export function rotatedFit(points, width, height, padding, topShare = 0.5) {
	const b = (BEARING * Math.PI) / 180;
	const cos = Math.cos(b);
	const sin = Math.sin(b);
	let x0 = Infinity;
	let x1 = -Infinity;
	let y0 = Infinity;
	let y1 = -Infinity;
	for (const [x, y] of points) {
		const rx = x * cos + y * sin;
		const ry = -x * sin + y * cos;
		if (rx < x0) x0 = rx;
		if (rx > x1) x1 = rx;
		if (ry < y0) y0 = ry;
		if (ry > y1) y1 = ry;
	}
	const zoom = Math.log2(Math.min((width - 2 * padding) / (x1 - x0), (height - 2 * padding) / (y1 - y0)));
	const spare = (height - 2 * padding) / 2 ** zoom - (y1 - y0);
	const cx = (x0 + x1) / 2;
	const cy = (y0 + y1) / 2 + spare * (0.5 - topShare);
	const mx = cx * cos - cy * sin;
	const my = cx * sin + cy * cos;
	return { center: [mercLng(mx), mercLat(my)], zoom };
}
