<script>
    import VotingSubDivisions from '../data/vsd.geo.json';
    import { onMount } from 'svelte';
    import mapboxgl from "mapbox-gl";
    
    mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nob29sb2ZjaXRpZXMiLCJhIjoiY2w4c3h6M2tuMDIwazNuczU3bXA3ZXpvaSJ9.ShjnM8qiYP6yqz2PcAUBOg';

    export let candidate;

    const candidates = {
        "tory": {
            "name": "John Tory",
            "column": "tory_john",
            "breaks": [0.4, 0.5, 0.6, 0.7],
            "colours": ["#f0f2f6", "#bbc3d2", "#8b98b0", "#55688b", "#1e3765"]
        }
    }

    console.log(candidates[candidate])

    let map;

    onMount(() => {
        map = new mapboxgl.Map({
			container: 'map', 
			style: 'mapbox://styles/schoolofcities/cl9wy9gww000j15r7llrtlun3',
			center: [-79.37, 43.715],
			zoom: 10.5,
			maxZoom: 16,
			minZoom: 9,
			bearing: -17.1,
			projection: 'globe',
			scrollZoom: true,
			attributionControl: true
		});
        map.addControl(new mapboxgl.NavigationControl(), 'top-left');
        map.addControl(new mapboxgl.ScaleControl(), 'bottom-left');
        map.scrollZoom.disable();

        map.on('load', function() {
            map.addSource('VotingSubDivisions', {
                'type': 'geojson',
                'data': VotingSubDivisions
            });

            map.addLayer({
                'id': 'VotingSubDivisionsFill',
                'type': 'fill',
                'source': 'VotingSubDivisions',
                'layout': {},
                'paint': {
                    'fill-color': [
                        'step',
                        ['/', ['get', candidates[candidate].column], ['get', 'total']],
                        candidates[candidate].colours[0],
                        candidates[candidate].breaks[0],
                        candidates[candidate].colours[1],
                        candidates[candidate].breaks[1],
                        candidates[candidate].colours[2],
                        candidates[candidate].breaks[2],
                        candidates[candidate].colours[3],
                        candidates[candidate].breaks[3],
                        candidates[candidate].colours[4]
                    ], 
                    'fill-opacity': 0.75
                }
            });
            map.addLayer({
                'id': 'VotingSubDivisionsLine',
                'type': 'line',
                'source': 'VotingSubDivisions',
                'layout': {},
                'paint': {
                    'line-color': '#fff',
                    'line-width': 1,
                    'line-opacity': 1
                }
            });
        });

    });

</script>


<h2>% {candidates[candidate].name}</h2>

<div id="map"></div>


<style>
    
    h2 {
        font-family: "Source Serif Pro", serif;
        font-weight: bold;
		font-size: 18px;
        text-align: center;
    }

    #map {
		height: 600px;
		width: 100%;
        border-top: 1px solid grey;
        border-bottom: 1px solid grey;
	}

</style>