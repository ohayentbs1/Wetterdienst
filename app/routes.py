from flask import Blueprint, render_template
from app.models import WetterEintrag

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Beispielhaftes Auslesen der Einträge aus der Datenbank
    eintraege = WetterEintrag.query.order_by(WetterEintrag.zeitstempel.desc()).all()
    return render_template('index.html', eintraege=eintraege)