from datetime import date

from app import db
from app.models import WeatherData
from app.services.WeatherAggregationService import WeatherAggregationService


class ChartService:
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

    def get_chart_data(
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

        datasets = [{
            'label': f'{self.CHART_FIELDS[selected_field][0]} ({self.CHART_FIELDS[selected_field][1]})',
            'data': aggregated['values'],
        }]
        return {
            'labels': aggregated['labels'],
            'datasets': datasets,
            'selected_field': selected_field,
            'aggregation_period': aggregated['aggregation_period'],
        }
