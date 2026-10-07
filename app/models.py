from app import db


class Station(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    von_datum = db.Column(db.Date)
    bis_datum = db.Column(db.Date)
    stationshoehe = db.Column(db.Integer)
    geo_breite = db.Column(db.Float)
    geo_laenge = db.Column(db.Float)
    stationsname = db.Column(db.String(100))
    bundesland = db.Column(db.String(100))
    abgabe = db.Column(db.String(20))
    weather_data = db.relationship('WeatherData', back_populates='station')


class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    STATIONS_ID = db.Column(db.Integer, db.ForeignKey('station.id'), nullable=False)
    MESS_DATUM = db.Column(db.Date, nullable=False)
    QN_3 = db.Column(db.Integer)
    FX = db.Column(db.Float)
    FM = db.Column(db.Float)
    QN_4 = db.Column(db.Integer)
    RSK = db.Column(db.Float)
    RSKF = db.Column(db.Integer)
    SDK = db.Column(db.Float)
    SHK_TAG = db.Column(db.Integer)
    NM = db.Column(db.Float)
    VPM = db.Column(db.Float)
    PM = db.Column(db.Float)
    TMK = db.Column(db.Float)
    UPM = db.Column(db.Float)
    TXK = db.Column(db.Float)
    TNK = db.Column(db.Float)
    TGK = db.Column(db.Float)

    station = db.relationship('Station', back_populates='weather_data')

    __table_args__ = (
        db.UniqueConstraint(
            'STATIONS_ID',
            'MESS_DATUM',
            name='uq_weather_data_station_date',
        ),
    )