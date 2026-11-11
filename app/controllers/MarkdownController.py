from io import BytesIO

from flask import flash, redirect, request, send_file, session, url_for

from app.enums import AggregationPeriod, WeatherField
from app.services.TableService import TableService


class MarkdownController:
    def export(self):
        payload = request.form or request.args
        selected_category = WeatherField.normalize(
            payload.get('weather_category') or session.get('selected_weather_category')
        ).value
        aggregation_period = AggregationPeriod.normalize(
            payload.get('aggregation_period') or session.get('selected_aggregation_period')
        )

        latitude = payload.get('latitude') or session.get('latitude')
        longitude = payload.get('longitude') or session.get('longitude')
        start_date_raw = payload.get('start_date') or session.get('start_date')
        end_date_raw = payload.get('end_date') or session.get('end_date')

        if latitude is None or longitude is None or not start_date_raw or not end_date_raw:
            flash('Für den Markdown-Export fehlen Standort- oder Datumsdaten.')
            return redirect(url_for('main.index'))

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            start_date = self._parse_date_value(start_date_raw)
            end_date = self._parse_date_value(end_date_raw)
            if start_date > end_date:
                raise ValueError('Das Startdatum muss vor oder auf dem Enddatum liegen.')
        except ValueError as error:
            flash(str(error) if str(error) else 'Bitte gib ein gültiges Start- und Enddatum an.')
            return redirect(url_for('main.index'))

        try:
            from app.controllers.StationController import StationController
            nearby = StationController().get_nearby_stations(latitude, longitude)
        except ValueError:
            flash('Ungültige Koordinaten. Bitte wähle einen Ort auf der Karte aus.')
            return redirect(url_for('main.index'))

        station_distances = {station.id: distance_km for station, distance_km in nearby}
        table_data = TableService().get_table_data(
            station_distances,
            start_date,
            end_date,
            selected_field=selected_category,
            aggregation_period=aggregation_period.value,
        )

        if not table_data['rows'] or all(row['value'] is None for row in table_data['rows']):
            flash('Für den ausgewählten Zeitraum liegen keine Wetterdaten für den Markdown-Export vor.')
            return redirect(url_for('main.index'))

        aggregation_label = {
            'day': 'Täglich',
            'month': 'Monatlich',
            'year': 'Jährlich',
        }.get(aggregation_period.value, aggregation_period.value)
        value_header = f'{table_data["label"]} ({table_data["unit"]})'
        markdown_lines = [
            '# Wetterdaten Export',
            '',
            f'Ort: {latitude:.5f}, {longitude:.5f} | Zeitraum: {start_date.isoformat()} bis {end_date.isoformat()}',
            f'Aggregation: {aggregation_label} | Kennzahl: {value_header}',
            '',
            '| Datum | ' + self._escape_table_cell(value_header) + ' |',
            '| --- | ---: |',
        ]
        for row in table_data['rows']:
            value_text = '-' if row['value'] is None else f"{row['value']:.2f}".replace('.', ',')
            markdown_lines.append(
                f'| {self._escape_table_cell(str(row["date"]))} | {self._escape_table_cell(value_text)} |'
            )

        markdown_buffer = BytesIO('\n'.join(markdown_lines).encode('utf-8'))
        filename = f'wetterdaten_{start_date.isoformat()}_bis_{end_date.isoformat()}.md'
        return send_file(
            markdown_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/markdown',
        )

    @staticmethod
    def _escape_table_cell(value: str) -> str:
        return value.replace('\\', '\\\\').replace('|', '\\|').replace('\n', ' ')

    @staticmethod
    def _parse_date_value(value: str):
        from datetime import datetime
        parsed = datetime.strptime(value, '%Y-%m-%d').date()
        if parsed.isoformat() != value:
            raise ValueError('Bitte gib ein gültiges Start- und Enddatum an.')
        return parsed
