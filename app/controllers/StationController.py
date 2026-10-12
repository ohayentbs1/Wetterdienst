import math
import ssl
from datetime import date, datetime
from urllib.request import urlopen

import certifi
from flask import flash, redirect, render_template, request, session, url_for
from geopy.distance import geodesic

from app import db
from app.models import Station
from app.services.ChartService import ChartService
from app.services.WeatherDataImportService import WeatherDataImportService


class StationController:
    SEARCH_RADIUS_KM = 50
    MAX_STATIONS = 5
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
        selected_category = (
            request.args.get('weather_category')
            or session.get('selected_weather_category')
            or 'RSK'
        ).upper()
        return self._render_weather_data(selected_category)

    def change_weather_data(self):
        selected_category = (
            request.form.get('weather_category')
            or session.get('selected_weather_category')
            or 'RSK'
        ).upper()
        session['selected_weather_category'] = selected_category
        return self._render_category_only(selected_category)

    def _render_weather_data(self, selected_category: str):
        if request.args.get('latitude') and request.args.get('longitude'):
            session['latitude'] = float(request.args['latitude'])
            session['longitude'] = float(request.args['longitude'])
            session['start_date'] = request.args['start_date']
            session['end_date'] = request.args['end_date']

        latitude = session.get('latitude')
        longitude = session.get('longitude')
        start_date_raw = session.get('start_date')
        end_date_raw = session.get('end_date')

        if latitude is None or longitude is None or not start_date_raw or not end_date_raw:
            return render_template(
                'index.html',
                error='Bitte zuerst einen Ort und einen Zeitraum auswählen.',
                selected_weather_category=selected_category,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            start_date = self._parse_selected_date(start_date_raw)
            end_date = self._parse_selected_date(end_date_raw)
            if start_date > end_date:
                return render_template(
                    'index.html',
                    latitude=latitude,
                    longitude=longitude,
                    start_date=start_date_raw,
                    end_date=end_date_raw,
                    error='Das Startdatum muss vor oder auf dem Enddatum liegen.',
                    selected_weather_category=selected_category,
                    chart_service_fields=ChartService.CHART_FIELDS,
                ), 400
        except (TypeError, ValueError):
            return render_template(
                'index.html',
                latitude=latitude,
                longitude=longitude,
                start_date=start_date_raw,
                end_date=end_date_raw,
                error='Bitte gib ein gültiges Start- und Enddatum an.',
                selected_weather_category=selected_category,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        try:
            nearby_station_results = self.get_nearby_stations(latitude, longitude)
        except ValueError:
            return render_template(
                'index.html',
                error='Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.',
                start_date=start_date_raw,
                end_date=end_date_raw,
                selected_weather_category=selected_category,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        nearby_station_results = nearby_station_results[:self.MAX_STATIONS]
        station_objects = []
        stations_for_display = []
        station_distances = {}
        for station, distance_km in nearby_station_results:
            station_objects.append(station)
            station_distances[station.id] = distance_km
            stations_for_display.append({
                'name': station.stationsname,
                'distance_km': distance_km,
            })

        self._store_station_context(station_distances, stations_for_display)
        session['selected_weather_category'] = selected_category

        imported_count = WeatherDataImportService().import_for_stations(station_objects)
        chart_data = ChartService().get_chart_data(
            station_distances,
            start_date,
            end_date,
            selected_field=selected_category,
        )
        has_chart_data = any(
            value is not None
            for dataset in chart_data['datasets']
            for value in dataset['data']
        )
        return render_template(
            'index.html',
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            stations=stations_for_display,
            import_message=f'{imported_count} neue Wetterdatensätze importiert.',
            chart_data=chart_data if has_chart_data else None,
            selected_weather_category=selected_category,
            chart_service_fields=ChartService.CHART_FIELDS,
        )

    def _render_category_only(self, selected_category: str):
        latitude = session.get('latitude')
        longitude = session.get('longitude')
        start_date_raw = session.get('start_date')
        end_date_raw = session.get('end_date')

        if latitude is None or longitude is None or not start_date_raw or not end_date_raw:
            return render_template(
                'index.html',
                error='Bitte zuerst einen Ort und einen Zeitraum auswählen.',
                selected_weather_category=selected_category,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            start_date = self._parse_selected_date(start_date_raw)
            end_date = self._parse_selected_date(end_date_raw)
            if start_date > end_date:
                return render_template(
                    'index.html',
                    latitude=latitude,
                    longitude=longitude,
                    start_date=start_date_raw,
                    end_date=end_date_raw,
                    error='Das Startdatum muss vor oder auf dem Enddatum liegen.',
                    selected_weather_category=selected_category,
                    chart_service_fields=ChartService.CHART_FIELDS,
                ), 400
        except (TypeError, ValueError):
            return render_template(
                'index.html',
                latitude=latitude,
                longitude=longitude,
                start_date=start_date_raw,
                end_date=end_date_raw,
                error='Bitte gib ein gültiges Start- und Enddatum an.',
                selected_weather_category=selected_category,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        station_distances = self._get_stored_station_distances()
        stations_for_display = session.get('stations_for_display') or []

        if not station_distances:
            try:
                nearby_station_results = self.get_nearby_stations(latitude, longitude)
            except ValueError:
                return render_template(
                    'index.html',
                    error='Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.',
                    start_date=start_date_raw,
                    end_date=end_date_raw,
                    selected_weather_category=selected_category,
                    chart_service_fields=ChartService.CHART_FIELDS,
                ), 400

            nearby_station_results = nearby_station_results[:self.MAX_STATIONS]
            station_distances = {
                station.id: distance_km
                for station, distance_km in nearby_station_results
            }
            stations_for_display = [
                {
                    'name': station.stationsname,
                    'distance_km': distance_km,
                }
                for station, distance_km in nearby_station_results
            ]
            self._store_station_context(station_distances, stations_for_display)

        chart_data = ChartService().get_chart_data(
            station_distances,
            start_date,
            end_date,
            selected_field=selected_category,
        )
        has_chart_data = any(
            value is not None
            for dataset in chart_data['datasets']
            for value in dataset['data']
        )
        return render_template(
            'index.html',
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            stations=stations_for_display,
            chart_data=chart_data if has_chart_data else None,
            selected_weather_category=selected_category,
            chart_service_fields=ChartService.CHART_FIELDS,
        )

    @staticmethod
    def _store_station_context(station_distances: dict[int, float], stations_for_display: list[dict]):
        session['station_distances'] = {
            str(station_id): float(distance_km)
            for station_id, distance_km in station_distances.items()
        }
        session['stations_for_display'] = stations_for_display

    @staticmethod
    def _get_stored_station_distances() -> dict[int, float]:
        stored = session.get('station_distances', {})
        if not isinstance(stored, dict):
            return {}
        try:
            return {
                int(station_id): float(distance_km)
                for station_id, distance_km in stored.items()
            }
        except (TypeError, ValueError):
            return {}

    @staticmethod
    def _parse_selected_date(value: str) -> date:
        parsed_date = datetime.strptime(value, '%Y-%m-%d').date()
        if parsed_date.isoformat() != value:
            raise ValueError('Ungültiges Datumsformat.')
        return parsed_date

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
