from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.controllers.ImportController import ImportController
from app.controllers.StationController import StationController
from app.controllers.WeatherDataController import WeatherDataController

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
        stations = StationController().get_nearby_stations(latitude, longitude)
    except (KeyError, ValueError):
        return render_template(
            'index.html',
            error='Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.',
        ), 400

    imported_count = WeatherDataController().import_for_stations(stations)
    return render_template(
        'index.html',
        latitude=latitude,
        longitude=longitude,
        stations=stations,
        import_message=f'{imported_count} neue Wetterdatensätze importiert.',
    )