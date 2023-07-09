<script>
    
    import { onMount } from 'svelte';
    import mapboxgl from "mapbox-gl";
    
    import VotingSubDivisions from '../data/vsd2023.geo.json';
    import Wards from '../data/wards.geo.json';
    import WardPts from '../data/wardsPts.geo.json';
    
    mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nob29sb2ZjaXRpZXMiLCJhIjoiY2xhMW5veXN2MDkxbDN2bW9iMWZ5NWI1dCJ9.AXhfsV6jCCoG-pJNLRvK2w';

    export let candidate;
    
    let pageHeight;
    let pageWidth;

    let mapHeight = 600;
    $: if (pageHeight < 800) {
        mapHeight = pageHeight - 200;
    } else {
        mapHeight = 600
    }

    const candidates = {
        "chow": {
            "name": "Olivia Chow",
            "column": "chow_olivia",
            "breaks": [0.2, 0.3, 0.4, 0.5],
            "colours": ["#fdf0ff", "#e0b7e7", "#c27dcf", "#a13cb5", "#83009c"]
        }, 
        "bailao": {
            "name": "Ana Bailão",
            "column": "bailao_ana",
            "breaks": [0.2, 0.3, 0.4, 0.5],
            "colours": ["#fbffe0", "#e8f1a9", "#c5de75", "#94b956", "#68983b"]
        },
        "saunders": {
            "name": "Mark Saunders",
            "column": "saunders_mark",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#f0f1f6", "#bec2d4", "#888faf", "#515d8b", "#1f2e69"]
        },
        "furey": {
            "name": "Anthony Furey",
            "column": "furey_anthony",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#f8ffff", "#a7e3e7", "#62ccd3", "#0dafbb", "#117c83"]
        },
        "matlow": {
            "name": "Josh Matlow",
            "column": "matlow_josh",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#f8ffff", "#b8f2df", "#80e7c2", "#40daa1", "#00a182"]
        },
        "hunter": {
            "name": "Mitzie Hunter",
            "column": "hunter_mitzie",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#f8feff", "#a5d6ed", "#4facdb", "#0085ca", "#00689f"]
        },
        "brown": {
            "name": "Chloe Brown",
            "column": "brown_chloe",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#fddede", "#f0b7b6", "#e1908e", "#ce6967", "#b94141"]
        },
        "bradford": {
            "name": "Brad Bradford",
            "column": "bradford_brad",
            "breaks": [0.05, 0.1, 0.15, 0.2],
            "colours": ["#f8feff", "#b8d2dd", "#7caabd", "#3e809c", "#00567b"]
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
			zoom: 9.5,
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
            
            map.addLayer({
                'id': 'VotingSubDivisionsFill',
                'type': 'fill',
                'source': 'VotingSubDivisions',
                'layout': {},
                'paint': {
                    'fill-color':  [
                        'case',
                        ['>=', ['/', ['get', candidates[candidate].column], ['get', 'total']], -1],
                        [
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
                        "#fff"
                ], 
                    'fill-opacity': layerOpacity
                    }
                }, 'rail');

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

            if (pageHeight > 700 && pageWidth > 800) {
                map.zoomTo(10.5)
            }
        });

        map.on('mousemove', 'VotingSubDivisionsFill', (e) => {
            
            message = "Ward: " + e.features[0].properties.ward + " --- Poll: " + e.features[0].properties.vsd + " --- Total Votes: " + e.features[0].properties.total + " --- Votes for " + candidates[candidate].name + ": " + e.features[0].properties[candidates[candidate].column] +  " --- % for " + candidates[candidate].name + ": " + Math.round(100 * e.features[0].properties[candidates[candidate].column] / e.features[0].properties.total) + "%"  
                  
        });

        map.on('mouseleave', 'VotingSubDivisionsFill', () => {
            message = " "
        });

    });

</script>



<svelte:window bind:innerHeight={pageHeight} bind:innerWidth={pageWidth}/>

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
