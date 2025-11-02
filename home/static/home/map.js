mapboxgl.accessToken = MAPBOX_TOKEN;  // defined in template
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-78.4767, 38.0293],
    zoom: 13
});

// Example marker
new mapboxgl.Marker({ color: 'green' })
    .setLngLat([-78.4767, 38.0293])
    .setPopup(new mapboxgl.Popup().setHTML("<h3>Example Tree</h3><p>Oak, 25 years old</p>"))
    .addTo(map);