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
let allMarkers = []; // Store all markers for filtering
let allTrees = []; // Store all tree data

try {
    mapboxgl.accessToken = MAPBOX_TOKEN;  // defined in template

    // Check if dark mode is active
    const currentTheme = document.documentElement.getAttribute('data-theme') || localStorage.getItem('theme') || 'light';
    const mapStyle = currentTheme === 'dark' ? 'mapbox://styles/mapbox/dark-v11' : 'mapbox://styles/mapbox/light-v11';

    map = new mapboxgl.Map({
        container: 'map',
        style: mapStyle,
        center: [-78.4767, 38.0293],
        zoom: 13
    });
    console.log('Map object created successfully with theme:', currentTheme);
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

        allTrees = data.trees; // Store all trees for filtering

        // Get unique species for filter dropdown
        const uniqueSpecies = [...new Set(data.trees.map(tree => tree.species))].sort();
        populateSpeciesFilter(uniqueSpecies);

        // Add a marker for each approved tree
        data.trees.forEach(tree => {
            console.log(`Adding marker for ${tree.species} at [${tree.longitude}, ${tree.latitude}]`);

            // Build popup content
            let popupContent = `
                <div class="tree-popup">
                    <h3>${tree.species}</h3>
                    <p>(${tree.latitude ?? 'No latitude'}, ${tree.longitude ?? 'No longitude'})</p>
                    <p>${tree.height ? 'Height: ' + tree.height + ' ft' : 'No height'}</p>
                    <p>${tree.diameter ? 'Diameter: ' + tree.diameter + ' in' : 'No diameter'}</p>
            `;

            // Image block
            if (tree.image) {
                popupContent += `
                    <div class="csp-popup-margin">
                        <img src="${tree.image}"
                            alt="${tree.species}"
                            class="csp-popup-img" />
                    </div>
                `;
            } else {
                popupContent += `<p>No image</p>`;
            }

            popupContent += `
                    <p>${tree.description || 'No description'}</p>
                    <p class="csp-popup-meta">Submitted by: ${tree.submitted_by}</p>
            `;

            // Add moderator controls if user is a moderator
            if (IS_MODERATOR) {
                popupContent += `
                    <div class="moderator-controls">
                        <button class="edit-tree-btn" data-tree-id="${tree.id}">Edit</button>
                        <button class="delete-tree-btn" data-tree-id="${tree.id}">Delete</button>
                    </div>
                `;
            } else if (IS_AUTHENTICATED && tree.submitted_by !== CURRENT_USER) {
                // Regular users can flag trees (but not their own)
                popupContent += `
                    <div class="user-controls">
                        <button class="flag-tree-btn csp-flag-btn" data-tree-id="${tree.id}">
                            🚩 Flag for Review
                        </button>
                    </div>
                `;
            }

            popupContent += `</div>`;

            const popup = new mapboxgl.Popup({ offset: 25 })
                .setHTML(popupContent);

            const marker = new mapboxgl.Marker({ color: '#228B22' })
                .setLngLat([tree.longitude, tree.latitude])
                .setPopup(popup)
                .addTo(map);

            // Store marker with species info for filtering
            allMarkers.push({
                marker: marker,
                species: tree.species
            });

            // Fix Mapbox accessibility issue: remove aria-hidden from close button
            popup.on('open', () => {
                const closeBtn = popup.getElement().querySelector('.mapboxgl-popup-close-button');
                if (closeBtn) {
                    closeBtn.removeAttribute('aria-hidden');
                }
            });
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
        map.getCanvas().classList.add('csp-map-crosshair');
        addBtn.textContent = 'Cancel';
    } else {
        // canceling add mode
        sidebar?.classList.remove('open');
        map.getCanvas().classList.remove('csp-map-crosshair');
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
    map.getCanvas().classList.remove('csp-map-crosshair');
    addMode = false;
    if (addBtn) addBtn.textContent = 'Add Tree';
});

treeForm?.addEventListener('submit', async (e) => {
    // // e.preventDefault();

    // alert('🌳 Tree submitted successfully! It will appear on the map immediately.');

    // // Reset UI
    // treeForm.reset();
    // sidebar?.classList.remove('open');
    // if (tempMarker) tempMarker.remove();
    // addMode = false;
    // if (addBtn) addBtn.textContent = 'Add Tree';
    // map.getCanvas().style.cursor = '';
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

// Event delegation for edit/delete buttons in popups
document.addEventListener('click', async function (e) {
    // Handle edit button
    if (e.target.classList.contains('edit-tree-btn')) {
        const treeId = e.target.dataset.treeId;
        const popup = e.target.closest('.tree-popup');
        const currentSpecies = popup.querySelector('h3').textContent;
        const currentDesc = popup.querySelector('p').textContent;

        const newSpecies = prompt('Edit species:', currentSpecies);
        if (newSpecies === null) return; // User cancelled

        const newDesc = prompt('Edit description:', currentDesc === 'No description' ? '' : currentDesc);
        if (newDesc === null) return; // User cancelled

        try {
            const response = await fetch(`/api/trees/${treeId}/edit/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    species: newSpecies,
                    description: newDesc
                }),
            });

            if (!response.ok) throw new Error('Failed to edit tree');

            alert('Tree updated successfully! Refreshing page...');
            location.reload();
        } catch (error) {
            console.error(error);
            alert('Error updating tree. Please try again.');
        }
    }

    // Handle delete button
    if (e.target.classList.contains('delete-tree-btn')) {
        const treeId = e.target.dataset.treeId;

        if (!confirm('Are you sure you want to delete this tree? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/trees/${treeId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            });

            if (!response.ok) throw new Error('Failed to delete tree');

            alert('Tree deleted successfully! Refreshing page...');
            location.reload();
        } catch (error) {
            console.error(error);
            alert('Error deleting tree. Please try again.');
        }
    }

    // Handle flag button
    if (e.target.classList.contains('flag-tree-btn')) {
        const treeId = e.target.dataset.treeId;

        const reason = prompt('Please provide a reason for flagging this tree (optional):');
        if (reason === null) return; // User cancelled

        try {
            const response = await fetch(`/api/trees/${treeId}/flag/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    reason: reason || 'No reason provided'
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                alert(result.error || 'Failed to flag tree');
                return;
            }

            alert('Tree flagged for moderator review successfully!');
            location.reload();
        } catch (error) {
            console.error(error);
            alert('Error flagging tree. Please try again.');
        }
    }
});

// Filter functionality
function populateSpeciesFilter(species) {
    const speciesList = document.getElementById('species-list');
    if (!speciesList) return;

    speciesList.innerHTML = '';

    species.forEach(sp => {
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.dataset.species = sp;
        option.textContent = sp;

        speciesList.appendChild(option);
    });
}

function filterBySpecies(selectedSpecies) {
    allMarkers.forEach(item => {
        if (selectedSpecies === 'all') {
            // Show all markers
            item.marker.getElement().style.display = 'block';
        } else {
            // Show only markers matching the selected species
            if (item.species === selectedSpecies) {
                item.marker.getElement().style.display = 'block';
            } else {
                item.marker.getElement().style.display = 'none';
            }
        }
    });
}

// Initialize filter button after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const filterBtn = document.getElementById('filter-btn');
    const filterDropdown = document.getElementById('filter-dropdown');

    console.log('Filter button:', filterBtn);
    console.log('Filter dropdown:', filterDropdown);

    if (filterBtn && filterDropdown) {
        filterBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            console.log('Filter button clicked');

            // Toggle show class
            filterDropdown.classList.toggle('show');
            console.log('Dropdown toggled, has show class:', filterDropdown.classList.contains('show'));
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!filterDropdown.contains(e.target) && !filterBtn.contains(e.target)) {
                filterDropdown.classList.remove('show');
            }
        });

        // Handle filter option clicks
        filterDropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.filter-option');
            if (!option) return;

            console.log('Selected species:', option.dataset.species);

            // Remove active class from all options
            filterDropdown.querySelectorAll('.filter-option').forEach(opt => {
                opt.classList.remove('active');
            });

            // Add active class to clicked option
            option.classList.add('active');

            // Filter markers
            const selectedSpecies = option.dataset.species;
            filterBySpecies(selectedSpecies);

            // Close dropdown
            filterDropdown.classList.remove('show');
        });
    } else {
        console.error('Filter button or dropdown not found!');
    }
});