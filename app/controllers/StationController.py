import math
import ssl
from datetime import datetime
from urllib.request import urlopen

import certifi
from flask import flash, redirect, render_template, request, url_for
from geopy.distance import geodesic

from app import db
from app.models import Station
from app.services.WeatherDataImportService import WeatherDataImportService


class StationController:
    SEARCH_RADIUS_KM = 50
    STATION_FILE_URL = (
        'https://opendata.dwd.de/climate_environment/CDC/observations_germany/'
        'climate/daily/kl/historical/KL_Tageswerte_Beschreibung_Stationen.txt'
    )

    def import_stations(self):
        context = ssl.create_default_context(cafile=certifi.where())

        with urlopen(self.STATION_FILE_URL, timeout=30, context=context) as response:
            content = response.read().decode('latin-1')

        lines = content.splitlines()
        stations = []
        for line_number, line in enumerate(lines[2:], start=3):
            if not line.strip():
                continue
            if len(line) < 149:
                raise ValueError(f'Ungültiger Stationsdatensatz in Zeile {line_number}.')

            stations.append(
                Station(
                    id=int(line[0:5]),
                    von_datum=self._parse_date(line[6:14], line_number),
                    bis_datum=self._parse_date(line[15:23], line_number),
                    stationshoehe=int(line[24:38].strip()),
                    geo_breite=float(line[43:50].strip()),
                    geo_laenge=float(line[50:61].strip()),
                    stationsname=line[61:102].strip(),
                    bundesland=line[102:143].strip(),
                    abgabe=line[143:149].strip() or None,
                )
            )

        if not stations:
            raise ValueError('Die Stationsdatei enthält keine Stationsdatensätze.')

        db.session.query(Station).delete()
        db.session.add_all(stations)
        db.session.commit()
        flash(f'{len(stations)} Stationen wurden importiert.')
        return redirect(url_for('main.index'))

    def show_weather_data(self):
        try:
            latitude = float(request.args['latitude'])
            longitude = float(request.args['longitude'])
            nearby_station_results = self.get_nearby_stations(
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

    def get_nearby_stations(
        self,
        latitude: float,
        longitude: float,
    ) -> list[tuple[Station, float]]:
        if (
            not math.isfinite(latitude)
            or not math.isfinite(longitude)
            or not -90 <= latitude <= 90
            or not -180 <= longitude <= 180
        ):
            raise ValueError('Ungültige Koordinaten.')

        nearby: list[tuple[float, Station]] = []
        stations = Station.query.filter(
            Station.geo_breite.isnot(None),
            Station.geo_laenge.isnot(None),
            Station.stationsname.isnot(None),
        ).all()

        for station in stations:
            if (
                not math.isfinite(station.geo_breite)
                or not math.isfinite(station.geo_laenge)
                or not -90 <= station.geo_breite <= 90
                or not -180 <= station.geo_laenge <= 180
            ):
                continue

            distance_km = geodesic(
                (latitude, longitude),
                (station.geo_breite, station.geo_laenge),
            ).km
            if distance_km <= self.SEARCH_RADIUS_KM:
                nearby.append((distance_km, station))

        nearby.sort(key=lambda entry: (entry[0], entry[1].stationsname))
        return [(station, distance_km) for distance_km, station in nearby]

    @staticmethod
    def _parse_date(value, line_number):
        try:
            return datetime.strptime(value, '%Y%m%d').date()
        except ValueError as error:
            raise ValueError(
                f'Ungültiges Datum in Stationsdatensatz, Zeile {line_number}.'
            ) from error
