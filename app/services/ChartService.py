from datetime import date

from app.enums import WeatherField
from app.services.WeatherAggregationService import WeatherAggregationService


class ChartService:
    CHART_FIELDS = {field.value: (field.label, field.unit) for field in WeatherField}

    def get_chart_data(
        self,
        station_distances: dict[int, float],
        start_date: date,
        end_date: date,
        selected_field: str | None = None,
        aggregation_period: str = 'day',
    ) -> dict:
        field = WeatherField.normalize(selected_field)
        aggregated = WeatherAggregationService().get_aggregated_data(
            station_distances,
            start_date,
            end_date,
            field.value,
            aggregation_period=aggregation_period,
        )
        label, unit = self.CHART_FIELDS[field.value]
        return {
            'labels': aggregated['labels'],
            'datasets': [{
                'label': f'{label} ({unit})',
                'data': aggregated['values'],
            }],
            'selected_field': field.value,
            'aggregation_period': aggregated['aggregation_period'],
        }
