import maplibregl from 'maplibre-gl';

import SubwayLines from '$data/subwayLines.geo.json';
import SubwayStations from '$data/subwayStations.geo.json';

/** @type {import('maplibre-gl').StyleSpecification} */
const baseMapStyle = {
	version: 8,
	name: 'Toronto Election Base',
	glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
	sources: {
		carto: {
			type: 'raster',
			tiles: [
				'https://a.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
				'https://b.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
				'https://c.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png',
				'https://d.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png'
			],
			tileSize: 256,
			attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
		}
	},
	layers: [
		{
			id: 'background',
			type: 'background',
			paint: {
				'background-color': '#f7f4ef'
			}
		},
		{
			id: 'carto-base',
			type: 'raster',
			source: 'carto',
			paint: {
				'raster-opacity': 0.92,
				'raster-saturation': -0.45,
				'raster-contrast': 0.1,
				'raster-brightness-min': 0.08,
				'raster-brightness-max': 0.96
			}
		}
	]
};

export const createBaseMapStyle = () => structuredClone(baseMapStyle);

/**
 * @param {import('maplibre-gl').Map} map
 */
export const addTransitBaseLayers = (map) => {
	map.addSource('SubwayLines', {
		type: 'geojson',
		data: SubwayLines
	});

	map.addSource('SubwayStations', {
		type: 'geojson',
		data: SubwayStations
	});

	map.addLayer({
		id: 'SubwayLineCasing',
		type: 'line',
		source: 'SubwayLines',
		layout: {
			'line-cap': 'round',
			'line-join': 'round'
		},
		paint: {
			'line-color': 'rgba(255,255,255,0.9)',
			'line-width': 6,
			'line-opacity': 0.95
		}
	});

	map.addLayer({
		id: 'SubwayLine',
		type: 'line',
		source: 'SubwayLines',
		layout: {
			'line-cap': 'round',
			'line-join': 'round'
		},
		paint: {
			'line-color': '#767676',
			'line-width': 2.2,
			'line-opacity': 0.95
		}
	});

	map.addLayer({
		id: 'SubwayStationDots',
		type: 'circle',
		source: 'SubwayStations',
		paint: {
			'circle-radius': 1.8,
			'circle-color': '#767676',
			'circle-stroke-color': '#ffffff',
			'circle-stroke-width': 0.8,
			'circle-opacity': 0.95
		}
	});
};

export default maplibregl;
