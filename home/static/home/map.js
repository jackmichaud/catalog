mapboxgl.accessToken = MAPBOX_TOKEN;  // defined in template
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v11',
    center: [-78.4767, 38.0293],
    zoom: 13
});

let addMode = false;
let tempMarker = null;

document.getElementById('add-tree-btn').addEventListener('click', () => {
    addMode = !addMode;
    map.getCanvas().style.cursor = addMode ? 'crosshair' : '';
});

map.on('click', (e) => {
    if (!addMode) return;
    if (tempMarker) tempMarker.remove();

    tempMarker = new mapboxgl.Marker({ color: 'green' })
        .setLngLat(e.lngLat)
        .addTo(map);

    // Populate sidebar form
    document.querySelector('#tree-form [name="latitude"]').value = e.lngLat.lat;
    document.querySelector('#tree-form [name="longitude"]').value = e.lngLat.lng;
    document.getElementById('sidebar').classList.add('open');
});