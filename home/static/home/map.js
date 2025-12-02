console.log('map.js loaded - starting initialization');
console.log('MAPBOX_TOKEN available?', typeof MAPBOX_TOKEN !== 'undefined');
console.log('mapboxgl available?', typeof mapboxgl !== 'undefined');

if (typeof mapboxgl === 'undefined') {
    console.error('ERROR: mapboxgl library not loaded!');
}

if (typeof MAPBOX_TOKEN === 'undefined') {
    console.error('ERROR: MAPBOX_TOKEN not defined!');
}

let map;
try {
    mapboxgl.accessToken = MAPBOX_TOKEN;  // defined in template
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-78.4767, 38.0293],
        zoom: 13
    });
    console.log('Map object created successfully');
} catch (error) {
    console.error('ERROR creating map:', error);
    throw error;
}

// Load and display approved trees when map loads
map.on('load', async () => {
    console.log('Map loaded, fetching trees...');
    try {
        const response = await fetch('/api/trees/');
        console.log('Response status:', response.status);

        if (!response.ok) throw new Error('Failed to fetch trees');

        const data = await response.json();
        console.log('Received trees data:', data);
        console.log('Number of approved trees:', data.trees.length);

        // Add a marker for each approved tree
        data.trees.forEach(tree => {
            console.log(`Adding marker for ${tree.species} at [${tree.longitude}, ${tree.latitude}]`);
            const marker = new mapboxgl.Marker({ color: '#228B22' })
                .setLngLat([tree.longitude, tree.latitude])
                .setPopup(
                    new mapboxgl.Popup({ offset: 25 })
                        .setHTML(`
                            <h3>${tree.species}</h3>
                            <p>${tree.description || 'No description'}</p>
                        `)
                )
                .addTo(map);
        });
        console.log('All markers added successfully');
    } catch (error) {
        console.error('Error loading trees:', error);
    }
});

let addMode = false;
let tempMarker = null;

const addBtn = document.getElementById('add-tree-btn');
const sidebar = document.getElementById('sidebar');
const cancelBtn = document.getElementById('cancel-sidebar-btn');
const treeForm = document.getElementById('tree-form');

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

treeForm?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        latitude: parseFloat(treeForm.latitude.value),
        longitude: parseFloat(treeForm.longitude.value),
        species: treeForm.species.value,
        description: treeForm.description.value,
    };

    try {
        const response = await fetch('/api/trees/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error('Failed to submit tree');

        const result = await response.json();
        alert('🌳 Tree submitted successfully! It will appear on the map after moderator approval.');

        // Reset UI
        treeForm.reset();
        sidebar?.classList.remove('open');
        if (tempMarker) tempMarker.remove();
        addMode = false;
        if (addBtn) addBtn.textContent = 'Add Tree';
        map.getCanvas().style.cursor = '';

    } catch (error) {
        console.error(error);
        alert('Error submitting tree. Please try again.');
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}