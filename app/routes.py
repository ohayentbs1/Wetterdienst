from flask import Blueprint, request

from app.controllers.StationController import StationController

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'import_stations':
            return StationController().import_stations()
        if action == 'load_weather_data':
            return StationController().show_weather_data(request.form)
        return StationController().change_weather_data(request.form)

    return StationController().show_weather_data(request.args)
