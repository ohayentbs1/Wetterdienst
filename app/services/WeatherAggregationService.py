from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from app import db
from app.models import WeatherData


class WeatherAggregationService:
    VALID_PERIODS = {'day', 'month', 'year'}

    def get_aggregated_data(
        self,
        station_distances: dict[int, float],
        start_date: date,
        end_date: date,
        selected_field: str,
        aggregation_period: str = 'day',
    ) -> dict:
        normalized_period = self._normalize_aggregation_period(aggregation_period)
        selected_field = (selected_field or 'RSK').upper()
        if selected_field not in self._field_names():
            selected_field = 'RSK'

        dates = self._build_periods(start_date, end_date, normalized_period)
        periods_by_key: dict[str, list[tuple[float, float]]] = defaultdict(list)
        rows = []
        if station_distances:
            metric_column = getattr(WeatherData, selected_field)
            rows = db.session.execute(
                db.select(
                    WeatherData.MESS_DATUM,
                    WeatherData.STATIONS_ID,
                    metric_column,
                ).where(
                    WeatherData.STATIONS_ID.in_(station_distances),
                    WeatherData.MESS_DATUM.between(start_date, end_date),
                )
            ).all()

        zero_distance_stations = {
            station_id
            for station_id, distance in station_distances.items()
            if distance == 0
        }
        if zero_distance_stations:
            weights = {
                station_id: 1.0 if station_id in zero_distance_stations else 0.0
                for station_id in station_distances
            }
        else:
            weights = {
                station_id: 1.0 / distance
                for station_id, distance in station_distances.items()
            }

        for row in rows:
            observation = row._mapping
            station_id = observation['STATIONS_ID']
            weight = weights.get(station_id, 0.0)
            if weight == 0:
                continue
            value = observation[selected_field]
            if value is None:
                continue
            period_key = self._group_key(observation['MESS_DATUM'], normalized_period)
            periods_by_key[period_key].append((value, weight))

        aggregated_values = []
        for period in dates:
            period_key = self._group_key(period, normalized_period)
            aggregated_values.append(self._weighted_mean(periods_by_key.get(period_key, [])))

        return {
            'selected_field': selected_field,
            'aggregation_period': normalized_period,
            'labels': [self._format_label(period, normalized_period) for period in dates],
            'values': aggregated_values,
        }

    @staticmethod
    def _field_names() -> set[str]:
        return {
            'FX', 'FM', 'RSK', 'SDK', 'SHK_TAG', 'NM', 'VPM', 'PM', 'TMK', 'UPM', 'TXK', 'TNK', 'TGK'
        }

    @staticmethod
    def _normalize_aggregation_period(aggregation_period: str | None) -> str:
        normalized = (aggregation_period or 'day').lower()
        return normalized if normalized in WeatherAggregationService.VALID_PERIODS else 'day'

    @staticmethod
    def _build_periods(start_date: date, end_date: date, aggregation_period: str) -> list[date]:
        if aggregation_period == 'day':
            return [
                start_date + timedelta(days=day_offset)
                for day_offset in range((end_date - start_date).days + 1)
            ]
        if aggregation_period == 'month':
            current = date(start_date.year, start_date.month, 1)
            last_month = date(end_date.year, end_date.month, 1)
            months = []
            while current <= last_month:
                months.append(current)
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)
            return months
        years = []
        current_year = start_date.year
        while current_year <= end_date.year:
            years.append(date(current_year, 1, 1))
            current_year += 1
        return years

    @staticmethod
    def _group_key(day: date, aggregation_period: str) -> str:
        if aggregation_period == 'month':
            return day.strftime('%Y-%m')
        if aggregation_period == 'year':
            return str(day.year)
        return day.isoformat()

    @staticmethod
    def _format_label(day: date, aggregation_period: str) -> str:
        if aggregation_period == 'month':
            return day.strftime('%Y-%m')
        if aggregation_period == 'year':
            return str(day.year)
        return day.isoformat()

    @staticmethod
    def _weighted_mean(values: list[tuple[float, float]]) -> float | None:
        total_weight = sum(weight for _, weight in values)
        if total_weight == 0:
            return None
        return sum(value * weight for value, weight in values) / total_weight

