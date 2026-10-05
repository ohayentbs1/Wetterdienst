import math

from geopy.distance import geodesic

from app.models import Station


class StationController:
    SEARCH_RADIUS_KM = 50

    def get_nearby_stations(self, latitude, longitude):
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

            distance_km = geodesic(
                (latitude, longitude),
                (station.geo_breite, station.geo_laenge),
            ).km
            if distance_km <= self.SEARCH_RADIUS_KM:
                nearby.append((distance_km, station.stationsname))

        nearby.sort(key=lambda entry: (entry[0], entry[1]))
        return [name for _, name in nearby]
