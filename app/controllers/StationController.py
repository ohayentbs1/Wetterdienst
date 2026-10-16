import math
import ssl
from datetime import date, datetime
from urllib.request import urlopen

import certifi
from flask import flash, redirect, render_template, request, session, url_for
from geopy.distance import geodesic

from app import db
from app.enums import AggregationPeriod, DisplayMode, WeatherField
from app.models import Station
from app.services.ChartService import ChartService
from app.services.TableService import TableService
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

        stations = []
        for line_number, line in enumerate(content.splitlines()[2:], start=3):
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
        flash(f'{len(stations)} Stationen importiert.')
        return redirect(url_for('main.index'))

    def show_weather_data(self):
        return self._render_page(request.args)

    def change_weather_data(self):
        return self._render_page(request.form)

    def _render_page(self, payload):
        selected_category = WeatherField.normalize(payload.get('weather_category')).value
        display_mode = DisplayMode.normalize(payload.get('display_mode') or session.get('selected_display_mode'))
        aggregation_period = AggregationPeriod.normalize(
            payload.get('aggregation_period') or session.get('selected_aggregation_period')
        )

        if payload.get('latitude') and payload.get('longitude'):
            session['latitude'] = float(payload['latitude'])
            session['longitude'] = float(payload['longitude'])
            session['start_date'] = payload['start_date']
            session['end_date'] = payload['end_date']

        latitude = session.get('latitude')
        longitude = session.get('longitude')
        start_date_raw = session.get('start_date')
        end_date_raw = session.get('end_date')

        if latitude is None or longitude is None or not start_date_raw or not end_date_raw:
            return render_template(
                'index.html',
                error='Bitte zuerst einen Ort und einen Zeitraum auswählen.',
                selected_weather_category=selected_category,
                selected_display_mode=display_mode.value,
                selected_aggregation_period=aggregation_period.value,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            start_date = self._parse_date_value(start_date_raw)
            end_date = self._parse_date_value(end_date_raw)
            if start_date > end_date:
                raise ValueError('Das Startdatum muss vor oder auf dem Enddatum liegen.')
        except ValueError as error:
            return render_template(
                'index.html',
                latitude=latitude,
                longitude=longitude,
                start_date=start_date_raw,
                end_date=end_date_raw,
                error=str(error) if str(error) else 'Bitte gib ein gültiges Start- und Enddatum an.',
                selected_weather_category=selected_category,
                selected_display_mode=display_mode.value,
                selected_aggregation_period=aggregation_period.value,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        try:
            nearby = self.get_nearby_stations(latitude, longitude)[: self.MAX_STATIONS]
        except ValueError:
            return render_template(
                'index.html',
                error='Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.',
                start_date=start_date_raw,
                end_date=end_date_raw,
                selected_weather_category=selected_category,
                selected_display_mode=display_mode.value,
                selected_aggregation_period=aggregation_period.value,
                chart_service_fields=ChartService.CHART_FIELDS,
            ), 400

        station_distances = {station.id: distance_km for station, distance_km in nearby}
        stations_for_display = [
            {'name': station.stationsname, 'distance_km': distance_km}
            for station, distance_km in nearby
        ]

        session['selected_weather_category'] = selected_category
        session['selected_display_mode'] = display_mode.value
        session['selected_aggregation_period'] = aggregation_period.value

        imported_count = WeatherDataImportService().import_for_stations([station for station, _ in nearby])
        chart_data = ChartService().get_chart_data(
            station_distances,
            start_date,
            end_date,
            selected_field=selected_category,
            aggregation_period=aggregation_period.value,
        )
        table_data = TableService().get_table_data(
            station_distances,
            start_date,
            end_date,
            selected_field=selected_category,
            aggregation_period=aggregation_period.value,
        )

        has_chart_data = any(value is not None for dataset in chart_data['datasets'] for value in dataset['data'])
        has_table_data = any(row['value'] is not None for row in table_data['rows'])

        return render_template(
            'index.html',
            latitude=latitude,
            longitude=longitude,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            stations=stations_for_display,
            import_message=f'{imported_count} neue Wetterdatensätze importiert.',
            chart_data=chart_data if has_chart_data else None,
            table_data=table_data if has_table_data else None,
            selected_weather_category=selected_category,
            selected_display_mode=display_mode.value,
            selected_aggregation_period=aggregation_period.value,
            chart_service_fields=ChartService.CHART_FIELDS,
        )

    @staticmethod
    def _parse_date_value(value: str) -> date:
        parsed = datetime.strptime(value, '%Y-%m-%d').date()
        if parsed.isoformat() != value:
            raise ValueError('Bitte gib ein gültiges Start- und Enddatum an.')
        return parsed

    def get_nearby_stations(self, latitude: float, longitude: float) -> list[tuple[Station, float]]:
        if (
            not math.isfinite(latitude)
            or not math.isfinite(longitude)
            or not -90 <= latitude <= 90
            or not -180 <= longitude <= 180
        ):
            raise ValueError('Ungültige Koordinaten.')

        nearby = []
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

            distance_km = geodesic((latitude, longitude), (station.geo_breite, station.geo_laenge)).km
            if distance_km <= self.SEARCH_RADIUS_KM:
                nearby.append((station, distance_km))

        nearby.sort(key=lambda entry: (entry[1], entry[0].stationsname))
        return nearby

    @staticmethod
    def _parse_date(value, line_number):
        try:
            return datetime.strptime(value, '%Y%m%d').date()
        except ValueError as error:
            raise ValueError(f'Ungültiges Datum in Stationsdatensatz, Zeile {line_number}.') from error
