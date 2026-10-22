// The width (px) of one colour class in the first turnout map's legend (a fixed-width bar, set
// in TurnoutMap.svelte). Other legends multiply it by their own class count, so every legend in the
// post has the same width per class (e.g. the 7-class Component 1 bar is 7/5 the 5-class one).
import { writable } from 'svelte/store';

export const legendClassWidth = writable(0);
