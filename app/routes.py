from flask import Blueprint, render_template
from app.controllers.StationController import StationController

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/stations/import', methods=['POST'])
def import_stations():
    return StationController().import_stations()


@main.route('/weather-data')
def show_weather_data():
    return StationController().show_weather_data()


@main.route('/change-weather-data', methods=['POST'])
def change_weather_data():
    return StationController().change_weather_data()
