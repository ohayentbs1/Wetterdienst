from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.controllers.ImportController import ImportController
from app.controllers.StationController import StationController
from app.services.WeatherDataImportService import WeatherDataImportService

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/stations/import', methods=['POST'])
def import_stations():
    imported_count = ImportController().import_stations()
    flash(f'{imported_count} Stationen wurden importiert.')
    return redirect(url_for('main.index'))


@main.route('/stations/nearby')
def nearby_stations():
    try:
        latitude = float(request.args['latitude'])
        longitude = float(request.args['longitude'])
        nearby_station_results = StationController().get_nearby_stations(
            latitude,
            longitude,
        )
    except (KeyError, ValueError):
        return render_template(
            'index.html',
            error='Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.',
        ), 400

    station_objects = []
    stations_for_display = []
    for station, distance_km in nearby_station_results:
        station_objects.append(station)
        stations_for_display.append({
            'name': station.stationsname,
            'distance_km': distance_km,
        })

    imported_count = WeatherDataImportService().import_for_stations(
        station_objects
    )
    return render_template(
        'index.html',
        latitude=latitude,
        longitude=longitude,
        stations=stations_for_display,
        import_message=f'{imported_count} neue Wetterdatensätze importiert.',
    )