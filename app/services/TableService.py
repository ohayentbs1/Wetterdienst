from datetime import date

from app.services.WeatherAggregationService import WeatherAggregationService


class TableService:
    CHART_FIELDS = {
        'FX': ('Maximale Windspitze', 'm/s'),
        'FM': ('Mittlere Windgeschwindigkeit', 'm/s'),
        'RSK': ('Niederschlag', 'mm'),
        'SDK': ('Sonnenscheindauer', 'h'),
        'SHK_TAG': ('Schneehöhe', 'cm'),
        'NM': ('Bewölkung', 'Achtel'),
        'VPM': ('Dampfdruck', 'hPa'),
        'PM': ('Luftdruck', 'hPa'),
        'TMK': ('Mittlere Lufttemperatur', '°C'),
        'UPM': ('Relative Luftfeuchte', '%'),
        'TXK': ('Maximale Lufttemperatur', '°C'),
        'TNK': ('Minimale Lufttemperatur', '°C'),
        'TGK': ('Minimum der Lufttemperatur in 5 cm Höhe', '°C'),
    }

    def get_table_data(
        self,
        station_distances: dict[int, float],
        start_date: date,
        end_date: date,
        selected_field: str | None = None,
        aggregation_period: str = 'day',
    ) -> dict:
        selected_field = (selected_field or 'RSK').upper()
        if selected_field not in self.CHART_FIELDS:
            selected_field = 'RSK'

        aggregation_service = WeatherAggregationService()
        aggregated = aggregation_service.get_aggregated_data(
            station_distances,
            start_date,
            end_date,
            selected_field,
            aggregation_period=aggregation_period,
        )

        rows = [
            {'date': label, 'value': value}
            for label, value in zip(aggregated['labels'], aggregated['values'])
        ]
        label, unit = self.CHART_FIELDS[selected_field]
        return {
            'selected_field': selected_field,
            'label': label,
            'unit': unit,
            'aggregation_period': aggregated['aggregation_period'],
            'rows': rows,
        }
