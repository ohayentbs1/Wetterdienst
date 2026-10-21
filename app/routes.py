from flask import Blueprint, redirect, request, url_for

from app.controllers.PdfController import PdfController
from app.controllers.StationController import StationController

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'import_stations':
            return StationController().import_stations()
        if action == 'load_weather_data':
            StationController().show_weather_data(request.form)
            return redirect(url_for('main.index'))
        if action == 'export_table_pdf':
            return PdfController().export_table_pdf()
        StationController().change_weather_data(request.form)
        return redirect(url_for('main.index'))

    return StationController().show_weather_data(request.args)
