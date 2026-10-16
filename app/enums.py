from __future__ import annotations

from enum import Enum


class DisplayMode(str, Enum):
    CHART = 'chart'
    TABLE = 'table'

    @classmethod
    def normalize(cls, value: str | None) -> 'DisplayMode':
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.CHART

        normalized = str(value).lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        return cls.CHART


class AggregationPeriod(str, Enum):
    DAY = 'day'
    MONTH = 'month'
    YEAR = 'year'

    @classmethod
    def normalize(cls, value: str | None) -> 'AggregationPeriod':
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.DAY

        normalized = str(value).lower()
        for period in cls:
            if period.value == normalized:
                return period
        return cls.DAY


class WeatherField(str, Enum):
    FX = 'FX'
    FM = 'FM'
    RSK = 'RSK'
    SDK = 'SDK'
    SHK_TAG = 'SHK_TAG'
    NM = 'NM'
    VPM = 'VPM'
    PM = 'PM'
    TMK = 'TMK'
    UPM = 'UPM'
    TXK = 'TXK'
    TNK = 'TNK'
    TGK = 'TGK'
    DEFAULT = RSK

    @classmethod
    def normalize(cls, value: str | None) -> 'WeatherField':
        if isinstance(value, cls):
            return value
        if value is None:
            return cls.DEFAULT

        normalized = str(value).upper()
        for field in cls:
            if field.value == normalized:
                return field
        return cls.DEFAULT

    @property
    def label(self) -> str:
        return {
            'FX': 'Maximale Windspitze',
            'FM': 'Mittlere Windgeschwindigkeit',
            'RSK': 'Niederschlag',
            'SDK': 'Sonnenscheindauer',
            'SHK_TAG': 'Schneehöhe',
            'NM': 'Bewölkung',
            'VPM': 'Dampfdruck',
            'PM': 'Luftdruck',
            'TMK': 'Mittlere Lufttemperatur',
            'UPM': 'Relative Luftfeuchte',
            'TXK': 'Maximale Lufttemperatur',
            'TNK': 'Minimale Lufttemperatur',
            'TGK': 'Minimum der Lufttemperatur in 5 cm Höhe',
        }[self.value]

    @property
    def unit(self) -> str:
        return {
            'FX': 'm/s',
            'FM': 'm/s',
            'RSK': 'mm',
            'SDK': 'h',
            'SHK_TAG': 'cm',
            'NM': 'Achtel',
            'VPM': 'hPa',
            'PM': 'hPa',
            'TMK': '°C',
            'UPM': '%',
            'TXK': '°C',
            'TNK': '°C',
            'TGK': '°C',
        }[self.value]

