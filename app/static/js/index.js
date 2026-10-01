const map = L.map('map').setView([51.1657, 10.4515], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const showCoordinatesButton = document.getElementById('show-weather-data');
const coordinatesOutput = document.getElementById('coordinates');
let selectedLocation = null;
let selectionMarker = null;

map.on('click', (event) => {
    selectedLocation = event.latlng;

    if (selectionMarker) {
        selectionMarker.setLatLng(selectedLocation);
    } else {
        selectionMarker = L.marker(selectedLocation).addTo(map);
    }

    showCoordinatesButton.disabled = false;
    coordinatesOutput.hidden = true;
});

showCoordinatesButton.addEventListener('click', () => {
    if (!selectedLocation) {
        return;
    }

    coordinatesOutput.textContent =
        `Ausgewählter Ort: ${selectedLocation.lat.toFixed(6)}, ${selectedLocation.lng.toFixed(6)}`;
    coordinatesOutput.hidden = false;
});
