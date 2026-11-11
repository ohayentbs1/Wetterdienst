from flask import Blueprint, redirect, request, session, url_for

from app.controllers.MarkdownController import MarkdownController
from app.controllers.PdfController import PdfController
from app.controllers.StationController import StationController

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        payload = request.form.to_dict()

        if payload.get('weather_category'):
            session['selected_weather_category'] = payload['weather_category']
        if payload.get('display_mode'):
            session['selected_display_mode'] = payload['display_mode']
        if payload.get('aggregation_period'):
            session['selected_aggregation_period'] = payload['aggregation_period']

        if payload.get('latitude') and payload.get('longitude'):
            session['latitude'] = float(payload['latitude'])
            session['longitude'] = float(payload['longitude'])
            if payload.get('start_date'):
                session['start_date'] = payload['start_date']
            if payload.get('end_date'):
                session['end_date'] = payload['end_date']

        if action == 'import_stations':
            return StationController().import_stations()
        if action == 'load_weather_data':
            return redirect(url_for('main.index'))
        if action == 'export_table_pdf':
            return PdfController().export_table_pdf()
        if action == 'export_table_markdown':
            return MarkdownController().export()
        return redirect(url_for('main.index'))

    return StationController().show_weather_data(request.args)
