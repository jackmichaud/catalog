mapboxgl.accessToken = MAPBOX_TOKEN;  // defined in template
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v11',
    center: [-78.4767, 38.0293],
    zoom: 13
});

let addMode = false;
let tempMarker = null;

const addBtn = document.getElementById('add-tree-btn');
const sidebar = document.getElementById('sidebar');
const cancelBtn = document.getElementById('cancel-sidebar-btn');

addBtn?.addEventListener('click', () => {
    addMode = !addMode;

    if (addMode) {
        // entering add mode
        sidebar?.classList.add('open');
        map.getCanvas().style.cursor = 'crosshair';
        addBtn.textContent = 'Cancel';
    } else {
        // canceling add mode
        sidebar?.classList.remove('open');
        map.getCanvas().style.cursor = '';
        if (tempMarker) tempMarker.remove();
        addBtn.textContent = 'Add Tree';
    }
});

// Map click to place marker
map.on('click', (e) => {
    if (!addMode) return;

    if (tempMarker) tempMarker.remove();

    tempMarker = new mapboxgl.Marker({ color: 'green' })
        .setLngLat(e.lngLat)
        .addTo(map);

    const latInput = document.querySelector('#tree-form [name="latitude"]');
    const lngInput = document.querySelector('#tree-form [name="longitude"]');
    if (latInput && lngInput) {
        latInput.value = e.lngLat.lat.toFixed(6);
        lngInput.value = e.lngLat.lng.toFixed(6);
    }
});

cancelBtn?.addEventListener('click', () => {
    sidebar?.classList.remove('open');
    if (tempMarker) tempMarker.remove();
    map.getCanvas().style.cursor = '';
    addMode = false;
    if (addBtn) addBtn.textContent = 'Add Tree';
});

// Prevent form reload
document.getElementById('tree-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Form submitted! (hook up Django POST later)');
});