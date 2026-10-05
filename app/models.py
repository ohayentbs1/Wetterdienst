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