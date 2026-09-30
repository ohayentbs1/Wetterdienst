from app import db
from datetime import datetime

class WetterEintrag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stadt = db.Column(db.String(100), nullable=False)
    temperatur = db.Column(db.Float, nullable=False)
    beschreibung = db.Column(db.String(200))
    zeitstempel = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WetterEintrag {self.stadt} - {self.temperatur}°C>'


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