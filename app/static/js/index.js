const mapElement = document.getElementById('map');
const map = L.map(mapElement).setView([51.1657, 10.4515], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const showCoordinatesButton = document.getElementById('show-weather-data');
const latitudeInput = document.getElementById('latitude');
const longitudeInput = document.getElementById('longitude');
let selectionMarker = null;

if (mapElement.dataset.selectedLatitude && mapElement.dataset.selectedLongitude) {
    const selectedLocation = [
        Number(mapElement.dataset.selectedLatitude),
        Number(mapElement.dataset.selectedLongitude)
    ];
    selectionMarker = L.marker(selectedLocation).addTo(map);
    map.setView(selectedLocation, 10);
}

map.on('click', (event) => {
    const selectedLocation = event.latlng;
    if (selectionMarker) {
        selectionMarker.setLatLng(selectedLocation);
    } else {
        selectionMarker = L.marker(selectedLocation).addTo(map);
    }

    latitudeInput.value = selectedLocation.lat;
    longitudeInput.value = selectedLocation.lng;
    showCoordinatesButton.disabled = false;
});
