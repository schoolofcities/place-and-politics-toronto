<script>
    import { onMount } from 'svelte';
    import mapboxgl from "mapbox-gl";

    mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nob29sb2ZjaXRpZXMiLCJhIjoiY2w4c3h6M2tuMDIwazNuczU3bXA3ZXpvaSJ9.ShjnM8qiYP6yqz2PcAUBOg';

    let map;

    onMount(() => {
        map = new mapboxgl.Map({
			container: 'map', 
			style: 'mapbox://styles/schoolofcities/cl8sy8euo002f14tbqhwrexda',
			center: [-79.22, 43.765], 
			zoom: 12,
			maxZoom: 13.5,
			minZoom: 8,
			bearing: -17.7,
			projection: 'globe',
			scrollZoom: true,
			attributionControl: false
		});
        map.addControl(new mapboxgl.NavigationControl(), 'top-left');
    });

</script>


<div id="map"></div>


<style>

    #map {
		height: 600px;
		width: 100%;
        /* border: 1px solid; */
	}

</style>