from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.controllers.ImportController import ImportController
from app.controllers.StationController import StationController
from app.models import WetterEintrag

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # Beispielhaftes Auslesen der Einträge aus der Datenbank
    eintraege = WetterEintrag.query.order_by(WetterEintrag.zeitstempel.desc()).all()
    return render_template('index.html', eintraege=eintraege)


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
            eintraege=[],
            error='Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.',
        ), 400

    eintraege = WetterEintrag.query.order_by(WetterEintrag.zeitstempel.desc()).all()
    return render_template(
        'index.html',
        eintraege=eintraege,
        latitude=latitude,
        longitude=longitude,
        stations=stations,
    )