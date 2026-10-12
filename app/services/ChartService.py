from datetime import date, timedelta

from app import db
from app.models import WeatherData


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
    ) -> dict:
        selected_field = (selected_field or 'RSK').upper()
        if selected_field not in self.CHART_FIELDS:
            selected_field = 'RSK'

        fields_to_use = [selected_field]
        dates = [
            start_date + timedelta(days=day_offset)
            for day_offset in range((end_date - start_date).days + 1)
        ]
        labels = [day.isoformat() for day in dates]
        metric_columns = [
            getattr(WeatherData, field)
            for field in fields_to_use
        ]
        rows = []
        if station_distances:
            rows = db.session.execute(
                db.select(
                    WeatherData.MESS_DATUM,
                    WeatherData.STATIONS_ID,
                    *metric_columns,
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
        weighted_values = {
            field: {}
            for field in fields_to_use
        }
        for row in rows:
            observation = row._mapping
            station_id = observation['STATIONS_ID']
            weight = weights[station_id]
            if weight == 0:
                continue
            day = observation['MESS_DATUM']
            for field in fields_to_use:
                value = observation[field]
                if value is not None:
                    weighted_values[field].setdefault(day, []).append((value, weight))

        datasets = []
        for field in fields_to_use:
            label, unit = self.CHART_FIELDS[field]
            values_by_date = weighted_values[field]
            datasets.append({
                'label': f'{label} ({unit})',
                'data': [
                    self._weighted_mean(values_by_date.get(day, []))
                    for day in dates
                ],
            })
        return {
            'labels': labels,
            'datasets': datasets,
            'selected_field': selected_field,
        }

    @staticmethod
    def _weighted_mean(values: list[tuple[float, float]]) -> float | None:
        total_weight = sum(weight for _, weight in values)
        if total_weight == 0:
            return None
        return sum(value * weight for value, weight in values) / total_weight
