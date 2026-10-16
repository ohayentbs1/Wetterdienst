from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from app import db
from app.enums import AggregationPeriod, WeatherField
from app.models import WeatherData


class WeatherAggregationService:
    def get_aggregated_data(
        self,
        station_distances: dict[int, float],
        start_date: date,
        end_date: date,
        selected_field: str,
        aggregation_period: str = 'day',
    ) -> dict:
        period_name = AggregationPeriod.normalize(aggregation_period).value
        field = WeatherField.normalize(selected_field)
        labels = self._build_labels(start_date, end_date, period_name)

        values_by_period: dict[str, list[tuple[float, float]]] = defaultdict(list)
        rows = []
        if station_distances:
            rows = db.session.execute(
                db.select(
                    WeatherData.MESS_DATUM,
                    WeatherData.STATIONS_ID,
                    getattr(WeatherData, field.value),
                ).where(
                    WeatherData.STATIONS_ID.in_(station_distances),
                    WeatherData.MESS_DATUM.between(start_date, end_date),
                )
            ).all()

        weights = {
            station_id: 1.0 / distance if distance else 1.0
            for station_id, distance in station_distances.items()
        }

        for row in rows:
            observation = row._mapping
            station_id = observation['STATIONS_ID']
            weight = weights.get(station_id, 0.0)
            value = observation[field.value]
            if value is None or weight == 0:
                continue
            key = self._group_key(observation['MESS_DATUM'], period_name)
            values_by_period[key].append((value, weight))

        aggregated_values = [
            self._weighted_mean(values_by_period.get(self._group_key(period, period_name), []))
            for period in self._build_periods(start_date, end_date, period_name)
        ]

        return {
            'selected_field': field.value,
            'aggregation_period': period_name,
            'labels': labels,
            'values': aggregated_values,
        }

    @staticmethod
    def _build_periods(start_date: date, end_date: date, aggregation_period: str) -> list[date]:
        if aggregation_period == AggregationPeriod.DAY.value:
            return [start_date + timedelta(days=offset) for offset in range((end_date - start_date).days + 1)]
        if aggregation_period == AggregationPeriod.MONTH.value:
            months = []
            current = date(start_date.year, start_date.month, 1)
            last = date(end_date.year, end_date.month, 1)
            while current <= last:
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
    def _build_labels(start_date: date, end_date: date, aggregation_period: str) -> list[str]:
        periods = WeatherAggregationService._build_periods(start_date, end_date, aggregation_period)
        return [WeatherAggregationService._format_label(period, aggregation_period) for period in periods]

    @staticmethod
    def _group_key(day: date, aggregation_period: str) -> str:
        if aggregation_period == AggregationPeriod.MONTH.value:
            return day.strftime('%Y-%m')
        if aggregation_period == AggregationPeriod.YEAR.value:
            return str(day.year)
        return day.isoformat()

    @staticmethod
    def _format_label(day: date, aggregation_period: str) -> str:
        if aggregation_period == AggregationPeriod.MONTH.value:
            return day.strftime('%Y-%m')
        if aggregation_period == AggregationPeriod.YEAR.value:
            return str(day.year)
        return day.isoformat()

    @staticmethod
    def _weighted_mean(values: list[tuple[float, float]]) -> float | None:
        if not values:
            return None
        total_weight = sum(weight for _, weight in values)
        if total_weight == 0:
            return None
        return sum(value * weight for value, weight in values) / total_weight
