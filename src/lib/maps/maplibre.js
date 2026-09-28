import maplibregl from 'maplibre-gl';

/** @type {import('maplibre-gl').StyleSpecification} */
const baseMapStyle = {
	version: 8,
	name: 'Toronto Election Base',
	glyphs: 'https://schoolofcities.github.io/fonts/fonts/{fontstack}/{range}.pbf',
	sources: {
		osm: {
			type: 'vector',
			tiles: [
				'https://vector.openstreetmap.org/shortbread_v1/{z}/{x}/{y}.mvt'
			],
			maxzoom: 14,
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
		}
	},
	layers: [
		{
			id: 'background',
			type: 'background',
			paint: {
				'background-color': '#fff'
			}
		},
		{
			id: 'water',
			type: 'fill',
			source: 'osm',
			'source-layer': 'water_polygons',
			paint: {
				'fill-color': '#e6e4e0'
			}
		},
		{
			id: 'ocean',
			type: 'fill',
			source: 'osm',
			'source-layer': 'ocean',
			paint: {
				'fill-color': '#e6e4e0'
			}
		}
	]
};

export const createBaseMapStyle = () => structuredClone(baseMapStyle);

export default maplibregl;
