from datetime import datetime
from urllib.request import urlopen

from app import db
from app.models import Station


STATION_FILE_URL = (
    'https://opendata.dwd.de/climate_environment/CDC/observations_germany/'
    'climate/daily/kl/historical/KL_Tageswerte_Beschreibung_Stationen.txt'
)


class ImportController:
    def import_stations(self):
        with urlopen(STATION_FILE_URL, timeout=30) as response:
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
        return len(stations)

    @staticmethod
    def _parse_date(value, line_number):
        try:
            return datetime.strptime(value, '%Y%m%d').date()
        except ValueError as error:
            raise ValueError(
                f'Ungültiges Datum in Stationsdatensatz, Zeile {line_number}.'
            ) from error
