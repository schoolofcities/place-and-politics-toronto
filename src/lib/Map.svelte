<script>
    import { onMount } from 'svelte';
    import mapboxgl from "mapbox-gl";

    mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nob29sb2ZjaXRpZXMiLCJhIjoiY2w4c3h6M2tuMDIwazNuczU3bXA3ZXpvaSJ9.ShjnM8qiYP6yqz2PcAUBOg';

    let map;

    onMount(() => {
        map = new mapboxgl.Map({
			container: 'map', 
			style: 'mapbox://styles/schoolofcities/cl9wy9gww000j15r7llrtlun3',
			center: [-79.37, 43.70],
			zoom: 10.5,
			maxZoom: 16,
			minZoom: 8,
			bearing: -17.7,
			projection: 'globe',
			scrollZoom: true,
			attributionControl: true
		});
        map.addControl(new mapboxgl.NavigationControl(), 'top-left');
    });

</script>


<div id="map"></div>


<style>

    #map {
		height: 600px;
		width: 100%;
        border-top: 1px solid grey;
        border-bottom: 1px solid grey;
        /* border: 1px solid; */
	}

</style>