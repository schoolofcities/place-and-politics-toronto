<script>
    
    import { onMount } from 'svelte';
    import mapboxgl from "mapbox-gl";
    
    import VotingSubDivisions from '../data/vsd.geo.json';
    import Wards from '../data/wards.geo.json';
    import WardPts from '../data/wardsPts.geo.json';
    
    mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nob29sb2ZjaXRpZXMiLCJhIjoiY2w2Z2xhOXprMTYzczNlcHNjMnNvdGlmNCJ9.lOgVHrajc1L-LlU0as2i2A';

    export let candidate;
    
    let pageHeight;
    let initZoom = 10.5;

    let mapHeight = 600;
    $: if (pageHeight < 800) {
        mapHeight = pageHeight - 200;
        initZoom = 8.5;
    } else {
        mapHeight = 600
        initZoom = 10.5;
    }

    const candidates = {
        "tory": {
            "name": "John Tory",
            "column": "tory_john",
            "breaks": [0.4, 0.5, 0.6, 0.7],
            "colours": ["#deebfd", "#a7c9ff", "#77a5ff", "#507fff", "#3d53fb"]
        }, 
        "penalosa": {
            "name": "Gil Peñalosa",
            "column": "penalosa_gil",
            "breaks": [0.1, 0.2, 0.3, 0.4],
            "colours": ["#defde0", "#b3e5b2", "#8acc84", "#62b354", "#369a1b"]
        },
        "brown": {
            "name": "Chloe Brown",
            "column": "brown_chloe_marie",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#fddede", "#f0b7b6", "#e1908e", "#ce6967", "#b94141"]
        },
        "margin": {
            "name": "Margin between first- and second-place finisher",
            "column": "margin",
            "breaks": [0.05, 0.1, 0.2, 0.4],
            "colours": ["#ff3ca5", "#c78bf4", "#8bbbff", "#99daf7", "#def1f1"]
        }
    }

    const layerOpacity = 0.69;

    let message = " ";    

    let map;

    const maxBounds = [
		[-79.6772, 43.4400], // SW coords
		[-79.04763, 44.03074] // NE coords
	];

    onMount(() => {
        map = new mapboxgl.Map({
			container: candidate, 
			style: 'mapbox://styles/schoolofcities/cl9wy9gww000j15r7llrtlun3',
			center: [-79.37, 43.715],
			zoom: initZoom,
			maxZoom: 16.5,
			minZoom: 8.5,
			bearing: -17.1,
			projection: 'globe',
			scrollZoom: true,
            maxBounds: maxBounds,
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

            map.addSource('Wards', {
                'type': 'geojson',
                'data': Wards
            });
            map.addSource('WardPts', {
                'type': 'geojson',
                'data': WardPts
            });
            
            if (candidate === "margin") {
                map.addLayer({
                'id': 'VotingSubDivisionsFill',
                'type': 'fill',
                'source': 'VotingSubDivisions',
                'layout': {},
                'paint': {
                    'fill-color': [
                        'step',
                        ['get', candidates[candidate].column],
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
                    'fill-opacity': layerOpacity
                    }
                }, 'rail');
            } else if (candidate === "race") {
                map.addLayer({
                'id': 'VotingSubDivisionsFill',
                'type': 'fill',
                'source': 'VotingSubDivisions',
                'layout': {},
                'paint': {
                    'fill-color': [
                        'match',
                        ['get', 'contest'],
                        'Tory-Penalosa',
                        '#3d53fb',
                        'Tory-Brown',
                        '#c78bf4',
                        'Penalosa-Tory',
                        '#369a1b',
                        'Penalosa-Brown',
                        '#3bb2d0',
                        'Brown-Penalosa',
                        '#b94141',
                        /* other */ '#ccc'
                    ], 
                    'fill-opacity': layerOpacity
                    }
                }, 'rail');
            } else {
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
                    'fill-opacity': layerOpacity
                    }
                }, 'rail');
            }
            

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
            }, 'rail');

            map.addLayer({
                'id': 'WardsWhite',
                'type': 'line',
                'source': 'Wards',
                'layout': {},
                'paint': {
                    'line-color': '#fff',
                    'line-width': 4,
                    'line-opacity': 1
                }
            }, 'rail');

            map.addLayer({
                'id': 'WardsBlack',
                'type': 'line',
                'source': 'Wards',
                'layout': {},
                'paint': {
                    'line-color': '#000',
                    'line-width': 2,
                    'line-opacity': 1
                }
            }, 'rail');

            map.addLayer({
                'id': 'WardsLabel',
                'type': 'symbol',
                'source': 'WardPts',
                'layout': {
                    'text-field': ['get', 'name'],
                    'text-font': ['Roboto Medium', "Arial Unicode MS Regular"],
                    'text-size': 12,
                    'text-transform': "uppercase",
                    'text-justify': 'center',
                    'text-allow-overlap': true,
                },
                'paint': {
                    'text-halo-width': 1, 
                    'text-halo-color': '#fff',
                    'text-opacity': [
                        "interpolate",
                        ["linear"],
                        ["zoom"],
                        10.1,
                        0,
                        10.2,
                        1
                    ]
                }
            });
        });

        map.on('mousemove', 'VotingSubDivisionsFill', (e) => {
            if (candidate === "margin") {
                message = "Ward: " + e.features[0].properties.ward + " --- Poll: " + e.features[0].properties.vsd + " --- Margin: " + Math.round(100 * e.features[0].properties[candidates[candidate].column]) + "%"
            } else if (candidate === "race") {
                message = "Ward: " + e.features[0].properties.ward + " --- Poll: " + e.features[0].properties.vsd
            } else {
                message = "Ward: " + e.features[0].properties.ward + " --- Poll: " + e.features[0].properties.vsd + " --- Total Votes: " + e.features[0].properties.total + " --- Votes for " + candidates[candidate].name + ": " + e.features[0].properties[candidates[candidate].column] +  " --- % for " + candidates[candidate].name + ": " + Math.round(100 * e.features[0].properties[candidates[candidate].column] / e.features[0].properties.total) + "%"  
            }
                  
        });

        map.on('mouseleave', 'VotingSubDivisionsFill', () => {
            message = " "
        });

    });

</script>



<svelte:window bind:innerHeight={pageHeight} />

{#if candidate === "race"}
    <h3>Top-two finishers</h3>

    <div id="legend">
        <svg width="320" height="80">
            <rect class="box" width="30" height = "15" x="0" y="0" style="fill:#3d53fb; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <text class="legend-label" x="35" y="12">1) Tory 2) Peñalosa</text>   
            
            <rect class="box" width="30" height = "15" x="160" y="0" style="fill:#c78bf4; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <text class="legend-label" x="195" y="12">1) Tory 2) Brown</text>
            
            <rect class="box" width="30" height = "15" x="0" y="20" style="fill:#369a1b; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <text class="legend-label" x="35" y="32">1) Peñalosa 2) Tory</text>     
            
            <rect class="box" width="30" height = "15" x="160" y="20" style="fill:#3bb2d0; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <text class="legend-label" x="195" y="32">1) Peñalosa 2) Brown</text> 
            
            <rect class="box" width="30" height = "15" x="0" y="40" style="fill:#b94141; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <text class="legend-label" x="35" y="52">1) Brown 2) Peñalosa</text> 
        </svg>
    </div>

    <div id={candidate} class="map" style="height: {mapHeight}px"></div>

   <div id="message"><p>{message}</p></div>

{:else}
    <h3>% {candidates[candidate].name}</h3>

    <div id="legend">
        <svg width="225" height="50">
            <text class="legend-label" x="35" y="30">{candidates[candidate].breaks[0] * 100}%</text>
            <text class="legend-label" x="80" y="30">{candidates[candidate].breaks[1] * 100}%</text>
            <text class="legend-label" x="125" y="30">{candidates[candidate].breaks[2] * 100}%</text>
            <text class="legend-label" x="170" y="30">{candidates[candidate].breaks[3] * 100}%</text>
            <rect class="box" width="45" height = "15" x="0" y="0" style="fill:{candidates[candidate].colours[0]}; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <rect class="box" width="45" height = "15" x="45" y="0" style="fill:{candidates[candidate].colours[1]}; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <rect class="box" width="45" height = "15" x="90" y="0" style="fill:{candidates[candidate].colours[2]}; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <rect class="box" width="45" height = "15" x="135" y="0" style="fill:{candidates[candidate].colours[3]}; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
            <rect class="box" width="45" height = "15" x="180" y="0" style="fill:{candidates[candidate].colours[4]}; stroke: rgb(206, 206, 206);" opacity={layerOpacity}></rect>
        </svg>
    </div>

    <div id={candidate} class="map" style="height: {mapHeight}px"></div>

    <div id="message"><p>{message}</p></div>
{/if}



<style>
    
    h3 {
        font-family: "Source Serif Pro", serif;
		font-size: 18px;
        text-align: center;
    }

    .map {
		width: 100%;
        border-top: 1px solid grey;
        border-bottom: 1px solid grey;
	}

    #legend {
        text-align: center;
        margin: -10px;
    }

    .legend-label {
		font-size: 13px;
		fill: rgb(66, 66, 66);
	}

    #message {
        font-family: "Roboto", sans-serif;
        height: 20px;
        font-size: 13px;
        color: rgb(66, 66, 66);
        text-align: center;
    }

</style>
