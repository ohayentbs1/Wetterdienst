import csv
import re
import zipfile
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from urllib.request import urlopen

from flask import current_app

from app import db
from app.models import Station, WeatherData

DWD_URL = (
    'https://opendata.dwd.de/climate_environment/CDC/observations_germany/'
    'climate/daily/kl/historical/'
)
WEATHER_FIELDS = (
    'QN_3', 'FX', 'FM', 'QN_4', 'RSK', 'RSKF', 'SDK', 'SHK_TAG',
    'NM', 'VPM', 'PM', 'TMK', 'UPM', 'TXK', 'TNK', 'TGK',
)
INTEGER_FIELDS = {'QN_3', 'QN_4', 'RSKF', 'SHK_TAG'}


class WeatherDataImportService:
    def import_for_stations(self, stations: list[Station]) -> int:
        station_ids = {station.id for station in stations if not self.has_weather_data(station)}
        if not station_ids:
            return 0

        archive_dir = Path(current_app.config['DWD_ARCHIVE_DIR'])
        archive_dir.mkdir(parents=True, exist_ok=True)

        with urlopen(DWD_URL, timeout=30) as response:
            directory = response.read().decode('utf-8')

        archive_names = [
            name for name in re.findall(r'tageswerte_KL_\d{5}_\d{8}_\d{8}_hist\.zip', directory)
            if int(name.split('_')[2]) in station_ids
        ]

        imported = 0
        for filename in archive_names:
            station_id = int(filename.split('_')[2])
            archive_path = self._download_archive(archive_dir, filename)
            with zipfile.ZipFile(archive_path) as archive:
                product_name = next(
                    name for name in archive.namelist()
                    if Path(name).name.startswith('produkt_klima_tag')
                )
                with archive.open(product_name) as product:
                    reader = csv.DictReader(
                        TextIOWrapper(product, encoding='latin-1', newline=''),
                        delimiter=';',
                    )
                    fieldnames = next(reader.reader)
                    reader.fieldnames = [header.strip() for header in fieldnames]
                    imported += self._save_rows(reader, station_id)

        return imported

    @staticmethod
    def has_weather_data(station: Station) -> bool:
        return bool(
            db.session.execute(
                db.select(db.exists().where(WeatherData.STATIONS_ID == station.id))
            ).scalar_one()
        )

    @staticmethod
    def _download_archive(archive_dir: Path, filename: str) -> Path:
        archive_path = archive_dir / filename
        if not archive_path.exists():
            with urlopen(DWD_URL + filename, timeout=60) as response:
                archive_path.write_bytes(response.read())
        return archive_path

    @staticmethod
    def _save_rows(reader, station_id: int) -> int:
        existing_dates = set(
            db.session.execute(
                db.select(WeatherData.MESS_DATUM).where(WeatherData.STATIONS_ID == station_id)
            ).scalars()
        )
        pending_rows = []
        imported = 0

        for row in reader:
            values = {name.strip(): value.strip() for name, value in row.items() if name}
            date = datetime.strptime(values['MESS_DATUM'], '%Y%m%d').date()
            if date in existing_dates:
                continue

            observation = {'STATIONS_ID': station_id, 'MESS_DATUM': date}
            for field in WEATHER_FIELDS:
                value = values.get(field, '')
                if not value or value == '-999':
                    observation[field] = None
                elif field in INTEGER_FIELDS:
                    observation[field] = int(float(value))
                else:
                    observation[field] = float(value)

            pending_rows.append(observation)
            existing_dates.add(date)
            imported += 1
            if len(pending_rows) >= 1000:
                db.session.execute(db.insert(WeatherData), pending_rows)
                db.session.commit()
                pending_rows = []

        if pending_rows:
            db.session.execute(db.insert(WeatherData), pending_rows)
            db.session.commit()

        return imported
