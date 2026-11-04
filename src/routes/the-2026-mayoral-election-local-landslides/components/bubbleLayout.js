// Pushes the bubble view's circles apart so none overlap, as the poll map and the change map
// both do: each node is pulled back towards its own shape (x0, y0) and kept clear of its
// neighbours by its radius r.
//
// The layout is only needed once someone switches to bubbles, and it is the slowest thing on the
// page (hundreds of milliseconds to seconds), so it is settled in short slices while the browser is
// idle after the maps are drawn, rather than all at once before they appear. finish() completes
// whatever is left right away, for a click that arrives before the slices have; the result is the
// same either way, as the simulation is deterministic.
import { forceSimulation, forceX, forceY, forceCollide } from 'd3';

const TICKS = 400;
const SLICE_MS = 12; // work per slice, well under a frame so hovering and scrolling stay smooth

export function settleBubbles(nodes) {
	const sim = forceSimulation(nodes)
		.force('x', forceX((d) => d.x0).strength(0.25))
		.force('y', forceY((d) => d.y0).strength(0.25))
		.force('collide', forceCollide((d) => d.r + 0.4).iterations(3))
		.stop();
	let left = TICKS;
	let timer = null;

	function slice() {
		timer = null;
		const end = performance.now() + SLICE_MS;
		do sim.tick(); while (--left > 0 && performance.now() < end);
		if (left > 0) timer = setTimeout(slice, 0);
	}
	timer = setTimeout(slice, 0);

	return {
		finish() {
			clearTimeout(timer);
			timer = null;
			if (left > 0) sim.tick(left);
			left = 0;
		},
		cancel() {
			clearTimeout(timer);
			timer = null;
			left = 0;
		},
	};
}
